"""
trustcalc.sidechannels.channels.synonym_channel
================================================

Synonym substitution covert channel.

Encodes information by selecting deterministic synonym
variants in a carrier text.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class SynonymChannel:
    """
    Deterministic synonym-based covert channel.

    Each synonym pair represents one binary choice:

        option 0 -> first synonym
        option 1 -> second synonym

    The implementation is intentionally deterministic so that
    encoding and decoding remain reproducible during evaluation.
    """

    synonyms: dict[str, tuple[str, str]] = field(
        default_factory=lambda: {
            "quick": ("quick", "fast"),
            "big": ("big", "large"),
            "small": ("small", "tiny"),
            "start": ("start", "begin"),
            "end": ("end", "finish"),
            "help": ("help", "assist"),
            "show": ("show", "display"),
            "make": ("make", "create"),
        }
    )

    def encode(
        self,
        carrier: str,
        secret: str,
    ) -> str:
        """
        Encode a secret into a carrier string.

        The secret is converted to a bit stream. Each eligible
        synonym occurrence provides one binary encoding position.
        """

        if not carrier:
            return carrier

        bits = self._to_bits(secret)

        if not bits:
            return carrier

        words = carrier.split()
        bit_index = 0

        for index, word in enumerate(words):
            normalized = word.lower().strip(".,!?;:")

            pair = self.synonyms.get(normalized)

            if pair is None:
                continue

            if bit_index >= len(bits):
                break

            replacement = pair[int(bits[bit_index])]

            # Preserve simple punctuation.
            punctuation = word[len(word.rstrip(".,!?;:")):]

            words[index] = replacement + punctuation
            bit_index += 1

        return " ".join(words)

    def decode(self, encoded: str) -> str:
        """
        Decode the binary payload represented by synonym choices.
        """

        bits: list[str] = []

        for word in encoded.split():
            normalized = word.lower().strip(".,!?;:")

            for first, second in self.synonyms.values():
                if normalized == first:
                    bits.append("0")
                    break

                if normalized == second:
                    bits.append("1")
                    break

        return self._from_bits("".join(bits))

    def detect(self, text: str) -> bool:
        """
        Detect whether synonym-channel substitutions are present.
        """

        for word in text.split():
            normalized = word.lower().strip(".,!?;:")

            for first, second in self.synonyms.values():
                if normalized == second:
                    return True

        return False

    def normalize(self, text: str) -> str:
        """
        Normalize synonym variants to their canonical forms.
        """

        words = text.split()

        canonical: dict[str, str] = {}

        for first, second in self.synonyms.values():
            canonical[second] = first

        normalized_words: list[str] = []

        for word in words:
            punctuation = word[len(word.rstrip(".,!?;:")):]
            token = word.rstrip(".,!?;:").lower()

            replacement = canonical.get(token, token)

            normalized_words.append(
                replacement + punctuation
            )

        return " ".join(normalized_words)

    def capacity(self, text: str) -> int:
        """
        Return the number of binary encoding positions in text.
        """

        count = 0

        for word in text.split():
            normalized = word.lower().strip(".,!?;:")

            if normalized in self.synonyms:
                count += 1

        return count

    @staticmethod
    def _to_bits(secret: str) -> str:
        """
        Convert text into an 8-bit binary representation.
        """

        return "".join(
            f"{byte:08b}"
            for byte in secret.encode("utf-8")
        )

    @staticmethod
    def _from_bits(bits: str) -> str:
        """
        Convert complete 8-bit groups back into UTF-8 text.
        """

        usable_length = len(bits) - (len(bits) % 8)

        if usable_length == 0:
            return ""

        data = bytes(
            int(bits[index:index + 8], 2)
            for index in range(0, usable_length, 8)
        )

        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return ""
