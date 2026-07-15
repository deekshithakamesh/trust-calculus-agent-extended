"""
trustcalc.policy.capabilities
=============================

Capability-based authorization model.

Capabilities grant permission to perform specific operations on
resources.

Unlike SecurityLabel, capabilities authorize actions rather than
describe information.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping


class CapabilityScope(str, Enum):
    LOCAL = "local"
    SESSION = "session"
    REQUEST = "request"
    GLOBAL = "global"


class ConstraintOperator(str, Enum):
    EQ = "=="
    NE = "!="
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="
    IN = "in"
    NOT_IN = "not_in"
    EXISTS = "exists"
    REGEX = "regex"


@dataclass(frozen=True)
class CapabilityConstraint:
    key: str
    operator: ConstraintOperator
    value: Any

    def evaluate(self, context: Mapping[str, Any]) -> bool:
        if self.operator == ConstraintOperator.EXISTS:
            return self.key in context

        if self.key not in context:
            return False

        current = context[self.key]

        if self.operator == ConstraintOperator.EQ:
            return current == self.value

        if self.operator == ConstraintOperator.NE:
            return current != self.value

        if self.operator == ConstraintOperator.LT:
            return current < self.value

        if self.operator == ConstraintOperator.LE:
            return current <= self.value

        if self.operator == ConstraintOperator.GT:
            return current > self.value

        if self.operator == ConstraintOperator.GE:
            return current >= self.value

        if self.operator == ConstraintOperator.IN:
            return current in self.value

        if self.operator == ConstraintOperator.NOT_IN:
            return current not in self.value

        if self.operator == ConstraintOperator.REGEX:
            import re

            return bool(re.fullmatch(self.value, str(current)))

        return False


@dataclass(frozen=True)
class Capability:
    resource: str
    action: str
    scope: CapabilityScope = CapabilityScope.REQUEST
    delegated_by: str | None = None
    expires_at: datetime | None = None
    constraints: frozenset[CapabilityConstraint] = field(default_factory=frozenset)
    metadata: tuple[tuple[str, Any], ...] = ()

    @property
    def identifier(self) -> str:
        return f"{self.resource}:{self.action}"

    @property
    def expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    def matches(
        self,
        resource: str,
        action: str,
        context: Mapping[str, Any] | None = None,
    ) -> bool:
        if self.expired:
            return False

        if self.resource != resource:
            return False

        if self.action != action:
            return False

        if context is None:
            context = {}

        return all(c.evaluate(context) for c in self.constraints)

    def to_dict(self) -> dict[str, Any]:
        return {
            "resource": self.resource,
            "action": self.action,
            "scope": self.scope.value,
            "delegated_by": self.delegated_by,
            "expires_at": self.expires_at,
            "constraints": [
                {
                    "key": c.key,
                    "operator": c.operator.value,
                    "value": c.value,
                }
                for c in self.constraints
            ],
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class CapabilitySet:
    capabilities: frozenset[Capability] = field(default_factory=frozenset)

    def add(self, capability: Capability):
        return CapabilitySet(self.capabilities | {capability})

    def remove(self, capability: Capability):
        return CapabilitySet(self.capabilities - {capability})

    def allows(self, resource: str, action: str, context=None):
        return any(
            capability.matches(
                resource,
                action,
                context,
            )
            for capability in self.capabilities
        )

    def get(self, resource, action):
        for capability in self.capabilities:
            if capability.matches(
                resource,
                action,
            ):
                return capability

        return None

    def __iter__(self):
        return iter(self.capabilities)

    def __len__(self):
        return len(self.capabilities)