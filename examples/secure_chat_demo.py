"""Small demo assistant that shows a prompt-to-policy security trace in real time.

This is intentionally lightweight: it is a local, toy "AI assistant" that chooses
from a small set of tools and submits each tool call through TrustCalc's gateway.
The objective is to make the runtime flow visible to a reviewer:

    prompt -> semantic risk analysis -> labels -> capability checks -> gateway decision -> allow/deny

It is designed for demonstration and presentation, not for production deployment.
"""

from __future__ import annotations

import json
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from trustcalc import (
    CONFIDENTIAL_LABEL,
    PUBLIC_LABEL,
    SECRET_LABEL,
    TOP_SECRET_LABEL,
    ExecutionContext,
    GatewayValidator,
    PolicyEngine,
    PolicyEnforcer,
    TaintTracker,
    Tool,
    ToolGateway,
    ToolRegistry,
)
from trustcalc.core.labels import Confidentiality, Integrity, SecurityLabel
from trustcalc.policy.capabilities import Capability, CapabilityScope, CapabilitySet


SAFE_LOCAL_ROOT = ROOT / "examples" / "demo_workspace"
SAFE_LOCAL_ROOT.mkdir(parents=True, exist_ok=True)


@dataclass
class SecurityTraceStep:
    step: str
    ms: float
    details: dict[str, object]


class LocalFileTool(Tool):
    def __init__(self):
        super().__init__(
            name="local_file",
            description="Read or write files in the local sandbox.",
            required_capability="local.file.read",
        )

    def execute(self, **kwargs):
        operation = kwargs["operation"]
        path = kwargs["path"]
        target = SAFE_LOCAL_ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if operation == "read":
            if not target.exists():
                return {"status": "missing_file", "path": str(target)}
            return {"status": "ok", "path": str(target), "content": target.read_text(encoding="utf-8")[:200]}
        if operation == "write":
            target.write_text(kwargs.get("content", ""), encoding="utf-8")
            return {"status": "ok", "path": str(target), "bytes": len(kwargs.get("content", ""))}
        return {"status": "unsupported_operation", "operation": operation}


class EmailTool(Tool):
    def __init__(self):
        super().__init__(
            name="send_email",
            description="Send outbound email.",
            required_capability="external.email.send",
        )

    def execute(self, **kwargs):
        return {"status": "not_implemented", "recipient": kwargs.get("recipient"), "subject": kwargs.get("subject")}


class WebSearchTool(Tool):
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the internet for public information.",
            required_capability="external.web.search",
        )

    def execute(self, **kwargs):
        return {"status": "not_implemented", "query": kwargs.get("query")}


class BankTransferTool(Tool):
    def __init__(self):
        super().__init__(
            name="bank_transfer",
            description="Transfer funds from a bank account.",
            required_capability="finance.bank.transfer",
        )

    def execute(self, **kwargs):
        return {"status": "blocked_by_demo", "amount": kwargs.get("amount"), "account": kwargs.get("account")}


class ShellTool(Tool):
    def __init__(self):
        super().__init__(
            name="shell_command",
            description="Execute a shell command in a sandboxed local environment.",
            required_capability="local.shell.execute",
        )

    def execute(self, **kwargs):
        return {"status": "not_implemented", "command": kwargs.get("command")}


# Capability model: local-only by default for demo.
LOCAL_CAPS = CapabilitySet(
    frozenset(
        {
            Capability("local_file", "read", CapabilityScope.LOCAL),
            Capability("local_file", "write", CapabilityScope.LOCAL),
            Capability("local.shell", "execute", CapabilityScope.LOCAL),
            Capability("local.file", "read", CapabilityScope.LOCAL),
        }
    )
)

# This is a demo configuration: the local assistant is allowed to operate only in the local sandbox.
ALLOWED_LOCAL_ONLY = CapabilitySet(
    frozenset(
        {
            Capability("local.file", "read", CapabilityScope.LOCAL),
            Capability("local.file", "write", CapabilityScope.LOCAL),
            Capability("local.shell", "execute", CapabilityScope.LOCAL),
        }
    )
)


def build_gateway() -> ToolGateway:
    registry = ToolRegistry()
    registry.register("local_file", LocalFileTool())
    registry.register("send_email", EmailTool())
    registry.register("web_search", WebSearchTool())
    registry.register("bank_transfer", BankTransferTool())
    registry.register("shell_command", ShellTool())

    gateway = ToolGateway(
        registry=registry,
        validator=GatewayValidator(),
        enforcer=PolicyEnforcer(PolicyEngine()),
    )
    return gateway


def risk_profile(prompt: str) -> dict[str, object]:
    """A lightweight semantic risk profile for the demo.

    This is intentionally not a keyword blacklist. It combines: sensitive terms,
    action terms, destination terms, and indirect-risk terms to approximate the
    security intent of the user's request.
    """
    lowered = prompt.lower()

    sensitive_terms = [
        "bank", "account", "transfer", "funds", "password", "secret", "token",
        "confidential", "medical", "finance", "personal", "ssn", "api key"
    ]
    action_terms = ["send", "transfer", "write", "delete", "execute", "download", "email", "search", "call"]
    external_terms = ["internet", "external", "url", "api", "web", "email", "phone", "smtp", "remote"]
    local_terms = ["local", "sandbox", "workspace", "this machine", "docs", "file", "read file", "within app"]

    sensitivity_score = sum(2 for term in sensitive_terms if term in lowered)
    action_score = sum(2 for term in action_terms if term in lowered)
    external_score = sum(2 for term in external_terms if term in lowered)
    local_score = sum(1 for term in local_terms if term in lowered)

    # Coarse semantic interpretation.
    risk = sensitivity_score + action_score + external_score
    if "bank" in lowered or "transfer" in lowered:
        risk += 4
    if "read file" in lowered or "open file" in lowered:
        risk += 1
    if "local" in lowered or "sandbox" in lowered:
        risk -= 1

    return {
        "sensitivity_score": sensitivity_score,
        "action_score": action_score,
        "external_score": external_score,
        "local_score": local_score,
        "risk_score": max(0, risk),
        "is_sensitive_action": risk >= 6,
        "is_external_action": external_score > 0,
    }


def classify_tool(prompt: str) -> tuple[str, dict[str, object]]:
    lowered = prompt.lower()

    if re.search(r"(read|open|show|display)\s+(file|document|log|notes|workspace)", lowered):
        return "local_file", {"operation": "read", "path": "demo_notes.txt"}
    if re.search(r"(write|save|create)\s+(file|note|document)", lowered):
        return "local_file", {"operation": "write", "path": "demo_notes.txt", "content": "safe local note"}
    if re.search(r"(email|send mail|send email)", lowered):
        return "send_email", {"recipient": "demo@example.com", "subject": "demo", "body": "hello"}
    if re.search(r"(search the web|web search|google|lookup)", lowered):
        return "web_search", {"query": "public demo query"}
    if re.search(r"(bank|transfer|funds|account|wire)", lowered):
        return "bank_transfer", {"account": "checking", "amount": 1000}
    if re.search(r"(shell|run command|execute|terminal)", lowered):
        return "shell_command", {"command": "echo safe demo"}

    return "local_file", {"operation": "read", "path": "demo_notes.txt"}


def build_context_for_tool(prompt: str, tool_name: str) -> ExecutionContext:
    profile = risk_profile(prompt)
    source_label = TOP_SECRET_LABEL if profile["is_sensitive_action"] else SECRET_LABEL if profile["sensitivity_score"] > 0 else PUBLIC_LABEL
    destination_label = PUBLIC_LABEL

    if tool_name in {"local_file", "shell_command"}:
        destination_label = PUBLIC_LABEL
    elif tool_name in {"send_email", "web_search", "bank_transfer"}:
        destination_label = PUBLIC_LABEL

    # Local-only demo: capabilities are permitted only inside the sandbox.
    context = ExecutionContext(
        user_id="demo-user",
        capabilities=ALLOWED_LOCAL_ONLY,
        labels={
            "source": source_label,
            "destination": destination_label,
            "prompt_risk": profile["risk_score"],
            "sensitive_action": profile["is_sensitive_action"],
            "external_action": profile["is_external_action"],
        },
        metadata={
            "tool_name": tool_name,
            "semantic_profile": profile,
        },
    )
    return context


def run_secure_trace(prompt: str) -> dict[str, object]:
    gateway = build_gateway()
    tracker = TaintTracker()
    steps: list[SecurityTraceStep] = []

    start = time.perf_counter_ns()
    profile = risk_profile(prompt)
    steps.append(SecurityTraceStep("semantic_risk", (time.perf_counter_ns() - start) / 1_000_000, {"profile": profile}))

    start = time.perf_counter_ns()
    wrapped_prompt = tracker.wrap(prompt, SECRET_LABEL if profile["sensitivity_score"] > 0 else PUBLIC_LABEL, name="user_prompt")
    steps.append(SecurityTraceStep("label_assignment", (time.perf_counter_ns() - start) / 1_000_000, {"label": str(wrapped_prompt.label)}))

    tool_name, tool_args = classify_tool(prompt)
    start = time.perf_counter_ns()
    context = build_context_for_tool(prompt, tool_name)
    steps.append(SecurityTraceStep("context_build", (time.perf_counter_ns() - start) / 1_000_000, {"tool": tool_name, "labels": dict(context.labels)}))

    start = time.perf_counter_ns()
    decision = gateway.authorize(tool_name, tool_args, context)
    steps.append(SecurityTraceStep("policy_gate", (time.perf_counter_ns() - start) / 1_000_000, {"decision": decision.to_dict()}))

    result = {"allowed": False, "reason": "denied"}
    if decision.allowed:
        start = time.perf_counter_ns()
        result = gateway.execute(tool_name, tool_args, context)
        steps.append(SecurityTraceStep("tool_execution", (time.perf_counter_ns() - start) / 1_000_000, {"result": result}))
        result["allowed"] = True
    else:
        result = {
            "allowed": False,
            "reason": decision.explanation,
            "tool": tool_name,
            "trace": [s.step for s in steps],
        }

    def to_jsonable(obj):
        if isinstance(obj, dict):
            return {str(k): to_jsonable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [to_jsonable(v) for v in obj]
        if isinstance(obj, tuple):
            return [to_jsonable(v) for v in obj]
        if hasattr(obj, "value") and isinstance(obj, (Confidentiality, Integrity)):
            return obj.name
        if hasattr(obj, "to_dict"):
            return to_jsonable(obj.to_dict())
        if isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        return str(obj)

    return {
        "prompt": prompt,
        "tool": tool_name,
        "profile": profile,
        "decision": to_jsonable(decision.to_dict()),
        "result": to_jsonable(result),
        "trace": [
            {"step": s.step, "ms": round(s.ms, 3), "details": to_jsonable(s.details)}
            for s in steps
        ],
    }


class DemoAssistant:
    """Minimal local assistant that selects a tool and passes it through the secure gateway."""

    def __init__(self):
        self.gateway = build_gateway()

    def chat(self, prompt: str) -> str:
        trace = run_secure_trace(prompt)
        formatted = json.dumps(trace, indent=2)
        return formatted


def interactive_demo():
    assistant = DemoAssistant()
    print("TrustCalc local demo assistant. Type 'quit' to exit.")
    while True:
        user_input = input("\nPrompt> ").strip()
        if user_input.lower() in {"quit", "exit", "q"}:
            print("Goodbye.")
            break
        print(assistant.chat(user_input))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_demo()
    else:
        demo_prompts = [
            "Please read the local sandbox file demo_notes.txt.",
            "Please send an email to demo@example.com with the confidential account details.",
            "I want to transfer $1000 from the bank account to an external recipient.",
            "Search the web for public information on the latest AI news.",
        ]
        for prompt in demo_prompts:
            print(f"\nPROMPT: {prompt}\n")
            print(json.dumps(run_secure_trace(prompt), indent=2))
            print("-" * 80)
