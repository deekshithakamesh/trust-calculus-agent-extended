"""
trustcalc.attacks.whitespace_attack
==================================

Whitespace covert-channel attack.

Wraps the WhitespaceChannel implementation as a reusable
evaluation attack.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from trustcalc.sidechannels.whitespace_channel import (
    WhitespaceChannel,
)

from .base import Attack, AttackResult


@dataclass(slots=True)
class WhitespaceAttack(Attack):
    """
    Whitespace covert-channel attack.
    """

    secret: str = ""

    category: str = "whitespace"

    severity: str = "medium"

    metadata: dict[str, Any] = field(default_factory=dict)

    channel: WhitespaceChannel = field(
        default_factory=WhitespaceChannel
    )

    # ---------------------------------------------------------

    def execute(
        self,
        target: Any,
        **kwargs: Any,
    ) -> AttackResult:
        """
        Execute the whitespace covert channel.
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
            message="Whitespace channel executed.",
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
        Decode hidden information.
        """

        return self.channel.decode(encoded)

    # ---------------------------------------------------------

    def detect(
        self,
        text: str,
    ) -> bool:
        """
        Detect whitespace encoding.
        """

        return self.channel.detect(text)

    # ---------------------------------------------------------

    def normalize(
        self,
        text: str,
    ) -> str:
        """
        Remove whitespace channel artifacts.
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
        """
        Return attack metadata.
        """

        return {
            "name": self.name,
            "category": self.category,
            "severity": self.severity,
            "secret_length": len(self.secret),
        }