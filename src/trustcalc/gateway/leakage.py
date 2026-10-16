"""Leakage-budgeted access to a tool gateway."""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from typing import Mapping, Sequence, TypeAlias

from trustcalc.core.labels import Confidentiality, Integrity, SecurityLabel
from trustcalc.gateway.exceptions import AuthorizationError, ToolExecutionError
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

    The default measure is ``log2(|universe| / |knowledge_set|)`` under a
    uniform prior. A custom prior changes the reported surprisal, but the
    documented budget guarantee is for the uniform prior only. The universe
    must include the true label.

    Requests must be selected from public information: their arguments and
    destination labels must not depend on the protected value. The refusal
    decision depends on the transcript and request only.

    A fraction of the budget can be reserved from probe requests. With
    per-caller accounting enabled, each non-empty ``ExecutionContext.user_id``
    gets a separate knowledge set; collusion between callers is not covered.
    """

    gateway: ToolGateway
    label_universe: Sequence[SecurityLabel]
    budget: float | None
    reserved_fraction: float = 0.0
    prior: Mapping[LabelKey, float] | None = None
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
        if not math.isfinite(self.reserved_fraction) or not 0 <= self.reserved_fraction <= 1:
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

    def _state_key(
        self,
        protected_value_id: str,
        context: ExecutionContext | None,
    ) -> tuple[str | None, str]:
        if not protected_value_id:
            raise ValueError("protected_value_id must not be empty.")
        user_id = None
        if self.per_caller:
            if context is None or not context.user_id:
                raise ValueError("per-caller budgets require a non-empty user_id.")
            user_id = context.user_id
        return user_id, protected_value_id

    def _knowledge_for(
        self,
        protected_value_id: str,
        context: ExecutionContext | None,
    ) -> tuple[tuple[str | None, str], frozenset[LabelKey]]:
        state_key = self._state_key(protected_value_id, context)
        if state_key not in self._knowledge:
            self._knowledge[state_key] = frozenset(self._keys)
        return state_key, self._knowledge[state_key]

    def spent_bits(
        self,
        protected_value_id: str = "default",
        *,
        context: ExecutionContext | None = None,
    ) -> float:
        """Return transcript surprisal under the configured prior."""
        _, knowledge = self._knowledge_for(protected_value_id, context)
        mass = sum(self._weights[key] for key in knowledge)
        return max(0.0, -math.log2(mass))

    def _worst_case_cost(
        self,
        knowledge: frozenset[LabelKey],
        outcomes: Mapping[LabelKey, bool],
    ) -> float:
        current_mass = sum(self._weights[key] for key in knowledge)
        class_masses = [
            sum(
                self._weights[key]
                for key in knowledge
                if outcomes[key] is allowed
            )
            for allowed in (False, True)
        ]
        return max(
            (
                -math.log2(mass / current_mass)
                for mass in class_masses
                if mass > 0
            ),
            default=0.0,
        )

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

        state_key, knowledge = self._knowledge_for(protected_value_id, context)
        decisions: dict[LabelKey, Decision] = {}
        outcomes: dict[LabelKey, bool] = {}
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
        permitted_budget = self.budget
        if permitted_budget is not None and not legitimate:
            permitted_budget *= 1 - self.reserved_fraction
        if permitted_budget is not None and spent + cost > permitted_budget + 1e-12:
            denied = Decision.deny("Leakage budget exceeded.")
            self.gateway.audit.record_authorization(tool_name, denied)
            return self.gateway._public_decision(denied)

        decision = decisions[source_key]
        outcome = outcomes[source_key]
        self._knowledge[state_key] = frozenset(
            key for key in knowledge if outcomes[key] is outcome
        )
        self.gateway.audit.record_authorization(tool_name, decision)
        return self.gateway._public_decision(decision)

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
        try:
            result = tool.execute(**arguments)
        except Exception as exc:
            self.gateway.audit.record_execution(tool_name, success=False)
            raise ToolExecutionError(
                f"Tool '{tool_name}' failed during execution."
            ) from exc
        self.gateway.audit.record_execution(tool_name, success=True)
        return result
