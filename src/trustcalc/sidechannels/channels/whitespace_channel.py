"""
trustcalc.sidechannels.channels.whitespace_channel
==================================================

Whitespace covert channel.

Embeds binary data using spaces and tabs.

Encoding
--------
0 -> space
1 -> tab
"""

from __future__ import annotations

from dataclasses import dataclass, field

from trustcalc.sidechannels.decoder import Decoder
from trustcalc.sidechannels.encoder import Encoder


@dataclass(slots=True)
class WhitespaceChannel:
    """
    Whitespace covert channel.
    """

    zero_symbol: str = " "

    one_symbol: str = "\t"

    encoder: Encoder = field(default_factory=Encoder)

    decoder: Decoder = field(default_factory=Decoder)

    # ---------------------------------------------------------
    # Encoding
    # ---------------------------------------------------------

    def encode(
        self,
        secret: str,
        message: str,
    ) -> str:
        """
        Embed a secret inside trailing whitespace.
        """

        bits = self.encoder.encode(secret)

        whitespace = "".join(
            self.one_symbol if bit == "1"
            else self.zero_symbol
            for bit in bits
        )

        return f"{message}{whitespace}"

    # ---------------------------------------------------------
    # Extraction
    # ---------------------------------------------------------

    def extract(
        self,
        encoded_message: str,
    ) -> str:
        """
        Recover the embedded binary string.
        """

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

    # ---------------------------------------------------------
    # Decoding
    # ---------------------------------------------------------

    def decode(
        self,
        encoded_message: str,
    ) -> str:
        """
        Recover the original secret.
        """

        bits = self.extract(
            encoded_message
        )

        return self.decoder.decode(bits)