"""Generate reproducible SDK evaluation evidence.

This benchmark intentionally includes a small allowed-attack control group so
the score calculation can be inspected rather than reporting a perfect score
from blocked cases only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trustcalc.analysis.analyzer import Analyzer
from trustcalc.analysis.metrics import MetricsAnalyzer
from trustcalc.analysis.plots import PlotGenerator
from trustcalc.analysis.report import ReportGenerator
from trustcalc.analysis.statistics import StatisticsAnalyzer
from trustcalc.attacks.data_exfiltration import DataExfiltrationAttack
from trustcalc.attacks.privilege_escalation import PrivilegeEscalationAttack
from trustcalc.attacks.prompt_injection import PromptInjectionAttack


OUTPUT_DIR = Path("artifacts/sdk-evidence")
REPETITIONS = 5
CONTROLLED_ALLOWED_CASES = 1


def attack_cases() -> list[tuple[Any, dict[str, Any]]]:
    return [
        (
            PromptInjectionAttack(name="prompt-injection"),
            {},
        ),
        (
            DataExfiltrationAttack(name="data-exfiltration"),
            {"allowed_destinations": []},
        ),
        (
            PrivilegeEscalationAttack(name="privilege-escalation"),
            {"allowed_capabilities": []},
        ),
    ]


def run() -> dict[str, Any]:
    analyzer = Analyzer()
    parameters = {
        "repetitions_per_attack": REPETITIONS,
        "controlled_allowed_cases_per_attack": CONTROLLED_ALLOWED_CASES,
        "target": "sdk-evaluation-target",
        "protected_configuration": {
            "prompt_injection_blocked": True,
            "allowed_destinations": [],
            "allowed_capabilities": [],
        },
        "score_formulas": {
            "leakage_rate": "total_leakage / total_attacks",
            "security_score": "clamp(block_rate*100 - leakage_rate*10, 0, 100)",
            "trust_score": "security_score * (1 - success_rate)",
        },
    }

    for attack, kwargs in attack_cases():
        for index in range(REPETITIONS):
            case_kwargs = dict(kwargs)
            if index >= REPETITIONS - CONTROLLED_ALLOWED_CASES:
                if isinstance(attack, PromptInjectionAttack):
                    case_kwargs["blocked"] = False
                elif isinstance(attack, DataExfiltrationAttack):
                    case_kwargs["allowed_destinations"] = [attack.destination]
                elif isinstance(attack, PrivilegeEscalationAttack):
                    case_kwargs["allowed_capabilities"] = [
                        attack.requested_capability
                    ]
            analyzer.add_result(
                attack.run(
                    parameters["target"],
                    **case_kwargs,
                )
            )

    result = analyzer.analyze()
    metrics = MetricsAnalyzer.compute(result)
    statistics = StatisticsAnalyzer(analyzer.results).summarize()
    report = ReportGenerator("TrustCalc SDK Evaluation Evidence").generate(result)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "results.json").write_text(
        json.dumps(
            {
                "parameters": parameters,
                "analysis": result.to_dict(),
                "metrics": metrics.to_dict(),
                "statistics": statistics.to_dict(),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / "report.md").write_text(
        ReportGenerator("TrustCalc SDK Evaluation Evidence").to_markdown(report)
        + "\n\n## Parameters\n\n"
        + "\n".join(
            f"- **{key}:** `{value}`" for key, value in parameters.items()
        )
        + "\n",
        encoding="utf-8",
    )
    PlotGenerator(OUTPUT_DIR).generate_all(result)

    print(json.dumps(metrics.to_dict(), indent=2))
    print(json.dumps(statistics.to_dict(), indent=2))
    return {"analysis": result, "metrics": metrics, "statistics": statistics}


if __name__ == "__main__":
    run()
