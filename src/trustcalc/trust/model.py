"""
Uncertainty-aware Trust Model for Trust Calculus.

Implements a Beta/Bayesian evidence model with temporal decay.

This is a lightweight prototype used by the PolicyEnforcer to make
context-aware, uncertainty-aware authorization decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import math
from typing import Dict, Tuple


def now_ts() -> float:
    return datetime.now(timezone.utc).timestamp()


@dataclass
class TrustRecord:
    alpha: float = 1.0
    beta: float = 1.0
    last_update: float = field(default_factory=now_ts)


@dataclass(slots=True)
class TrustStore:
    """In-memory store of trust records keyed by (subject, action).

    Records store Beta(alpha,beta) counts that decay toward the prior
    over time using exponential decay.
    """

    records: Dict[Tuple[str, str], TrustRecord] = field(default_factory=dict)

    # half-life in seconds for exponential decay of evidence
    half_life_seconds: float = 3600.0

    def _decay_factor(self, dt_seconds: float) -> float:
        # weight = 0.5^(dt / half_life)
        return math.pow(0.5, dt_seconds / self.half_life_seconds)

    def _decay_record(self, rec: TrustRecord) -> None:
        now = now_ts()
        dt = now - rec.last_update
        if dt <= 0:
            return
        factor = self._decay_factor(dt)
        # decay alpha and beta toward the prior (1.0)
        rec.alpha = 1.0 + (rec.alpha - 1.0) * factor
        rec.beta = 1.0 + (rec.beta - 1.0) * factor
        rec.last_update = now

    def _get_record(self, subject: str, action: str) -> TrustRecord:
        key = (subject, action)
        rec = self.records.get(key)
        if rec is None:
            rec = TrustRecord()
            self.records[key] = rec
        else:
            self._decay_record(rec)
        return rec

    def record_result(self, subject: str, action: str, success: bool) -> None:
        """Record an observed invocation result: success=True for success, False for failure."""
        rec = self._get_record(subject, action)
        if success:
            rec.alpha += 1.0
        else:
            rec.beta += 1.0
        rec.last_update = now_ts()

    def get_posterior(self, subject: str, action: str) -> Tuple[float, float]:
        """Return (alpha, beta) for the subject/action after applying decay."""
        rec = self._get_record(subject, action)
        return rec.alpha, rec.beta

    def expected_trust(self, subject: str, action: str) -> float:
        alpha, beta = self.get_posterior(subject, action)
        return alpha / (alpha + beta) if (alpha + beta) > 0 else 0.0

    def confidence(self, subject: str, action: str) -> float:
        """Return a simple confidence metric derived from Beta variance.

        Confidence = 1 - variance, normalized to (0,1) with a conservative floor.
        """
        alpha, beta = self.get_posterior(subject, action)
        s = alpha + beta
        if s <= 0:
            return 0.0
        # variance of Beta distribution
        var = (alpha * beta) / ((s * s) * (s + 1.0))
        conf = 1.0 - var
        # clamp
        if conf < 0.0:
            conf = 0.0
        if conf > 1.0:
            conf = 1.0
        return conf


__all__ = ["TrustStore", "TrustRecord"]
