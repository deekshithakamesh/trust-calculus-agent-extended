from trustcalc.core.labels import *
from trustcalc.core.lattice import *


def test_join():

    a = PUBLIC_LABEL

    b = SECRET_LABEL

    c = join(a, b)

    assert c.confidentiality == Confidentiality.SECRET


def test_meet():

    a = PUBLIC_LABEL

    b = SECRET_LABEL

    c = meet(a, b)

    assert c.confidentiality == Confidentiality.PUBLIC


def test_flow():

    assert flows_to(
        PUBLIC_LABEL,
        SECRET_LABEL,
    )

    assert not flows_to(
        SECRET_LABEL,
        PUBLIC_LABEL,
    )


def test_join_all():

    label = join_all(
        PUBLIC_LABEL,
        SECRET_LABEL,
        UNTRUSTED_LABEL,
    )

    assert label.integrity == Integrity.UNTRUSTED


def test_lattice_laws():

    assert is_commutative(
        PUBLIC_LABEL,
        SECRET_LABEL,
    )

    assert is_idempotent(SECRET_LABEL)

    assert is_associative(
        PUBLIC_LABEL,
        SECRET_LABEL,
        UNTRUSTED_LABEL,
    )
