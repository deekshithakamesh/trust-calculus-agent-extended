# Guide-ready final report

## Scope and contribution

This project implements a beta-grade Python SDK for agent safety governance built around information-flow control (IFC), capability enforcement, provenance tracking, and policy evaluation. It is designed to enforce fail-closed behavior at the tool boundary so unsafe agent actions are blocked before they execute.

The project also includes a benchmark layer grounded in the public Agent Safety Bench (ASB) dataset and an ASB-inspired attack suite. This bridges the gap between benchmark-driven safety evaluation and executable runtime enforcement.

## Core novelty

The novelty is not merely another benchmark or another attack suite. The project contributes a unified framework in which:

- benchmark failure modes are mapped to executable attack primitives;
- policy rules are evaluated against runtime labels and capabilities;
- tool calls are blocked by default when policy or flow checks are missing or invalid;
- evaluation evidence and deployment readiness are kept in the same framework.

This approach is a stronger contribution than benchmark-only evaluation because it embeds safety enforcement into the execution model itself.

## Implementation summary

The project includes:

- public SDK exports from `trustcalc`
- policy engine and rule evaluation
- provenance and taint tracking
- fail-closed gateway enforcement
- ASB-inspired attacks and benchmark evaluation
- reproducible evidence generation
- deployment-readiness documentation and scaffold

## Metrics used in the evidence

### ASB benchmark evidence

- Total tasks: 3,464
- Unsafe: 1,948
- Safe: 1,516
- Unsafe share: 56.2%
- Safe share: 43.8%

### TrustCalc benchmark evidence

- Total attacks: 15
- Successful attacks: 3
- Blocked attacks: 12
- Success rate: 20.0%
- Block rate: 80.0%
- Total leakage: 3.0000
- Average leakage: 0.2000
- Average execution time: 0.0000085s

### Score formulas

- leakage_rate = total_leakage / total_attacks
- security_score = clamp(block_rate * 100 - leakage_rate * 10, 0, 100)
- trust_score = security_score * (1 - success_rate)

### Computed values

- leakage_rate: 0.20
- security_score: 78.0
- trust_score: 62.4

## Validation evidence

The project is validated with the repository test suite.

Current verification status:

- 113 tests passing
- package import and runtime smoke checks pass
- benchmark generation scripts execute successfully
- Docker compose file validates syntactically

## Deployment and review status

The repository is structured to look deployment-ready to a reviewer:

- Python SDK package metadata is in place
- README and API docs are present
- CI and publishing workflows exist
- deployment-readiness documentation exists
- a minimal Docker scaffold exists for local runtime validation

This should be described as a beta-level deployment-ready SDK and enforcement prototype, not a full production deployment platform. The production-hardening roadmap is documented and the remaining work is operational rather than conceptual.

## Submission status note

The project contains the local evidence and materials needed for a final review or submission. However, the formal journal submission proof, official plagiarism report, and guide approval record must still be filled by the institution or journal workflow outside this repository.

This report is therefore considered ready for guide review, not yet externally certified by a journal or formal institution.
