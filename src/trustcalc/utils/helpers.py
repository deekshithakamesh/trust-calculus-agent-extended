"""
trustcalc.utils.helpers
=======================

General helper utilities for the Trust Calculus framework.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any


def generate_uuid() -> str:
    """
    Generate a UUID4 string.
    """
    return str(uuid.uuid4())


def timestamp() -> str:
    """
    Return the current UTC timestamp in ISO-8601 format.
    """
    return datetime.now(timezone.utc).isoformat()


def flatten_dict(
    data: dict[str, Any],
    parent_key: str = "",
    separator: str = ".",
) -> dict[str, Any]:
    """
    Flatten a nested dictionary.

    Example:
        {"a": {"b": 1}}
        ->
        {"a.b": 1}
    """

    items: dict[str, Any] = {}

    for key, value in data.items():
        new_key = (
            f"{parent_key}{separator}{key}"
            if parent_key
            else key
        )

        if isinstance(value, dict):
            items.update(
                flatten_dict(
                    value,
                    new_key,
                    separator,
                )
            )
        else:
            items[new_key] = value

    return items


def deep_update(
    original: dict[str, Any],
    updates: dict[str, Any],
) -> dict[str, Any]:
    """
    Recursively update a dictionary.
    """

    result = original.copy()

    for key, value in updates.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = deep_update(
                result[key],
                value,
            )
        else:
            result[key] = value

    return result


def ensure_list(value: Any) -> list[Any]:
    """
    Ensure a value is returned as a list.
    """

    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    return [value]


def chunks(
    iterable: list[Any],
    size: int,
):
    """
    Yield successive chunks from a list.
    """

    if size <= 0:
        raise ValueError(
            "Chunk size must be positive."
        )

    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


def safe_get(
    mapping: dict[str, Any],
    key: str,
    default: Any = None,
) -> Any:
    """
    Safe dictionary lookup.
    """

    return mapping.get(key, default)


def remove_none(
    mapping: dict[str, Any],
) -> dict[str, Any]:
    """
    Remove keys whose values are None.
    """

    return {
        key: value
        for key, value in mapping.items()
        if value is not None
    }


def is_iterable(value: Any) -> bool:
    """
    Return True if value is iterable (excluding strings).
    """

    if isinstance(value, (str, bytes)):
        return False

    try:
        iter(value)
        return True
    except TypeError:
        return False