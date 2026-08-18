from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class TrustState:
    """Tracks the trust and confidence assigned to an entity for one action."""

    entity_id: str
    action: str
    context: str = "default"
    time: float = 0.0
    trust: float = 0.5
    confidence: float = 0.5
    alpha: float = 1.0
    beta: float = 1.0
    risk: float = 0.0
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    provenance: List[str] = field(default_factory=list)
    delegation_depth: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.alpha = float(self.alpha)
        self.beta = float(self.beta)
        self.trust = float(self.trust)
        self.confidence = float(self.confidence)
        self.risk = float(self.risk)
        self.delegation_depth = int(self.delegation_depth)
        if self.alpha <= 0:
            self.alpha = 1e-6
        if self.beta <= 0:
            self.beta = 1e-6
        if not 0.0 <= self.trust <= 1.0:
            self.trust = min(max(self.trust, 0.0), 1.0)
        if not 0.0 <= self.confidence <= 1.0:
            self.confidence = min(max(self.confidence, 0.0), 1.0)

    @property
    def total_evidence(self) -> float:
        return self.alpha + self.beta

    def clone(self) -> "TrustState":
        return TrustState(
            entity_id=self.entity_id,
            action=self.action,
            context=self.context,
            time=self.time,
            trust=self.trust,
            confidence=self.confidence,
            alpha=self.alpha,
            beta=self.beta,
            risk=self.risk,
            evidence=[item.copy() for item in self.evidence],
            provenance=list(self.provenance),
            delegation_depth=self.delegation_depth,
            metadata=dict(self.metadata),
        )
