"""
trustcalc.sidechannels.canonicalizer
====================================

Canonicalization utilities.

Removes formatting variations that may be used as covert
communication channels while preserving semantic content.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


@dataclass(slots=True)
class Canonicalizer:
    """
    Normalize text to a canonical representation.
    """

    collapse_whitespace: bool = True

    normalize_case: bool = False

    strip_markdown: bool = True

    strip_zero_width: bool = True

    normalize_punctuation: bool = True

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def normalize(
        self,
        message: str,
    ) -> str:
        """
        Canonicalize a message.
        """

        text = unicodedata.normalize(
            "NFKC",
            message,
        )

        if self.strip_zero_width:
            text = self._remove_zero_width(text)

        if self.strip_markdown:
            text = self._remove_markdown(text)

        if self.normalize_punctuation:
            text = self._normalize_punctuation(text)

        if self.collapse_whitespace:
            text = self._collapse_whitespace(text)

        if self.normalize_case:
            text = text.lower()

        return text.strip()

    # ---------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------

    def _remove_zero_width(
        self,
        text: str,
    ) -> str:

        zero_width = (
            "\u200b",
            "\u200c",
            "\u200d",
            "\ufeff",
        )

        for character in zero_width:
            text = text.replace(character, "")

        return text

    # ---------------------------------------------------------

    def _remove_markdown(
        self,
        text: str,
    ) -> str:

        patterns = (
            r"\*\*(.*?)\*\*",
            r"\*(.*?)\*",
            r"__(.*?)__",
            r"_(.*?)_",
            r"`(.*?)`",
        )

        for pattern in patterns:

            text = re.sub(
                pattern,
                r"\1",
                text,
            )

        return text

    # ---------------------------------------------------------

    def _normalize_punctuation(
        self,
        text: str,
    ) -> str:

        text = re.sub(
            r"[!?]+",
            ".",
            text,
        )

        text = re.sub(
            r"\.{2,}",
            ".",
            text,
        )

        return text

    # ---------------------------------------------------------

    def _collapse_whitespace(
        self,
        text: str,
    ) -> str:

        return re.sub(
            r"\s+",
            " ",
            text,
        )