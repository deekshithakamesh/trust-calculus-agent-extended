"""
Research-grade tests for FileTool directory sandboxing.

These tests verify that path-traversal attempts are rejected,
confining the tool to its configured base path.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from trustcalc.tools.file_tool import FileTool


@pytest.fixture
def sandbox(tmp_path: Path):
    """Create a FileTool confined to a temporary directory."""
    tool = FileTool(base_path=tmp_path)
    return tool, tmp_path


def test_read_within_sandbox(sandbox):
    tool, root = sandbox

    (root / "hello.txt").write_text("world", encoding="utf-8")

    result = tool.execute(
        operation="read",
        path="hello.txt",
    )

    assert result["content"] == "world"


def test_write_within_sandbox(sandbox):
    tool, root = sandbox

    result = tool.execute(
        operation="write",
        path="new.txt",
        content="data",
    )

    assert result["bytes"] == 4
    assert (root / "new.txt").exists()
    assert (root / "new.txt").read_text() == "data"


def test_write_creates_nested_dirs(sandbox):
    tool, root = sandbox

    result = tool.execute(
        operation="write",
        path="a/b/c.txt",
        content="x",
    )

    assert (root / "a" / "b" / "c.txt").exists()
    assert result["bytes"] == 1


def test_parent_traversal_rejected(sandbox):
    tool, root = sandbox

    with pytest.raises(ValueError, match="escapes the sandbox"):
        tool.execute(
            operation="read",
            path="../outside.txt",
        )


def test_encoded_dots_are_literal_and_safe(sandbox):
    # URL-encoded dots are treated as a literal directory inside the
    # sandbox, never decoded into a traversal. This is safe because
    # the resulting path remains confined to the base path.
    tool, root = sandbox

    result = tool.execute(
        operation="write",
        path="%2e%2e/inside.txt",
        content="ok",
    )

    assert (root / "%2e%2e" / "inside.txt").exists()


def test_absolute_path_outside_rejected(sandbox):
    tool, root = sandbox

    with tempfile.TemporaryDirectory() as outside:
        outside_file = Path(outside) / "secret.txt"
        outside_file.write_text("secret", encoding="utf-8")

        with pytest.raises(ValueError, match="escapes the sandbox"):
            tool.execute(
                operation="read",
                path=str(outside_file),
            )


def test_repeated_parent_traversal_rejected(sandbox):
    tool, root = sandbox

    with pytest.raises(ValueError, match="escapes the sandbox"):
        tool.execute(
            operation="read",
            path="../../../../etc/passwd",
        )


def test_symbolic_link_escape_rejected(sandbox):
    tool, root = sandbox

    # Create a symlink inside the sandbox pointing outside.
    with tempfile.TemporaryDirectory() as outside:
        outside_file = Path(outside) / "secret.txt"
        outside_file.write_text("secret", encoding="utf-8")

        link = root / "link.txt"
        try:
            link.symlink_to(outside_file)
        except (OSError, NotImplementedError):
            pytest.skip("symlinks not supported on this platform")

        with pytest.raises(ValueError, match="escapes the sandbox"):
            tool.execute(
                operation="read",
                path="link.txt",
            )


def test_non_string_path_rejected(sandbox):
    tool, root = sandbox

    with pytest.raises(ValueError, match="must be a string"):
        tool.execute(
            operation="read",
            path=12345,
        )


def test_unsupported_operation_rejected(sandbox):
    tool, root = sandbox

    with pytest.raises(ValueError, match="Unsupported file operation"):
        tool.execute(
            operation="delete",
            path="x.txt",
        )
