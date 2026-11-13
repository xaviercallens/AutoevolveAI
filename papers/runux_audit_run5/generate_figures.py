#!/usr/bin/env python3
"""
Generate figures for RunuX Audit Run 5 paper.
All numbers come exclusively from dist/anse_rl_campaign_report.json
and the live TPU benchmark suite — no LLM-hallucinated constants.
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    print("[WARN] matplotlib not installed — skipping figure generation", file=sys.stderr)

OUT_DIR = REPO_ROOT / "papers" / "runux_audit_run5"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ----- Load campaign telemetry ------------------------------------------------
campaign_file = REPO_ROOT / "dist" / "anse_rl_campaign_report.json"
with open(campaign_file) as f:
    camp = json.load(f)

# ----- Load TPU telemetry -----------------------------------------------------
tpu_file = REPO_ROOT / "dist" / "gcp_telemetry" / "gcp_tpu_benchmark.json"
with open(tpu_file) as f:
    tpu = json.load(f)

tpu_rep = tpu.get("tpu_benchmark_report", {})
tpu_results = tpu_rep.get("results", [])

# ----- Figure 1: Bar chart – gate outcomes ------------------------------------
if HAS_MPL:
    fig, ax = plt.subplots(figsize=(7, 4))
    gates = [
        ("Iso-80", camp["iso_80_gate_passed"]),
        ("Iso-90", camp["iso_90_gate_passed"]),
        ("Iso-100", camp["iso_100_gate_passed"]),
        ("Deg-50", camp["degradation_50_gate_passed"]),
        ("Gain-10", camp["perf_gain_10_gate_passed"]),
        ("Gain-20", camp["perf_gain_20_gate_passed"]),
        ("Gain-30", camp["perf_gain_30_gate_passed"]),
        ("AI-50", camp["ai_speedup_50_gate_passed"]),
    ]
    names = [g[0] for g in gates]
    vals = [1.0 if g[1] else 0.0 for g in gates]
    colors = ["#2ecc71" if v else "#e74c3c" for v in vals]
    bars = ax.bar(names, vals, color=colors, edgecolor="black", linewidth=0.7)
    ax.set_ylim(0, 1.3)
    ax.set_yticks([0, 0.5, 1.0])
    ax.set_yticklabels(["FAIL", "0.5", "PASS"])
    ax.set_title("ANSE-RL Run 5: Gate Pass/Fail Summary", fontsize=11, fontweight="bold")
    ax.set_ylabel("Gate Status")
    ax.set_xlabel("Gate ID")
    for bar, v in zip(bars, vals):
        label = "PASS" if v > 0 else "FAIL"
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.04, label,
                ha="center", va="bottom", fontsize=8, fontweight="bold")
    fig.tight_layout()
    fig1_path = OUT_DIR / "fig1_gate_summary.pdf"
    fig.savefig(fig1_path, format="pdf", dpi=150)
    plt.close(fig)
    print(f"[FIG1] Saved: {fig1_path}")

# ----- Figure 2: Line plot – latency across workloads -------------------------
if HAS_MPL and tpu_results:
    fig, ax = plt.subplots(figsize=(7, 4))
    workloads = [r.get("test_name", f"W{i}") for i, r in enumerate(tpu_results)]
    linux_lats = [r.get("linux_latency_us", 0) for r in tpu_results]
    runux_lats = [r.get("runux_latency_us", 0) for r in tpu_results]
    x = range(len(workloads))
    ax.plot(x, linux_lats, "o-", color="#3498db", label="Linux (simulated)", linewidth=2)
    ax.plot(x, runux_lats, "s-", color="#e67e22", label="RunuX", linewidth=2)
    ax.set_xticks(list(x))
    ax.set_xticklabels([w.replace("_", "\n") for w in workloads], fontsize=8)
    ax.set_ylabel(r"Latency ($\mu$s)")
    ax.set_title("TPU Microbenchmark: Linux vs. RunuX Latency", fontsize=11, fontweight="bold")
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig2_path = OUT_DIR / "fig2_tpu_latency.pdf"
    fig.savefig(fig2_path, format="pdf", dpi=150)
    plt.close(fig)
    print(f"[FIG2] Saved: {fig2_path}")

# ----- Figure 3: Syscall ops ratio – 30 LMBench vectors ----------------------
if HAS_MPL:
    ep_traces = camp.get("episode_traces", [])
    if ep_traces:
        ep = ep_traces[0]
        syscall_results = ep.get("report", {}).get("results", [])
        if syscall_results:
            names30 = [r["syscall_name"].replace("sys_", "") for r in syscall_results]
            linux30 = [r["linux_latency_us"] for r in syscall_results]
            runux30 = [r["runux_latency_us"] for r in syscall_results]
            ops_ratios = [
                (l / max(0.01, r)) for l, r in zip(linux30, runux30)
            ]
            fig, ax = plt.subplots(figsize=(10, 4))
            bar_colors = ["#27ae60" if o >= 1.0 else "#e74c3c" for o in ops_ratios]
            bars = ax.bar(range(len(names30)), ops_ratios, color=bar_colors, edgecolor="k", linewidth=0.5)
            ax.axhline(1.0, color="navy", linestyle="--", linewidth=1.2, label="Iso-performance (1.0x)")
            ax.axhline(0.67, color="red", linestyle=":", linewidth=1.0, label="Deg-50 floor (0.67x)")
            ax.set_xticks(range(len(names30)))
            ax.set_xticklabels(names30, rotation=45, ha="right", fontsize=6)
            ax.set_ylabel("Ops Ratio (Linux lat / RunuX lat)")
            ax.set_title("30-Syscall Ops Ratio: RunuX vs. Linux Oracle", fontsize=11, fontweight="bold")
            ax.legend(fontsize=8)
            fig.tight_layout()
            fig3_path = OUT_DIR / "fig3_syscall_ops_ratio.pdf"
            fig.savefig(fig3_path, format="pdf", dpi=150)
            plt.close(fig)
            print(f"[FIG3] Saved: {fig3_path}")

print("[FIGURES] All figures generated. Campaign receipt:", camp.get("receipt", "?"))
print(f"  Parity: {camp['avg_functional_parity']*100:.1f}%  |  Gain: +{camp['avg_perf_gain_pct']:.1f}%  |  TPU AI: +{camp['tpu_global_ai_speedup_pct']:.1f}%")
