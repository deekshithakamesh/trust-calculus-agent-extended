from __future__ import annotations

from typing import List

from trustcalc.core.labels import Label


class Executor:
    def __init__(self) -> None:
        self.actions: List[str] = []

    def execute(self, action: str) -> str:
        self.actions.append(action)
        return f"executed:{action}"

    def label_for(self, action: str) -> Label:
        return Label("public") if action == "read" else Label("secret")
