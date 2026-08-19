"""
trustcalc.utils.decorators
==========================

Reusable decorators for the Trust Calculus framework.
"""

from __future__ import annotations

import functools
import logging
import threading
import time
import warnings
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def retry(
    attempts: int = 3,
    delay: float = 0.0,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Retry a callable when an expected exception is raised."""

    if attempts < 1:
        raise ValueError("attempts must be >= 1")

    if delay < 0:
        raise ValueError("delay must be >= 0")

    def decorator(func: Callable[P, R]) -> Callable[P, R]:

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == attempts - 1:
                        raise

                    if delay:
                        time.sleep(delay)

            raise RuntimeError("Retry failed unexpectedly.")

        return wrapper

    return decorator


def deprecated(
    reason: str = "",
    *,
    version: str | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Mark a function as deprecated."""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:

        message = f"{func.__name__} is deprecated."

        if version:
            message += f" Deprecated since version {version}."

        if reason:
            message += f" {reason}"

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            warnings.warn(
                message,
                DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator


def singleton(cls: type[Any]) -> type[Any]:
    """Make a class a thread-safe singleton."""

    lock = threading.Lock()
    instance: Any = None
    original_new = cls.__new__

    def __new__(
        target_cls: type[Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        nonlocal instance

        if instance is None:
            with lock:
                if instance is None:
                    instance = original_new(
                        target_cls,
                        *args,
                        **kwargs,
                    )

        return instance

    cls.__new__ = staticmethod(__new__)  # type: ignore[method-assign]

    return cls


def synchronized(
    func: Callable[P, R],
) -> Callable[P, R]:
    """Serialize calls to a function using a re-entrant lock."""

    lock = threading.RLock()

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        with lock:
            return func(*args, **kwargs)

    return wrapper


def memoize(
    func: Callable[P, R],
) -> Callable[P, R]:
    """Cache results for hashable arguments."""

    cache: dict[tuple[Any, ...], R] = {}
    lock = threading.RLock()

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            key = (
                args,
                tuple(sorted(kwargs.items())),
            )
            hash(key)
        except TypeError:
            return func(*args, **kwargs)

        with lock:
            if key in cache:
                return cache[key]

            result = func(*args, **kwargs)
            cache[key] = result

            return result

    def cache_clear() -> None:
        with lock:
            cache.clear()

    wrapper.cache_clear = cache_clear  # type: ignore[attr-defined]

    return wrapper


def log_calls(
    logger: logging.Logger | None = None,
    level: int = logging.DEBUG,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Log function entry and completion."""

    log = logger or logging.getLogger(__name__)

    def decorator(func: Callable[P, R]) -> Callable[P, R]:

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            log.log(
                level,
                "Calling %s",
                func.__qualname__,
            )

            result = func(*args, **kwargs)

            log.log(
                level,
                "Completed %s",
                func.__qualname__,
            )

            return result

        return wrapper

    return decorator


__all__ = [
    "retry",
    "deprecated",
    "singleton",
    "synchronized",
    "memoize",
    "log_calls",
]
