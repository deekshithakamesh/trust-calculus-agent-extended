"""
trustcalc.sidechannels.encoder
==============================

Binary encoder for covert-channel experiments.

Converts secrets into a binary representation that can be
embedded by different covert channels.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Encoder:
    """
    Encodes secrets into binary strings.
    """

    encoding: str = "utf-8"

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def encode(self, secret: str) -> str:
        """
        Encode a secret into a binary string.
        """

        data = secret.encode(self.encoding)

        return "".join(
            f"{byte:08b}"
            for byte in data
        )

    # ---------------------------------------------------------

    def encode_bytes(
        self,
        data: bytes,
    ) -> str:
        """
        Encode raw bytes into binary.
        """

        return "".join(
            f"{byte:08b}"
            for byte in data
        )

    # ---------------------------------------------------------

    def bit_length(
        self,
        secret: str,
    ) -> int:
        """
        Number of transmitted bits.
        """

        return len(
            self.encode(secret)
        )

    # ---------------------------------------------------------

    def byte_length(
        self,
        secret: str,
    ) -> int:
        """
        Number of bytes.
        """

        return len(
            secret.encode(
                self.encoding
            )
        )

    # ---------------------------------------------------------

    def supports(
        self,
        encoding: str,
    ) -> bool:
        """
        Check whether an encoding is supported.
        """

        try:
            "".encode(encoding)
            return True
        except LookupError:
            return False