"""
trustcalc.config.paths
======================

Path management utilities for the Trust Calculus framework.
"""

from __future__ import annotations

from pathlib import Path

from .settings import OutputConfig


class ProjectPaths:
    """
    Manages project output directories.
    """

    def __init__(
        self,
        output: OutputConfig,
    ) -> None:
        self.output = output

    # ---------------------------------------------------------

    @property
    def root(self) -> Path:
        return self.output.root

    @property
    def reports(self) -> Path:
        return self.output.reports

    @property
    def plots(self) -> Path:
        return self.output.plots

    @property
    def logs(self) -> Path:
        return self.output.logs

    @property
    def exports(self) -> Path:
        return self.output.exports

    # ---------------------------------------------------------

    def create(self) -> None:
        """
        Create all configured output directories.
        """

        for directory in (
            self.root,
            self.reports,
            self.plots,
            self.logs,
            self.exports,
        ):
            directory.mkdir(
                parents=True,
                exist_ok=True,
            )

    # ---------------------------------------------------------

    def exists(self) -> bool:
        """
        Return True if all configured directories exist.
        """

        return all(
            directory.exists()
            for directory in (
                self.root,
                self.reports,
                self.plots,
                self.logs,
                self.exports,
            )
        )

    # ---------------------------------------------------------

    def as_dict(self) -> dict[str, str]:
        """
        Return all paths as strings.
        """

        return {
            "root": str(self.root),
            "reports": str(self.reports),
            "plots": str(self.plots),
            "logs": str(self.logs),
            "exports": str(self.exports),
        }

    # ---------------------------------------------------------

    def resolve(self) -> dict[str, Path]:
        """
        Return resolved absolute paths.
        """

        return {
            "root": self.root.resolve(),
            "reports": self.reports.resolve(),
            "plots": self.plots.resolve(),
            "logs": self.logs.resolve(),
            "exports": self.exports.resolve(),
        }

    # ---------------------------------------------------------

    def clear(self) -> None:
        """
        Remove empty output directories.

        Non-empty directories are left untouched.
        """

        for directory in (
            self.exports,
            self.logs,
            self.plots,
            self.reports,
            self.root,
        ):
            try:
                directory.rmdir()
            except OSError:
                pass