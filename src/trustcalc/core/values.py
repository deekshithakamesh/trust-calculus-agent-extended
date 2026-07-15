"""
trustcalc.core.values
=====================

Immutable value wrapper for the Trust Calculus runtime.

Every piece of data flowing through the runtime is represented as a
TrustedValue.

Unlike many IFC systems, TrustedValue intentionally contains NO
propagation logic.

Propagation is implemented exclusively by runtime.taint_tracker.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, Mapping, TypeVar
from types import MappingProxyType

from trustcalc.core.labels import SecurityLabel
from trustcalc.core.provenance import ProvenanceNode

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class TrustedValue(Generic[T]):
    """
    Immutable runtime value.

    Parameters
    ----------
    value
        Wrapped runtime object.

    label
        Security label.

    provenance
        Immutable provenance node.

    metadata
        Optional runtime metadata.

    Notes
    -----
    This class deliberately contains NO transformation logic.

    All propagation is performed by the TaintTracker.
    """

    value: T

    label: SecurityLabel

    provenance: ProvenanceNode

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

    @property
    def integrity(self):
        return self.label.integrity

    @property
    def confidentiality(self):
        return self.label.confidentiality

    @property
    def compartments(self):
        return self.label.compartments

    @property
    def is_public(self):
        return self.label.is_public

    @property
    def is_secret(self):
        return self.label.is_secret

    @property
    def is_trusted(self):
        return self.label.is_trusted

    @property
    def is_verified(self):
        return self.label.is_verified

    def unwrap(self) -> T:
        """
        Return the underlying value.

        The Tool Gateway is expected to be the primary component
        that unwraps TrustedValues before invoking tools.
        """
        return self.value

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize for logging/debugging.
        """

        return {
            "value": repr(self.value),
            "label": self.label.to_dict(),
            "provenance": self.provenance.to_dict(),
            "metadata": dict(self.metadata),
        }

    def __str__(self):

        return (
            "TrustedValue("
            f"value={self.value!r}, "
            f"integrity={self.integrity.name}, "
            f"confidentiality={self.confidentiality.name}"
            ")"
        )

    def __repr__(self):
        return self.__str__()
