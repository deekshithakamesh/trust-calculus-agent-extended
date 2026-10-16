"""
trustcalc.gateway.gateway
=========================

Policy Enforcement Point (PEP).

The ToolGateway coordinates request validation,
policy enforcement, audit logging, and tool execution.

It intentionally delegates work to:

    - GatewayValidator
    - PolicyEnforcer
    - GatewayAudit

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from trustcalc.gateway.audit import GatewayAudit
from trustcalc.gateway.enforcement import PolicyEnforcer
from trustcalc.gateway.exceptions import (
    AuthorizationError,
    InvalidToolError,
    ToolExecutionError,
)
from trustcalc.gateway.validator import GatewayValidator
from trustcalc.policy.decisions import Decision
from trustcalc.runtime.execution_context import ExecutionContext
from trustcalc.tools.registry import ToolRegistry


@dataclass(slots=True)
class ToolGateway:
    """
    Runtime Policy Enforcement Point.
    """

    registry: ToolRegistry

    validator: GatewayValidator

    enforcer: PolicyEnforcer

    audit: GatewayAudit = field(
        default_factory=GatewayAudit
    )

    expose_denial_reasons: bool = False

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def authorize(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        context: ExecutionContext,
    ) -> Decision:
        """
        Evaluate a tool request without executing it.

        Returns a Decision. The caller is responsible for
        acting on the decision.
        """

        tool = self.registry.get(tool_name)

        if tool is None:
            decision = Decision.deny(
                explanation=(
                    f"Unknown tool '{tool_name}'."
                )
            )
            self.audit.record_authorization(tool_name, decision)
            return self._public_decision(decision)

        self.validator.validate(
            tool,
            arguments,
        )

        decision = self.enforcer.authorize(
            tool=tool,
            arguments=arguments,
            context=context,
        )

        self.audit.record_authorization(
            tool_name,
            decision,
        )

        return self._public_decision(decision)

    def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        context: ExecutionContext,
    ):
        """
        Execute a tool request.
        """

        tool = self.registry.get(tool_name)

        if tool is None:
            raise InvalidToolError(
                f"Unknown tool '{tool_name}'."
            )

        # ---------------- Validation ----------------

        self.validator.validate(
            tool,
            arguments,
        )

        # ---------------- Authorization ----------------

        decision = self.enforcer.authorize(
            tool=tool,
            arguments=arguments,
            context=context,
        )

        self.audit.record_authorization(
            tool_name,
            decision,
        )

        if decision.denied:
            raise AuthorizationError(
                self._public_decision(decision).explanation
            )

        return self._execute_authorized_tool(
            tool_name,
            tool,
            arguments,
        )

    def _public_decision(self, decision: Decision) -> Decision:
        if decision.denied and not self.expose_denial_reasons:
            return Decision.deny("Tool call denied by policy.")
        return decision

    def _execute_authorized_tool(
        self,
        tool_name: str,
        tool: Any,
        arguments: dict[str, Any],
    ):
        """Execute a tool after authorization has already succeeded."""
        try:
            result = tool.execute(
                **arguments
            )
        except Exception as exc:
            self.audit.record_execution(
                tool_name,
                success=False,
            )
            raise ToolExecutionError(
                f"Tool '{tool_name}' failed during execution."
            ) from exc

        self.audit.record_execution(
            tool_name,
            success=True,
        )

        return result

    # ---------------------------------------------------------

    def contains(
        self,
        tool_name: str,
    ) -> bool:

        return self.registry.get(
            tool_name
        ) is not None

    # ---------------------------------------------------------

    def get(
        self,
        tool_name: str,
    ):

        return self.registry.get(
            tool_name
        )

    # ---------------------------------------------------------

    def registered_tools(self):

        return self.registry.names()

    # ---------------------------------------------------------

    def clear_audit(self):

        self.audit.clear()

    # ---------------------------------------------------------

    def history(self):

        return self.audit.history()

    # ---------------------------------------------------------

    def statistics(self):

        return self.audit.statistics()
