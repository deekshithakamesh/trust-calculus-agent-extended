"""
trustcalc.agents.orchestrator
=============================

High-level agent orchestrator.

Coordinates planning, interpretation, execution, and
policy enforcement.

The orchestrator does not execute tools directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from trustcalc.agents.planner_llm import PlannerLLM
from trustcalc.agents.quarantined_llm import QuarantinedLLM
from trustcalc.runtime.execution_context import ExecutionContext
from trustcalc.runtime.interpreter import Interpreter


@dataclass(slots=True)
class Orchestrator:
    """
    High-level agent coordinator.
    """

    planner: PlannerLLM

    interpreter: Interpreter

    llm: QuarantinedLLM

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def run(
        self,
        goal: str,
        context: ExecutionContext,
    ) -> list[Any]:
        """
        Execute an agent goal.
        """

        plan = self.planner.plan(goal)

        return self.interpreter.execute(
            plan,
            context,
        )

    # ---------------------------------------------------------

    def plan(
        self,
        goal: str,
    ) -> list[dict[str, Any]]:
        """
        Produce an execution plan only.
        """

        return self.planner.plan(goal)

    # ---------------------------------------------------------

    def explain(
        self,
        goal: str,
    ) -> str:
        """
        Explain the generated execution plan.
        """

        plan = self.plan(goal)

        return self.planner.explain_plan(
            plan
        )

    # ---------------------------------------------------------

    def generate(
        self,
        prompt: str,
    ):
        """
        Generate an LLM response without executing tools.
        """

        return self.llm.generate(prompt)

    # ---------------------------------------------------------

    def execute_plan(
        self,
        plan: list[dict[str, Any]],
        context: ExecutionContext,
    ):
        """
        Execute an existing plan.
        """

        return self.interpreter.execute(
            plan,
            context,
        )