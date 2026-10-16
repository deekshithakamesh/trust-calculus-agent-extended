# TrustCalc

TrustCalc is a Python SDK for enforcing information-flow, capability, and
policy controls around agent tool execution. It combines security labels,
taint tracking, provenance, a policy engine, and an auditable tool gateway.

## Installation

```bash
python -m pip install trust-calculus-agent-extended
```

For local development:

```bash
git clone https://github.com/deekshithakamesh/trust-calculus-agent-extended.git
cd trust-calculus-agent-extended
python -m pip install -e '.[dev]'
python -m pytest -q
```

## Quick start

```python
from trustcalc import (
    ExecutionContext,
    GatewayValidator,
    PUBLIC_LABEL,
    PolicyEngine,
    PolicyEnforcer,
    TaintTracker,
    ToolGateway,
    ToolRegistry,
)

tracker = TaintTracker()
message = tracker.wrap("hello", PUBLIC_LABEL, name="message")

registry = ToolRegistry()
gateway = ToolGateway(
    registry=registry,
    validator=GatewayValidator(),
    enforcer=PolicyEnforcer(PolicyEngine()),
)

context = ExecutionContext(
    labels={"source": message.label, "destination": PUBLIC_LABEL},
)
decision = gateway.authorize("my-tool", {}, context)
assert decision.denied  # The tool is not registered.
```

Most applications register concrete `Tool` implementations and call
`ToolGateway.execute(...)`. Authorization, argument validation, information
flow checks, and audit events are then applied consistently at the boundary.

## Core concepts

- `SecurityLabel` models integrity, confidentiality, and compartments.
- `TrustedValue` couples a value to its label and provenance.
- `TaintTracker` wraps values, propagates labels, and records lineage.
- `PolicyEngine` evaluates declarative rules and returns immutable `Decision`
  objects rather than bare booleans.
- `ToolGateway` is the policy enforcement point for tool execution.
- `ExecutionContext` carries capabilities, labels, identity, and metadata.

The stable top-level API is exported from `trustcalc`; lower-level modules are
available for advanced integrations.

## Leakage budgets

`BudgetedGateway` limits the information exposed by repeated allow/deny
responses. For each protected value it tracks the set of source labels
consistent with the transcript and refuses a request when its worst-case
outcome would exceed the configured budget. The default measure assumes a
uniform prior and reports `log2(universe size / remaining labels)` bits. The
label universe must include the true source label.

The guarantee assumes every request is built from public information: neither
its arguments nor its destination may depend on the protected value. A
secret-dependent destination can still reveal information through whether a
request is refused. A non-uniform prior changes the reported bit values and is
model-dependent; the formal guarantee documented and tested here is a bound
under the uniform prior only.

`reserved_fraction` protects that fraction of the budget from requests not
marked `legitimate=True`. Set `per_caller=True` to maintain separate budgets
using `ExecutionContext.user_id`; callers have independent transcripts, so
collusion between callers is not covered by that accounting. Use a distinct,
stable `protected_value_id` when tracking separate protected values. Denials
are returned as `Tool call denied by policy.` by default while the audit log
retains the full reason. Set `expose_denial_reasons=True` only when disclosure
is acceptable.

Run the exhaustive comparison of shared, reserved, and per-caller budgets with:

```bash
PYTHONPATH=src python scripts/run_leakage_budget.py
```

It enumerates 20 labels, seven probing strategies, and six budget settings,
then writes `evidence/leakage_budget.json`, `evidence/leakage_budget.md`, and
`evidence/figures/leakage_curve.png`.

Run the denial-feedback probe with:

```bash
PYTHONPATH=src python scripts/run_denial_probe.py
```

It writes `evidence/denial_probe.json` and `evidence/denial_probe.md`.

## Documentation and examples

- [Architecture](docs/architecture.md)
- [SDK API reference](docs/sdk_api.md)
- [Evaluation evidence and scoring](artifacts/sdk-evidence/report.md)
- [Advanced review graphs](artifacts/advanced-evidence/auroc_curve.png)
- [ASB gap analysis](artifacts/asb-gap-analysis/report.md)
- [Deployment readiness](docs/deployment_readiness.md)
- [Final report draft](docs/final_report.md)
- [Similarity report](docs/plagiarism_report.md)
- [Journal submission readiness](docs/journal_submission_readiness.md)
- [Policy authoring guide](docs/policy_authoring_guide.md)
- [Threat model](docs/design/threat_model.md)
- Runnable examples are in `examples/`

## ASB-inspired attack families

The project also includes ASB-style benchmark scenarios for the most common
agent security failure modes:

- direct prompt injection
- observation prompt injection
- memory poisoning
- plan-of-thought backdoor execution
- mixed multi-stage attacks

These are exposed through the `trustcalc.attacks` package, including
`DirectPromptInjectionAttack`, `ObservationPromptInjectionAttack`,
`MemoryPoisoningAttack`, `PlanOfThoughtBackdoorAttack`, and `MixedASBAttack`.

## ASB dataset gap analysis

The project additionally includes a public benchmark-grounded analysis using the
Hugging Face dataset `aradhye/agent-safety-bench`, with charts and a short gap
analysis under `artifacts/asb-gap-analysis/`.

## Project status

TrustCalc is currently an early SDK release (`0.1.x`). The public Python API
is usable, but consumers should expect API refinement before a `1.0.0` release.
Security-sensitive deployments should review the policy configuration and
threat model for their environment.

## License

See [LICENSE](LICENSE).