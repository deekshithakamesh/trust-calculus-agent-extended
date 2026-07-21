"""
trustcalc.analysis.metrics
==========================

Evaluation metrics for Trust Calculus.

Computes security, leakage and performance metrics
from attack analysis results.
"""

from __future__ import annotations

from dataclasses import dataclass

from .analyzer import AnalysisResult


@dataclass(slots=True)
class EvaluationMetrics:
    """
    Overall evaluation metrics.
    """

    success_rate: float
    block_rate: float
    leakage_rate: float
    security_score: float
    trust_score: float
    average_execution_time: float

    def to_dict(self) -> dict[str, float]:
        return {
            "success_rate": self.success_rate,
            "block_rate": self.block_rate,
            "leakage_rate": self.leakage_rate,
            "security_score": self.security_score,
            "trust_score": self.trust_score,
            "average_execution_time": self.average_execution_time,
        }


class MetricsAnalyzer:
    """
    Computes evaluation metrics from an AnalysisResult.
    """

    @staticmethod
    def compute(result: AnalysisResult) -> EvaluationMetrics:

        leakage_rate = (
            result.total_leakage / result.total_attacks
            if result.total_attacks
            else 0.0
        )

        security_score = (
            (result.block_rate * 100.0)
            - (leakage_rate * 10.0)
        )

        security_score = max(
            0.0,
            min(100.0, security_score),
        )

        trust_score = (
            security_score
            * (1.0 - result.success_rate)
        )

        return EvaluationMetrics(
            success_rate=result.success_rate,
            block_rate=result.block_rate,
            leakage_rate=leakage_rate,
            security_score=security_score,
            trust_score=trust_score,
            average_execution_time=result.average_execution_time,
        )