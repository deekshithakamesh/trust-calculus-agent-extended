from trustcalc.evaluation.baselines import BaselineSystem, RiskBasedBaseline, ProposedBaseline
from trustcalc.evaluation.simulator import AttackScenario, AttackSimulator


def test_attack_simulator_tracks_success_and_blocked_count():
    simulator = AttackSimulator()

    scenarios = [
        AttackScenario(name="prompt_injection", malicious=True, risk=0.6, trust=0.3, confidence=0.8),
        AttackScenario(name="web_search", malicious=False, risk=0.1, trust=0.9, confidence=0.9),
    ]

    summary = simulator.run(scenarios, ProposedBaseline())

    assert summary["total"] == 2
    assert summary["blocked"] >= 1
    assert summary["success_rate"] >= 0.0


def test_risk_based_baseline_blocks_high_risk_malicious_action():
    baseline = RiskBasedBaseline()

    decision = baseline.decide(trust=0.35, confidence=0.8, risk=0.9, malicious=True)

    assert decision == "DENY"


def test_proposed_baseline_uses_confidence_and_risk_together():
    baseline = ProposedBaseline()

    safe = baseline.decide(trust=0.92, confidence=0.9, risk=0.2, malicious=False)
    unsafe = baseline.decide(trust=0.72, confidence=0.2, risk=0.8, malicious=True)

    assert safe == "ALLOW"
    assert unsafe in {"SANDBOX", "DENY"}


def test_baseline_system_summary_is_stable():
    baselines = [
        BaselineSystem(name="no_security"),
        RiskBasedBaseline(),
        ProposedBaseline(),
    ]

    summary = BaselineSystem.summarize(baselines)

    assert set(summary) == {"no_security", "risk_based", "proposed"}
    assert all("decision" in summary[name] for name in summary)
