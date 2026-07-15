"""
trustcalc.core.provenance
=========================

Persistent provenance graph.

Every TrustedValue stores only a provenance UUID.

The actual provenance graph is maintained here.

The graph is append-only.

Once created, provenance nodes are never modified.

This provides a complete audit trail of how every value in the runtime
was produced.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Iterable, Iterator
from uuid import UUID, uuid4


# =====================================================================
# Operation Types
# =====================================================================


class OperationType(str, Enum):

    ORIGIN = "origin"

    USER_INPUT = "user_input"

    WEB_FETCH = "web_fetch"

    FILE_READ = "file_read"

    FILE_WRITE = "file_write"

    TOOL_CALL = "tool_call"

    LLM_PROMPT = "llm_prompt"

    LLM_RESPONSE = "llm_response"

    TRANSFORM = "transform"

    MERGE = "merge"

    FILTER = "filter"

    POLICY = "policy"

    GATEWAY = "gateway"

    UNKNOWN = "unknown"


# =====================================================================
# Provenance Node
# =====================================================================


@dataclass(frozen=True, slots=True)
class ProvenanceNode:

    id: UUID = field(default_factory=uuid4)

    operation: OperationType = OperationType.UNKNOWN

    actor: str = "system"

    description: str = ""

    parents: tuple[UUID, ...] = ()

    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:

        return {
            "id": str(self.id),
            "operation": self.operation.value,
            "actor": self.actor,
            "description": self.description,
            "parents": [str(p) for p in self.parents],
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def origin(
        cls,
        actor: str,
        description: str = "",
        **metadata,
    ) -> "ProvenanceNode":

        return cls(
            operation=OperationType.ORIGIN,
            actor=actor,
            description=description,
            metadata=metadata,
        )

    @classmethod
    def derived(
        cls,
        operation: OperationType,
        parents: Iterable[UUID],
        actor: str = "runtime",
        description: str = "",
        **metadata,
    ) -> "ProvenanceNode":

        return cls(
            operation=operation,
            actor=actor,
            description=description,
            parents=tuple(parents),
            metadata=metadata,
        )


# =====================================================================
# Provenance Graph
# =====================================================================


class ProvenanceGraph:
    """
    Persistent append-only DAG.
    """

    def __init__(self):

        self._nodes: Dict[UUID, ProvenanceNode] = {}

    # ------------------------------------------------------------

    def add(
        self,
        node: ProvenanceNode,
    ) -> UUID:

        self._nodes[node.id] = node

        return node.id

    # ------------------------------------------------------------

    def get(
        self,
        node_id: UUID,
    ) -> ProvenanceNode | None:

        return self._nodes.get(node_id)

    # ------------------------------------------------------------

    def contains(
        self,
        node_id: UUID,
    ) -> bool:

        return node_id in self._nodes

    # ------------------------------------------------------------

    def parents(
        self,
        node_id: UUID,
    ) -> tuple[ProvenanceNode, ...]:

        node = self.get(node_id)

        if node is None:
            return ()

        return tuple(
            self._nodes[parent] for parent in node.parents if parent in self._nodes
        )

    # ------------------------------------------------------------

    def lineage(
        self,
        node_id: UUID,
    ) -> tuple[ProvenanceNode, ...]:
        """
        Depth-first lineage traversal.
        """

        visited: set[UUID] = set()

        ordered: list[ProvenanceNode] = []

        def dfs(current: UUID):

            if current in visited:
                return

            visited.add(current)

            node = self.get(current)

            if node is None:
                return

            ordered.append(node)

            for parent in node.parents:
                dfs(parent)

        dfs(node_id)

        return tuple(ordered)

    # ------------------------------------------------------------

    def explain(
        self,
        node_id: UUID,
    ) -> str:
        """
        Human-readable provenance explanation.
        """

        chain = self.lineage(node_id)

        if not chain:
            return "Unknown provenance."

        lines = []

        for node in chain:

            lines.append(
                f"[{node.operation.value}] " f"{node.actor}: " f"{node.description}"
            )

        return "\n".join(lines)

    # ------------------------------------------------------------

    def __len__(self):

        return len(self._nodes)

    def __iter__(
        self,
    ) -> Iterator[ProvenanceNode]:

        return iter(self._nodes.values())
