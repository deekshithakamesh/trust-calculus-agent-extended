"""
trustcalc.utils.exceptions
==========================

Custom exception hierarchy for the Trust Calculus framework.
"""

from __future__ import annotations


class TrustCalcError(Exception):
    """
    Base exception for all Trust Calculus errors.
    """

    pass


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------


class ConfigurationError(TrustCalcError):
    """
    Raised when configuration loading or validation fails.
    """

    pass


# ---------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------


class RuntimeError(TrustCalcError):
    """
    Raised for runtime execution failures.
    """

    pass


class InitializationError(RuntimeError):
    """
    Raised when a component fails to initialize.
    """

    pass


class ShutdownError(RuntimeError):
    """
    Raised when a component fails to shut down cleanly.
    """

    pass


# ---------------------------------------------------------------------
# Trust & Policy
# ---------------------------------------------------------------------


class TrustError(TrustCalcError):
    """
    Base class for trust-related failures.
    """

    pass


class TrustThresholdError(TrustError):
    """
    Raised when trust falls below an acceptable threshold.
    """

    pass


class PolicyError(TrustCalcError):
    """
    Raised when policy evaluation fails.
    """

    pass


class PolicyViolationError(PolicyError):
    """
    Raised when a security policy is violated.
    """

    pass


# ---------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------


class SecurityError(TrustCalcError):
    """
    Base class for security-related failures.
    """

    pass


class PermissionDeniedError(SecurityError):
    """
    Raised when access is denied.
    """

    pass


class SideChannelError(SecurityError):
    """
    Raised when a side-channel issue is detected.
    """

    pass


class LeakageError(SecurityError):
    """
    Raised when confidential information is leaked.
    """

    pass


class AttackError(SecurityError):
    """
    Raised when an attack execution fails.
    """

    pass


# ---------------------------------------------------------------------
# Agents & Tools
# ---------------------------------------------------------------------


class AgentError(TrustCalcError):
    """
    Raised for agent-related failures.
    """

    pass


class ToolError(TrustCalcError):
    """
    Raised when a tool invocation fails.
    """

    pass


class GatewayError(TrustCalcError):
    """
    Raised when gateway communication fails.
    """

    pass


# ---------------------------------------------------------------------
# Evaluation & Analysis
# ---------------------------------------------------------------------


class EvaluationError(TrustCalcError):
    """
    Raised during evaluation failures.
    """

    pass


class AnalysisError(TrustCalcError):
    """
    Raised during analysis failures.
    """

    pass


class ReportError(TrustCalcError):
    """
    Raised while generating reports.
    """

    pass


# ---------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------


class SerializationError(TrustCalcError):
    """
    Raised when serialization or deserialization fails.
    """

    pass


# ---------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------


class ValidationError(TrustCalcError):
    """
    Raised when validation fails.
    """

    pass