from __future__ import annotations

from .labels import Label


class PolicyEngine:
    def __init__(self) -> None:
        self._allowed = {"read": {"public"}}

    def evaluate(self, action: str, subject: Label, resource: str) -> bool:
        if action == "read" and subject.confidentiality in self._allowed[action]:
            return True
        return False
