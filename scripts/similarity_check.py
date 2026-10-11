#!/usr/bin/env python3
"""Generate a local lexical similarity report for project documents."""

from __future__ import annotations

import difflib
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "README.md",
    ROOT / "docs" / "sdk_api.md",
    ROOT / "docs" / "deployment_readiness.md",
    ROOT / "docs" / "architecture.md",
    ROOT / "artifacts" / "sdk-evidence" / "report.md",
    ROOT / "artifacts" / "asb-gap-analysis" / "report.md",
    ROOT / "thesis" / "report.tex",
]


def iter_files() -> Iterable[Path]:
    for path in TARGETS:
        if path.exists():
            yield path


def normalize(text: str) -> str:
    return " ".join(text.lower().replace("\n", " ").split())


def main() -> None:
    files = list(iter_files())
    print("Similarity report for project documents")
    print("=" * 60)
    for idx, left in enumerate(files):
        for right in files[idx + 1 :]:
            left_text = left.read_text(encoding="utf-8", errors="ignore")
            right_text = right.read_text(encoding="utf-8", errors="ignore")
            ratio = difflib.SequenceMatcher(
                None,
                normalize(left_text),
                normalize(right_text),
            ).ratio()
            print(f"{left.name} vs {right.name}: {ratio:.2%}")


if __name__ == "__main__":
    main()
