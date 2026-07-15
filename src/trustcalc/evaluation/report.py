"""
trustcalc.evaluation.report
===========================

Evaluation report generation.

Produces structured reports from evaluation experiments.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from trustcalc.evaluation.statistics import EvaluationStatistics


@dataclass(slots=True)
class EvaluationReport:
    """
    Generate evaluation reports.
    """

    statistics: EvaluationStatistics = field(
        default_factory=EvaluationStatistics
    )

    title: str = "Trust Calculus Evaluation Report"

    author: str = "Trust Calculus Framework"

    # ---------------------------------------------------------
    # Report Generation
    # ---------------------------------------------------------

    def generate(
        self,
        experiments: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Generate a structured report.
        """

        stats = self.statistics.summarize(
            experiments
        )

        return {
            "title": self.title,
            "author": self.author,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": stats,
            "experiments": experiments,
            "conclusion": self._conclusion(stats),
        }

    # ---------------------------------------------------------
    # Export
    # ---------------------------------------------------------

    def to_markdown(
        self,
        report: dict[str, Any],
    ) -> str:
        """
        Convert a report into Markdown.
        """

        summary = report["summary"]

        lines = [
            f"# {report['title']}",
            "",
            f"**Author:** {report['author']}",
            f"**Generated:** {report['generated_at']}",
            "",
            "## Summary",
            "",
            f"- Experiments: {summary['count']}",
            f"- Average Leakage: {summary['average_leakage']:.3f}",
            f"- Median Leakage: {summary['median_leakage']:.3f}",
            f"- Success Rate: {summary['success_rate']:.3f}",
            f"- Standard Deviation: {summary['std_leakage']:.3f}",
            "",
            "## Conclusion",
            "",
            report["conclusion"],
        ]

        return "\n".join(lines)

    # ---------------------------------------------------------
    # Internal
    # ---------------------------------------------------------

    def _conclusion(
        self,
        summary: dict[str, Any],
    ) -> str:
        """
        Generate a simple textual conclusion.
        """

        leakage = summary["average_leakage"]

        if leakage < 0.10:
            return (
                "Mitigation is highly effective. "
                "Only minimal information leakage was observed."
            )

        if leakage < 0.30:
            return (
                "Mitigation substantially reduces covert "
                "channel capacity."
            )

        if leakage < 0.60:
            return (
                "Moderate leakage remains after mitigation."
            )

        return (
            "Significant covert-channel leakage remains. "
            "Additional mitigations are recommended."
        )