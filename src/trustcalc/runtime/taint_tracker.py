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

    The tracker itself contains only one mutable object:

        ProvenanceGraph
    """

    graph: ProvenanceGraph = field(
        default_factory=ProvenanceGraph
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

        return TrustedValue(

            value=value,

            label=label,

            provenance=node,
        )

    # ---------------------------------------------------------
    # Existing Value
    # ---------------------------------------------------------

    def taint(
        self,
        value: TrustedValue[T],
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

        return TrustedValue(
            value=merged_value,
            label=merged_label,
            provenance=node,
        )

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

        return TrustedValue(
            value=new_value,
            label=value.label,
            provenance=node,
        )

    # ---------------------------------------------------------
    # Relabel
    # ---------------------------------------------------------

    def relabel(
        self,
        value: TrustedValue[T],
        label: SecurityLabel,
        actor: str = "runtime",
        description: str = "relabel",
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

        return TrustedValue(
            value=value.value,
            label=label,
            provenance=node,
        )

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

        return TrustedValue(
            value=value.value,
            label=sanitized_label,
            provenance=node,
            metadata=value.metadata,
        )

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

        return TrustedValue(
            value=value.value,
            label=new_label,
            provenance=node,
            metadata=value.metadata,
        )

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