"""
trustcalc.tools.shell_tool
==========================

Shell execution tool.

Provides controlled command execution.

IMPORTANT:
This implementation intentionally executes nothing.
Real execution should only be enabled in a sandboxed
environment and only after gateway authorization.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from trustcalc.tools.base import Tool


@dataclass(slots=True)
class ShellTool(Tool):
    """
    Shell command tool.
    """

    name: str = "shell"

    description: str = (
        "Execute operating system commands."
    )

    required_capability: str = "shell.execute"

    argument_schema = {
        "required": ("command",),
        "properties": {
            "command": str,
        },
    }

    def execute(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Placeholder shell execution.

        Real command execution should only be enabled
        after gateway approval and sandbox isolation.
        """

        command = kwargs["command"]

        return {
            "tool": self.name,
            "status": "not_implemented",
            "command": command,
        }