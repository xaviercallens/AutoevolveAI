"""Figure c16 (Z-RIESZ): Riesz energies of the triangular and square lattices at density one.

Left: per-point Riesz s-energy E_L(s) = sum_{a in L minus 0} |a|^{-s} for the covolume-one triangular lattice A and
the unit square lattice Z^2, for 2 < s <= 8, from the closed forms
    E_square(s) = 4 zeta(s/2) beta(s/2)
    E_tri(s)    = (2/sqrt 3)^{-s/2} * 6 zeta(s/2) L_{-3}(s/2)
(beta = Dirichlet L-function of the character mod 4, L_{-3} that of the character mod 3), cross-checked against direct
lattice sums with an integral tail correction. Right: partial sums over |a| <= R at s = 4 (they settle) and at s = 2
(they keep growing like 2 pi log R), which is why the statement is only informative for s > 2 (the divergence at s = 2
is a floating-point observation here, Tier X; the finiteness for s > 2 is the kernel-checked D1b).

Positive control (asserts): the values of papers/triangular_riesz/triangular_riesz.tex, Table 1, at rho = 1:
s = 3: 8.8927451004 / 9.0336216831; s = 4: 5.7833592997 / 6.0268120397; s = 6: 4.1412565472 / 4.6589136156.
Pencil numbers of the chapter (asserts): ring |a| <= 1.5 at s = 4 gives 4.5 (triangular) and 5 (square);
the negative control 2A has energy E_tri(4)/16.
Run: .venv/bin/python -I papers/discovery_journal_2026/code/fig16.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mpmath
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "papers" / "discovery_journal_2026" / "figures"
OKABE = {"orange": "#E69F00", "bleu_ciel": "#56B4E9", "vert": "#009E73", "jaune": "#F0E442",
         "bleu": "#0072B2", "vermillon": "#D55E00", "pourpre": "#CC79A7", "noir": "#000000"}
IVOIRE = "#FFFFF0"
mpmath.mp.dps = 30


def style() -> None:
    plt.rcParams.update({"font.family": "serif", "font.serif": ["DejaVu Serif"], "font.size": 9,
                         "axes.facecolor": IVOIRE, "figure.facecolor": IVOIRE, "savefig.facecolor": IVOIRE,
                         "axes.edgecolor": "#555555", "axes.linewidth": 0.6, "axes.grid": True,
                         "grid.color": "#dddddd", "grid.linewidth": 0.5, "axes.spines.top": False,
                         "axes.spines.right": False, "pdf.fonttype": 42,
                         "mathtext.fontset": "dejavuserif"})


def virgule(x: float, _pos: int) -> str:
    return f"{x:g}".replace(".", ",")


def e_square(s: float) -> float:
    u = mpmath.mpf(s) / 2
    return float(4 * mpmath.zeta(u) * mpmath.dirichlet(u, [0, 1, 0, -1]))


def e_tri(s: float) -> float:
    u = mpmath.mpf(s) / 2
    scale = (2 / mpmath.sqrt(3)) ** (-u)
    return float(scale * 6 * mpmath.zeta(u) * mpmath.dirichlet(u, [0, 1, -1]))


def lattice_points(kind: str, radius: float) -> np.ndarray:
    """Squared norms of the nonzero points of the covolume-one lattice inside the disk of given radius."""
    if kind == "square":
        b1, b2 = np.array([1.0, 0.0]), np.array([0.0, 1.0])
    else:
        c = np.sqrt(2.0 / np.sqrt(3.0))
        b1, b2 = np.array([c, 0.0]), np.array([c / 2.0, c * np.sqrt(3.0) / 2.0])
    m = int(np.ceil(radius / min(np.linalg.norm(b1), np.sqrt(3.0) / 2.0 * np.linalg.norm(b1)))) + 2
    j, k = np.meshgrid(np.arange(-m, m + 1), np.arange(-m, m + 1), indexing="ij")
    pts = j[..., None] * b1 + k[..., None] * b2
    r2 = (pts ** 2).sum(axis=-1).ravel()
    return r2[(r2 > 0) & (r2 <= radius ** 2)]


def direct_sum(kind: str, s: float, radius: float) -> float:
    r2 = lattice_points(kind, radius)
    tail = 2 * np.pi * radius ** (2 - s) / (s - 2)  # density one
    return float(np.sum(r2 ** (-s / 2)) + tail)


def main() -> None:
    style()
    table = {3: (8.8927451004, 9.0336216831), 4: (5.7833592997, 6.0268120397), 6: (4.1412565472, 4.6589136156)}
    for s, (t_ref, q_ref) in table.items():
        t, q = e_tri(s), e_square(s)
        assert abs(t - t_ref) < 1e-9 and abs(q - q_ref) < 1e-9, (s, t, q)
        td, qd = direct_sum("tri", s, 300.0), direct_sum("square", s, 300.0)
        assert abs(td - t) < 2e-3 and abs(qd - q) < 2e-3, (s, td, t, qd, q)
        print(f"s={s}: tri {t:.10f} (direct {td:.6f})  square {q:.10f} (direct {qd:.6f})")

    # pencil numbers: points with |a| <= 1.5 at s = 4
    ring_t = float(np.sum(lattice_points("tri", 1.5) ** -2.0))
    ring_q = float(np.sum(lattice_points("square", 1.5) ** -2.0))
    assert abs(ring_t - 4.5) < 1e-12 and abs(ring_q - 5.0) < 1e-12, (ring_t, ring_q)
    neg = e_tri(4) / 16
    assert neg < e_tri(4)
    print(f"ring |a|<=1.5, s=4: tri {ring_t}, square {ring_q}; 2A energy at s=4: {neg:.6f}")

    s_grid = np.linspace(2.6, 8.0, 109)
    et = np.array([e_tri(s) for s in s_grid])
    eq = np.array([e_square(s) for s in s_grid])
    assert np.all(et < eq)
    gap = 100 * (eq / et - 1)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.9))
    ax1.plot(s_grid, et, color=OKABE["bleu"], lw=1.4, label="réseau triangulaire")
    ax1.plot(s_grid, eq, color=OKABE["vermillon"], lw=1.2, ls="--", label="réseau carré")
    for s in table:
        ax1.plot([s], [table[s][0]], "o", ms=3.5, color=OKABE["bleu"])
        ax1.plot([s], [table[s][1]], "s", ms=3.5, mfc="none", color=OKABE["vermillon"])
    ax1.set_xlabel("exposant $s$ de la répulsion $1/r^s$")
    ax1.set_ylabel("énergie par point (densité 1)")
    ax1.set_title("Le triangulaire est toujours plus bas", fontsize=9)
    ax1.xaxis.set_major_formatter(plt.FuncFormatter(virgule))
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(virgule))
    axg = ax1.twinx()
    axg.plot(s_grid, gap, color=OKABE["vert"], lw=0.9, ls=":")
    axg.set_ylabel("écart carré/triangulaire (%)", color=OKABE["vert"], fontsize=8)
    axg.tick_params(axis="y", colors=OKABE["vert"], labelsize=7)
    axg.grid(False)
    axg.spines["right"].set_visible(True)
    axg.yaxis.set_major_formatter(plt.FuncFormatter(virgule))
    ax1.plot([], [], color=OKABE["vert"], lw=0.9, ls=":", label="écart en % (axe de droite)")
    ax1.legend(fontsize=7, loc="upper center", frameon=False)

    radii = np.geomspace(2.0, 200.0, 40)
    r2_all = lattice_points("tri", 200.0)
    part4 = [float(np.sum(r2_all[r2_all <= r * r] ** -2.0)) for r in radii]
    part2 = [float(np.sum(r2_all[r2_all <= r * r] ** -1.0)) for r in radii]
    assert abs(part4[-1] - e_tri(4)) < 1e-3
    slope = (part2[-1] - part2[-10]) / (np.log(radii[-1]) - np.log(radii[-10]))
    assert abs(slope - 2 * np.pi) < 0.2, slope
    print(f"s=2 partial-sum growth per unit log R: {slope:.3f} (2 pi = {2 * np.pi:.3f})")
    ax2.plot(radii, part4, "-o", ms=2.2, lw=1.0, color=OKABE["bleu"], label="$s=4$ : la somme se stabilise")
    ax2.axhline(e_tri(4), color=OKABE["bleu"], lw=0.6, ls="--")
    ax2.plot(radii, part2, "-^", ms=2.2, lw=1.0, color=OKABE["orange"],
             label="$s=2$ : elle grandit sans fin (X)")
    ax2.set_xscale("log")
    ax2.set_xlabel("rayon $R$ du disque sommé")
    ax2.set_ylabel("somme partielle, réseau triangulaire")
    ax2.set_title("Au-dessus de $s=2$, un minimum fini", fontsize=9)
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(virgule))
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(virgule))
    ax2.legend(fontsize=7, loc="upper left", frameon=False)
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "c16_riesz.pdf", dpi=300)
    fig.savefig(OUT / "c16_riesz.png", dpi=300)
    print(f"gap at s=2.6: {gap[0]:.2f} %, at s=8: {gap[-1]:.2f} %")
    print("wrote", OUT / "c16_riesz.pdf")


if __name__ == "__main__":
    main()
