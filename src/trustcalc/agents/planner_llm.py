"""
trustcalc.agents.planner_llm
============================

Planner LLM.

Responsible for converting a user goal into an execution
plan. The planner never executes actions directly.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PlannerLLM:
    """
    Planner component.

    Produces execution plans from user goals.
    """

    model_name: str = "planner"

    system_prompt: str = (
        "You are a secure planning agent."
    )

    planning_history: list[str] = field(
        default_factory=list
    )

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def plan(
        self,
        goal: str,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Produce an execution plan.

        This is currently a placeholder implementation.
        """

        self.planning_history.append(goal)

        return [
            {
                "type": "llm",
                "prompt": goal,
            }
        ]

    # ---------------------------------------------------------

    def explain_plan(
        self,
        plan: list[dict[str, Any]],
    ) -> str:
        """
        Produce a human-readable description of a plan.
        """

        lines = []

        for index, step in enumerate(plan, start=1):

            step_type = step.get("type", "unknown")

            lines.append(
                f"{index}. {step_type}"
            )

        return "\n".join(lines)

    # ---------------------------------------------------------

    def history(self) -> list[str]:
        """
        Return planning history.
        """

        return list(self.planning_history)

    # ---------------------------------------------------------

    def clear_history(self) -> None:
        """
        Clear planning history.
        """

        self.planning_history.clear()

    # ---------------------------------------------------------

    def __len__(self) -> int:

        return len(self.planning_history)