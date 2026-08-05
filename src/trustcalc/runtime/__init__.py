"""
trustcalc.runtime
=================

Runtime execution components.

This package intentionally uses lazy attribute resolution
(PEP 562) for cross-package imports to avoid the circular
dependency between ``trustcalc.runtime`` and
``trustcalc.gateway``:

    gateway.enforcement imports runtime.execution_context
    runtime.__init__      imports gateway.ToolGateway

By deferring the gateway import until attribute access, the
package graph remains clean and import order independent.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "ToolGateway",
    "Interpreter",
    "Mediator",
    "TaintTracker",
]


def __getattr__(name: str) -> Any:
    """
    Lazily resolve package-level exports.

    This avoids importing ``trustcalc.gateway`` at module load
    time, breaking the circular dependency between the runtime
    and gateway packages.
    """

    if name == "ToolGateway":
        from trustcalc.gateway.gateway import ToolGateway

        return ToolGateway

    if name == "Interpreter":
        from trustcalc.runtime.interpreter import Interpreter

        return Interpreter

    if name == "Mediator":
        from trustcalc.runtime.mediator import Mediator

        return Mediator

    if name == "TaintTracker":
        from trustcalc.runtime.taint_tracker import TaintTracker

        return TaintTracker

    raise AttributeError(
        f"module {__name__!r} has no attribute {name!r}"
    )
