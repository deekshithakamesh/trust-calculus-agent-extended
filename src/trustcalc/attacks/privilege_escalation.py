"""
trustcalc.attacks.privilege_escalation
=====================================

Privilege Escalation Attack.

Simulates attempts to obtain capabilities or permissions
beyond those explicitly granted by the Trust Calculus.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .base import Attack, AttackResult


@dataclass(slots=True)
class PrivilegeEscalationAttack(Attack):
    """
    Simulated privilege escalation attack.
    """

    requested_capability: str = "admin"

    current_capability: str = "user"

    category: str = "privilege_escalation"

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
        Execute a simulated privilege escalation attack.
        """

        allowed_capabilities = kwargs.get(
            "allowed_capabilities",
            [],
        )

        blocked = (
            self.requested_capability
            not in allowed_capabilities
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
                "Privilege escalation blocked."
                if blocked
                else "Privilege escalation succeeded."
            ),
            metadata={
                "current_capability": self.current_capability,
                "requested_capability": self.requested_capability,
                "allowed_capabilities": allowed_capabilities,
            },
        )

    # ---------------------------------------------------------

    def request(
        self,
        capability: str,
    ) -> None:
        """
        Request a different capability.
        """

        self.requested_capability = capability

    # ---------------------------------------------------------

    def downgrade(
        self,
        capability: str,
    ) -> None:
        """
        Change the current capability.
        """

        self.current_capability = capability

    # ---------------------------------------------------------

    def describe(self) -> dict[str, Any]:
        """
        Return attack metadata.
        """

        return {
            "name": self.name,
            "category": self.category,
            "severity": self.severity,
            "current_capability": self.current_capability,
            "requested_capability": self.requested_capability,
        }

    # ---------------------------------------------------------

    def can_escalate(
        self,
        allowed_capabilities: list[str],
    ) -> bool:
        """
        Check whether escalation would succeed.
        """

        return (
            self.requested_capability
            in allowed_capabilities
        )