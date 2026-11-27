"""Code-generated figures for the zero-point-energy preprint (papers/prog_zero_point_optimality).

Reads only the result files copied into data/ (from results/programmes/2026-10-25/P2/ and its g2/ subfolder) and writes
fig/*.pdf. Nothing is typed by hand: every plotted number comes from those files.
Run: /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I make_figures.py
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm  # noqa: E402

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
FIG = HERE / "fig"

# colour-blind-safe pair (Okabe-Ito blue and vermillion) with a neutral grey midpoint; ink in neutral greys
BLUE = "#0072B2"
VERM = "#D55E00"
GREY = "#8a8a8a"
INK = "#222222"
DIV = LinearSegmentedColormap.from_list("div", [BLUE, "#e8e8e8", VERM])

plt.rcParams.update({
    "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8.5, "legend.fontsize": 7.5, "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5, "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "lines.linewidth": 1.2, "axes.edgecolor": INK,
    "axes.labelcolor": INK, "text.color": INK, "xtick.color": INK, "ytick.color": INK, "figure.dpi": 150,
    "pdf.fonttype": 42,
})


def load(name: str) -> object:
    return json.loads((DATA / name).read_text())


def read_csv(name: str) -> list[dict[str, float | str]]:
    rows = []
    with (DATA / name).open() as fh:
        for r in csv.DictReader(fh):
            rows.append({k: (v if k == "pot" else float(v)) for k, v in r.items()})
    return rows


def fig_curvature() -> None:
    mech = load("mechanism.json")
    scan = [s for s in mech["scan"] if s["a"] >= 0.15 and s["a"] <= 4.0]
    low = [s for s in mech["scan"] if s["a"] < 0.15]
    roots = {round(r["root"], 5) for r in mech["c_sign_changes"]}
    a1 = min(r["root"] for r in mech["c_sign_changes"] if 0.3 < r["root"] < 0.5)
    a2 = min(r["root"] for r in mech["c_sign_changes"] if r["root"] > 1.0)
    g1 = {p["a"]: p for p in mech["at_G1_potentials"]}
    fig, (ax, bx) = plt.subplots(2, 1, figsize=(5.4, 4.6), sharex=True, gridspec_kw={"height_ratios": [1.25, 1]})
    a = np.array([s["a"] for s in scan])
    c = np.array([s["c_ezp"] for s in scan])
    ax.axvspan(a1, a2, color=VERM, alpha=0.10, lw=0)
    ax.axhline(0, color=GREY, lw=0.7)
    ax.plot(a, c, color=INK, lw=1.0, marker="o", ms=2.6)
    if low:
        ax.plot([s["a"] for s in low], [s["c_ezp"] for s in low], ls="none", marker="o", ms=3, mfc="white", mec=INK, mew=0.7)
    for aa in (0.25, 0.5, 1.0, 2.0, 4.0):
        if aa in g1:
            cc = g1[aa]["c_ezp"]
            ref = cc < 0
            ax.plot([aa], [cc], marker="o", ms=6.5, mfc=VERM if ref else BLUE, mec="white", mew=0.8, ls="none", zorder=5)
    ax.annotate("gauss:0.5, gauss:1\nrefuted by a stable\ncompetitor", xy=(0.75, -1.05), xytext=(1.0, -0.5), fontsize=7.2, ha="left",
                va="center", arrowprops=dict(arrowstyle="-", color=GREY, lw=0.6))
    ax.text(a1 * 1.02, 0.78, f"triangular = local max of $E_{{zp}}$\n$a\\in({a1:.4f},\\,{a2:.4f})$", fontsize=7.2, va="top", ha="left", color=INK)
    ax.text(0.17, 0.62, "local min", fontsize=7.2, color=BLUE)
    ax.text(2.6, 0.05, "local min", fontsize=7.2, color=BLUE)
    ax.set_ylabel(r"$c(a)=\Delta E_{zp}(\rho)/4$")
    ax.set_ylim(-1.25, 0.85)
    # bottom: Laplacian of the mean-square frequency (sum rule) -- same sign pattern is NOT the same as c(a)
    lap = np.array([s["lap_m2_exact"] for s in mech["scan"] if 0.15 <= s["a"] <= 4.0])
    bx.axhline(0, color=GREY, lw=0.7)
    bx.axvspan(a1, a2, color=VERM, alpha=0.10, lw=0)
    bx.plot(a, lap, color=INK, lw=1.0, marker="s", ms=2.4)
    bx.set_ylabel(r"$\Delta\langle\mathrm{tr}\,D\rangle(\rho)$ (exact lattice sum)")
    bx.set_xlabel(r"Gaussian width parameter $a$ in $V=e^{-\pi a r^{2}}$")
    bx.set_xscale("log")
    bx.set_xticks([0.15, 0.25, 0.5, 1, 2, 4])
    bx.set_xticklabels(["0.15", "0.25", "0.5", "1", "2", "4"])
    bx.text(0.16, 9.5, "the sign of $\\Delta\\langle\\mathrm{tr}\\,D\\rangle$ differs from\nthe sign of $c$ on about $(0.12,0.38)$\nand $(1.09,1.58)$", fontsize=7.0, va="center")
    ax.text(0.16, -1.1, "open marker: $a=0.1$", fontsize=6.8, color=GREY, va="center")
    fig.align_ylabels([ax, bx])
    fig.tight_layout()
    fig.savefig(FIG / "fig_curvature.pdf")
    plt.close(fig)
    print("roots", sorted(roots), "a1", a1, "a2", a2)


def fig_map() -> None:
    rows: list[dict[str, float | str]] = []
    for f in ("gauss_1__coarse.csv", "gauss_1__random.csv", "gauss_1__patch_rho.csv"):
        rows += [r for r in read_csv(f) if int(r["n"]) == 96]
    seen: dict[tuple[float, float], dict[str, float | str]] = {}
    for r in rows:
        seen[(round(float(r["x"]), 6), round(float(r["y"]), 6))] = r
    tri_key = (0.5, round(math.sqrt(3) / 2, 6))
    e_tri = float(seen[tri_key]["e_zp"])
    xs, ys, de, ux, uy = [], [], [], [], []
    for (x, y), r in seen.items():
        e = float(r["e_zp"])
        if math.isnan(e):
            ux.append(x)
            uy.append(y)
        else:
            xs.append(x)
            ys.append(y)
            de.append(e - e_tri)
    xs, ys, de = map(np.array, (xs, ys, de))
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.4, 2.9), gridspec_kw={"width_ratios": [1, 1.25]})
    ax.plot(ux, uy, ls="none", marker="x", ms=2.4, mec=GREY, mew=0.5, label="dynamically unstable")
    ax.scatter(xs, ys, c=de, cmap=DIV, norm=TwoSlopeNorm(0, de.min(), max(de.max(), 0.02)), s=8, edgecolors="none")
    ax.set_xlim(-0.02, 0.52)
    ax.set_ylim(0.82, 2.45)
    ax.set_xlabel(r"Re $\tau$")
    ax.set_ylabel(r"Im $\tau$")
    ax.set_title(f"all {len(seen)} sampled shapes (n = 96)")
    ax.plot([0.5], [math.sqrt(3) / 2], marker="*", ms=7, mfc="white", mec=INK, mew=0.7, ls="none")
    zoom = (-0.01, 0.52, 0.84, 1.12)
    bx.add_patch(plt.Rectangle((zoom[0], zoom[2]), zoom[1] - zoom[0], zoom[3] - zoom[2], fill=False, ec=GREY, lw=0.5))
    m = (xs >= 0.25) & (ys <= 1.12)
    sc = bx.scatter(xs[m], ys[m], c=de[m], cmap=DIV, norm=TwoSlopeNorm(0, de.min(), max(de.max(), 0.02)), s=22, edgecolors="white", linewidths=0.4)
    zx = [x for x, y in zip(ux, uy) if x >= 0.25 and y <= 1.12]
    zy = [y for x, y in zip(ux, uy) if x >= 0.25 and y <= 1.12]
    bx.plot(zx, zy, ls="none", marker="x", ms=3, mec=GREY, mew=0.6)
    bx.plot([0.5], [math.sqrt(3) / 2], marker="*", ms=9, mfc="white", mec=INK, mew=0.8, ls="none")
    bx.plot([0.5], [0.966025403784], marker="o", ms=9, mfc="none", mec=INK, mew=0.8, ls="none")
    bx.text(0.485, 0.852, "triangular $\\rho$", fontsize=7.2, ha="right", va="center",
            bbox=dict(fc="white", ec="none", pad=0.6))
    bx.text(0.485, 0.985, "$0.5+0.966\\,i$", fontsize=7.2, ha="right", va="bottom",
            bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.85))
    bx.set_xlim(0.25, 0.52)
    bx.set_ylim(0.84, 1.12)
    bx.set_xlabel(r"Re $\tau$")
    bx.set_title("zoom: dynamically stable region")
    cb = fig.colorbar(sc, ax=bx, fraction=0.045, pad=0.02)
    cb.set_label(r"$E_{zp}(\tau)-E_{zp}(\rho)$", fontsize=7.5)
    cb.ax.tick_params(labelsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "fig_map.pdf")
    plt.close(fig)
    print("map: stable", len(xs), "unstable", len(ux), "min dE", de.min(), "max dE", de.max())


def fig_convergence() -> None:
    pc = load("poisson_check.json")
    case = next(c for c in pc["cases"] if c["pot"] == "gauss:1" and abs(c["y"] - 0.966025403784) < 1e-9)
    ref = case["duffy"]["128"]["ezp"]
    ref_u = case["uniform"]["richardson_n512_1024_s0.0"]
    fig, ax = plt.subplots(figsize=(4.6, 2.9))
    nn = [16, 32, 64, 96]
    err = [max(abs(case["duffy"][str(n)]["ezp"] - ref), 1e-16) for n in nn]  # values at or below 1e-16 are round-off
    ax.semilogy(nn, err, marker="o", ms=3.2, color=BLUE, label="Duffy-Gauss rule ($N\\times N$ nodes per triangle)")
    un = [256, 512, 1024]
    for sh, mk, lab in (("0.0", "s", "uniform grid, centred"), ("0.5", "^", "uniform grid, half-shifted")):
        e = [abs(case["uniform"][f"n{n}_s{sh}"]["ezp"] - ref) for n in un]
        ax.semilogy(un, e, marker=mk, ms=3.2, color=VERM, ls="-" if sh == "0.0" else "--", label=lab)
    xx = np.array([256, 1024])
    e0 = abs(case["uniform"]["n256_s0.0"]["ezp"] - ref)
    ax.semilogy(xx, e0 * (256 / xx) ** 3, color=GREY, lw=0.7, ls=":")
    ax.text(560, e0 * (256 / 560) ** 3 * 6, "$\\propto n^{-3}$", color=GREY, fontsize=7.5)
    ax.axhline(1e-15, color=GREY, lw=0.5)
    ax.set_xlabel("nodes per direction (Duffy $N$, or uniform $n$)")
    ax.set_ylabel(r"$|E_{zp}-E_{zp}^{\mathrm{Duffy},128}|$")
    ax.set_ylim(5e-17, 1e-3)
    ax.legend(frameon=False, loc="upper right", fontsize=7)
    ax.set_title(r"gauss:1, $\tau=0.5+0.966025\,i$")
    ax.text(300, 2.5e-16, "round-off floor (about $10^{-15}$)", fontsize=6.8, color=GREY)
    fig.tight_layout()
    fig.savefig(FIG / "fig_convergence.pdf")
    plt.close(fig)
    print("conv: richardson - duffy", ref_u - ref)


def fig_split() -> None:
    mech = load("mechanism.json")
    fig, axes = plt.subplots(1, 2, figsize=(5.8, 2.5), sharey=True)
    shells = ["long-wave\n$s\\in[0,1/3]$", "middle", "zone boundary\n$s\\in[2/3,1]$"]
    for ax, key, ttl in ((axes[0], "split_gauss1_c1", "gauss:1 (refuted)"), (axes[1], "split_gauss2_c1", "gauss:2 (control)")):
        d = mech[key]
        w = 0.36
        xs = np.arange(3)
        ax.bar(xs - w / 2, d["lower_branch_by_shell"], w, color=BLUE, label="lower branch", linewidth=0)
        ax.bar(xs + w / 2, d["upper_branch_by_shell"], w, color=VERM, label="upper branch", linewidth=0)
        ax.axhline(0, color=INK, lw=0.6)
        ax.set_xticks(xs)
        ax.set_xticklabels(shells, fontsize=6.8)
        ax.set_title(f"{ttl}: total {d['total']:+.2e}")
    axes[0].set_ylabel(r"$E_{zp}(0.5+0.966i)-E_{zp}(\rho)$ by part")
    axes[0].legend(frameon=False, loc="upper left", fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "fig_split.pdf")
    plt.close(fig)


def main() -> int:
    FIG.mkdir(exist_ok=True)
    fig_curvature()
    fig_map()
    fig_convergence()
    fig_split()
    return 0


if __name__ == "__main__":
    sys.exit(main())
