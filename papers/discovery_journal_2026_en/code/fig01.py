"""Figure c01: how a staircase of rectangles encloses a distance integral, and the widths of the seven enclosures.

Panel (a) is an illustration of the method of papers/certified_bao (1/E decreasing, so the integral lies between the
lower and the upper Riemann sums), drawn on a deliberately coarse grid of 10 cells instead of the paper's 2000 cells
per unit redshift. Panel (b) plots the relative widths of the seven kernel-checked enclosures, read as exact
fractions from results/certified_numerics/P1_bao/bounds_Fit.json, and checks that an independent numerical
integration of chi(z) lies inside every enclosure.
Run: .venv/bin/python -I papers/discovery_journal_2026_en/code/fig01.py
"""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mpmath as mp
import numpy as np
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "papers" / "discovery_journal_2026_en" / "figures"
OKABE = {"orange": "#E69F00", "bleu_ciel": "#56B4E9", "vert": "#009E73", "jaune": "#F0E442",
         "bleu": "#0072B2", "vermillon": "#D55E00", "pourpre": "#CC79A7", "noir": "#000000"}
IVOIRE = "#FFFFF0"
OM = 0.29743


def style() -> None:
    plt.rcParams.update({"font.family": "serif", "font.serif": ["DejaVu Serif"], "font.size": 9,
                         "mathtext.fontset": "dejavuserif",
                         "axes.facecolor": IVOIRE, "figure.facecolor": IVOIRE, "savefig.facecolor": IVOIRE,
                         "axes.edgecolor": "#555555", "axes.linewidth": 0.6, "axes.grid": True,
                         "grid.color": "#dddddd", "grid.linewidth": 0.5, "axes.spines.top": False,
                         "axes.spines.right": False})


def virgule(x: float, _pos: int) -> str:
    return f"{x:g}"


def inv_e(x: np.ndarray | float, om: float = OM) -> np.ndarray | float:
    return 1.0 / np.sqrt(om * (1 + x) ** 3 + 1 - om)


def main() -> None:
    style()
    mp.mp.dps = 30
    rec = json.loads((ROOT / "results/certified_numerics/P1_bao/bounds_Fit.json").read_text())
    assert rec["Om"] == "29743/100000"
    zs, widths = [], []
    for key, r in rec["redshifts"].items():
        z = Fraction(r["z"])
        lo, hi = Fraction(r["chi_lo"]), Fraction(r["chi_hi"])
        chi = mp.quad(lambda x: 1 / mp.sqrt(mp.mpf(29743) / 100000 * (1 + x) ** 3 + 1 - mp.mpf(29743) / 100000),
                      [0, mp.mpf(z.numerator) / z.denominator])
        inside = mp.mpf(lo.numerator) / lo.denominator <= chi <= mp.mpf(hi.numerator) / hi.denominator
        w = float((hi - lo) / ((hi + lo) / 2))
        print(f"check {key}: chi(mpmath)={mp.nstr(chi, 15)} in [{float(lo):.10f}, {float(hi):.10f}] -> {inside};"
              f" relative width {w:.3e}")
        assert inside
        zs.append(float(z))
        widths.append(w)
    print(f"check widths min {min(widths):.3e} max {max(widths):.3e} (paper: 2.53e-4 to 2.79e-4)")
    assert 2.52e-4 < min(widths) and max(widths) < 2.80e-4

    # coarse illustrative staircase on [0, 1] with 10 cells (the paper uses 2000 cells per unit of z)
    n_cells = 10
    xs = np.linspace(0.0, 1.0, n_cells + 1)
    f = inv_e(xs)
    lower = float(np.sum(f[1:]) / n_cells)
    upper = float(np.sum(f[:-1]) / n_cells)
    true = float(mp.quad(lambda x: 1 / mp.sqrt(OM * (1 + x) ** 3 + 1 - OM), [0, 1]))
    print(f"illustration, 10 cells on [0,1]: lower {lower:.4f} <= true {true:.4f} <= upper {upper:.4f}")
    assert lower <= true <= upper

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.3, 2.6), gridspec_kw={"width_ratios": [1.15, 1]})
    for a in (a1, a2):
        a.xaxis.set_major_formatter(FuncFormatter(virgule))
        a.yaxis.set_major_formatter(FuncFormatter(virgule))
    fine = np.linspace(0, 1, 400)
    a1.bar(xs[:-1], f[:-1], width=1 / n_cells, align="edge", color=OKABE["bleu_ciel"], alpha=0.35,
           edgecolor=IVOIRE, lw=1.0, label=f"upper steps (sum {upper:.3f})")
    a1.bar(xs[:-1], f[1:], width=1 / n_cells, align="edge", color=OKABE["bleu"], alpha=0.75,
           edgecolor=IVOIRE, lw=1.0, label=f"lower steps (sum {lower:.3f})")
    a1.plot(fine, inv_e(fine), color=OKABE["vermillon"], lw=1.6, label=f"curve (area {true:.3f})")
    a1.set_xlim(0, 1)
    a1.set_ylim(0.5, 1.05)
    a1.set_xlabel("redshift $z$")
    a1.set_ylabel("$1/E(z)$")
    a1.set_title("(a) the area is squeezed from both sides", fontsize=9, loc="left")
    a1.legend(fontsize=7, loc="upper right", frameon=False)

    a2.plot(zs, np.array(widths) * 1e4, "o", ms=6, color=OKABE["orange"], mec=IVOIRE, mew=1.2)
    a2.set_ylim(0, 6)
    a2.axhline(5, color=OKABE["noir"], lw=0.8, ls="--")
    a2.text(1.3, 5.15, "threshold announced in advance", fontsize=7.5, ha="center")
    a2.set_xlabel("$z$ of the seven measurements")
    a2.set_ylabel("relative width (in $10^{-4}$)")
    a2.set_title("(b) the seven kernel-checked enclosures", fontsize=9, loc="left")
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"c01_encadrement.{ext}", dpi=300)
    print("wrote", OUT / "c01_encadrement.pdf", "and .png")


if __name__ == "__main__":
    main()
