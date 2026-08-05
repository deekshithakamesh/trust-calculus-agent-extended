"""
Runtime mediation glue.

The Mediator coordinates the Policy Decision Point and the
TaintTracker to answer authorization and inspection questions
for the runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from trustcalc.core.labels import SecurityLabel
from trustcalc.policy.decisions import Decision
from trustcalc.policy.engine import PolicyEngine
from trustcalc.policy.rules import Rule, RuleContext
from trustcalc.runtime.taint_tracker import TaintTracker
from trustcalc.core.values import TrustedValue


@dataclass(slots=True)
class Mediator:
    """
    Coordination layer between policy and taint tracking.

    Parameters
    ----------
    policy_engine
        The Policy Decision Point used for authorization.

    taint_tracker
        Runtime taint propagation engine.
    """

    policy_engine: PolicyEngine = field(
        default_factory=PolicyEngine
    )

    taint_tracker: TaintTracker = field(
        default_factory=TaintTracker
    )

    # ---------------------------------------------------------
    # Authorization
    # ---------------------------------------------------------

    def authorize(
        self,
        rule: Rule,
        context: RuleContext,
    ) -> Decision:
        """
        Evaluate a single policy rule and return a Decision.
        """

        return self.policy_engine.evaluate(
            rule,
            context,
        )

    def authorize_all(
        self,
        rules: tuple[Rule, ...],
        context: RuleContext,
    ) -> Decision:
        """
        Evaluate an ordered set of rules with deny-overrides semantics.
        """

        return self.policy_engine.evaluate_all(
            rules,
            context,
        )

    # ---------------------------------------------------------
    # Compatibility helper: subject/resource style authorization
    # ---------------------------------------------------------

    def check(
        self,
        rule: Rule,
        subject: SecurityLabel,
        resource: str,
        capability_set: Any = None,
        runtime_context: Mapping[str, Any] | None = None,
    ) -> Decision:
        """
        Convenience wrapper that builds a RuleContext from a subject
        label and evaluates a rule against it.
        """

        rule_context = RuleContext(
            label=subject,
            capability_set=capability_set,
            tool_name=resource,
            action="access",
            runtime_context=runtime_context or {},
        )

        return self.authorize(
            rule,
            rule_context,
        )

    # ---------------------------------------------------------
    # Value inspection
    # ---------------------------------------------------------

    def inspect(
        self,
        name: str,
    ) -> TrustedValue[Any] | None:
        """
        Retrieve a tracked TrustedValue by name.
        """

        return self.taint_tracker.get_taint(name)

    def label_for(
        self,
        name: str,
    ) -> SecurityLabel | None:
        """
        Return the security label of a tracked value.
        """

        value = self.inspect(name)

        if value is None:
            return None

        return value.label

    # ---------------------------------------------------------
    # Flow control
    # ---------------------------------------------------------

    def can_flow(
        self,
        source_name: str,
        destination_label: SecurityLabel,
    ) -> bool:
        """
        Check whether a tracked value may flow into a label.
        """

        value = self.inspect(source_name)

        if value is None:
            return False

        return value.label.can_flow_to(
            destination_label
        )

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def statistics(self) -> dict[str, Any]:
        """
        Runtime statistics across policy and taint tracking.
        """

        return {
            "taint": self.taint_tracker.statistics(),
        }
