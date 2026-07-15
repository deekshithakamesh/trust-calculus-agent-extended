from __future__ import annotations

from .labels import Label


class FlowRules:
    """Simple flow constraints for label propagation."""

    def can_flow(self, source: Label, target: Label) -> bool:
        order = {"public": 0, "secret": 1}
        return order[source.confidentiality] <= order[target.confidentiality]
