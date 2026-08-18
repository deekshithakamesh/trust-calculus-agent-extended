"""
trustcalc.evaluation.attack_scenarios
=====================================

Rich, realistic attack scenario definitions and generators for
comprehensive evaluation of trust-based authorization baselines.

This module provides:
- AttackScenarioType: Enum of attack categories
- AttackScenarioLibrary: Pre-configured attack scenarios
- ScenarioGenerator: Factory for composing attack sequences
- SequentialAttackScenario: Multi-stage attack sequences
- StatisticalScenarioSet: Benchmark scenario collections

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

import numpy as np


class AttackScenarioType(str, Enum):
    """Types of attacks to simulate."""

    RECONNAISSANCE = "reconnaissance"
    SOCIAL_ENGINEERING = "social_engineering"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    PROMPT_INJECTION = "prompt_injection"
    TIMING_ATTACK = "timing_attack"
    COVERT_CHANNEL = "covert_channel"
    MALWARE_INJECTION = "malware_injection"
    DENIAL_OF_SERVICE = "denial_of_service"
    INSIDER_THREAT = "insider_threat"


@dataclass(slots=True)
class AttackScenarioDefinition:
    """Complete definition of a single attack scenario."""

    name: str
    attack_type: AttackScenarioType
    description: str = ""
    
    # Attack characteristics
    base_risk: float = 0.5
    stealth: float = 0.5  # 0.0 = obvious, 1.0 = undetectable
    sophistication: float = 0.5  # 0.0 = simple, 1.0 = advanced
    
    # Initial trust assumptions
    initial_trust: float = 0.6
    initial_confidence: float = 0.5
    
    # Attack impact on trust
    trust_damage_on_success: float = 0.3
    confidence_damage_on_success: float = 0.4
    
    # Observable indicators
    detectable_signals: List[str] = field(default_factory=list)
    evasion_tactics: List[str] = field(default_factory=list)
    
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SequentialAttackScenario:
    """Multi-stage attack sequence."""

    name: str
    stages: List[AttackScenarioDefinition] = field(default_factory=list)
    description: str = ""
    
    # Sequential properties
    cumulative_effect: bool = True  # Do earlier stages degrade trust further?
    detector_adaptation: bool = False  # Does attacker adapt to defenses?
    time_between_stages: float = 0.0  # Seconds
    
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_stage(self, scenario: AttackScenarioDefinition) -> SequentialAttackScenario:
        """Add an attack stage to this sequence."""
        self.stages.append(scenario)
        return self

    def get_cumulative_risk(self) -> float:
        """Calculate cumulative risk across all stages."""
        if not self.stages:
            return 0.0
        if not self.cumulative_effect:
            return self.stages[-1].base_risk
        # Risk compounds: each stage increases the overall risk
        return min(1.0, sum(s.base_risk for s in self.stages) / len(self.stages))


class AttackScenarioLibrary:
    """Pre-configured attack scenarios based on real threat patterns."""

    @staticmethod
    def reconnaissance() -> AttackScenarioDefinition:
        """Information gathering attack."""
        return AttackScenarioDefinition(
            name="Reconnaissance",
            attack_type=AttackScenarioType.RECONNAISSANCE,
            description="Attacker gathers information about system, tools, and capabilities",
            base_risk=0.2,
            stealth=0.8,
            sophistication=0.3,
            initial_trust=0.7,
            initial_confidence=0.6,
            trust_damage_on_success=0.1,
            confidence_damage_on_success=0.15,
            detectable_signals=["unusual_queries", "excessive_tool_probing"],
            evasion_tactics=["slow_probing", "mixed_legitimate_queries"],
        )

    @staticmethod
    def social_engineering() -> AttackScenarioDefinition:
        """Social engineering attack."""
        return AttackScenarioDefinition(
            name="Social Engineering",
            attack_type=AttackScenarioType.SOCIAL_ENGINEERING,
            description="Attacker manipulates user into granting higher privileges",
            base_risk=0.4,
            stealth=0.6,
            sophistication=0.5,
            initial_trust=0.65,
            initial_confidence=0.55,
            trust_damage_on_success=0.35,
            confidence_damage_on_success=0.45,
            detectable_signals=["unusual_requests", "privilege_elevation_attempts"],
            evasion_tactics=["gradual_escalation", "flattery", "urgency_framing"],
        )

    @staticmethod
    def privilege_escalation() -> AttackScenarioDefinition:
        """Privilege escalation attack."""
        return AttackScenarioDefinition(
            name="Privilege Escalation",
            attack_type=AttackScenarioType.PRIVILEGE_ESCALATION,
            description="Attacker exploits vulnerabilities to gain higher authority",
            base_risk=0.65,
            stealth=0.4,
            sophistication=0.7,
            initial_trust=0.55,
            initial_confidence=0.45,
            trust_damage_on_success=0.5,
            confidence_damage_on_success=0.6,
            detectable_signals=["privilege_boundary_violations", "unauthorized_access"],
            evasion_tactics=["timing_attacks", "race_conditions"],
        )

    @staticmethod
    def data_exfiltration() -> AttackScenarioDefinition:
        """Data exfiltration attack."""
        return AttackScenarioDefinition(
            name="Data Exfiltration",
            attack_type=AttackScenarioType.DATA_EXFILTRATION,
            description="Attacker steals sensitive data through various channels",
            base_risk=0.7,
            stealth=0.7,
            sophistication=0.6,
            initial_trust=0.5,
            initial_confidence=0.4,
            trust_damage_on_success=0.6,
            confidence_damage_on_success=0.7,
            detectable_signals=["unusual_data_access", "large_transfers", "anomalous_patterns"],
            evasion_tactics=["covert_channels", "steganography", "timing_obfuscation"],
        )

    @staticmethod
    def prompt_injection() -> AttackScenarioDefinition:
        """Prompt injection attack against LLM."""
        return AttackScenarioDefinition(
            name="Prompt Injection",
            attack_type=AttackScenarioType.PROMPT_INJECTION,
            description="Attacker injects malicious instructions into LLM prompts",
            base_risk=0.6,
            stealth=0.5,
            sophistication=0.6,
            initial_trust=0.6,
            initial_confidence=0.5,
            trust_damage_on_success=0.4,
            confidence_damage_on_success=0.5,
            detectable_signals=["malicious_tokens", "instruction_override_patterns"],
            evasion_tactics=["obfuscation", "encoding", "indirect_instructions"],
        )

    @staticmethod
    def timing_attack() -> AttackScenarioDefinition:
        """Timing side-channel attack."""
        return AttackScenarioDefinition(
            name="Timing Attack",
            attack_type=AttackScenarioType.TIMING_ATTACK,
            description="Attacker infers information through timing analysis",
            base_risk=0.4,
            stealth=0.9,
            sophistication=0.7,
            initial_trust=0.7,
            initial_confidence=0.6,
            trust_damage_on_success=0.25,
            confidence_damage_on_success=0.3,
            detectable_signals=["statistical_timing_anomalies"],
            evasion_tactics=["constant_time_operations", "noise_injection"],
        )

    @staticmethod
    def malware_injection() -> AttackScenarioDefinition:
        """Malware injection attack."""
        return AttackScenarioDefinition(
            name="Malware Injection",
            attack_type=AttackScenarioType.MALWARE_INJECTION,
            description="Attacker injects malicious code into agent tools or runtime",
            base_risk=0.8,
            stealth=0.3,
            sophistication=0.8,
            initial_trust=0.4,
            initial_confidence=0.3,
            trust_damage_on_success=0.7,
            confidence_damage_on_success=0.8,
            detectable_signals=["code_signature", "behavioral_anomalies", "resource_abuse"],
            evasion_tactics=["polymorphism", "packing", "behavioral_mimicry"],
        )


class ScenarioGenerator:
    """Factory for generating realistic attack scenario collections."""

    @staticmethod
    def single_attack_scenarios() -> List[AttackScenarioDefinition]:
        """Generate individual attack scenarios."""
        return [
            AttackScenarioLibrary.reconnaissance(),
            AttackScenarioLibrary.social_engineering(),
            AttackScenarioLibrary.privilege_escalation(),
            AttackScenarioLibrary.data_exfiltration(),
            AttackScenarioLibrary.prompt_injection(),
            AttackScenarioLibrary.timing_attack(),
            AttackScenarioLibrary.malware_injection(),
        ]

    @staticmethod
    def multi_stage_campaigns() -> List[SequentialAttackScenario]:
        """Generate realistic multi-stage attack campaigns."""
        campaigns = []

        # Campaign 1: Reconnaissance -> Privilege Escalation -> Exfiltration
        campaign1 = SequentialAttackScenario(
            name="APT-style Campaign",
            description="Classic advanced persistent threat: recon, escalate, exfiltrate",
            cumulative_effect=True,
            time_between_stages=5.0,
        )
        campaign1.add_stage(AttackScenarioLibrary.reconnaissance())
        campaign1.add_stage(AttackScenarioLibrary.privilege_escalation())
        campaign1.add_stage(AttackScenarioLibrary.data_exfiltration())
        campaigns.append(campaign1)

        # Campaign 2: Social Engineering -> Prompt Injection
        campaign2 = SequentialAttackScenario(
            name="Deceptive Campaign",
            description="Low-tech social engineering + high-tech prompt injection",
            cumulative_effect=True,
            time_between_stages=2.0,
        )
        campaign2.add_stage(AttackScenarioLibrary.social_engineering())
        campaign2.add_stage(AttackScenarioLibrary.prompt_injection())
        campaigns.append(campaign2)

        # Campaign 3: Malware Injection with Covert Exfiltration
        campaign3 = SequentialAttackScenario(
            name="Malware Campaign",
            description="Direct malware injection with timing-based covert channel",
            cumulative_effect=True,
            time_between_stages=3.0,
        )
        campaign3.add_stage(AttackScenarioLibrary.malware_injection())
        campaign3.add_stage(AttackScenarioLibrary.timing_attack())
        campaigns.append(campaign3)

        return campaigns

    @staticmethod
    def adversarial_difficulty_levels() -> Dict[str, List[AttackScenarioDefinition]]:
        """Generate attack scenarios organized by difficulty level."""
        scenarios = ScenarioGenerator.single_attack_scenarios()
        
        return {
            "easy": [s for s in scenarios if s.sophistication < 0.4],
            "medium": [s for s in scenarios if 0.4 <= s.sophistication < 0.7],
            "hard": [s for s in scenarios if s.sophistication >= 0.7],
        }

    @staticmethod
    def statistical_benchmark_set(
        num_scenarios: int = 100,
        rng_seed: int = 42,
    ) -> List[AttackScenarioDefinition]:
        """
        Generate a statistically representative benchmark set
        by sampling and parameterizing attack scenarios.
        """
        rng = np.random.RandomState(rng_seed)
        base_scenarios = ScenarioGenerator.single_attack_scenarios()
        
        benchmarks = []
        for i in range(num_scenarios):
            base = base_scenarios[i % len(base_scenarios)]
            
            # Add random variation to base scenarios
            scenario = AttackScenarioDefinition(
                name=f"{base.name}_{i:03d}",
                attack_type=base.attack_type,
                description=base.description,
                base_risk=float(np.clip(base.base_risk + rng.normal(0, 0.1), 0.0, 1.0)),
                stealth=float(np.clip(base.stealth + rng.normal(0, 0.1), 0.0, 1.0)),
                sophistication=float(np.clip(base.sophistication + rng.normal(0, 0.1), 0.0, 1.0)),
                initial_trust=float(np.clip(base.initial_trust + rng.normal(0, 0.08), 0.0, 1.0)),
                initial_confidence=float(np.clip(base.initial_confidence + rng.normal(0, 0.08), 0.0, 1.0)),
                trust_damage_on_success=float(np.clip(base.trust_damage_on_success + rng.normal(0, 0.1), 0.0, 1.0)),
                confidence_damage_on_success=float(np.clip(base.confidence_damage_on_success + rng.normal(0, 0.1), 0.0, 1.0)),
                detectable_signals=base.detectable_signals.copy(),
                evasion_tactics=base.evasion_tactics.copy(),
            )
            benchmarks.append(scenario)
        
        return benchmarks
