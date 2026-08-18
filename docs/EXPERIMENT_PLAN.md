Experiment Plan — Baselines, Metrics, and Reproducible Runs

Purpose
-------
Describe the experimental protocol, baselines, metrics, reproducibility, and minimal scripts needed to evaluate the proposed Dynamic Trust→Contextual Authority calculus against adaptive attackers.

Goals
-----
- Measure security (attack success, detection, privilege escalation) and utility (task success, false blocking) across baselines and the proposed system.
- Provide reproducible scripts that produce JSON/CSV outputs and generate standard plots for analysis.
- Support ablation studies and randomized trials with fixed seeds.

Baselines
---------
1. No security (baseline)
   - LLM agent calls tools directly; no authority gate.
2. Static allow/deny policy
   - Per-tool fixed permissions (allow read, deny write, etc.).
3. Simple reputation
   - Aggregate simple success/failure counts into a scalar reputation score (no uncertainty, no provenance).
4. Trust-threshold (prototype)
   - Beta posterior expected value compared to a fixed threshold; no provenance/trajectory.
5. Risk-only
   - Decisions based purely on action risk mapping; no trust dynamics.
6. Trajectory-only defense
   - Simple heuristics on recent event patterns (e.g., escalation frequency) without Bayesian trust.

Proposed system
---------------
- Full Trust-to-Authority calculus with:
  - Evidence + provenance + trajectory
  - Beta posterior + confidence
  - Delegation attenuation
  - Deterministic authority engine with configurable thresholds

Experiment harness
------------------
- Use scripts/experiment_runner.py or scripts/run_comparison.py to run a suite of scenarios.
- Each run configuration contains:
  - seed, run_id, attacker_strategy, defender_config, baseline_type, num_steps, toolset
- Outputs:
  - outputs/<run-id>/metadata.json (seed, config)
  - outputs/<run-id>/events.log (event stream)
  - outputs/<run-id>/summary.json (aggregated metrics)
  - outputs/<run-id>/metrics.csv (time-series of trust/authority)

Reproducibility
---------------
- Use Python RNG seeded via config and pass seed to all components (numpy.random, random).
- Log exact package versions (pyproject.toml / requirements.txt) in metadata.json.
- Use deterministic agent policies where possible (or record policy RNG seeds).

Metrics (security & utility)
----------------------------
Security metrics
- Attack Success Rate
- Unauthorized Action Rate
- Malicious Tool Invocation Rate
- Detection Rate
- Time to Detection
- Privilege Escalation Rate
- Trust Manipulation Success Rate
Utility metrics
- Task Success Rate
- Task Completion Rate
- False Blocking Rate (FN where legitimate action was blocked)
- Verification Rate (# of VERIFY prompts per task)
- Latency overhead (average additional decision time)

Data collection & analysis
--------------------------
- Prefer JSON-lines for event logs; each event includes timestamp, actor, action, context, decision, trust_before/after, authority_before/after, evidence_added.
- Provide a Jupyter notebook / scripts/plot_results.py that computes:
  - ROC-style plots for defenders (tradeoff between blocking attacker and blocking legitimate tasks)
  - Time-to-detection CDFs
  - Security–utility Pareto plots

Experiment schedule (minimal)
-----------------------------
Phase A: Sanity
- Run single-run examples manually to validate components (no attacker or trivial attacker). Validate logs and summary generation.

Phase B: Baseline comparison (per attack)
- For each attack type in Threat Model, run 30 seeded trials for each baseline and the proposed system.
- Compute means and confidence intervals for metrics.

Phase C: Ablations
- For a chosen attack or set, run with components removed (no provenance, no trajectory, no uncertainty). Compare to full system.

Phase D: Adaptive attacker
- Run longer episodes with an attacker optimizer that adapts to defender decisions. Track whether defender thresholds or decay cause vulnerability.

Statistical rigor
-----------------
- Use fixed seeds and at least 30 trials for each configuration for initial statistical power.
- Use two-sided t-tests or nonparametric tests (Mann–Whitney) to compare metrics across conditions.
- Report effect sizes.

Deliverables
------------
- Reproducible scripts and configs under scripts/ and experiments/ with README explaining how to reproduce each figure.
- A results/ directory with raw outputs and processed CSVs for the paper figures.
- Notebooks/analysis.ipynb reproducing the core plots used in the paper.

Quick checks & smoke tests
--------------------------
- unit tests for: trust updates, evidence ingestion, provenance discounting, authority decision rules, delegation attenuation.
- integration test: run a short scenario end-to-end and assert that outputs/<run-id>/summary.json is created and contains expected keys.

Next steps after plan approval
-----------------------------
1. Implement append-only EventLog and Evidence API.
2. Wrap TrustStore to accept Evidence objects and persist alpha/beta counts with provenance links.
3. Implement AuthorityEngine and a minimal config/policy file.
4. Implement a minimal toolset (mocked) and a trivial attacker that performs hidden-trigger attack.
5. Run Phase A sanity checks and add tests.

Notes
-----
This plan deliberately favors reproducibility and small incremental steps. The initial experiment set targets the research question by measuring whether dynamic, provenance- and trajectory-aware trust leads to materially better security-utility tradeoffs than plausible baselines.