from __future__ import annotations

from typing import Any, Dict, Optional


class ToolRegistry:
    """Simple registry for tools used by the gateway."""

    def __init__(self) -> None:
        self._tools: Dict[str, Any] = {}

    def register(self, name: str, tool: Any) -> None:
        self._tools[name] = tool

    def get(self, name: str) -> Optional[Any]:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return sorted(self._tools.keys())

    def unregister(self, name: str) -> None:
        self._tools.pop(name, None)

    def contains(self, name: str) -> bool:
        return name in self._tools

    def clear(self) -> None:
        self._tools.clear()

    def __len__(self) -> int:
        return len(self._tools)

    def __iter__(self):
        return iter(self._tools.values())