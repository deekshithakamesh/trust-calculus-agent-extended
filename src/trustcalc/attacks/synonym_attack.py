"""
trustcalc.attacks.synonym_attack
================================

Synonym covert-channel attack.

Wraps the SynonymChannel implementation as a reusable
evaluation attack.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from trustcalc.sidechannels.synonym_channel import (
    SynonymChannel,
)

from .base import Attack, AttackResult


@dataclass(slots=True)
class SynonymAttack(Attack):
    """
    Synonym-based covert channel attack.
    """

    secret: str = ""

    category: str = "synonym"

    severity: str = "medium"

    metadata: dict[str, Any] = field(default_factory=dict)

    channel: SynonymChannel = field(
        default_factory=SynonymChannel
    )

    # ---------------------------------------------------------
    # Attack Execution
    # ---------------------------------------------------------

    def execute(
        self,
        target: Any,
        **kwargs: Any,
    ) -> AttackResult:
        """
        Execute the synonym covert channel.
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
            message="Synonym channel executed.",
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
        Decode the hidden payload.
        """

        return self.channel.decode(encoded)

    # ---------------------------------------------------------

    def detect(
        self,
        text: str,
    ) -> bool:
        """
        Detect synonym-based encoding.
        """

        return self.channel.detect(text)

    # ---------------------------------------------------------

    def normalize(
        self,
        text: str,
    ) -> str:
        """
        Normalize synonym substitutions.
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