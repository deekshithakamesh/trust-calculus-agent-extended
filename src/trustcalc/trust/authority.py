from __future__ import annotations

from enum import Enum


class AuthorityDecision(str, Enum):
    ALLOW = "ALLOW"
    VERIFY = "VERIFY"
    RESTRICT = "RESTRICT"
    SANDBOX = "SANDBOX"
    DENY = "DENY"


def decide_authority(trust: float, confidence: float, risk: float) -> AuthorityDecision:
    """Return the authority decision for the action under current state."""
    trust = min(max(float(trust), 0.0), 1.0)
    confidence = min(max(float(confidence), 0.0), 1.0)
    risk = min(max(float(risk), 0.0), 1.0)

    required = 0.5 + 0.5 * risk

    if trust < 0.35 or confidence < 0.10:
        return AuthorityDecision.DENY

    if confidence < 0.35:
        return AuthorityDecision.SANDBOX

    if trust >= required and confidence >= 0.75:
        return AuthorityDecision.ALLOW

    if trust >= required * 0.9 and confidence >= 0.55:
        return AuthorityDecision.VERIFY

    if trust >= required * 0.8 and confidence >= 0.45:
        return AuthorityDecision.RESTRICT

    return AuthorityDecision.SANDBOX
