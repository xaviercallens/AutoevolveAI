"""Figure c08 (Z-UO-BOOK): two illustrations of the student textbook's statement.

Left (the book's new result D4, open versus closed disks): for the density-one triangular lattice A of
papers/textbook_universal_optimality/FACTS.md section 1 (triangularPoint (j,k) = b^{-1/2} (j + k/2, k b), b = sqrt3/2,
so |p(j,k)|^2 = (j^2 + jk + k^2)/b), the count of points in the closed disk (|p| <= R) and in the open disk (|p| < R),
divided by pi R^2. Counting is exact in integers: |p|^2 <= R^2  <=>  j^2 + jk + k^2 <= b R^2, evaluated just at and
just below each shell radius.
Right: Gaussian lattice energies sum_{a != 0} exp(-pi alpha |a|^2) of the triangular and square lattices at density
one, against alpha. Check: Poisson self-duality theta(alpha) = theta(1/alpha)/alpha for both (each is congruent to its
dual), where theta includes the origin term 1.
Run: .venv/bin/python -I papers/discovery_journal_2026/code/fig08.py
"""
from __future__ import annotations

from math import exp, pi, sqrt
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
B = sqrt(3) / 2


def style() -> None:
    plt.rcParams.update({"font.family": "serif", "font.serif": ["DejaVu Serif"], "font.size": 9,
                         "axes.facecolor": IVOIRE, "figure.facecolor": IVOIRE, "savefig.facecolor": IVOIRE,
                         "axes.edgecolor": "#555555", "axes.linewidth": 0.6, "axes.grid": True,
                         "grid.color": "#dddddd", "grid.linewidth": 0.5, "axes.spines.top": False,
                         "axes.spines.right": False})


def virgule(x: float, _pos: int) -> str:
    return f"{x:g}".replace(".", ",")


def norms_tri(jmax: int) -> np.ndarray:
    """Integer quadratic form q = j^2 + jk + k^2 for |j|, |k| <= jmax (|p|^2 = q / b)."""
    j, k = np.meshgrid(np.arange(-jmax, jmax + 1), np.arange(-jmax, jmax + 1))
    return (j * j + j * k + k * k).ravel()


def theta_tri(alpha: float, jmax: int = 40) -> float:
    q = norms_tri(jmax)
    return float(np.sum(np.exp(-pi * alpha * q / B)))


def theta_sq(alpha: float, jmax: int = 40) -> float:
    j, k = np.meshgrid(np.arange(-jmax, jmax + 1), np.arange(-jmax, jmax + 1))
    return float(np.sum(np.exp(-pi * alpha * (j * j + k * k))))


def main() -> None:
    style()
    q = norms_tri(60)
    shells = np.unique(q[(q > 0) & (q <= 300)])
    # pencil example: nearest-neighbour shell q = 1 has six points, radius a = sqrt(1/b) = sqrt(2/sqrt3)
    assert int(np.sum(q == 1)) == 6 and shells[0] == 1
    a = sqrt(1 / B)
    assert abs(a - sqrt(2 / sqrt(3))) < 1e-15 and abs(a - 1.0746) < 1e-4
    n_closed_a = int(np.sum(q <= 1))
    n_open_a = int(np.sum(q < 1))
    assert (n_closed_a, n_open_a) == (7, 1)
    print("radius a =", a, "closed count", n_closed_a, "open count", n_open_a, "pi a^2 =", pi * a * a)

    radii, closed, opened = [], [], []
    for s in shells:
        rad = sqrt(s / B)
        radii.append(rad)
        closed.append(np.sum(q <= s) / (pi * rad * rad))
        opened.append(np.sum(q < s) / (pi * rad * rad))
    radii_a = np.array(radii)
    closed_a, opened_a = np.array(closed), np.array(opened)
    big = radii_a > 15
    print("at largest shell R =", radii_a[-1], "closed ratio", closed_a[-1], "open ratio", opened_a[-1])
    assert abs(closed_a[big] - 1).max() < 0.15 and abs(opened_a[big] - 1).max() < 0.15
    assert np.all(closed_a >= opened_a)

    alphas = np.geomspace(0.25, 4.0, 60)
    for al in (0.5, 1.0, 2.0, 0.3):
        for th in (theta_tri, theta_sq):
            assert abs(th(al) - th(1 / al) / al) < 1e-12 * th(al), (th.__name__, al)
    e_tri = np.array([theta_tri(al) - 1 for al in alphas])
    e_sq = np.array([theta_sq(al) - 1 for al in alphas])
    assert np.all(e_tri < e_sq)
    print("alpha=1: E_tri", theta_tri(1.0) - 1, "E_sq", theta_sq(1.0) - 1)
    assert abs((theta_tri(1.0) - 1) - 6 * exp(-pi / B) * 1.0) < 0.01  # first shell dominates at alpha = 1

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.9))
    ax1.plot(radii_a, closed_a, "o", ms=2.2, color=OKABE["vermillon"], label="disque fermé ($\\leq R$)")
    ax1.plot(radii_a, opened_a, "o", ms=2.2, color=OKABE["bleu"], label="disque ouvert ($< R$)")
    ax1.axhline(1.0, color=OKABE["noir"], lw=0.8, ls="--")
    ax1.set_xscale("log")
    ax1.set_xlabel("rayon $R$ (aux rayons des couronnes)")
    ax1.set_ylabel(r"points comptés $/\ (\pi R^2)$")
    ax1.set_title("Fermé ou ouvert : même densité limite", fontsize=9)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(virgule))
    ax1.xaxis.set_major_formatter(plt.FuncFormatter(virgule))
    ax1.legend(fontsize=7, frameon=False)

    excess = 100 * (e_sq - e_tri) / e_tri
    ax2.plot(alphas, excess, color=OKABE["orange"], lw=1.4)
    ax2.set_yscale("log")
    ax2.set_xscale("log")
    ax2.set_xticks([0.25, 0.5, 1, 2, 4])
    ax2.minorticks_off()
    ax2.set_xlabel(r"paramètre $\alpha$ de la répulsion gaussienne $e^{-\pi\alpha r^2}$")
    ax2.set_ylabel("excès d'énergie du carré (%)")
    ax2.set_title("Densité 1 : le carré est toujours au-dessus", fontsize=9)
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(virgule))
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(virgule))
    print("excess % at alpha = 0.25, 1, 4:", excess[0], 100 * ((theta_sq(1.0) - theta_tri(1.0)) / (theta_tri(1.0) - 1)),
          excess[-1])
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "c08_disques.pdf", dpi=300)
    fig.savefig(OUT / "c08_disques.png", dpi=300)
    print("wrote", OUT / "c08_disques.pdf")


if __name__ == "__main__":
    main()
