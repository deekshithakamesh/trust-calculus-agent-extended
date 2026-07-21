"""
trustcalc.analysis.leakage
==========================

Information leakage analysis utilities.

Provides helper methods for computing leakage-related
metrics from attack evaluation results.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Iterable

from trustcalc.attacks.base import AttackResult


@dataclass(slots=True)
class LeakageMetrics:
    """
    Aggregate leakage statistics.
    """

    total_leakage: float
    average_leakage: float
    maximum_leakage: float
    minimum_leakage: float
    leakage_rate: float

    def to_dict(self) -> dict[str, float]:
        return {
            "total_leakage": self.total_leakage,
            "average_leakage": self.average_leakage,
            "maximum_leakage": self.maximum_leakage,
            "minimum_leakage": self.minimum_leakage,
            "leakage_rate": self.leakage_rate,
        }


class LeakageAnalyzer:
    """
    Computes information leakage metrics.
    """

    def __init__(self, results: Iterable[AttackResult] | None = None):
        self._results = list(results) if results else []

    # ---------------------------------------------------------

    def add_result(self, result: AttackResult) -> None:
        """
        Add a single attack result.
        """
        self._results.append(result)

    # ---------------------------------------------------------

    def add_results(self, results: Iterable[AttackResult]) -> None:
        """
        Add multiple attack results.
        """
        self._results.extend(results)

    # ---------------------------------------------------------

    def clear(self) -> None:
        """
        Remove all stored results.
        """
        self._results.clear()

    # ---------------------------------------------------------

    @property
    def results(self) -> list[AttackResult]:
        return list(self._results)

    # ---------------------------------------------------------

    def total_leakage(self) -> float:
        return sum(result.leakage for result in self._results)

    # ---------------------------------------------------------

    def average_leakage(self) -> float:
        if not self._results:
            return 0.0

        return mean(result.leakage for result in self._results)

    # ---------------------------------------------------------

    def maximum_leakage(self) -> float:
        if not self._results:
            return 0.0

        return max(result.leakage for result in self._results)

    # ---------------------------------------------------------

    def minimum_leakage(self) -> float:
        if not self._results:
            return 0.0

        return min(result.leakage for result in self._results)

    # ---------------------------------------------------------

    def leakage_rate(self) -> float:
        """
        Fraction of attacks that leaked information.
        """

        if not self._results:
            return 0.0

        leaked = sum(
            result.leakage > 0
            for result in self._results
        )

        return leaked / len(self._results)

    # ---------------------------------------------------------

    def category_leakage(self) -> dict[str, float]:
        """
        Total leakage grouped by attack category.
        """

        categories: dict[str, float] = {}

        for result in self._results:
            categories[result.category] = (
                categories.get(result.category, 0.0)
                + result.leakage
            )

        return categories

    # ---------------------------------------------------------

    def analyze(self) -> LeakageMetrics:
        """
        Compute aggregate leakage statistics.
        """

        return LeakageMetrics(
            total_leakage=self.total_leakage(),
            average_leakage=self.average_leakage(),
            maximum_leakage=self.maximum_leakage(),
            minimum_leakage=self.minimum_leakage(),
            leakage_rate=self.leakage_rate(),
        )