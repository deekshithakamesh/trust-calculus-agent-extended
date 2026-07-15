"""
trustcalc.gateway.exceptions
============================

Gateway-specific exceptions.

These exceptions are raised during request validation,
policy enforcement, and tool execution.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations


class GatewayError(Exception):
    """
    Base class for all gateway exceptions.
    """


# ---------------------------------------------------------------------
# Validation Errors
# ---------------------------------------------------------------------


class InvalidToolError(GatewayError):
    """
    Raised when a requested tool is unknown or invalid.
    """


class InvalidArgumentError(GatewayError):
    """
    Raised when tool arguments are malformed.
    """


class MissingArgumentError(InvalidArgumentError):
    """
    Raised when a required argument is missing.
    """


class InvalidArgumentTypeError(InvalidArgumentError):
    """
    Raised when an argument has an unexpected type.
    """


# ---------------------------------------------------------------------
# Authorization Errors
# ---------------------------------------------------------------------


class AuthorizationError(GatewayError):
    """
    Raised when a request is denied by the policy engine.
    """


class CapabilityError(AuthorizationError):
    """
    Raised when the required capability is missing.
    """


class LabelViolationError(AuthorizationError):
    """
    Raised when a security label prevents information flow.
    """


class IntegrityViolationError(AuthorizationError):
    """
    Raised when integrity requirements are violated.
    """


class ConfidentialityViolationError(AuthorizationError):
    """
    Raised when confidentiality rules are violated.
    """


# ---------------------------------------------------------------------
# Runtime Errors
# ---------------------------------------------------------------------


class ToolExecutionError(GatewayError):
    """
    Raised when a tool fails during execution.
    """


class ToolTimeoutError(ToolExecutionError):
    """
    Raised when tool execution exceeds the allowed timeout.
    """


class ToolUnavailableError(ToolExecutionError):
    """
    Raised when a tool is unavailable.
    """


class AuditError(GatewayError):
    """
    Raised when audit logging fails.
    """