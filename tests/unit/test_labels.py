from trustcalc.core.labels import *


def test_public_label():

    assert PUBLIC_LABEL.is_public
    assert PUBLIC_LABEL.is_trusted


def test_secret_label():

    assert SECRET_LABEL.is_secret


def test_untrusted():

    assert UNTRUSTED_LABEL.integrity is Integrity.UNTRUSTED


def test_add_compartment():

    label = PUBLIC_LABEL.with_compartment("finance")

    assert "finance" in label.compartments


def test_remove_compartment():

    label = PUBLIC_LABEL.with_compartment("finance").without_compartment("finance")

    assert len(label.compartments) == 0


def test_metadata():

    label = PUBLIC_LABEL.with_metadata(owner="planner")

    assert label.metadata["owner"] == "planner"


def test_json_roundtrip():

    label = SECRET_LABEL.with_compartment("payroll")

    restored = SecurityLabel.from_json(label.to_json())

    assert restored == label


def test_copy():

    copied = PUBLIC_LABEL.copy()

    assert copied == PUBLIC_LABEL


def test_helper_functions():

    assert is_public(PUBLIC_LABEL)

    assert is_secret(SECRET_LABEL)

    assert is_untrusted(UNTRUSTED_LABEL)

    assert is_verified(TOP_SECRET_LABEL)
