"""
Research-grade tests for the information-flow control (IFC) layer.

These tests validate the fail-closed enforcement semantics that
prevent confidential data from flowing to public sinks.
"""

from __future__ import annotations

from trustcalc.core.labels import (
    CONFIDENTIAL_LABEL,
    PUBLIC_LABEL,
    SECRET_LABEL,
    Confidentiality,
    Integrity,
    SecurityLabel,
)
from trustcalc.gateway.enforcement import PolicyEnforcer
from trustcalc.policy.decisions import Decision
from trustcalc.policy.engine import PolicyEngine
from trustcalc.runtime.execution_context import ExecutionContext


# ---------------------------------------------------------------------
# SecurityLabel.can_flow_to lattice semantics
# ---------------------------------------------------------------------


def test_public_flows_to_public():
    assert PUBLIC_LABEL.can_flow_to(PUBLIC_LABEL)


def test_public_flows_to_secret():
    # Bell-LaPadula: lower confidentiality may flow upward.
    assert PUBLIC_LABEL.can_flow_to(SECRET_LABEL)


def test_secret_does_not_flow_to_public():
    # Bell-LaPadula: no-write-down for confidentiality.
    assert not SECRET_LABEL.can_flow_to(PUBLIC_LABEL)


def test_secret_flows_to_secret():
    assert SECRET_LABEL.can_flow_to(SECRET_LABEL)


def test_high_integrity_source_flows_to_low_integrity_sink():
    # Biba: high-integrity data may flow to low-integrity sinks.
    high = SecurityLabel(
        integrity=Integrity.VERIFIED,
        confidentiality=Confidentiality.PUBLIC,
    )
    low = SecurityLabel(
        integrity=Integrity.UNTRUSTED,
        confidentiality=Confidentiality.PUBLIC,
    )
    assert high.can_flow_to(low)


def test_low_integrity_source_does_not_flow_to_high_integrity_sink():
    # Biba: no-write-up for integrity.
    high = SecurityLabel(
        integrity=Integrity.VERIFIED,
        confidentiality=Confidentiality.PUBLIC,
    )
    low = SecurityLabel(
        integrity=Integrity.UNTRUSTED,
        confidentiality=Confidentiality.PUBLIC,
    )
    assert not low.can_flow_to(high)


def test_compartment_gating():
    # A source in 'finance' cannot flow to a sink without it.
    source = CONFIDENTIAL_LABEL.with_compartment("finance")
    sink = CONFIDENTIAL_LABEL
    assert not source.can_flow_to(sink)

    sink_with = CONFIDENTIAL_LABEL.with_compartment("finance")
    assert source.can_flow_to(sink_with)


# ---------------------------------------------------------------------
# Fail-closed enforcement.check_information_flow
# ---------------------------------------------------------------------


def _enforcer() -> PolicyEnforcer:
    return PolicyEnforcer(policy_engine=PolicyEngine())


def test_check_information_flow_allows_legal_flow():
    decision = _enforcer().check_information_flow(
        PUBLIC_LABEL,
        SECRET_LABEL,
    )
    assert decision.allowed


def test_check_information_flow_denies_illegal_flow():
    decision = _enforcer().check_information_flow(
        SECRET_LABEL,
        PUBLIC_LABEL,
    )
    assert decision.denied


def test_check_information_flow_fails_closed_on_unknown_label():
    # A label-like object without can_flow_to must be denied, not
    # silently permitted (fail-closed).
    class BogusLabel:
        pass

    decision = _enforcer().check_information_flow(
        BogusLabel(),
        PUBLIC_LABEL,
    )
    assert decision.denied
    assert "denying by default" in decision.explanation


# ---------------------------------------------------------------------
# End-to-end authorization wiring in the PolicyEnforcer
# ---------------------------------------------------------------------


def test_authorize_enforces_ifc_when_labels_present():
    enforcer = _enforcer()

    class DummyTool:
        name = "sink"
        required_capability = None
        policy_rules = ()

    context = ExecutionContext(
        labels={
            "source": SECRET_LABEL,
            "destination": PUBLIC_LABEL,
        }
    )

    decision = enforcer.authorize(
        tool=DummyTool(),
        arguments={},
        context=context,
    )

    assert decision.denied


def test_authorize_allows_when_flow_legal():
    enforcer = _enforcer()

    class DummyTool:
        name = "sink"
        required_capability = None
        policy_rules = ()

    context = ExecutionContext(
        labels={
            "source": PUBLIC_LABEL,
            "destination": SECRET_LABEL,
        }
    )

    decision = enforcer.authorize(
        tool=DummyTool(),
        arguments={},
        context=context,
    )

    assert decision.allowed


def test_authorize_allows_when_no_ifc_labels():
    # No labels -> no IFC check triggered; capability/policy still gate.
    enforcer = _enforcer()

    class DummyTool:
        name = "sink"
        required_capability = None
        policy_rules = ()

    context = ExecutionContext()

    decision = enforcer.authorize(
        tool=DummyTool(),
        arguments={},
        context=context,
    )

    assert decision.allowed


def test_authorize_denies_missing_capability():
    enforcer = _enforcer()

    class CapabilityTool:
        name = "cap"
        required_capability = "file.access"
        policy_rules = ()

    context = ExecutionContext(
        capabilities=set(),
    )

    decision = enforcer.authorize(
        tool=CapabilityTool(),
        arguments={},
        context=context,
    )

    assert decision.denied
    assert "Missing capability" in decision.explanation
