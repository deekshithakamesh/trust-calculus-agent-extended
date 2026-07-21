"""
trustcalc.attacks.data_exfiltration
==================================

Data Exfiltration Attack.

Simulates attempts to move sensitive information from a
protected source to an unauthorized destination.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .base import Attack, AttackResult


@dataclass(slots=True)
class DataExfiltrationAttack(Attack):
    """
    Simulated data exfiltration attack.

    Represents an attacker attempting to extract sensitive
    information from the Trust Calculus framework.
    """

    source: str = "protected_resource"

    destination: str = "external_endpoint"

    classification: str = "confidential"

    category: str = "data_exfiltration"

    severity: str = "critical"

    metadata: dict[str, Any] = field(default_factory=dict)

    # ---------------------------------------------------------
    # Attack Execution
    # ---------------------------------------------------------

    def execute(
        self,
        target: Any,
        **kwargs: Any,
    ) -> AttackResult:
        """
        Execute the simulated exfiltration attack.
        """

        allowed_destinations = kwargs.get(
            "allowed_destinations",
            []
        )

        blocked = (
            self.destination
            not in allowed_destinations
        )

        success = not blocked

        leakage = 1.0 if success else 0.0

        return AttackResult(
            attack_id=self.attack_id,
            attack_name=self.name,
            category=self.category,
            target=str(target),
            success=success,
            blocked=blocked,
            leakage=leakage,
            message=(
                "Data exfiltration blocked."
                if blocked
                else "Data exfiltration succeeded."
            ),
            metadata={
                "source": self.source,
                "destination": self.destination,
                "classification": self.classification,
                "allowed_destinations": allowed_destinations,
            },
        )

    # ---------------------------------------------------------

    def set_source(
        self,
        source: str,
    ) -> None:
        """
        Update the protected data source.
        """

        self.source = source

    # ---------------------------------------------------------

    def set_destination(
        self,
        destination: str,
    ) -> None:
        """
        Update the destination endpoint.
        """

        self.destination = destination

    # ---------------------------------------------------------

    def set_classification(
        self,
        classification: str,
    ) -> None:
        """
        Update the data classification.
        """

        self.classification = classification

    # ---------------------------------------------------------

    def is_sensitive(self) -> bool:
        """
        Determine whether the data should be protected.
        """

        return self.classification.lower() in {
            "secret",
            "confidential",
            "restricted",
            "internal",
        }

    # ---------------------------------------------------------

    def describe(self) -> dict[str, Any]:
        """
        Return a structured description of the attack.
        """

        return {
            "name": self.name,
            "category": self.category,
            "severity": self.severity,
            "source": self.source,
            "destination": self.destination,
            "classification": self.classification,
        }