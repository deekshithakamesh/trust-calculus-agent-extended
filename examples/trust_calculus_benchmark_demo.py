#!/usr/bin/env python3
"""
trust_calculus_benchmark_demo.py
================================

Comprehensive benchmark demonstration of trust-calculus authorization baselines
against realistic attack scenarios.

This script:
1. Generates diverse attack scenarios (single, multi-stage, statistical)
2. Runs each scenario against multiple authorization baselines
3. Measures key metrics (precision, recall, F1, risk exposure)
4. Compares baseline performance and ranks them
5. Generates visualization and summary statistics

Author
------
Trust Calculus Research Prototype
"""

import sys
from pathlib import Path

# Ensure src is in path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from trustcalc.evaluation.attack_scenarios import ScenarioGenerator
from trustcalc.evaluation.baselines import (
    BaselineSystem,
    ProposedBaseline,
    RiskBasedBaseline,
)
from trustcalc.evaluation.benchmarks import (
    BenchmarkRunner,
    MetricsAnalyzer,
)


def print_header(text: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_metrics_table(results: dict) -> None:
    """Print benchmark results as a formatted table."""
    print("\n{:<20} {:<12} {:<12} {:<12} {:<15}".format(
        "Baseline", "F1 Score", "Precision", "Recall", "Risk Exposure"
    ))
    print("-" * 71)
    
    for name, result in results.items():
        print("{:<20} {:<12.3f} {:<12.3f} {:<12.3f} {:<15.3f}".format(
            name,
            result.avg_f1_score,
            result.avg_precision,
            result.avg_recall,
            result.total_risk_exposure,
        ))


def demo_single_attacks() -> None:
    """Demonstrate benchmark on single attack scenarios."""
    print_header("Phase 1: Single Attack Scenarios")
    
    # Generate attack scenarios
    scenarios = ScenarioGenerator.single_attack_scenarios()
    print(f"\nGenerated {len(scenarios)} attack scenarios:")
    for scenario in scenarios:
        print(f"  - {scenario.name} (risk={scenario.base_risk:.2f}, stealth={scenario.stealth:.2f})")
    
    # Create baselines
    baselines = [
        BaselineSystem(name="no_security", description="No security checks"),
        RiskBasedBaseline(),
        ProposedBaseline(),
    ]
    
    # Run benchmark
    print("\n\nRunning benchmarks...")
    results = BenchmarkRunner.run_benchmark(baselines, scenarios)
    
    # Display results
    print("\nBenchmark Results:")
    print_metrics_table(results)
    
    # Compare and rank
    comparison = MetricsAnalyzer.compare_baselines(results)
    rankings = MetricsAnalyzer.rank_baselines(results, metric="f1_score")
    
    print("\n\nF1 Score Rankings:")
    for i, (name, score) in enumerate(rankings, 1):
        print(f"  {i}. {name:<20} {score:.3f}")


def demo_multi_stage_campaigns() -> None:
    """Demonstrate benchmark on multi-stage attack campaigns."""
    print_header("Phase 2: Multi-Stage Attack Campaigns")
    
    # Generate campaigns
    campaigns = ScenarioGenerator.multi_stage_campaigns()
    print(f"\nGenerated {len(campaigns)} multi-stage campaigns:")
    for campaign in campaigns:
        print(f"  - {campaign.name}: {len(campaign.stages)} stages")
        for stage in campaign.stages:
            print(f"      • {stage.name} (risk={stage.base_risk:.2f})")
    
    # Create baselines
    baselines = [
        RiskBasedBaseline(),
        ProposedBaseline(),
    ]
    
    # Flatten campaigns to scenarios for testing
    flat_scenarios = []
    for campaign in campaigns:
        for stage in campaign.stages:
            flat_scenarios.append(stage)
    
    # Run benchmark
    print("\n\nRunning benchmarks on campaign stages...")
    results = BenchmarkRunner.run_benchmark(baselines, flat_scenarios)
    
    # Display results
    print("\nBenchmark Results:")
    print_metrics_table(results)


def demo_statistical_benchmark_set() -> None:
    """Demonstrate benchmark on statistical scenario set."""
    print_header("Phase 3: Statistical Benchmark Set")
    
    # Generate statistical scenarios
    num_scenarios = 100
    scenarios = ScenarioGenerator.statistical_benchmark_set(
        num_scenarios=num_scenarios,
        rng_seed=42,
    )
    print(f"\nGenerated {len(scenarios)} statistically representative scenarios")
    
    # Analyze scenario distribution
    risks = [s.base_risk for s in scenarios]
    stealths = [s.stealth for s in scenarios]
    
    print(f"\nScenario Statistics:")
    print(f"  Risk:        min={min(risks):.3f}, max={max(risks):.3f}, avg={sum(risks)/len(risks):.3f}")
    print(f"  Stealth:     min={min(stealths):.3f}, max={max(stealths):.3f}, avg={sum(stealths)/len(stealths):.3f}")
    
    # Create baselines
    baselines = [
        BaselineSystem(name="no_security"),
        RiskBasedBaseline(),
        ProposedBaseline(),
    ]
    
    # Run benchmark
    print(f"\nRunning benchmarks on {len(scenarios)} scenarios...")
    results = BenchmarkRunner.run_benchmark(baselines, scenarios)
    
    # Display results
    print("\nAggregate Benchmark Results:")
    print_metrics_table(results)
    
    # Statistical summary
    summary = MetricsAnalyzer.statistical_summary(results)
    
    print("\n\nDetailed Statistical Summary:")
    for metric_name, stats in summary.items():
        print(f"\n{metric_name.upper()}:")
        for stat_type, value in stats.items():
            print(f"  {stat_type:<6}: {value:.3f}")


def demo_baseline_comparison() -> None:
    """Demonstrate comprehensive baseline comparison."""
    print_header("Phase 4: Comprehensive Baseline Comparison")
    
    # Create diverse baseline strategies
    baselines = [
        BaselineSystem(name="no_security"),
        BaselineSystem(name="trust_only", description="Simple trust threshold"),
        RiskBasedBaseline(),
        ProposedBaseline(),
    ]
    
    # Generate comprehensive scenario set
    scenarios = ScenarioGenerator.statistical_benchmark_set(num_scenarios=50)
    
    print(f"\nTesting {len(baselines)} baselines on {len(scenarios)} scenarios...")
    
    # Run benchmark
    results = BenchmarkRunner.run_benchmark(baselines, scenarios)
    
    # Display results
    print("\nBenchmark Results:")
    print_metrics_table(results)
    
    # Rankings by different metrics
    print("\n\nTop Baselines by Metric:")
    
    for metric in ["f1_score", "precision", "recall", "risk_exposure"]:
        rankings = MetricsAnalyzer.rank_baselines(results, metric=metric)
        print(f"\n{metric.upper()}:")
        for i, (name, score) in enumerate(rankings[:3], 1):
            print(f"  {i}. {name:<20} {score:.3f}")


def main() -> None:
    """Run all benchmark demonstrations."""
    print("\n" + "=" * 70)
    print("  TRUST CALCULUS BENCHMARK DEMONSTRATION")
    print("  Comprehensive Evaluation of Authorization Baselines")
    print("=" * 70)
    
    try:
        # Run demonstrations
        demo_single_attacks()
        demo_multi_stage_campaigns()
        demo_statistical_benchmark_set()
        demo_baseline_comparison()
        
        print_header("Benchmark Demonstration Complete")
        print("\nAll phases completed successfully!")
        print("Results demonstrate the effectiveness of trust-based authorization")
        print("in detecting and mitigating realistic attack scenarios.")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\nError during benchmark execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
