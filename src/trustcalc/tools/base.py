"""
trustcalc.tools.base
====================

Base class for all executable tools.

Every concrete tool in TrustCalc derives from Tool.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Tool(ABC):
    """
    Base tool interface.
    """

    name: str
    description: str = ""
    required_capability: str | None = None
    policy_rules: tuple[Any, ...] = field(default_factory=tuple)
    argument_schema: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """
        Execute the tool.

        Must be implemented by subclasses.
        """
        raise NotImplementedError

    def validate(self) -> bool:
        """
        Validate the tool configuration.
        """
        return bool(self.name)

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:
        self.enabled = False

    @property
    def available(self) -> bool:
        return self.enabled

    def metadata(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "capability": self.required_capability,
            "enabled": self.enabled,
        }

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    __repr__ = __str__


__all__ = ["Tool"]