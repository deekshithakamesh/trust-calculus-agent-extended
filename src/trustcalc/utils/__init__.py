"""
trustcalc.utils
===============

Common utility functions and helper classes used throughout the
Trust Calculus framework.
"""

from .decorators import (
    deprecated,
    log_calls,
    memoize,
    retry,
    singleton,
    synchronized,
)

from .exceptions import (
    AgentError,
    AnalysisError,
    AttackError,
    ConfigurationError,
    EvaluationError,
    GatewayError,
    InitializationError,
    LeakageError,
    PermissionDeniedError,
    PolicyError,
    PolicyViolationError,
    ReportError,
    RuntimeError,
    SecurityError,
    SerializationError,
    ShutdownError,
    SideChannelError,
    ToolError,
    TrustCalcError,
    TrustError,
    TrustThresholdError,
    ValidationError,
)

from .helpers import (
    chunks,
    deep_update,
    ensure_list,
    flatten_dict,
    generate_uuid,
    is_iterable,
    remove_none,
    safe_get,
    timestamp,
)

from .logging import (
    LoggerFactory,
    disable_logging,
    enable_logging,
    get_logger,
    set_log_level,
)

from .serialization import (
    SerializationError as SerializerError,
    Serializer,
)

from .timing import (
    Timer,
    TimingResult,
    Stopwatch,
    measure,
    now,
    timed,
)

from .validators import (
    validate_callable,
    validate_choice,
    validate_directory,
    validate_file,
    validate_identifier,
    validate_non_empty,
    validate_not_none,
    validate_path_exists,
    validate_positive,
    validate_probability,
    validate_range,
    validate_type,
)

__all__ = [
    # Helpers
    "generate_uuid",
    "timestamp",
    "flatten_dict",
    "deep_update",
    "ensure_list",
    "chunks",
    "safe_get",
    "remove_none",
    "is_iterable",

    # Logging
    "LoggerFactory",
    "get_logger",
    "set_log_level",
    "disable_logging",
    "enable_logging",

    # Serialization
    "Serializer",
    "SerializerError",

    # Timing
    "Timer",
    "TimingResult",
    "Stopwatch",
    "measure",
    "timed",
    "now",

    # Decorators
    "retry",
    "deprecated",
    "singleton",
    "synchronized",
    "memoize",
    "log_calls",

    # Validators
    "validate_type",
    "validate_not_none",
    "validate_non_empty",
    "validate_range",
    "validate_probability",
    "validate_positive",
    "validate_identifier",
    "validate_path_exists",
    "validate_file",
    "validate_directory",
    "validate_choice",
    "validate_callable",

    # Exceptions
    "TrustCalcError",
    "ConfigurationError",
    "RuntimeError",
    "InitializationError",
    "ShutdownError",
    "TrustError",
    "TrustThresholdError",
    "PolicyError",
    "PolicyViolationError",
    "SecurityError",
    "PermissionDeniedError",
    "SideChannelError",
    "LeakageError",
    "AttackError",
    "AgentError",
    "ToolError",
    "GatewayError",
    "EvaluationError",
    "AnalysisError",
    "ReportError",
    "SerializationError",
    "ValidationError",
]