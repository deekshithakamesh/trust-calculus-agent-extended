from __future__ import annotations

from trustcalc.core.labels import Label
from trustcalc.policy import PolicyEngine
from trustcalc.runtime.taint_tracker import TaintTracker


class Mediator:
    def __init__(self) -> None:
        self.policy_engine = PolicyEngine()
        self.taint_tracker = TaintTracker()

    def authorize(self, action: str, subject: Label, resource: str) -> bool:
        return self.policy_engine.evaluate(action, subject, resource)

    def inspect(self, name: str) -> Label | None:
        return self.taint_tracker.get_taint(name)
