from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class EvidenceType(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    ANOMALY = "anomaly"
    POLICY = "policy"
    PROVENANCE = "provenance"
    RECOMMENDATION = "recommendation"
    SECURITY_EVENT = "security_event"
    TIMEOUT = "timeout"
    ATTACK = "attack"


@dataclass(slots=True)
class Evidence:
    """Single evidence observation for updating trust."""

    type: EvidenceType
    value: float
    weight: float = 1.0
    source: str = "unknown"
    context: str = "default"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[float] = None

    def __post_init__(self) -> None:
        self.value = float(self.value)
        self.weight = float(self.weight)
        if not 0.0 <= self.value <= 1.0:
            self.value = min(max(self.value, 0.0), 1.0)
        if self.weight < 0.0:
            self.weight = 0.0
        if self.timestamp is None:
            import time

            self.timestamp = time.time()

    @property
    def effective_weight(self) -> float:
        return max(self.weight, 0.0)
