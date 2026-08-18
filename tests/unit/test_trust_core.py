import math

import pytest

from trustcalc.trust.authority import AuthorityDecision, decide_authority
from trustcalc.trust.evidence import Evidence, EvidenceType
from trustcalc.trust.risk import estimate_action_risk, required_trust
from trustcalc.trust.state import TrustState
from trustcalc.trust.temporal import apply_temporal_decay
from trustcalc.trust.delegation import effective_authority
from trustcalc.trust.updater import update_trust


def test_evidence_updates_belief_upward():
    state = TrustState(entity_id="tool-1", action="web_search")
    evidence = Evidence(
        type=EvidenceType.SUCCESS,
        value=1.0,
        weight=2.0,
        source="benchmark",
    )

    updated = update_trust(state, evidence, success=True)

    assert updated.alpha > state.alpha
    assert updated.beta == state.beta
    assert updated.trust > 0.5
    assert updated.confidence > 0.0


def test_higher_risk_requires_higher_trust():
    low_risk = required_trust(estimate_action_risk("web_search"))
    high_risk = required_trust(estimate_action_risk("code_execution"))

    assert high_risk > low_risk


def test_authority_decision_allows_well_calibrated_actions():
    decision = decide_authority(0.9, 0.9, estimate_action_risk("web_search"))

    assert decision == AuthorityDecision.ALLOW


def test_authority_decision_sandboxes_low_confidence_high_trust():
    decision = decide_authority(0.92, 0.18, estimate_action_risk("database_write"))

    assert decision == AuthorityDecision.SANDBOX


def test_temporal_decay_reduces_trust_without_new_evidence():
    state = TrustState(entity_id="tool-2", action="file_read", trust=0.9, alpha=9.0, beta=1.0)

    decayed = apply_temporal_decay(state, days=30)

    assert decayed.trust < state.trust


def test_delegation_reduces_effective_authority():
    auth = effective_authority(0.9, delegation_depth=3)

    assert 0 < auth < 0.9
    assert math.isfinite(auth)
