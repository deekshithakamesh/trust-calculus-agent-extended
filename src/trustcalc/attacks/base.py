"""
trustcalc.attacks.base
======================

Base abstractions for security attacks used by the
Trust Calculus evaluation framework.

Every attack derives from this module.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from time import perf_counter
from typing import Any
from uuid import uuid4


# ---------------------------------------------------------------------
# Attack Result
# ---------------------------------------------------------------------


@dataclass(slots=True)
class AttackResult:
    """
    Standardized attack execution result.
    """

    attack_id: str

    attack_name: str

    category: str

    target: str

    success: bool

    blocked: bool

    message: str = ""

    leakage: float = 0.0

    execution_time: float = 0.0

    metadata: dict[str, Any] = field(default_factory=dict)

    timestamp: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------
# Base Attack
# ---------------------------------------------------------------------


@dataclass(slots=True)
class Attack(ABC):
    """
    Abstract base class for all attacks.
    """

    name: str

    description: str = ""

    category: str = "generic"

    severity: str = "medium"

    enabled: bool = True

    metadata: dict[str, Any] = field(default_factory=dict)

    attack_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    # ---------------------------------------------------------

    @abstractmethod
    def execute(
        self,
        target: Any,
        **kwargs: Any,
    ) -> AttackResult:
        """
        Execute the attack.
        """

    # ---------------------------------------------------------

    def validate(self) -> bool:
        """
        Validate attack configuration.
        """

        return (
            self.enabled
            and bool(self.name)
            and bool(self.category)
        )

    # ---------------------------------------------------------

    def run(
        self,
        target: Any,
        **kwargs: Any,
    ) -> AttackResult:
        """
        Execute attack while measuring runtime.
        """

        if not self.validate():
            raise ValueError(
                f"Attack '{self.name}' failed validation."
            )

        start = perf_counter()

        result = self.execute(
            target,
            **kwargs,
        )

        result.execution_time = (
            perf_counter() - start
        )

        return result

    # ---------------------------------------------------------

    def info(self) -> dict[str, Any]:
        """
        Return attack metadata.
        """

        return {
            "id": self.attack_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "severity": self.severity,
            "enabled": self.enabled,
            "metadata": self.metadata,
        }

    # ---------------------------------------------------------

    def enable(self) -> None:
        """
        Enable the attack.
        """

        self.enabled = True

    # ---------------------------------------------------------

    def disable(self) -> None:
        """
        Disable the attack.
        """

        self.enabled = False

    # ---------------------------------------------------------

    def reset(self) -> None:
        """
        Reset runtime metadata.
        """

        self.metadata.clear()

    # ---------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize attack configuration.
        """

        return self.info()

    # ---------------------------------------------------------

    def __str__(self) -> str:
        return (
            f"{self.category}"
            f"::{self.name}"
        )

    __repr__ = __str__