from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List


@dataclass(slots=True)
class BaselineSystem:
    """Simple baseline authorization strategy for comparison."""

    name: str = "baseline"
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def decide(self, *, trust: float, confidence: float, risk: float, malicious: bool = False) -> str:
        if malicious and (trust < 0.4 or confidence < 0.15):
            return "DENY"
        if trust < 0.5:
            return "SANDBOX"
        return "ALLOW"

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "decision": "ALLOW",
        }

    @staticmethod
    def summarize(baselines: Iterable["BaselineSystem"]) -> Dict[str, Dict[str, Any]]:
        result: Dict[str, Dict[str, Any]] = {}
        for baseline in baselines:
            result[baseline.name] = baseline.summary()
        return result


@dataclass(slots=True)
class RiskBasedBaseline(BaselineSystem):
    name: str = "risk_based"
    description: str = "authorize only if trust exceeds required threshold for risk"

    def decide(self, *, trust: float, confidence: float, risk: float, malicious: bool = False) -> str:
        required = 0.5 + 0.5 * risk
        if malicious and trust < required:
            return "DENY"
        if confidence < 0.2:
            return "SANDBOX"
        return "ALLOW" if trust >= required else "SANDBOX"


@dataclass(slots=True)
class ProposedBaseline(BaselineSystem):
    name: str = "proposed"
    description: str = "proposed trust calculus baseline with confidence guards"

    def decide(self, *, trust: float, confidence: float, risk: float, malicious: bool = False) -> str:
        required = 0.5 + 0.5 * risk
        if trust < 0.35 or confidence < 0.1:
            return "DENY"
        if confidence < 0.35:
            return "SANDBOX"
        if malicious and trust < required:
            return "DENY"
        if trust >= required and confidence >= 0.75:
            return "ALLOW"
        if trust >= required * 0.9 and confidence >= 0.55:
            return "VERIFY"
        if trust >= required * 0.8 and confidence >= 0.45:
            return "RESTRICT"
        return "SANDBOX"
