"""
tests/unit/test_attack_scenarios
================================

Unit tests for attack scenario definitions and generators.

Author
------
Trust Calculus Research Prototype
"""

import pytest

from trustcalc.evaluation.attack_scenarios import (
    AttackScenarioLibrary,
    AttackScenarioType,
    ScenarioGenerator,
    SequentialAttackScenario,
)


class TestAttackScenarioLibrary:
    """Test pre-configured attack scenarios."""

    def test_reconnaissance_scenario(self):
        scenario = AttackScenarioLibrary.reconnaissance()
        assert scenario.name == "Reconnaissance"
        assert scenario.attack_type == AttackScenarioType.RECONNAISSANCE
        assert scenario.stealth > 0.5  # High stealth
        assert scenario.sophistication < 0.5  # Low sophistication
        assert scenario.base_risk < 0.4  # Low risk

    def test_social_engineering_scenario(self):
        scenario = AttackScenarioLibrary.social_engineering()
        assert scenario.name == "Social Engineering"
        assert scenario.attack_type == AttackScenarioType.SOCIAL_ENGINEERING
        assert scenario.base_risk > 0.3
        assert len(scenario.evasion_tactics) > 0

    def test_privilege_escalation_scenario(self):
        scenario = AttackScenarioLibrary.privilege_escalation()
        assert scenario.name == "Privilege Escalation"
        assert scenario.attack_type == AttackScenarioType.PRIVILEGE_ESCALATION
        assert scenario.sophistication > 0.5
        assert scenario.base_risk > 0.5

    def test_data_exfiltration_scenario(self):
        scenario = AttackScenarioLibrary.data_exfiltration()
        assert scenario.name == "Data Exfiltration"
        assert scenario.attack_type == AttackScenarioType.DATA_EXFILTRATION
        assert scenario.stealth > 0.5  # Covert
        assert scenario.base_risk > 0.6  # High risk

    def test_prompt_injection_scenario(self):
        scenario = AttackScenarioLibrary.prompt_injection()
        assert scenario.name == "Prompt Injection"
        assert scenario.attack_type == AttackScenarioType.PROMPT_INJECTION

    def test_timing_attack_scenario(self):
        scenario = AttackScenarioLibrary.timing_attack()
        assert scenario.name == "Timing Attack"
        assert scenario.attack_type == AttackScenarioType.TIMING_ATTACK
        assert scenario.stealth == 0.9  # Very stealthy


class TestSequentialAttackScenario:
    """Test multi-stage attack campaigns."""

    def test_empty_scenario_cumulative_risk(self):
        scenario = SequentialAttackScenario(name="Empty")
        assert scenario.get_cumulative_risk() == 0.0

    def test_single_stage_cumulative_risk(self):
        scenario = SequentialAttackScenario(name="Single Stage")
        scenario.add_stage(AttackScenarioLibrary.reconnaissance())
        risk = scenario.get_cumulative_risk()
        assert 0.0 <= risk <= 1.0

    def test_multi_stage_cumulative_risk_with_effect(self):
        scenario = SequentialAttackScenario(
            name="Multi Stage",
            cumulative_effect=True,
        )
        scenario.add_stage(AttackScenarioLibrary.reconnaissance())
        scenario.add_stage(AttackScenarioLibrary.privilege_escalation())
        scenario.add_stage(AttackScenarioLibrary.data_exfiltration())
        
        risk = scenario.get_cumulative_risk()
        # With 3 stages, cumulative risk should be higher than individual
        assert 0.0 < risk <= 1.0

    def test_multi_stage_no_cumulative_effect(self):
        scenario = SequentialAttackScenario(
            name="No Cumulative",
            cumulative_effect=False,
        )
        scenario.add_stage(AttackScenarioLibrary.reconnaissance())
        scenario.add_stage(AttackScenarioLibrary.privilege_escalation())
        
        # Without cumulative effect, risk should equal last stage's risk
        risk = scenario.get_cumulative_risk()
        assert risk == AttackScenarioLibrary.privilege_escalation().base_risk


class TestScenarioGenerator:
    """Test scenario generation and factory methods."""

    def test_single_attack_scenarios(self):
        scenarios = ScenarioGenerator.single_attack_scenarios()
        assert len(scenarios) > 0
        assert all(hasattr(s, 'base_risk') for s in scenarios)
        assert all(hasattr(s, 'stealth') for s in scenarios)

    def test_multi_stage_campaigns(self):
        campaigns = ScenarioGenerator.multi_stage_campaigns()
        assert len(campaigns) > 0
        assert all(isinstance(c, SequentialAttackScenario) for c in campaigns)
        assert all(len(c.stages) > 1 for c in campaigns)

    def test_adversarial_difficulty_levels(self):
        levels = ScenarioGenerator.adversarial_difficulty_levels()
        
        assert "easy" in levels
        assert "medium" in levels
        assert "hard" in levels
        
        # Easy scenarios should have low sophistication
        easy_scenarios = levels["easy"]
        if easy_scenarios:
            assert all(s.sophistication < 0.4 for s in easy_scenarios)
        
        # Hard scenarios should have high sophistication
        hard_scenarios = levels["hard"]
        if hard_scenarios:
            assert all(s.sophistication >= 0.7 for s in hard_scenarios)

    def test_statistical_benchmark_set_size(self):
        num = 50
        benchmarks = ScenarioGenerator.statistical_benchmark_set(num_scenarios=num)
        assert len(benchmarks) == num

    def test_statistical_benchmark_set_variation(self):
        benchmarks = ScenarioGenerator.statistical_benchmark_set(num_scenarios=100, rng_seed=42)
        
        # Scenarios should have variation (not all identical)
        risks = [s.base_risk for s in benchmarks]
        stealth = [s.stealth for s in benchmarks]
        
        assert len(set(risks)) > 1, "Benchmarks should have variable risk values"
        assert len(set(stealth)) > 1, "Benchmarks should have variable stealth values"

    def test_statistical_benchmark_set_reproducibility(self):
        # Same seed should produce same results
        benchmarks1 = ScenarioGenerator.statistical_benchmark_set(
            num_scenarios=20,
            rng_seed=42,
        )
        benchmarks2 = ScenarioGenerator.statistical_benchmark_set(
            num_scenarios=20,
            rng_seed=42,
        )
        
        for b1, b2 in zip(benchmarks1, benchmarks2):
            assert b1.base_risk == b2.base_risk
            assert b1.stealth == b2.stealth
            assert b1.sophistication == b2.sophistication
