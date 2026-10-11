# ASB dataset gap analysis

The public Agent Safety Bench dataset provides the benchmark substrate for adversarial tool-use tasks.
It contains 3464 tasks spanning a broad set of risk categories, with 1948 labeled unsafe and 1516 labeled safe.

## Snapshot

- Total records: 3464
- Unsafe share: 56.2%
- Safe share: 43.8%
- Average risk tags per task: 1.000
- Environments observed: 350

## Dominant risk patterns

The most common risk families in the dataset are:

1. Contribute to harmful / vulnerable code
2. Violate law or ethics / damage society
3. Lead to property loss
4. Lead to physical harm
5. Spread unsafe information / misinformation
6. Compromise availability
7. Leak sensitive data / information
8. Produce unsafe information / misinformation

## Why this matters

ASB is a strong benchmark for identifying the classes of unsafe behaviors that tool-using agents can trigger. However, the dataset alone does not enforce runtime safeguards; it is benchmark evidence, not an execution policy layer.

TrustCalc patches that gap by converting benchmark failure modes into executable attack primitives and by enforcing fail-closed policy semantics, provenance tracking, and capability restrictions. In other words, ASB tells us what is unsafe, while TrustCalc shows how to block it in a deployable SDK.

## Novelty angle

The novelty is not simply adding another benchmark. The novelty is bridging the benchmark-to-enforcement gap:

- public benchmark coverage from ASB
- ASB-inspired attack families inside TrustCalc
- runtime defense semantics through taint tracking, flow checks, and capability gating
- reproducible evidence artifacts and score reports for presentation and review

This turns an evaluation dataset into an actionable safety SDK for agent systems.

