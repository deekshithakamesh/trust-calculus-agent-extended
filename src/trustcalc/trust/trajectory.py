from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(slots=True)
class TrajectoryEvent:
    actor: str
    action: str
    outcome: str
    timestamp: float
    metadata: dict | None = None


def analyze_trajectory(events: List[TrajectoryEvent]) -> dict:
    """Flag suspicious sequences by repetition and risky transitions."""
    if not events:
        return {"anomaly_detected": False, "risk_score": 0.0, "summary": "no events"}

    counts: dict[str, int] = {}
    for event in events:
        counts[event.action] = counts.get(event.action, 0) + 1

    repeated = max(counts.values()) if counts else 0
    risky = sum(1 for event in events if event.outcome == "attack")
    risk_score = min(1.0, (repeated / max(len(events), 1)) + (risky / max(len(events), 1)))

    anomaly_detected = repeated >= 4 or risky > 0
    return {
        "anomaly_detected": anomaly_detected,
        "risk_score": risk_score,
        "summary": "repeated action sequence or security violation detected" if anomaly_detected else "normal trajectory",
        "event_count": len(events),
        "repeated_action_count": repeated,
    }
