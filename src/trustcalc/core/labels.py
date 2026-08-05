"""
trustcalc.core.labels
=====================

Core security label definitions for the Trust Calculus runtime.

This module intentionally contains only immutable data structures.
The lattice algorithms (join, meet, dominance, flow checking) are
implemented in trustcalc.core.lattice.

Architecture
------------

SecurityLabel
    ├── Integrity
    ├── Confidentiality
    ├── Compartments
    ├── Provenance ID
    └── Metadata

This separation keeps labels as pure data while allowing the runtime
and policy engine to implement the trust calculus independently.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from enum import IntEnum
from typing import TYPE_CHECKING, Any, FrozenSet, Mapping, Optional

if TYPE_CHECKING:
    from trustcalc.core.lattice import flows_to as _flows_to_impl


# ============================================================================
# Integrity Lattice
# ============================================================================


class Integrity(IntEnum):
    """
    Integrity labels.

    Higher values indicate greater trustworthiness.

        VERIFIED
            ▲
          HIGH
            ▲
         MEDIUM
            ▲
           LOW
            ▲
       UNTRUSTED
    """

    UNTRUSTED = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERIFIED = 4

    @property
    def trusted(self) -> bool:
        """Return True if the integrity is HIGH or VERIFIED."""
        return self >= Integrity.HIGH

    @property
    def verified(self) -> bool:
        """Return True if integrity is VERIFIED."""
        return self == Integrity.VERIFIED


# ============================================================================
# Confidentiality Lattice
# ============================================================================


class Confidentiality(IntEnum):
    """
    Confidentiality labels.

    Higher values indicate more sensitive information.

        TOP_SECRET
             ▲
           SECRET
             ▲
       CONFIDENTIAL
             ▲
          INTERNAL
             ▲
           PUBLIC
    """

    PUBLIC = 0
    INTERNAL = 1
    CONFIDENTIAL = 2
    SECRET = 3
    TOP_SECRET = 4

    @property
    def public(self) -> bool:
        return self == Confidentiality.PUBLIC

    @property
    def secret(self) -> bool:
        return self >= Confidentiality.SECRET


# ============================================================================
# Security Label
# ============================================================================


@dataclass(frozen=True, slots=True)
class SecurityLabel:
    """
    Immutable security label.

    Notes
    -----
    A SecurityLabel describes the *information* carried by a value.

    It does NOT describe:

        • user identity
        • capabilities
        • permissions
        • tool access

    Those belong to the execution context and policy engine.

    Parameters
    ----------
    integrity
        Trust level of the information.

    confidentiality
        Sensitivity level.

    compartments
        Information compartments (finance, hr, legal, ...).

    provenance_id
        UUID of the provenance node.

    metadata
        Optional implementation-specific metadata.
    """

    integrity: Integrity = Integrity.UNTRUSTED

    confidentiality: Confidentiality = Confidentiality.PUBLIC

    compartments: FrozenSet[str] = field(default_factory=frozenset)

    provenance_id: Optional[str] = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Normalize immutable fields.
        """

        object.__setattr__(
            self,
            "compartments",
            frozenset(self.compartments),
        )

        object.__setattr__(
            self,
            "metadata",
            dict(self.metadata),
        )

    # ---------------------------------------------------------------------
    # Convenience Properties
    # ---------------------------------------------------------------------

    @property
    def is_public(self) -> bool:
        return self.confidentiality.public

    @property
    def is_secret(self) -> bool:
        return self.confidentiality.secret

    @property
    def is_trusted(self) -> bool:
        return self.integrity.trusted

    @property
    def is_verified(self) -> bool:
        return self.integrity.verified

    # ---------------------------------------------------------------------
    # Immutable Update Helpers
    # ---------------------------------------------------------------------

    def with_integrity(
        self,
        integrity: Integrity,
    ) -> "SecurityLabel":
        """
        Return a copy with updated integrity.
        """
        return replace(
            self,
            integrity=integrity,
        )

    def with_confidentiality(
        self,
        confidentiality: Confidentiality,
    ) -> "SecurityLabel":
        """
        Return a copy with updated confidentiality.
        """
        return replace(
            self,
            confidentiality=confidentiality,
        )

    def with_compartment(
        self,
        compartment: str,
    ) -> "SecurityLabel":
        """
        Return a copy with one additional compartment.
        """
        return replace(
            self,
            compartments=self.compartments | {compartment},
        )

    def without_compartment(
        self,
        compartment: str,
    ) -> "SecurityLabel":
        """
        Return a copy with one compartment removed.
        """
        return replace(
            self,
            compartments=self.compartments - {compartment},
        )

    def with_provenance(
        self,
        provenance_id: str,
    ) -> "SecurityLabel":
        """
        Attach a provenance identifier.
        """
        return replace(
            self,
            provenance_id=provenance_id,
        )

    def with_metadata(
        self,
        **metadata: Any,
    ) -> "SecurityLabel":
        """
        Return a copy with merged metadata.
        """
        updated = dict(self.metadata)
        updated.update(metadata)

        return replace(
            self,
            metadata=updated,
        )

    # ---------------------------------------------------------------------
    # Information Flow
    # ---------------------------------------------------------------------

    def can_flow_to(
        self,
        destination: "SecurityLabel",
    ) -> bool:
        """
        Determine whether information carrying this label may legally
        flow into a value carrying *destination*.

        This is a thin convenience wrapper over the lattice
        ``flows_to`` relation (Bell-LaPadula + Biba + compartments).

        The implementation imports lazily to avoid a circular import
        between ``labels`` and ``lattice`` at module load time.
        """
        from trustcalc.core.lattice import flows_to

        return flows_to(self, destination)

    # ---------------------------------------------------------------------
    # Factory Constructors
    # ---------------------------------------------------------------------

    @classmethod
    def public(cls) -> "SecurityLabel":
        """
        Trusted public information.
        """
        return cls(
            integrity=Integrity.HIGH,
            confidentiality=Confidentiality.PUBLIC,
        )

    @classmethod
    def internal(cls) -> "SecurityLabel":
        """
        Trusted internal information.
        """
        return cls(
            integrity=Integrity.HIGH,
            confidentiality=Confidentiality.INTERNAL,
        )

    @classmethod
    def confidential(cls) -> "SecurityLabel":
        """
        Trusted confidential information.
        """
        return cls(
            integrity=Integrity.HIGH,
            confidentiality=Confidentiality.CONFIDENTIAL,
        )

    @classmethod
    def secret(cls) -> "SecurityLabel":
        """
        Trusted secret information.
        """
        return cls(
            integrity=Integrity.HIGH,
            confidentiality=Confidentiality.SECRET,
        )

    @classmethod
    def top_secret(cls) -> "SecurityLabel":
        """
        Verified top-secret information.
        """
        return cls(
            integrity=Integrity.VERIFIED,
            confidentiality=Confidentiality.TOP_SECRET,
        )

    @classmethod
    def untrusted(cls) -> "SecurityLabel":
        """
        Completely untrusted public information.
        """
        return cls(
            integrity=Integrity.UNTRUSTED,
            confidentiality=Confidentiality.PUBLIC,
        )

    # ---------------------------------------------------------------------
    # Validation
    # ---------------------------------------------------------------------

    def validate(self) -> None:
        """
        Validate the label.

        Raises
        ------
        ValueError
            If the label contains invalid values.
        """

        if not isinstance(self.integrity, Integrity):
            raise ValueError(f"Invalid integrity: {self.integrity}")

        if not isinstance(
            self.confidentiality,
            Confidentiality,
        ):
            raise ValueError(f"Invalid confidentiality: " f"{self.confidentiality}")

        if not isinstance(
            self.compartments,
            frozenset,
        ):
            raise ValueError("Compartments must be a frozenset.")

        if self.provenance_id is not None and not isinstance(
            self.provenance_id,
            str,
        ):
            raise ValueError("Provenance ID must be a string.")

    # ---------------------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Convert label into a JSON-serializable dictionary.
        """

        return {
            "integrity": self.integrity.name,
            "confidentiality": self.confidentiality.name,
            "compartments": sorted(self.compartments),
            "provenance_id": self.provenance_id,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "SecurityLabel":
        """
        Construct a SecurityLabel from a dictionary.
        """

        return cls(
            integrity=Integrity[data["integrity"]],
            confidentiality=Confidentiality[data["confidentiality"]],
            compartments=frozenset(
                data.get(
                    "compartments",
                    [],
                )
            ),
            provenance_id=data.get("provenance_id"),
            metadata=data.get(
                "metadata",
                {},
            ),
        )

    # ---------------------------------------------------------------------

    def to_json(
        self,
        *,
        indent: int = 2,
    ) -> str:
        """
        Serialize to JSON.
        """

        return json.dumps(
            self.to_dict(),
            indent=indent,
            sort_keys=True,
        )

    @classmethod
    def from_json(
        cls,
        value: str,
    ) -> "SecurityLabel":
        """
        Deserialize from JSON.
        """

        return cls.from_dict(json.loads(value))

    # ---------------------------------------------------------------------
    # Utility Methods
    # ---------------------------------------------------------------------

    def copy(self) -> "SecurityLabel":
        """
        Explicit immutable copy.
        """
        return replace(self)

    def clear_metadata(self) -> "SecurityLabel":
        """
        Return a copy without metadata.
        """
        return replace(
            self,
            metadata={},
        )

    def clear_provenance(self) -> "SecurityLabel":
        """
        Return a copy without provenance.
        """
        return replace(
            self,
            provenance_id=None,
        )

    # ---------------------------------------------------------------------
    # String Representation
    # ---------------------------------------------------------------------

    def __str__(self) -> str:
        compartments = (
            ", ".join(sorted(self.compartments)) if self.compartments else "-"
        )

        return (
            "SecurityLabel("
            f"integrity={self.integrity.name}, "
            f"confidentiality={self.confidentiality.name}, "
            f"compartments=[{compartments}]"
            ")"
        )

    def __repr__(self) -> str:
        return self.__str__()

    # ============================================================================


# Module Constants
# ============================================================================

PUBLIC_LABEL = SecurityLabel.public()

INTERNAL_LABEL = SecurityLabel.internal()

CONFIDENTIAL_LABEL = SecurityLabel.confidential()

SECRET_LABEL = SecurityLabel.secret()

TOP_SECRET_LABEL = SecurityLabel.top_secret()

UNTRUSTED_LABEL = SecurityLabel.untrusted()

# Compatibility alias for the older simple label API used by some modules.
Label = SecurityLabel


# ============================================================================
# Helper Functions
# ============================================================================


def is_public(label: SecurityLabel) -> bool:
    """
    Return True if the label is public.
    """
    return label.confidentiality is Confidentiality.PUBLIC


def is_secret(label: SecurityLabel) -> bool:
    """
    Return True if the label represents secret information.
    """
    return label.confidentiality >= Confidentiality.SECRET


def is_untrusted(label: SecurityLabel) -> bool:
    """
    Return True if the integrity is UNTRUSTED.
    """
    return label.integrity is Integrity.UNTRUSTED


def is_verified(label: SecurityLabel) -> bool:
    """
    Return True if the label is cryptographically or administratively
    verified.
    """
    return label.integrity is Integrity.VERIFIED


def has_compartment(
    label: SecurityLabel,
    compartment: str,
) -> bool:
    """
    Check whether a label belongs to a compartment.
    """
    return compartment in label.compartments


# ============================================================================
# Convenience Constructors
# ============================================================================


def make_public(**metadata: Any) -> SecurityLabel:
    """
    Construct a trusted public label.
    """
    return PUBLIC_LABEL.with_metadata(**metadata)


def make_secret(**metadata: Any) -> SecurityLabel:
    """
    Construct a trusted secret label.
    """
    return SECRET_LABEL.with_metadata(**metadata)


def make_untrusted(**metadata: Any) -> SecurityLabel:
    """
    Construct an untrusted label.
    """
    return UNTRUSTED_LABEL.with_metadata(**metadata)


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "Integrity",
    "Confidentiality",
    "SecurityLabel",
    "PUBLIC_LABEL",
    "INTERNAL_LABEL",
    "CONFIDENTIAL_LABEL",
    "SECRET_LABEL",
    "TOP_SECRET_LABEL",
    "UNTRUSTED_LABEL",
    "is_public",
    "is_secret",
    "is_untrusted",
    "is_verified",
    "has_compartment",
    "make_public",
    "make_secret",
    "make_untrusted",
]
