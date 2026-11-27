"""Figure c05: the tabulated structure factor of superfluid helium-4 against the envelope sqrt(Q / 2k*).

Data: the 99 points of papers/prog_superfluid_structure_factor/data/he4_Sk_donnelly_table14_1.csv (the Q = 0 row is a
theory value adopted by the compilation and is excluded, as in the paper). k* = 2 m c / hbar is recomputed from
CODATA constants (scipy.constants), m = 4.0026032 g/mol and c = 238.3 m/s. The verdict rule of the paper is applied:
consistent if S <= B, refuted if S - B > 0.082, undecided otherwise. Checks: the counts 29/7/63, the 21 roton-region
points (1.7-2.4 1/Angstrom) all refuted with S/B between 1.62 and 2.49, the smallest roton margin 0.328, and the
per-point verdicts of data/test_he4.csv.
Run: .venv/bin/python -I papers/discovery_journal_2026/code/fig05.py
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter
from scipy import constants

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "papers" / "discovery_journal_2026" / "figures"
DATA = ROOT / "papers" / "prog_superfluid_structure_factor" / "data"
OKABE = {"orange": "#E69F00", "bleu_ciel": "#56B4E9", "vert": "#009E73", "jaune": "#F0E442",
         "bleu": "#0072B2", "vermillon": "#D55E00", "pourpre": "#CC79A7", "noir": "#000000"}
IVOIRE = "#FFFFF0"
DELTA = 0.082


def style() -> None:
    plt.rcParams.update({"font.family": "serif", "font.serif": ["DejaVu Serif"], "font.size": 9,
                         "mathtext.fontset": "dejavuserif",
                         "axes.facecolor": IVOIRE, "figure.facecolor": IVOIRE, "savefig.facecolor": IVOIRE,
                         "axes.edgecolor": "#555555", "axes.linewidth": 0.6, "axes.grid": True,
                         "grid.color": "#dddddd", "grid.linewidth": 0.5, "axes.spines.top": False,
                         "axes.spines.right": False})


def virgule(x: float, _pos: int) -> str:
    return f"{x:g}".replace(".", ",")


def verdict(s: float, b: float) -> str:
    if s <= b:
        return "CONSISTENT"
    return "REFUTED" if s - b > DELTA else "UNDECIDED"


def main() -> None:
    style()
    m = 4.0026032e-3 / constants.N_A
    kstar = 2 * m * 238.3 / constants.hbar * 1e-10  # in 1/Angstrom
    print(f"check k* = {kstar:.5f} 1/A (paper 3.00379)")
    assert abs(kstar - 3.00379) < 5e-5
    with (DATA / "he4_Sk_donnelly_table14_1.csv").open() as fh:
        rows = [r for r in csv.DictReader(fh) if float(r["Q_invA"]) > 0]
    with (DATA / "test_he4.csv").open() as fh:
        ref = list(csv.DictReader(fh))
    q = np.array([float(r["Q_invA"]) for r in rows])
    s = np.array([float(r["S"]) for r in rows])
    b = np.sqrt(q / (2 * kstar))
    v = [verdict(si, bi) for si, bi in zip(s, b)]
    assert len(rows) == 99 == len(ref)
    mism = sum(1 for vi, r in zip(v, ref) if vi != r["verdict"])
    counts = {k: v.count(k) for k in ("CONSISTENT", "UNDECIDED", "REFUTED")}
    print(f"check counts {counts} (paper 29 / 7 / 63); verdict mismatches vs test_he4.csv: {mism}")
    assert counts == {"CONSISTENT": 29, "UNDECIDED": 7, "REFUTED": 63} and mism == 0
    roton = (q >= 1.7) & (q <= 2.4)
    ratio = s[roton] / b[roton]
    margin = (s - b)[roton]
    print(f"check roton region: {int(roton.sum())} points, refuted {sum(1 for i in np.where(roton)[0] if v[i]=='REFUTED')},"
          f" S/B {ratio.min():.2f}-{ratio.max():.2f}, min margin {margin.min():.3f} (paper 21, 21, 1.62-2.49, 0.328)")
    assert int(roton.sum()) == 21 and all(v[i] == "REFUTED" for i in np.where(roton)[0])
    i_pk = int(np.argmax(s))
    print(f"peak point Q={q[i_pk]} S={s[i_pk]} B={b[i_pk]:.4f} ratio {s[i_pk]/b[i_pk]:.2f} (paper 2.058, 1.458, 0.5853, 2.49)")

    fig, ax = plt.subplots(figsize=(6.3, 2.8))
    ax.xaxis.set_major_formatter(FuncFormatter(virgule))
    ax.yaxis.set_major_formatter(FuncFormatter(virgule))
    ax.axvspan(1.7, 2.4, color=OKABE["jaune"], alpha=0.25, lw=0)
    ax.text(2.05, 1.62, "région du roton", ha="center", fontsize=7.5)
    qq = np.linspace(0.0, 2 * kstar, 400)
    ax.plot(qq, np.sqrt(qq / (2 * kstar)), color=OKABE["noir"], lw=1.3, label=r"enveloppe proposée $\sqrt{Q/2k_*}$")
    ax.fill_between(qq, np.sqrt(qq / (2 * kstar)), np.sqrt(qq / (2 * kstar)) + DELTA, color="#bbbbbb", alpha=0.4,
                    lw=0, label="marge de tolérance 0,082")
    style_of = {"CONSISTENT": (OKABE["bleu"], "o", "compatible (29)"),
                "UNDECIDED": (OKABE["orange"], "s", "indécis (7)"),
                "REFUTED": (OKABE["vermillon"], "^", "réfuté (63)")}
    for key, (col, mk, lab) in style_of.items():
        sel = np.array([vi == key for vi in v])
        ax.plot(q[sel], s[sel], mk, ms=4.5, color=col, mec=IVOIRE, mew=0.6, label=lab, ls="none")
    ax.set_xlim(0, 6.1)
    ax.set_ylim(0, 1.75)
    ax.set_xlabel(r"vecteur d'onde $Q$ (Å$^{-1}$)")
    ax.set_ylabel("facteur de structure $S(Q)$")
    ax.legend(fontsize=7, loc="lower right", frameon=False, ncol=2)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"c05_helium.{ext}", dpi=300)
    print("wrote", OUT / "c05_helium.pdf", "and .png")


if __name__ == "__main__":
    main()
