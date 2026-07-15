from trustcalc.core.labels import PUBLIC_LABEL
from trustcalc.core.provenance import ProvenanceNode
from trustcalc.core.values import TrustedValue


def test_create():

    value = TrustedValue(
        value="hello",
        label=PUBLIC_LABEL,
        provenance=ProvenanceNode.origin(actor="system"),
    )

    assert value.value == "hello"

    assert value.is_public


def test_unwrap():

    value = TrustedValue(
        value=123,
        label=PUBLIC_LABEL,
        provenance=ProvenanceNode.origin(actor="system"),
    )

    assert value.unwrap() == 123


def test_serialization():

    value = TrustedValue(
        value="abc",
        label=PUBLIC_LABEL,
        provenance=ProvenanceNode.origin(actor="system"),
    )

    assert "label" in value.to_dict()


def test_metadata():

    value = TrustedValue(
        value="hello",
        label=PUBLIC_LABEL,
        provenance=ProvenanceNode.origin(actor="system"),
        metadata={"x": 10},
    )

    assert value.metadata["x"] == 10
