"""
Evidence model for the Trust Calculus prototype.

Contains a lightweight Evidence dataclass and helpers for mapping evidence to
Beta increments. Evidence objects are intended to be small, serializable, and
attributed to a source with optional provenance.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional
import uuid


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Evidence:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source: str = "unknown"
    timestamp: str = field(default_factory=now_iso)
    type: str = "success"  # 'success'|'failure'|'anomaly'|'recommendation' etc.
    payload: Optional[Dict[str, Any]] = None
    strength: float = 1.0  # reliability estimate in [0,1]
    weight: float = 1.0  # numeric weight mapped to Beta increments
    provenance: List[str] = field(default_factory=list)  # list of source ids

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "timestamp": self.timestamp,
            "type": self.type,
            "payload": self.payload,
            "strength": self.strength,
            "weight": self.weight,
            "provenance": list(self.provenance),
        }


def map_strength_to_weight(strength: float, base: float = 1.0) -> float:
    """Map a reliability strength in [0,1] to an evidence weight (positive float).

    This mapping is deliberately simple and configurable. For now, weight = base * (0.5 + 0.5*strength)
    so strength=0 -> 0.5*base, strength=1 -> 1.0*base.
    """
    try:
        s = float(strength)
    except Exception:
        s = 0.5
    s = max(0.0, min(1.0, s))
    return base * (0.5 + 0.5 * s)


__all__ = ["Evidence", "map_strength_to_weight"]
