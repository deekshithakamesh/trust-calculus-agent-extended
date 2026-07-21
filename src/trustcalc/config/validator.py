"""
trustcalc.config.validator
==========================

Configuration validator for the Trust Calculus framework.
"""

from __future__ import annotations

from pathlib import Path

from .settings import TrustCalcConfig


class ConfigValidationError(ValueError):
    """
    Raised when configuration validation fails.
    """


class ConfigValidator:
    """
    Validates Trust Calculus configuration.
    """

    VALID_LOG_LEVELS = {
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    }

    @classmethod
    def validate(
        cls,
        config: TrustCalcConfig,
    ) -> None:
        """
        Validate an entire configuration.
        """

        cls.validate_runtime(config)
        cls.validate_security(config)
        cls.validate_logging(config)
        cls.validate_output(config)

    # ---------------------------------------------------------

    @staticmethod
    def validate_runtime(
        config: TrustCalcConfig,
    ) -> None:

        runtime = config.runtime

        if runtime.max_workers <= 0:
            raise ConfigValidationError(
                "max_workers must be greater than zero."
            )

        if runtime.timeout <= 0:
            raise ConfigValidationError(
                "timeout must be greater than zero."
            )

    # ---------------------------------------------------------

    @classmethod
    def validate_security(
        cls,
        config: TrustCalcConfig,
    ) -> None:

        security = config.security

        if not 0.0 <= security.trust_threshold <= 1.0:
            raise ConfigValidationError(
                "trust_threshold must be between 0 and 1."
            )

        if security.max_leakage < 0:
            raise ConfigValidationError(
                "max_leakage cannot be negative."
            )

    # ---------------------------------------------------------

    @classmethod
    def validate_logging(
        cls,
        config: TrustCalcConfig,
    ) -> None:

        logging = config.logging

        if logging.level.upper() not in cls.VALID_LOG_LEVELS:
            raise ConfigValidationError(
                f"Invalid logging level: {logging.level}"
            )

    # ---------------------------------------------------------

    @staticmethod
    def validate_output(
        config: TrustCalcConfig,
    ) -> None:

        output = config.output

        for path in (
            output.root,
            output.reports,
            output.plots,
            output.logs,
            output.exports,
        ):
            if not isinstance(path, Path):
                raise ConfigValidationError(
                    f"Invalid output path: {path}"
                )

    # ---------------------------------------------------------

    @classmethod
    def is_valid(
        cls,
        config: TrustCalcConfig,
    ) -> bool:
        """
        Return True if configuration is valid.
        """

        try:
            cls.validate(config)
            return True
        except ConfigValidationError:
            return False