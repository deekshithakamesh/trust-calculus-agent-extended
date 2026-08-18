from __future__ import annotations

from trustcalc.trust.state import TrustState


def apply_temporal_decay(state: TrustState, days: float = 30.0, decay_rate: float = 0.01) -> TrustState:
    """Apply exponential decay to trust and confidence without new evidence."""
    updated = state.clone()
    factor = 2.718281828459045 ** (-(decay_rate * max(days, 0.0)))
    updated.trust = max(0.0, state.trust * factor)
    updated.confidence = max(0.0, state.confidence * factor)
    updated.alpha = max(1e-6, state.alpha * factor)
    updated.beta = max(1e-6, state.beta * (1.0 + 0.1 * (days / 30.0)))
    return updated
