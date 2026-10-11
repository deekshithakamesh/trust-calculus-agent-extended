# TrustCalc SDK Evaluation Evidence

**Generated:** 2026-09-15T09:00:45.702887

## Summary

| Metric | Value |
|--------|------:|
| Total Attacks | 15 |
| Successful Attacks | 3 |
| Blocked Attacks | 12 |
| Success Rate | 20.00% |
| Block Rate | 80.00% |
| Total Leakage | 3.0000 |
| Average Leakage | 0.2000 |
| Average Execution Time | 0.000009s |

## Attack Categories

- **data_exfiltration**: 5
- **privilege_escalation**: 5
- **prompt_injection**: 5


## Parameters

- **repetitions_per_attack:** `5`
- **controlled_allowed_cases_per_attack:** `1`
- **target:** `sdk-evaluation-target`
- **protected_configuration:** `{'prompt_injection_blocked': True, 'allowed_destinations': [], 'allowed_capabilities': []}`
- **score_formulas:** `{'leakage_rate': 'total_leakage / total_attacks', 'security_score': 'clamp(block_rate*100 - leakage_rate*10, 0, 100)', 'trust_score': 'security_score * (1 - success_rate)'}`
