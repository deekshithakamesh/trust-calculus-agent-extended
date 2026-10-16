from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

import pytest

from trustcalc.core.labels import Confidentiality, Integrity, SecurityLabel
from trustcalc.gateway import BudgetedGateway
from trustcalc.gateway.enforcement import PolicyEnforcer
from trustcalc.gateway.gateway import ToolGateway
from trustcalc.gateway.validator import GatewayValidator
from trustcalc.policy.engine import PolicyEngine
from trustcalc.runtime.execution_context import ExecutionContext
from trustcalc.tools.base import Tool
from trustcalc.tools.registry import ToolRegistry


@dataclass(slots=True)
class EchoTool(Tool):
    name: str = "echo"

    def execute(self, **kwargs):
        return kwargs


def _universe(confidentialities=tuple(Confidentiality)):
    compartments = ("FIN", "HR")
    subsets = [
        frozenset(subset)
        for count in range(len(compartments) + 1)
        for subset in combinations(compartments, count)
    ]
    return tuple(
        SecurityLabel(
            integrity=Integrity.HIGH,
            confidentiality=confidentiality,
            compartments=subset,
        )
        for confidentiality in confidentialities
        for subset in subsets
    )


def _budgeted_gateway(
    universe,
    *,
    budget=3.0,
    reserved_fraction=0.0,
):
    registry = ToolRegistry()
    registry.register("echo", EchoTool())
    gateway = ToolGateway(
        registry=registry,
        validator=GatewayValidator(),
        enforcer=PolicyEnforcer(PolicyEngine()),
    )
    return BudgetedGateway(
        gateway=gateway,
        label_universe=universe,
        budget=budget,
        reserved_fraction=reserved_fraction,
    )


def _context(source, destination_compartments):
    return ExecutionContext(
        labels={
            "source": source,
            "destination": SecurityLabel(
                integrity=Integrity.HIGH,
                confidentiality=Confidentiality.INTERNAL,
                compartments=frozenset(destination_compartments),
            ),
        }
    )


def test_probe_share_exhaustion_does_not_consume_legitimate_reserve():
    universe = _universe((Confidentiality.INTERNAL,))
    actual = next(
        label for label in universe
        if label.compartments == frozenset({"HR"})
    )
    gateway = _budgeted_gateway(
        universe,
        budget=2.0,
        reserved_fraction=0.5,
    )

    first_probe = gateway.authorize(
        "echo",
        {},
        _context(actual, {"FIN"}),
    )
    assert first_probe.denied
    assert gateway.spent_bits() == pytest.approx(1.0)

    blocked_probe = gateway.authorize(
        "echo",
        {},
        _context(actual, {"HR"}),
    )
    assert blocked_probe.denied
    assert blocked_probe.explanation == "Tool call denied by policy."
    assert gateway.spent_bits() == pytest.approx(1.0)

    legitimate = gateway.authorize(
        "echo",
        {},
        _context(actual, {"HR"}),
        legitimate=True,
    )
    assert legitimate.allowed
    assert gateway.spent_bits() == pytest.approx(2.0)
    assert gateway.spent_bits() <= 2.0


def test_leakage_never_exceeds_budget_for_any_universe_label():
    universe = _universe()
    destinations = (
        SecurityLabel(
            integrity=Integrity.HIGH,
            confidentiality=confidentiality,
            compartments=frozenset(compartments),
        )
        for confidentiality in Confidentiality
        for compartments in ((), ("FIN",), ("HR",), ("FIN", "HR"))
    )
    destination_labels = tuple(destinations)

    for actual in universe:
        gateway = _budgeted_gateway(
            universe,
            budget=3.0,
            reserved_fraction=0.25,
        )
        for index, destination in enumerate(destination_labels * 2):
            gateway.authorize(
                "echo",
                {},
                ExecutionContext(labels={"source": actual, "destination": destination}),
                legitimate=index % 4 == 0,
            )
            assert gateway.spent_bits() <= 3.0 + 1e-12


def test_true_label_must_be_in_the_label_universe():
    gateway = _budgeted_gateway(_universe((Confidentiality.INTERNAL,)))
    secret = SecurityLabel(
        integrity=Integrity.HIGH,
        confidentiality=Confidentiality.SECRET,
    )

    with pytest.raises(ValueError, match="universe must contain"):
        gateway.authorize(
            "echo",
            {},
            _context(secret, ()),
        )


def test_hashable_label_keys_support_unhashable_security_labels():
    from trustcalc.gateway.leakage import label_key, to_label

    label = SecurityLabel(
        integrity=Integrity.HIGH,
        confidentiality=Confidentiality.INTERNAL,
        compartments=frozenset({"FIN"}),
        metadata={"origin": "test"},
    )

    with pytest.raises(TypeError):
        hash(label)
    assert to_label(label_key(label)) == SecurityLabel(
        integrity=Integrity.HIGH,
        confidentiality=Confidentiality.INTERNAL,
        compartments=frozenset({"FIN"}),
    )
