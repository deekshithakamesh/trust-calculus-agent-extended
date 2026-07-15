"""
trustcalc.attacks.base
======================

Base attack interface.

Every attack in the Trust Calculus framework derives
from this class.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Attack(ABC):
    """
    Base attack abstraction.
    """

    name: str

    description: str = ""

    category: str = "generic"

    severity: str = "medium"

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    # ---------------------------------------------------------

    @abstractmethod
    def execute(
        self,
        target: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute the attack.
        """
        raise NotImplementedError

    # ---------------------------------------------------------

    def validate(self) -> bool:
        return bool(self.name)

    # ---------------------------------------------------------

    def info(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "severity": self.severity,
            "description": self.description,
            "metadata": self.metadata,
        }

    # ---------------------------------------------------------

    def __str__(self) -> str:
        return f"{self.category}:{self.name}"

    __repr__ = __str__