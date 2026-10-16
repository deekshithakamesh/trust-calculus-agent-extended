"""Measure information exposed by redacted gateway denials."""

from __future__ import annotations

import math
from dataclasses import dataclass

from trustcalc.core.labels import PUBLIC_LABEL, SECRET_LABEL
from trustcalc.gateway.audit import GatewayAudit
from trustcalc.gateway.enforcement import PolicyEnforcer
from trustcalc.gateway.gateway import ToolGateway
from trustcalc.gateway.validator import GatewayValidator
from trustcalc.policy.engine import PolicyEngine
from trustcalc.runtime.execution_context import ExecutionContext
from trustcalc.tools.base import Tool
from trustcalc.tools.registry import ToolRegistry

DENIAL_MESSAGE = "Tool call denied by policy."


@dataclass(slots=True)
class _ProbeTool(Tool):
    name: str = "sink"

    def execute(self, **kwargs):
        return None


@dataclass(slots=True)
class _CapabilityTool(Tool):
    name: str = "restricted"
    required_capability: str | None = "records:read"

    def execute(self, **kwargs):
        return None


def _gateway(tool: Tool) -> ToolGateway:
    registry = ToolRegistry()
    registry.register(tool.name, tool)
    return ToolGateway(
        registry=registry,
        validator=GatewayValidator(),
        enforcer=PolicyEnforcer(PolicyEngine()),
        audit=GatewayAudit(),
    )


def run_denial_probe() -> dict:
    """Compare observed denial feedback for public and secret source labels."""
    gateway = _gateway(_ProbeTool())
    observations = []
    for name, source in (("PUBLIC", PUBLIC_LABEL), ("SECRET", SECRET_LABEL)):
        decision = gateway.authorize(
            "sink",
            {},
            ExecutionContext(
                labels={"source": source, "destination": PUBLIC_LABEL},
            ),
        )
        observations.append(
            {
                "source_label": name,
                "allowed": decision.allowed,
                "caller_feedback": (
                    "Tool call allowed."
                    if decision.allowed
                    else decision.explanation
                ),
            }
        )

    outcome_counts: dict[bool, int] = {}
    for observation in observations:
        outcome = observation["allowed"]
        outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1
    observation_entropy = -sum(
        (count / len(observations)) * math.log2(count / len(observations))
        for count in outcome_counts.values()
    )

    capability_gateway = _gateway(_CapabilityTool())
    capability_decision = capability_gateway.authorize(
        "restricted",
        {},
        ExecutionContext(capabilities=set()),
    )
    capability_audit_reason = capability_gateway.audit.history()[-1]["reason"]

    return {
        "assumptions": {
            "prior": "Uniform over the two source labels in this probe.",
            "request": "Fixed tool arguments and PUBLIC destination.",
            "scope": (
                "The result measures this allow/deny channel only; it is not "
                "a bound for requests whose destination or arguments encode "
                "the protected label."
            ),
        },
        "observations": observations,
        "denial_message": DENIAL_MESSAGE,
        "capability_name_disclosed": (
            "records:read" in capability_decision.explanation
        ),
        "capability_audit_keeps_full_reason": (
            "records:read" in capability_audit_reason
        ),
        "allow_deny_channel_bits": observation_entropy,
    }
