"""
trustcalc.utils.timing
======================

Timing utilities for the Trust Calculus framework.
"""

from __future__ import annotations

import time
from contextlib import ContextDecorator
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable


@dataclass(slots=True)
class TimingResult:
    """
    Stores timing information.
    """

    start_time: float
    end_time: float
    elapsed_time: float

    def to_dict(self) -> dict[str, float]:
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "elapsed_time": self.elapsed_time,
        }


class Timer(ContextDecorator):
    """
    Context manager and decorator for timing code.
    """

    def __init__(self) -> None:
        self.start_time = 0.0
        self.end_time = 0.0
        self.elapsed_time = 0.0

    def __enter__(self) -> "Timer":
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.end_time = time.perf_counter()
        self.elapsed_time = self.end_time - self.start_time
        return False

    @property
    def result(self) -> TimingResult:
        return TimingResult(
            start_time=self.start_time,
            end_time=self.end_time,
            elapsed_time=self.elapsed_time,
        )


class Stopwatch:
    """
    Simple stopwatch utility.
    """

    def __init__(self) -> None:
        self._start = None
        self._elapsed = 0.0

    def start(self) -> None:
        self._start = time.perf_counter()

    def stop(self) -> float:
        if self._start is None:
            raise RuntimeError("Stopwatch has not been started.")

        self._elapsed = time.perf_counter() - self._start
        self._start = None
        return self._elapsed

    def reset(self) -> None:
        self._start = None
        self._elapsed = 0.0

    @property
    def elapsed(self) -> float:
        return self._elapsed


def timed(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator that measures execution time.

    The wrapped function returns:
        (result, elapsed_time)
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()

        result = func(*args, **kwargs)

        elapsed = time.perf_counter() - start

        return result, elapsed

    return wrapper


def measure(func: Callable[..., Any], *args, **kwargs) -> TimingResult:
    """
    Measure execution time of a callable.
    """

    start = time.perf_counter()

    func(*args, **kwargs)

    end = time.perf_counter()

    return TimingResult(
        start_time=start,
        end_time=end,
        elapsed_time=end - start,
    )


def now() -> float:
    """
    Return the current high-resolution timer value.
    """

    return time.perf_counter()