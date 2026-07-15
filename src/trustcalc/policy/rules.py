"""
trustcalc.policy.rules
======================

Declarative policy rules.

Rules are immutable policy objects.

Evaluation is implemented by the PolicyEngine.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, Sequence

from trustcalc.core.labels import (
    Confidentiality,
    Integrity,
)


# ================================================================
# Rule Type
# ================================================================


class RuleType(str, Enum):
    """
    Supported rule categories.
    """

    INTEGRITY = "integrity"

    CONFIDENTIALITY = "confidentiality"

    CAPABILITY = "capability"

    COMPARTMENT = "compartment"

    COMPOSITE = "composite"


# ================================================================
# Logical Operator
# ================================================================


class LogicalOperator(str, Enum):
    """
    Composite rule operators.
    """

    AND = "and"

    OR = "or"

    NOT = "not"


# ================================================================
# Rule Protocol
# ================================================================


class Rule(Protocol):
    """
    Base protocol implemented by every rule.
    """

    name: str

    description: str

    rule_type: RuleType


# ================================================================
# Rule Context
# ================================================================


@dataclass(frozen=True, slots=True)
class RuleContext:
    """
    Context supplied to the Policy Engine.

    The engine evaluates rules against this context.
    """

    label: Any

    capability_set: Any

    tool_name: str

    action: str

    runtime_context: Mapping[str, Any] = field(default_factory=dict)


# ================================================================
# Rule Result
# ================================================================


@dataclass(frozen=True, slots=True)
class RuleResult:
    """
    Result of evaluating one rule.
    """

    passed: bool

    rule_name: str

    message: str = ""

    metadata: Mapping[str, Any] = field(default_factory=dict)


# ================================================================
# Integrity Rule
# ================================================================


@dataclass(frozen=True, slots=True)
class IntegrityRule:
    """
    Require minimum integrity.
    """

    minimum: Integrity

    name: str = "minimum_integrity"

    description: str = ""

    rule_type: RuleType = RuleType.INTEGRITY


# ================================================================
# Confidentiality Rule
# ================================================================


@dataclass(frozen=True, slots=True)
class ConfidentialityRule:
    """
    Maximum confidentiality accepted.
    """

    maximum: Confidentiality

    name: str = "maximum_confidentiality"

    description: str = ""

    rule_type: RuleType = RuleType.CONFIDENTIALITY


# ================================================================
# Capability Rule
# ================================================================


@dataclass(frozen=True, slots=True)
class CapabilityRule:
    """
    Required capability.
    """

    resource: str

    action: str

    name: str = "required_capability"

    description: str = ""

    rule_type: RuleType = RuleType.CAPABILITY


# ================================================================
# Compartment Rule
# ================================================================


@dataclass(frozen=True, slots=True)
class CompartmentRule:
    """
    Required security compartment.
    """

    compartment: str

    name: str = "required_compartment"

    description: str = ""

    rule_type: RuleType = RuleType.COMPARTMENT

    # ================================================================


# Composite Rule
# ================================================================


@dataclass(frozen=True, slots=True)
class CompositeRule:
    """
    Base composite rule.

    Composite rules combine multiple atomic rules using a logical
    operator. Evaluation is performed by the PolicyEngine.
    """

    operator: LogicalOperator

    rules: tuple[Rule, ...]

    name: str = "composite"

    description: str = ""

    rule_type: RuleType = RuleType.COMPOSITE

    def __post_init__(self):

        if len(self.rules) == 0:
            raise ValueError("CompositeRule requires at least one child rule.")


# ================================================================
# AND Rule
# ================================================================


@dataclass(frozen=True, slots=True)
class AndRule:
    """
    Logical AND.

    Every child rule must pass.
    """

    rules: tuple[Rule, ...]

    name: str = "and"

    description: str = ""

    rule_type: RuleType = RuleType.COMPOSITE

    operator: LogicalOperator = LogicalOperator.AND

    def __post_init__(self):

        if len(self.rules) < 2:
            raise ValueError("AndRule requires at least two rules.")


# ================================================================
# OR Rule
# ================================================================


@dataclass(frozen=True, slots=True)
class OrRule:
    """
    Logical OR.

    At least one child rule must pass.
    """

    rules: tuple[Rule, ...]

    name: str = "or"

    description: str = ""

    rule_type: RuleType = RuleType.COMPOSITE

    operator: LogicalOperator = LogicalOperator.OR

    def __post_init__(self):

        if len(self.rules) < 2:
            raise ValueError("OrRule requires at least two rules.")


# ================================================================
# NOT Rule
# ================================================================


@dataclass(frozen=True, slots=True)
class NotRule:
    """
    Logical NOT.

    Negates the result of a child rule.
    """

    rule: Rule

    name: str = "not"

    description: str = ""

    rule_type: RuleType = RuleType.COMPOSITE

    operator: LogicalOperator = LogicalOperator.NOT


# ================================================================
# Rule Validation Helpers
# ================================================================


def validate_rule(rule: Rule) -> None:
    """
    Validate a rule definition.

    Raises
    ------
    ValueError
        If the rule definition is invalid.
    """

    if not getattr(rule, "name", None):
        raise ValueError("Rule name cannot be empty.")

    if not isinstance(rule.rule_type, RuleType):
        raise ValueError("Invalid rule type.")


def validate_rules(
    rules: Sequence[Rule],
) -> None:
    """
    Validate a collection of rules.
    """

    for rule in rules:
        validate_rule(rule)


# ================================================================
# Serialization
# ================================================================


def rule_to_dict(
    rule: Rule,
) -> dict[str, Any]:
    """
    Convert a rule into a serializable dictionary.

    Used by the YAML policy loader.
    """

    data = {
        "type": rule.rule_type.value,
        "name": rule.name,
        "description": rule.description,
    }

    if isinstance(rule, IntegrityRule):

        data["minimum"] = rule.minimum.name

    elif isinstance(rule, ConfidentialityRule):

        data["maximum"] = rule.maximum.name

    elif isinstance(rule, CapabilityRule):

        data["resource"] = rule.resource
        data["action"] = rule.action

    elif isinstance(rule, CompartmentRule):

        data["compartment"] = rule.compartment

    elif isinstance(rule, (AndRule, OrRule)):

        data["operator"] = rule.operator.value
        data["rules"] = [rule_to_dict(r) for r in rule.rules]

    elif isinstance(rule, NotRule):

        data["operator"] = rule.operator.value
        data["rule"] = rule_to_dict(rule.rule)

    return data


# ================================================================
# Pretty Printing
# ================================================================


def describe_rule(
    rule: Rule,
) -> str:
    """
    Human-readable description.
    """

    if isinstance(rule, IntegrityRule):

        return "Integrity >= " f"{rule.minimum.name}"

    if isinstance(rule, ConfidentialityRule):

        return "Confidentiality <= " f"{rule.maximum.name}"

    if isinstance(rule, CapabilityRule):

        return f"Capability({rule.resource}:" f"{rule.action})"

    if isinstance(rule, CompartmentRule):

        return f"Compartment({rule.compartment})"

    if isinstance(rule, AndRule):

        return " AND ".join(describe_rule(r) for r in rule.rules)

    if isinstance(rule, OrRule):

        return " OR ".join(describe_rule(r) for r in rule.rules)

    if isinstance(rule, NotRule):

        return "NOT (" + describe_rule(rule.rule) + ")"

    return str(rule)


# ================================================================
# Deserialization
# ================================================================


def rule_from_dict(
    data: Mapping[str, Any],
) -> Rule:
    """
    Reconstruct a rule from a dictionary.

    Used by the YAML policy loader.
    """

    rule_type = RuleType(data["type"])

    if rule_type == RuleType.INTEGRITY:

        return IntegrityRule(
            minimum=Integrity[data["minimum"]],
            name=data.get("name", "minimum_integrity"),
            description=data.get("description", ""),
        )

    if rule_type == RuleType.CONFIDENTIALITY:

        return ConfidentialityRule(
            maximum=Confidentiality[data["maximum"]],
            name=data.get(
                "name",
                "maximum_confidentiality",
            ),
            description=data.get("description", ""),
        )

    if rule_type == RuleType.CAPABILITY:

        return CapabilityRule(
            resource=data["resource"],
            action=data["action"],
            name=data.get(
                "name",
                "required_capability",
            ),
            description=data.get("description", ""),
        )

    if rule_type == RuleType.COMPARTMENT:

        return CompartmentRule(
            compartment=data["compartment"],
            name=data.get(
                "name",
                "required_compartment",
            ),
            description=data.get("description", ""),
        )

    if data.get("operator") == "and":

        return AndRule(
            rules=tuple(rule_from_dict(r) for r in data["rules"]),
            name=data.get("name", "and"),
            description=data.get("description", ""),
        )

    if data.get("operator") == "or":

        return OrRule(
            rules=tuple(rule_from_dict(r) for r in data["rules"]),
            name=data.get("name", "or"),
            description=data.get("description", ""),
        )

    if data.get("operator") == "not":

        return NotRule(
            rule=rule_from_dict(data["rule"]),
            name=data.get("name", "not"),
            description=data.get("description", ""),
        )

    raise ValueError(f"Unknown rule: {data}")


# ================================================================
# Module Exports
# ================================================================

__all__ = [
    "Rule",
    "RuleType",
    "LogicalOperator",
    "RuleContext",
    "RuleResult",
    "IntegrityRule",
    "ConfidentialityRule",
    "CapabilityRule",
    "CompartmentRule",
    "CompositeRule",
    "AndRule",
    "OrRule",
    "NotRule",
    "validate_rule",
    "validate_rules",
    "rule_to_dict",
    "rule_from_dict",
    "describe_rule",
]
