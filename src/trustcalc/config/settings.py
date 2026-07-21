"""
trustcalc.config.settings
=========================

Configuration models for the Trust Calculus framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class RuntimeConfig:
    """
    Runtime configuration.
    """

    max_workers: int = 4
    timeout: float = 30.0
    enable_async: bool = True
    verbose: bool = False


@dataclass(slots=True)
class SecurityConfig:
    """
    Security configuration.
    """

    allow_privilege_escalation: bool = False
    enable_policy_engine: bool = True
    detect_side_channels: bool = True
    max_leakage: float = 0.0
    trust_threshold: float = 0.80


@dataclass(slots=True)
class LoggingConfig:
    """
    Logging configuration.
    """

    enabled: bool = True
    level: str = "INFO"
    log_to_file: bool = True
    filename: str = "trustcalc.log"


@dataclass(slots=True)
class OutputConfig:
    """
    Output directories.
    """

    root: Path = Path("output")
    reports: Path = Path("output/reports")
    plots: Path = Path("output/plots")
    logs: Path = Path("output/logs")
    exports: Path = Path("output/exports")


@dataclass(slots=True)
class TrustCalcConfig:
    """
    Top-level configuration object.
    """

    project_name: str = "Trust Calculus"
    version: str = "1.0.0"

    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary.
        """

        return {
            "project_name": self.project_name,
            "version": self.version,
            "runtime": vars(self.runtime),
            "security": vars(self.security),
            "logging": vars(self.logging),
            "output": {
                k: str(v)
                for k, v in vars(self.output).items()
            },
        }