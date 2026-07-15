from trustcalc.policy.capabilities import (
    Capability,
    CapabilitySet,
)


def test_create():

    cap = Capability(
        resource="email",
        action="send",
    )

    assert cap.identifier == "email:send"


def test_set():

    cap = Capability(
        resource="email",
        action="send",
    )

    caps = CapabilitySet().add(cap)

    assert caps.allows(
        "email",
        "send",
    )


def test_remove():

    cap = Capability(
        resource="email",
        action="send",
    )

    caps = CapabilitySet().add(cap)

    caps = caps.remove(cap)

    assert not caps.allows(
        "email",
        "send",
    )
