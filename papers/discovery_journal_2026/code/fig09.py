"""Figure c09 (ED-09): the bilayer dipolar-exciton interaction and its lattice energies.

Left: V(r) = 2(1/r - 1/sqrt(r^2 + d^2)) (units e^2/(4 pi eps), d = 1), with its far form d^2/r^3 and the
same-layer Coulomb pair term 2/r, computed from the formula of papers/ar_dipolar_exciton/main.tex.
Right: relative excess of the square and honeycomb lattices over the triangular one, e_X/e_tri - 1, against the
dimensionless layer separation d*sqrt(n), read from the record papers/ar_dipolar_exciton/data/lattice_gaps.jsonl
(Rust Ewald sums, Tier X). Markers: my own recomputation of e_sq/e_tri - 1 by a different method (expansion of
U = V/d^2 in d^2/r^2 and closed-form Epstein zeta functions, mpmath), valid for d below the nearest-neighbour
distance; asserted against the record and against the audit table (AUDIT.md section 2).
Run: .venv/bin/python -I papers/discovery_journal_2026/code/fig09.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mpmath as mp
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "papers" / "discovery_journal_2026" / "figures"
REC = ROOT / "papers" / "ar_dipolar_exciton" / "data" / "lattice_gaps.jsonl"
OKABE = {"orange": "#E69F00", "bleu_ciel": "#56B4E9", "vert": "#009E73", "jaune": "#F0E442",
         "bleu": "#0072B2", "vermillon": "#D55E00", "pourpre": "#CC79A7", "noir": "#000000"}
IVOIRE = "#FFFFF0"
mp.mp.dps = 30
A_TRI = mp.sqrt(2 / mp.sqrt(3))


def style() -> None:
    plt.rcParams.update({"font.family": "serif", "font.serif": ["DejaVu Serif"], "font.size": 9,
                         "axes.facecolor": IVOIRE, "figure.facecolor": IVOIRE, "savefig.facecolor": IVOIRE,
                         "axes.edgecolor": "#555555", "axes.linewidth": 0.6, "axes.grid": True,
                         "grid.color": "#dddddd", "grid.linewidth": 0.5, "axes.spines.top": False,
                         "axes.spines.right": False})


def virgule(x: float, _pos: int) -> str:
    return f"{x:g}".replace(".", ",")


def dirichlet_l(u: mp.mpf, period: int, residues: dict[int, int]) -> mp.mpf:
    """L(u, chi) = period^{-u} sum_a chi(a) zeta(u, a/period)."""
    return mp.power(period, -u) * sum(c * mp.zeta(u, mp.mpf(a) / period) for a, c in residues.items())


def z_tri(s: mp.mpf) -> mp.mpf:
    """sum over the density-one triangular lattice of |x|^{-s}: 6 zeta(u) L(u, chi_-3) a^{-s}, u = s/2."""
    u = s / 2
    return 6 * mp.zeta(u) * dirichlet_l(u, 3, {1: 1, 2: -1}) * mp.power(A_TRI, -s)


def z_sq(s: mp.mpf) -> mp.mpf:
    """sum over Z^2 minus 0 of |x|^{-s}: 4 zeta(u) beta(u)."""
    u = s / 2
    return 4 * mp.zeta(u) * dirichlet_l(u, 4, {1: 1, 3: -1})


def energy(d: float, z) -> mp.mpf:
    """e = (1/2) sum' U, U = V/d^2, expanded as -(1/d^2) sum_k binom(-1/2, k) d^{2k} Z(1+2k)."""
    dd = mp.mpf(d)
    tot = mp.mpf(0)
    for k in range(1, 600):
        term = mp.binomial(mp.mpf(-0.5), k) * dd ** (2 * k) * z(mp.mpf(1 + 2 * k))
        tot += term
        if abs(term) < mp.mpf(10) ** -24:
            break
    return -tot / dd ** 2


def main() -> None:
    style()
    rows = [json.loads(line) for line in REC.read_text().splitlines() if line.strip()]
    d_rec = np.array([r["d"] for r in rows])
    sq_rec = np.array([r["rel_gap_square"] for r in rows])
    hc_rec = np.array([r["rel_gap_honeycomb"] for r in rows])
    assert len(rows) == 41 and abs(d_rec[0] - 0.01) < 1e-12 and abs(d_rec[-1] - 3) < 1e-9
    assert np.all(sq_rec > 0) and np.all(hc_rec > 0)
    assert abs(sq_rec[0] - 1.584e-2) < 1e-5 and abs(sq_rec[-1] - 1.361e-3) < 1e-6

    # audit table values (AUDIT.md section 2): e_tri and e_sq at d = 0.066
    assert abs(float(energy(0.066, z_tri)) - 4.438685393575) < 1e-11
    assert abs(float(energy(0.066, z_sq)) - 4.508522037703) < 1e-11
    mine_d, mine_gap = [], []
    for k in (0, 8, 16, 24):
        d = rows[k]["d"]
        assert d < 0.9
        et, es = energy(d, z_tri), energy(d, z_sq)
        gap = float(es / et - 1)
        # the record prints d with 7 significant digits, so agreement is limited to about 1e-9 relative here
        # (the audit, at exact d, found about 1e-13)
        assert abs(float(et) - rows[k]["e_tri"]) < 5e-9 * rows[k]["e_tri"], (d, float(et), rows[k]["e_tri"])
        assert abs(gap - rows[k]["rel_gap_square"]) < 1e-8, (d, gap, rows[k]["rel_gap_square"])
        mine_d.append(d)
        mine_gap.append(gap)
        print(f"d={d:.4f}  e_tri mine {float(et):.12f} record {rows[k]['e_tri']:.12f}  gap {gap:.6e}")

    # pencil values of the chapter (d = 1)
    v = lambda r: 2 * (1 / r - 1 / np.sqrt(r * r + 1))  # noqa: E731
    assert abs(v(1.0) - (2 - np.sqrt(2))) < 1e-15 and abs(v(1.0) - 0.586) < 1e-3
    assert abs(v(10.0) - 0.000993) < 1e-6
    print("V(1) =", v(1.0), " V(10) =", v(10.0), " d^2/r^3 at 10 =", 1e-3)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.9))
    r = np.geomspace(0.05, 30, 400)
    ax1.plot(r, v(r), color=OKABE["bleu"], lw=1.6, label="entre deux excitons")
    ax1.plot(r, 1 / r ** 3, color=OKABE["vermillon"], lw=1.0, ls="--", label="loin : $d^2/r^3$")
    ax1.plot(r, 2 / r, color=OKABE["noir"], lw=0.9, ls=":", label="charges d'une même couche : $2/r$")
    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_xlabel("distance dans le plan $r$ (en unités de $d$)")
    ax1.set_ylabel("répulsion $V(r)$")
    ax1.set_title("Une répulsion entre petits dipôles", fontsize=9)
    ax1.xaxis.set_major_formatter(plt.FuncFormatter(virgule))
    ax1.legend(fontsize=7, frameon=False, loc="lower left")

    ax2.plot(d_rec, 100 * sq_rec, color=OKABE["orange"], lw=1.4, label="carré (registre)")
    ax2.plot(d_rec, 100 * hc_rec, color=OKABE["pourpre"], lw=1.4, label="nid d'abeille (registre)")
    ax2.plot(mine_d, 100 * np.array(mine_gap), "o", ms=4, mfc="none", color=OKABE["noir"],
             label="carré, recalculé ici")
    ax2.axvspan(0.0209, 0.1143, color=OKABE["bleu_ciel"], alpha=0.25, lw=0)
    ax2.text(0.0225, 3.2, "densités\nexpérimentales", fontsize=7)
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xlabel(r"séparation des couches $d\sqrt{n}$")
    ax2.set_ylabel("excès d'énergie sur le triangulaire (%)")
    ax2.set_title("Le triangulaire reste le plus bas", fontsize=9)
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(virgule))
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(virgule))
    ax2.legend(fontsize=7, frameon=False, loc="lower left")
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "c09_dipoles.pdf", dpi=300)
    fig.savefig(OUT / "c09_dipoles.png", dpi=300)
    print("wrote", OUT / "c09_dipoles.pdf")


if __name__ == "__main__":
    main()
