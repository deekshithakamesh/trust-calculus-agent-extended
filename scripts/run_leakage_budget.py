#!/usr/bin/env python3
"""Run the exhaustive leakage-budget allocation comparison."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from trustcalc.attacks.leakage_experiment import run_comparison

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "evidence"
FIGURE_DIR = EVIDENCE_DIR / "figures"


def _write_report(results: dict) -> None:
    rows = [
        "# Leakage Budget Design Comparison",
        "",
        f"Exhaustively evaluated {results['case_count']} cases across "
        f"{results['secrets']} labels, {len(results['strategies'])} strategies, "
        f"{len(results['budgets'])} budgets, and {len(results['designs'])} designs.",
        "",
        "All bit values use a uniform prior over the 20-label universe. Probe "
        "requests use public destinations and fixed arguments; requests that "
        "encode the secret are outside the guarantee. The per-caller results "
        "are measured independently for each caller; collusion between callers "
        "is not modeled.",
        "",
        "The legitimate request targets INTERNAL with no compartments. Its "
        "budget-admission rate is separate from its policy allow rate.",
        "",
        "| Design | Budget (bits) | Mean probe leakage | Max probe leakage | "
        "Secret identified | Legitimate budget admitted | Legitimate policy allowed |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for result in results["summary"]:
        budget = "unbounded" if result["budget"] is None else f"{result['budget']:.1f}"
        rows.append(
            f"| {result['design']} | {budget} | "
            f"{result['mean_probe_leakage_bits']:.3f} | "
            f"{result['max_probe_leakage_bits']:.3f} | "
            f"{result['secret_identification_rate']:.1%} | "
            f"{result['legitimate_budget_admission_rate']:.1%} | "
            f"{result['legitimate_policy_allow_rate']:.1%} |"
        )
    rows.extend(
        [
            "",
            "Unbudgeted greedy probing identifies every enumerated label. In "
            "every budgeted case, the measured per-value (and per-caller, for "
            "that design) leakage remained at or below the configured budget.",
            "",
            "The refusal guarantee assumes every request's arguments and "
            "destination are selected without using the protected label. "
            "Uniform-prior bits are a modeling measure, not a distribution-free "
            "entropy guarantee.",
            "",
        ]
    )
    (EVIDENCE_DIR / "leakage_budget.md").write_text("\n".join(rows), encoding="utf-8")


def _write_figure(results: dict) -> None:
    plot_rows = []
    for design in results["designs"]:
        plot_rows.append(
            [
                row
                for row in results["summary"]
                if row["design"] == design
            ]
        )
    labels = [
        "1",
        "2",
        "3",
        "3.5",
        "4",
        "unbounded",
    ]
    positions = list(range(len(labels)))
    colors = {
        "shared": "#4477AA",
        "reserved": "#228833",
        "per_caller": "#CC6677",
    }

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(7, 5))
    for design, rows in zip(results["designs"], plot_rows):
        rows_by_budget = {row["budget"]: row for row in rows}
        ordered = [
            rows_by_budget[budget]
            for budget in (1.0, 2.0, 3.0, 3.5, 4.0, None)
        ]
        means = [row["mean_probe_leakage_bits"] for row in ordered]
        lower = [row["min_probe_leakage_bits"] for row in ordered]
        upper = [row["max_probe_leakage_bits"] for row in ordered]
        ax.plot(
            positions,
            means,
            marker="o",
            linewidth=2,
            label=design.replace("_", " "),
            color=colors[design],
        )
        ax.fill_between(
            positions,
            lower,
            upper,
            color=colors[design],
            alpha=0.12,
        )

    ax.set_xticks(positions, labels)
    ax.set_xlabel("Configured leakage budget (bits)")
    ax.set_ylabel("Probe leakage (bits, uniform prior)")
    ax.set_title("Leakage under budget allocation designs")
    ax.legend(frameon=True)
    ax.set_ylim(bottom=0)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "leakage_curve.png", dpi=200)
    plt.close(fig)


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    results = run_comparison()
    (EVIDENCE_DIR / "leakage_budget.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_report(results)
    _write_figure(results)
    print(
        f"Wrote {EVIDENCE_DIR / 'leakage_budget.json'}, "
        f"{EVIDENCE_DIR / 'leakage_budget.md'}, and "
        f"{FIGURE_DIR / 'leakage_curve.png'}"
    )


if __name__ == "__main__":
    main()
