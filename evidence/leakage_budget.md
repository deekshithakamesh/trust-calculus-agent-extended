# Leakage Budget Design Comparison

Exhaustively evaluated 2520 cases across 20 labels, 7 strategies, 6 budgets, and 3 designs.

All bit values use a uniform prior over the 20-label universe. Probe requests use public destinations and fixed arguments; requests that encode the secret are outside the guarantee. Per-caller results are measured independently; collusion between callers is not modeled.

The legitimate request targets INTERNAL with no compartments. Its budget-admission rate is separate from its policy allow rate.

| Design | Budget (bits) | Mean probe leakage | Max probe leakage | Secret identified | Legitimate budget admitted | Legitimate policy allowed |
|---|---:|---:|---:|---:|---:|---:|
| shared | unbounded | 4.322 | 4.322 | 100.0% | 100.0% | 10.0% |
| shared | 4.0 | 2.068 | 3.322 | 0.0% | 95.7% | 7.1% |
| shared | 3.5 | 2.068 | 3.322 | 0.0% | 95.7% | 7.1% |
| shared | 3.0 | 1.279 | 2.737 | 0.0% | 57.9% | 0.0% |
| shared | 2.0 | 0.792 | 2.000 | 0.0% | 32.1% | 0.0% |
| shared | 1.0 | 0.286 | 1.000 | 0.0% | 14.3% | 0.0% |
| reserved | unbounded | 4.322 | 4.322 | 100.0% | 100.0% | 10.0% |
| reserved | 4.0 | 1.279 | 2.737 | 0.0% | 95.7% | 7.1% |
| reserved | 3.5 | 0.985 | 2.322 | 0.0% | 100.0% | 10.0% |
| reserved | 3.0 | 0.792 | 2.000 | 0.0% | 32.1% | 0.0% |
| reserved | 2.0 | 0.563 | 1.322 | 0.0% | 28.6% | 0.0% |
| reserved | 1.0 | 0.000 | 0.000 | 0.0% | 0.0% | 0.0% |
| per_caller | unbounded | 4.322 | 4.322 | 100.0% | 100.0% | 10.0% |
| per_caller | 4.0 | 2.068 | 3.322 | 0.0% | 100.0% | 10.0% |
| per_caller | 3.5 | 2.068 | 3.322 | 0.0% | 100.0% | 10.0% |
| per_caller | 3.0 | 1.279 | 2.737 | 0.0% | 0.0% | 0.0% |
| per_caller | 2.0 | 0.792 | 2.000 | 0.0% | 0.0% | 0.0% |
| per_caller | 1.0 | 0.286 | 1.000 | 0.0% | 0.0% | 0.0% |

Unbudgeted greedy probing identifies every enumerated label. In every budgeted case, measured leakage remained at or below the configured budget under the uniform prior.

The refusal guarantee assumes every request's arguments and destination are selected without using the protected label. Uniform-prior bits are a modeling measure, not a distribution-free entropy guarantee.
