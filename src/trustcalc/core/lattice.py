"""
trustcalc.core.lattice
======================

Formal lattice operations for the Trust Calculus runtime.

This module implements the mathematical semantics of the trust calculus.

SecurityLabel itself is immutable data.

All lattice algorithms live here.

Implements

    join (⊔)

    meet (⊓)

    dominates (⊒)

    flows_to (→)

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import replace

from trustcalc.core.labels import (
    Confidentiality,
    Integrity,
    SecurityLabel,
)

# ================================================================
# Integrity Operations (Biba)
# ================================================================


def integrity_join(
    left: Integrity,
    right: Integrity,
) -> Integrity:
    """
    Least trusted dominates.

    HIGH ⊔ LOW = LOW
    """
    return min(left, right)


def integrity_meet(
    left: Integrity,
    right: Integrity,
) -> Integrity:
    """
    Greatest lower bound.
    """
    return max(left, right)


# ================================================================
# Confidentiality Operations (Bell-LaPadula)
# ================================================================


def confidentiality_join(
    left: Confidentiality,
    right: Confidentiality,
) -> Confidentiality:
    """
    Most restrictive dominates.

    PUBLIC ⊔ SECRET = SECRET
    """
    return max(left, right)


def confidentiality_meet(
    left: Confidentiality,
    right: Confidentiality,
) -> Confidentiality:
    """
    Least restrictive label.
    """
    return min(left, right)


# ================================================================
# Label Join
# ================================================================


def join(
    left: SecurityLabel,
    right: SecurityLabel,
) -> SecurityLabel:
    """
    Compute the least upper bound of two labels.

    Rules

    Integrity
        minimum

    Confidentiality
        maximum

    Compartments
        union

    Metadata
        merged

    Provenance
        removed
    """

    return SecurityLabel(
        integrity=integrity_join(
            left.integrity,
            right.integrity,
        ),
        confidentiality=confidentiality_join(
            left.confidentiality,
            right.confidentiality,
        ),
        compartments=left.compartments | right.compartments,
        provenance_id=None,
        metadata={
            **left.metadata,
            **right.metadata,
        },
    )


# ================================================================
# Label Meet
# ================================================================


def meet(
    left: SecurityLabel,
    right: SecurityLabel,
) -> SecurityLabel:
    """
    Greatest lower bound.
    """

    return SecurityLabel(
        integrity=integrity_meet(
            left.integrity,
            right.integrity,
        ),
        confidentiality=confidentiality_meet(
            left.confidentiality,
            right.confidentiality,
        ),
        compartments=left.compartments & right.compartments,
        provenance_id=None,
        metadata={
            **left.metadata,
            **right.metadata,
        },
    )


# ================================================================
# Dominance
# ================================================================


def dominates(
    left: SecurityLabel,
    right: SecurityLabel,
) -> bool:
    """
    Does left dominate right?
    """

    return (
        left.integrity >= right.integrity
        and left.confidentiality >= right.confidentiality
        and left.compartments.issuperset(right.compartments)
    )


# ================================================================
# Information Flow Relation
# ================================================================


def flows_to(
    source: SecurityLabel,
    destination: SecurityLabel,
) -> bool:
    """
    Determine whether information may legally flow from
    source to destination.

    Biba (Integrity)
        source.integrity >= destination.integrity

    Bell-LaPadula (Confidentiality)
        source.confidentiality <= destination.confidentiality

    Compartments
        Every source compartment must exist in destination.
    """

    integrity_ok = source.integrity >= destination.integrity

    confidentiality_ok = source.confidentiality <= destination.confidentiality

    compartments_ok = source.compartments.issubset(destination.compartments)

    return integrity_ok and confidentiality_ok and compartments_ok


# ================================================================
# Merge Helpers
# ================================================================


def join_all(
    *labels: SecurityLabel,
) -> SecurityLabel:
    """
    Join an arbitrary number of labels.

    Raises
    ------
    ValueError
        If no labels are supplied.
    """

    if not labels:
        raise ValueError("join_all() requires at least one label.")

    result = labels[0]

    for label in labels[1:]:
        result = join(result, label)

    return result


def meet_all(
    *labels: SecurityLabel,
) -> SecurityLabel:
    """
    Meet an arbitrary number of labels.
    """

    if not labels:
        raise ValueError("meet_all() requires at least one label.")

    result = labels[0]

    for label in labels[1:]:
        result = meet(result, label)

    return result


# ================================================================
# Convenience Predicates
# ================================================================


def equivalent(
    left: SecurityLabel,
    right: SecurityLabel,
) -> bool:
    """
    Lattice equivalence.
    """
    return left == right


def incomparable(
    left: SecurityLabel,
    right: SecurityLabel,
) -> bool:
    """
    Two labels are incomparable if neither dominates
    the other.
    """

    return not dominates(left, right) and not dominates(right, left)


# ================================================================
# Lattice Law Verification
# ================================================================


def is_commutative(
    left: SecurityLabel,
    right: SecurityLabel,
) -> bool:
    """
    Verify

        a ⊔ b == b ⊔ a
    """

    return join(left, right) == join(right, left)


def is_associative(
    a: SecurityLabel,
    b: SecurityLabel,
    c: SecurityLabel,
) -> bool:
    """
    Verify

        (a ⊔ b) ⊔ c

        ==

        a ⊔ (b ⊔ c)
    """

    return join(join(a, b), c) == join(a, join(b, c))


def is_idempotent(
    label: SecurityLabel,
) -> bool:
    """
    Verify

        a ⊔ a = a
    """

    return join(label, label) == label


# ================================================================
# Module Exports
# ================================================================

__all__ = [
    "integrity_join",
    "integrity_meet",
    "confidentiality_join",
    "confidentiality_meet",
    "join",
    "meet",
    "join_all",
    "meet_all",
    "dominates",
    "flows_to",
    "equivalent",
    "incomparable",
    "is_commutative",
    "is_associative",
    "is_idempotent",
]
