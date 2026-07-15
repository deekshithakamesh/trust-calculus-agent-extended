"""
trustcalc.policy.engine
=======================

Policy Decision Point (PDP).

Evaluates policy rules against runtime state and returns immutable
Decision objects.

Evaluation strategy

    Rule
        ↓
Atomic evaluator
        ↓
Decision
        ↓
Composite evaluator
        ↓
Final Decision

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass

from trustcalc.core.labels import SecurityLabel
from trustcalc.policy.capabilities import CapabilitySet
from trustcalc.policy.decisions import (
    Decision,
    DecisionEffect,
)
from trustcalc.policy.rules import (
    Rule,
    RuleContext,
    RuleResult,
    IntegrityRule,
    ConfidentialityRule,
    CapabilityRule,
    CompartmentRule,
    AndRule,
    OrRule,
    NotRule,
)


# ================================================================
# Policy Engine
# ================================================================


@dataclass(slots=True)
class PolicyEngine:
    """
    Central Policy Decision Point.

    All policy evaluation is performed here.

    The engine itself contains no mutable state.
    """

    # ------------------------------------------------------------

    def evaluate(
        self,
        rule: Rule,
        context: RuleContext,
    ) -> Decision:
        """
        Entry point.

        Dispatches to the appropriate evaluator.
        """

        if isinstance(rule, IntegrityRule):
            return self._evaluate_integrity(
                rule,
                context,
            )

        if isinstance(rule, ConfidentialityRule):
            return self._evaluate_confidentiality(
                rule,
                context,
            )

        if isinstance(rule, CapabilityRule):
            return self._evaluate_capability(
                rule,
                context,
            )

        if isinstance(rule, CompartmentRule):
            return self._evaluate_compartment(
                rule,
                context,
            )

        if isinstance(rule, AndRule):
            return self._evaluate_and(
                rule,
                context,
            )

        if isinstance(rule, OrRule):
            return self._evaluate_or(
                rule,
                context,
            )

        if isinstance(rule, NotRule):
            return self._evaluate_not(
                rule,
                context,
            )

        return Decision.indeterminate(explanation=f"Unknown rule: {type(rule)}")

    # ============================================================
    # Atomic Rules
    # ============================================================

    def _evaluate_integrity(
        self,
        rule: IntegrityRule,
        context: RuleContext,
    ) -> Decision:

        label: SecurityLabel = context.label

        if label.integrity >= rule.minimum:

            return Decision.allow("Integrity requirement satisfied.").add_match(
                rule.name
            )

        return Decision.deny("Integrity requirement failed.").add_violation(rule.name)

    # ------------------------------------------------------------

    def _evaluate_confidentiality(
        self,
        rule: ConfidentialityRule,
        context: RuleContext,
    ) -> Decision:

        label: SecurityLabel = context.label

        if label.confidentiality <= rule.maximum:

            return Decision.allow("Confidentiality requirement satisfied.").add_match(
                rule.name
            )

        return Decision.deny("Confidentiality requirement failed.").add_violation(
            rule.name
        )

    # ------------------------------------------------------------

    def _evaluate_capability(
        self,
        rule: CapabilityRule,
        context: RuleContext,
    ) -> Decision:

        capabilities: CapabilitySet = context.capability_set

        if capabilities.allows(
            rule.resource,
            rule.action,
            context.runtime_context,
        ):

            return Decision.allow("Capability granted.").add_match(rule.name)

        return Decision.deny("Capability missing.").add_missing_capability(
            f"{rule.resource}:{rule.action}"
        )

    # ------------------------------------------------------------

    def _evaluate_compartment(
        self,
        rule: CompartmentRule,
        context: RuleContext,
    ) -> Decision:

        label: SecurityLabel = context.label

        if rule.compartment in label.compartments:

            return Decision.allow("Compartment requirement satisfied.").add_match(
                rule.name
            )

        return Decision.deny("Missing required compartment.").add_violation(rule.name)
        # ============================================================

    # Composite Rules
    # ============================================================

    def _evaluate_and(
        self,
        rule: AndRule,
        context: RuleContext,
    ) -> Decision:
        """
        Evaluate logical AND.

        Every child rule must succeed.
        """

        decision = Decision.allow(explanation="AND rule satisfied.")

        for child in rule.rules:

            result = self.evaluate(
                child,
                context,
            )

            if result.denied:

                return (
                    Decision.deny("AND rule failed.")
                    .with_metadata(failed_rule=child.name)
                    .add_violation(child.name)
                )

            decision = self._merge(
                decision,
                result,
            )

        return decision

    # ------------------------------------------------------------

    def _evaluate_or(
        self,
        rule: OrRule,
        context: RuleContext,
    ) -> Decision:
        """
        Evaluate logical OR.

        At least one child rule must succeed.
        """

        failures: list[str] = []

        for child in rule.rules:

            result = self.evaluate(
                child,
                context,
            )

            if result.allowed:

                return Decision.allow("OR rule satisfied.").add_match(child.name)

            failures.extend(result.violated_rules)

        decision = Decision.deny("OR rule failed.")

        for failure in failures:
            decision = decision.add_violation(failure)

        return decision

    # ------------------------------------------------------------

    def _evaluate_not(
        self,
        rule: NotRule,
        context: RuleContext,
    ) -> Decision:
        """
        Evaluate logical NOT.
        """

        result = self.evaluate(
            rule.rule,
            context,
        )

        if result.allowed:

            return Decision.deny("NOT rule failed.").add_violation(rule.name)

        return Decision.allow("NOT rule satisfied.").add_match(rule.name)

    # ============================================================
    # Decision Aggregation
    # ============================================================

    def _merge(
        self,
        left: Decision,
        right: Decision,
    ) -> Decision:
        """
        Merge two policy decisions.

        Deny overrides Allow.
        """

        if left.effect == DecisionEffect.DENY or right.effect == DecisionEffect.DENY:

            effect = DecisionEffect.DENY

        elif (
            left.effect == DecisionEffect.INDETERMINATE
            or right.effect == DecisionEffect.INDETERMINATE
        ):

            effect = DecisionEffect.INDETERMINATE

        else:

            effect = DecisionEffect.ALLOW

        return Decision(
            effect=effect,
            matched_rules=(left.matched_rules + right.matched_rules),
            violated_rules=(left.violated_rules + right.violated_rules),
            missing_capabilities=(
                left.missing_capabilities + right.missing_capabilities
            ),
            explanation=(left.explanation or right.explanation),
            metadata={
                **left.metadata,
                **right.metadata,
            },
        )

    # ============================================================
    # Multiple Rule Evaluation
    # ============================================================

    def evaluate_all(
        self,
        rules: tuple[Rule, ...],
        context: RuleContext,
    ) -> Decision:
        """
        Evaluate an ordered collection of rules.

        The overall policy uses deny-overrides semantics.
        """

        decision = Decision.allow(explanation="Policy evaluation started.")

        for rule in rules:

            result = self.evaluate(
                rule,
                context,
            )

            decision = self._merge(
                decision,
                result,
            )

            if decision.denied:
                break

        return decision
        # ============================================================

    # Validation
    # ============================================================

    def validate(
        self,
        rules: tuple[Rule, ...],
    ) -> bool:
        """
        Validate a collection of rules.

        Returns
        -------
        bool
            True if every rule appears structurally valid.
        """

        try:

            for rule in rules:

                if rule is None:
                    return False

                if not hasattr(rule, "name"):
                    return False

                if not hasattr(rule, "rule_type"):
                    return False

            return True

        except Exception:
            return False

    # ============================================================
    # Statistics
    # ============================================================

    def statistics(
        self,
        decision: Decision,
    ) -> dict[str, int]:
        """
        Produce simple evaluation statistics.
        """

        return {
            "matched_rules": len(decision.matched_rules),
            "violated_rules": len(decision.violated_rules),
            "missing_capabilities": len(decision.missing_capabilities),
        }

    # ============================================================
    # Explanation
    # ============================================================

    def explain(
        self,
        decision: Decision,
    ) -> str:
        """
        Produce a human-readable explanation.
        """

        lines: list[str] = []

        lines.append(f"Decision: {decision.effect.value}")

        if decision.matched_rules:

            lines.append("Matched Rules:")

            for rule in decision.matched_rules:

                lines.append(f"  • {rule}")

        if decision.violated_rules:

            lines.append("Violated Rules:")

            for rule in decision.violated_rules:

                lines.append(f"  • {rule}")

        if decision.missing_capabilities:

            lines.append("Missing Capabilities:")

            for capability in decision.missing_capabilities:

                lines.append(f"  • {capability}")

        if decision.explanation:

            lines.append("")
            lines.append(decision.explanation)

        return "\n".join(lines)
