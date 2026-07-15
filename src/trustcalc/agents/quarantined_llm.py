"""
trustcalc.agents.quarantined_llm
================================

Quarantined LLM.

Provides an isolated interface for interacting with an LLM.
All prompts and responses remain inside the trust boundary
until released by the runtime.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from trustcalc.core.labels import PUBLIC_LABEL
from trustcalc.runtime.taint_tracker import TaintTracker


@dataclass(slots=True)
class QuarantinedLLM:
    """
    Isolated LLM interface.

    All generated outputs are wrapped as TrustedValues
    before being returned.
    """

    taint_tracker: TaintTracker

    model_name: str = "quarantined"

    system_prompt: str = (
        "You are a secure language model."
    )

    interaction_history: list[dict[str, str]] = field(
        default_factory=list
    )

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def generate(
        self,
        prompt: str,
        **kwargs: Any,
    ):
        """
        Generate an LLM response.

        Placeholder implementation.
        """

        self.interaction_history.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        response = (
            f"Generated response for: {prompt}"
        )

        self.interaction_history.append(
            {
                "role": "assistant",
                "content": response,
            }
        )

        return self.taint_tracker.wrap(
            value=response,
            label=PUBLIC_LABEL,
            actor="quarantined_llm",
            description="LLM generation",
        )

    # ---------------------------------------------------------

    def history(self) -> list[dict[str, str]]:
        """
        Return interaction history.
        """

        return list(self.interaction_history)

    # ---------------------------------------------------------

    def clear_history(self) -> None:
        """
        Clear interaction history.
        """

        self.interaction_history.clear()

    # ---------------------------------------------------------

    def conversation_length(self) -> int:
        """
        Number of stored messages.
        """

        return len(self.interaction_history)

    # ---------------------------------------------------------

    def __len__(self) -> int:

        return self.conversation_length()