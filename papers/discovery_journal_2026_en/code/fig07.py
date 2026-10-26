"""Figure c07 (ED-23): single-mutant fixation probabilities on small graphs, birth-death updating.

The configuration chain is bdK of formal_cert/Programmes/EvoGraph/BirthDeath.lean: node i reproduces with
probability mu_i f_S(i) / sum_k mu_k f_S(k) (f = r for mutants, 1 for residents) and its offspring replaces node j
with probability W i j. The graphs are those of formal_cert/Programmes/EvoGraph/Examples.lean (WH, Wstar, muStar,
Wcyc) plus the 4-node star (Tier X in the paper). Absorption probabilities are solved exactly with Fractions
(Gauss-Jordan on the 2^n configurations). Every plotted number is computed here.
Checks (asserts) against papers/p3_isothermal_theorem/AUDIT.md section 3: star n=3, r=2 centre 5/12, leaf 2/3,
uniform 7/12; Moran 4/7; star with mu = (1/2,1/4,1/4) centre 4/7; 4-cycle single mutant 8/15 and (P+, P-) =
(1/3, 1/6) at {0,1}, (2/3, 1/3) at {0,2}; W_H (n=3) 4/7; star n=4 centre 392/1265, leaf 168/253, mean 728/1265.
Run: .venv/bin/python -I papers/discovery_journal_2026_en/code/fig07.py
"""
from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "papers" / "discovery_journal_2026_en" / "figures"
OKABE = {"orange": "#E69F00", "bleu_ciel": "#56B4E9", "vert": "#009E73", "jaune": "#F0E442",
         "bleu": "#0072B2", "vermillon": "#D55E00", "pourpre": "#CC79A7", "noir": "#000000"}
IVOIRE = "#FFFFF0"
Matrix = list[list[Fraction]]
F = Fraction


def style() -> None:
    plt.rcParams.update({"font.family": "serif", "font.serif": ["DejaVu Serif"], "font.size": 9,
                         "axes.facecolor": IVOIRE, "figure.facecolor": IVOIRE, "savefig.facecolor": IVOIRE,
                         "axes.edgecolor": "#555555", "axes.linewidth": 0.6, "axes.grid": True,
                         "grid.color": "#dddddd", "grid.linewidth": 0.5, "axes.spines.top": False,
                         "axes.spines.right": False})


def virgule(x: float, _pos: int) -> str:
    return f"{x:g}"


def transitions(w: Matrix, mu: list[Fraction], r: Fraction, s: int) -> dict[int, Fraction]:
    """One step of bdK from configuration s (bitmask of mutants)."""
    n = len(w)
    fit = [r if (s >> i) & 1 else F(1) for i in range(n)]
    tot = sum((mu[i] * fit[i] for i in range(n)), F(0))
    out: dict[int, Fraction] = {}
    for i in range(n):
        for j in range(n):
            p = mu[i] * fit[i] / tot * w[i][j]
            if p == 0:
                continue
            t = s | (1 << j) if (s >> i) & 1 else s & ~(1 << j)
            out[t] = out.get(t, F(0)) + p
    return out


def up_down(w: Matrix, r: Fraction, s: int) -> tuple[Fraction, Fraction]:
    k = bin(s).count("1")
    tr = transitions(w, [F(1)] * len(w), r, s)
    up = sum((p for t, p in tr.items() if bin(t).count("1") == k + 1), F(0))
    down = sum((p for t, p in tr.items() if bin(t).count("1") == k - 1), F(0))
    return up, down


def fixation(w: Matrix, mu: list[Fraction], r: Fraction) -> dict[int, Fraction]:
    """Exact absorption probability into the all-mutant state, h = K h, h(0) = 0, h(full) = 1."""
    n = len(w)
    full = (1 << n) - 1
    states = list(range(1, full))
    idx = {s: k for k, s in enumerate(states)}
    m = len(states)
    a = [[F(0)] * (m + 1) for _ in range(m)]
    for s in states:
        row = a[idx[s]]
        row[idx[s]] += 1
        for t, p in transitions(w, mu, r, s).items():
            if t == full:
                row[m] += p
            elif t != 0:
                row[idx[t]] -= p
    for c in range(m):
        piv = next(k for k in range(c, m) if a[k][c] != 0)
        a[c], a[piv] = a[piv], a[c]
        pv = a[c][c]
        a[c] = [x / pv for x in a[c]]
        for k in range(m):
            if k != c and a[k][c] != 0:
                fac = a[k][c]
                a[k] = [x - fac * y for x, y in zip(a[k], a[c])]
    return {s: a[idx[s]][m] for s in states}


def moran(n: int, r: Fraction) -> Fraction:
    return (1 - 1 / r) / (1 - 1 / r ** n)


def star(n: int) -> Matrix:
    w = [[F(0)] * n for _ in range(n)]
    for j in range(1, n):
        w[0][j] = F(1, n - 1)
        w[j][0] = F(1)
    return w


def main() -> None:
    style()
    r = F(2)
    one3 = [F(1)] * 3
    one4 = [F(1)] * 4
    wh3 = [[F(1, 3)] * 3 for _ in range(3)]
    wcyc = [[F(0), F(1, 2), F(0), F(1, 2)], [F(1, 2), F(0), F(1, 2), F(0)],
            [F(0), F(1, 2), F(0), F(1, 2)], [F(1, 2), F(0), F(1, 2), F(0)]]
    wh4 = [[F(1, 4)] * 4 for _ in range(4)]

    assert moran(3, r) == F(4, 7) and moran(4, r) == F(8, 15)
    h_wh3 = fixation(wh3, one3, r)
    assert all(h_wh3[1 << v] == F(4, 7) for v in range(3))
    h_s3 = fixation(star(3), one3, r)
    centre3, leaf3 = h_s3[1], h_s3[2]
    uni3 = (centre3 + 2 * leaf3) / 3
    assert (centre3, leaf3, uni3) == (F(5, 12), F(2, 3), F(7, 12)), (centre3, leaf3, uni3)
    assert h_s3[3] == F(5, 6) and h_s3[6] == F(14, 15)
    h_s3mu = fixation(star(3), [F(1, 2), F(1, 4), F(1, 4)], r)
    assert h_s3mu[1] == F(4, 7)
    h_cyc = fixation(wcyc, one4, r)
    for s, hs in h_cyc.items():
        k = bin(s).count("1")
        assert hs == (1 - r ** -k) / (1 - r ** -4), (s, hs)
    assert up_down(wcyc, r, 0b0011) == (F(1, 3), F(1, 6))
    assert up_down(wcyc, r, 0b0101) == (F(2, 3), F(1, 3))
    h_wh4 = fixation(wh4, one4, r)
    assert h_wh4[1] == F(8, 15)
    h_s4 = fixation(star(4), one4, r)
    centre4, leaf4 = h_s4[1], h_s4[2]
    uni4 = (centre4 + 3 * leaf4) / 4
    assert (centre4, leaf4, uni4) == (F(392, 1265), F(168, 253), F(728, 1265)), (centre4, leaf4, uni4)
    print("n=3: complete 4/7, star centre", centre3, "leaf", leaf3, "uniform", uni3, "; star mu centre", h_s3mu[1])
    print("n=4: cycle", h_cyc[1], "complete", h_wh4[1], "star centre", centre4, "leaf", leaf4, "uniform", uni4)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={"width_ratios": [5, 4]})
    lab3 = ["complete", "star\n(centre)", "star\n(leaf)", "star\n(random)", "star\nweighted"]
    val3 = [h_wh3[1], centre3, leaf3, uni3, h_s3mu[1]]
    col3 = [OKABE["bleu"], OKABE["vermillon"], OKABE["vermillon"], OKABE["vermillon"], OKABE["vert"]]
    lab4 = ["complete", "cycle", "star\n(centre)", "star\n(random)"]
    val4 = [h_wh4[1], h_cyc[1], centre4, uni4]
    col4 = [OKABE["bleu"], OKABE["bleu"], OKABE["vermillon"], OKABE["vermillon"]]
    for ax, labs, vals, cols, n in [(ax1, lab3, val3, col3, 3), (ax2, lab4, val4, col4, 4)]:
        xs = range(len(vals))
        ax.bar(xs, [float(v) for v in vals], color=cols, width=0.62)
        for x, v in zip(xs, vals):
            ax.text(x, float(v) + 0.015, f"{v.numerator}/{v.denominator}", ha="center", fontsize=7)
        m = moran(n, r)
        ax.axhline(float(m), color=OKABE["noir"], ls="--", lw=0.9)
        ax.text(-0.4, 0.80, f"- - - well-mixed population: {m.numerator}/{m.denominator}",
                ha="left", fontsize=7)
        ax.set_xticks(list(xs))
        ax.set_xticklabels(labs, fontsize=7)
        ax.set_ylim(0, 0.85)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(virgule))
        ax.set_title(f"{n} sites, advantage $r=2$", fontsize=9)
    ax1.set_ylabel("chance that a mutant takes over")
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "c07_graphes.pdf", dpi=300)
    fig.savefig(OUT / "c07_graphes.png", dpi=300)
    print("wrote", OUT / "c07_graphes.pdf")


if __name__ == "__main__":
    main()
