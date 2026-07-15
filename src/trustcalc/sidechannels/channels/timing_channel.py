"""
trustcalc.sidechannels.channels.timing_channel
==============================================

Timing covert channel.

Represents covert information using timing intervals.
This implementation simulates timing values instead of
introducing real delays.
"""

from __future__ import annotations

from dataclasses import dataclass

from trustcalc.sidechannels.decoder import Decoder
from trustcalc.sidechannels.encoder import Encoder


@dataclass(slots=True)
class TimingChannel:
    """
    Timing covert channel.
    """

    short_interval: float = 0.1
    long_interval: float = 0.5

    encoder: Encoder = Encoder()
    decoder: Decoder = Decoder()

    # ---------------------------------------------------------
    # Encoding
    # ---------------------------------------------------------

    def encode(self, secret: str) -> list[float]:
        """
        Convert a secret into simulated timing intervals.
        """

        bits = self.encoder.encode(secret)

        return [
            self.long_interval if bit == "1"
            else self.short_interval
            for bit in bits
        ]

    # ---------------------------------------------------------
    # Extraction
    # ---------------------------------------------------------

    def extract(self, timings: list[float]) -> str:
        """
        Recover the binary string from timing intervals.
        """

        threshold = (
            self.short_interval + self.long_interval
        ) / 2.0

        return "".join(
            "1" if value >= threshold else "0"
            for value in timings
        )

    # ---------------------------------------------------------
    # Decoding
    # ---------------------------------------------------------

    def decode(
        self,
        timings: list[float],
    ) -> str:
        """
        Recover the original secret.
        """

        bits = self.extract(timings)

        return self.decoder.decode(bits)