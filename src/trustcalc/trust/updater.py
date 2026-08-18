from __future__ import annotations

from trustcalc.trust.evidence import Evidence
from trustcalc.trust.state import TrustState


def update_trust(state: TrustState, evidence: Evidence, success: bool | None = None) -> TrustState:
    """Update Beta-Binomial belief with a single evidence observation."""
    if success is None:
        success = evidence.value >= 0.5

    alpha = float(state.alpha)
    beta = float(state.beta)

    weight = evidence.effective_weight
    if evidence.type.value in {"attack", "failure", "anomaly", "timeout", "security_event"}:
        beta += weight * (1.0 + evidence.value)
        alpha += weight * (0.0 + (1.0 - evidence.value) * 0.25)
    else:
        alpha += weight * (1.0 + evidence.value)
        beta += weight * (0.0 + (1.0 - evidence.value) * 0.25)

    if success:
        alpha += weight * 0.75
    else:
        beta += weight * 0.75

    trust = alpha / (alpha + beta)
    confidence = (alpha + beta) / (alpha + beta + 10.0)
    if confidence > 1.0:
        confidence = 1.0

    updated = state.clone()
    updated.alpha = alpha
    updated.beta = beta
    updated.trust = trust
    updated.confidence = confidence
    updated.evidence.append(
        {
            "type": evidence.type.value,
            "value": evidence.value,
            "weight": weight,
            "source": evidence.source,
            "context": evidence.context,
            "success": success,
        }
    )
    return updated
