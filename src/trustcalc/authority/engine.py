"""
Simple deterministic Authority Engine that maps trust + confidence + risk +
delegation + provenance warnings + trajectory anomalies to one of:
ALLOW | VERIFY | RESTRICT | SANDBOX | DENY

This is intentionally simple and rule-based for auditability; thresholds are
configurable and kept small for the demo prototype.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class AuthorityDecision:
    decision: str
    reason: str
    inputs: Dict


class AuthorityEngine:
    def __init__(self, thresholds: Optional[Dict] = None) -> None:
        # default thresholds
        self.thresholds = thresholds or {
            "very_high": {"allow_expected": 0.85, "allow_conf": 0.8, "verify_expected": 0.7, "verify_conf": 0.5},
            "high": {"allow_expected": 0.7, "allow_conf": 0.5, "verify_expected": 0.55, "verify_conf": 0.3},
            "medium": {"allow_expected": 0.5, "allow_conf": 0.2, "verify_expected": 0.4, "verify_conf": 0.15},
            "low": {"allow_expected": 0.3, "allow_conf": 0.0, "verify_expected": 0.2, "verify_conf": 0.0},
        }

    def decide(self, *, subject: str, action: str, expected: float, confidence: float, risk: str = "medium", delegation_depth: int = 0, provenance_warnings: Optional[List[str]] = None, trajectory_features: Optional[Dict] = None) -> AuthorityDecision:
        cfg = self.thresholds.get(risk, self.thresholds["medium"])
        pw = provenance_warnings or []
        # increase thresholds slightly if provenance warnings exist
        delta = 0.1 * len(pw)
        allow_expected = cfg["allow_expected"] + delta
        allow_conf = cfg["allow_conf"] + delta
        verify_expected = cfg["verify_expected"] + delta
        verify_conf = cfg["verify_conf"] + delta

        # delegation attenuation: deeper delegations require stronger evidence
        delegation_penalty = 0.05 * delegation_depth
        allow_expected += delegation_penalty
        verify_expected += delegation_penalty

        inputs = {
            "subject": subject,
            "action": action,
            "expected": expected,
            "confidence": confidence,
            "risk": risk,
            "delegation_depth": delegation_depth,
            "provenance_warnings": pw,
            "trajectory_features": trajectory_features,
            "thresholds": {"allow_expected": allow_expected, "allow_conf": allow_conf, "verify_expected": verify_expected, "verify_conf": verify_conf},
        }

        # Decision rules (deterministic)
        if expected >= allow_expected and confidence >= allow_conf:
            return AuthorityDecision(decision="ALLOW", reason="Satisfies allow thresholds", inputs=inputs)
        if expected >= verify_expected and confidence >= verify_conf:
            return AuthorityDecision(decision="VERIFY", reason="Satisfies verify thresholds", inputs=inputs)

        # Sandbox for very suspicious (low expected but high confidence of failure)
        if expected < 0.3 and confidence >= 0.6 and risk in ("high", "very_high"):
            return AuthorityDecision(decision="SANDBOX", reason="Low expected with high confidence on high-risk action", inputs=inputs)

        # Restrict for uncertain but possibly risky
        if expected < verify_expected and (confidence < verify_conf or expected < verify_expected):
            return AuthorityDecision(decision="RESTRICT", reason="Insufficient evidence for high privilege", inputs=inputs)

        return AuthorityDecision(decision="DENY", reason="Default deny: thresholds not met", inputs=inputs)


__all__ = ["AuthorityEngine", "AuthorityDecision"]
