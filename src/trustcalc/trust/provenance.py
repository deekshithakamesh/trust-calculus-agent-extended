from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple
from uuid import uuid4


@dataclass(slots=True)
class ProvenanceNode:
    id: str
    label: str
    operation: str = "event"
    parents: Tuple[str, ...] = ()
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def parent_ids(self) -> Tuple[str, ...]:
        return self.parents


class ProvenanceGraph:
    """Simple causal provenance graph for evidence and tool outcomes."""

    def __init__(self) -> None:
        self.nodes: Dict[str, ProvenanceNode] = {}

    def add_node(self, label: str, operation: str, parents: Optional[Iterable[str]] = None, metadata: Optional[Dict[str, Any]] = None) -> ProvenanceNode:
        node_id = str(uuid4())
        parent_tuple = tuple(parents or ())
        node = ProvenanceNode(id=node_id, label=label, operation=operation, parents=parent_tuple, metadata=metadata or {})
        self.nodes[node_id] = node
        return node


def discount_correlated_evidence(evidence: Iterable[Dict[str, Any]], shared_sources: Optional[set[str]] = None) -> List[Dict[str, Any]]:
    """Reduce weight of evidence when sources are correlated or duplicated."""
    shared_sources = shared_sources or set()
    discounted: List[Dict[str, Any]] = []
    for item in evidence:
        mutable = dict(item)
        source = str(mutable.get("source", "unknown"))
        weight = float(mutable.get("weight", 1.0))
        if source in shared_sources:
            weight *= 0.5
        mutable["weight"] = max(0.0, min(weight, 1.0))
        discounted.append(mutable)
    return discounted
