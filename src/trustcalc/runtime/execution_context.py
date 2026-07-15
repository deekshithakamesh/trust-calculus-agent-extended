from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(slots=True)
class ExecutionContext:
    """Simple execution context passed to the gateway and policy engine."""

    user_id: str | None = None
    capabilities: Any | None = None
    labels: Mapping[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
