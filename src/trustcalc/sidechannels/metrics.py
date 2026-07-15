"""
trustcalc.sidechannels.metrics
==============================

Evaluation metrics for covert-channel experiments.

Aggregates multiple experiment results into publication-
ready statistics.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean, median
from typing import Any


@dataclass(slots=True)
class SideChannelMetrics:
    """
    Aggregate metrics for covert-channel evaluations.
    """

    experiments: list[dict[str, Any]] = field(
        default_factory=list
    )

    # ---------------------------------------------------------
    # Recording
    # ---------------------------------------------------------

    def add_result(
        self,
        *,
        leakage: float,
        capacity: float,
        success: bool,
        mitigation: float = 0.0,
        error_rate: float = 0.0,
    ) -> None:
        """
        Record the outcome of a single experiment.
        """

        self.experiments.append(
            {
                "leakage": leakage,
                "capacity": capacity,
                "success": success,
                "mitigation": mitigation,
                "error_rate": error_rate,
            }
        )

    # ---------------------------------------------------------
    # Counts
    # ---------------------------------------------------------

    def total_experiments(self) -> int:
        return len(self.experiments)

    def successful_experiments(self) -> int:
        return sum(
            experiment["success"]
            for experiment in self.experiments
        )

    def failed_experiments(self) -> int:
        return (
            self.total_experiments()
            - self.successful_experiments()
        )

    # ---------------------------------------------------------
    # Aggregate Statistics
    # ---------------------------------------------------------

    def average_leakage(self) -> float:

        if not self.experiments:
            return 0.0

        return mean(
            experiment["leakage"]
            for experiment in self.experiments
        )

    def median_leakage(self) -> float:

        if not self.experiments:
            return 0.0

        return median(
            experiment["leakage"]
            for experiment in self.experiments
        )

    def average_capacity(self) -> float:

        if not self.experiments:
            return 0.0

        return mean(
            experiment["capacity"]
            for experiment in self.experiments
        )

    def average_error_rate(self) -> float:

        if not self.experiments:
            return 0.0

        return mean(
            experiment["error_rate"]
            for experiment in self.experiments
        )

    def average_mitigation(self) -> float:

        if not self.experiments:
            return 0.0

        return mean(
            experiment["mitigation"]
            for experiment in self.experiments
        )

    def success_rate(self) -> float:

        total = self.total_experiments()

        if total == 0:
            return 0.0

        return (
            self.successful_experiments()
            / total
        )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    def summary(self) -> dict[str, Any]:
        """
        Produce an aggregate evaluation summary.
        """

        return {
            "experiments": self.total_experiments(),
            "successful_experiments": self.successful_experiments(),
            "failed_experiments": self.failed_experiments(),
            "success_rate": self.success_rate(),
            "average_leakage": self.average_leakage(),
            "median_leakage": self.median_leakage(),
            "average_capacity": self.average_capacity(),
            "average_error_rate": self.average_error_rate(),
            "average_mitigation": self.average_mitigation(),
        }

    # ---------------------------------------------------------
    # Maintenance
    # ---------------------------------------------------------

    def clear(self) -> None:
        """
        Remove all recorded experiments.
        """

        self.experiments.clear()

    def __len__(self) -> int:
        return len(self.experiments)