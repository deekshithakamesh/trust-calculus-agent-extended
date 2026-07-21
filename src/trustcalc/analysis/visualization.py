"""
trustcalc.analysis.visualization
================================

High-level visualization manager for Trust Calculus.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .analyzer import AnalysisResult
from .metrics import EvaluationMetrics, MetricsAnalyzer
from .plots import PlotGenerator


class VisualizationManager:
    """
    Coordinates metric computation and plot generation.
    """

    def __init__(
        self,
        output_dir: str = "plots",
    ) -> None:

        self.output_dir = Path(output_dir)

        self.metric_analyzer = MetricsAnalyzer()
        self.plot_generator = PlotGenerator(output_dir)

    # ---------------------------------------------------------

    def compute_metrics(
        self,
        result: AnalysisResult,
    ) -> EvaluationMetrics:
        """
        Compute evaluation metrics.
        """
        return self.metric_analyzer.compute(result)

    # ---------------------------------------------------------

    def generate_plots(
        self,
        result: AnalysisResult,
    ) -> dict[str, Path]:
        """
        Generate all plots.
        """
        return self.plot_generator.generate_all(result)

    # ---------------------------------------------------------

    def generate_dashboard(
        self,
        result: AnalysisResult,
    ) -> dict[str, Any]:
        """
        Generate complete visualization artifacts.
        """

        metrics = self.compute_metrics(result)

        figures = self.generate_plots(result)

        return {
            "metrics": metrics,
            "plots": figures,
        }

    # ---------------------------------------------------------

    def export(
        self,
        result: AnalysisResult,
    ) -> dict[str, Any]:
        """
        Generate all visual outputs.

        Alias for generate_dashboard().
        """
        return self.generate_dashboard(result)