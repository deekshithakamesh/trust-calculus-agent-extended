#!/usr/bin/env python3
"""Run the denial-feedback information probe."""

from __future__ import annotations

import json
from pathlib import Path

from trustcalc.attacks.denial_probe import run_denial_probe

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "evidence"


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    results = run_denial_probe()
    (EVIDENCE_DIR / "denial_probe.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    denied = next(
        observation
        for observation in results["observations"]
        if not observation["allowed"]
    )
    report = "\n".join(
        [
            "# Denial Feedback Probe",
            "",
            "With fixed arguments and a PUBLIC destination, the two-label "
            "uniform-prior probe returns different allow/deny statuses for "
            "PUBLIC and SECRET sources. The status therefore carries "
            f"{results['allow_deny_channel_bits']:.1f} bit in this probe even "
            "though denial text is generic.",
            "",
            f"Caller-visible denial: `{denied['caller_feedback']}`",
            "",
            f"Capability name disclosed in denial: "
            f"`{results['capability_name_disclosed']}`.",
            f"Full capability reason retained in audit: "
            f"`{results['capability_audit_keeps_full_reason']}`.",
            "",
            "This result assumes the request is independent of the protected "
            "label. A destination or argument selected based on that label can "
            "also leak through whether a request is refused and is outside this "
            "probe's guarantee.",
            "",
        ]
    )
    (EVIDENCE_DIR / "denial_probe.md").write_text(report, encoding="utf-8")
    print(
        f"Wrote {EVIDENCE_DIR / 'denial_probe.json'} and "
        f"{EVIDENCE_DIR / 'denial_probe.md'}"
    )


if __name__ == "__main__":
    main()
