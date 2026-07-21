"""
trustcalc.policy.policy
=======================

Immutable policy definition.

A Policy groups one or more declarative rules that are evaluated
by the PolicyEngine.

Policies themselves contain no evaluation logic.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Any

from trustcalc.policy.rules import Rule


@dataclass(frozen=True, slots=True)
class Policy:
    """
    Immutable policy definition.

    Parameters
    ----------
    name
        Unique policy name.

    description
        Human-readable description.

    rules
        Rules evaluated by the PolicyEngine.

    metadata
        Optional implementation-specific metadata.
    """

    name: str

    rules: tuple[Rule, ...]

    description: str = ""

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "rules", tuple(self.rules))
        object.__setattr__(self, "metadata", dict(self.metadata))

    def __len__(self) -> int:
        return len(self.rules)

    def __iter__(self):
        return iter(self.rules)

    def add_rule(self, rule: Rule) -> "Policy":
        """
        Return a new Policy with an additional rule.
        """
        return Policy(
            name=self.name,
            description=self.description,
            rules=self.rules + (rule,),
            metadata=self.metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "rules": [rule.name for rule in self.rules],
            "metadata": dict(self.metadata),
        }