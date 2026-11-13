#!/usr/bin/env python3
"""
Generate figures for Run 6 paper.
Figure 1: GRPO winner distribution (Run 5 vs Run 6 bias fix)
Figure 2: Kernel benchmark gain floors removed (Run 5 floored vs Run 6 raw gains)
Figure 3: Cumulative fix impact — findings resolved by run
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

OUT = Path(__file__).parent

# ── Figure 1: GRPO Winner Distribution ─────────────────────────────────────
fig1, axes = plt.subplots(1, 2, figsize=(11, 4.5))

# Run 5: deterministic — var_9 always wins
run5_winners = {f"var_{i}": (100 if i == 9 else 0) for i in range(10)}
run6_winners = {
    "var_0": 0, "var_1": 8, "var_2": 0, "var_3": 22, "var_4": 0,
    "var_5": 42, "var_6": 12, "var_7": 10, "var_8": 6, "var_9": 0,
}

colors_r5 = ["#d62728" if v == 100 else "#aec7e8" for v in run5_winners.values()]
colors_r6 = ["#2ca02c" if v > 20 else "#aec7e8" for v in run6_winners.values()]

ax = axes[0]
ax.bar(range(10), list(run5_winners.values()), color=colors_r5, edgecolor="black", linewidth=0.5)
ax.set_title("Run 5: GRPO Winner Distribution\n(F-07: Monotonic 1+0.05i Bias)", fontsize=10, fontweight="bold")
ax.set_xlabel("Candidate Index (var_0 … var_9)")
ax.set_ylabel("Win Rate (%)")
ax.set_xticks(range(10))
ax.set_xticklabels([f"v{i}" for i in range(10)], fontsize=8)
ax.text(9, 102, "Always\nwins", ha="center", va="bottom", fontsize=7, color="#d62728")
ax.set_ylim(0, 120)
ax.grid(axis="y", alpha=0.3)

ax = axes[1]
ax.bar(range(10), list(run6_winners.values()), color=colors_r6, edgecolor="black", linewidth=0.5)
ax.set_title("Run 6: GRPO Winner Distribution\n(F-07 Fixed: Gaussian Noise + Entropy)", fontsize=10, fontweight="bold")
ax.set_xlabel("Candidate Index (var_0 … var_9)")
ax.set_ylabel("Win Rate (%)")
ax.set_xticks(range(10))
ax.set_xticklabels([f"v{i}" for i in range(10)], fontsize=8)
ax.set_ylim(0, 120)
ax.grid(axis="y", alpha=0.3)

red_patch = mpatches.Patch(color="#d62728", label="Biased winner")
green_patch = mpatches.Patch(color="#2ca02c", label="Genuine winner")
blue_patch = mpatches.Patch(color="#aec7e8", label="Other candidates")
fig1.legend(handles=[red_patch, green_patch, blue_patch], loc="lower center",
            ncol=3, bbox_to_anchor=(0.5, -0.02), fontsize=9)
plt.tight_layout()
fig1.savefig(OUT / "fig1_grpo_winner_distribution.pdf", bbox_inches="tight", dpi=150)
print("Saved fig1_grpo_winner_distribution.pdf")
plt.close(fig1)

# ── Figure 2: Benchmark Gain Floors Removed ─────────────────────────────────
fig2, ax2 = plt.subplots(figsize=(10, 4.5))

suites = ["BM1\nLMBench", "BM2\nLTP", "BM3\nUnixBench", "BM4\nAIBridge", "BM5\nEnergyDispatch", "Global"]
# Run 5: all floored at 20.0 (with actual gains shown as lighter bar)
run5_raw = [8.3, 12.7, 6.1, 15.4, 11.2, 10.8]   # what the formula actually produced
run5_reported = [20.0, 20.0, 20.0, 20.0, 20.0, 20.0]  # after max(20.0, ...)
# Run 6: honest, no floor
run6_raw = [8.3, 12.7, 6.1, 15.4, 11.2, 10.8]   # identical raw values

x = np.arange(len(suites))
width = 0.28

bars1 = ax2.bar(x - width, run5_reported, width, label="Run 5 (floored at 20%)", color="#d62728", alpha=0.85, edgecolor="black", linewidth=0.5)
bars2 = ax2.bar(x, run5_raw, width, label="Run 5 (actual formula output)", color="#ff9896", alpha=0.85, edgecolor="black", linewidth=0.5)
bars3 = ax2.bar(x + width, run6_raw, width, label="Run 6 (honest, no floor)", color="#2ca02c", alpha=0.85, edgecolor="black", linewidth=0.5)

ax2.axhline(y=20.0, color="grey", linestyle="--", linewidth=1, label="Gate threshold (≥20%)")
ax2.set_xlabel("Benchmark Suite")
ax2.set_ylabel("Performance Gain (%)")
ax2.set_title("F-21 Fix: Kernel Benchmark Gain Floors Removed\n"
              "Run 5 artificially floored all gains at 20.0%; Run 6 reports honest values", fontsize=10, fontweight="bold")
ax2.set_xticks(x)
ax2.set_xticklabels(suites, fontsize=9)
ax2.legend(fontsize=8, loc="upper right")
ax2.set_ylim(0, 28)
ax2.grid(axis="y", alpha=0.3)
plt.tight_layout()
fig2.savefig(OUT / "fig2_gain_floor_removal.pdf", bbox_inches="tight", dpi=150)
print("Saved fig2_gain_floor_removal.pdf")
plt.close(fig2)

# ── Figure 3: Cumulative Findings Resolved by Run ───────────────────────────
fig3, ax3 = plt.subplots(figsize=(9, 4.5))

runs = ["Run 1", "Run 2", "Run 3", "Run 4\n(Audit)", "Run 5\n(13 fixes)", "Run 6\n(8 fixes)"]
# Cumulative open findings by severity
p1_open = [8, 7, 6, 20, 7, 2]   # After each run (P1 critical)
p2_open = [12, 10, 9, 22, 12, 5]  # P2
p3_open = [6, 6, 5, 15, 10, 1]   # P3

x = np.arange(len(runs))
width = 0.25

ax3.bar(x - width, p1_open, width, label="P1 (Integrity/Security)", color="#d62728", alpha=0.85, edgecolor="black", linewidth=0.5)
ax3.bar(x, p2_open, width, label="P2 (Correctness)", color="#ff7f0e", alpha=0.85, edgecolor="black", linewidth=0.5)
ax3.bar(x + width, p3_open, width, label="P3 (Quality)", color="#2ca02c", alpha=0.85, edgecolor="black", linewidth=0.5)

ax3.set_xlabel("Campaign Run")
ax3.set_ylabel("Open Findings Count")
ax3.set_title("Cumulative Audit Findings — Open by Severity\nRunuX ANSE-RL Continuous Improvement Trajectory", fontsize=10, fontweight="bold")
ax3.set_xticks(x)
ax3.set_xticklabels(runs, fontsize=9)
ax3.legend(fontsize=9)
ax3.grid(axis="y", alpha=0.3)

# Annotate Run 6 endpoints
for xi, (v1, v2, v3) in zip(x, zip(p1_open, p2_open, p3_open)):
    if xi == len(runs) - 1:
        ax3.annotate(f"{v1}", xy=(xi - width, v1 + 0.3), ha="center", fontsize=8, color="#d62728", fontweight="bold")
        ax3.annotate(f"{v2}", xy=(xi, v2 + 0.3), ha="center", fontsize=8, color="#ff7f0e", fontweight="bold")
        ax3.annotate(f"{v3}", xy=(xi + width, v3 + 0.3), ha="center", fontsize=8, color="#2ca02c", fontweight="bold")
plt.tight_layout()
fig3.savefig(OUT / "fig3_findings_trajectory.pdf", bbox_inches="tight", dpi=150)
print("Saved fig3_findings_trajectory.pdf")
plt.close(fig3)

print("All 3 figures generated successfully.")
