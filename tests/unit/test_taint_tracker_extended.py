"""
Research-grade tests for the extended TaintTracker API.

Covers the named value registry (get_taint / register_taint),
label-aware wrapping, and flow checking.
"""

from __future__ import annotations

from trustcalc.core.labels import (
    PUBLIC_LABEL,
    SECRET_LABEL,
)
from trustcalc.core.values import TrustedValue
from trustcalc.runtime.taint_tracker import TaintTracker


def test_wrap_with_name_registers_value():
    tracker = TaintTracker()

    value = tracker.wrap(
        "hello",
        PUBLIC_LABEL,
        name="greeting",
    )

    assert tracker.get_taint("greeting") is value


def test_wrap_without_name_not_registered():
    tracker = TaintTracker()

    tracker.wrap(
        "hello",
        PUBLIC_LABEL,
    )

    assert tracker.get_taint("greeting") is None


def test_taint_registers_named_value():
    tracker = TaintTracker()

    value = tracker.wrap(
        "hello",
        PUBLIC_LABEL,
    )

    tracker.taint(value, name="named")

    assert tracker.get_taint("named") is value


def test_register_taint_overwrites():
    tracker = TaintTracker()

    v1 = tracker.wrap("a", PUBLIC_LABEL)
    v2 = tracker.wrap("b", PUBLIC_LABEL)

    tracker.register_taint("key", v1)
    tracker.register_taint("key", v2)

    assert tracker.get_taint("key") is v2


def test_tracked_names():
    tracker = TaintTracker()

    tracker.wrap("a", PUBLIC_LABEL, name="first")
    tracker.wrap("b", PUBLIC_LABEL, name="second")

    assert set(tracker.tracked_names()) == {"first", "second"}


def test_clear_values():
    tracker = TaintTracker()

    tracker.wrap("a", PUBLIC_LABEL, name="x")

    tracker.clear_values()

    assert tracker.get_taint("x") is None


def test_statistics_includes_tracked_values():
    tracker = TaintTracker()

    tracker.wrap("a", PUBLIC_LABEL, name="x")

    stats = tracker.statistics()

    assert stats["tracked_values"] == 1
    assert stats["nodes"] == 1


def test_flow_check_allows_public_to_secret():
    tracker = TaintTracker()

    source = tracker.wrap(
        "sensitive",
        SECRET_LABEL,
    )

    # Confidential secret may flow into another secret sink.
    assert tracker.flow_check(source, SECRET_LABEL)


def test_flow_check_denies_secret_to_public():
    tracker = TaintTracker()

    source = tracker.wrap(
        "sensitive",
        SECRET_LABEL,
    )

    assert not tracker.flow_check(source, PUBLIC_LABEL)


def test_merge_registers_named_result():
    tracker = TaintTracker()

    a = tracker.wrap("Hello ", PUBLIC_LABEL)
    b = tracker.wrap("World", PUBLIC_LABEL)

    merged = tracker.merge(
        a,
        b,
        lambda x, y: x + y,
        name="combined",
    )

    assert tracker.get_taint("combined") is merged
    assert merged.value == "Hello World"


def test_transform_registers_named_result():
    tracker = TaintTracker()

    value = tracker.wrap("hello", PUBLIC_LABEL)

    transformed = tracker.transform(
        value,
        str.upper,
        name="upper",
    )

    assert tracker.get_taint("upper") is transformed
    assert transformed.value == "HELLO"


def test_sanitize_registers_named_result():
    tracker = TaintTracker()

    value = tracker.wrap("secret", SECRET_LABEL)

    sanitized = tracker.sanitize(
        value,
        PUBLIC_LABEL,
        name="clean",
    )

    assert tracker.get_taint("clean") is sanitized
    assert sanitized.label == PUBLIC_LABEL


def test_get_taint_returns_trusted_value():
    tracker = TaintTracker()

    tracker.wrap("payload", PUBLIC_LABEL, name="p")

    value = tracker.get_taint("p")

    assert isinstance(value, TrustedValue)
    assert value.value == "payload"


def test_flow_check_denies_invalid_inputs_explicitly():
    tracker = TaintTracker()
    source = tracker.wrap("payload", PUBLIC_LABEL)

    assert not tracker.flow_check(object(), PUBLIC_LABEL)
    assert not tracker.flow_check(source, object())
