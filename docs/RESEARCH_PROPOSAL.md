# Research Proposal: Dynamic Trust-to-Authority Calculus for Secure Autonomous LLM Agents

**B.Tech Research Project**  
**Status:** Phase 0 - Architecture & Planning  
**Date:** 2026-08-18

---

## 1. Core Research Question

**"Given everything that has happened so far, how much authority should this entity have to perform THIS action in THIS context?"**

This research proposes a **runtime trust-to-authority calculus** that:

1. Tracks trust, confidence, and evidence separately
2. Updates dynamically based on behavioral observations
3. Contextualizes authority decisions by action risk and interaction history
4. Resists adversarial trust manipulation
5. Supports delegation with principled attenuation
6. Analyzes interaction trajectories to detect anomalies
7. Maintains transparent provenance for all trust decisions

---

## 2. Hypothesized Contribution

Not merely a "trust score" for tools.

**Instead:** A principled, uncertainty-aware, provenance-aware, trajectory-aware dynamic calculus that converts trust observations into context- and risk-sensitive authority decisions, with formal defenses against manipulation.

Specifically:
- Trust ≠ Authority
- High trust in low-risk actions ≠ authorization for high-risk actions  
- Evidence from correlated sources should not be treated as independent
- Low-confidence trust should conservatively restrict high-risk authorization
- Delegation should attenuate authority by default
- Trajectories should inform anomaly detection

---

## 3. Current Repository State

**Existing Infrastructure:**
- Information Flow Control (IFC) layer with security labels
- Integrity/Confidentiality lattices  
- Provenance graph (append-only)
- Policy engine for rule-based authorization
- Tool/agent framework
- Basic attack implementations

**Key Gaps:**
- No explicit trust state separate from IFC labels
- No confidence/uncertainty model
- No evidence aggregation
- No temporal dynamics (trust decay, recovery)
- No risk model
- No action-specific trust context
- No delegation or authority attenuation
- No trajectory analysis framework
- No comprehensive adaptive attack simulator
- No baseline systems or ablation studies

---

## 4. Proposed System Architecture

### 4.1 Layered Design

```
┌─────────────────────────────────────┐
│   USER / EXTERNAL SYSTEM            │
└────────────────┬────────────────────┘
                 │
┌─────────────────▼────────────────────┐
│   LLM AGENT                         │
│   (Proposes Actions)                │
└────────────────┬────────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │ PROPOSED ACTION│
        │  (Entity,      │
        │   ToolCall,    │
        │   Args)        │
        └────────┬───────┘
                 │
                 ▼
    ┌────────────────────────────┐
    │ TRUST CALCULUS LAYER       │
    │                            │
    │ ┌──────────────────────┐   │
    │ │ Trust State         │   │
    │ │ (entity, action, ctx)   │
    │ │ - trust (0..1)      │   │
    │ │ - confidence (0..1) │   │
    │ │ - evidence []       │   │
    │ │ - provenance        │   │
    │ └──────────────────────┘   │
    │                            │
    │ ┌──────────────────────┐   │
    │ │ Risk Model          │   │
    │ │ - action_risk       │   │
    │ │ - context_risk      │   │
    │ │ - sensitivity       │   │
    │ └──────────────────────┘   │
    │                            │
    │ ┌──────────────────────┐   │
    │ │ Trajectory Analysis │   │
    │ │ - event_log         │   │
    │ │ - anomaly_scores    │   │
    │ │ - pattern_analysis  │   │
    │ └──────────────────────┘   │
    │                            │
    │ ┌──────────────────────┐   │
    │ │ Delegation Model    │   │
    │ │ - delegation_chain  │   │
    │ │ - attenuation       │   │
    │ │ - scope             │   │
    │ └──────────────────────┘   │
    └────────────┬───────────────┘
                 │
                 ▼
    ┌────────────────────────────┐
    │ AUTHORITY ENGINE           │
    │                            │
    │  Input: (trust, conf,      │
    │          risk, context,    │
    │          history, traj)    │
    │                            │
    │  Decision:                 │
    │  - ALLOW                   │
    │  - VERIFY                  │
    │  - RESTRICT                │
    │  - SANDBOX                 │
    │  - DENY                    │
    │                            │
    │  + Explanation             │
    │  + Anomaly flags           │
    │  + Provenance warnings     │
    └────────────┬───────────────┘
                 │
                 ▼
    ┌────────────────────────────┐
    │ IFC ENFORCEMENT LAYER      │
    │ (Existing)                 │
    │ - SecurityLabel checks     │
    │ - Flow rules               │
    │ - Compartment isolation    │
    └────────────┬───────────────┘
                 │
                 ▼
    ┌────────────────────────────┐
    │ SANDBOXED TOOL EXECUTION   │
    │ - Monitored execution      │
    │ - Observed outcome         │
    │ - Behavior recording       │
    └────────────┬───────────────┘
                 │
                 ▼
    ┌────────────────────────────┐
    │ EVIDENCE GENERATION        │
    │ - Success/Failure          │
    │ - Behavioral anomaly       │
    │ - Security event           │
    │ - Performance              │
    │ - Provenance               │
    └────────────┬───────────────┘
                 │
                 ▼
    ┌────────────────────────────┐
    │ TRUST UPDATE               │
    │ - Bayesian update          │
    │ - Confidence adjustment    │
    │ - New trust_state          │
    └────────────┬───────────────┘
                 │
                 ▼
        ┌────────────────┐
        │ NEXT ITERATION │
        │ (Loop)         │
        └────────────────┘
```

### 4.2 Key Distinctions from Current System

| Aspect | Current IFC Layer | Trust-to-Authority Layer (NEW) |
|--------|------------------|-------------------------------|
| **Primary Unit** | Information flows | Trust decisions |
| **Labels** | Integrity/Confidentiality | (Not labels - structured state) |
| **Scope** | Data properties | Entity + Action + Context + Time |
| **Dynamics** | Static per labeled value | Evolves with observations |
| **Confidence** | Not represented | Explicit (0..1) |
| **Evidence** | Implicitly in labels | Explicit, aggregated, weighted |
| **Provenance** | Graph of data origins | Graph of trust evidence |
| **Adaptation** | Policy rules only | Trust Bayesian updates + risk |
| **Decision Model** | Lattice-based flow | Authority engine |
| **Uncertainty** | No mechanism | Separate from trust |

---

## 5. Trust State Definition

### 5.1 Structured Trust State

```
TrustState(
    entity_id: str,
    action: str,
    context: str,
    time: datetime
) = {
    trust: float [0..1],                    # Core trust value
    confidence: float [0..1],               # Certainty in trust estimate
    evidence: List[Evidence],               # Supporting observations
    provenance: ProvenanceGraph,            # Evidence origin tracking
    temporal_state: TemporalBehavior,       # Decay, recovery curves
    behavioral_state: BehavioralProfile,    # History of actions
    risk_assessment: RiskProfile,           # Action + context risk
    delegation_state: DelegationChain,      # Attenuation info
}
```

### 5.2 Trust vs. Confidence

**Trust:** The degree to which we believe an entity will behave benignly in a specific action/context.

**Confidence:** The degree to which we believe our trust estimate is accurate based on evidence.

**Example:**
```
Tool A:
  trust = 0.95       (seems trustworthy)
  confidence = 0.15  (but little evidence)

Tool B:
  trust = 0.90       (seems trustworthy)
  confidence = 0.99  (and well-evidenced)

→ Tool B should be preferred for high-risk actions
```

### 5.3 Trust Models (Candidate)

**Option 1: Beta-Binomial Model**
- Trust as expected value of Beta distribution: $E[\theta] = \frac{\alpha}{\alpha + \beta}$
- Confidence as concentration: $\text{Conf} = \alpha + \beta$
- Pros: Principled Bayesian, well-studied, handles sparse evidence
- Cons: Symmetric priors may not fit domain

**Option 2: Belief Functions (Dempster-Shafer)**
- Decompose {Trust, Doubt, Ignorance}
- Pros: Explicitly represents ignorance
- Cons: More complex, harder to calibrate

**Option 3: Credibility Theory**
- Combine multiple evidence sources with credibility weights
- Pros: Handles correlated evidence naturally
- Cons: Requires careful weight calibration

**Decision:** Start with Beta-Binomial (Bayesian) because:
- Principled and well-understood
- Naturally handles evidence accumulation
- Separates trust from confidence clearly
- Standard in reputation systems literature

---

## 6. Evidence Model

### 6.1 Evidence Structure

```
Evidence(
    source: str,                       # Who generated this evidence
    timestamp: datetime,                # When
    type: EvidenceType,                # What kind (see below)
    strength: float [0..1],            # How strong (0=weak, 1=definitive)
    reliability: float [0..1],         # How trustworthy the source
    affected_entity: str,              # Which entity
    affected_action: str,              # Which action context
    observation: dict,                 # Details
    provenance_path: List[UUID],      # Chain of trust
)
```

### 6.2 Evidence Types

1. **Behavioral:**
   - SuccessfulAction: Action completed as expected
   - FailedAction: Action failed unexpectedly
   - AnomalousAction: Unusual parameters or timing
   - UnauthorizedAttempt: Action blocked by policy

2. **Security:**
   - MaliciousBehavior: Detected attack/malice
   - SecurityAnomaly: Unusual pattern detected
   - PolicyViolation: Broke IFC/policy rules
   - CompromisedIndicator: Signs of compromise

3. **Third-Party:**
   - AgentRecommendation: Another entity recommends
   - HumanVerification: Human confirmed trustworthiness
   - ExternalRating: Outside service provided rating
   - HistoricalRecord: Public reputation data

4. **Observational:**
   - PerformanceMetric: Speed/efficiency/quality
   - ResourceUsage: Memory/CPU/network consumption
   - ErrorRate: Frequency of errors
   - LatencyProfile: Response timing

---

## 7. Risk Model

### 7.1 Action Risk

Risk is NOT the inverse of trust. It's orthogonal.

```
ActionRisk(
    action: str,
    parameters: dict,
    context: str,
    sensitivity: SensitivityLevel,
) → float [0..1]
```

**Risk Levels (Examples):**
- WebSearch: LOW (0.1)
- FileRead(public): LOW (0.1)  
- FileRead(private): MEDIUM (0.5)
- DatabaseWrite: HIGH (0.8)
- CodeExecution: VERY_HIGH (0.95)
- ExternalAPI(payment): VERY_HIGH (0.95)

**Property:** Risk must NOT be reduced by high trust alone.

**Principle:** If risk increases while trust stays constant, authorization should not become easier.

### 7.2 Context Risk

The context amplifies or reduces action risk:

- **Benign context:** Normal operation, expected timing
- **Suspicious context:** Unusual parameters, rapid succession, anomalous trajectory
- **High-stakes context:** Important data, critical systems, financial impact

---

## 8. Temporal Dynamics

Trust evolves over time.

### 8.1 Trust Decay

Without new evidence, trust gradually decays:

$$T(t) = T_0 \cdot e^{-\lambda t}$$

Where:
- $T_0$ = initial trust
- $\lambda$ = decay rate (configurable per entity/action)
- $t$ = time elapsed

**Intuition:** Silence is not endorsement. Lack of evidence to the contrary doesn't preserve trust indefinitely.

### 8.2 Trust Recovery

After negative evidence → positive evidence, trust can recover, but conservatively.

$$T_{\text{recovered}} = \text{min}(T_{\text{pre-incident}}, T_{\text{new}} \cdot \text{recovery\_factor})$$

**Intuition:** Once burned, trust is harder to rebuild.

### 8.3 Confidence Dynamics

Confidence increases with positive evidence, decreases rapidly with negative evidence:

$$\text{Conf}(t+1) = \begin{cases}
\text{Conf}(t) + \Delta_{\text{pos}} & \text{if positive evidence} \\
\text{Conf}(t) \times \text{decay\_factor} & \text{if negative evidence} \\
\text{Conf}(t) \times e^{-\lambda t} & \text{otherwise}
\end{cases}$$

---

## 9. Authority Engine

The authority engine makes final access control decisions.

### 9.1 Decision Types

| Decision | Meaning |
|----------|---------|
| **ALLOW** | Execute tool unrestricted |
| **VERIFY** | Execute, but record closely; prepare to audit |
| **RESTRICT** | Execute with restrictions (e.g., quota, limited scope) |
| **SANDBOX** | Execute in isolated environment, monitor output |
| **DENY** | Reject the action entirely |

### 9.2 Decision Logic (Pseudocode)

```
def authorize(entity, action, context, trust_state, risk):
    trust = trust_state.trust
    conf = trust_state.confidence
    anomalies = trajectory_analyzer.detect(trust_state)
    provenance_warnings = evidence_checker.check_independence(trust_state)
    
    # Conservatism principle
    if conf < MIN_CONFIDENCE_THRESHOLD:
        if risk > MEDIUM:
            return DENY_with_explanation(
                reason="Insufficient evidence for high-risk action"
            )
        return VERIFY_with_explanation()
    
    # Risk monotonicity principle
    required_trust_for_risk = calculate_threshold(risk)
    if trust < required_trust_for_risk:
        return SANDBOX_with_explanation()
    
    # Anomaly checking
    if anomalies.severity > THRESHOLD:
        return VERIFY_or_RESTRICT_with_explanation()
    
    # Provenance checking
    if provenance_warnings.correlated_evidence:
        effective_trust = apply_provenance_discount(trust)
        if effective_trust < required_trust_for_risk:
            return RESTRICT_with_explanation()
    
    # Delegation checking
    delegation_discount = authority_loss_from_delegation(trust_state)
    effective_auth = trust - delegation_discount
    if effective_auth < required_trust_for_risk:
        return SANDBOX_with_explanation()
    
    # Default to least permissive sufficient decision
    if risk > HIGH:
        return VERIFY_with_explanation()
    
    return ALLOW_with_explanation()
```

### 9.3 Decision Explanation

Every decision must include:
```
AuthorityDecision(
    decision: DecisionType,
    explanation: str,                  # Human-readable rationale
    trust: float,                      # Trust value used
    confidence: float,                 # Confidence used
    risk: float,                       # Risk level
    anomalies: List[str],              # Detected anomalies
    provenance_warnings: List[str],    # Provenance concerns
    decision_factors: dict,            # All factors that influenced decision
)
```

---

## 10. Delegation and Authority Attenuation

When entity A delegates to entity B to perform action X:

### 10.1 Attenuation Principle

$$\text{Auth}(B, X) \leq \text{Auth}(A, X)$$

Authority flows downward with loss.

### 10.2 Attenuation Calculation

$$\text{Auth}_{\text{attenuated}} = \text{Auth}_{\text{source}} \times e^{-\lambda \cdot \text{depth}}$$

Where:
- $\lambda$ = attenuation constant (e.g., 0.3)
- $depth$ = delegation depth (1 = direct delegation, 2 = delegation of delegation)

### 10.3 Explicit Delegation Scope

Delegations should be scoped:
```
Delegation(
    delegator: str,
    delegate: str,
    capability: str,             # Specific action or capability
    scope: Dict[str, Any],       # Context/parameter restrictions
    expiration: datetime,         # Time limit
    max_depth: int,              # How many levels deep can delegate further delegate
    revocation_handler: Callable, # What happens if delegator revoked
)
```

---

## 11. Trajectory Analysis

The event log records every security-relevant event.

### 11.1 Event Structure

```
SecurityEvent(
    timestamp: datetime,
    entity: str,
    action: str,
    context: str,
    requested: bool,              # Was authorization requested
    decision: AuthorityDecision,   # What was authorized
    executed: bool,               # Was action actually executed
    outcome: ExecutionOutcome,    # Result
    observations: List[Evidence], # Evidence generated
    trust_before: float,          # Trust state pre-action
    trust_after: float,           # Trust state post-action
)
```

### 11.2 Trajectory Patterns (Examples)

**Normal:** 
Tool A → Request → Allow → Success → Evidence(+) → Trust increases

**Suspicious Sequence:**
Tool A → Request(denied) → Request(denied) → Request(denied) → Success(??) → Evidence(anomaly)

**Privilege Escalation Pattern:**
Tool A → {request(low risk × 10)} → Success → Request(higher risk) → Success

**Collusion Pattern:**
Tool A → Recommends Tool B → Tool B → Requests(Tool A sensitive) → Success

### 11.3 Anomaly Detection

Trajectory analyzer should flag:
- Rapid repeated rejections followed by success
- Unusual parameter combinations
- Timing anomalies (too fast, too slow)
- Authority drift (gradual escalation)
- Pattern changes (normal behavior suddenly different)
- Correlated activity (Tool A always recommends B, then B performs malicious action)

---

## 12. Provenance and Evidence Independence

### 12.1 Correlated Evidence Problem

If evidence comes from correlated sources, it should not be treated as independent.

**Example:**
- Tool A recommends Tool B → Evidence for B
- Tool B confirms Tool A works well → Evidence for A
- These are NOT independent

### 12.2 Provenance Tracking

```
EvidenceProvenance(
    evidence_id: UUID,
    source_entity: str,
    source_confidence: float,
    chain: List[UUID],             # Lineage of evidence
    is_derived: bool,              # Is this evidence based on other evidence
    dependencies: List[UUID],      # What other evidence influenced this
    common_ancestor: Optional[UUID], # Shared origin with other evidence
)
```

### 12.3 Discount Factor for Correlated Evidence

```
def effective_trust_with_provenance(evidence_list, provenance_map):
    # Group evidence by common origin
    clusters = group_by_ancestor(evidence_list, provenance_map)
    
    # For each cluster, reduce influence
    effective_weight = 0
    for cluster in clusters:
        cluster_weight = sum(e.strength for e in cluster)
        # Discount correlated evidence
        cluster_discount = 1.0 / (1.0 + 0.5 * len(cluster))
        effective_weight += cluster_weight * cluster_discount
    
    # Recalculate trust from discounted evidence
    return trust_from_evidence(effective_weight)
```

---

## 13. Attack Scenarios

The system must defend against these attacks:

### 13.1 Immediate Malicious Behavior
Tool A immediately attempts malicious action → Should be detected, denied.

### 13.2 Reputation Poisoning (Slow)
Tool A behaves normally for N interactions, gradually becomes more malicious → Trust increases during poisoning phase, risk should accelerate mitigation.

### 13.3 Hidden Trigger
Tool A behaves benignly, but triggers on specific input pattern (e.g., "EXECUTE_PAYLOAD") → Requires trajectory analysis and anomaly detection.

### 13.4 Compromised Trusted Tool
Tool A is legitimately trusted but becomes compromised (e.g., code injection) → Should be detected by behavioral change + anomalies.

### 13.5 Collusion
Tool A + Tool B coordinate: A recommends B, B performs attack, A covers up → Provenance tracking should detect correlated evidence chains.

### 13.6 Sybil / Reputation Manipulation
Attacker creates many tool identities, generates positive evidence between them → Provenance independence checking should flag this.

### 13.7 Delegation Attack
Tool A obtains delegation from trusted entity, uses it maliciously → Authority attenuation alone insufficient; need trajectory + anomaly analysis.

### 13.8 Prompt Injection
Attacker injects instructions into tool output to cause unauthorized actions → Depends on IFC layer; Trust layer should monitor for unexpected tool transitions.

### 13.9 Context Manipulation
Attacker misleads agent about current context to authorize higher-risk actions → Trust calculus should consider context anomalies.

### 13.10 On-Off Attack
Tool A behaves normally, then attacks, then resumes normal behavior → Temporal analysis should detect this pattern.

### 13.11 Authority Inflation
Tool A requests progressively riskier actions, each approved, each building "trust" for next step → Risk monotonicity principle should prevent this.

### 13.12 Privilege Escalation via Delegation
Tool A → delegates to Tool B → B delegates to Tool C → C performs unauthorized action using attenuated authority → Attenuation + provenance should detect.

---

## 14. Baseline Systems for Comparison

### 14.1 Baseline 1: No Security
Baseline: All tool calls allowed immediately.
- Metric: 100% task success, 100% attack success (useless as security)

### 14.2 Baseline 2: Static Allowlist/Denylist
Baseline: Pre-defined rules, no dynamics.
- Metric: Depends on rule quality; no adaptation

### 14.3 Baseline 3: Simple Reputation Score
Baseline: Single scalar trust value, updated on success/failure.
- Issues: No confidence, no risk, no context

### 14.4 Baseline 4: Simple Threshold
Baseline: If trust > 0.7, allow; else deny.
- Issues: No gradation (VERIFY/SANDBOX), no risk scaling

### 14.5 Baseline 5: Risk-Based Authorization
Baseline: Allow if (trust > risk_threshold(risk)).
- Issues: No confidence, no trajectory, no delegation

### 14.6 Baseline 6: Trajectory-Only Defense
Baseline: Allow if no anomalies detected in event log.
- Issues: No risk model, no delegation attenuation

### Proposed: Dynamic Trust-to-Authority Calculus
Combines all principles: trust, confidence, evidence, risk, context, trajectory, delegation.

---

## 15. Experiments

### 15.1 Experiment Structure

For each attack scenario:

```
Experiment(
    attack_type: str,
    baseline: BaselineSystem,
    proposed: ProposedSystem,
    num_iterations: int,
    random_seed: int,
    config: dict,
)

Result(
    security_metrics: {
        attack_success_rate: float,
        time_to_detection: float,
        false_positive_rate: float,
    },
    utility_metrics: {
        task_success_rate: float,
        false_blocking_rate: float,
        latency_overhead: float,
    },
    tradeoff_score: float,
)
```

### 15.2 Reproducibility

- Fixed random seeds for every experiment
- Structured JSON output of all metrics
- Replay logs for every attack sequence
- Configuration files checked into repo
- Script to reproduce all experiments

---

## 16. Ablation Studies

Run the full system, then remove one component at a time:

1. **Full System** (baseline for comparison)
2. **No Uncertainty** (remove confidence tracking)
3. **No Provenance** (ignore evidence correlated)
4. **No Trajectory** (use only current state)
5. **No Context** (ignore action/context risk)
6. **No Risk Model** (treat all actions as equal)
7. **No Delegation Attenuation** (delegation = no loss)
8. **No Temporal Decay** (trust doesn't degrade over time)

For each: measure attack success, false positives, task success, latency.

---

## 17. Formal Properties

Where practical, encode property tests:

### 17.1 Boundedness
Trust remains in [0, 1]. Confidence remains in [0, 1].

### 17.2 Risk Monotonicity
If risk(action1) > risk(action2), then authorization_threshold(action1) >= authorization_threshold(action2).

### 17.3 Delegation Attenuation
Auth(delegate) ≤ Auth(delegator) for same action.

### 17.4 Revocation Propagation
If entity A is revoked, all delegated authorities from A terminate appropriately.

### 17.5 Evidence Sensitivity
Strong negative evidence (e.g., confirmed malicious behavior) → trust drops sharply.

### 17.6 Uncertainty Conservatism
Low confidence + high risk → no authorization.

### 17.7 Stability
Small evidence changes should not cause large trust oscillations (unless evidence is very strong).

---

## 18. Implementation Phases

### Phase 0: Architecture & Planning (CURRENT)
- [x] Inspect repository
- [ ] Create architecture document
- [ ] Create trust model specification
- [ ] Create threat model
- [ ] Create experiment plan
- [ ] Literature review + novelty analysis

### Phase 1: Trust State & Evidence (Week 1-2)
- [ ] Define TrustState dataclass
- [ ] Implement Evidence model
- [ ] Implement Bayesian trust updates (Beta distribution)
- [ ] Create evidence aggregation
- [ ] Unit tests for trust updates

### Phase 2: Temporal Dynamics (Week 2-3)
- [ ] Implement trust decay
- [ ] Implement confidence dynamics
- [ ] Implement trust recovery
- [ ] Temporal tests

### Phase 3: Risk & Context (Week 3)
- [ ] Define action risk model
- [ ] Implement risk calculation
- [ ] Implement context multipliers
- [ ] Risk model tests

### Phase 4: Authority Engine (Week 4)
- [ ] Implement decision logic
- [ ] ALLOW/VERIFY/SANDBOX/DENY decisions
- [ ] Decision explanations
- [ ] Integration with existing IFC layer

### Phase 5: Trajectory & Anomaly (Week 5)
- [ ] Implement SecurityEvent log
- [ ] Implement trajectory analyzer
- [ ] Implement anomaly detection
- [ ] Trajectory analysis tests

### Phase 6: Delegation & Attenuation (Week 5-6)
- [ ] Implement Delegation model
- [ ] Implement authority attenuation
- [ ] Implement revocation
- [ ] Delegation tests

### Phase 7: Provenance Tracking (Week 6)
- [ ] Implement evidence provenance model
- [ ] Implement correlated evidence detection
- [ ] Implement discount factors
- [ ] Provenance tests

### Phase 8: Attack Simulator (Week 7-8)
- [ ] Implement adaptive attacker framework
- [ ] Implement 12 attack scenarios
- [ ] Implement attack orchestrator
- [ ] Attack tests

### Phase 9: Baselines (Week 8-9)
- [ ] Implement 6 baseline systems
- [ ] Comparison harness
- [ ] Baseline tests

### Phase 10: Experiments (Week 9-10)
- [ ] Reproducible experiment runner
- [ ] Experiment harness
- [ ] Metrics collection
- [ ] Results analysis scripts

### Phase 11: Ablation Studies (Week 10-11)
- [ ] Ablation harness
- [ ] Ablation experiment runner
- [ ] Ablation result analysis

### Phase 12: Formal Properties (Week 11-12)
- [ ] Property test framework
- [ ] Property implementations
- [ ] Property verification

### Phase 13: Integration & Polish (Week 12-13)
- [ ] External benchmark integration (AgentDojo, etc.)
- [ ] Documentation completion
- [ ] Results finalization
- [ ] Research write-up

---

## 19. Repository Structure (Target)

```
/src/trustcalc/
├── trust/                      # NEW: Trust calculus layer
│   ├── state.py               # TrustState dataclass
│   ├── evidence.py            # Evidence model + aggregation
│   ├── updater.py             # Bayesian trust updates
│   ├── temporal.py            # Decay, recovery dynamics
│   ├── risk.py                # Risk model + calculation
│   ├── trajectory.py          # Event log + anomaly detection
│   └── delegation.py          # Delegation + attenuation
├── authority/                 # NEW: Authority engine
│   ├── engine.py              # Decision logic
│   ├── decisions.py           # Decision types
│   └── explanation.py         # Decision explanations
├── provenance/                # EXTEND: Evidence provenance
│   ├── model.py               # Provenance structures
│   ├── checker.py             # Independence checking
│   └── discounting.py         # Correlated evidence discounts
├── core/                      # EXISTING: IFC layer
├── policy/                    # EXISTING: Policy engine
├── gateway/                   # EXISTING: Tool gateway
├── runtime/                   # EXISTING: Execution
├── tools/                     # EXISTING: Tool implementations
├── agents/                    # EXISTING: Agent framework
├── attacks/                   # EXTEND: Attack scenarios
│   ├── adaptivatacker.py      # NEW: Stateful attacker
│   ├── scenarios/             # 12 attack implementations
│   └── orchestrator.py        # Attack coordination
├── evaluation/                # EXTEND: Evaluation framework
│   ├── baselines.py           # 6 baseline implementations
│   ├── experiment.py          # Experiment harness
│   ├── ablation.py            # Ablation study harness
│   ├── metrics.py             # Metrics collection
│   └── properties.py          # Formal property tests
├── config/                    # Configuration
├── utils/                     # Utilities
└── sidechannels/              # (existing)

/tests/
├── unit/
│   ├── test_trust_state.py
│   ├── test_evidence.py
│   ├── test_temporal_dynamics.py
│   ├── test_risk_model.py
│   ├── test_authority_engine.py
│   ├── test_trajectory.py
│   ├── test_delegation.py
│   ├── test_provenance.py
│   └── ...
├── integration/
│   ├── test_trust_to_authority_pipeline.py
│   ├── test_attack_scenarios.py
│   ├── test_baselines.py
│   └── ...
├── property/
│   └── test_formal_properties.py
└── ...

/experiments/
├── run_experiment.py
├── run_ablation.py
├── run_baselines.py
├── configs/                   # Experiment configs
│   ├── attack_*.json
│   ├── baseline_*.json
│   └── ...
└── results/                   # JSON results, analysis scripts

/docs/
├── RESEARCH_PROPOSAL.md       # THIS FILE
├── ARCHITECTURE.md            # System architecture (to be written)
├── TRUST_MODEL.md             # Mathematical trust model details
├── THREAT_MODEL.md            # Attack scenarios + threat analysis
├── EXPERIMENT_PLAN.md         # Detailed experiment specifications
├── LITERATURE_REVIEW.md       # Related work + comparison
├── NOVELTY_ANALYSIS.md        # Contribution uniqueness
└── ...
```

---

## 20. Comparison with Related Work

**Literature to review:**

1. **Trust & Authorization:**
   - "Trust No Tool" (related work)
   - AgentDojo threat model
   - AgentTrust framework

2. **Provenance & Evidence:**
   - Provenance-aware agent security
   - Verifiably safe tool use literature

3. **Delegation & Capability:**
   - Delegation and capability security
   - Authority propagation models

4. **Adaptive Attackers:**
   - Game-theoretic attacks on reputation systems
   - Adversarial robustness in ML

**Key questions to answer:**
- Does existing work already implement dynamic trust-to-authority?
- Does existing work handle uncertainty + provenance + trajectory together?
- What is genuinely novel about this approach?

---

## 21. Research Integrity Principles

1. **No hidden security failures:** Log every decision and its rationale.
2. **No hand-wavy math:** Every formula documented and justified.
3. **Reproducibility:** Fixed seeds, configuration-driven, scripts for all results.
4. **Honest comparison:** Baselines implemented fairly, no strawmen.
5. **Uncertainty quantified:** Confidence explicitly tracked, never hidden.
6. **Ablation thoroughness:** Every component's contribution measured.
7. **Challenge yourself:** Look for counter-examples to your own design.

---

## 22. Success Criteria

### Technical Success:
- [ ] Trust calculus system implemented and tested
- [ ] Attack simulator working with 12+ scenarios
- [ ] Baselines + proposed system compared reproducibly
- [ ] Ablation studies show all components contribute
- [ ] Formal properties verified (or exceptions documented)
- [ ] Experiments reproducible with fixed seeds

### Research Success:
- [ ] Contribution is novel vs. related work
- [ ] Mathematical formulation is principled, not arbitrary
- [ ] Uncertainty is properly modeled (not hidden)
- [ ] Provenance independence is addressed
- [ ] Trajectory analysis provides value
- [ ] Delegation attenuation is justified
- [ ] Results are honest about limitations

### Presentation Success:
- [ ] Architecture is clear and well-documented
- [ ] Code is readable and maintainable
- [ ] Experiments are reproducible and auditable
- [ ] Research write-up clearly explains contribution
- [ ] Comparison with related work is thorough and fair

---

## Next Steps

1. **Review this proposal** with advisors
2. **Challenge assumptions:** Which parts are unsupported?
3. **Check literature:** Is this work truly novel?
4. **Finalize trust model:** Bayesian vs. alternatives?
5. **Begin Phase 1:** Implement TrustState and Evidence

---

**Status:** Ready for feedback and literature review before coding begins.
