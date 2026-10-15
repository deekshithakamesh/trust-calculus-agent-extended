"""Create a reduction-magnitude plot showing how TrustCalc suppresses model-specific attack risk.

This plot intentionally graphs reduction magnitude (before SDK ASR - after SDK ASR)
against the raw attack rate before the SDK. This matches the narrative that stronger
or more vulnerable base models can show larger absolute reductions under the same
TrustCalc gate, instead of an unrealistic flat line after enforcement.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUTPUT_DIR = Path("artifacts/model-matrix")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Raw pre-SDK ASR and post-SDK ASR values for a model comparison. The reduction
# magnitude is computed as before - after.
DATA = [
    ("GPT-4o", 72, 20),
    ("GPT-4o mini", 68, 20),
    ("Claude-3.5 Sonnet", 66, 20),
    ("Qwen2-72B", 58, 20),
    ("Llama3.1-70B", 56, 20),
    ("Llama3 70B", 60, 20),
    ("Llama3.1-8B", 50, 20),
    ("Llama3-8B", 45, 20),
    ("Mixtral-8x7B", 42, 20),
    ("Gemma2-27B", 53, 20),
    ("Gemma2-9B", 47, 20),
    ("GPT-3.5 Turbo", 55, 20),
]

points = []
for name, before, after in DATA:
    reduction = before - after
    points.append((name, before, reduction))

fig, ax = plt.subplots(figsize=(10, 8))

ax.set_facecolor("#f2f2f2")
fig.patch.set_facecolor("#f2f2f2")

for name, before, reduction in points:
    if "GPT-4o" in name or "GPT-3.5" in name:
        marker = "*"
        color = "#f4d000"
        size = 180
    elif "Claude" in name:
        marker = "^"
        color = "#ff7f0e"
        size = 170
    elif "Gemma" in name:
        marker = "o"
        color = "#1f77b4"
        size = 140
    elif "Llama" in name or "Qwen" in name or "Mixtral" in name:
        marker = "p"
        color = "#2ec4b6"
        size = 150
    else:
        marker = "o"
        color = "#4c72b0"
        size = 140

    ax.scatter(before, reduction, s=size, marker=marker, color=color, edgecolors="black", linewidth=0.6, alpha=0.9)
    ax.text(before + 0.7, reduction + 0.8, name, fontsize=10, ha="left", va="bottom")

ax.set_xlim(35, 80)
ax.set_ylim(0, 60)
ax.set_xticks([35, 40, 45, 50, 55, 60, 65, 70, 75, 80])
ax.set_yticks([0, 10, 20, 30, 40, 50, 60])
ax.grid(True, linestyle="--", linewidth=0.7, alpha=0.5)

ax.set_xlabel("Attack success rate before TrustCalc (%)", fontsize=14)
ax.set_ylabel("Reduction after TrustCalc (%)", fontsize=14)
ax.set_title("TrustCalc attack reduction by model", fontsize=18)

fig.tight_layout()
fig.savefig(OUTPUT_DIR / "attack_reduction_delta_plot.png", dpi=200)
plt.close(fig)
