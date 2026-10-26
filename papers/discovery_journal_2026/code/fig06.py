"""Figure c06 (ED-18): fixation probabilities as limits of matrix powers.

Left: exact rational powers P^n of the Moran kernel (N = 3, r = 2) applied to one mutant, P^n(1, N), against n,
together with the kernel-checked limit 4/7 and the neutral value 1/3.
Right: the limit S_i/S_N for N = 10 and r = 3/2, 1, 0.8, and the Wright-Fisher neutral chain (N = 10) after
2000 steps, which lands on i/N.

The kernels are those of formal_cert/Programmes/PopGen/MoranModel.lean (moranUp, moranDown, bdP) and
formal_cert/Autoresearch/PopGenWrightFisher.lean (wfP). Every plotted number is computed here.
Checks (asserts) against papers/prog_population_genetics_fixation/AUDIT.md section 2:
P^n(1,3) = 0, 0.0889, 0.5098, 0.571427 at n = 1, 2, 10, 50; the N = 2, r = 2 row (1/6, 1/2, 1/3); moranFix 3 2 1 = 4/7.
Run: .venv/bin/python -I papers/discovery_journal_2026/code/fig06.py
"""
from __future__ import annotations

from fractions import Fraction
from math import comb
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "papers" / "discovery_journal_2026" / "figures"
OKABE = {"orange": "#E69F00", "bleu_ciel": "#56B4E9", "vert": "#009E73", "jaune": "#F0E442",
         "bleu": "#0072B2", "vermillon": "#D55E00", "pourpre": "#CC79A7", "noir": "#000000"}
IVOIRE = "#FFFFF0"


def style() -> None:
    plt.rcParams.update({"font.family": "serif", "font.serif": ["DejaVu Serif"], "font.size": 9,
                         "axes.facecolor": IVOIRE, "figure.facecolor": IVOIRE, "savefig.facecolor": IVOIRE,
                         "axes.edgecolor": "#555555", "axes.linewidth": 0.6, "axes.grid": True,
                         "grid.color": "#dddddd", "grid.linewidth": 0.5, "axes.spines.top": False,
                         "axes.spines.right": False})


def virgule(x: float, _pos: int) -> str:
    return f"{x:g}".replace(".", ",")


def moran_kernel(n_pop: int, r: Fraction) -> list[list[Fraction]]:
    """bdP N (moranUp N r) (moranDown N r) on {0, ..., N}."""
    big_n = Fraction(n_pop)
    rows: list[list[Fraction]] = []
    for i in range(n_pop + 1):
        fi = Fraction(i)
        den = r * fi + (big_n - fi)
        up = r * fi / den * ((big_n - fi) / big_n)
        down = (big_n - fi) / den * (fi / big_n)
        row = [Fraction(0)] * (n_pop + 1)
        if i + 1 <= n_pop:
            row[i + 1] += up
        if i - 1 >= 0:
            row[i - 1] += down
        row[i] += 1 - up - down
        rows.append(row)
    return rows


def wf_kernel(n_pop: int) -> np.ndarray:
    """wfP N i j = C(N, j) (i/N)^j (1 - i/N)^(N - j)."""
    p = np.zeros((n_pop + 1, n_pop + 1))
    for i in range(n_pop + 1):
        x = i / n_pop
        for j in range(n_pop + 1):
            p[i, j] = comb(n_pop, j) * x ** j * (1 - x) ** (n_pop - j)
    return p


def matmul(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    m = len(a)
    return [[sum((a[i][k] * b[k][j] for k in range(m)), Fraction(0)) for j in range(m)] for i in range(m)]


def moran_fix(n_pop: int, r: float, i: int) -> float:
    """S_i / S_N with S_n = sum_{k<n} r^{-k} (moranFix)."""
    s_i = sum(r ** (-k) for k in range(i))
    s_n = sum(r ** (-k) for k in range(n_pop))
    return s_i / s_n


def main() -> None:
    style()
    # pencil-and-paper row of the chapter: N = 2, r = 2, i = 1
    row = moran_kernel(2, Fraction(2))[1]
    assert row == [Fraction(1, 6), Fraction(1, 2), Fraction(1, 3)], row

    p3 = moran_kernel(3, Fraction(2))
    limit = Fraction(1, 1) * (1 - Fraction(1, 2)) / (1 - Fraction(1, 8))
    assert limit == Fraction(4, 7)
    s = sum((Fraction(1, 2) ** k for k in range(1)), Fraction(0)) / sum((Fraction(1, 2) ** k for k in range(3)),
                                                                        Fraction(0))
    assert s == Fraction(4, 7)

    ns = list(range(1, 61))
    vals: list[float] = []
    power = [[Fraction(int(i == j)) for j in range(4)] for i in range(4)]
    exact: dict[int, Fraction] = {}
    for n in ns:
        power = matmul(power, p3)
        exact[n] = power[1][3]
        vals.append(float(power[1][3]))
    audit = {1: 0.0, 2: 0.0889, 10: 0.5098, 50: 0.571427}
    for n, v in audit.items():
        assert abs(float(exact[n]) - v) < 5e-5, (n, float(exact[n]), v)
    assert all(vals[k] <= vals[k + 1] for k in range(len(vals) - 1))
    print("P^n(1,3) at n=2,10,50:", float(exact[2]), float(exact[10]), float(exact[50]), " limit 4/7 =", 4 / 7)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.9))
    ax1.plot(ns, vals, "o", ms=2.6, color=OKABE["bleu"], label=r"$P^n(1,3)$ calculé exactement")
    ax1.axhline(4 / 7, color=OKABE["vermillon"], lw=1.2, label="limite vérifiée : 4/7")
    ax1.axhline(1 / 3, color=OKABE["noir"], lw=0.9, ls="--", label="sans sélection : 1/3")
    ax1.set_xlabel("nombre de pas $n$")
    ax1.set_ylabel("probabilité d'avoir envahi")
    ax1.set_title("Moran, 3 individus, avantage $r=2$", fontsize=9)
    ax1.set_ylim(-0.02, 0.7)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(virgule))
    ax1.legend(fontsize=7, loc="lower right", frameon=False)

    n_pop = 10
    i_vals = np.arange(0, n_pop + 1)
    curves = [(1.5, OKABE["vermillon"], "Moran, $r=1{,}5$"), (1.0, OKABE["noir"], "Moran, $r=1$ (neutre)"),
              (0.8, OKABE["bleu_ciel"], "Moran, $r=0{,}8$")]
    for r, col, lab in curves:
        if r == 1.0:
            y = i_vals / n_pop
        else:
            y = np.array([moran_fix(n_pop, r, int(i)) for i in i_vals])
        ax2.plot(i_vals, y, "-o", ms=2.8, lw=1.0, color=col, label=lab)
    wf = np.linalg.matrix_power(wf_kernel(n_pop), 2000)
    assert np.max(np.abs(wf[:, n_pop] - i_vals / n_pop)) < 1e-9
    ax2.plot(i_vals, wf[:, n_pop], "s", ms=4.5, mfc="none", color=OKABE["vert"],
             label="Wright–Fisher, 2000 pas")
    # check against the closed forms quoted in the record (N = 10, r = 3/2, i = 1)
    assert abs(moran_fix(10, 1.5, 1) - (1 - 1 / 1.5) / (1 - 1.5 ** -10)) < 1e-15
    ax2.set_xlabel("mutants au départ $i$ (sur $N=10$)")
    ax2.set_ylabel("probabilité d'envahir")
    ax2.set_title("La limite selon l'avantage $r$", fontsize=9)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(virgule))
    ax2.legend(fontsize=7, loc="upper left", frameon=False)
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "c06_fixation.pdf", dpi=300)
    fig.savefig(OUT / "c06_fixation.png", dpi=300)
    print("Moran N=10 r=1.5 i=1:", moran_fix(10, 1.5, 1))
    print("wrote", OUT / "c06_fixation.pdf")


if __name__ == "__main__":
    main()
