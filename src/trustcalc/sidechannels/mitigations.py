"""
trustcalc.sidechannels.mitigations
==================================

Covert-channel mitigation framework.

Provides configurable defenses against formatting,
whitespace, timing, and other covert channels.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from trustcalc.sidechannels.canonicalizer import Canonicalizer


@dataclass(slots=True)
class NoiseInjectionMitigation:
    """
    Generic covert-channel mitigation framework.
    """

    level: float = 0.25

    canonicalizer: Canonicalizer = field(
        default_factory=Canonicalizer
    )

    randomize_case: bool = False

    randomize_punctuation: bool = False

    normalize_output: bool = True

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def apply(
        self,
        message: str,
    ) -> str:
        """
        Apply all enabled mitigations.
        """

        text = message

        if self.normalize_output:
            text = self.canonicalizer.normalize(text)

        if self.randomize_case:
            text = self._randomize_case(text)

        if self.randomize_punctuation:
            text = self._randomize_punctuation(text)

        if self.level > 0:
            text = self._inject_noise(text)

        return text

    # ---------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------

    def _inject_noise(
        self,
        text: str,
    ) -> str:
        """
        Simulate noise injection.

        The implementation intentionally keeps semantic
        content unchanged while perturbing the output.
        """

        if random.random() > self.level:
            return text

        return f"{text}."

    # ---------------------------------------------------------

    def _randomize_case(
        self,
        text: str,
    ) -> str:

        characters = []

        for character in text:

            if character.isalpha():

                if random.random() < 0.5:
                    character = character.upper()
                else:
                    character = character.lower()

            characters.append(character)

        return "".join(characters)

    # ---------------------------------------------------------

    def _randomize_punctuation(
        self,
        text: str,
    ) -> str:

        replacements = {
            ".": random.choice([".", "!"]),
            "!": random.choice(["!", "."]),
            "?": random.choice(["?", "."]),
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text

    # ---------------------------------------------------------

    def effectiveness(
        self,
        before: float,
        after: float,
    ) -> float:
        """
        Estimate mitigation effectiveness.
        """

        if before <= 0:
            return 0.0

        return (before - after) / before