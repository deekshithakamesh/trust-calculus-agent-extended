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

# optional trust model
from trustcalc.trust.model import TrustStore


@dataclass(slots=True)
class PolicyEnforcer:
    """
    Gateway policy enforcement.

    This class performs authorization only.
    It never executes tools.

    The enforcer optionally integrates an uncertainty-aware TrustStore
    which provides contextual trust and confidence values for subjects
    (tools) and actions. Decisions can then use trust+confidence+risk
    to make more nuanced authorization choices.
    """

    policy_engine: PolicyEngine

    # Optional trust store for dynamic trust reasoning
    trust_store: "TrustStore" | None = None

    # Thresholds for demonstration; these may be configured elsewhere
    high_risk_threshold: float = 0.7
    medium_risk_threshold: float = 0.5

    # Minimum confidence required to allow high-risk actions without extra confirmation
    min_confidence_for_high_risk: float = 0.2

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
        # Trust-aware capability/risk enforcement
        # --------------------------------------------------

        # Determine subject (tool) name and action
        tool_name = getattr(tool, 'name', None) or str(tool)
        action = arguments.get('action') or context.metadata.get('action') or 'default'
        risk = arguments.get('risk') or context.metadata.get('risk') or 'medium'

        # If a trust store is available, consult it
        if self.trust_store is not None:
            expected = self.trust_store.expected_trust(tool_name, action)
            conf = self.trust_store.confidence(tool_name, action)

            # Use AuthorityEngine to make a deterministic, explainable decision
            try:
                from trustcalc.authority.engine import AuthorityEngine
                ae = AuthorityEngine()
                # delegation depth and provenance warnings may be passed in arguments
                delegation_depth = int(arguments.get("delegation_depth", 0))
                provenance_warnings = arguments.get("provenance_warnings", None)
                trajectory_features = arguments.get("trajectory_features", None)

                auth_dec = ae.decide(
                    subject=tool_name,
                    action=action,
                    expected=expected,
                    confidence=conf,
                    risk=risk,
                    delegation_depth=delegation_depth,
                    provenance_warnings=provenance_warnings,
                    trajectory_features=trajectory_features,
                )

                # Map AuthorityDecision -> Policy Decision
                if auth_dec.decision == "ALLOW":
                    return Decision.allow(
                        explanation=f"Allowed by AuthorityEngine: {auth_dec.reason}",
                        trust=expected,
                        confidence=conf,
                        authority=auth_dec.decision,
                        authority_reason=auth_dec.reason,
                    )
                if auth_dec.decision == "VERIFY":
                    return Decision.indeterminate(
                        explanation=f"Verification required by AuthorityEngine: {auth_dec.reason}",
                        trust=expected,
                        confidence=conf,
                        authority=auth_dec.decision,
                        authority_reason=auth_dec.reason,
                    )
                # For other cases prefer conservative behavior
                return Decision.deny(
                    explanation=f"Authority decision: {auth_dec.decision} - {auth_dec.reason}",
                    trust=expected,
                    confidence=conf,
                    authority=auth_dec.decision,
                    authority_reason=auth_dec.reason,
                )
            except Exception:
                # fallback to legacy numerical thresholds if anything goes wrong
                pass

            # Simple decision rules combining trust, confidence and risk
            if risk == 'high':
                if expected < self.high_risk_threshold:
                    return Decision.deny(
                        explanation=(
                            f"High-risk action '{action}' denied: trust={expected:.3f} < "
                            f"threshold={self.high_risk_threshold}"
                        ),
                        trust=expected,
                        confidence=conf,
                        required=self.high_risk_threshold,
                    )

                if conf < self.min_confidence_for_high_risk:
                    return Decision.deny(
                        explanation=(
                            f"High-risk action '{action}' denied due to low confidence: {conf:.3f}"
                        ),
                        trust=expected,
                        confidence=conf,
                        reason='low_confidence',
                    )

            elif risk == 'medium':
                if expected < self.medium_risk_threshold:
                    return Decision.deny(
                        explanation=(
                            f"Medium-risk action '{action}' denied: trust={expected:.3f} < "
                            f"threshold={self.medium_risk_threshold}"
                        ),
                        trust=expected,
                        confidence=conf,
                        required=self.medium_risk_threshold,
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
