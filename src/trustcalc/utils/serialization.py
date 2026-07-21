"""
trustcalc.utils.serialization
=============================

Serialization utilities for the Trust Calculus framework.
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None


class SerializationError(Exception):
    """
    Raised when serialization or deserialization fails.
    """


class Serializer:
    """
    Utility class for serializing Python objects.
    """

    @staticmethod
    def to_dict(obj: Any) -> dict[str, Any]:
        """
        Convert an object to a dictionary.
        """

        if hasattr(obj, "to_dict"):
            return obj.to_dict()

        if is_dataclass(obj):
            return asdict(obj)

        if isinstance(obj, dict):
            return obj

        raise SerializationError(
            f"Cannot serialize object of type {type(obj).__name__}"
        )

    @classmethod
    def to_json(
        cls,
        obj: Any,
        indent: int = 4,
    ) -> str:
        """
        Serialize an object to JSON.
        """

        return json.dumps(
            cls.to_dict(obj),
            indent=indent,
            default=str,
        )

    @classmethod
    def save_json(
        cls,
        obj: Any,
        filename: str | Path,
        indent: int = 4,
    ) -> None:
        """
        Save an object as a JSON file.
        """

        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            json.dump(
                cls.to_dict(obj),
                file,
                indent=indent,
                default=str,
            )

    @staticmethod
    def load_json(
        filename: str | Path,
    ) -> dict[str, Any]:
        """
        Load a JSON file.
        """

        with Path(filename).open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    @classmethod
    def to_yaml(
        cls,
        obj: Any,
    ) -> str:
        """
        Serialize an object to YAML.
        """

        if yaml is None:
            raise SerializationError(
                "PyYAML is not installed."
            )

        return yaml.safe_dump(
            cls.to_dict(obj),
            sort_keys=False,
        )

    @classmethod
    def save_yaml(
        cls,
        obj: Any,
        filename: str | Path,
    ) -> None:
        """
        Save an object as YAML.
        """

        if yaml is None:
            raise SerializationError(
                "PyYAML is not installed."
            )

        path = Path(filename)
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with path.open(
            "w",
            encoding="utf-8",
        ) as file:
            yaml.safe_dump(
                cls.to_dict(obj),
                file,
                sort_keys=False,
            )

    @staticmethod
    def load_yaml(
        filename: str | Path,
    ) -> dict[str, Any]:
        """
        Load a YAML file.
        """

        if yaml is None:
            raise SerializationError(
                "PyYAML is not installed."
            )

        with Path(filename).open(
            "r",
            encoding="utf-8",
        ) as file:
            return yaml.safe_load(file)