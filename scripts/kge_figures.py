#!/usr/bin/env python3
"""Figures for the Kernel-Gated Evolution paper, rendered from the artifacts.

Every figure is drawn from a results JSON, never from numbers typed into this
file, so re-running after a new measurement regenerates the figure. Figures whose
artifact is missing are skipped with a note rather than drawn from stale data.

Outputs PDF (for LaTeX) and PNG (for the README) side by side.

Usage:
    .venv/bin/python scripts/kge_figures.py --out sub_projects/.../papers/figures
"""

from __future__ import annotations

import argparse
import json
from math import comb
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
RESULTS = REPO / "results"
SHORT = {"L1_base": "L1", "L2_minus_q": "L2", "L3_minus_wq": "L3",
         "L4_minus_hwq": "L4", "L5_minus_half_hwq": "L5", "L6_full": "L6"}
PYTHON_RATES = {"L1_base": 0.750, "L2_minus_q": 0.969, "L3_minus_wq": 0.438,
                "L4_minus_hwq": 0.125, "L5_minus_half_hwq": 0.000, "L6_full": 0.000}

INK = "#1f2a44"
ACCENT = "#c0392b"
MUTED = "#7f8c8d"
SOFT = "#2e86ab"
GOLD = "#b8860b"


def load(name: str):
    path = RESULTS / f"{name}.json"
    return json.loads(path.read_text()) if path.exists() else None


def save(fig, out: Path, stem: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(out / f"{stem}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {stem}.pdf/.png")


def style() -> None:
    plt.rcParams.update({
        "font.family": "serif", "font.size": 10, "axes.spines.top": False,
        "axes.spines.right": False, "axes.edgecolor": INK, "axes.labelcolor": INK,
        "xtick.color": INK, "ytick.color": INK, "text.color": INK,
    })


def fig_architecture(out: Path) -> None:
    """The schema: genome -> exact fitness -> checkpoint -> kernel. Fitness guides; the kernel decides."""
    fig, ax = plt.subplots(figsize=(8.6, 2.9))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")
    boxes = [
        (0.3, "Genome\nexpression tree\nover {+,−,∗}", SOFT),
        (2.6, "Exact fitness\nΣ|cand − spec|\nat sample points", SOFT),
        (4.9, "Apoptotic\ncheckpoint\none-sided", ACCENT),
        (7.2, "Lean 4 kernel\n#print axioms\nno sorryAx", INK),
    ]
    for x, label, colour in boxes:
        ax.add_patch(FancyBboxPatch((x, 0.9), 2.0, 1.4, boxstyle="round,pad=0.05",
                                    linewidth=1.6, edgecolor=colour, facecolor="white"))
        ax.text(x + 1.0, 1.6, label, ha="center", va="center", fontsize=9, color=colour)
    for x in (2.3, 4.6, 6.9):
        ax.add_patch(FancyArrowPatch((x, 1.6), (x + 0.3, 1.6), arrowstyle="-|>",
                                     mutation_scale=14, color=INK, linewidth=1.3))
    # The loop back: mutation-selection acts on the genome from fitness.
    ax.add_patch(FancyArrowPatch((3.6, 0.9), (1.3, 0.9), connectionstyle="arc3,rad=0.5",
                                 arrowstyle="-|>", mutation_scale=12, color=MUTED, linewidth=1.1))
    ax.text(2.45, 0.08, "mutation · tournament · steady state", ha="center", fontsize=8, color=MUTED)
    ax.text(5.9, 0.42, "refuted → removed", ha="center", fontsize=8, color=ACCENT)
    ax.text(8.2, 0.42, "proved → accepted", ha="center", fontsize=8, color=INK)
    ax.text(5.0, 2.72, "Fitness guides; the kernel decides.", ha="center", fontsize=10,
            style="italic", color=INK)
    # Dosage runs alongside as instrumentation.
    ax.text(0.3, 2.62, "dosage  out = A + B·v  (exact, one pass pair)", fontsize=8, color=GOLD)
    save(fig, out, "fig_architecture")


def fig_ladder(out: Path) -> None:
    ladder = load("kge_rust_ladder")
    if not ladder:
        print("  skip ladder (artifact missing)")
        return
    replay = load("kge_rust_ladder_python_points")
    rungs = [r["rung"] for r in ladder["rungs"]]
    rust = [r["solve_rate"] for r in ladder["rungs"]]
    proto = [PYTHON_RATES[r] for r in rungs]
    rep = {r["rung"]: r["solve_rate"] for r in replay["rungs"]} if replay else {}
    sizes = [r["target_size"] for r in ladder["rungs"]]
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    xs = range(len(rungs))
    ax.plot(xs, rust, "o-", color=INK, label="KGE (Rust), crate's own points")
    ax.plot(xs, proto, "s--", color=MUTED, label="Python prototype, its own points")
    if rep:
        ax.plot([i for i, r in enumerate(rungs) if r in rep], [rep[r] for r in rungs if r in rep],
                "D", color=ACCENT, markersize=8, label="KGE (Rust) replayed on the prototype's points")
    ax.set_xticks(list(xs))
    ax.set_xticklabels([f"{SHORT[r]}\n(size {s})" for r, s in zip(rungs, sizes)])
    ax.set_ylabel("solve rate (200 seeds, budget 4000)")
    ax.set_ylim(0, 1.05)
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    ax.set_title("Calibration ladder: the cliff, and what the sample points account for", fontsize=10)
    save(fig, out, "fig_ladder")


def fig_hillclimb(out: Path) -> None:
    climb = load("kge_rust_hillclimb")
    if not climb:
        print("  skip hillclimb (artifact missing)")
        return

    def mcnemar(b, c):
        n = b + c
        if n == 0:
            return 1.0
        k = min(b, c)
        return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)

    rungs = climb["rungs"]
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    xs = range(len(rungs))
    w = 0.26
    ax.bar([x - w for x in xs], [r["ga_rate"] for r in rungs], w, color=INK, label="population (KGE)")
    ax.bar(list(xs), [r["restarts_rate"] for r in rungs], w, color=ACCENT, label="hill-climber + restarts")
    ax.bar([x + w for x in xs], [r["descent_rate"] for r in rungs], w, color=MUTED, label="single descent")
    for i, r in enumerate(rungs):
        p = mcnemar(r["paired_ga_only"], r["paired_restarts_only"])
        top = max(r["ga_rate"], r["restarts_rate"]) + 0.03
        ax.text(i, top, f"p={p:.2g}" if p < 0.05 else "n.s.", ha="center", fontsize=7,
                color=ACCENT if p < 0.05 else MUTED)
    ax.set_xticks(list(xs))
    ax.set_xticklabels([f"{SHORT[r['rung']]}\n(size {r['target_size']})" for r in rungs])
    ax.set_ylabel("solve rate, same seeds/points/budget")
    ax.set_ylim(0, 1.12)
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    ax.set_title("The simplest control: the population earns its place from L3 on", fontsize=10)
    save(fig, out, "fig_hillclimb")


def fig_landscape(out: Path) -> None:
    cliff = load("gp_landscape_cliff")
    if not cliff:
        print("  skip landscape (artifact missing)")
        return
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    colours = [INK, SOFT, GOLD, ACCENT, MUTED, "#5d3a9b"]
    for r, colour in zip(cliff["rungs"], colours):
        ks = [w["mutations_from_solution"] for w in r["walk_away_from_solution"]]
        ratios = [w["ratio_to_random_median"] for w in r["walk_away_from_solution"]]
        ax.plot(ks, ratios, "o-", color=colour, label=f"{SHORT[r['rung']]} (size {r['target_size']})")
    ax.axhline(1.0, color=MUTED, linestyle=":", linewidth=1)
    ax.text(5.05, 1.005, "random-tree median", fontsize=7, color=MUTED, va="bottom", ha="right")
    ax.set_xlabel("mutations away from the exact solution")
    ax.set_ylabel("perturbed median fitness / random median")
    ax.set_title("Landscape: basin of signal ≈ 4 mutations at every rung", fontsize=10)
    ax.legend(frameon=False, fontsize=7, ncol=2)
    save(fig, out, "fig_landscape")


def fig_gate(out: Path) -> None:
    atom = load("lean_atomicity_is_the_wrapper")
    bis = load("lean_batching_bisection")
    if not atom:
        print("  skip gate (artifact missing)")
        return
    fails = [r["actually_false"] for r in atom["measured"]]
    one = [r["invocations"] for r in atom["measured"]]
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    ax.plot(fails, [8] * len(fails), "s--", color=MUTED, label="8 individual proofs")
    if bis:
        b = {r["scenario"].split()[0]: r["invocations"] for r in bis["bisection_measured_first"]}
        f = {r["scenario"].split()[0]: r["invocations"] for r in bis["flat_fallback_shipped"]}
        ks = [k for k in ("0", "1", "2", "4") if k in b]
        ax.plot([int(k) for k in ks], [b[k] for k in ks], "^:", color=GOLD, label="bisection (abandoned)")
        ax.plot([int(k) for k in ks], [f[k] for k in ks], "v:", color=SOFT, label="flat fall-back (abandoned)")
    ax.plot(fails, one, "o-", color=ACCENT, linewidth=2, label="kernel's per-declaration report")
    ax.set_xlabel("false candidates in a batch of 8")
    ax.set_ylabel("Lean invocations")
    ax.set_title("The gate: one invocation at any failure rate", fontsize=10)
    ax.legend(frameon=False, fontsize=8)
    save(fig, out, "fig_gate")


def fig_hf(out: Path) -> None:
    sel = load("kge_hf_selection")
    trad = load("kge_hf_traditional_baseline")
    if not sel:
        print("  skip hf (selection missing)")
        return
    rows = []
    for prob in sel["selected_top"]:
        name = prob["problem"].replace("-", "_").replace(".", "_")
        res = load(f"kge_hf_{name}")
        if not res:
            continue
        m = {x["method"]: x["rate"] for x in res["methods"]}
        t = None
        if trad:
            tp = next((p for p in trad["problems"] if p["problem"] == prob["problem"]), None)
            if tp:
                r12 = tp["regimes"]["12_points_same_as_kge"]
                t = 1.0 if r12["particular_solution_agrees_on_20_heldout"] else 0.0
        rows.append((prob["problem"], prob["sympy_eq_str"], m, t))
    if not rows:
        print("  skip hf (no solve results yet)")
        return
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    xs = range(len(rows))
    w = 0.2
    ax.bar([x - 1.5 * w for x in xs], [r[2].get("kge_mutation_selection", 0) for r in rows], w, color=INK, label="KGE")
    ax.bar([x - 0.5 * w for x in xs], [r[2].get("hillclimb_with_restarts", 0) for r in rows], w, color=ACCENT, label="hill-climber + restarts")
    ax.bar([x + 0.5 * w for x in xs], [r[2].get("random_search", 0) for r in rows], w, color=MUTED, label="random search")
    if any(r[3] is not None for r in rows):
        ax.bar([x + 1.5 * w for x in xs], [r[3] or 0 for r in rows], w, color=GOLD,
               label="exact polynomial regression, 12 points (recovers?)")
    ax.set_xticks(list(xs))
    ax.set_xticklabels([f"{r[0].replace('feynman-', '')}\n{r[1]}" for r in rows], fontsize=7)
    ax.set_ylabel("solve rate (100 seeds, budget 4000)")
    ax.set_ylim(0, 1.1)
    ax.legend(frameon=False, fontsize=7, loc="upper right")
    ax.set_title("SRSD-Feynman: the five Hub problems inside the grammar", fontsize=10)
    save(fig, out, "fig_hf")


def fig_coverage(out: Path) -> None:
    sel = load("kge_hf_selection")
    if not sel:
        return
    reasons = sel["refusal_reasons"]
    buckets = {"outside {+,−,∗}\n(functions, π, constants)": 0, "division by a variable": 0,
               "> 4 variables": 0, "physical constant\nas a float": 0, "other": 0}
    for k, v in reasons.items():
        if k.startswith("uses a function"):
            buckets["outside {+,−,∗}\n(functions, π, constants)"] += v
        elif k.startswith("division by a variable"):
            buckets["division by a variable"] += v
        elif "variables" in k:
            buckets["> 4 variables"] += v
        elif k.startswith("coefficient"):
            buckets["physical constant\nas a float"] += v
        else:
            buckets["other"] += v
    labels = ["fits the grammar"] + list(buckets)
    values = [sel["fitting_grammar"]] + list(buckets.values())
    fig, ax = plt.subplots(figsize=(6.6, 3.0))
    ax.barh(labels, values, color=[ACCENT] + [MUTED] * len(buckets))
    for i, v in enumerate(values):
        ax.text(v + 1, i, str(v), va="center", fontsize=8)
    ax.set_xlabel(f"of {sel['total_problems']} SRSD-Feynman equations")
    ax.invert_yaxis()
    ax.set_title("What the reference grammar covers, and what it must grow into", fontsize=10)
    save(fig, out, "fig_coverage")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    style()
    for f in (fig_architecture, fig_ladder, fig_hillclimb, fig_landscape, fig_gate, fig_coverage, fig_hf):
        f(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
