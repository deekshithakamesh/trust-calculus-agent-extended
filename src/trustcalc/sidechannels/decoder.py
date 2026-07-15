"""
trustcalc.sidechannels.decoder
==============================

Binary decoder for covert-channel experiments.

Converts binary strings back into their original
representation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Decoder:
    """
    Decodes binary strings into text.
    """

    encoding: str = "utf-8"

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def decode(
        self,
        bits: str,
    ) -> str:
        """
        Decode a binary string.
        """

        if len(bits) % 8 != 0:
            raise ValueError(
                "Binary string length must be a multiple of 8."
            )

        data = bytes(
            int(bits[i : i + 8], 2)
            for i in range(0, len(bits), 8)
        )

        return data.decode(self.encoding)

    # ---------------------------------------------------------

    def decode_bytes(
        self,
        bits: str,
    ) -> bytes:
        """
        Decode binary into raw bytes.
        """

        if len(bits) % 8 != 0:
            raise ValueError(
                "Binary string length must be a multiple of 8."
            )

        return bytes(
            int(bits[i : i + 8], 2)
            for i in range(0, len(bits), 8)
        )

    # ---------------------------------------------------------

    def is_valid(
        self,
        bits: str,
    ) -> bool:
        """
        Validate a binary string.
        """

        if len(bits) % 8 != 0:
            return False

        return all(bit in {"0", "1"} for bit in bits)

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