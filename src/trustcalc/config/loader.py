"""
trustcalc.config.loader
=======================

Configuration loader for the Trust Calculus framework.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

from .settings import (
    LoggingConfig,
    OutputConfig,
    RuntimeConfig,
    SecurityConfig,
    TrustCalcConfig,
)


class ConfigLoader:
    """
    Loads Trust Calculus configuration.
    """

    @staticmethod
    def from_dict(data: dict[str, Any]) -> TrustCalcConfig:
        """
        Create configuration from a dictionary.
        """

        runtime = RuntimeConfig(
            **data.get("runtime", {})
        )

        security = SecurityConfig(
            **data.get("security", {})
        )

        logging = LoggingConfig(
            **data.get("logging", {})
        )

        output_data = data.get("output", {})

        output = OutputConfig(
            root=Path(output_data.get("root", "output")),
            reports=Path(output_data.get("reports", "output/reports")),
            plots=Path(output_data.get("plots", "output/plots")),
            logs=Path(output_data.get("logs", "output/logs")),
            exports=Path(output_data.get("exports", "output/exports")),
        )

        return TrustCalcConfig(
            project_name=data.get(
                "project_name",
                "Trust Calculus",
            ),
            version=data.get(
                "version",
                "1.0.0",
            ),
            runtime=runtime,
            security=security,
            logging=logging,
            output=output,
        )

    @classmethod
    def from_json(
        cls,
        filename: str | Path,
    ) -> TrustCalcConfig:
        """
        Load configuration from a JSON file.
        """

        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        return cls.from_dict(data)

    @classmethod
    def from_yaml(
        cls,
        filename: str | Path,
    ) -> TrustCalcConfig:
        """
        Load configuration from a YAML file.
        """

        if yaml is None:
            raise ImportError(
                "PyYAML is required to load YAML configuration."
            )

        with open(filename, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        return cls.from_dict(data)

    @classmethod
    def load(
        cls,
        filename: str | Path,
    ) -> TrustCalcConfig:
        """
        Automatically detect configuration format.
        """

        filename = Path(filename)

        suffix = filename.suffix.lower()

        if suffix == ".json":
            return cls.from_json(filename)

        if suffix in (".yaml", ".yml"):
            return cls.from_yaml(filename)

        raise ValueError(
            f"Unsupported configuration format: {suffix}"
        )