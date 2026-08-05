"""
Trusted agent executor.

Executes discrete actions and returns security labels for the
resulting information using the core Trust Calculus label model.
"""

from __future__ import annotations

from typing import List

from trustcalc.core.labels import (
    PUBLIC_LABEL,
    SECRET_LABEL,
    SecurityLabel,
)


class Executor:
    """
    Executes actions and assigns security labels.
    """

    def __init__(self) -> None:
        self.actions: List[str] = []

    def execute(self, action: str) -> str:
        """
        Execute a discrete action.
        """
        self.actions.append(action)
        return f"executed:{action}"

    def label_for(self, action: str) -> SecurityLabel:
        """
        Return the security label associated with an action.
        """

        if action == "read":
            return SECRET_LABEL

        return PUBLIC_LABEL

    def history(self) -> List[str]:
        """
        Return the list of executed actions.
        """

        return list(self.actions)
