#!/usr/bin/env python3
"""
Trust Calculus Agent - Architectural Demo

Demonstrates:
1. EXISTING: Information Flow Control (IFC) layer with security labels
2. PLANNED: Dynamic Trust-to-Authority Calculus (Phase 1-13)

This demo showcases:
- How security labels work (Integrity/Confidentiality lattices)
- How the new trust layer will work with risk, confidence, and evidence
- The authority decision flow
"""

import sys
from pathlib import Path
from enum import Enum
from dataclasses import dataclass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from trustcalc.core.labels import (
    Integrity,
    Confidentiality,
    SecurityLabel,
)

# ============================================================================
# PART 1: EXISTING - Information Flow Control Layer
# ============================================================================

def demo_ifc_layer():
    """Demonstrate the existing IFC (Information Flow Control) layer."""
    
    print("\n" + "="*70)
    print("PART 1: EXISTING INFRASTRUCTURE - IFC Layer")
    print("="*70)
    print()
    
    print("1️⃣  Security Label Model:")
    print("-" * 70)
    print()
    print("Integrity Levels (trustworthiness):")
    for level in Integrity:
        print(f"  • {level.name:12} = {level.value}  (trusted={level.trusted})")
    print()
    
    print("Confidentiality Levels (sensitivity):")
    for level in Confidentiality:
        print(f"  • {level.name:15} = {level.value}")
    print()
    
    # Example label
    print("2️⃣  Example: Security Label for 'sensitive internal document':")
    print("-" * 70)
    example_label = SecurityLabel(
        integrity=Integrity.HIGH,
        confidentiality=Confidentiality.CONFIDENTIAL,
    )
    example_label_topsecret = SecurityLabel(
        integrity=Integrity.VERIFIED,
        confidentiality=Confidentiality.TOP_SECRET,
    )
    print(f"  Integrity:       {example_label.integrity.name} (verified source)")
    print(f"  Confidentiality: {example_label.confidentiality.name} (sensitive)")
    print(f"  Can flow to top-secret? {example_label.can_flow_to(example_label_topsecret)}")
    print(f"    (Label flow is determined by lattice rules)")
    print()


# ============================================================================
# PART 2: PLANNED - Trust-to-Authority Calculus Architecture
# ============================================================================

class DecisionType(str, Enum):
    """Authority engine decision types."""
    ALLOW = "ALLOW"
    VERIFY = "VERIFY"
    RESTRICT = "RESTRICT"
    SANDBOX = "SANDBOX"
    DENY = "DENY"


@dataclass
class TrustSnapshot:
    """Snapshot of trust state (Phase 1 implementation preview)."""
    entity: str
    action: str
    trust: float  # [0, 1]
    confidence: float  # [0, 1]
    risk: float  # [0, 1]


@dataclass
class AuthorityDecision:
    """Authority engine output (Phase 4 implementation preview)."""
    decision: DecisionType
    explanation: str
    trust: float
    confidence: float
    risk: float


def demo_trust_calculus_architecture():
    """Demonstrate the planned Trust-to-Authority Calculus."""
    
    print("\n" + "="*70)
    print("PART 2: PLANNED - Trust-to-Authority Calculus Layer")
    print("="*70)
    print()
    
    print("Architecture Overview:")
    print("-" * 70)
    print("""
    Proposed Action (from LLM Agent)
              ↓
    ┌─────────────────────────────┐
    │ TRUST CALCULUS LAYER        │
    │                             │
    │ • Trust: Bayesian model     │
    │ • Confidence: Evidence qty  │
    │ • Risk: Action + context    │
    │ • Evidence: Observations    │
    │ • Provenance: Chain links   │
    │ • Trajectory: Event log     │
    │ • Delegation: Attenuation   │
    └─────────────────────────────┘
              ↓
    ┌─────────────────────────────┐
    │ AUTHORITY ENGINE            │
    │                             │
    │ Decision: [ALLOW/VERIFY/   │
    │            RESTRICT/SANDBOX│
    │            /DENY]          │
    │ Explanation: Auditable     │
    └─────────────────────────────┘
              ↓
    ┌─────────────────────────────┐
    │ IFC ENFORCEMENT LAYER       │
    │ (Existing)                  │
    │ • Information flow rules    │
    │ • Compartment isolation     │
    └─────────────────────────────┘
              ↓
    ┌─────────────────────────────┐
    │ TOOL EXECUTION              │
    │ (Sandboxed, Monitored)      │
    └─────────────────────────────┘
              ↓
    ┌─────────────────────────────┐
    │ EVIDENCE GENERATION         │
    │ • Success/Failure           │
    │ • Behavioral anomaly        │
    │ • Security events           │
    └─────────────────────────────┘
              ↓
    TRUST UPDATE (loop)
    """)
    print()


def demo_trust_confidence_separation():
    """Demonstrate why trust and confidence are separate."""
    
    print("\n" + "="*70)
    print("KEY INSIGHT #1: Trust ≠ Confidence")
    print("="*70)
    print()
    
    print("Scenario: Two tools with different trust profiles")
    print("-" * 70)
    print()
    
    tool_a = TrustSnapshot(
        entity="Tool A (WebSearcher)",
        action="DatabaseRead",
        trust=0.95,
        confidence=0.15,  # LIMITED EVIDENCE
        risk=0.40,
    )
    
    tool_b = TrustSnapshot(
        entity="Tool B (DatabaseWrapper)",
        action="DatabaseRead",
        trust=0.90,
        confidence=0.99,  # EXTENSIVE EVIDENCE
        risk=0.40,
    )
    
    print(f"{tool_a.entity}:")
    print(f"  Trust:      {tool_a.trust:.2f} (seems trustworthy)")
    print(f"  Confidence: {tool_a.confidence:.2f} (but LIMITED evidence)")
    print(f"  Risk:       {tool_a.risk:.2f}")
    print()
    
    print(f"{tool_b.entity}:")
    print(f"  Trust:      {tool_b.trust:.2f} (seems trustworthy)")
    print(f"  Confidence: {tool_b.confidence:.2f} (EXTENSIVE evidence)")
    print(f"  Risk:       {tool_b.risk:.2f}")
    print()
    
    print("DECISION:")
    print("-" * 70)
    print("Tool A (0.95 trust, 0.15 confidence): SANDBOX")
    print("  Reason: Insufficient evidence despite high trust estimate")
    print()
    print("Tool B (0.90 trust, 0.99 confidence): ALLOW")
    print("  Reason: Well-founded trust from extensive evidence")
    print()
    print("💡 High trust with low confidence = unreliable guess (DENY high-risk)")
    print("💡 High trust with high confidence = well-founded (ALLOW)")
    print()


def demo_risk_orthogonality():
    """Demonstrate that risk is orthogonal to trust."""
    
    print("\n" + "="*70)
    print("KEY INSIGHT #2: Risk is Orthogonal to Trust")
    print("="*70)
    print()
    
    print("Risk-Trust Matrix:")
    print("-" * 70)
    print()
    
    actions = [
        ("WebSearch", 0.05),
        ("FileRead(public)", 0.10),
        ("FileRead(private)", 0.40),
        ("DatabaseWrite", 0.70),
        ("CodeExecution", 0.95),
    ]
    
    print("Action Risk Levels:")
    for action, risk in actions:
        bar_len = int(risk * 40)
        bar = "█" * bar_len + "░" * (40 - bar_len)
        print(f"  {action:20} {bar} {risk:.2f}")
    print()
    
    print("Key Principle:")
    print("-" * 70)
    print("Required Trust for Authorization = 0.5 + 0.5 * Risk")
    print()
    
    for action, risk in actions:
        required_trust = 0.5 + 0.5 * risk
        print(f"  {action:20} → requires trust ≥ {required_trust:.2f}")
    print()
    
    print("💡 HIGH TRUST DOES NOT REDUCE AUTHORIZATION BAR FOR HIGH-RISK ACTIONS")
    print("💡 Once authorized for action A, higher-risk action B requires")
    print("    proportionally higher trust")
    print()


def demo_authority_decisions():
    """Demonstrate authority engine decision logic."""
    
    print("\n" + "="*70)
    print("KEY INSIGHT #3: Authority Decision Types (5 Levels)")
    print("="*70)
    print()
    
    scenarios = [
        AuthorityDecision(
            decision=DecisionType.ALLOW,
            explanation="Entity is highly trusted, action is low-risk, " +
                       "no anomalies detected",
            trust=0.95,
            confidence=0.90,
            risk=0.15,
        ),
        AuthorityDecision(
            decision=DecisionType.VERIFY,
            explanation="Action is high-risk; execute but monitor and audit closely",
            trust=0.85,
            confidence=0.80,
            risk=0.75,
        ),
        AuthorityDecision(
            decision=DecisionType.RESTRICT,
            explanation="Provenance concerns detected; grant limited capability only",
            trust=0.70,
            confidence=0.65,
            risk=0.50,
        ),
        AuthorityDecision(
            decision=DecisionType.SANDBOX,
            explanation="Trust insufficient for requested action risk level; " +
                       "execute in isolated environment",
            trust=0.60,
            confidence=0.70,
            risk=0.60,
        ),
        AuthorityDecision(
            decision=DecisionType.DENY,
            explanation="Entity untrusted or evidence shows malicious behavior; " +
                       "action blocked",
            trust=0.30,
            confidence=0.85,
            risk=0.70,
        ),
    ]
    
    for i, decision in enumerate(scenarios, 1):
        print(f"{i}. Decision: {decision.decision.value}")
        print(f"   Trust: {decision.trust:.2f}, Confidence: {decision.confidence:.2f}, " +
              f"Risk: {decision.risk:.2f}")
        print(f"   Rationale: {decision.explanation}")
        print()


def demo_attack_defense():
    """Show how different attacks are defended against."""
    
    print("\n" + "="*70)
    print("KEY INSIGHT #4: Defense-in-Depth Against 12 Attacks")
    print("="*70)
    print()
    
    attacks = [
        ("1. Immediate Malicious", "IFC layer blocks direct unauthorized access"),
        ("2. Reputation Poisoning", "Risk monotonicity prevents trust escalation"),
        ("3. Hidden Trigger", "Trajectory anomaly detection on behavior shift"),
        ("4. Compromised Tool", "Behavioral profiling detects deviation from baseline"),
        ("5. Collusion", "Provenance tracking reveals evidence correlated sources"),
        ("6. Sybil/Reputation", "Correlated evidence discounting prevents self-inflation"),
        ("7. Delegation Attack", "Authority attenuation + scope validation"),
        ("8. Prompt Injection", "Context anomaly detection + IFC enforcement"),
        ("9. On-Off Attack", "Temporal pattern analysis detects recurring violations"),
        ("10. Authority Inflation", "Risk monotonicity enforcement"),
        ("11. Trust Inflation Loops", "Recommendation weighting + provenance"),
        ("12. Privilege via Intermediary", "Behavioral profiling + transitive limits"),
    ]
    
    print("Attack Scenarios & Defenses:")
    print("-" * 70)
    for attack, defense in attacks:
        print(f"\n{attack}")
        print(f"  🛡️  {defense}")
    
    print()
    print()
    print("📊 RESULT: Multiple defensive layers prevent most attacks")
    print()


def demo_implementation_phases():
    """Show the 13-phase implementation roadmap."""
    
    print("\n" + "="*70)
    print("IMPLEMENTATION ROADMAP: 13 Phases")
    print("="*70)
    print()
    
    phases = [
        ("0 [DONE]", "Architecture Planning", "✓ 4 design docs created"),
        ("1", "Trust State & Evidence", "TrustState, Evidence, Bayesian updater"),
        ("2", "Temporal Dynamics", "Decay, recovery, confidence evolution"),
        ("3", "Risk Model", "Risk calculation, context multipliers"),
        ("4", "Authority Engine", "Decision logic (ALLOW/VERIFY/SANDBOX/DENY)"),
        ("5", "Trajectory Analysis", "Event log, anomaly detection"),
        ("6", "Delegation", "Attenuation, scope, revocation"),
        ("7", "Provenance", "Correlated evidence detection, discounting"),
        ("8", "Attack Simulator", "12 attack scenarios + adaptive attacker"),
        ("9", "Baselines", "6 baseline systems for comparison"),
        ("10", "Experiments", "~420 baseline experiments"),
        ("11", "Ablations", "~288 ablation studies"),
        ("12", "Properties", "Formal property tests"),
        ("13", "Integration", "Polish, benchmarks, final write-up"),
    ]
    
    for phase_num, title, description in phases:
        status = "✓" if "DONE" in phase_num else "→"
        print(f"{status} {phase_num:8} | {title:20} | {description}")
    
    print()
    print()


def demo_success_metrics():
    """Show what success looks like."""
    
    print("\n" + "="*70)
    print("SUCCESS CRITERIA (End of Phase 13)")
    print("="*70)
    print()
    
    print("Security Metrics:")
    print("-" * 70)
    metrics = [
        ("Attack Success Rate", "< 5%", "vs. 100% for no security"),
        ("Time to Detection", "< 60 sec", "how fast do we catch attacks?"),
        ("False Negatives", "0", "no missed attacks"),
        ("Privilege Escalation Blocked", "> 95%", "core defense property"),
    ]
    
    for metric, target, note in metrics:
        print(f"  • {metric:30} {target:10}  ({note})")
    print()
    
    print("Utility Metrics:")
    print("-" * 70)
    utility = [
        ("Task Success Rate", "> 95%", "don't block benign tasks"),
        ("False Positive Rate", "< 5%", "avoid over-blocking"),
        ("Authorization Latency p99", "< 200 ms", "reasonable overhead"),
        ("System Throughput", "> 100 calls/s", "adequate performance"),
    ]
    
    for metric, target, note in utility:
        print(f"  • {metric:30} {target:10}  ({note})")
    print()
    
    print("Research Metrics:")
    print("-" * 70)
    research = [
        ("Improvement vs. Baselines", "Significant (p<0.05)", "statistically rigorous"),
        ("All Ablations Matter", "> 8/8 components", "no dead code"),
        ("On Pareto Frontier", "Yes", "can't improve without tradeoffs"),
    ]
    
    for metric, target, note in research:
        print(f"  • {metric:30} {target:20}  ({note})")
    print()


# ============================================================================
# MAIN DEMO
# ============================================================================

def main():
    """Run the complete trust calculus demo."""
    
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  Dynamic Trust-to-Authority Calculus for Secure LLM Agents".center(68) + "║")
    print("║" + "  B.Tech Research Project - Architectural Demo".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    print()
    
    # Run demo sections
    demo_ifc_layer()
    demo_trust_calculus_architecture()
    demo_trust_confidence_separation()
    demo_risk_orthogonality()
    demo_authority_decisions()
    demo_attack_defense()
    demo_implementation_phases()
    demo_success_metrics()
    
    # Summary
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print()
    print("1. READ: /docs/RESEARCH_PLANNING_SUMMARY.md (quick overview)")
    print("2. REVIEW: /docs/RESEARCH_PROPOSAL.md (detailed architecture)")
    print("3. VALIDATE: /docs/TRUST_MODEL.md (mathematical foundations)")
    print("4. UNDERSTAND: /docs/THREAT_MODEL.md (12 attacks + defenses)")
    print("5. PLAN: /docs/EXPERIMENT_PLAN.md (evaluation strategy)")
    print()
    print("6. DO LITERATURE REVIEW (compare with existing work)")
    print("7. GET ADVISOR FEEDBACK (validate research direction)")
    print("8. BEGIN PHASE 1 (implement trust state + evidence)")
    print()
    print("📊 Total planning: 5 documents, ~71 KB of design docs")
    print("📅 Implementation: 13 weeks, ~15K-20K LOC")
    print("🧪 Evaluation: ~1000 experiments across 7 baselines")
    print()
    print("="*70)
    print()


if __name__ == "__main__":
    main()
