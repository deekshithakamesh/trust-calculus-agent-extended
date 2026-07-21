"""
trustcalc.analysis.plots
========================

Plotting utilities for Trust Calculus.

Uses matplotlib to generate publication-ready figures.
"""

from __future__ import annotations

from pathlib import Path

from .analyzer import AnalysisResult


class PlotGenerator:
    """
    Generates plots from AnalysisResult.
    """

    def __init__(
        self,
        output_dir: str = "plots",
    ) -> None:

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    @staticmethod
    def _plt():
        try:
            import matplotlib.pyplot as plt

            return plt

        except ImportError as exc:
            raise RuntimeError(
                "matplotlib is required."
            ) from exc

    def attack_outcomes(
        self,
        result: AnalysisResult,
        filename: str = "attack_outcomes.png",
    ) -> Path:

        plt = self._plt()

        fig, ax = plt.subplots()

        ax.bar(
            ["Successful", "Blocked"],
            [
                result.successful_attacks,
                result.blocked_attacks,
            ],
        )

        ax.set_title("Attack Outcomes")
        ax.set_ylabel("Count")

        path = self.output_dir / filename

        fig.tight_layout()
        fig.savefig(path)
        plt.close(fig)

        return path

    def leakage(
        self,
        result: AnalysisResult,
        filename: str = "leakage.png",
    ) -> Path:

        plt = self._plt()

        fig, ax = plt.subplots()

        ax.bar(
            ["Total", "Average"],
            [
                result.total_leakage,
                result.average_leakage,
            ],
        )

        ax.set_title("Leakage")
        ax.set_ylabel("Leakage")

        path = self.output_dir / filename

        fig.tight_layout()
        fig.savefig(path)
        plt.close(fig)

        return path

    def categories(
        self,
        result: AnalysisResult,
        filename: str = "categories.png",
    ) -> Path:

        plt = self._plt()

        fig, ax = plt.subplots()

        ax.bar(
            list(result.categories.keys()),
            list(result.categories.values()),
        )

        ax.set_title("Attack Categories")
        ax.tick_params(
            axis="x",
            rotation=45,
        )

        path = self.output_dir / filename

        fig.tight_layout()
        fig.savefig(path)
        plt.close(fig)

        return path

    def execution_time(
        self,
        result: AnalysisResult,
        filename: str = "execution_time.png",
    ) -> Path:

        plt = self._plt()

        fig, ax = plt.subplots()

        ax.bar(
            ["Average"],
            [result.average_execution_time],
        )

        ax.set_title("Execution Time")
        ax.set_ylabel("Seconds")

        path = self.output_dir / filename

        fig.tight_layout()
        fig.savefig(path)
        plt.close(fig)

        return path

    def generate_all(
        self,
        result: AnalysisResult,
    ) -> dict[str, Path]:

        return {
            "attack_outcomes": self.attack_outcomes(result),
            "leakage": self.leakage(result),
            "categories": self.categories(result),
            "execution_time": self.execution_time(result),
        }