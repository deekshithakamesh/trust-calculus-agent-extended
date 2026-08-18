"""
Simple provenance graph utilities for the Trust Calculus prototype.

This provides a minimal directed graph that links evidence and entities. It
is intentionally lightweight and in-memory for early experiments. A more
featureful provenance store (W3C-PROV style or a graph DB) can replace this
module later.
"""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Dict, Iterable, List, Set, Tuple


class ProvenanceGraph:
    """Lightweight directed provenance graph.

    Nodes are arbitrary identifiers (str). Edges are recorded as adjacency
    lists: src -> [dst]. Typical use: record that evidence E was recommended_by
    node A by adding edge E <- A (or A -> E depending on query direction).
    """

    def __init__(self) -> None:
        self._adj: Dict[str, List[str]] = defaultdict(list)
        self._rev: Dict[str, List[str]] = defaultdict(list)

    def add_edge(self, src: str, dst: str) -> None:
        self._adj[src].append(dst)
        self._rev[dst].append(src)

    def predecessors(self, node: str) -> List[str]:
        return list(self._rev.get(node, []))

    def successors(self, node: str) -> List[str]:
        return list(self._adj.get(node, []))

    def reachable_sources(self, node: str, max_hops: int = 5) -> Set[str]:
        """Return a set of upstream nodes reachable within max_hops (walk backwards)."""
        seen: Set[str] = set()
        q = deque([(node, 0)])
        while q:
            cur, d = q.popleft()
            if d >= max_hops:
                continue
            for p in self.predecessors(cur):
                if p not in seen:
                    seen.add(p)
                    q.append((p, d + 1))
        return seen

    def share_common_root(self, a: str, b: str, max_hops: int = 5) -> bool:
        """Return True if a and b share any common upstream node within max_hops."""
        ra = self.reachable_sources(a, max_hops)
        rb = self.reachable_sources(b, max_hops)
        return len(ra.intersection(rb)) > 0

    def discount_factor_for(self, evidence_id: str, existing_evidence_ids: Iterable[str], base: float = 1.0) -> float:
        """Return a discount factor in (0,1] to reduce effective weight of evidence
        when it shares upstream sources with existing evidence.

        Very simple heuristic: for each existing evidence that shares a common root
        with evidence_id, multiply discount by 0.5 (configurable). The result is
        clamped to [0.01, 1.0].
        """
        discount = 1.0
        for e in existing_evidence_ids:
            if self.share_common_root(evidence_id, e):
                discount *= 0.5
        return max(0.01, min(1.0, discount))


__all__ = ["ProvenanceGraph"]
