"""
trustcalc.policy.decisions
==========================

Policy decision model.

The Policy Engine never returns booleans.

Instead it returns immutable Decision objects that contain:

    • allow / deny
    • matched rules
    • violated rules
    • missing capabilities
    • explanation
    • metadata

These decisions are consumed by the Tool Gateway,
Audit subsystem, and Runtime.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Sequence


# ============================================================
# Decision Effect
# ============================================================


class DecisionEffect(str, Enum):
    """
    Policy decision outcome.
    """

    ALLOW = "allow"

    DENY = "deny"

    INDETERMINATE = "indeterminate"


# ============================================================
# Decision
# ============================================================


@dataclass(frozen=True, slots=True)
class Decision:
    """
    Result returned by the Policy Engine.
    """

    effect: DecisionEffect

    matched_rules: tuple[str, ...] = ()

    violated_rules: tuple[str, ...] = ()

    missing_capabilities: tuple[str, ...] = ()

    explanation: str = ""

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):

        object.__setattr__(
            self,
            "matched_rules",
            tuple(self.matched_rules),
        )

        object.__setattr__(
            self,
            "violated_rules",
            tuple(self.violated_rules),
        )

        object.__setattr__(
            self,
            "missing_capabilities",
            tuple(self.missing_capabilities),
        )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

    # --------------------------------------------------------

    @property
    def allowed(self) -> bool:
        return self.effect == DecisionEffect.ALLOW

    @property
    def denied(self) -> bool:
        return self.effect == DecisionEffect.DENY

    @property
    def indeterminate(self) -> bool:
        return self.effect == DecisionEffect.INDETERMINATE

    # --------------------------------------------------------

    def with_metadata(
        self,
        **kwargs: Any,
    ) -> "Decision":

        metadata = dict(self.metadata)
        metadata.update(kwargs)

        return replace(
            self,
            metadata=metadata,
        )

    # --------------------------------------------------------

    def add_match(
        self,
        rule: str,
    ) -> "Decision":

        return replace(
            self,
            matched_rules=self.matched_rules + (rule,),
        )

    # --------------------------------------------------------

    def add_violation(
        self,
        rule: str,
    ) -> "Decision":

        return replace(
            self,
            violated_rules=self.violated_rules + (rule,),
            effect=DecisionEffect.DENY,
        )

    # --------------------------------------------------------

    def add_missing_capability(
        self,
        capability: str,
    ) -> "Decision":

        return replace(
            self,
            missing_capabilities=(self.missing_capabilities + (capability,)),
            effect=DecisionEffect.DENY,
        )

    # --------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:

        return {
            "effect": self.effect.value,
            "allowed": self.allowed,
            "matched_rules": list(self.matched_rules),
            "violated_rules": list(self.violated_rules),
            "missing_capabilities": list(self.missing_capabilities),
            "explanation": self.explanation,
            "metadata": dict(self.metadata),
        }

    # --------------------------------------------------------

    @classmethod
    def allow(
        cls,
        explanation: str = "",
        **metadata: Any,
    ) -> "Decision":

        return cls(
            effect=DecisionEffect.ALLOW,
            explanation=explanation,
            metadata=metadata,
        )

    @classmethod
    def deny(
        cls,
        explanation: str = "",
        **metadata: Any,
    ) -> "Decision":

        return cls(
            effect=DecisionEffect.DENY,
            explanation=explanation,
            metadata=metadata,
        )

    @classmethod
    def indeterminate(
        cls,
        explanation: str = "",
        **metadata: Any,
    ) -> "Decision":

        return cls(
            effect=DecisionEffect.INDETERMINATE,
            explanation=explanation,
            metadata=metadata,
        )

    # --------------------------------------------------------

    def __bool__(self):

        return self.allowed

    def __str__(self):

        return (
            "Decision("
            f"{self.effect.value}, "
            f"matches={len(self.matched_rules)}, "
            f"violations={len(self.violated_rules)})"
        )

    __repr__ = __str__


# ============================================================
# Decision Report
# ============================================================


@dataclass(frozen=True, slots=True)
class DecisionReport:
    """
    Aggregated report for multiple policy evaluations.

    Useful when the gateway evaluates several tools
    or several candidate plans.
    """

    decisions: tuple[Decision, ...]

    @property
    def allowed(self) -> bool:

        return all(decision.allowed for decision in self.decisions)

    @property
    def denied(self) -> bool:

        return not self.allowed

    @property
    def violations(self) -> tuple[str, ...]:

        violations: list[str] = []

        for decision in self.decisions:
            violations.extend(decision.violated_rules)

        return tuple(violations)

    def to_dict(self):

        return {
            "allowed": self.allowed,
            "violations": list(self.violations),
            "decisions": [decision.to_dict() for decision in self.decisions],
        }


__all__ = [
    "Decision",
    "DecisionEffect",
    "DecisionReport",
]
