from trustcalc.core.labels import (
    Confidentiality,
    Integrity,
)

from trustcalc.policy.rules import *


def test_integrity_rule():

    rule = IntegrityRule(minimum=Integrity.HIGH)

    assert rule.minimum == Integrity.HIGH


def test_capability_rule():

    rule = CapabilityRule(
        resource="email",
        action="send",
    )

    assert rule.resource == "email"

    assert rule.action == "send"


def test_and_rule():

    rule = AndRule(
        rules=(
            IntegrityRule(minimum=Integrity.HIGH),
            CapabilityRule(
                "email",
                "send",
            ),
        )
    )

    assert len(rule.rules) == 2


def test_serialization():

    rule = IntegrityRule(minimum=Integrity.HIGH)

    restored = rule_from_dict(rule_to_dict(rule))

    assert restored.minimum == Integrity.HIGH


def test_description():

    rule = ConfidentialityRule(maximum=Confidentiality.SECRET)

    assert "SECRET" in describe_rule(rule)


def test_validation():

    validate_rule(IntegrityRule(minimum=Integrity.HIGH))
