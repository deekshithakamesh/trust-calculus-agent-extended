from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List

from trustcalc.evaluation.baselines import BaselineSystem


@dataclass(slots=True)
class AttackScenario:
    name: str
    malicious: bool = False
    risk: float = 0.0
    trust: float = 0.5
    confidence: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AttackSimulator:
    """Minimal reproducible attack simulator for comparing authorization baselines."""

    scenarios: List[AttackScenario] = field(default_factory=list)

    def add_scenario(self, scenario: AttackScenario) -> None:
        self.scenarios.append(scenario)

    def run(self, scenarios: Iterable[AttackScenario], baseline: BaselineSystem) -> Dict[str, Any]:
        results: List[Dict[str, Any]] = []
        blocked = 0
        allowed = 0
        denied = 0

        for scenario in scenarios:
            decision = baseline.decide(
                trust=scenario.trust,
                confidence=scenario.confidence,
                risk=scenario.risk,
                malicious=scenario.malicious,
            )
            is_blocked = decision in {"DENY", "SANDBOX", "RESTRICT", "VERIFY"} and scenario.malicious
            if decision == "DENY":
                denied += 1
            elif decision in {"ALLOW", "VERIFY"}:
                allowed += 1
            if decision in {"DENY", "SANDBOX", "RESTRICT"}:
                blocked += 1
            results.append(
                {
                    "name": scenario.name,
                    "malicious": scenario.malicious,
                    "decision": decision,
                    "blocked": is_blocked,
                    "risk": scenario.risk,
                    "trust": scenario.trust,
                    "confidence": scenario.confidence,
                }
            )

        total = len(results)
        success_rate = (denied / total) if total else 0.0
        return {
            "baseline": baseline.name,
            "total": total,
            "blocked": blocked,
            "denied": denied,
            "allowed": allowed,
            "success_rate": success_rate,
            "results": results,
        }
