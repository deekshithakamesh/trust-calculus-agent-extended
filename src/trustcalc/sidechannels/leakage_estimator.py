"""
trustcalc.sidechannels.leakage_estimator
========================================

Leakage estimation utilities.

Provides quantitative measurements for covert-channel
capacity and mitigation effectiveness.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class LeakageEstimator:
    """
    Estimate covert-channel leakage.
    """

    # ---------------------------------------------------------
    # Bit Leakage
    # ---------------------------------------------------------

    def bit_leakage(
        self,
        transmitted_bits: int,
        recovered_bits: int,
    ) -> float:
        """
        Fraction of transmitted bits successfully recovered.
        """

        if transmitted_bits <= 0:
            return 0.0

        return recovered_bits / transmitted_bits

    # ---------------------------------------------------------
    # Error Rate
    # ---------------------------------------------------------

    def bit_error_rate(
        self,
        transmitted_bits: int,
        recovered_bits: int,
    ) -> float:
        """
        Fraction of bits lost.
        """

        if transmitted_bits <= 0:
            return 0.0

        return (
            transmitted_bits - recovered_bits
        ) / transmitted_bits

    # ---------------------------------------------------------
    # Mitigation Effectiveness
    # ---------------------------------------------------------

    def mitigation_effectiveness(
        self,
        before: float,
        after: float,
    ) -> float:
        """
        Percentage reduction in leakage.
        """

        if before <= 0:
            return 0.0

        reduction = before - after

        return reduction / before

    # ---------------------------------------------------------
    # Capacity
    # ---------------------------------------------------------

    def channel_capacity(
        self,
        transmitted_bits: int,
        duration_seconds: float,
    ) -> float:
        """
        Estimate bits transmitted per second.
        """

        if duration_seconds <= 0:
            return 0.0

        return (
            transmitted_bits /
            duration_seconds
        )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    def summarize(
        self,
        transmitted_bits: int,
        recovered_bits: int,
        duration_seconds: float,
    ) -> dict[str, float]:
        """
        Produce a summary of leakage statistics.
        """

        leakage = self.bit_leakage(
            transmitted_bits,
            recovered_bits,
        )

        return {
            "bit_leakage": leakage,
            "bit_error_rate": self.bit_error_rate(
                transmitted_bits,
                recovered_bits,
            ),
            "channel_capacity": self.channel_capacity(
                transmitted_bits,
                duration_seconds,
            ),
        }