"""
trustcalc.core.exceptions
=========================

Exception hierarchy for the Trust Calculus runtime.

All framework-specific exceptions inherit from TrustCalcError.

The hierarchy is intentionally granular so callers can catch
specific classes of failures (policy, gateway, leakage, etc.)
without relying on generic exceptions.
"""

from __future__ import annotations


class TrustCalcError(Exception):
    """
    Base class for all Trust Calculus exceptions.
    """

    default_message = "Trust Calculus error."

    def __init__(self, message: str | None = None):
        super().__init__(message or self.default_message)


# =====================================================================
# Label / Lattice
# =====================================================================


class LabelError(TrustCalcError):
    default_message = "Invalid security label."


class InvalidLabelError(LabelError):
    default_message = "Security label validation failed."


class LatticeError(TrustCalcError):
    default_message = "Lattice operation failed."


class FlowViolation(LatticeError):
    default_message = "Information flow violates trust calculus."


# =====================================================================
# Policy
# =====================================================================


class PolicyError(TrustCalcError):
    default_message = "Policy evaluation failed."


class PolicyViolation(PolicyError):
    default_message = "Policy denied the requested action."


class CapabilityError(PolicyError):
    default_message = "Capability validation failed."


class CapabilityDenied(CapabilityError):
    default_message = "Required capability is missing."


# =====================================================================
# Runtime
# =====================================================================


class RuntimeError(TrustCalcError):
    default_message = "Runtime execution error."


class TaintError(RuntimeError):
    default_message = "Taint propagation failed."


class InterpreterError(RuntimeError):
    default_message = "Interpreter execution failed."


# =====================================================================
# Gateway
# =====================================================================


class GatewayError(TrustCalcError):
    default_message = "Gateway enforcement failed."


class GatewayDenied(GatewayError):
    default_message = "Gateway blocked the requested operation."


# =====================================================================
# Side Channels
# =====================================================================


class LeakageError(TrustCalcError):
    default_message = "Leakage analysis failed."


class LeakageViolation(LeakageError):
    default_message = "Potential covert channel detected."


class CanonicalizationError(LeakageError):
    default_message = "Canonicalization failed."


# =====================================================================
# Audit
# =====================================================================


class AuditError(TrustCalcError):
    default_message = "Audit logging failed."


# =====================================================================
# Tooling
# =====================================================================


class ToolError(TrustCalcError):
    default_message = "Tool execution failed."


class ToolExecutionError(ToolError):
    default_message = "Tool execution terminated unexpectedly."


class ToolValidationError(ToolError):
    default_message = "Tool request validation failed."


__all__ = [
    "TrustCalcError",
    "LabelError",
    "InvalidLabelError",
    "LatticeError",
    "FlowViolation",
    "PolicyError",
    "PolicyViolation",
    "CapabilityError",
    "CapabilityDenied",
    "RuntimeError",
    "TaintError",
    "InterpreterError",
    "GatewayError",
    "GatewayDenied",
    "LeakageError",
    "LeakageViolation",
    "CanonicalizationError",
    "AuditError",
    "ToolError",
    "ToolExecutionError",
    "ToolValidationError",
]
