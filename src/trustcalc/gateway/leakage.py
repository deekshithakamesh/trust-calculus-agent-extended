"""Leakage-budgeted access to a tool gateway."""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from typing import Mapping, Sequence, TypeAlias

from trustcalc.core.labels import (
    Confidentiality,
    Integrity,
    SecurityLabel,
)
from trustcalc.gateway.exceptions import AuthorizationError
from trustcalc.gateway.gateway import ToolGateway
from trustcalc.policy.decisions import Decision
from trustcalc.runtime.execution_context import ExecutionContext

LabelKey: TypeAlias = tuple[int, int, tuple[str, ...]]


def label_key(label: SecurityLabel) -> LabelKey:
    """Return a hashable key for a label's security dimensions."""
    if not isinstance(label, SecurityLabel):
        raise TypeError("The label universe must contain SecurityLabel values.")
    return (
        int(label.integrity),
        int(label.confidentiality),
        tuple(sorted(label.compartments)),
    )


def to_label(key: LabelKey) -> SecurityLabel:
    """Rebuild a label from its hashable security-dimension key."""
    integrity, confidentiality, compartments = key
    return SecurityLabel(
        integrity=Integrity(integrity),
        confidentiality=Confidentiality(confidentiality),
        compartments=frozenset(compartments),
    )


@dataclass(slots=True)
class BudgetedGateway:
    """Enforce a transcript leakage budget for protected source labels.

    The leakage measure is surprisal under ``prior``. With the default
    uniform prior this is ``log2(|universe| / |knowledge_set|)``. Requests
    must be independent of the protected value: their arguments and
    destination labels must be selected from public information. The formal
    leakage guarantee documented and tested here is a bound under the uniform
    prior only; a non-uniform prior produces model-dependent bit values.

    ``reserved_fraction`` sets aside that fraction of the total budget for
    calls marked ``legitimate=True``. Probe calls may use only the remainder;
    legitimate calls may use the full budget. The total transcript leakage
    remains capped by ``budget``. With ``per_caller=True``, each authenticated
    ``ExecutionContext.user_id`` has an independent knowledge set and budget;
    cross-caller collusion is outside that accounting model.
    """

    gateway: ToolGateway
    label_universe: Sequence[SecurityLabel]
    budget: float | None
    reserved_fraction: float = 0.0
    prior: Mapping[LabelKey, float] | None = None
    expose_denial_reasons: bool | None = None
    per_caller: bool = False
    _keys: tuple[LabelKey, ...] = field(init=False, repr=False)
    _weights: dict[LabelKey, float] = field(init=False, repr=False)
    _knowledge: dict[tuple[str | None, str], frozenset[LabelKey]] = field(
        init=False,
        default_factory=dict,
        repr=False,
    )

    def __post_init__(self) -> None:
        labels = tuple(self.label_universe)
        if not labels:
            raise ValueError("The label universe must not be empty.")

        keys = tuple(label_key(label) for label in labels)
        if len(set(keys)) != len(keys):
            raise ValueError("The label universe must not contain duplicate labels.")

        if self.budget is not None and (
            not math.isfinite(self.budget) or self.budget < 0
        ):
            raise ValueError("budget must be a finite non-negative number or None.")
        if (
            not math.isfinite(self.reserved_fraction)
            or not 0 <= self.reserved_fraction <= 1
        ):
            raise ValueError("reserved_fraction must be between 0 and 1.")

        self.label_universe = labels
        self._keys = keys
        if self.prior is None:
            self._weights = {key: 1 / len(keys) for key in keys}
        else:
            if set(self.prior) != set(keys):
                raise ValueError("prior must provide one positive weight per label.")
            weights = dict(self.prior)
            if any(not math.isfinite(weight) or weight <= 0 for weight in weights.values()):
                raise ValueError("prior weights must be finite and positive.")
            total = sum(weights.values())
            self._weights = {key: weight / total for key, weight in weights.items()}

    @property
    def _exposes_reasons(self) -> bool:
        if self.expose_denial_reasons is None:
            return self.gateway.expose_denial_reasons
        return self.expose_denial_reasons

    def _state_key(
        self,
        context: ExecutionContext | None,
        protected_value_id: str,
    ) -> tuple[str | None, str]:
        if not protected_value_id:
            raise ValueError("protected_value_id must not be empty.")
        caller_id = None
        if self.per_caller:
            if context is None or not context.user_id:
                raise ValueError("per-caller budgets require a non-empty user_id.")
            caller_id = context.user_id
        return caller_id, protected_value_id

    def _knowledge_for(
        self,
        context: ExecutionContext | None,
        protected_value_id: str,
    ) -> tuple[tuple[str | None, str], frozenset[LabelKey]]:
        state_key = self._state_key(context, protected_value_id)
        if state_key not in self._knowledge:
            self._knowledge[state_key] = frozenset(self._keys)
        return state_key, self._knowledge[state_key]

    def spent_bits(
        self,
        protected_value_id: str = "default",
        *,
        context: ExecutionContext | None = None,
    ) -> float:
        """Return transcript leakage for a protected value under its prior."""
        _, knowledge = self._knowledge_for(context, protected_value_id)
        mass = sum(self._weights[key] for key in knowledge)
        return max(0.0, -math.log2(mass))

    def _worst_case_cost(
        self,
        knowledge: frozenset[LabelKey],
        outcomes: Mapping[LabelKey, bool],
    ) -> float:
        current_mass = sum(self._weights[key] for key in knowledge)
        outcome_masses = {
            allowed: sum(
                self._weights[key]
                for key in knowledge
                if outcomes[key] is allowed
            )
            for allowed in (False, True)
        }
        nonempty_masses = [mass for mass in outcome_masses.values() if mass > 0]
        return max(
            (-math.log2(mass / current_mass) for mass in nonempty_masses),
            default=0.0,
        )

    def _public_decision(self, decision: Decision) -> Decision:
        if decision.denied and not self._exposes_reasons:
            return Decision.deny("Tool call denied by policy.")
        return decision

    def authorize(
        self,
        tool_name: str,
        arguments: dict,
        context: ExecutionContext,
        *,
        protected_value_id: str = "default",
        legitimate: bool = False,
    ) -> Decision:
        """Authorize a request and update the protected value's transcript."""
        source = context.labels.get("source")
        if source is None:
            return self.gateway.authorize(tool_name, arguments, context)
        source_key = label_key(source)
        if source_key not in self._weights:
            raise ValueError("The label universe must contain the true source label.")

        tool = self.gateway.registry.get(tool_name)
        if tool is None:
            return self.gateway.authorize(tool_name, arguments, context)
        self.gateway.validator.validate(tool, arguments)

        state_key, knowledge = self._knowledge_for(context, protected_value_id)
        outcomes: dict[LabelKey, bool] = {}
        decisions: dict[LabelKey, Decision] = {}
        for candidate_key in knowledge:
            candidate_labels = dict(context.labels)
            candidate_labels["source"] = to_label(candidate_key)
            candidate_context = replace(context, labels=candidate_labels)
            decision = self.gateway.enforcer.authorize(
                tool=tool,
                arguments=arguments,
                context=candidate_context,
            )
            decisions[candidate_key] = decision
            outcomes[candidate_key] = decision.allowed

        cost = self._worst_case_cost(knowledge, outcomes)
        spent = self.spent_bits(protected_value_id, context=context)
        if self.budget is not None:
            permitted_budget = self.budget
            if not legitimate:
                permitted_budget *= 1 - self.reserved_fraction
            if spent + cost > permitted_budget + 1e-12:
                denied = Decision.deny("Leakage budget exceeded.")
                self.gateway.audit.record_authorization(tool_name, denied)
                return self._public_decision(denied)

        actual_decision = decisions[source_key]
        observed_outcome = outcomes[source_key]
        updated = frozenset(
            key for key in knowledge if outcomes[key] is observed_outcome
        )
        self._knowledge[state_key] = updated
        self.gateway.audit.record_authorization(tool_name, actual_decision)
        return self._public_decision(actual_decision)

    def execute(
        self,
        tool_name: str,
        arguments: dict,
        context: ExecutionContext,
        *,
        protected_value_id: str = "default",
        legitimate: bool = False,
    ):
        """Authorize and execute a request through the wrapped gateway."""
        source = context.labels.get("source")
        if source is None:
            return self.gateway.execute(tool_name, arguments, context)

        tool = self.gateway.registry.get(tool_name)
        if tool is None:
            return self.gateway.execute(tool_name, arguments, context)

        decision = self.authorize(
            tool_name,
            arguments,
            context,
            protected_value_id=protected_value_id,
            legitimate=legitimate,
        )
        if decision.denied:
            raise AuthorizationError(decision.explanation)
        return self.gateway._execute_authorized_tool(tool_name, tool, arguments)
