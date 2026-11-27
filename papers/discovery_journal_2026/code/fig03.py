"""Figure c03: the vacancy argument, and the square-minus-triangular energy gap of the planar Yukawa interaction.

Panel (a) draws the density-one triangular lattice with the origin removed and the three points of the non-uniqueness
argument of papers/universal_optimality_tiered (Theorem 2: an isometry would send 2a-b to 2p(1,0)-p(2,0) = 0).
Panel (b) recomputes, by direct lattice sums, the energy per particle (1/2) sum V(|v|) of the triangular and square
lattices at density one for V(r) = exp(-kappa r)/r, both for the exact potential and for the shifted-force cut at
r_c = 8 used by the 2026-10-11 paper, and checks the four published shifted-force values (gen_numbers.tex of that
paper) and the exact values of papers/ar_yukawa_crystal/data/mpmath_control.json.
Run: .venv/bin/python -I papers/discovery_journal_2026/code/fig03.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "papers" / "discovery_journal_2026" / "figures"
OKABE = {"orange": "#E69F00", "bleu_ciel": "#56B4E9", "vert": "#009E73", "jaune": "#F0E442",
         "bleu": "#0072B2", "vermillon": "#D55E00", "pourpre": "#CC79A7", "noir": "#000000"}
IVOIRE = "#FFFFF0"
A_TRI = np.sqrt(2.0 / np.sqrt(3.0))


def style() -> None:
    plt.rcParams.update({"font.family": "serif", "font.serif": ["DejaVu Serif"], "font.size": 9,
                         "mathtext.fontset": "dejavuserif",
                         "axes.facecolor": IVOIRE, "figure.facecolor": IVOIRE, "savefig.facecolor": IVOIRE,
                         "axes.edgecolor": "#555555", "axes.linewidth": 0.6, "axes.grid": True,
                         "grid.color": "#dddddd", "grid.linewidth": 0.5, "axes.spines.top": False,
                         "axes.spines.right": False})


def virgule(x: float, _pos: int) -> str:
    return f"{x:g}".replace(".", ",")


def lattice_dists(kind: str, rmax: float) -> np.ndarray:
    m = int(rmax / 0.8) + 2
    i, j = np.meshgrid(np.arange(-m, m + 1), np.arange(-m, m + 1), indexing="ij")
    if kind == "tri":
        x = A_TRI * (i + 0.5 * j)
        y = A_TRI * (np.sqrt(3.0) / 2.0) * j
    else:
        x, y = i.astype(float), j.astype(float)
    r = np.hypot(x, y).ravel()
    return np.sort(r[(r > 0) & (r < rmax)])


def energy_exact(kind: str, kappa: float) -> float:
    r = lattice_dists(kind, 45.0 / kappa + 5.0)
    return float(0.5 * np.sum(np.exp(-kappa * r) / r))


def energy_sf(kind: str, kappa: float, rc: float = 8.0) -> float:
    r = lattice_dists(kind, rc)
    v = np.exp(-kappa * r) / r
    vc = np.exp(-kappa * rc) / rc
    dvc = -np.exp(-kappa * rc) * (kappa * rc + 1.0) / rc ** 2
    return float(0.5 * np.sum(v - vc - (r - rc) * dvc))


def main() -> None:
    style()
    published_sf = {(2, "tri"): 0.3935333668, (2, "sq"): 0.4009647699, (1, "tri"): 1.6076092172,
                    (1, "sq"): 1.6171455730}
    for (k, kind), val in published_sf.items():
        mine = energy_sf(kind, k)
        print(f"check shifted force kappa={k} {kind}: {mine:.10f} vs published {val}")
        assert abs(mine - val) < 2e-10
    mpc = json.loads((ROOT / "papers/ar_yukawa_crystal/data/mpmath_control.json").read_text())
    for row in mpc["rows"]:
        kind = "tri" if row["lattice"] == "tri" else "sq"
        mine = energy_exact(kind, row["kappa"])
        print(f"check exact kappa={row['kappa']} {kind}: {mine:.13f} vs mpmath {row['mp_direct'][:16]}")
        assert abs(mine - float(row["mp_direct"])) < 1e-12

    kappas = np.linspace(0.5, 3.0, 26)
    gap = np.array([energy_exact("sq", k) - energy_exact("tri", k) for k in kappas])
    assert np.all(gap > 0)
    print(f"gap square - triangular, exact potential, kappa in [0.5,3]: min {gap.min():.4e} max {gap.max():.4e}")

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.3, 2.7), gridspec_kw={"width_ratios": [1, 1.25]})
    # (a) vacancy picture
    pts = []
    for i in range(-4, 5):
        for j in range(-4, 5):
            x = A_TRI * (i + 0.5 * j)
            y = A_TRI * (np.sqrt(3) / 2) * j
            if abs(x) <= 2.9 and abs(y) <= 2.0 and (i, j) != (0, 0):
                pts.append((x, y))
    pts = np.array(pts)
    a1.plot(pts[:, 0], pts[:, 1], "o", ms=6, color=OKABE["bleu"], mec=IVOIRE, mew=1.0)
    a1.plot([0], [0], "o", ms=7, mfc=IVOIRE, mec=OKABE["vermillon"], mew=1.4)
    p1, p2 = np.array([A_TRI, 0.0]), np.array([2 * A_TRI, 0.0])
    a1.plot(*p1, "o", ms=7, color=OKABE["orange"], mec=IVOIRE, mew=1.0)
    a1.plot(*p2, "o", ms=7, color=OKABE["orange"], mec=IVOIRE, mew=1.0)
    a1.annotate("", xy=(0.12, 0.0), xytext=p2 - np.array([0.1, 0]),
                arrowprops={"arrowstyle": "->", "color": OKABE["noir"], "lw": 0.9})
    a1.text(p1[0], -0.42, "$p(1,0)$", ha="center", fontsize=7.5)
    a1.text(p2[0], -0.42, "$p(2,0)$", ha="center", fontsize=7.5)
    a1.text(0, 0.32, "trou", ha="center", fontsize=7.5, color=OKABE["vermillon"])
    a1.set_aspect("equal")
    a1.set_xlim(-3.0, 3.0)
    a1.set_ylim(-2.1, 2.1)
    a1.set_xticks([])
    a1.set_yticks([])
    a1.grid(False)
    for s in ("left", "bottom"):
        a1.spines[s].set_visible(False)
    a1.set_title("(a) le réseau privé d'un point", fontsize=9, loc="left")

    # (b) exact gap
    a2.xaxis.set_major_formatter(FuncFormatter(virgule))
    a2.plot(kappas, gap * 1e3, color=OKABE["bleu"], lw=1.6)
    for k in (1, 2):
        g = energy_exact("sq", k) - energy_exact("tri", k)
        a2.plot([k], [g * 1e3], "o", ms=6, color=OKABE["orange"], mec=IVOIRE, mew=1.2)
        a2.annotate(f"{g*1e3:.2f}".replace(".", ","), (k, g * 1e3), xytext=(6, 4), textcoords="offset points",
                    fontsize=7.5)
    a2.set_ylim(0, None)
    a2.yaxis.set_major_formatter(FuncFormatter(virgule))
    a2.set_xlabel(r"écrantage $\kappa$")
    a2.set_ylabel(r"écart par particule (en $10^{-3}$)")
    a2.set_title("(b) énergie du carré moins celle du triangle", fontsize=9, loc="left")
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"c03_lacune.{ext}", dpi=300)
    print("wrote", OUT / "c03_lacune.pdf", "and .png")


if __name__ == "__main__":
    main()
