"""
Whitespace covert channel.

Encodes bits as trailing whitespace characters; provides capacity, detect, normalize utilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from trustcalc.sidechannels.decoder import Decoder
from trustcalc.sidechannels.encoder import Encoder


@dataclass(slots=True)
class WhitespaceChannel:
    zero_symbol: str = " "
    one_symbol: str = "\t"

    encoder: Encoder = field(default_factory=Encoder)
    decoder: Decoder = field(default_factory=Decoder)

    def encode(self, message: str, secret: str) -> str:
        bits = self.encoder.encode(secret)
        whitespace = "".join(self.one_symbol if bit == "1" else self.zero_symbol for bit in bits)
        return f"{message}{whitespace}"

    def extract(self, encoded_message: str) -> str:
        bits = []
        for character in reversed(encoded_message):
            if character == self.zero_symbol:
                bits.append("0")
            elif character == self.one_symbol:
                bits.append("1")
            else:
                break
        bits.reverse()
        return "".join(bits)

    def decode(self, encoded_message: str) -> str:
        bits = self.extract(encoded_message)
        return self.decoder.decode(bits)

    def capacity(self, encoded_message: Any) -> int:
        """If passed the encoded message, return number of embedded bits (trailing whitespace length). If passed a plain message, return potential capacity as number of words."""
        if isinstance(encoded_message, str):
            # count trailing whitespace bits
            bits = 0
            for ch in reversed(encoded_message):
                if ch == self.zero_symbol or ch == self.one_symbol:
                    bits += 1
                else:
                    break
            if bits > 0:
                return bits
            # else estimate by number of words
            return len(encoded_message.split())
        return 0

    def detect(self, text: str) -> bool:
        # suspicious if trailing spaces/tabs exist
        return len(text) > 0 and (text.endswith(self.zero_symbol) or text.endswith(self.one_symbol))

    def normalize(self, text: str) -> str:
        # strip trailing whitespace (simple normalization)
        return text.rstrip(' \t')
