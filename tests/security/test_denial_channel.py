from __future__ import annotations

from dataclasses import dataclass

import pytest

from trustcalc.gateway.enforcement import PolicyEnforcer
from trustcalc.gateway.exceptions import AuthorizationError
from trustcalc.gateway.gateway import ToolGateway
from trustcalc.gateway.validator import GatewayValidator
from trustcalc.policy.engine import PolicyEngine
from trustcalc.runtime.execution_context import ExecutionContext
from trustcalc.tools.base import Tool
from trustcalc.tools.registry import ToolRegistry


@dataclass(slots=True)
class ProtectedTool(Tool):
    name: str = "protected"
    required_capability: str | None = "records:read"

    def execute(self, **kwargs):
        return None


def _gateway(*, expose_denial_reasons: bool = False) -> ToolGateway:
    registry = ToolRegistry()
    registry.register("protected", ProtectedTool())
    return ToolGateway(
        registry=registry,
        validator=GatewayValidator(),
        enforcer=PolicyEnforcer(PolicyEngine()),
        expose_denial_reasons=expose_denial_reasons,
    )


def test_denial_feedback_is_generic_while_audit_keeps_full_reason():
    gateway = _gateway()

    decision = gateway.authorize(
        "protected",
        {},
        ExecutionContext(capabilities=set()),
    )

    assert decision.denied
    assert decision.explanation == "Tool call denied by policy."
    assert gateway.history()[-1]["reason"] == "Missing capability 'records:read'."


def test_execute_uses_generic_denial_feedback_by_default():
    gateway = _gateway()

    with pytest.raises(AuthorizationError, match="^Tool call denied by policy\\.$"):
        gateway.execute(
            "protected",
            {},
            ExecutionContext(capabilities=set()),
        )

    assert gateway.history()[-1]["reason"] == "Missing capability 'records:read'."


def test_denial_reasons_can_be_exposed_explicitly():
    gateway = _gateway(expose_denial_reasons=True)

    decision = gateway.authorize(
        "protected",
        {},
        ExecutionContext(capabilities=set()),
    )

    assert decision.denied
    assert decision.explanation == "Missing capability 'records:read'."
