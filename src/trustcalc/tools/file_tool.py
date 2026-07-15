"""
trustcalc.tools.file_tool
=========================

Secure file access tool.

Provides controlled read/write access to files. All
operations are expected to be authorized by the Gateway
before execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from trustcalc.tools.base import Tool


@dataclass(slots=True)
class FileTool(Tool):
    """
    Secure file access tool.
    """

    name: str = "file"

    description: str = (
        "Read and write local files."
    )

    required_capability: str = "file.access"

    argument_schema = {
        "required": (
            "operation",
            "path",
        ),
        "properties": {
            "operation": str,
            "path": str,
            "content": str,
        },
    }

    def execute(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:

        operation = kwargs["operation"]

        path = Path(kwargs["path"])

        if operation == "read":

            return {
                "operation": "read",
                "path": str(path),
                "content": path.read_text(
                    encoding="utf-8"
                ),
            }

        if operation == "write":

            content = kwargs.get(
                "content",
                "",
            )

            path.write_text(
                content,
                encoding="utf-8",
            )

            return {
                "operation": "write",
                "path": str(path),
                "bytes": len(content),
            }

        raise ValueError(
            f"Unsupported file operation '{operation}'."
        )