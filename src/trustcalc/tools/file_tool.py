"""
trustcalc.tools.file_tool
=========================

Secure file access tool.

Provides controlled read/write access to files. All
operations are expected to be authorized by the Gateway
before execution.

The tool enforces a directory sandbox: every requested path
is resolved against a configured ``base_path`` and rejected
if it escapes the sandbox (path-traversal protection).
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

    Parameters
    ----------
    base_path
        Root directory that all file operations are confined to.
        Defaults to the current working directory.
    """

    name: str = "file"

    description: str = (
        "Read and write local files."
    )

    required_capability: str = "file.access"

    base_path: Path = Path.cwd()

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

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def execute(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:

        operation = kwargs["operation"]

        raw_path = kwargs["path"]

        target = self._resolve_path(raw_path)

        if operation == "read":

            return {
                "operation": "read",
                "path": str(target),
                "content": target.read_text(
                    encoding="utf-8"
                ),
            }

        if operation == "write":

            content = kwargs.get(
                "content",
                "",
            )

            # Ensure the parent directory exists while remaining
            # inside the sandbox (the resolved target is already
            # verified to be confined to the base path).
            target.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            target.write_text(
                content,
                encoding="utf-8",
            )

            return {
                "operation": "write",
                "path": str(target),
                "bytes": len(content),
            }

        raise ValueError(
            f"Unsupported file operation '{operation}'."
        )

    # ---------------------------------------------------------
    # Path Safety
    # ---------------------------------------------------------

    def _resolve_path(
        self,
        raw_path: str,
    ) -> Path:
        """
        Resolve a requested path and enforce the sandbox.

        Raises
        ------
        ValueError
            If the path is not a string, or escapes the sandbox.
        """

        if not isinstance(raw_path, str):
            raise ValueError(
                "File path must be a string."
            )

        root = self.base_path.expanduser().resolve()

        if not root.exists():
            root.mkdir(parents=True, exist_ok=True)

        # Always resolve relative to the sandbox root so that
        # relative paths are interpreted inside the sandbox.
        candidate = (
            root
            / Path(raw_path).expanduser()
        ).resolve()

        # Reject absolute paths that escape the sandbox. The
        # absolute path is first joined to root, so a fully
        # absolute raw_path will be rejected by is_relative_to.
        if not candidate.is_relative_to(root):
            raise ValueError(
                f"Path '{raw_path}' escapes the sandbox '{root}'."
            )

        return candidate

    # ---------------------------------------------------------

    def _is_within(
        self,
        candidate: Path,
        root: Path,
    ) -> bool:
        """
        Return True if ``candidate`` is inside ``root``.
        """

        try:
            candidate.relative_to(root)
            return True
        except ValueError:
            return False
