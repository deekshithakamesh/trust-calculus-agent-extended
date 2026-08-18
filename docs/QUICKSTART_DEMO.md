Quickstart Demo — Core Trust→Authority

This file describes how to run the demo that exercises the Evidence API, EventLog,
TrustStore and AuthorityEngine.

Requirements
------------
- Python 3.11+ (project uses 3.12 in CI but 3.11+ should work)
- Project virtualenv with requirements installed (see requirements.txt)

Run demo
--------
From the repository root (ensure PYTHONPATH=src if running without packaging):

PYTHONPATH=src .venv/bin/python scripts/demo_core.py

Outputs
-------
- outputs/demo-run/summary.json — summary of trust and decisions before/after attacker evidence
- outputs/demo-run/events.jsonl — JSONL event log for the demo run

Purpose
-------
This demo is intentionally small and deterministic. It demonstrates how Evidence
objects are ingested, how they modify the Beta posterior via TrustStore.record_evidence,
how the EventLog records events, and how the AuthorityEngine makes a deterministic,
auditable decision (ALLOW/VERIFY/RESTRICT/SANDBOX/DENY).