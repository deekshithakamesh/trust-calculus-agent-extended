import pytest
from trustcalc.sidechannels.denial_redaction import DenialFeedbackRedactor


class TestDenialFeedbackRedaction:
    @pytest.fixture
    def redactor(self):
        return DenialFeedbackRedactor(
            secrets=["API_KEY=demo1", "******"],
            patterns=[r"TOKEN=\w+"],
        )

    def test_exact_secret_redaction(self, redactor):
        msg = "Error: API_KEY=demo1 is invalid"
        assert "demo1" not in redactor.redact(msg)
        assert "[REDACTED]" in redactor.redact(msg)

    def test_regex_pattern_redaction(self, redactor):
        msg = "Token: TOKEN=tok1 is expired"
        assert "tok1" not in redactor.redact(msg)

    def test_nested_json_redaction(self, redactor):
        msg = '{"error": "API_KEY=demo1", "token": "TOKEN=tok1"}'
        result = redactor.redact(msg)
        assert "demo1" not in result
        assert "tok1" not in result

    def test_policy_enforcer_integration(self):
        from trustcalc.gateway.enforcement import PolicyEnforcer
        from trustcalc.policy.engine import PolicyEngine

        enforcer = PolicyEnforcer(policy_engine=PolicyEngine())
        denial = enforcer.generate_denial("delete", "API_KEY=demo1 invalid")
        assert "demo1" not in denial
        assert "[REDACTED]" in denial
