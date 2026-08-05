"""
Runtime taint propagation.

Every runtime value MUST pass through this module.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Generic, Iterable, TypeVar

from trustcalc.core.labels import SecurityLabel
from trustcalc.core.lattice import join
from trustcalc.core.provenance import (
    OperationType,
    ProvenanceGraph,
    ProvenanceNode,
)
from trustcalc.core.values import TrustedValue

T = TypeVar("T")
U = TypeVar("U")


@dataclass(slots=True)
class TaintTracker:
    """
    Runtime taint propagation engine.

    Responsible for:

    - wrapping raw values
    - propagating labels
    - maintaining provenance
    - validating information flow

    The tracker itself contains mutable state:

        ProvenanceGraph
        values (name -> TrustedValue registry)
    """

    graph: ProvenanceGraph = field(
        default_factory=ProvenanceGraph
    )

    values: dict[str, TrustedValue[Any]] = field(
        default_factory=dict
    )

    # ---------------------------------------------------------
    # Value Creation
    # ---------------------------------------------------------

    def wrap(
        self,
        value: T,
        label: SecurityLabel,
        actor: str = "runtime",
        description: str = "",
        name: str | None = None,
        **metadata: Any,
    ) -> TrustedValue[T]:
        """
        Wrap a raw Python value.

        This should be the only entry point
        from untrusted runtime values.
        """

        node = ProvenanceNode.origin(
            actor=actor,
            description=description,
            **metadata,
        )

        self.graph.add(node)

        trusted = TrustedValue(
            value=value,
            label=label,
            provenance=node,
        )

        if name is not None:
            self.values[name] = trusted

        return trusted

    # ---------------------------------------------------------
    # Existing Value
    # ---------------------------------------------------------

    def taint(
        self,
        value: TrustedValue[T],
        name: str | None = None,
    ) -> TrustedValue[T]:
        """
        Register an existing TrustedValue
        inside the provenance graph.

        Useful when values are loaded
        from storage.
        """

        if not self.graph.contains(
            value.provenance.id
        ):
            self.graph.add(
                value.provenance
            )

        if name is not None:
            self.values[name] = value

        return value

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    def validate(
        self,
        value: TrustedValue[Any],
    ) -> bool:
        """
        Ensure provenance exists.
        """

        return self.graph.contains(
            value.provenance.id
        )

    # ---------------------------------------------------------
    # Explanation
    # ---------------------------------------------------------

    def explain(
        self,
        value: TrustedValue[Any],
    ) -> str:

        return self.graph.explain(
            value.provenance.id
        )

    # ---------------------------------------------------------
    # Merge
    # ---------------------------------------------------------

    def merge(
        self,
        left: TrustedValue[T],
        right: TrustedValue[U],
        merge_fn: Callable[[T, U], Any],
        actor: str = "runtime",
        description: str = "merge",
        name: str | None = None,
        **metadata: Any,
    ) -> TrustedValue[Any]:
        """
        Merge two TrustedValues.

        Labels are combined using the lattice join operation.
        Provenance records both parent values.
        """

        merged_value = merge_fn(
            left.value,
            right.value,
        )

        merged_label = join(
            left.label,
            right.label,
        )

        node = ProvenanceNode.derived(
            operation=OperationType.MERGE,
            parents=(
                left.provenance.id,
                right.provenance.id,
            ),
            actor=actor,
            description=description,
            **metadata,
        )

        self.graph.add(node)

        trusted = TrustedValue(
            value=merged_value,
            label=merged_label,
            provenance=node,
        )

        if name is not None:
            self.values[name] = trusted

        return trusted

    # ---------------------------------------------------------
    # Transform
    # ---------------------------------------------------------

    def transform(
        self,
        value: TrustedValue[T],
        transform_fn: Callable[[T], U],
        operation: OperationType = OperationType.TRANSFORM,
        actor: str = "runtime",
        description: str = "",
        name: str | None = None,
        **metadata: Any,
    ) -> TrustedValue[U]:
        """
        Apply a transformation while preserving labels.
        """

        new_value = transform_fn(
            value.value
        )

        node = ProvenanceNode.derived(
            operation=operation,
            parents=(value.provenance.id,),
            actor=actor,
            description=description,
            **metadata,
        )

        self.graph.add(node)

        trusted = TrustedValue(
            value=new_value,
            label=value.label,
            provenance=node,
        )

        if name is not None:
            self.values[name] = trusted

        return trusted

    # ---------------------------------------------------------
    # Relabel
    # ---------------------------------------------------------

    def relabel(
        self,
        value: TrustedValue[T],
        label: SecurityLabel,
        actor: str = "runtime",
        description: str = "relabel",
        name: str | None = None,
        **metadata: Any,
    ) -> TrustedValue[T]:
        """
        Explicitly assign a new security label.

        Used only after policy-approved
        sanitization or declassification.
        """

        node = ProvenanceNode.derived(
            operation=OperationType.POLICY,
            parents=(value.provenance.id,),
            actor=actor,
            description=description,
            **metadata,
        )

        self.graph.add(node)

        trusted = TrustedValue(
            value=value.value,
            label=label,
            provenance=node,
        )

        if name is not None:
            self.values[name] = trusted

        return trusted

    # ---------------------------------------------------------
    # Clone
    # ---------------------------------------------------------

    def clone(
        self,
        value: TrustedValue[T],
    ) -> TrustedValue[T]:
        """
        Return an equivalent TrustedValue.

        No new provenance is created.
        """

        return TrustedValue(
            value=value.value,
            label=value.label,
            provenance=value.provenance,
            metadata=value.metadata,
        )

    # ---------------------------------------------------------
    # Batch Transform
    # ---------------------------------------------------------

    def transform_many(
        self,
        values: Iterable[TrustedValue[T]],
        transform_fn: Callable[[T], U],
        actor: str = "runtime",
    ) -> list[TrustedValue[U]]:
        """
        Apply the same transformation
        to multiple TrustedValues.
        """

        return [
            self.transform(
                value,
                transform_fn,
                actor=actor,
            )
            for value in values
        ]

    # ---------------------------------------------------------
    # Sanitize
    # ---------------------------------------------------------

    def sanitize(
        self,
        value: TrustedValue[T],
        sanitized_label: SecurityLabel,
        actor: str = "policy",
        description: str = "sanitize",
        name: str | None = None,
        **metadata: Any,
    ) -> TrustedValue[T]:
        """
        Produce a sanitized version of a TrustedValue.

        This operation must only be called after a successful
        policy decision. It records the sanitization in the
        provenance graph.
        """

        node = ProvenanceNode.derived(
            operation=OperationType.POLICY,
            parents=(value.provenance.id,),
            actor=actor,
            description=description,
            **metadata,
        )

        self.graph.add(node)

        trusted = TrustedValue(
            value=value.value,
            label=sanitized_label,
            provenance=node,
            metadata=value.metadata,
        )

        if name is not None:
            self.values[name] = trusted

        return trusted

    # ---------------------------------------------------------
    # Downgrade
    # ---------------------------------------------------------

    def downgrade(
        self,
        value: TrustedValue[T],
        new_label: SecurityLabel,
        actor: str = "policy",
    ) -> TrustedValue[T]:
        """
        Controlled declassification.

        Alias for sanitize() to make policy code
        easier to read.
        """

        return self.sanitize(
            value=value,
            sanitized_label=new_label,
            actor=actor,
            description="downgrade",
        )

    # ---------------------------------------------------------
    # Upgrade
    # ---------------------------------------------------------

    def upgrade(
        self,
        value: TrustedValue[T],
        new_label: SecurityLabel,
        actor: str = "policy",
    ) -> TrustedValue[T]:
        """
        Raise the security label.

        Useful when new information indicates a value
        should be treated as more confidential or less
        trustworthy.
        """

        node = ProvenanceNode.derived(
            operation=OperationType.POLICY,
            parents=(value.provenance.id,),
            actor=actor,
            description="upgrade",
        )

        self.graph.add(node)

        trusted = TrustedValue(
            value=value.value,
            label=new_label,
            provenance=node,
            metadata=value.metadata,
        )

        return trusted

    # ---------------------------------------------------------
    # Value Registry
    # ---------------------------------------------------------

    def get_taint(
        self,
        name: str,
    ) -> TrustedValue[Any] | None:
        """
        Retrieve a tracked value by name.

        Returns None if the name is unknown.
        """

        return self.values.get(name)

    def register_taint(
        self,
        name: str,
        value: TrustedValue[Any],
    ) -> TrustedValue[Any]:
        """
        Register a value under a name.
        """

        self.values[name] = value

        return value

    def tracked_names(self) -> list[str]:
        """
        Return the names of all tracked values.
        """

        return list(self.values.keys())

    def clear_values(self) -> None:
        """
        Clear the value registry.
        """

        self.values.clear()

    # ---------------------------------------------------------
    # Lineage
    # ---------------------------------------------------------

    def lineage(
        self,
        value: TrustedValue[Any],
    ) -> tuple[ProvenanceNode, ...]:
        """
        Return the provenance lineage of a value.
        """

        return self.graph.lineage(
            value.provenance.id
        )

    # ---------------------------------------------------------
    # History
    # ---------------------------------------------------------

    def history(
        self,
        value: TrustedValue[Any],
    ) -> list[str]:
        """
        Human-readable provenance history.
        """

        return [
            f"{node.operation.value}: {node.description}"
            for node in self.lineage(value)
        ]

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def statistics(self) -> dict[str, int]:
        """
        Runtime provenance statistics.
        """

        return {
            "nodes": len(self.graph),
            "tracked_values": len(self.values),
        }

    # ---------------------------------------------------------
    # Flow Check
    # ---------------------------------------------------------

    def flow_check(
        self,
        source: TrustedValue[Any],
        destination_label: SecurityLabel,
    ) -> bool:
        """
        Check whether information is allowed to flow
        from the source label into the destination label.

        Uses the lattice ordering.
        """

        return source.label.can_flow_to(
            destination_label
        )
