from trustcalc.core.labels import PUBLIC_LABEL
from trustcalc.runtime.taint_tracker import TaintTracker


def test_wrap():

    tracker = TaintTracker()

    value = tracker.wrap(

        "hello",

        PUBLIC_LABEL,
    )

    assert value.value == "hello"

    assert tracker.validate(value)


def test_taint():

    tracker = TaintTracker()

    value = tracker.wrap(

        "hello",

        PUBLIC_LABEL,
    )

    value = tracker.taint(value)

    assert tracker.validate(value)


def test_explain():

    tracker = TaintTracker()

    value = tracker.wrap(

        "abc",

        PUBLIC_LABEL,
    )

    explanation = tracker.explain(value)

    assert "origin" in explanation
def test_transform():

    tracker = TaintTracker()

    value = tracker.wrap(
        "hello",
        PUBLIC_LABEL,
    )

    upper = tracker.transform(
        value,
        lambda s: s.upper(),
    )

    assert upper.value == "HELLO"

    assert upper.label == value.label


def test_merge():

    tracker = TaintTracker()

    a = tracker.wrap(
        "Hello ",
        PUBLIC_LABEL,
    )

    b = tracker.wrap(
        "World",
        PUBLIC_LABEL,
    )

    c = tracker.merge(
        a,
        b,
        lambda x, y: x + y,
    )

    assert c.value == "Hello World"


def test_clone():

    tracker = TaintTracker()

    value = tracker.wrap(
        "abc",
        PUBLIC_LABEL,
    )

    copy = tracker.clone(value)

    assert copy.value == value.value

    assert copy.label == value.label

def test_sanitize():

    tracker = TaintTracker()

    value = tracker.wrap(
        "secret",
        PUBLIC_LABEL,
    )

    sanitized = tracker.sanitize(
        value,
        PUBLIC_LABEL,
    )

    assert sanitized.label == PUBLIC_LABEL


def test_lineage():

    tracker = TaintTracker()

    value = tracker.wrap(
        "hello",
        PUBLIC_LABEL,
    )

    lineage = tracker.lineage(value)

    assert len(lineage) == 1


def test_statistics():

    tracker = TaintTracker()

    tracker.wrap(
        "x",
        PUBLIC_LABEL,
    )

    stats = tracker.statistics()

    assert stats["nodes"] == 1


def test_history():

    tracker = TaintTracker()

    value = tracker.wrap(
        "abc",
        PUBLIC_LABEL,
    )

    history = tracker.history(value)

    assert len(history) == 1