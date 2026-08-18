Trust Model — Formalization (Draft)

Purpose
-------
Document the formal trust state, update rules, uncertainty representation, evidence model, provenance, temporal decay, and how trust is used to compute authority for specific actions and contexts.

Design principles
-----------------
- Trust is contextual: it is a function of (entity, action, context, history) and never a single global scalar.
- Separate trust (expectation of correct behavior) from confidence/uncertainty (how much evidence supports that expectation).
- Evidence is explicit, attributed, timestamped, and carries a reliability/reputation score.
- Trust updates are Bayesian where possible (Beta model for binary outcomes), but evidence objects are first-class and can be mapped to Beta increments.
- Temporal decay reduces influence of old evidence (half-life parameterizable).
- Provenance links evidence to sources and supports discounting for correlated evidence.
- Trajectory-aware updates consider ordered sequences of events and features derived from them (e.g., rate of privilege escalation requests, delegation depth).

Formal trust state (conceptual)
-------------------------------
Define TrustState as a structured record:

TrustState(entity, action, context, t) -> {
  expected: float,        # E[success] in [0,1]
  confidence: float,      # confidence in expected, [0,1]
  evidence: List[Evidence],
  provenance_graph: ProvenanceGraph,
  counts: {alpha, beta},  # Beta posterior counts (internal)
  last_update: timestamp,
  meta: {delegation_depth, owner, risk_profile, notes}
}

Evidence model
--------------
Each Evidence object is a record:

Evidence {
  id: uuid,
  source: entity_id_or_monitor,
  timestamp: iso8601,
  type: enum(success, failure, anomaly, recommendation, verification, human_assertion, monitor_alert),
  payload: arbitrary JSON (e.g., execution logs, diffs),
  strength: float  # a reliability score in [0,1] describing how trustworthy the source is for this evidence
  weight: float    # mapped to Beta increments, e.g., +w to alpha, +w to beta
  provenance: list[source ids],
}

Provenance
----------
- Maintain a directed provenance graph where nodes are entities/evidence and edges are "recommended_by" or "observed_by" relations.
- When evidence is dependent on other evidence (e.g., Tool A recommended Tool B), record those edges to detect correlated evidence and to discount duplicated source chains.
- Implement simple provenance discounting: when multiple pieces of evidence share root sources, reduce effective weight via a discount factor.

Mathematical core (Beta posterior)
----------------------------------
- Maintain Beta(alpha, beta) per (subject, action) as a succinct posterior for binary success/failure.
- Map Evidence weight -> fractional increment to alpha or beta depending on type:
  - success evidence: alpha += weight
  - failure evidence: beta += weight
- After each evidence insertion, compute:
  expected = alpha / (alpha + beta)
  var = (alpha * beta) / ((alpha + beta)^2 * (alpha + beta + 1))
  confidence = 1 - normalized_var  (map variance to [0,1])
- Use exponential decay toward prior (alpha0=1,beta0=1) using configurable half-life to age alpha/beta.

Confidence interpretation
-------------------------
- Confidence is derived from posterior variance; low variance (many observations) => high confidence.
- For high-risk actions, require both high expected and high confidence.
- Expose numeric confidence to authority engine; do not conflate with expected.

Trajectory and temporal features
--------------------------------
- Keep an append-only EventLog of actions for each agent/tool; event includes pre/post trust and authority values.
- Derive features from trajectory: recent failure rate, escalation frequency, recommended-tool-chains, delegation depth, sudden spikes.
- Include sequence detectors for hidden-trigger patterns (e.g., behave → escalate → request privileged action).

Provenance-aware discounting
----------------------------
- If multiple evidences share a common upstream source within k hops, reduce their effective weights by a correlation factor c in (0,1].
- This prevents a malicious origin from amplifying its influence via multiple recommendation hops.

Delegation model
----------------
- Track delegation chains: (A delegates to B for action X with scope S, expiry E).
- Authority should attenuate along delegation chains unless explicit re-authorization/evidence supports escalation.
- Implement a simple attenuation function: Authority(B) <= attenuation(depth) * Authority(A). Depth-based exponential attenuation is a reasonable starting point.

Decision thresholds (authority engine inputs)
--------------------------------------------
AuthorityEngine receives:
- expected, confidence, risk(action), delegation_depth, provenance_warnings, trajectory_anomalies

Prototype decision rules (configurable):
- If risk==very_high: require expected >= 0.85 and confidence >= 0.8 -> ALLOW; if expected >= 0.7 and confidence >= 0.5 -> VERIFY; else DENY.
- If risk==high: expected >= 0.7 and confidence >= 0.4 -> ALLOW; expected >= 0.55 -> VERIFY; else RESTRICT.
- If risk==medium: expected >= 0.5 -> ALLOW; else VERIFY.
- If any provenance_warnings (correlated evidence, untrusted sources), increase required thresholds by configurable delta.

Explainability
--------------
Every authority decision must return a deterministic explanation structure containing:
- numeric inputs (expected, confidence, risk, delegation depth)
- rule evaluated and threshold values
- provenance issues and event snippets used
- recommended next step (human verification details if VERIFY)

Why this model?
----------------
- Beta posterior gives a well-understood Bayesian interpretation for binary outcomes and straightforward confidence estimates via variance.
- Evidence objects and provenance separate observation from summarizing counts; they support richer analysis (discounting, trajectory detection) without abandoning a compact posterior for efficient decisioning.

Extensions (future research)
----------------------------
- Use hierarchical Bayesian models for multi-action correlations.
- Use Dirichlet priors for multi-categorical outcomes.
- Investigate belief functions / Dempster–Shafer if combining conflicting evidence with unknown reliabilities proves advantageous.
- Explore formal guarantees (e.g., monotonicity, boundedness) and how to test them empirically.

Notes
-----
This document is a draft. After the literature review completes, revise the model to incorporate best practices or prior art (e.g., existing trust/reputation systems, provenance models such as W3C-PROV, and prior Bayesian trust literature).