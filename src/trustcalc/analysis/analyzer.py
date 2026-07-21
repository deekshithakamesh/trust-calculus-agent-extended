"""
trustcalc.analysis.analyzer
===========================

Core analysis engine for the Trust Calculus framework.

Collects evaluation results and computes aggregate
security, trust, and leakage metrics.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean
from typing import Any

from trustcalc.attacks.base import AttackResult


@dataclass(slots=True)
class AnalysisResult:
    """
    Aggregate analysis results.
    """

    total_attacks: int
    successful_attacks: int
    blocked_attacks: int

    success_rate: float
    block_rate: float

    total_leakage: float
    average_leakage: float

    average_execution_time: float

    categories: dict[str, int]

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_attacks": self.total_attacks,
            "successful_attacks": self.successful_attacks,
            "blocked_attacks": self.blocked_attacks,
            "success_rate": self.success_rate,
            "block_rate": self.block_rate,
            "total_leakage": self.total_leakage,
            "average_leakage": self.average_leakage,
            "average_execution_time": self.average_execution_time,
            "categories": self.categories,
            "metadata": self.metadata,
        }


class Analyzer:
    """
    Aggregates and analyzes attack results.
    """

    def __init__(self) -> None:
        self._results: list[AttackResult] = []

    # ---------------------------------------------------------

    def add_result(
        self,
        result: AttackResult,
    ) -> None:
        """
        Add a single attack result.
        """

        self._results.append(result)

    # ---------------------------------------------------------

    def add_results(
        self,
        results: list[AttackResult],
    ) -> None:
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

    def analyze(self) -> AnalysisResult:
        """
        Compute aggregate statistics.
        """

        total = len(self._results)

        if total == 0:
            return AnalysisResult(
                total_attacks=0,
                successful_attacks=0,
                blocked_attacks=0,
                success_rate=0.0,
                block_rate=0.0,
                total_leakage=0.0,
                average_leakage=0.0,
                average_execution_time=0.0,
                categories={},
            )

        successful = sum(
            r.success for r in self._results
        )

        blocked = sum(
            r.blocked for r in self._results
        )

        total_leakage = sum(
            r.leakage for r in self._results
        )

        avg_leakage = total_leakage / total

        avg_time = mean(
            r.execution_time
            for r in self._results
        )

        categories: dict[str, int] = {}

        for result in self._results:
            categories[result.category] = (
                categories.get(result.category, 0) + 1
            )

        return AnalysisResult(
            total_attacks=total,
            successful_attacks=successful,
            blocked_attacks=blocked,
            success_rate=successful / total,
            block_rate=blocked / total,
            total_leakage=total_leakage,
            average_leakage=avg_leakage,
            average_execution_time=avg_time,
            categories=categories,
        )

    # ---------------------------------------------------------

    def summary(self) -> dict[str, Any]:
        """
        Return the analysis as a dictionary.
        """

        return self.analyze().to_dict()

    # ---------------------------------------------------------

    def __len__(self) -> int:
        return len(self._results)

    def __iter__(self):
        return iter(self._results)