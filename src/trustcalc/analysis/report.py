"""
trustcalc.analysis.report
=========================

Report generation utilities for the Trust Calculus framework.

Creates Markdown, JSON, and plain-text summaries of
analysis results.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .analyzer import AnalysisResult


@dataclass(slots=True)
class Report:
    """
    Represents an analysis report.
    """

    title: str
    created_at: str
    summary: AnalysisResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "created_at": self.created_at,
            "summary": self.summary.to_dict(),
        }


class ReportGenerator:
    """
    Generates reports from analysis results.
    """

    def __init__(
        self,
        title: str = "Trust Calculus Analysis Report",
    ) -> None:
        self.title = title

    # ---------------------------------------------------------

    def generate(
        self,
        result: AnalysisResult,
    ) -> Report:
        """
        Create a Report object.
        """

        return Report(
            title=self.title,
            created_at=datetime.now().isoformat(),
            summary=result,
        )

    # ---------------------------------------------------------

    def to_json(
        self,
        report: Report,
        indent: int = 4,
    ) -> str:
        """
        Export report as JSON.
        """

        return json.dumps(
            report.to_dict(),
            indent=indent,
        )

    # ---------------------------------------------------------

    def to_markdown(
        self,
        report: Report,
    ) -> str:
        """
        Export report as Markdown.
        """

        summary = report.summary

        return f"""# {report.title}

**Generated:** {report.created_at}

## Summary

| Metric | Value |
|--------|------:|
| Total Attacks | {summary.total_attacks} |
| Successful Attacks | {summary.successful_attacks} |
| Blocked Attacks | {summary.blocked_attacks} |
| Success Rate | {summary.success_rate:.2%} |
| Block Rate | {summary.block_rate:.2%} |
| Total Leakage | {summary.total_leakage:.4f} |
| Average Leakage | {summary.average_leakage:.4f} |
| Average Execution Time | {summary.average_execution_time:.6f}s |

## Attack Categories

{self._format_categories(summary.categories)}
"""

    # ---------------------------------------------------------

    def to_text(
        self,
        report: Report,
    ) -> str:
        """
        Export report as plain text.
        """

        summary = report.summary

        return (
            f"{report.title}\n"
            f"{'=' * len(report.title)}\n\n"
            f"Generated: {report.created_at}\n\n"
            f"Total Attacks      : {summary.total_attacks}\n"
            f"Successful Attacks : {summary.successful_attacks}\n"
            f"Blocked Attacks    : {summary.blocked_attacks}\n"
            f"Success Rate       : {summary.success_rate:.2%}\n"
            f"Block Rate         : {summary.block_rate:.2%}\n"
            f"Total Leakage      : {summary.total_leakage:.4f}\n"
            f"Average Leakage    : {summary.average_leakage:.4f}\n"
            f"Average Time       : "
            f"{summary.average_execution_time:.6f}s\n"
        )

    # ---------------------------------------------------------

    @staticmethod
    def _format_categories(
        categories: dict[str, int],
    ) -> str:
        if not categories:
            return "_No attack categories available._"

        return "\n".join(
            f"- **{name}**: {count}"
            for name, count in sorted(categories.items())
        )