# TODO - Fix Bugs & Research-Grade Improvements

## Layer 1 — Lattice wiring
- [x] Add `SecurityLabel.can_flow_to()` in `labels.py` delegating to `lattice.flows_to()`
- [x] Make `enforcement.check_information_flow()` fail-closed (deny on missing method)
- [x] Wire `check_information_flow()` into `authorize()` so IFC is enforced

## Layer 2 — Runtime/gateway API alignment
- [x] Add `get_taint()` and value-tracking map to `TaintTracker`
- [x] Fix `Mediator` to use correct `PolicyEngine` and `TaintTracker` APIs
- [x] Add `ToolGateway.authorize()` and align `Interpreter` with real gateway
- [x] Wrap tool results as `TrustedValue` in interpreter
- [x] Fix circular import between `runtime/__init__.py` and `gateway` (PEP 562 lazy attrs)

## Layer 3 — Tool hardening
- [x] Add directory sandboxing / path traversal prevention to `FileTool`

## Layer 4 — Research-grade tests
- [x] Unit tests for `can_flow_to`
- [x] Tests for fail-closed IFC in enforcement
- [x] Tests for path traversal prevention
- [x] Integration test for gateway-interpreter

## Layer 5 — Improvements
- [x] Improve `mediator` with full flow/policy integration
- [x] Add provenance integrity checks (`ProvenanceGraph.verify_integrity`)
- [ ] Harden `TaintTracker` flow_check with explicit deny
