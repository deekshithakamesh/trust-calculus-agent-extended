"""
trustcalc.evaluation.runner
===========================

Evaluation runner.

Coordinates attack execution, mitigation, leakage
estimation, and metric collection.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from trustcalc.sidechannels.leakage_estimator import LeakageEstimator
from trustcalc.sidechannels.metrics import SideChannelMetrics


@dataclass(slots=True)
class EvaluationRunner:
    """
    Runs evaluation experiments.

    The runner coordinates experiments but performs no
    attack logic itself.
    """

    estimator: LeakageEstimator = field(
        default_factory=LeakageEstimator
    )

    metrics: SideChannelMetrics = field(
        default_factory=SideChannelMetrics
    )

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def run_experiment(
        self,
        *,
        attack_name: str,
        transmitted_bits: int,
        recovered_bits: int,
        duration_seconds: float,
        mitigation_before: float = 0.0,
        mitigation_after: float = 0.0,
    ) -> dict[str, Any]:
        """
        Execute a single experiment.
        """

        summary = self.estimator.summarize(
            transmitted_bits=transmitted_bits,
            recovered_bits=recovered_bits,
            duration_seconds=duration_seconds,
        )

        mitigation = (
            self.estimator.mitigation_effectiveness(
                mitigation_before,
                mitigation_after,
            )
        )

        self.metrics.add_result(
            leakage=summary["bit_leakage"],
            capacity=summary["channel_capacity"],
            success=recovered_bits > 0,
            mitigation=mitigation,
            error_rate=summary["bit_error_rate"],
        )

        return {
            "attack": attack_name,
            **summary,
            "mitigation": mitigation,
        }

    # ---------------------------------------------------------

    def run_suite(
        self,
        experiments: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Execute a collection of experiments.
        """

        results: list[dict[str, Any]] = []

        for experiment in experiments:

            results.append(
                self.run_experiment(**experiment)
            )

        return results

    # ---------------------------------------------------------

    def summary(self) -> dict[str, Any]:
        """
        Aggregate results from all experiments.
        """

        return self.metrics.summary()

    # ---------------------------------------------------------

    def clear(self) -> None:
        """
        Reset evaluation state.
        """

        self.metrics.clear()

    # ---------------------------------------------------------

    @property
    def experiment_count(self) -> int:
        """
        Number of completed experiments.
        """

        return len(self.metrics)