"""
trustcalc.analysis.statistics
=============================

Statistical analysis utilities for Trust Calculus.

Provides reusable statistical summaries for attack
evaluation results.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, median, pstdev, variance
from typing import Iterable

from trustcalc.attacks.base import AttackResult


@dataclass(slots=True)
class StatisticsSummary:
    """
    Statistical summary of attack results.
    """

    count: int
    mean_execution_time: float
    median_execution_time: float
    std_execution_time: float
    variance_execution_time: float
    success_rate: float
    block_rate: float

    def to_dict(self) -> dict[str, float | int]:
        return {
            "count": self.count,
            "mean_execution_time": self.mean_execution_time,
            "median_execution_time": self.median_execution_time,
            "std_execution_time": self.std_execution_time,
            "variance_execution_time": self.variance_execution_time,
            "success_rate": self.success_rate,
            "block_rate": self.block_rate,
        }


class StatisticsAnalyzer:
    """
    Computes statistical summaries for attack results.
    """

    def __init__(
        self,
        results: Iterable[AttackResult] | None = None,
    ) -> None:
        self._results = list(results) if results else []

    # ---------------------------------------------------------

    def add_result(
        self,
        result: AttackResult,
    ) -> None:
        self._results.append(result)

    # ---------------------------------------------------------

    def add_results(
        self,
        results: Iterable[AttackResult],
    ) -> None:
        self._results.extend(results)

    # ---------------------------------------------------------

    def clear(self) -> None:
        self._results.clear()

    # ---------------------------------------------------------

    @property
    def results(self) -> list[AttackResult]:
        return list(self._results)

    # ---------------------------------------------------------

    def execution_times(self) -> list[float]:
        return [
            result.execution_time
            for result in self._results
        ]

    # ---------------------------------------------------------

    def success_rate(self) -> float:
        if not self._results:
            return 0.0

        return (
            sum(result.success for result in self._results)
            / len(self._results)
        )

    # ---------------------------------------------------------

    def block_rate(self) -> float:
        if not self._results:
            return 0.0

        return (
            sum(result.blocked for result in self._results)
            / len(self._results)
        )

    # ---------------------------------------------------------

    def summarize(self) -> StatisticsSummary:

        times = self.execution_times()

        if not times:
            return StatisticsSummary(
                count=0,
                mean_execution_time=0.0,
                median_execution_time=0.0,
                std_execution_time=0.0,
                variance_execution_time=0.0,
                success_rate=0.0,
                block_rate=0.0,
            )

        return StatisticsSummary(
            count=len(times),
            mean_execution_time=mean(times),
            median_execution_time=median(times),
            std_execution_time=(
                pstdev(times)
                if len(times) > 1
                else 0.0
            ),
            variance_execution_time=(
                variance(times)
                if len(times) > 1
                else 0.0
            ),
            success_rate=self.success_rate(),
            block_rate=self.block_rate(),
        )