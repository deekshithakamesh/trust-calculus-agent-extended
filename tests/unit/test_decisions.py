from trustcalc.policy.decisions import (
    Decision,
    DecisionEffect,
)


def test_allow():

    decision = Decision.allow()

    assert decision.allowed


def test_deny():

    decision = Decision.deny()

    assert decision.denied


def test_violation():

    decision = Decision.allow().add_violation("IntegrityRule")

    assert decision.denied

    assert len(decision.violated_rules) == 1


def test_missing_capability():

    decision = Decision.allow().add_missing_capability("email:send")

    assert decision.denied


def test_bool():

    assert Decision.allow()

    assert not Decision.deny()


def test_serialization():

    decision = Decision.allow(explanation="OK")

    data = decision.to_dict()

    assert data["allowed"]
