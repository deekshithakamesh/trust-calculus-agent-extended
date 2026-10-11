"""Live local-model security demo using Ollama + TrustCalc.

This example demonstrates a minimal end-to-end flow:

    user prompt -> local LLM (llama3:latest via Ollama)
      -> parsed intent / tool candidate
      -> TrustCalc label + capability + sandbox enforcement
      -> allow / deny trace printed with timing

The local LLM is not executed with full autonomy; instead, the policy layer acts as
an enforcement boundary before any sensitive or external tool is allowed.
"""

from __future__ import annotations

import json
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import request, error

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from trustcalc import (
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
from trustcalc.policy.capabilities import Capability, CapabilityScope, CapabilitySet

SAFE_LOCAL_ROOT = ROOT / "examples" / "demo_workspace"
SAFE_LOCAL_ROOT.mkdir(parents=True, exist_ok=True)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3:latest"


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


def build_gateway() -> ToolGateway:
    registry = ToolRegistry()
    registry.register("local_file", LocalFileTool())
    registry.register("send_email", EmailTool())
    registry.register("web_search", WebSearchTool())
    registry.register("bank_transfer", BankTransferTool())
    registry.register("shell_command", ShellTool())

    return ToolGateway(
        registry=registry,
        validator=GatewayValidator(),
        enforcer=PolicyEnforcer(PolicyEngine()),
    )


ALLOWED_LOCAL_ONLY = CapabilitySet(
    frozenset(
        {
            Capability("local.file", "read", CapabilityScope.LOCAL),
            Capability("local.file", "write", CapabilityScope.LOCAL),
            Capability("local.shell", "execute", CapabilityScope.LOCAL),
        }
    )
)


@dataclass
class SecurityTraceStep:
    step: str
    ms: float
    details: dict[str, Any]


def risk_profile(prompt: str) -> dict[str, Any]:
    lowered = prompt.lower()

    sensitive_terms = [
        "bank", "account", "transfer", "funds", "secret", "token", "password",
        "medical", "financial", "api key", "ssn", "confidential"
    ]
    action_terms = ["send", "transfer", "write", "delete", "execute", "download", "email", "search", "call"]
    external_terms = ["internet", "external", "url", "api", "email", "phone", "smtp", "remote"]
    local_terms = ["local", "sandbox", "workspace", "this machine", "file", "inside app"]

    sensitivity_score = sum(2 for term in sensitive_terms if term in lowered)
    action_score = sum(2 for term in action_terms if term in lowered)
    external_score = sum(2 for term in external_terms if term in lowered)
    local_score = sum(1 for term in local_terms if term in lowered)

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


def classify_tool_from_prompt(prompt: str) -> tuple[str, dict[str, Any]]:
    lowered = prompt.lower()

    if re.search(r"(read|open|show|display)\s+(file|document|note|log|workspace)", lowered):
        return "local_file", {"operation": "read", "path": "demo_notes.txt"}
    if re.search(r"(write|save|create)\s+(file|note|document)", lowered):
        return "local_file", {"operation": "write", "path": "demo_notes.txt", "content": "safe local note"}
    if re.search(r"(email|send mail|send email)", lowered):
        return "send_email", {"recipient": "demo@example.com", "subject": "demo", "body": "hello"}
    if re.search(r"(search the web|web search|google|lookup|browse)", lowered):
        return "web_search", {"query": "public information"}
    if re.search(r"(bank|transfer|funds|account|wire)", lowered):
        return "bank_transfer", {"account": "checking", "amount": 1000}
    if re.search(r"(shell|run command|execute|terminal)", lowered):
        return "shell_command", {"command": "echo safe demo"}

    return "local_file", {"operation": "read", "path": "demo_notes.txt"}


def build_context(prompt: str, tool_name: str) -> ExecutionContext:
    profile = risk_profile(prompt)
    source_label = TOP_SECRET_LABEL if profile["is_sensitive_action"] else SECRET_LABEL if profile["sensitivity_score"] > 0 else PUBLIC_LABEL
    destination_label = PUBLIC_LABEL

    return ExecutionContext(
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


def ollama_generate(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2, "num_predict": 256},
    }
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(OLLAMA_URL, data=body, headers={"Content-Type": "application/json"})

    try:
        with request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except error.URLError as exc:
        raise RuntimeError(f"Could not reach Ollama at {OLLAMA_URL}. Is Ollama running? Details: {exc}") from exc

    if isinstance(data, dict) and "response" in data:
        return str(data["response"]).strip()
    if isinstance(data, dict):
        return json.dumps(data, indent=2)
    return str(data)


def to_jsonable(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(v) for v in obj]
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    if hasattr(obj, "to_dict"):
        return to_jsonable(obj.to_dict())
    if hasattr(obj, "value"):
        return to_jsonable(obj.value)
    return str(obj)


def secure_decision_trace(prompt: str) -> dict[str, Any]:
    gateway = build_gateway()
    tracker = TaintTracker()
    steps: list[SecurityTraceStep] = []

    start = time.perf_counter_ns()
    profile = risk_profile(prompt)
    steps.append(SecurityTraceStep("risk_analysis", (time.perf_counter_ns() - start) / 1_000_000, {"profile": profile}))

    start = time.perf_counter_ns()
    wrapped_prompt = tracker.wrap(prompt, SECRET_LABEL if profile["sensitivity_score"] > 0 else PUBLIC_LABEL, name="user_prompt")
    steps.append(SecurityTraceStep("label_assignment", (time.perf_counter_ns() - start) / 1_000_000, {"label": str(wrapped_prompt.label)}))

    start = time.perf_counter_ns()
    llm_output = ollama_generate(prompt)
    steps.append(SecurityTraceStep("llm_generation", (time.perf_counter_ns() - start) / 1_000_000, {"llm_output": llm_output[:400]}))

    tool_name, tool_args = classify_tool_from_prompt(prompt)
    start = time.perf_counter_ns()
    context = build_context(prompt, tool_name)
    steps.append(SecurityTraceStep("context_build", (time.perf_counter_ns() - start) / 1_000_000, {"tool": tool_name, "labels": dict(context.labels)}))

    start = time.perf_counter_ns()
    decision = gateway.authorize(tool_name, tool_args, context)
    steps.append(SecurityTraceStep("gateway_decision", (time.perf_counter_ns() - start) / 1_000_000, {"decision": decision.to_dict()}))

    result: dict[str, Any]
    if decision.allowed:
        start = time.perf_counter_ns()
        result = gateway.execute(tool_name, tool_args, context)
        steps.append(SecurityTraceStep("tool_execution", (time.perf_counter_ns() - start) / 1_000_000, {"result": result}))
    else:
        result = {
            "allowed": False,
            "reason": decision.explanation,
            "tool": tool_name,
            "policy_boundary": "local sandbox only",
        }

    return {
        "model": MODEL_NAME,
        "prompt": prompt,
        "tool_candidate": tool_name,
        "llm_output": llm_output,
        "profile": profile,
        "decision": to_jsonable(decision.to_dict()),
        "result": to_jsonable(result),
        "trace": [
            {"step": s.step, "ms": round(s.ms, 3), "details": to_jsonable(s.details)}
            for s in steps
        ],
    }


def main() -> None:
    prompts = [
        "Please read the local sandbox file demo_notes.txt.",
        "Please send an email to demo@example.com with the confidential account details.",
        "I want to transfer $1000 from the bank account to an external recipient.",
        "Search the web for public information on the latest AI news.",
    ]

    print("TrustCalc + Ollama local demo")
    print(f"Model: {MODEL_NAME}")
    print("Local sandbox policy: deny external actions by default\n")

    for prompt in prompts:
        print("=" * 80)
        print(f"PROMPT: {prompt}\n")
        try:
            trace = secure_decision_trace(prompt)
            print(json.dumps(trace, indent=2))
        except RuntimeError as exc:
            print(f"Ollama unavailable: {exc}")
            print("Start Ollama with: ollama serve")
            break
        print()


if __name__ == "__main__":
    main()
