"""
trustcalc.utils.logging
=======================

Logging utilities for the Trust Calculus framework.
"""

from __future__ import annotations

import logging
from pathlib import Path


class LoggerFactory:
    """
    Factory class for creating configured loggers.
    """

    @staticmethod
    def create_logger(
        name: str,
        level: str = "INFO",
        log_file: str | None = None,
        console: bool = True,
    ) -> logging.Logger:
        """
        Create and configure a logger.

        Parameters
        ----------
        name : str
            Logger name.
        level : str
            Logging level.
        log_file : str | None
            Optional log file.
        console : bool
            Enable console logging.

        Returns
        -------
        logging.Logger
        """

        logger = logging.getLogger(name)

        if logger.handlers:
            return logger

        logger.setLevel(getattr(logging, level.upper(), logging.INFO))

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        )

        if console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            file_handler = logging.FileHandler(log_path)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        logger.propagate = False

        return logger


def get_logger(
    name: str,
) -> logging.Logger:
    """
    Get or create a logger.

    Parameters
    ----------
    name : str
        Logger name.
    """

    return LoggerFactory.create_logger(name)


def set_log_level(
    logger: logging.Logger,
    level: str,
) -> None:
    """
    Update logger level.
    """

    logger.setLevel(
        getattr(logging, level.upper(), logging.INFO)
    )


def disable_logging() -> None:
    """
    Disable all logging.
    """

    logging.disable(logging.CRITICAL)


def enable_logging() -> None:
    """
    Re-enable logging.
    """

    logging.disable(logging.NOTSET)