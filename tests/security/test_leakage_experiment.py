from __future__ import annotations

from trustcalc.attacks.leakage_experiment import run_comparison


def test_experiment_exhaustively_checks_designs_and_budget_invariants():
    results = run_comparison()

    assert results["secrets"] == 20
    assert results["case_count"] == 3 * 6 * 7 * 20
    assert len(results["summary"]) == 3 * 6
    assert all(
        case["secret_identified"]
        for case in results["cases"]
        if case["budget"] is None and case["strategy"] == "greedy"
    )
    assert all(
        case["max_caller_leakage_bits"] <= case["budget"] + 1e-12
        for case in results["cases"]
        if case["budget"] is not None
    )
