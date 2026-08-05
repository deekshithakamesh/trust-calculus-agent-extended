"""
trustcalc.gateway.enforcement
=============================

Policy enforcement for the Tool Gateway.

The PolicyEnforcer is responsible for deciding whether a
validated tool request is authorized.

It delegates policy evaluation to the PolicyEngine and
performs additional gateway-level checks when necessary.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from trustcalc.policy.decisions import Decision
from trustcalc.policy.engine import PolicyEngine
from trustcalc.runtime.execution_context import ExecutionContext


@dataclass(slots=True)
class PolicyEnforcer:
    """
    Gateway policy enforcement.

    This class performs authorization only.
    It never executes tools.
    """

    policy_engine: PolicyEngine

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def authorize(
        self,
        tool: Any,
        arguments: dict[str, Any],
        context: ExecutionContext,
    ) -> Decision:
        """
        Determine whether a tool invocation is permitted.
        """

        rules = getattr(tool, "policy_rules", ())

        if rules:
            decision = self.policy_engine.evaluate_all(
                rules,
                context,
            )

            if decision.denied:
                return decision

        capability = getattr(tool, "required_capability", None)

        if capability is not None:

            if not self._check_capability(
                capability,
                context,
            ):
                return Decision.deny(
                    explanation=(
                        f"Missing capability '{capability}'."
                    )
                )

        # --------------------------------------------------
        # Information-flow enforcement
        # --------------------------------------------------

        source_label = context.labels.get(
            "source",
        )

        destination_label = context.labels.get(
            "destination",
        )

        if (
            source_label is not None
            and destination_label is not None
        ):

            decision = self.check_information_flow(
                source_label,
                destination_label,
            )

            if decision.denied:
                return decision

        return Decision.allow()

    # ---------------------------------------------------------
    # Capability Enforcement
    # ---------------------------------------------------------

    def _check_capability(
        self,
        capability: str,
        context: ExecutionContext,
    ) -> bool:
        """
        Verify that the execution context contains
        the required capability.
        """

        capabilities = getattr(
            context,
            "capabilities",
            None,
        )

        if capabilities is None:
            return False

        if hasattr(capabilities, "allows"):
            return capabilities.allows(capability)

        return capability in capabilities

    # ---------------------------------------------------------
    # Label Enforcement
    # ---------------------------------------------------------

    def check_information_flow(
        self,
        source_label,
        destination_label,
    ) -> Decision:
        """
        Verify information-flow constraints.

        This is fail-closed: if the source label does not expose a
        ``can_flow_to`` check, access is denied rather than silently
        permitted. This prevents an accidental bypass of the
        information-flow control policy.
        """

        if not hasattr(source_label, "can_flow_to"):

            return Decision.deny(
                explanation=(
                    "Information-flow check unavailable; "
                    "denying by default."
                )
            )

        if source_label.can_flow_to(destination_label):

            return Decision.allow(
                "Information flow permitted."
            )

        return Decision.deny(
            explanation=(
                "Information flow violates confidentiality, "
                "integrity, or compartment constraints."
            )
        )

    # ---------------------------------------------------------
    # Convenience
    # ---------------------------------------------------------

    def can_execute(
        self,
        tool: Any,
        arguments: dict[str, Any],
        context: ExecutionContext,
    ) -> bool:
        """
        Boolean authorization helper.
        """

        return self.authorize(
            tool,
            arguments,
            context,
        ).allowed
