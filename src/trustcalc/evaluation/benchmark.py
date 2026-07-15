"""
trustcalc.evaluation.benchmark
==============================

Benchmark suite for Trust Calculus.

Defines reusable benchmark scenarios for evaluating
covert-channel attacks and mitigation strategies.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from trustcalc.evaluation.experiment import Experiment
from trustcalc.evaluation.report import EvaluationReport
from trustcalc.evaluation.runner import EvaluationRunner


@dataclass(slots=True)
class BenchmarkSuite:
    """
    Benchmark suite for Trust Calculus.
    """

    runner: EvaluationRunner = field(
        default_factory=EvaluationRunner
    )

    reporter: EvaluationReport = field(
        default_factory=EvaluationReport
    )

    experiments: list[Experiment] = field(
        default_factory=list
    )

    # ---------------------------------------------------------
    # Experiment Management
    # ---------------------------------------------------------

    def add(
        self,
        experiment: Experiment,
    ) -> None:
        """
        Add an experiment to the benchmark suite.
        """

        self.experiments.append(experiment)

    # ---------------------------------------------------------

    def clear(self) -> None:
        """
        Remove all configured experiments.
        """

        self.experiments.clear()
        self.runner.clear()

    # ---------------------------------------------------------
    # Benchmark Execution
    # ---------------------------------------------------------

    def run(self) -> dict[str, Any]:
        """
        Execute all configured experiments.
        """

        self.runner.clear()

        results = self.runner.run_suite(
            [
                experiment.to_dict()
                for experiment in self.experiments
            ]
        )

        report = self.reporter.generate(results)

        return {
            "results": results,
            "summary": self.runner.summary(),
            "report": report,
        }

    # ---------------------------------------------------------
    # Default Benchmarks
    # ---------------------------------------------------------

    def load_default_suite(self) -> None:
        """
        Load a representative benchmark suite.
        """

        self.clear()

        self.add(
            Experiment(
                name="Formatting Channel",
                attack="formatting",
                transmitted_bits=128,
                recovered_bits=120,
                duration_seconds=1.2,
                mitigation_before=1.0,
                mitigation_after=0.35,
            )
        )

        self.add(
            Experiment(
                name="Whitespace Channel",
                attack="whitespace",
                transmitted_bits=128,
                recovered_bits=82,
                duration_seconds=1.1,
                mitigation_before=1.0,
                mitigation_after=0.22,
            )
        )

        self.add(
            Experiment(
                name="Timing Channel",
                attack="timing",
                transmitted_bits=128,
                recovered_bits=55,
                duration_seconds=2.8,
                mitigation_before=1.0,
                mitigation_after=0.12,
            )
        )

        self.add(
            Experiment(
                name="Synonym Channel",
                attack="synonym",
                transmitted_bits=128,
                recovered_bits=101,
                duration_seconds=1.4,
                mitigation_before=1.0,
                mitigation_after=0.41,
            )
        )

    # ---------------------------------------------------------

    @property
    def size(self) -> int:
        """
        Number of configured experiments.
        """

        return len(self.experiments)