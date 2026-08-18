"""
trustcalc.evaluation.benchmarks
===============================

Benchmark measurement suite for evaluating and comparing
trust-based authorization baselines across attack scenarios.

This module provides:
- BenchmarkMetrics: Individual scenario metrics
- BenchmarkResult: Aggregated benchmark results
- BenchmarkRunner: Orchestrates baseline testing
- MetricsAnalyzer: Statistical analysis and comparison

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

import numpy as np

from trustcalc.evaluation.attack_scenarios import AttackScenarioDefinition
from trustcalc.evaluation.baselines import BaselineSystem


@dataclass(slots=True)
class BenchmarkMetrics:
    """Metrics for a single attack scenario against a baseline."""

    scenario_name: str
    baseline_name: str
    
    # Decision metrics
    allow_count: int = 0
    deny_count: int = 0
    sandbox_count: int = 0
    restrict_count: int = 0
    verify_count: int = 0
    
    # Attack outcome
    attacks_blocked: int = 0
    attacks_successful: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    
    # Performance
    true_positive_rate: float = 0.0  # Correctly identified attacks
    false_positive_rate: float = 0.0  # Incorrectly denied benign requests
    true_negative_rate: float = 0.0  # Correctly allowed benign requests
    false_negative_rate: float = 0.0  # Missed attacks
    precision: float = 0.0  # TP / (TP + FP)
    recall: float = 0.0  # TP / (TP + FN)
    f1_score: float = 0.0  # Harmonic mean of precision and recall
    
    # Risk assessment
    avg_risk_exposure: float = 0.0  # Average risk of successful attacks
    max_risk_exposure: float = 0.0  # Maximum risk event
    total_risk_exposure: float = 0.0
    
    # Trust degradation
    avg_trust_impact: float = 0.0
    avg_confidence_impact: float = 0.0
    
    metadata: Dict[str, Any] = field(default_factory=dict)

    def compute_derived_metrics(self) -> None:
        """Compute derived metrics from base counters."""
        total = self.attacks_blocked + self.attacks_successful
        
        if total > 0:
            # True positive: attack was malicious and blocked
            tp = self.attacks_blocked
            # False positive: benign request was denied
            fp = self.false_positives
            # True negative: benign request was allowed
            tn = total - self.attacks_successful - self.false_positives
            # False negative: attack was malicious and allowed
            fn = self.attacks_successful
            
            self.true_positive_rate = tp / total if total > 0 else 0.0
            self.false_negative_rate = fn / total if total > 0 else 0.0
            
            # Precision: of things we denied, how many were actually attacks?
            if (tp + fp) > 0:
                self.precision = tp / (tp + fp)
            
            # Recall: of actual attacks, how many did we catch?
            if (tp + fn) > 0:
                self.recall = tp / (tp + fn)
            
            # F1: harmonic mean of precision and recall
            if (self.precision + self.recall) > 0:
                self.f1_score = 2 * (self.precision * self.recall) / (self.precision + self.recall)


@dataclass(slots=True)
class BenchmarkResult:
    """Aggregated benchmark result for a baseline across multiple scenarios."""

    baseline_name: str
    scenario_count: int = 0
    metrics: List[BenchmarkMetrics] = field(default_factory=list)
    
    # Aggregated metrics
    avg_f1_score: float = 0.0
    avg_precision: float = 0.0
    avg_recall: float = 0.0
    avg_true_positive_rate: float = 0.0
    avg_false_positive_rate: float = 0.0
    
    total_risk_exposure: float = 0.0
    avg_risk_exposure: float = 0.0
    
    total_attacks_blocked: int = 0
    total_attacks_successful: int = 0
    
    metadata: Dict[str, Any] = field(default_factory=dict)

    def aggregate_metrics(self) -> None:
        """Compute aggregate metrics from individual scenario results."""
        if not self.metrics:
            return
        
        self.scenario_count = len(self.metrics)
        
        # Average decision metrics
        self.avg_f1_score = np.mean([m.f1_score for m in self.metrics]) if self.metrics else 0.0
        self.avg_precision = np.mean([m.precision for m in self.metrics]) if self.metrics else 0.0
        self.avg_recall = np.mean([m.recall for m in self.metrics]) if self.metrics else 0.0
        self.avg_true_positive_rate = np.mean([m.true_positive_rate for m in self.metrics]) if self.metrics else 0.0
        self.avg_false_positive_rate = np.mean([m.false_positive_rate for m in self.metrics]) if self.metrics else 0.0
        
        # Aggregate risk and attack metrics
        self.total_risk_exposure = sum(m.total_risk_exposure for m in self.metrics)
        self.avg_risk_exposure = self.total_risk_exposure / len(self.metrics) if self.metrics else 0.0
        
        self.total_attacks_blocked = sum(m.attacks_blocked for m in self.metrics)
        self.total_attacks_successful = sum(m.attacks_successful for m in self.metrics)


class BenchmarkRunner:
    """Orchestrates benchmark execution across baselines and scenarios."""

    @staticmethod
    def run_scenario(
        baseline: BaselineSystem,
        scenario: AttackScenarioDefinition,
    ) -> BenchmarkMetrics:
        """Run a single scenario against a baseline."""
        
        # Determine if this is an attack based on risk and initial trust
        is_malicious = scenario.base_risk > 0.5 and scenario.initial_trust < 0.6
        
        # Get baseline decision
        decision = baseline.decide(
            trust=scenario.initial_trust,
            confidence=scenario.initial_confidence,
            risk=scenario.base_risk,
            malicious=is_malicious,
        )
        
        # Create metrics record
        metrics = BenchmarkMetrics(
            scenario_name=scenario.name,
            baseline_name=baseline.name,
        )
        
        # Count decision type
        if decision == "ALLOW":
            metrics.allow_count = 1
        elif decision == "DENY":
            metrics.deny_count = 1
        elif decision == "SANDBOX":
            metrics.sandbox_count = 1
        elif decision == "RESTRICT":
            metrics.restrict_count = 1
        elif decision == "VERIFY":
            metrics.verify_count = 1
        
        # Evaluate attack success
        if is_malicious:
            if decision in {"DENY", "SANDBOX", "RESTRICT"}:
                metrics.attacks_blocked = 1
            else:
                metrics.attacks_successful = 1
        else:
            if decision == "ALLOW":
                metrics.false_positives = 0
            else:
                metrics.false_positives = 1
        
        # Compute risk exposure
        if is_malicious and metrics.attacks_successful > 0:
            metrics.total_risk_exposure = scenario.base_risk
            metrics.avg_risk_exposure = scenario.base_risk
            metrics.max_risk_exposure = scenario.base_risk
        
        # Compute trust impact
        if is_malicious:
            metrics.avg_trust_impact = scenario.trust_damage_on_success
            metrics.avg_confidence_impact = scenario.confidence_damage_on_success
        
        metrics.compute_derived_metrics()
        return metrics

    @staticmethod
    def run_benchmark(
        baselines: List[BaselineSystem],
        scenarios: List[AttackScenarioDefinition],
    ) -> Dict[str, BenchmarkResult]:
        """Run full benchmark across all baselines and scenarios."""
        
        results: Dict[str, BenchmarkResult] = {}
        
        for baseline in baselines:
            result = BenchmarkResult(baseline_name=baseline.name)
            
            for scenario in scenarios:
                metrics = BenchmarkRunner.run_scenario(baseline, scenario)
                result.metrics.append(metrics)
            
            result.aggregate_metrics()
            results[baseline.name] = result
        
        return results


class MetricsAnalyzer:
    """Statistical analysis and comparison of benchmark results."""

    @staticmethod
    def compare_baselines(results: Dict[str, BenchmarkResult]) -> Dict[str, Any]:
        """Compare multiple baseline results."""
        
        comparison = {
            "baselines": list(results.keys()),
            "f1_scores": {},
            "precision_scores": {},
            "recall_scores": {},
            "risk_exposures": {},
            "attack_blocks": {},
        }
        
        for name, result in results.items():
            comparison["f1_scores"][name] = result.avg_f1_score
            comparison["precision_scores"][name] = result.avg_precision
            comparison["recall_scores"][name] = result.avg_recall
            comparison["risk_exposures"][name] = result.total_risk_exposure
            comparison["attack_blocks"][name] = result.total_attacks_blocked
        
        return comparison

    @staticmethod
    def rank_baselines(
        results: Dict[str, BenchmarkResult],
        metric: str = "f1_score",
    ) -> List[tuple[str, float]]:
        """Rank baselines by a specific metric."""
        
        rankings = []
        for name, result in results.items():
            if metric == "f1_score":
                score = result.avg_f1_score
            elif metric == "precision":
                score = result.avg_precision
            elif metric == "recall":
                score = result.avg_recall
            elif metric == "risk_exposure":
                score = -result.total_risk_exposure  # Lower is better
            elif metric == "attack_blocks":
                score = result.total_attacks_blocked  # Higher is better
            else:
                score = 0.0
            
            rankings.append((name, score))
        
        return sorted(rankings, key=lambda x: x[1], reverse=True)

    @staticmethod
    def statistical_summary(results: Dict[str, BenchmarkResult]) -> Dict[str, Any]:
        """Generate statistical summary of all benchmark results."""
        
        all_f1 = []
        all_precision = []
        all_recall = []
        all_risk = []
        
        for result in results.values():
            all_f1.append(result.avg_f1_score)
            all_precision.append(result.avg_precision)
            all_recall.append(result.avg_recall)
            all_risk.append(result.total_risk_exposure)
        
        return {
            "f1_score": {
                "mean": float(np.mean(all_f1)),
                "std": float(np.std(all_f1)),
                "min": float(np.min(all_f1)),
                "max": float(np.max(all_f1)),
            },
            "precision": {
                "mean": float(np.mean(all_precision)),
                "std": float(np.std(all_precision)),
                "min": float(np.min(all_precision)),
                "max": float(np.max(all_precision)),
            },
            "recall": {
                "mean": float(np.mean(all_recall)),
                "std": float(np.std(all_recall)),
                "min": float(np.min(all_recall)),
                "max": float(np.max(all_recall)),
            },
            "risk_exposure": {
                "mean": float(np.mean(all_risk)),
                "std": float(np.std(all_risk)),
                "min": float(np.min(all_risk)),
                "max": float(np.max(all_risk)),
            },
        }
