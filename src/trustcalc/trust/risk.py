from __future__ import annotations

from typing import Dict


_BASE_RISK: Dict[str, float] = {
    "web_search": 0.05,
    "file_read": 0.10,
    "file_write": 0.35,
    "database_read": 0.40,
    "database_write": 0.70,
    "code_execution": 0.95,
    "shell_exec": 0.90,
    "email_send": 0.55,
    "network_request": 0.30,
    "tool_call": 0.25,
    "default": 0.50,
}


def estimate_action_risk(action: str, context: str = "") -> float:
    """Return a normalized risk score for an action in context."""
    normalized = (action or "default").strip().lower().replace("-", "_")
    risk = _BASE_RISK.get(normalized, _BASE_RISK["default"])
    if context and "secret" in context.lower():
        risk = min(1.0, risk + 0.15)
    if context and "untrusted" in context.lower():
        risk = min(1.0, risk + 0.10)
    return min(max(risk, 0.0), 1.0)


def required_trust(risk: float) -> float:
    """Minimum trust required to authorize an action of this risk."""
    risk = min(max(float(risk), 0.0), 1.0)
    return 0.5 + 0.5 * risk
