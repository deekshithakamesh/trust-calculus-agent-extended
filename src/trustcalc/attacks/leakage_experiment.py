"""Exhaustive comparison of leakage-budget allocation designs."""

from __future__ import annotations

import random
from dataclasses import dataclass
from itertools import combinations
from typing import Any

from trustcalc.core.labels import Confidentiality, Integrity, SecurityLabel
from trustcalc.gateway import BudgetedGateway, GatewayAudit, GatewayValidator
from trustcalc.gateway.enforcement import PolicyEnforcer
from trustcalc.gateway.gateway import ToolGateway
from trustcalc.gateway.leakage import LabelKey, label_key, to_label
from trustcalc.policy.engine import PolicyEngine
from trustcalc.runtime.execution_context import ExecutionContext
from trustcalc.tools.base import Tool
from trustcalc.tools.registry import ToolRegistry

COMPARTMENTS = ("FIN", "HR")
RANDOM_SEEDS = (1, 2, 3, 4, 5)
BUDGETS: tuple[float | None, ...] = (None, 4.0, 3.5, 3.0, 2.0, 1.0)
DESIGNS = ("shared", "reserved", "per_caller")
LEGITIMATE_DESTINATION = SecurityLabel(
    integrity=Integrity.HIGH,
    confidentiality=Confidentiality.INTERNAL,
)


def build_label_universe() -> tuple[SecurityLabel, ...]:
    """Enumerate all 20 confidentiality/compartment combinations."""
    compartment_sets = tuple(
        frozenset(subset)
        for size in range(len(COMPARTMENTS) + 1)
        for subset in combinations(COMPARTMENTS, size)
    )
    return tuple(
        SecurityLabel(
            integrity=Integrity.HIGH,
            confidentiality=confidentiality,
            compartments=compartments,
        )
        for confidentiality in Confidentiality
        for compartments in compartment_sets
    )


@dataclass(slots=True)
class _ProbeTool(Tool):
    name: str = "sink"

    def execute(self, **kwargs):
        return None


def _gateway() -> ToolGateway:
    registry = ToolRegistry()
    registry.register("sink", _ProbeTool())
    return ToolGateway(
        registry=registry,
        validator=GatewayValidator(),
        enforcer=PolicyEnforcer(PolicyEngine()),
        audit=GatewayAudit(),
    )


def _context(
    secret: SecurityLabel,
    destination: SecurityLabel,
    caller_id: str,
) -> ExecutionContext:
    return ExecutionContext(
        user_id=caller_id,
        labels={"source": secret, "destination": destination},
    )


def _allowed(candidate: SecurityLabel, destination: SecurityLabel) -> bool:
    return candidate.can_flow_to(destination)


def _request_order(
    strategy: str,
    destinations: tuple[SecurityLabel, ...],
) -> list[SecurityLabel]:
    requests = list(destinations)
    if strategy.startswith("random-"):
        random.Random(int(strategy.removeprefix("random-"))).shuffle(requests)
    return requests


def _probe(
    gateway: BudgetedGateway,
    secret: SecurityLabel,
    *,
    strategy: str,
    universe: tuple[SecurityLabel, ...],
    caller_id: str,
) -> tuple[frozenset[LabelKey], int]:
    candidates = frozenset(label_key(label) for label in universe)
    requests = _request_order(strategy, universe)
    attempts = 0
    while len(candidates) > 1 and requests:
        if strategy == "greedy":
            scored = []
            for index, destination in enumerate(requests):
                allowed_count = sum(
                    _allowed(to_label(candidate), destination)
                    for candidate in candidates
                )
                denied_count = len(candidates) - allowed_count
                scored.append((min(allowed_count, denied_count), -index, destination))
            best_score = max(item[0] for item in scored)
            if best_score == 0:
                break
            destination = max(scored, key=lambda item: (item[0], item[1]))[2]
            requests.remove(destination)
        else:
            destination = requests.pop(0)
            first_outcome = _allowed(to_label(next(iter(candidates))), destination)
            if all(
                _allowed(to_label(candidate), destination) == first_outcome
                for candidate in candidates
            ):
                continue

        decision = gateway.authorize(
            "sink",
            {},
            _context(secret, destination, caller_id),
        )
        attempts += 1
        if gateway.gateway.audit.history()[-1]["reason"] == "Leakage budget exceeded.":
            break
        candidates = frozenset(
            candidate
            for candidate in candidates
            if _allowed(to_label(candidate), destination) == decision.allowed
        )
        if label_key(secret) not in candidates:
            raise AssertionError("A transcript removed its true label.")
    return candidates, attempts


def _simulate(
    secret: SecurityLabel,
    *,
    budget: float | None,
    design: str,
    strategy: str,
    universe: tuple[SecurityLabel, ...],
) -> dict[str, Any]:
    reserved_fraction = 0.25 if design == "reserved" else 0.0
    probe_caller = "probe" if design == "per_caller" else "shared"
    budgeted = BudgetedGateway(
        gateway=_gateway(),
        label_universe=universe,
        budget=budget,
        reserved_fraction=reserved_fraction,
        per_caller=design == "per_caller",
    )
    candidates, attempts = _probe(
        budgeted,
        secret,
        strategy=strategy,
        universe=universe,
        caller_id=probe_caller,
    )
    probe_bits = budgeted.spent_bits(
        context=ExecutionContext(user_id=probe_caller),
    )

    legitimate_caller = "legitimate" if design == "per_caller" else probe_caller
    legitimate = budgeted.authorize(
        "sink",
        {},
        _context(secret, LEGITIMATE_DESTINATION, legitimate_caller),
        legitimate=design == "reserved",
    )
    legitimate_budget_admitted = (
        budgeted.gateway.audit.history()[-1]["reason"] != "Leakage budget exceeded."
    )
    legitimate_bits = budgeted.spent_bits(
        context=ExecutionContext(user_id=legitimate_caller),
    )
    max_caller_bits = max(probe_bits, legitimate_bits)
    if budget is not None and max_caller_bits > budget + 1e-12:
        raise AssertionError("Observed leakage exceeded its configured budget.")

    return {
        "design": design,
        "budget": budget,
        "strategy": strategy,
        "secret_confidentiality": secret.confidentiality.name,
        "secret_compartments": sorted(secret.compartments),
        "probe_requests": attempts,
        "probe_leakage_bits": probe_bits,
        "remaining_candidates": len(candidates),
        "secret_identified": len(candidates) == 1,
        "legitimate_budget_admitted": legitimate_budget_admitted,
        "legitimate_policy_allowed": legitimate.allowed,
        "legitimate_leakage_bits": legitimate_bits,
        "max_caller_leakage_bits": max_caller_bits,
    }


def run_comparison() -> dict[str, Any]:
    """Run all secret, strategy, budget, and allocation-design combinations."""
    universe = build_label_universe()
    strategies = (
        "greedy",
        "sequential",
        *(f"random-{seed}" for seed in RANDOM_SEEDS),
    )
    cases = [
        _simulate(
            secret,
            budget=budget,
            design=design,
            strategy=strategy,
            universe=universe,
        )
        for design in DESIGNS
        for budget in BUDGETS
        for strategy in strategies
        for secret in universe
    ]
    greedy_unbounded = [
        case
        for case in cases
        if case["budget"] is None and case["strategy"] == "greedy"
    ]
    if not all(case["secret_identified"] for case in greedy_unbounded):
        raise AssertionError("Unbudgeted greedy failed to identify every label.")

    summaries = []
    for design in DESIGNS:
        for budget in BUDGETS:
            group = [
                case for case in cases
                if case["design"] == design and case["budget"] == budget
            ]
            summaries.append(
                {
                    "design": design,
                    "budget": budget,
                    "mean_probe_leakage_bits": sum(
                        case["probe_leakage_bits"] for case in group
                    ) / len(group),
                    "max_probe_leakage_bits": max(
                        case["probe_leakage_bits"] for case in group
                    ),
                    "min_probe_leakage_bits": min(
                        case["probe_leakage_bits"] for case in group
                    ),
                    "secret_identification_rate": sum(
                        case["secret_identified"] for case in group
                    ) / len(group),
                    "legitimate_budget_admission_rate": sum(
                        case["legitimate_budget_admitted"] for case in group
                    ) / len(group),
                    "legitimate_policy_allow_rate": sum(
                        case["legitimate_policy_allowed"] for case in group
                    ) / len(group),
                    "max_caller_leakage_bits": max(
                        case["max_caller_leakage_bits"] for case in group
                    ),
                }
            )
    return {
        "assumptions": {
            "label_universe": "20 labels: 5 confidentiality levels x 4 FIN/HR compartment subsets",
            "prior": "Uniform over the enumerated labels.",
            "request_independence": (
                "Probe destinations and arguments are selected from public "
                "information and do not depend on the true label."
            ),
            "legitimate_destination": "INTERNAL with no compartments.",
            "reserved_fraction": 0.25,
            "per_caller_model": (
                "Probe and legitimate calls have separate user_id budgets; "
                "collusion across callers is not modeled."
            ),
            "leakage_bound": (
                "The bound is evaluated per protected value and per caller "
                "for per-caller accounting under a uniform prior."
            ),
        },
        "budgets": list(BUDGETS),
        "designs": list(DESIGNS),
        "strategies": list(strategies),
        "secrets": len(universe),
        "case_count": len(cases),
        "summary": summaries,
        "cases": cases,
    }
