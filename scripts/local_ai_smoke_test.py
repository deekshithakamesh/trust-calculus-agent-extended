"""Local smoke test for the public TrustCalc API and runtime enforcement boundary."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from trustcalc import (
    ExecutionContext,
    GatewayValidator,
    PUBLIC_LABEL,
    PolicyEngine,
    PolicyEnforcer,
    TaintTracker,
    ToolGateway,
    ToolRegistry,
)


def main() -> None:
    tracker = TaintTracker()
    message = tracker.wrap("hello", PUBLIC_LABEL, name="message")

    registry = ToolRegistry()
    gateway = ToolGateway(
        registry=registry,
        validator=GatewayValidator(),
        enforcer=PolicyEnforcer(PolicyEngine()),
    )

    context = ExecutionContext(
        labels={"source": message.label, "destination": PUBLIC_LABEL},
    )

    decision = gateway.authorize("my-tool", {}, context)
    if not decision.denied:
        raise AssertionError("Gateway should deny unregistered tools by default")

    # Sanity-check the policy engine and taint wrapper still work in the public API.
    if message.label is None:
        raise AssertionError("message.label should be present after wrapping")

    print("Local API smoke test passed")


if __name__ == "__main__":
    main()
