"""
tests/unit/test_benchmarks
==========================

Unit tests for benchmark measurement, execution, and analysis.

Author
------
Trust Calculus Research Prototype
"""

import pytest

from trustcalc.evaluation.attack_scenarios import (
    AttackScenarioLibrary,
    ScenarioGenerator,
)
from trustcalc.evaluation.baselines import (
    BaselineSystem,
    ProposedBaseline,
    RiskBasedBaseline,
)
from trustcalc.evaluation.benchmarks import (
    BenchmarkMetrics,
    BenchmarkResult,
    BenchmarkRunner,
    MetricsAnalyzer,
)


class TestBenchmarkMetrics:
    """Test individual scenario metrics."""

    def test_metrics_initialization(self):
        metrics = BenchmarkMetrics(
            scenario_name="test_scenario",
            baseline_name="test_baseline",
        )
        assert metrics.scenario_name == "test_scenario"
        assert metrics.baseline_name == "test_baseline"
        assert metrics.allow_count == 0
        assert metrics.deny_count == 0

    def test_metrics_compute_derived_metrics_precision_recall(self):
        metrics = BenchmarkMetrics(
            scenario_name="test",
            baseline_name="test",
        )
        
        # Simulate: 10 attacks, 8 blocked, 2 successful
        metrics.attacks_blocked = 8
        metrics.attacks_successful = 2
        metrics.false_positives = 1
        
        metrics.compute_derived_metrics()
        
        # Precision = TP / (TP + FP) = 8 / (8 + 1) ≈ 0.889
        assert metrics.precision > 0.8
        # Recall = TP / (TP + FN) = 8 / (8 + 2) = 0.8
        assert metrics.recall == 0.8


class TestBenchmarkResult:
    """Test aggregated benchmark results."""

    def test_benchmark_result_initialization(self):
        result = BenchmarkResult(baseline_name="test_baseline")
        assert result.baseline_name == "test_baseline"
        assert result.scenario_count == 0
        assert len(result.metrics) == 0

    def test_aggregate_metrics_empty(self):
        result = BenchmarkResult(baseline_name="test")
        result.aggregate_metrics()
        
        assert result.scenario_count == 0
        assert result.avg_f1_score == 0.0

    def test_aggregate_metrics_single(self):
        result = BenchmarkResult(baseline_name="test")
        
        metrics = BenchmarkMetrics(scenario_name="test", baseline_name="test")
        metrics.attacks_blocked = 5
        metrics.attacks_successful = 1
        metrics.precision = 0.9
        metrics.recall = 0.8
        metrics.f1_score = 0.85
        metrics.total_risk_exposure = 0.5
        
        result.metrics.append(metrics)
        result.aggregate_metrics()
        
        assert result.scenario_count == 1
        assert result.avg_f1_score == 0.85
        assert result.avg_precision == 0.9
        assert result.total_attacks_blocked == 5
        assert result.total_attacks_successful == 1


class TestBenchmarkRunner:
    """Test benchmark execution."""

    def test_run_scenario_benign_allow(self):
        baseline = BaselineSystem(name="test")
        scenario = AttackScenarioLibrary.reconnaissance()
        
        metrics = BenchmarkRunner.run_scenario(baseline, scenario)
        
        assert metrics.scenario_name == "Reconnaissance"
        assert metrics.baseline_name == "test"

    def test_run_scenario_malicious_blocked(self):
        baseline = BaselineSystem(name="test")
        scenario = AttackScenarioLibrary.privilege_escalation()
        
        metrics = BenchmarkRunner.run_scenario(baseline, scenario)
        
        # Privilege escalation is high-risk, should be detected
        assert metrics.deny_count + metrics.sandbox_count + metrics.restrict_count >= 0

    def test_run_benchmark_multiple_scenarios(self):
        baselines = [
            BaselineSystem(name="baseline_1"),
            RiskBasedBaseline(),
        ]
        scenarios = ScenarioGenerator.single_attack_scenarios()[:3]
        
        results = BenchmarkRunner.run_benchmark(baselines, scenarios)
        
        assert len(results) == 2
        assert all(name in results for name in ["baseline_1", "risk_based"])
        
        for result in results.values():
            assert result.scenario_count == 3
            assert len(result.metrics) == 3


class TestMetricsAnalyzer:
    """Test metrics analysis and comparison."""

    def test_compare_baselines(self):
        result1 = BenchmarkResult(baseline_name="baseline_1")
        metrics1 = BenchmarkMetrics(scenario_name="s1", baseline_name="baseline_1")
        metrics1.f1_score = 0.85
        metrics1.precision = 0.9
        metrics1.recall = 0.8
        result1.metrics.append(metrics1)
        result1.aggregate_metrics()
        
        result2 = BenchmarkResult(baseline_name="baseline_2")
        metrics2 = BenchmarkMetrics(scenario_name="s1", baseline_name="baseline_2")
        metrics2.f1_score = 0.75
        metrics2.precision = 0.8
        metrics2.recall = 0.7
        result2.metrics.append(metrics2)
        result2.aggregate_metrics()
        
        results = {"baseline_1": result1, "baseline_2": result2}
        comparison = MetricsAnalyzer.compare_baselines(results)
        
        assert "baseline_1" in comparison["baselines"]
        assert "baseline_2" in comparison["baselines"]
        assert comparison["f1_scores"]["baseline_1"] > comparison["f1_scores"]["baseline_2"]

    def test_rank_baselines_by_f1_score(self):
        result1 = BenchmarkResult(baseline_name="baseline_1")
        metrics1 = BenchmarkMetrics(scenario_name="s1", baseline_name="baseline_1")
        metrics1.f1_score = 0.85
        result1.metrics.append(metrics1)
        result1.aggregate_metrics()
        
        result2 = BenchmarkResult(baseline_name="baseline_2")
        metrics2 = BenchmarkMetrics(scenario_name="s1", baseline_name="baseline_2")
        metrics2.f1_score = 0.75
        result2.metrics.append(metrics2)
        result2.aggregate_metrics()
        
        results = {"baseline_1": result1, "baseline_2": result2}
        rankings = MetricsAnalyzer.rank_baselines(results, metric="f1_score")
        
        assert len(rankings) == 2
        assert rankings[0][0] == "baseline_1"  # baseline_1 has higher f1_score
        assert rankings[1][0] == "baseline_2"

    def test_statistical_summary(self):
        result1 = BenchmarkResult(baseline_name="baseline_1")
        metrics1 = BenchmarkMetrics(scenario_name="s1", baseline_name="baseline_1")
        metrics1.f1_score = 0.85
        metrics1.precision = 0.9
        metrics1.recall = 0.8
        result1.metrics.append(metrics1)
        result1.aggregate_metrics()
        
        result2 = BenchmarkResult(baseline_name="baseline_2")
        metrics2 = BenchmarkMetrics(scenario_name="s1", baseline_name="baseline_2")
        metrics2.f1_score = 0.75
        metrics2.precision = 0.8
        metrics2.recall = 0.7
        result2.metrics.append(metrics2)
        result2.aggregate_metrics()
        
        results = {"baseline_1": result1, "baseline_2": result2}
        summary = MetricsAnalyzer.statistical_summary(results)
        
        assert "f1_score" in summary
        assert "precision" in summary
        assert "recall" in summary
        assert "mean" in summary["f1_score"]
        assert "std" in summary["f1_score"]
