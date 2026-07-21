"""
trustcalc.config
================

Configuration package for the Trust Calculus framework.

Provides configuration models, defaults, loading,
validation, and project path management.
"""

from .defaults import *
from .loader import ConfigLoader
from .paths import ProjectPaths
from .settings import (
    LoggingConfig,
    OutputConfig,
    RuntimeConfig,
    SecurityConfig,
    TrustCalcConfig,
)
from .validator import (
    ConfigValidationError,
    ConfigValidator,
)

__all__ = [
    # Settings
    "TrustCalcConfig",
    "RuntimeConfig",
    "SecurityConfig",
    "LoggingConfig",
    "OutputConfig",

    # Loader
    "ConfigLoader",

    # Validator
    "ConfigValidator",
    "ConfigValidationError",

    # Paths
    "ProjectPaths",
]