"""
trustcalc.runtime.interpreter
=============================

Secure runtime interpreter.

The Interpreter executes agent plans while coordinating:

    • TaintTracker
    • PolicyEngine
    • ToolGateway

It does NOT implement tool logic itself.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from trustcalc.policy.engine import PolicyEngine
from trustcalc.runtime.execution_context import ExecutionContext
from trustcalc.runtime.taint_tracker import TaintTracker


@dataclass(slots=True)
class Interpreter:
    """
    Secure runtime interpreter.

    Parameters
    ----------
    taint_tracker
        Runtime taint propagation engine.

    policy_engine
        Policy Decision Point.

    gateway
        Tool Gateway (late bound to avoid circular imports).
    """

    taint_tracker: TaintTracker

    policy_engine: PolicyEngine

    gateway: Any

    execution_log: list[dict[str, Any]] = field(
        default_factory=list
    )

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def execute(
        self,
        plan: list[dict[str, Any]],
        context: ExecutionContext,
    ) -> list[Any]:
        """
        Execute an ordered execution plan.
        """

        results: list[Any] = []

        self.execution_log.clear()

        for step in plan:

            result = self.execute_step(
                step,
                context,
            )

            results.append(result)

        return results

    # ---------------------------------------------------------

    def execute_step(
        self,
        step: dict[str, Any],
        context: ExecutionContext,
    ):
        """
        Execute one step.
        """

        self.validate_step(step)

        step_type = step["type"]

        self.execution_log.append(
            {
                "step": step_type,
                "status": "started",
            }
        )

        if step_type == "tool":

            result = self.execute_tool(
                step,
                context,
            )

        elif step_type == "llm":

            result = self.execute_llm(
                step,
                context,
            )

        elif step_type == "transform":

            result = self.execute_transform(
                step,
                context,
            )

        else:

            raise ValueError(
                f"Unknown step type: {step_type}"
            )

        self.execution_log[-1]["status"] = "completed"

        return result

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    def validate_step(
        self,
        step: dict[str, Any],
    ) -> None:
        """
        Basic structural validation.
        """

        if "type" not in step:

            raise ValueError(
                "Execution step missing 'type'."
            )

        if step["type"] not in {
            "tool",
            "llm",
            "transform",
        }:

            raise ValueError(
                f"Unsupported step type: {step['type']}"
            )
        # ---------------------------------------------------------
    # Tool Execution
    # ---------------------------------------------------------

    def execute_tool(
        self,
        step: dict[str, Any],
        context: ExecutionContext,
    ):
        """
        Execute a tool through the Tool Gateway.

        Every tool invocation MUST pass through the gateway.
        """

        tool_name = step["tool"]

        arguments = step.get(
            "args",
            {},
        )

        # --------------------------------------------------
        # Gateway authorization
        # --------------------------------------------------

        decision = self.gateway.authorize(
            tool_name=tool_name,
            arguments=arguments,
            context=context,
        )

        if decision.denied:

            self.execution_log.append(
                {
                    "tool": tool_name,
                    "status": "blocked",
                    "reason": decision.explanation,
                }
            )

            raise PermissionError(
                decision.explanation
            )

        # --------------------------------------------------
        # Tool invocation
        # --------------------------------------------------

        result = self.gateway.execute(
            tool_name=tool_name,
            arguments=arguments,
            context=context,
        )

        # --------------------------------------------------
        # Register inside taint tracker
        # --------------------------------------------------

        trusted_result = self.taint_tracker.taint(
            result
        )

        self.execution_log.append(
            {
                "tool": tool_name,
                "status": "completed",
            }
        )

        return trusted_result

    # ---------------------------------------------------------
    # LLM Execution
    # ---------------------------------------------------------

    def execute_llm(
        self,
        step: dict[str, Any],
        context: ExecutionContext,
    ):
        """
        Execute an LLM call.

        The interpreter delegates model execution to the
        gateway (or another runtime component) so that
        prompts and responses can be tracked uniformly.
        """

        prompt = step["prompt"]

        result = self.gateway.execute_llm(
            prompt=prompt,
            context=context,
        )

        trusted = self.taint_tracker.taint(
            result
        )

        self.execution_log.append(
            {
                "llm": True,
                "status": "completed",
            }
        )

        return trusted

    # ---------------------------------------------------------
    # Transform Execution
    # ---------------------------------------------------------

    def execute_transform(
        self,
        step: dict[str, Any],
        context: ExecutionContext,
    ):
        """
        Execute a pure runtime transformation.
        """

        value = step["value"]

        function = step["function"]

        transformed = self.taint_tracker.transform(
            value,
            function,
            description="runtime transform",
        )

        self.execution_log.append(
            {
                "transform": True,
                "status": "completed",
            }
        )

        return transformed

    # ---------------------------------------------------------
    # Execution Helpers
    # ---------------------------------------------------------

    def reset(self):
        """
        Reset interpreter state.
        """

        self.execution_log.clear()

    def history(self):
        """
        Return execution history.
        """

        return list(self.execution_log)

    def last_step(self):
        """
        Return the most recent execution record.
        """

        if not self.execution_log:
            return None

        return self.execution_log[-1]
        # ---------------------------------------------------------
    # Plan Validation
    # ---------------------------------------------------------

    def validate_plan(
        self,
        plan: list[dict[str, Any]],
    ) -> bool:
        """
        Validate an execution plan before execution.

        Returns
        -------
        bool
            True if the plan is structurally valid.
        """

        if not isinstance(plan, list):
            return False

        try:

            for step in plan:

                self.validate_step(step)

            return True

        except Exception:

            return False

    # ---------------------------------------------------------
    # Safe Execute
    # ---------------------------------------------------------

    def safe_execute(
        self,
        plan: list[dict[str, Any]],
        context: ExecutionContext,
    ) -> list[Any]:
        """
        Execute a plan while trapping runtime failures.

        Any failure immediately aborts execution.
        """

        results: list[Any] = []

        self.execution_log.clear()

        for index, step in enumerate(plan):

            try:

                result = self.execute_step(
                    step,
                    context,
                )

                results.append(result)

            except Exception as exc:

                self.execution_log.append(
                    {
                        "step": index,
                        "status": "failed",
                        "error": str(exc),
                    }
                )

                break

        return results

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def statistics(self) -> dict[str, int]:
        """
        Execution statistics.
        """

        total = len(self.execution_log)

        completed = sum(
            entry.get("status") == "completed"
            for entry in self.execution_log
        )

        failed = sum(
            entry.get("status") == "failed"
            for entry in self.execution_log
        )

        blocked = sum(
            entry.get("status") == "blocked"
            for entry in self.execution_log
        )

        return {

            "steps": total,

            "completed": completed,

            "failed": failed,

            "blocked": blocked,
        }

    # ---------------------------------------------------------
    # Execution Report
    # ---------------------------------------------------------

    def report(self) -> dict[str, Any]:
        """
        Produce a runtime execution report.
        """

        return {

            "statistics": self.statistics(),

            "history": self.history(),
        }

    # ---------------------------------------------------------
    # Rollback
    # ---------------------------------------------------------

    def rollback(self):
        """
        Reset interpreter state.

        In the MVP this clears the execution log.
        Future versions may also revert runtime state.
        """

        self.reset()