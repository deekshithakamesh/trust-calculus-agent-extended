"""
trustcalc.evaluation.statistics
===============================

Statistical analysis for evaluation experiments.

Aggregates experiment results into summary statistics.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import mean, median
from typing import Any


@dataclass(slots=True)
class EvaluationStatistics:
    """
    Statistical analysis of evaluation results.
    """

    # ---------------------------------------------------------
    # Basic Statistics
    # ---------------------------------------------------------

    def average(
        self,
        values: list[float],
    ) -> float:

        return mean(values) if values else 0.0

    # ---------------------------------------------------------

    def median(
        self,
        values: list[float],
    ) -> float:

        return median(values) if values else 0.0

    # ---------------------------------------------------------

    def minimum(
        self,
        values: list[float],
    ) -> float:

        return min(values) if values else 0.0

    # ---------------------------------------------------------

    def maximum(
        self,
        values: list[float],
    ) -> float:

        return max(values) if values else 0.0

    # ---------------------------------------------------------

    def variance(
        self,
        values: list[float],
    ) -> float:

        if len(values) < 2:
            return 0.0

        avg = mean(values)

        return sum(
            (x - avg) ** 2
            for x in values
        ) / len(values)

    # ---------------------------------------------------------

    def standard_deviation(
        self,
        values: list[float],
    ) -> float:

        return sqrt(
            self.variance(values)
        )

    # ---------------------------------------------------------
    # Success Metrics
    # ---------------------------------------------------------

    def success_rate(
        self,
        successes: int,
        total: int,
    ) -> float:

        if total == 0:
            return 0.0

        return successes / total

    # ---------------------------------------------------------
    # Aggregate Summary
    # ---------------------------------------------------------

    def summarize(
        self,
        experiments: list[dict[str, Any]],
    ) -> dict[str, Any]:

        if not experiments:
            return {
                "count": 0,
                "average_leakage": 0.0,
                "median_leakage": 0.0,
                "min_leakage": 0.0,
                "max_leakage": 0.0,
                "std_leakage": 0.0,
                "success_rate": 0.0,
            }

        leakage = [
            experiment["bit_leakage"]
            for experiment in experiments
        ]

        successes = sum(
            experiment["bit_leakage"] > 0
            for experiment in experiments
        )

        return {
            "count": len(experiments),
            "average_leakage": self.average(leakage),
            "median_leakage": self.median(leakage),
            "min_leakage": self.minimum(leakage),
            "max_leakage": self.maximum(leakage),
            "std_leakage": self.standard_deviation(
                leakage
            ),
            "success_rate": self.success_rate(
                successes,
                len(experiments),
            ),
        }