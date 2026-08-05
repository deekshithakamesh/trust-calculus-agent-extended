"""
Integration tests wiring the real ToolGateway with the Interpreter.

These tests verify that the interpreter's tool execution path works
against the actual gateway (not a DummyGateway), and that tool
results are wrapped in TrustedValues with provenance.
"""

from __future__ import annotations

from dataclasses import dataclass

from trustcalc.core.labels import PUBLIC_LABEL
from trustcalc.gateway.enforcement import PolicyEnforcer
from trustcalc.gateway.exceptions import (
    AuthorizationError,
    InvalidToolError,
)
from trustcalc.gateway.gateway import ToolGateway
from trustcalc.gateway.validator import GatewayValidator
from trustcalc.policy.engine import PolicyEngine
from trustcalc.runtime.execution_context import ExecutionContext
from trustcalc.runtime.interpreter import Interpreter
from trustcalc.runtime.taint_tracker import TaintTracker
from trustcalc.tools.base import Tool
from trustcalc.tools.registry import ToolRegistry


@dataclass(slots=True)
class EchoTool(Tool):
    """A simple no-side-effect tool for integration tests."""

    name: str = "echo"
    description: str = "Echoes a message."
    required_capability: str | None = None

    argument_schema = {
        "required": ("message",),
        "properties": {"message": str},
    }

    def execute(self, **kwargs):
        return f"echo:{kwargs['message']}"


def _build_gateway(**context_kwargs):
    registry = ToolRegistry()
    registry.register("echo", EchoTool())

    validator = GatewayValidator()
    enforcer = PolicyEnforcer(policy_engine=PolicyEngine())
    gateway = ToolGateway(registry=registry, validator=validator, enforcer=enforcer)

    context = ExecutionContext(**context_kwargs)

    return gateway, context


def test_gateway_authorize_method_exists():
    gateway, _ = _build_gateway()

    decision = gateway.authorize(
        tool_name="echo",
        arguments={"message": "hi"},
        context=ExecutionContext(),
    )

    assert decision.allowed


def test_gateway_authorize_denies_unknown_tool():
    gateway, _ = _build_gateway()

    decision = gateway.authorize(
        tool_name="nope",
        arguments={},
        context=ExecutionContext(),
    )

    assert decision.denied


def test_gateway_execute_unknown_tool_raises():
    gateway, _ = _build_gateway()

    try:
        gateway.execute(
            tool_name="nope",
            arguments={},
            context=ExecutionContext(),
        )
        assert False, "expected InvalidToolError"
    except InvalidToolError:
        pass


def test_interpreter_executes_tool_through_real_gateway():
    gateway, context = _build_gateway()

    tracker = TaintTracker()

    interpreter = Interpreter(
        taint_tracker=tracker,
        policy_engine=PolicyEngine(),
        gateway=gateway,
    )

    plan = [
        {
            "type": "tool",
            "tool": "echo",
            "args": {"message": "hello"},
        }
    ]

    results = interpreter.execute(plan, context)

    trusted = results[0]

    assert trusted.value == "echo:hello"
    assert trusted.label == PUBLIC_LABEL
    assert tracker.validate(trusted)


def test_interpreter_blocks_when_ifc_denied():
    from trustcalc.core.labels import SECRET_LABEL

    gateway, _ = _build_gateway()

    # Source secret, destination public => illegal flow.
    context = ExecutionContext(
        labels={
            "source": SECRET_LABEL,
            "destination": PUBLIC_LABEL,
        }
    )

    tracker = TaintTracker()

    interpreter = Interpreter(
        taint_tracker=tracker,
        policy_engine=PolicyEngine(),
        gateway=gateway,
    )

    plan = [
        {
            "type": "tool",
            "tool": "echo",
            "args": {"message": "secret"},
        }
    ]

    try:
        interpreter.execute(plan, context)
        assert False, "expected PermissionError"
    except PermissionError:
        pass


def test_interpreter_wraps_result_in_trusted_value():
    gateway, context = _build_gateway()

    tracker = TaintTracker()

    interpreter = Interpreter(
        taint_tracker=tracker,
        policy_engine=PolicyEngine(),
        gateway=gateway,
    )

    plan = [
        {
            "type": "tool",
            "tool": "echo",
            "args": {"message": "wrapped"},
        }
    ]

    results = interpreter.execute(plan, context)

    trusted = results[0]

    from trustcalc.core.values import TrustedValue

    assert isinstance(trusted, TrustedValue)
    assert tracker.get_taint("echo") is trusted


def test_interpreter_history_records_tool_completion():
    gateway, context = _build_gateway()

    tracker = TaintTracker()

    interpreter = Interpreter(
        taint_tracker=tracker,
        policy_engine=PolicyEngine(),
        gateway=gateway,
    )

    plan = [
        {
            "type": "tool",
            "tool": "echo",
            "args": {"message": "hi"},
        }
    ]

    interpreter.execute(plan, context)

    history = interpreter.history()

    assert any(
        entry.get("tool") == "echo"
        and entry.get("status") == "completed"
        for entry in history
    )
