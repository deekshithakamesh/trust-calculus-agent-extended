"""
trustcalc.evaluation.experiment
===============================

Experiment definition.

Represents a single evaluation experiment for the
Trust Calculus framework.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Experiment:
    """
    A single evaluation experiment.
    """

    name: str

    attack: str

    description: str = ""

    transmitted_bits: int = 0

    recovered_bits: int = 0

    duration_seconds: float = 0.0

    mitigation_before: float = 0.0

    mitigation_after: float = 0.0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    def validate(self) -> bool:
        """
        Validate experiment configuration.
        """

        return (
            self.transmitted_bits >= 0
            and self.recovered_bits >= 0
            and self.duration_seconds >= 0
        )

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Convert experiment to a dictionary compatible
        with EvaluationRunner.
        """

        return {
            "attack_name": self.attack,
            "transmitted_bits": self.transmitted_bits,
            "recovered_bits": self.recovered_bits,
            "duration_seconds": self.duration_seconds,
            "mitigation_before": self.mitigation_before,
            "mitigation_after": self.mitigation_after,
        }

    # ---------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Experiment":
        """
        Construct an Experiment from a dictionary.
        """

        return cls(
            name=data.get("name", ""),
            attack=data.get("attack_name", ""),
            description=data.get("description", ""),
            transmitted_bits=data.get(
                "transmitted_bits",
                0,
            ),
            recovered_bits=data.get(
                "recovered_bits",
                0,
            ),
            duration_seconds=data.get(
                "duration_seconds",
                0.0,
            ),
            mitigation_before=data.get(
                "mitigation_before",
                0.0,
            ),
            mitigation_after=data.get(
                "mitigation_after",
                0.0,
            ),
            metadata=data.get(
                "metadata",
                {},
            ),
        )

    # ---------------------------------------------------------

    @property
    def leakage(self) -> float:
        """
        Fraction of recovered bits.
        """

        if self.transmitted_bits == 0:
            return 0.0

        return (
            self.recovered_bits
            / self.transmitted_bits
        )

    # ---------------------------------------------------------

    @property
    def success(self) -> bool:
        """
        Whether any information was recovered.
        """

        return self.recovered_bits > 0