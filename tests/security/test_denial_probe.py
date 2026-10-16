from trustcalc.attacks.denial_probe import run_denial_probe


def test_redaction_removes_capability_name_but_not_status_channel():
    results = run_denial_probe()

    assert results["denial_message"] == "Tool call denied by policy."
    assert results["capability_name_disclosed"] is False
    assert results["capability_audit_keeps_full_reason"] is True
    assert results["allow_deny_channel_bits"] == 1.0
    assert [item["allowed"] for item in results["observations"]] == [True, False]
    assert results["observations"][1]["caller_feedback"] == results["denial_message"]
