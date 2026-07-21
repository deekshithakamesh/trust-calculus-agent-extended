"""
trustcalc.attacks.formatting_attack
==================================

Formatting covert-channel attack.

Wraps the FormattingChannel implementation as a reusable
evaluation attack.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from trustcalc.sidechannels.formatting_channel import (
    FormattingChannel,
)

from .base import Attack, AttackResult


@dataclass(slots=True)
class FormattingAttack(Attack):
    """
    Formatting-based covert channel attack.
    """

    secret: str = ""

    category: str = "formatting"

    severity: str = "medium"

    metadata: dict[str, Any] = field(default_factory=dict)

    channel: FormattingChannel = field(
        default_factory=FormattingChannel
    )

    # ---------------------------------------------------------

    def execute(
        self,
        target: Any,
        **kwargs: Any,
    ) -> AttackResult:
        """
        Execute the formatting covert channel.
        """

        carrier = str(target)

        encoded = self.channel.encode(
            carrier,
            self.secret,
        )

        capacity = self.channel.capacity(
            encoded
        )

        return AttackResult(
            attack_id=self.attack_id,
            attack_name=self.name,
            category=self.category,
            target=carrier,
            success=True,
            blocked=False,
            leakage=capacity,
            message="Formatting channel executed.",
            metadata={
                "carrier": carrier,
                "encoded": encoded,
                "capacity": capacity,
            },
        )

    # ---------------------------------------------------------

    def decode(
        self,
        encoded: str,
    ) -> str:
        """
        Recover hidden information.
        """

        return self.channel.decode(encoded)

    # ---------------------------------------------------------

    def detect(
        self,
        text: str,
    ) -> bool:
        """
        Detect formatting channel usage.
        """

        return self.channel.detect(text)

    # ---------------------------------------------------------

    def normalize(
        self,
        text: str,
    ) -> str:
        """
        Remove formatting artifacts.
        """

        return self.channel.normalize(text)

    # ---------------------------------------------------------

    def set_secret(
        self,
        secret: str,
    ) -> None:
        """
        Update the hidden payload.
        """

        self.secret = secret

    # ---------------------------------------------------------

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "severity": self.severity,
            "secret_length": len(self.secret),
        }