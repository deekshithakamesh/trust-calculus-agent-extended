import pytest

from trustcalc.core.exceptions import (
    CapabilityDenied,
    FlowViolation,
    GatewayDenied,
    InvalidLabelError,
    LeakageViolation,
    PolicyViolation,
)


def test_label_error():
    with pytest.raises(InvalidLabelError):
        raise InvalidLabelError()


def test_policy_error():
    with pytest.raises(PolicyViolation):
        raise PolicyViolation()


def test_capability_error():
    with pytest.raises(CapabilityDenied):
        raise CapabilityDenied()


def test_gateway_error():
    with pytest.raises(GatewayDenied):
        raise GatewayDenied()


def test_flow_error():
    with pytest.raises(FlowViolation):
        raise FlowViolation()


def test_leakage_error():
    with pytest.raises(LeakageViolation):
        raise LeakageViolation("Leakage detected")
