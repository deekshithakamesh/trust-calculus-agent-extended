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
class _EchoTool(Tool):
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


def _budgeted_gateway(universe, *, budget=3.0, reserved_fraction=0.0, per_caller=False):
    registry = ToolRegistry()
    registry.register("echo", _EchoTool())
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
        per_caller=per_caller,
    )


def _context(source, compartments, user_id=None):
    return ExecutionContext(
        user_id=user_id,
        labels={
            "source": source,
            "destination": SecurityLabel(
                integrity=Integrity.HIGH,
                confidentiality=Confidentiality.INTERNAL,
                compartments=frozenset(compartments),
            ),
        },
    )


def test_reserved_share_keeps_legitimate_workload_admitted():
    universe = _universe((Confidentiality.INTERNAL,))
    true_label = next(label for label in universe if label.compartments == {"HR"})
    gateway = _budgeted_gateway(universe, budget=2.0, reserved_fraction=0.5)

    probe = gateway.authorize("echo", {}, _context(true_label, {"FIN"}))
    assert probe.denied
    assert gateway.spent_bits() == pytest.approx(1.0)
    blocked_probe = gateway.authorize("echo", {}, _context(true_label, {"HR"}))
    assert blocked_probe.denied
    assert blocked_probe.explanation == "Tool call denied by policy."
    assert gateway.spent_bits() == pytest.approx(1.0)

    legitimate = gateway.authorize(
        "echo",
        {},
        _context(true_label, {"HR"}),
        legitimate=True,
    )
    assert legitimate.allowed
    assert gateway.spent_bits() == pytest.approx(2.0)
    assert gateway.spent_bits() <= 2.0


def test_total_leakage_stays_within_budget_for_each_secret():
    universe = _universe()
    destinations = tuple(
        SecurityLabel(
            integrity=Integrity.HIGH,
            confidentiality=confidentiality,
            compartments=frozenset(compartments),
        )
        for confidentiality in Confidentiality
        for compartments in ((), ("FIN",), ("HR",), ("FIN", "HR"))
    )
    for secret in universe:
        gateway = _budgeted_gateway(
            universe,
            budget=3.0,
            reserved_fraction=0.25,
        )
        for index, destination in enumerate(destinations * 2):
            gateway.authorize(
                "echo",
                {},
                ExecutionContext(
                    labels={"source": secret, "destination": destination},
                ),
                legitimate=index % 4 == 0,
            )
            assert gateway.spent_bits() <= 3.0 + 1e-12


def test_caller_budgets_are_isolated():
    universe = _universe((Confidentiality.INTERNAL,))
    secret = next(label for label in universe if label.compartments == {"HR"})
    gateway = _budgeted_gateway(universe, budget=1.0, per_caller=True)

    first = gateway.authorize(
        "echo",
        {},
        _context(secret, {"FIN"}, user_id="caller-a"),
        protected_value_id="record",
    )
    assert first.denied
    assert gateway.spent_bits(
        "record",
        context=ExecutionContext(user_id="caller-a"),
    ) == pytest.approx(1.0)

    second = gateway.authorize(
        "echo",
        {},
        _context(secret, {"HR"}, user_id="caller-b"),
        protected_value_id="record",
    )
    assert second.allowed
    assert gateway.spent_bits(
        "record",
        context=ExecutionContext(user_id="caller-b"),
    ) == pytest.approx(1.0)


def test_universe_must_contain_the_true_label():
    gateway = _budgeted_gateway(_universe((Confidentiality.INTERNAL,)))
    secret = SecurityLabel(
        integrity=Integrity.HIGH,
        confidentiality=Confidentiality.SECRET,
    )
    with pytest.raises(ValueError, match="universe must contain"):
        gateway.authorize("echo", {}, _context(secret, ()))
