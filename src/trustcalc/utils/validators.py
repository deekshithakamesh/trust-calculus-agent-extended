"""
trustcalc.utils.validators
==========================

Validation utilities for the Trust Calculus framework.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterable


def validate_type(
    value: Any,
    expected_type: type | tuple[type, ...],
    name: str = "value",
) -> None:
    """
    Validate that a value is of the expected type.
    """
    if not isinstance(value, expected_type):
        expected = (
            expected_type.__name__
            if isinstance(expected_type, type)
            else ", ".join(t.__name__ for t in expected_type)
        )
        raise TypeError(
            f"{name} must be of type {expected}, "
            f"got {type(value).__name__}."
        )


def validate_not_none(
    value: Any,
    name: str = "value",
) -> None:
    """
    Ensure a value is not None.
    """
    if value is None:
        raise ValueError(f"{name} cannot be None.")


def validate_non_empty(
    value: str | Iterable[Any],
    name: str = "value",
) -> None:
    """
    Ensure a string or collection is non-empty.
    """
    if len(value) == 0:
        raise ValueError(f"{name} cannot be empty.")


def validate_range(
    value: float | int,
    minimum: float | int | None = None,
    maximum: float | int | None = None,
    name: str = "value",
) -> None:
    """
    Validate a numeric range.
    """
    if minimum is not None and value < minimum:
        raise ValueError(
            f"{name} must be >= {minimum}."
        )

    if maximum is not None and value > maximum:
        raise ValueError(
            f"{name} must be <= {maximum}."
        )


def validate_probability(
    value: float,
    name: str = "probability",
) -> None:
    """
    Validate a probability value.
    """
    validate_range(value, 0.0, 1.0, name)


def validate_positive(
    value: float | int,
    name: str = "value",
) -> None:
    """
    Validate that a value is positive.
    """
    if value <= 0:
        raise ValueError(
            f"{name} must be positive."
        )


def validate_identifier(
    identifier: str,
    name: str = "identifier",
) -> None:
    """
    Validate a Python-style identifier.
    """
    pattern = r"^[A-Za-z_][A-Za-z0-9_]*$"

    if not re.fullmatch(pattern, identifier):
        raise ValueError(
            f"Invalid {name}: {identifier}"
        )


def validate_path_exists(
    path: str | Path,
) -> Path:
    """
    Validate that a filesystem path exists.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(path)

    return path


def validate_file(
    path: str | Path,
    suffixes: tuple[str, ...] | None = None,
) -> Path:
    """
    Validate a file path.
    """
    path = validate_path_exists(path)

    if not path.is_file():
        raise ValueError(f"{path} is not a file.")

    if suffixes and path.suffix.lower() not in suffixes:
        raise ValueError(
            f"Unsupported file type: {path.suffix}"
        )

    return path


def validate_directory(
    path: str | Path,
) -> Path:
    """
    Validate a directory path.
    """
    path = validate_path_exists(path)

    if not path.is_dir():
        raise ValueError(
            f"{path} is not a directory."
        )

    return path


def validate_choice(
    value: Any,
    choices: Iterable[Any],
    name: str = "value",
) -> None:
    """
    Validate membership in a collection.
    """
    if value not in choices:
        raise ValueError(
            f"{name} must be one of {list(choices)}."
        )


def validate_callable(
    obj: Any,
    name: str = "callable",
) -> None:
    """
    Validate that an object is callable.
    """
    if not callable(obj):
        raise TypeError(
            f"{name} must be callable."
        )