"""
trustcalc.attacks.timing_attack
===============================

Timing covert-channel attack.

Wraps the TimingChannel implementation as a reusable
evaluation attack.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from trustcalc.sidechannels.timing_channel import TimingChannel

from .base import Attack, AttackResult


@dataclass(slots=True)
class TimingAttack(Attack):
    """
    Timing-based covert channel attack.
    """

    secret: str = ""

    category: str = "timing"

    severity: str = "high"

    metadata: dict[str, Any] = field(default_factory=dict)

    channel: TimingChannel = field(
        default_factory=TimingChannel
    )

    # ---------------------------------------------------------

    def execute(
        self,
        target: Any,
        **kwargs: Any,
    ) -> AttackResult:
        """
        Execute the timing covert channel.
        """

        carrier = str(target)

        start = time.perf_counter()

        encoded = self.channel.encode(
            carrier,
            self.secret,
        )

        elapsed = time.perf_counter() - start

        capacity = self.channel.capacity(encoded)

        bandwidth = (
            capacity / elapsed
            if elapsed > 0
            else 0.0
        )

        return AttackResult(
            attack_id=self.attack_id,
            attack_name=self.name,
            category=self.category,
            target=carrier,
            success=True,
            blocked=False,
            leakage=capacity,
            execution_time=elapsed,
            message="Timing channel executed.",
            metadata={
                "carrier": carrier,
                "encoded": encoded,
                "capacity": capacity,
                "bandwidth": bandwidth,
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
        Detect timing-channel artifacts.
        """

        return self.channel.detect(text)

    # ---------------------------------------------------------

    def normalize(
        self,
        text: str,
    ) -> str:
        """
        Remove timing-channel artifacts.
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