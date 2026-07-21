"""
trustcalc.core.flow_rules
=========================

High-level information flow policy.

This module wraps the mathematical lattice semantics with
policy-oriented flow decisions that can be extended by the
runtime or policy engine.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass

from trustcalc.core.labels import SecurityLabel
from trustcalc.core.lattice import flows_to


@dataclass(frozen=True, slots=True)
class FlowDecision:
    """
    Result of a flow evaluation.
    """

    allowed: bool
    reason: str = ""

    @property
    def denied(self) -> bool:
        return not self.allowed


class FlowRules:
    """
    High-level wrapper around lattice flow semantics.

    The lattice determines whether a flow is mathematically valid.

    This class allows additional policy checks to be added later
    without modifying the lattice implementation.
    """

    def can_flow(
        self,
        source: SecurityLabel,
        destination: SecurityLabel,
    ) -> bool:
        """
        Return True if information may legally flow.
        """
        return flows_to(source, destination)

    def evaluate(
        self,
        source: SecurityLabel,
        destination: SecurityLabel,
    ) -> FlowDecision:
        """
        Evaluate a flow and return an explanation.
        """

        if not flows_to(source, destination):

            return FlowDecision(
                allowed=False,
                reason=(
                    "Information flow violates confidentiality, "
                    "integrity, or compartment constraints."
                ),
            )

        return FlowDecision(
            allowed=True,
            reason="Flow permitted.",
        )

    def require(
        self,
        source: SecurityLabel,
        destination: SecurityLabel,
    ) -> None:
        """
        Raise PermissionError if the flow is not permitted.
        """

        decision = self.evaluate(source, destination)

        if decision.denied:
            raise PermissionError(decision.reason)