# Deployment readiness plan

This document captures the minimal production-readiness path for the TrustCalc SDK.
It is intentionally explicit: the project is a strong beta SDK and research prototype,
not a fully hardened production deployment system.

## Current status

TrustCalc already contains the core building blocks for a production-oriented agent
safety layer:

- security labels and information-flow semantics
- provenance and taint propagation
- capability checks and rule evaluation
- policy enforcement at the tool gateway boundary
- ASB-inspired attack families for evaluation and red-teaming

The missing work is operational hardening: deployment boundaries, sandboxing,
secrets handling, external service protections, and runtime observability.

## Deployment architecture

A realistic deployment shape is:

1. User or model request enters the application boundary.
2. The agent runtime creates an `ExecutionContext` with labels, capabilities, and
   identity metadata.
3. The `PolicyEnforcer` checks authorization and information-flow constraints.
4. Tool invocations are routed through `ToolGateway`.
5. The runtime validates arguments, checks provenance, and denies by default on
   missing or invalid policy state.
6. Audit and telemetry logs are emitted for every decision.

This architecture keeps the policy decision boundary close to the tool surface,
which is the correct place to enforce fail-closed behavior.

## Required production controls

Before calling this project production-ready, the deployment should add:

- isolated tool execution sandboxing
- per-tenant or per-session policy isolation
- secret management and redaction pipelines
- container runtime hardening (non-root user, minimal base image, read-only root filesystem)
- comprehensive audit logging with tamper-resistant storage
- structured policy versioning and release tracking
- canary rollout and rollback procedures
- red-team evaluation using ASB-inspired and custom adversarial scenarios

## Deployment topology

A minimal production topology should place the policy layer in front of the tool
router and execution runtime:

- public HTTP or agent gateway
- TrustCalc policy service / SDK runtime
- tool execution sandbox or remote executor
- audit sink and policy registry

The important design property is that the `ToolGateway` remains the enforcement
boundary. Tools should never execute directly without passing through
authorization and information-flow checks.

## Local deployment scaffold

This repository includes a minimal Docker scaffold to support local validation:

```bash
docker compose build

docker compose run --rm trustcalc
```

The default container smoke test verifies importability and SDK loading without
starting a full model or agent runtime.

This is intentionally a controlled validation scaffold, not a full production
service definition.

## Production gates

The project should not be described as production-deployed until the following
conditions are met:

1. all tool calls are isolated from the host system
2. policy evaluation is enforced for every tool boundary
3. capability and label checks are verified in integration tests
4. audit logs are retained and reviewed
5. unsafe actions are confirmed blocked in adaptive red-team runs
6. deployment configuration is reviewed for secrets, identity, and tenancy separation

## Recommendation

Use this repository as a beta-grade safety SDK and enforcement prototype that is
ready for controlled evaluation, red-teaming, and partner demos. It is not yet a
fully hardened production platform by itself, but it is now a credible foundation
for that next step.
