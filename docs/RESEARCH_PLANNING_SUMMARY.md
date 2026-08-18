# Architecture and Research Planning Summary

**Dynamic Trust-to-Authority Calculus for Secure Autonomous LLM Agents**

---

## Overview

You now have a comprehensive research architecture document set:

1. **RESEARCH_PROPOSAL.md** – High-level research direction, system architecture, implementation phases
2. **TRUST_MODEL.md** – Mathematical foundation using Beta-Binomial model, confidence tracking, temporal dynamics
3. **THREAT_MODEL.md** – 12 attack scenarios with detailed analysis of each attack and defense mechanisms
4. **EXPERIMENT_PLAN.md** – Reproducible evaluation framework with baselines, metrics, and ~1000 experiments

---

## Key Architectural Decisions

### 1. Two-Layer Design

**IFC Layer (Information Flow Control)** – EXISTING
- Security labels (Integrity/Confidentiality)
- Lattice-based flow rules
- Compartment isolation
- Blocks obvious data exfiltration

**Trust Layer (NEW) – Dynamic Trust-to-Authority Calculus**
- Separate trust state from IFC labels
- Confidence explicitly tracked (not just trust)
- Evidence aggregation with provenance
- Temporal dynamics (decay, recovery)
- Risk model (separate from trust)
- Authority engine (deterministic, auditable)
- Trajectory analysis for anomaly detection
- Delegation with attenuation
- Correlated evidence discounting

These layers work **together** but are **conceptually distinct**.

### 2. Trust Model: Beta-Binomial Framework

**Why Beta-Binomial?**
- Principled: Founded in Bayesian probability
- Separates trust from confidence
- Handles sparse evidence naturally
- Handles evidence of mixed strength
- Extensive literature and calibration methods
- Avoids arbitrary score aggregations

**Key Equations:**

$$T(e,a,c,t) = E[\theta] = \frac{\alpha(t)}{\alpha(t) + \beta(t)}$$

$$C(e,a,c,t) = \frac{\alpha(t) + \beta(t)}{N_{\text{calibration}}}$$

$$T_{\text{required}}(R) = 0.5 + 0.5 \times R$$

### 3. Risk Orthogonality

**Critical Property:** Risk is NOT the inverse of trust.

- High trust in low-risk actions ≠ authorization for high-risk actions
- High-risk actions have higher minimum trust requirement
- Risk monotonicity enforced: as risk increases, authorization bar rises

### 4. Uncertainty Explicitly Handled

**Trust alone is insufficient:**

| Trust | Confidence | Interpretation | Decision |
|-------|-----------|-----------------|----------|
| 0.95 | 0.15 | Optimistic guess | DENY high-risk (insufficient evidence) |
| 0.95 | 0.95 | Well-founded | ALLOW |
| 0.30 | 0.95 | Well-founded distrust | DENY |
| 0.50 | 0.05 | Complete ignorance | DENY anything risky |

### 5. Provenance and Evidence Independence

**Problem:** Two pieces of evidence from correlated sources are NOT independent.

**Solution:**
- Track evidence provenance (chain of custody)
- Detect common ancestors
- Apply discount factors to correlated evidence
- Defends against Sybil attacks and reputation poisoning

### 6. Delegation with Attenuation

**Principle:** Authority cannot flow downward at full strength.

$$\text{Auth}_{\text{eff}}(d) = \text{Auth}_0 \times e^{-\lambda \cdot d}$$

- Each level of delegation attenuates by ~30%
- Scope must not expand in re-delegation
- Revocation cascades on compromise

### 7. Trajectory-Aware Analysis

**The event log is central:**
- Every security-relevant action recorded
- Evidence generation from observations
- Anomaly detection on behavior patterns
- Pattern recognition (privilege escalation, on-off attacks)
- Trust state evolution tracked over time

---

## 12 Attack Scenarios (Summary)

| # | Attack | Threat Level | Key Defense |
|---|--------|--------------|------------|
| 1 | Immediate Malicious | LOW | IFC + Evidence |
| 2 | Reputation Poisoning | MEDIUM | Risk Monotonicity |
| 3 | Hidden Trigger | HIGH | Trajectory Anomaly Detection |
| 4 | Compromised Tool | HIGH | Behavioral Profiling |
| 5 | Collusion | VERY_HIGH | Provenance Independence Checking |
| 6 | Sybil/Reputation | HIGH | Evidence Correlated Discounting |
| 7 | Delegation Attack | MEDIUM-HIGH | Attenuation + Scope Validation |
| 8 | Prompt Injection | MEDIUM | Context Anomaly Detection |
| 9 | On-Off Attack | MEDIUM | Temporal Pattern Analysis |
| 10 | Authority Inflation | MEDIUM | Risk Monotonicity |
| 11 | Trust Inflation Loops | MEDIUM | Recommendation Weighting |
| 12 | Privilege via Intermediary | HIGH | Behavioral Profiling |

**Defense-in-depth approach:** Most attacks require multiple defensive layers.

---

## Experimental Framework

### Baselines (7 systems)

1. **No Security** – Everything allowed (strawman)
2. **Static Policy** – Pre-defined rules, no adaptation
3. **Simple Score** – Single trust value, linear updates
4. **Simple Threshold** – If trust > 0.7, allow
5. **Risk-Based** – Trust vs. risk threshold, no confidence
6. **Trajectory-Only** – Anomaly detection on behavior alone
7. **Proposed** – Full dynamic trust-to-authority calculus

### Experiments (~1000 total)

- **Baseline Comparisons:** 12 attacks × 7 baselines × 5 seeds = 420
- **Ablations:** 8 components × 12 attacks × 3 seeds = 288
- **Robustness:** 5 parameters × ~5 values × 6 attacks × 2 seeds ≈ 300

### Key Metrics

**Security:**
- Attack success rate (target: <5%)
- Time to detection (target: <60 sec)
- False negatives (target: 0)

**Utility:**
- Task success rate (target: >95%)
- False positive rate (target: <5%)
- Authorization latency p99 (target: <200ms)

**Composite:**
- Pareto frontier analysis (tradeoff between security and utility)

---

## Implementation Roadmap

### Phase 0: CURRENT ✓
- [x] Inspect existing repository
- [x] Create research architecture
- [x] Design trust model
- [x] Design threat model
- [x] Plan experiments

### Phase 1: Trust State & Evidence (Week 1-2)
- [ ] `src/trustcalc/trust/state.py` – TrustState dataclass
- [ ] `src/trustcalc/trust/evidence.py` – Evidence model
- [ ] `src/trustcalc/trust/updater.py` – Bayesian updates
- [ ] Unit tests for trust/evidence

### Phase 2: Temporal Dynamics (Week 2-3)
- [ ] `src/trustcalc/trust/temporal.py` – Decay, recovery
- [ ] Temporal property tests

### Phase 3: Risk & Context (Week 3)
- [ ] `src/trustcalc/risk/model.py` – Risk quantification
- [ ] Risk thresholds and context multipliers

### Phase 4: Authority Engine (Week 4)
- [ ] `src/trustcalc/authority/engine.py` – Decision logic
- [ ] Integration with IFC layer

### Phase 5: Trajectory Analysis (Week 5)
- [ ] `src/trustcalc/trust/trajectory.py` – Event logging
- [ ] Anomaly detection

### Phase 6: Delegation (Week 5-6)
- [ ] `src/trustcalc/trust/delegation.py` – Delegation model

### Phase 7: Provenance Enhancement (Week 6)
- [ ] `src/trustcalc/provenance/checker.py` – Correlated evidence detection
- [ ] Evidence discounting

### Phase 8: Attack Simulator (Week 7-8)
- [ ] `src/trustcalc/attacks/adaptive_attacker.py` – Stateful attacker framework
- [ ] Implement 12 attack scenarios

### Phase 9: Baselines (Week 8-9)
- [ ] `src/trustcalc/evaluation/baselines.py` – 6 baseline systems

### Phase 10: Experiments (Week 9-10)
- [ ] `experiments/run_experiment.py` – Experiment runner
- [ ] Metrics collection

### Phase 11: Ablation Studies (Week 10-11)
- [ ] Ablation harness

### Phase 12: Formal Properties (Week 11-12)
- [ ] Property tests

### Phase 13: Integration & Polish (Week 12-13)
- [ ] Integration with benchmarks
- [ ] Results finalization
- [ ] Research write-up

---

## Critical Design Principles

### 1. Interpretability Over Complexity
- Use simple, explainable models
- Avoid ML models for deterministic security decisions
- Every decision has a documented rationale

### 2. Conservative Defaults
- When uncertain, default to safe behavior
- Never silently fail open on security decisions
- Confidence explicitly gates high-risk actions

### 3. Transparency and Auditability
- Log every security-relevant event
- All decisions include explanations
- Provenance tracked for every piece of evidence

### 4. Separation of Concerns
- Trust layer separate from IFC layer
- Authority engine independent from LLM agent
- Risk model independent from trust model

### 5. Reproducibility and Rigorous Evaluation
- Fixed random seeds for all experiments
- Configuration-driven (no hard-coded parameters)
- Statistical significance testing
- Ablation studies show component contribution

### 6. Honest About Limitations
- No black-box decisions
- All thresholds justified and calibrated
- Known attack vectors documented
- Adaptive attacker simulations tested

---

## Research Questions to Answer

### Primary
1. **Is the dynamic trust-to-authority calculus genuinely novel?**
   - Literature review: Compare with Trust-No-Tool, AgentTrust, VIGIL, ToolSafe, others
   - Identify what is novel (hypothesis: uncertainty + provenance + trajectory combination)

2. **Does the system actually defend against sophisticated attacks?**
   - Ablations: Which components are necessary?
   - Attacks: What percentage are detected/blocked?

3. **What is the security-utility tradeoff?**
   - How much utility is sacrificed for security?
   - Is it acceptable?

### Secondary
1. What is the optimal confidence threshold?
2. How should decay rates be calibrated?
3. What evidence strength scales are realistic?
4. Can adaptive attackers beat the system?
5. How does performance scale with entity count?

---

## Next Immediate Steps

### Before Implementation:

1. **Literature Review**
   - Read: Trust-No-Tool, AgentDojo, AgentTrust, VIGIL, ToolSafe, ShieldMCP, SkillGuard, Task Shield
   - Document: What each paper does, how it differs from this approach
   - Conclusion: Is this approach novel? What should we change?

2. **Review Existing Code**
   - Understand: Current IFC implementation
   - Clarify: How will trust layer integrate with policy engine?
   - Plan: API boundaries between IFC and trust layers

3. **Validate Math**
   - Beta-Binomial: Is this the right model?
   - Alternatives: Dempster-Shafer, Credibility theory?
   - Decision: Make it or confirm it's right

4. **Get Feedback**
   - Advisor review of RESEARCH_PROPOSAL.md
   - Challenge assumptions: Which parts are unsupported?
   - Refine: Adjust architecture if needed

### When Ready to Code:

1. **Start with Phase 1**
   - Implement TrustState dataclass
   - Implement Evidence model
   - Implement Bayesian updater
   - Write unit tests (TDD approach)

2. **Test incrementally**
   - Don't build entire system first
   - Test each component as built
   - Integrate progressively

3. **Follow the plan**
   - Don't skip phases
   - Complete phase N before starting phase N+1
   - Update documentation as you build

---

## Repository Status

**Current State:**
- IFC layer: ✓ Implemented
- Policy engine: ✓ Implemented
- Tools & agents: ✓ Implemented
- Evaluation framework: ✓ Partial

**To Be Added:**
- Trust state and evidence model
- Bayesian trust updates
- Temporal dynamics
- Risk model
- Authority engine
- Trajectory analysis
- Delegation model
- Provenance enhancements
- Attack simulator (comprehensive)
- Baseline systems
- Comprehensive experiments
- Ablation studies
- Formal property tests

**Total LOC estimate:** ~15,000-20,000 lines across all components

---

## Success Metrics (Final Evaluation)

### Code Quality
- [ ] All components have unit tests (>80% coverage)
- [ ] All public APIs documented
- [ ] Code is readable and maintainable
- [ ] No technical debt (or documented)

### Research Quality
- [ ] Contribution is novel (vs. literature)
- [ ] Math is principled and justified
- [ ] Experiments are rigorous and reproducible
- [ ] Results are honest (including limitations)

### System Quality
- [ ] Defends against 12 attack scenarios
- [ ] <5% attack success rate on average
- [ ] <5% false positive rate
- [ ] Within 2x latency of no-security baseline
- [ ] Ablations show all components matter

### Documentation Quality
- [ ] Clear explanation of research contribution
- [ ] Reproducible experiment instructions
- [ ] Threat model comprehensively analyzed
- [ ] Architecture clearly documented

---

## Key Files Created

All in `/docs/`:

1. **RESEARCH_PROPOSAL.md** (22 KB, 800+ lines)
   - High-level architecture
   - 22 detailed sections covering design principles
   - Implementation phases with milestones

2. **TRUST_MODEL.md** (18 KB, 600+ lines)
   - Mathematical foundations
   - Beta-Binomial model with equations
   - Confidence and evidence definitions
   - Temporal dynamics formulas
   - Calibration guidelines

3. **THREAT_MODEL.md** (15 KB, 500+ lines)
   - 12 attack scenarios with detailed analysis
   - Attacker capabilities and constraints
   - Defense mechanisms for each attack
   - Coverage analysis and test cases

4. **EXPERIMENT_PLAN.md** (16 KB, 600+ lines)
   - Experimental design and setup
   - 7 baseline systems
   - ~1000 experiment matrix
   - Metrics and statistical analysis
   - Reproducibility checklist

**Total:** ~71 KB of research planning documentation

---

## Final Thought

This is not a system to be "built quickly."

This is a research contribution that requires:
- **Principled design** (not ad-hoc features)
- **Rigorous evaluation** (not cherry-picked results)
- **Honest about tradeoffs** (not strawman baselines)
- **Grounded in math** (not black-box decisions)
- **Defensible novelty** (not incremental tweaks)

Take the time to:
1. Review literature thoroughly
2. Validate mathematical foundations
3. Implement components carefully
4. Test extensively
5. Analyze results honestly

The goal is not to produce the largest codebase, but to produce the most defensible research contribution on the core question:

**"Given everything that has happened so far, how much authority should this entity have to perform THIS action in THIS context?"**

Good luck with the research project!

---

**Created:** 2026-08-18  
**Status:** Architecture and planning complete. Ready for code implementation and literature review.
