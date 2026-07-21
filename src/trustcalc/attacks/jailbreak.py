"""
trustcalc.attacks.jailbreak
===========================

Jailbreak Attack.

Simulates attempts to bypass system restrictions,
safety policies, or execution constraints.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .base import Attack, AttackResult


@dataclass(slots=True)
class JailbreakAttack(Attack):
    """
    Simulated jailbreak attack.
    """

    strategy: str = "role_override"

    objective: str = (
        "Bypass safety constraints"
    )

    category: str = "jailbreak"

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
        Execute a simulated jailbreak attempt.
        """

        policy_enforced = kwargs.get(
            "policy_enforced",
            True,
        )

        blocked = policy_enforced

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
                "Jailbreak prevented."
                if blocked
                else "Jailbreak successful."
            ),
            metadata={
                "strategy": self.strategy,
                "objective": self.objective,
            },
        )

    # ---------------------------------------------------------

    def set_strategy(
        self,
        strategy: str,
    ) -> None:
        """
        Update the jailbreak strategy.
        """

        self.strategy = strategy

    # ---------------------------------------------------------

    def describe(self) -> dict[str, Any]:
        """
        Return attack metadata.
        """

        return {
            "name": self.name,
            "category": self.category,
            "severity": self.severity,
            "strategy": self.strategy,
            "objective": self.objective,
        }