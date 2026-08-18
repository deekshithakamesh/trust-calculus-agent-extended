Dynamic Trust-to-Authority Calculus — System Architecture

Purpose
-------
This document describes the proposed high-level architecture for the "Dynamic Trust-to-Authority Calculus for Secure Autonomous LLM Agents" research prototype and maps the components to the existing repository structure so implementation can proceed incrementally and traceably.

Core design goal
----------------
Answer the research question:

"Given everything that has happened so far, how much authority should this entity have to perform THIS action in THIS context?"

Key property: the LLM proposes actions but the Trust/Authority layer independently decides final authorization.

System overview
---------------
USER
  ↓
LLM AGENT (planner)  — proposes action(s) and candidate delegation
  ↓
PROPOSED ACTION
  ↓
TRUST CALCULUS (stateful decision input)
  - Trust state (entity, action, context, time)
  - Confidence / uncertainty
  - Evidence & provenance
  - Trajectory / history
  - Delegation state
  - Context & risk
  ↓
AUTHORITY ENGINE (deterministic policy mapping)
  - Decisions: ALLOW | VERIFY | RESTRICT | SANDBOX | DENY
  - Produces deterministic, auditable explanation + decision metadata
  ↓
TOOL (mocked in early stages)
  ↓
OBSERVATIONS → EVIDENCE → TRUST UPDATE
  ↓
NEW TRUST STATE (persisted in-memory initially)

Repository mapping (existing code)
----------------------------------
- LLM Agent / experiments
  - src/trustcalc/agents/  — agent abstractions and example agent loops
- Tools & environment
  - src/trustcalc/tools/ — tool mocks (WebSearch, FileRead, FileWrite, Database*, EmailSend, CodeExecute, PaymentAPI, ExternalAgent)
  - src/trustcalc/environment/ or src/trustcalc/runtime/ — runtime wrappers and sandboxing (some code under runtime and sidechannels)
- Trust model (prototype exists)
  - src/trustcalc/trust/model.py — Beta/Bayesian trust store with temporal decay (prototype)
- Authority / enforcement
  - src/trustcalc/gateway/enforcement.py — PolicyEnforcer integrates trust in decisions (prototype)
- Attacks & simulator
  - src/trustcalc/attacks/ — existing attack implementations and channels (formatting, whitespace, timing, synonym, etc.)
- Evaluation & runner
  - src/trustcalc/evaluation/runner.py
  - scripts/run_comparison.py  — comparison runner (exists)
- Side-channel measurement
  - src/trustcalc/sidechannels/ — channels and leakage estimators
- Tests
  - tests/ — existing unit tests (108 passing earlier)

Where new components live (recommended)
--------------------------------------
- src/trustcalc/trust/  — expand with evidence, provenance, trajectory, delegation modules (model.py already here)
  - evidence.py
  - provenance.py
  - trajectory.py
  - delegation.py
- src/trustcalc/authority/  — new deterministic authority engine implementing the trust→authority mapping and policies
  - engine.py
  - policies.yaml (configurable risk-action mappings)
- src/trustcalc/attacks/adaptive/ — adaptive attacker implementations
- src/trustcalc/evaluation/ — experiments, baselines, metrics, ablation harness
- scripts/ — experiment orchestration scripts (reproducible runs)
- docs/ — architecture and research documents (this commit)

Components to implement next (minimal research-critical path)
-------------------------------------------------------------
1. Event logging & trajectory store (small, append-only event log).  (src/trustcalc/runtime or new src/trustcalc/trajectory)
2. Evidence & provenance model — types, schema, source attribution, and helpers to record evidence on observations.
3. TrustState extension — upgrade TrustStore to accept and attribute evidence objects, not only success/failure counts.
4. Authority engine — deterministic mapping that consumes TrustState + risk + context + delegation → decision with explanation.
5. Mock tool environment — small set of tools with metadata and risk levels.
6. Adaptive attacker harness — implement at least one slow-reputation and one hidden-trigger attack.
7. Baseline implementations & experiment runner — scripts to run controlled experiments and collect JSON/CSV outputs.
8. Tests for trust updates, authority decisions, delegation attenuation, and key formal properties.

Assumptions and constraints
---------------------------
- Early prototype uses in-memory TrustStore; persistence (SQLite/Redis) can be added later for long runs.
- Tools will be mocked/sandboxed—no connection to real sensitive systems during development.
- Use deterministic randomness (seeded RNGs) for reproducibility of experiments.
- Prefer simple, interpretable math (Beta/Bayesian) and deterministic authority logic. Do not use LLMs to make the final security decision.

Next artifacts to produce
------------------------
- docs/TRUST_MODEL.md — formal definitions and equations for trust, confidence, evidence, provenance, temporal decay.
- docs/THREAT_MODEL.md — attacker goals, capabilities, attack taxonomy and adaptive attacker design.
- docs/EXPERIMENT_PLAN.md — baselines, metrics, reproducible experiment scripts, seeds and outputs.

Change plan & files to modify
----------------------------
- Add docs: docs/TRUST_MODEL.md, docs/THREAT_MODEL.md, docs/EXPERIMENT_PLAN.md (created alongside this file).
- Add new modules (listed above) under src/trustcalc/* in small, test-driven increments.
- Add tests under tests/ for each new module.

Versioning & reproducibility
---------------------------
- Add runtimes/experiment manifest describing exact pyproject/requirements and seed used for each experiment run.
- Keep all experiments' raw outputs under /outputs/<run-id>/ with metadata.json (seed, config, time).

Approval to proceed
-------------------
Please review this architecture and the repository mapping. After you confirm, the next step will be to create docs/TRUST_MODEL.md, docs/THREAT_MODEL.md, docs/EXPERIMENT_PLAN.md (I will draft them next), then propose the minimal set of code changes to implement the event log and evidence model.