# SDK API

The supported consumer-facing imports are available from `trustcalc`.

## Security and values

- `SecurityLabel`, `Integrity`, and `Confidentiality` describe information.
- `PUBLIC_LABEL`, `SECRET_LABEL`, and the other label constants provide common
  policies.
- `TrustedValue[T]` wraps a value with its label and provenance.
- `TaintTracker` wraps, transforms, merges, and checks values.

## Policy and execution

- `PolicyEngine` evaluates policy rules.
- `Decision` and `DecisionReport` provide structured outcomes.
- `ExecutionContext` carries identity, capabilities, labels, and metadata.
- `ToolGateway` validates, authorizes, executes, and audits tool calls.
- `Tool`, `ToolRegistry`, and `PolicyEnforcer` support custom tool integration.

## Errors

Gateway failures use `GatewayError` and its specific subclasses:
`InvalidToolError`, `InvalidArgumentError`, `AuthorizationError`, and
`ToolExecutionError`.

Lower-level modules remain available for advanced integrations, but consumers
should prefer the top-level exports to keep imports stable across releases.
