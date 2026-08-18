"""
Timing covert channel (updated to accept either secret or (carrier, secret)).
Simulates timing intervals rather than real delays.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Any

from trustcalc.sidechannels.decoder import Decoder
from trustcalc.sidechannels.encoder import Encoder


@dataclass(slots=True)
class TimingChannel:
    short_interval: float = 0.1
    long_interval: float = 0.5

    encoder: Encoder = field(default_factory=Encoder)
    decoder: Decoder = field(default_factory=Decoder)

    def encode(self, *args: Any) -> List[float]:
        """
        Accept either encode(secret) or encode(carrier, secret).
        Returns a list of simulated timing intervals representing bits.
        """
        if len(args) == 1:
            secret = args[0]
        elif len(args) >= 2:
            # ignore carrier
            secret = args[1]
        else:
            raise TypeError("encode requires at least a secret")

        bits = self.encoder.encode(secret)
        return [self.long_interval if bit == "1" else self.short_interval for bit in bits]

    def extract(self, timings: List[float]) -> str:
        threshold = (self.short_interval + self.long_interval) / 2.0
        return "".join("1" if value >= threshold else "0" for value in timings)

    def decode(self, timings: List[float]) -> str:
        bits = self.extract(timings)
        return self.decoder.decode(bits)

    def capacity(self, timings_or_message: Any) -> int:
        """If passed timings (list), return number of bits; if passed a message string, estimate capacity as number of words."""
        if isinstance(timings_or_message, (list, tuple)):
            return len(timings_or_message)
        if isinstance(timings_or_message, str):
            return len(timings_or_message.split())
        return 0

    def detect(self, text: str) -> bool:
        # No real side-effect detection for timing; return False by default
        return False

    def normalize(self, text: str) -> str:
        return text
