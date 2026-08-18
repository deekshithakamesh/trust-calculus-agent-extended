# Trust Model Specification

**Mathematical Foundation for Dynamic Trust-to-Authority Calculus**

---

## 1. Core Definitions

### 1.1 Trust

**Intuitive:** The degree to which an entity will behave benignly in a specific action and context, given our current knowledge.

**Formal:** 

Let $T(e, a, c, t)$ denote the trust in entity $e$ to perform action $a$ in context $c$ at time $t$.

$$T: \text{Entity} \times \text{Action} \times \text{Context} \times \text{Time} \to [0, 1]$$

Where:
- $T(e, a, c, t) = 1$ means: we are certain $e$ will behave benignly for action $a$ in context $c$
- $T(e, a, c, t) = 0$ means: we are certain $e$ will behave maliciously for action $a$ in context $c$
- $T(e, a, c, t) = 0.5$ means: we have no information to distinguish benign from malicious

**Key property:** Trust is entity-action-context specific, NOT a global entity score.

### 1.2 Confidence

**Intuitive:** How certain we are that our trust estimate is accurate.

**Formal:**

Let $C(e, a, c, t)$ denote confidence in the trust estimate.

$$C: \text{Entity} \times \text{Action} \times \text{Context} \times \text{Time} \to [0, 1]$$

Where:
- $C = 1$ means: our trust estimate is based on extensive, reliable evidence
- $C = 0$ means: our trust estimate is purely a guess (no evidence)

**Key property:** High confidence with negative evidence is more informative than high confidence with positive evidence.

### 1.3 Evidence

**Intuitive:** Observable events that provide information about trustworthiness.

**Formal:** See Evidence section (1.6).

### 1.4 Risk

**Intuitive:** The potential harm if the entity misbehaves.

**Formal:**

Let $R(a, c)$ denote the risk of action $a$ in context $c$.

$$R: \text{Action} \times \text{Context} \to [0, 1]$$

Where:
- $R = 0$ means: no harm if misbehavior occurs (e.g., harmless query)
- $R = 1$ means: catastrophic harm if misbehavior occurs (e.g., delete all data)

**Key property:** Risk is orthogonal to trust. High trust does not reduce risk; high risk does not increase trust.

### 1.5 Authority

**Intuitive:** Permission to execute an action based on the combination of trust, confidence, risk, context, and history.

**Formal:** Discrete decision produced by the Authority Engine.

$$A: (\text{Trust}, \text{Confidence}, \text{Risk}, \text{Context}, \text{History}) \to \{\text{ALLOW, VERIFY, RESTRICT, SANDBOX, DENY}\}$$

**Key property:** Authority is the output of a deterministic, auditable function. Not determined by an LLM.

### 1.6 Uncertainty

**Intuitive:** The gap between what we know and what we need to decide safely.

**Formal:** Characterized by the pair $(T, C)$.

When $C$ is low, we have uncertainty:
- High $T$ with low $C$ = optimistic guess (unreliable)
- Low $T$ with low $C$ = pessimistic guess (unreliable)
- High $T$ with high $C$ = well-founded confidence
- Low $T$ with high $C$ = well-founded distrust

---

## 2. Bayesian Trust Model

We adopt a **Beta-Binomial** model for trust.

### 2.1 Beta Distribution

Trust is modeled as the expected value of a Beta distribution:

$$T(e, a, c, t) = E[\theta_{e,a,c}(t)] = \frac{\alpha(t)}{\alpha(t) + \beta(t)}$$

Where:
- $\theta_{e,a,c}$ ~ $\text{Beta}(\alpha, \beta)$ is the latent trustworthiness parameter
- $\alpha(t)$ = count of "benign" evidence observations
- $\beta(t)$ = count of "malicious" evidence observations

### 2.2 Confidence (Concentration)

Confidence is the total evidence accumulated:

$$C(e, a, c, t) = \frac{\alpha(t) + \beta(t)}{\alpha_{\text{max}} + \beta_{\text{max}}}$$

Where:
- $\alpha_{\text{max}}, \beta_{\text{max}}$ are calibration parameters (e.g., 100 observations each)

**Intuition:** After 200 total observations, confidence ≈ 1.0.

### 2.3 Prior Beliefs

For a new entity with no evidence, use a prior:

$$\alpha_0 = \beta_0 = 1 \quad \text{(uniform prior, expressing maximal uncertainty)}$$

Alternative priors:
- $\alpha_0 = 10, \beta_0 = 1$ = optimistic prior (assume benign until proven otherwise)
- $\alpha_0 = 1, \beta_0 = 10$ = pessimistic prior (assume malicious until proven otherwise)

**Recommendation:** Uniform prior for maximum conservatism.

### 2.4 Evidence Incorporation

When new evidence $e$ with strength $s \in [0, 1]$ arrives:

**If evidence is positive (benign):**
$$\alpha(t+1) = \alpha(t) + s$$

**If evidence is negative (malicious):**
$$\beta(t+1) = \beta(t) + s$$

**If evidence is neutral or mixed:**
$$\alpha(t+1) = \alpha(t) + s_{\text{positive}} \\
\beta(t+1) = \beta(t) + s_{\text{negative}}$$

where $s_{\text{positive}} + s_{\text{negative}} = s$.

### 2.5 Advantages of Beta-Binomial

1. **Principled:** Foundation in Bayesian statistics and conjugate priors
2. **Separates trust from confidence:** Unlike simple averages
3. **Handles sparse evidence:** Natural behavior with few observations
4. **Incorporates evidence strength:** Evidence weighted by reliability
5. **Well-studied:** Extensive literature on calibration and properties
6. **Interpretable:** $\alpha$ and $\beta$ have clear meaning

### 2.6 Calibration

For accuracy, calibration constants should be:

$$\alpha_{\text{max}} + \beta_{\text{max}} = N_{\text{calibration}}$$

**Recommendation:** $N_{\text{calibration}} = 50$ (confidence saturates after ~50 strong observations).

---

## 3. Temporal Dynamics

Trust changes over time. We implement two mechanisms:

### 3.1 Decay Without Evidence

In the absence of new evidence, trust decays toward the prior:

$$\alpha(t) = \alpha_0 + (\alpha(t_0) - \alpha_0) \cdot e^{-\lambda (t - t_0)}$$
$$\beta(t) = \beta_0 + (\beta(t_0) - \beta_0) \cdot e^{-\lambda (t - t_0)}$$

Where:
- $\lambda$ = decay rate (e.g., 0.01 per day means half-life ≈ 70 days)
- $t_0$ = time of last observation

**Intuition:** Silence is not endorsement.

### 3.2 Trust Recovery After Compromise

If an entity is compromised (malicious evidence found), then exhibits good behavior, trust can recover, but conservatively.

**Recovery strategy:**
1. Upon strong negative evidence, confidence initially remains high (we're certain it's malicious)
2. If good behavior is later observed, confidence gradually decreases while positive evidence accumulates
3. Trust can eventually recover, but at a slower rate than it was originally built

**Formula:**

After strong negative evidence at time $t_{\text{incident}}$:

$$\alpha(t) = \alpha_{\text{recovered}} \quad \text{if } t > t_{\text{incident}} + t_{\text{recovery_period}}$$

$$t_{\text{recovery_period}} = t_{\text{incident}} + \text{days_since_incident} \times k_{\text{recovery}}$$

where $k_{\text{recovery}} = 2$ (recovery is twice as slow as decay).

### 3.3 Confidence Dynamics

Separate from trust dynamics, confidence changes based on evidence frequency:

**With frequent positive evidence:**
$$C(t) = C(t_0) + \Delta_{\text{positive}} \cdot \text{evidence_rate}$$

**With rare evidence:**
$$C(t) = C(t_0) \times e^{-\lambda_C (t - t_{\text{last\_evidence}})}$$

where $\lambda_C \approx 0.001$ (slow decay).

**With strong negative evidence:**
$$C(t) = \text{min}(1.0, C(t_0) + \Delta_{\text{negative}})$$

where $\Delta_{\text{negative}} > \Delta_{\text{positive}}$ (negative evidence builds confidence faster).

---

## 4. Evidence Model

### 4.1 Evidence Types

Formally, evidence is characterized by:

$$\text{Evidence} = (s, \text{type}, \text{strength}, \text{reliability}, \text{provenance})$$

Where:

**type:** Categorical variable

| Type | Sign | Strength Range | Example |
|------|------|-----------------|---------|
| SuccessfulAction | + | [0.1, 0.5] | Tool completed task correctly |
| FailedAction | - | [0.1, 0.3] | Tool failed to complete task (may be environment) |
| AnomalousAction | - | [0.2, 0.6] | Tool behaved unexpectedly (suspicious) |
| UnauthorizedAttempt | - | [0.4, 0.8] | Tool tried to exceed permissions (blocked) |
| MaliciousBehavior | - | [0.7, 1.0] | Confirmed malicious intent (very strong) |
| SecurityAnomaly | - | [0.3, 0.7] | Detected pattern inconsistent with entity history |
| PolicyViolation | - | [0.4, 0.8] | Broke IFC/policy rules |
| AgentRecommendation | + | [0.05, 0.3] | Another entity recommends (weak, dependent on recommender trust) |
| HumanVerification | + | [0.7, 1.0] | Human verified trustworthiness |
| PerformanceMetric | +/- | [0.1, 0.3] | Speed/efficiency measurement |

**strength:** How strongly this evidence supports or contradicts trustworthiness ($s \in [0, 1]$).

**reliability:** How trustworthy the evidence source is ($r \in [0, 1]$).

**provenance:** Chain of custody for evidence (UUID chain).

### 4.2 Strength Guidelines

**Benign Evidence:**
- SuccessfulAction: $s = 0.1 + 0.4 \times \text{difficulty}$ (harder actions provide more evidence)
- HumanVerification: $s = 0.8$

**Malicious Evidence:**
- MaliciousBehavior (confirmed): $s = 1.0$ (definitive)
- UnauthorizedAttempt: $s = 0.6$ (suspicious but not definitive)
- PolicyViolation: $s = 0.7$
- AnomalousAction: $s = 0.3$ (weak, could be benign)

### 4.3 Adjusted Evidence Strength

When evidence comes from a source with its own trust level, adjust:

$$s_{\text{adjusted}} = s \times r$$

where $r$ = reliability of evidence source.

**Example:**
- Direct observation: $r = 1.0$
- Human report: $r = 0.9$
- Other tool recommendation: $r = T_{\text{recommender}}$ (recommender's trust)
- Untrusted source: $r = 0.1$

---

## 5. Risk Model

### 5.1 Quantifying Action Risk

Risk is a function of:

$$R(a, c, s) = R_{\text{action}} + R_{\text{context}} - R_{\text{sensitivity}}$$

Where:

**$R_{\text{action}}$:** Inherent risk of the action type ($\in [0, 1]$).

| Action | $R_{\text{action}}$ |
|--------|---------|
| WebSearch | 0.05 |
| FileRead(public) | 0.10 |
| FileRead(private) | 0.40 |
| DatabaseRead | 0.30 |
| DatabaseWrite | 0.70 |
| CodeExecution | 0.90 |
| ExternalAPI(payment) | 0.90 |
| PrivilegeEscalation | 1.00 |

**$R_{\text{context}}$:** Additional risk from context ($\in [-0.3, 0.3]$).

| Context | $R_{\text{context}}$ |
|---------|---------|
| Normal operation, expected timing | -0.1 |
| Unusual parameters | +0.1 |
| High-stakes data (PII, financial) | +0.2 |
| Critical system | +0.3 |
| Rapid succession of requests | +0.1 |

**$R_{\text{sensitivity}}$:** Reduction for benign intent signals ($\in [-0.2, 0]$).

| Signal | $R_{\text{sensitivity}}$ |
|--------|---------|
| Explicitly requested by user | -0.1 |
| Logged in audit trail | -0.05 |
| Followed by verification request | 0 |

### 5.2 Risk Monotonicity

**Property:** Risk must not decrease as authority increases for the same entity.

**Formal:** If $R_1 > R_2$, then the minimum trust required to authorize action 1 must be $\geq$ minimum trust required for action 2.

$$\text{required\_trust}(R_1) \geq \text{required\_trust}(R_2) \quad \text{if } R_1 > R_2$$

This is a hard constraint in the Authority Engine.

---

## 6. Authority Decision Function

### 6.1 Decision Logic

The authority engine maps $(T, C, R, \text{history}, \text{anomaly})$ to a decision:

```
def authorize(T, C, R, history, trajectory_anomaly):
    
    # 1. Confidence gate: low confidence + high risk = deny
    if C < C_MIN and R > R_THRESHOLD:
        return DENY("Insufficient evidence for high-risk action")
    
    # 2. Risk gate: compute minimum trust required
    T_required = compute_trust_threshold(R)
    if T < T_required:
        return SANDBOX("Trust insufficient for action risk")
    
    # 3. Anomaly detection
    if trajectory_anomaly.severity > ANOMALY_THRESHOLD:
        return VERIFY("Detected behavior anomaly")
    
    # 4. Default to least permissive sufficient decision
    if R > 0.7:
        return VERIFY("High-risk action requires verification")
    elif R > 0.4:
        return SANDBOX("Medium-risk action sandboxed")
    else:
        return ALLOW("Low-risk action, trust sufficient")
```

### 6.2 Trust Threshold by Risk

$$T_{\text{required}}(R) = 0.5 + 0.5 \times R$$

| $R$ | $T_{\text{required}}$ |
|-----|-----------------|
| 0.0 | 0.50 (no trust needed for harmless actions) |
| 0.3 | 0.65 |
| 0.5 | 0.75 |
| 0.7 | 0.85 |
| 1.0 | 1.00 (perfect trust needed for critical actions) |

### 6.3 Confidence-Based Thresholds

If confidence is low, increase the required trust:

$$T_{\text{required\_adjusted}} = T_{\text{required}} + (1 - C) \times \alpha$$

where $\alpha = 0.2$ (confidence deficit of 0.5 adds 0.1 to required trust).

### 6.4 Decision Types

| Decision | Meaning | When Applied |
|----------|---------|--------------|
| **ALLOW** | Execute unrestricted | $T \geq T_{\text{req}}$, $C \geq 0.7$, no anomalies |
| **VERIFY** | Execute, record closely | $T \geq T_{\text{req}}$, anomalies detected |
| **RESTRICT** | Execute with limitations (e.g., quota, audit) | $T \geq 0.6 T_{\text{req}}$, provenance concerns |
| **SANDBOX** | Execute in isolated environment | $T < T_{\text{req}}$ but $T > 0.5$, or medium risk |
| **DENY** | Reject entirely | $T < 0.5$, or $C < 0.2$ and $R > 0.5$ |

---

## 7. Delegation and Authority Attenuation

### 7.1 Delegation Model

When entity $A$ delegates authority for action $X$ to entity $B$:

$$\text{Auth}(B, X | \text{delegated from } A) \leq \text{Auth}(A, X)$$

### 7.2 Attenuation Formula

$$T_{\text{effective}}(B, X) = T_A(X) \times e^{-\lambda \cdot d}$$

where:
- $d$ = delegation depth (1 for direct, 2 for sub-delegation, etc.)
- $\lambda$ = attenuation constant (e.g., 0.3)

**Example:**
- $T_A = 0.9$ (Entity A is highly trusted)
- $A$ delegates to $B$ ($d = 1$): $T_{\text{eff}} = 0.9 \times e^{-0.3} \approx 0.72$
- $B$ delegates to $C$ ($d = 2$): $T_{\text{eff}} = 0.9 \times e^{-0.6} \approx 0.54$

### 7.3 Delegation Revocation

If $A$ revokes delegation:
1. All delegations from $A$ to $B$ become invalid
2. All sub-delegations from $B$ become invalid (cascade)
3. New requests from $B$ are treated as $B$ directly (low baseline trust)

---

## 8. Provenance and Evidence Independence

### 8.1 Common Ancestor Problem

If two pieces of evidence originate from the same source (directly or through chains), they are NOT independent.

**Example:**
- Tool A recommends Tool B → evidence for B's trust
- Tool B confirms Tool A works → evidence for A's trust
- These evidence chains share a common ancestor (the recommendation)

### 8.2 Provenance Discount

For a set of evidence with common ancestors:

$$T_{\text{discounted}} = T_{\text{raw}} \times d_{\text{provenance}}$$

where:

$$d_{\text{provenance}} = \prod_{i} \frac{1}{1 + \lambda_i \times (\text{cluster\_size}_i - 1)}$$

where:
- $\lambda_i \approx 0.3$ (discount factor)
- $\text{cluster\_size}_i$ = size of evidence cluster with common ancestor $i$

**Intuition:** If 5 pieces of evidence trace to one source, we discount by $\approx 1 / (1 + 0.3 \times 4) = 0.45$.

---

## 9. Formal Properties

### 9.1 Boundedness

$$T(e, a, c, t) \in [0, 1] \quad \forall e, a, c, t$$
$$C(e, a, c, t) \in [0, 1] \quad \forall e, a, c, t$$

### 9.2 Monotonicity in Risk

$$T_{\text{required}}(R_1) \geq T_{\text{required}}(R_2) \quad \text{if } R_1 > R_2$$

### 9.3 Monotonicity in Confidence-aware decisions

$$\text{threshold}(C_1, R) \leq \text{threshold}(C_2, R) \quad \text{if } C_1 < C_2$$

(Lower confidence requires higher trust for same risk.)

### 9.4 Delegation Attenuation

$$T_{\text{eff}}(d) \geq T_{\text{eff}}(d+1) \quad \text{for all } d \geq 1$$

### 9.5 Negative Evidence Dominance

Strong negative evidence has stronger effect than equivalent positive evidence:

$$|\Delta T_{\text{negative}}| > |\Delta T_{\text{positive}}| \quad \text{for same evidence strength}$$

---

## 10. Calibration and Parameter Tuning

### 10.1 Calibration Constants

| Parameter | Value | Justification |
|-----------|-------|---------------|
| $\alpha_0, \beta_0$ | 1, 1 | Uniform prior (maximal skepticism) |
| $N_{\text{calibration}}$ | 50 | Confidence saturates after ~50 strong observations |
| $\lambda_{\text{decay}}$ | 0.01/day | Half-life of ~70 days without evidence |
| $\lambda_{\text{attenuation}}$ | 0.3 | Delegation attenuates by ~30% per level |
| $C_{\text{MIN}}$ | 0.3 | Require 30% confidence for high-risk actions |
| $R_{\text{THRESHOLD}}$ | 0.5 | Medium-risk boundary |

### 10.2 Tuning Strategy

1. **Start with defaults** (above)
2. **Run baseline experiment** (random trust vs. no defense)
3. **Measure:** What trust value makes system 50% effective?
4. **Adjust thresholds** if needed
5. **Ablate:** Remove each threshold adjustment, measure impact

---

## 11. Advantages and Limitations

### 11.1 Advantages

1. **Principled:** Founded in Bayesian probability theory
2. **Interpretable:** $\alpha$ and $\beta$ have clear meaning
3. **Handles uncertainty:** Confidence explicitly tracked
4. **Temporal:** Supports decay and recovery
5. **Evidence-based:** Can incorporate any type of evidence
6. **Actionable:** Produces deterministic, auditable decisions

### 11.2 Limitations

1. **Binary evidence:** Beta-binomial assumes evidence is ultimately benign or malicious
   - **Mitigation:** Use mixed evidence $(s_+, s_-)$ for nuanced cases

2. **Independence assumption:** Assumes evidence is independent before provenance discounting
   - **Mitigation:** Explicit provenance tracking and discounting

3. **Static prior:** Uniform prior may not fit domain
   - **Mitigation:** Configurable prior, tuned per use case

4. **Calibration sensitivity:** Requires careful tuning of decay rates, thresholds
   - **Mitigation:** Systematic ablation studies to validate choices

---

## 12. Example: Trust Calculus in Action

### 12.1 Scenario

Tool A (WebSearchTool) making request: "Read /etc/passwd"

**Initial State:**
- Tool A: $T = 0.7$ (generally trusted), $C = 0.8$ (good history)
- Action: FileRead(private)
- Context: Unexpected (not part of typical web search)

### 12.2 Risk Calculation

$$R = R_{\text{action}} + R_{\text{context}} - R_{\text{sensitivity}}$$
$$R = 0.40 + 0.2 - 0 = 0.60$$

**Required Trust:**
$$T_{\text{required}} = 0.5 + 0.5 \times 0.60 = 0.80$$

**Adjustment for confidence:**
$$T_{\text{adjusted}} = 0.80 + (1 - 0.8) \times 0.2 = 0.84$$

### 12.3 Decision

Tool A has $T = 0.7 < 0.84$, so:

$$\text{Decision: SANDBOX}$$

**Explanation:**
```
SANDBOX

Trust: 0.70
Confidence: 0.80
Risk: 0.60
Required Trust: 0.84

Reason: Tool A's trust (0.70) is insufficient for 
high-risk action (FileRead private). Confidence is high, 
so this is a well-founded distrust, not uncertainty. 
Action will be sandboxed and monitored closely.
```

### 12.4 Outcome Handling

**Case 1: FileRead succeeds (normal behavior)**
- Evidence: SuccessfulAction, $s = 0.1$ (read operation is routine)
- Update: $\alpha \gets 0.7 \times 50 + 0.1 \approx 35.1$, $T \gets 35.1/50 = 0.70$ (no change)

**Case 2: FileRead attempts to exfiltrate data (malicious)**
- Evidence: MaliciousBehavior, $s = 1.0$, $r = 1.0$ (direct observation)
- Update: $\beta \gets 0.3 \times 50 + 1.0 \approx 16.0$, $T \gets 35/51 \approx 0.69$, $C \gets 51/50 = 1.02 \to 1.0$
- **Tool A is now distrusted with high confidence**

---

## 13. Validation

### 13.1 Sanity Checks

- [ ] Does trust increase with more positive evidence?
- [ ] Does confidence increase monotonically with evidence count?
- [ ] Does decay reduce trust when no evidence appears?
- [ ] Do low-confidence estimates refuse high-risk actions?
- [ ] Does attenuation reduce effective trust for delegations?

### 13.2 Property Tests (Formal)

See section 9 (Formal Properties).

---

## 14. Future Extensions

1. **Multi-level evidence:** Evidence that is neither fully benign nor malicious
2. **Contextual priors:** Different priors for different entity types (tool, agent, human)
3. **Causal reasoning:** Model causal relationships between entities' recommendations
4. **Adaptive thresholds:** Learn risk thresholds from past decisions
5. **Hierarchical trust:** Trust at multiple levels (entity, class of entity, source)

---

## Bibliography

Key references for Beta-Binomial trust models:

1. Josang & Ismail. "The Beta Reputation System"
2. Sentz & Ferson. "Combination of Evidence in Dempster-Shafer Theory"
3. Whitby, Jøsang & Indulska. "Filtering Out Unfair Ratings"
4. Mauw & Overmars. "Defining Reputation"

---

**Status:** Ready for implementation and calibration.
