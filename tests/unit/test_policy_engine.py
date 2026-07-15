from trustcalc.core.labels import PUBLIC_LABEL
from trustcalc.policy.capabilities import (
    Capability,
    CapabilitySet,
)
from trustcalc.policy.engine import PolicyEngine
from trustcalc.policy.rules import (
    CapabilityRule,
    IntegrityRule,
    RuleContext,
)
from trustcalc.core.labels import Integrity


def test_integrity():

    engine = PolicyEngine()

    context = RuleContext(
        label=PUBLIC_LABEL,
        capability_set=CapabilitySet(),
        tool_name="email",
        action="send",
    )

    decision = engine.evaluate(
        IntegrityRule(minimum=Integrity.HIGH),
        context,
    )

    assert decision.allowed


def test_capability():

    engine = PolicyEngine()

    capabilities = CapabilitySet(
        {
            Capability(
                resource="email",
                action="send",
            )
        }
    )

    context = RuleContext(
        label=PUBLIC_LABEL,
        capability_set=capabilities,
        tool_name="email",
        action="send",
    )

    decision = engine.evaluate(
        CapabilityRule(
            "email",
            "send",
        ),
        context,
    )

    assert decision.allowed


def test_statistics():

    engine = PolicyEngine()

    stats = engine.statistics(
        engine.evaluate(
            IntegrityRule(minimum=Integrity.HIGH),
            RuleContext(
                label=PUBLIC_LABEL,
                capability_set=CapabilitySet(),
                tool_name="email",
                action="send",
            ),
        )
    )

    assert "matched_rules" in stats
