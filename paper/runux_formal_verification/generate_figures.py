#!/usr/bin/env python3
"""
generate_paper_figures.py — Generate publication-grade figures for the RunuX Lean 4
formal verification paper.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

FIG_DIR = Path("/home/xavkal/.gemini/antigravity/worktrees/AutoevolveAI/clone_rust_linux_kernel/paper/runux_formal_verification/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Set high-quality typography
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
    "figure.dpi": 300,
})

def generate_wave_evolution_plot():
    waves = ["Base", "W4", "W8", "W12", "W14", "W15", "W16"]
    x = np.arange(len(waves))
    
    stubs = [259, 259, 254, 220, 172, 165, 0]
    sorrys = [249, 245, 217, 194, 142, 96, 87]
    tests = [335, 344, 385, 397, 417, 425, 609]
    safety = [0.1397, 0.1410, 0.1600, 0.1800, 0.4087, 0.4038, 0.6098]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    
    # Left subplot: Debts & Tests
    ax1.plot(x, stubs, "r-o", linewidth=2, label="Const Stub Fns (Eradicated $\\to$ 0)")
    ax1.plot(x, sorrys, "b-s", linewidth=2, label="Formal Sorries ($249 \\to 87$)")
    ax1.plot(x, tests, "g-^", linewidth=2, label="Unit Tests ($335 \\to 609$)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(waves)
    ax1.set_xlabel("Development Wave")
    ax1.set_ylabel("Count")
    ax1.set_title("Formal Debt & Test Suite Scaling")
    ax1.grid(True, linestyle="--", alpha=0.6)
    ax1.legend(loc="center right")
    
    # Right subplot: Safety Comment Ratio
    ax2.plot(x, safety, "m-D", linewidth=2.2, label="Safety Ratio (Comments / Unsafe Blocks)")
    ax2.axhline(0.40, color="gray", linestyle=":", label="Ratchet Gate (0.40)")
    ax2.set_xticks(x)
    ax2.set_xticklabels(waves)
    ax2.set_xlabel("Development Wave")
    ax2.set_ylabel("Safety Comment Ratio")
    ax2.set_title("Unsafe Surface Documentation Surge")
    ax2.grid(True, linestyle="--", alpha=0.6)
    ax2.legend(loc="upper left")
    
    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig_wave_evolution.pdf", format="pdf")
    fig.savefig(FIG_DIR / "fig_wave_evolution.png", format="png")
    plt.close(fig)
    print("Generated fig_wave_evolution.pdf / .png")

def generate_tier_energy_plot():
    tiers = ["Tier 1\n(Bulk Hardening)", "Tier 2\n(Architecture)", "Tier 3\n(Lean 4 Proofs)", "Tier 4\n(Deep Subsystems)"]
    x = np.arange(len(tiers))
    width = 0.35
    
    # Real telemetry from workflowrunux_all.py
    wall_time = [23.12, 23.17, 20.73, 13.20]
    energy = [17852.56, 23321.35, 20903.08, 11747.15]
    tokens = [6, 6, 5, 6]  # 23 total
    
    fig, ax1 = plt.subplots(figsize=(8.5, 4.5))
    
    color = "tab:blue"
    ax1.set_xlabel("Verification Tier")
    ax1.set_ylabel("Wall Clock Duration (seconds)", color=color)
    bars1 = ax1.bar(x - width/2, wall_time, width, label="Wall Time (s)", color=color, alpha=0.85)
    ax1.tick_params(axis="y", labelcolor=color)
    ax1.set_ylim(0, 30)
    
    ax2 = ax1.twinx()
    color = "tab:purple"
    ax2.set_ylabel("Thermodynamic Action Energy ($E$)", color=color)
    bars2 = ax2.bar(x + width/2, energy, width, label="System Energy ($E$)", color=color, alpha=0.85)
    ax2.tick_params(axis="y", labelcolor=color)
    ax2.set_ylim(0, 30000)
    
    # Add proof token badges on top of bars
    for i, tok in enumerate(tokens):
        ax1.text(x[i] - width/2, wall_time[i] + 0.8, f"{tok} Tokens", ha="center", fontsize=9, fontweight="bold")
    
    plt.title("RunuX Master Orchestrator: Multi-Tier Thermodynamic Performance (100% Green)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(tiers)
    
    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig_tier_energy.pdf", format="pdf")
    fig.savefig(FIG_DIR / "fig_tier_energy.png", format="png")
    plt.close(fig)
    print("Generated fig_tier_energy.pdf / .png")

def generate_module_distribution_plot():
    # Top formal specification modules by LOC
    modules = [
        "RunuxDefenses", "NatProto", "FibSemantics", "AfInet", 
        "AfInet6", "Slab", "ConntrackICMPv6", "ConntrackICMP",
        "PageAlloc", "NatCore", "ConntrackSCTP", "ConntrackTCP"
    ]
    locs = [1543, 775, 713, 692, 664, 623, 614, 600, 585, 584, 572, 522]
    
    fig, ax = plt.subplots(figsize=(10, 4.5))
    y_pos = np.arange(len(modules))
    
    colors = plt.cm.viridis(np.linspace(0.2, 0.85, len(modules)))
    bars = ax.barh(y_pos, locs, color=colors, align="center")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(modules)
    ax.invert_yaxis()  # Top-down
    ax.set_xlabel("Formal Specification Lines of Code (Lean 4)")
    ax.set_title("Distribution of Formal Code Across High-Assurance Kernel Subsystems")
    
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 20, bar.get_y() + bar.get_height()/2, f"{int(width):,} LOC",
                va="center", ha="left", fontsize=9)
    
    ax.set_xlim(0, 1850)
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    
    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig_module_distribution.pdf", format="pdf")
    fig.savefig(FIG_DIR / "fig_module_distribution.png", format="png")
    plt.close(fig)
    print("Generated fig_module_distribution.pdf / .png")

if __name__ == "__main__":
    generate_wave_evolution_plot()
    generate_tier_energy_plot()
    generate_module_distribution_plot()
