from trustcalc.trust.model import TrustStore
from trustcalc.trust.evidence import Evidence, map_strength_to_weight


def test_evidence_updates_posterior():
    ts = TrustStore(half_life_seconds=3600.0)
    subj = "tool-A"
    action = "read-public"

    # baseline
    a0, b0 = ts.get_posterior(subj, action)

    ev = Evidence(source="monitor-1", type="success", strength=0.9)
    ev.weight = map_strength_to_weight(ev.strength)
    ts.record_evidence(subj, action, ev)

    a1, b1 = ts.get_posterior(subj, action)
    assert a1 > a0, "alpha should increase after success evidence"
    assert b1 == b0, "beta should be unchanged for success evidence"

    # failure evidence
    ev2 = Evidence(source="monitor-2", type="failure", strength=0.8)
    ev2.weight = map_strength_to_weight(ev2.strength)
    ts.record_evidence(subj, action, ev2)
    a2, b2 = ts.get_posterior(subj, action)
    assert b2 > b1, "beta should increase after failure evidence"


def test_get_trust_state_serializable():
    ts = TrustStore()
    ts.record_result("tool-B", "write-db", True)
    state = ts.get_trust_state("tool-B", "write-db")
    assert "expected" in state and "confidence" in state
