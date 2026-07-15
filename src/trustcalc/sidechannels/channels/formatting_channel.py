"""
trustcalc.sidechannels.channels.formatting_channel
==================================================

Formatting covert channel.

Embeds binary information using different formatting
strategies. The implementation is intentionally modular so
new strategies can be added for experimentation.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from trustcalc.sidechannels.decoder import Decoder
from trustcalc.sidechannels.encoder import Encoder


class FormattingStrategy(str, Enum):
    """Supported formatting encodings."""

    MARKDOWN_BOLD = "markdown_bold"
    MARKDOWN_ITALIC = "markdown_italic"
    CAPITALIZATION = "capitalization"
    PUNCTUATION = "punctuation"
    ZERO_WIDTH = "zero_width"


@dataclass(slots=True)
class FormattingChannelAttack:
    """
    Formatting-based covert channel.
    """

    strategy: FormattingStrategy = (
        FormattingStrategy.MARKDOWN_BOLD
    )

    encoder: Encoder = Encoder()

    decoder: Decoder = Decoder()

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def encode(
        self,
        secret: str,
        message: str,
    ) -> str:
        """
        Embed a secret inside formatted text.
        """

        bits = self.encoder.encode(secret)

        words = message.split()

        if not words:
            return message

        encoded: list[str] = []

        for index, word in enumerate(words):

            bit = bits[index] if index < len(bits) else "0"

            encoded.append(
                self._encode_word(
                    word,
                    bit,
                )
            )

        return " ".join(encoded)

    # ---------------------------------------------------------

    def extract(
        self,
        encoded_message: str,
    ) -> str:
        """
        Recover the embedded binary string.
        """

        bits: list[str] = []

        for word in encoded_message.split():

            bits.append(
                self._extract_bit(word)
            )

        return "".join(bits)

    # ---------------------------------------------------------

    def decode(
        self,
        encoded_message: str,
    ) -> str:
        """
        Recover the original secret.
        """

        bits = self.extract(encoded_message)

        usable = len(bits) - (len(bits) % 8)

        return self.decoder.decode(bits[:usable])

    # ---------------------------------------------------------

    def capacity(
        self,
        message: str,
    ) -> int:
        """
        Maximum embeddable bits.
        """

        return len(message.split())

    # ---------------------------------------------------------

    def detect(
        self,
        message: str,
    ) -> bool:
        """
        Detect possible formatting manipulation.
        """

        if "**" in message:
            return True

        if "*" in message:
            return True

        if "\u200b" in message:
            return True

        return False

    # ---------------------------------------------------------

    def normalize(
        self,
        message: str,
    ) -> str:
        """
        Remove formatting artifacts.
        """

        return (
            message.replace("**", "")
            .replace("*", "")
            .replace("\u200b", "")
        )

    # ---------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------

    def _encode_word(
        self,
        word: str,
        bit: str,
    ) -> str:

        if self.strategy == FormattingStrategy.MARKDOWN_BOLD:

            return (
                f"**{word}**"
                if bit == "1"
                else word
            )

        if self.strategy == FormattingStrategy.MARKDOWN_ITALIC:

            return (
                f"*{word}*"
                if bit == "1"
                else word
            )

        if self.strategy == FormattingStrategy.CAPITALIZATION:

            return (
                word.upper()
                if bit == "1"
                else word.lower()
            )

        if self.strategy == FormattingStrategy.PUNCTUATION:

            return (
                word + "!"
                if bit == "1"
                else word + "."
            )

        if self.strategy == FormattingStrategy.ZERO_WIDTH:

            return (
                word + "\u200b"
                if bit == "1"
                else word
            )

        return word

    # ---------------------------------------------------------

    def _extract_bit(
        self,
        word: str,
    ) -> str:

        if self.strategy == FormattingStrategy.MARKDOWN_BOLD:

            return (
                "1"
                if word.startswith("**")
                and word.endswith("**")
                else "0"
            )

        if self.strategy == FormattingStrategy.MARKDOWN_ITALIC:

            return (
                "1"
                if word.startswith("*")
                and word.endswith("*")
                else "0"
            )

        if self.strategy == FormattingStrategy.CAPITALIZATION:

            return (
                "1"
                if word.isupper()
                else "0"
            )

        if self.strategy == FormattingStrategy.PUNCTUATION:

            return (
                "1"
                if word.endswith("!")
                else "0"
            )

        if self.strategy == FormattingStrategy.ZERO_WIDTH:

            return (
                "1"
                if word.endswith("\u200b")
                else "0"
            )

        return "0"