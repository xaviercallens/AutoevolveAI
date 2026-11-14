"""Figure c10 (ED-11): the Rytova-Keldysh potential as a positive mixture of Gaussians.

Left: V(r) = (pi / (2 r0)) [H_0 - Y_0](r / r0) (Struve and Neumann functions, mpmath) and the Lean mixture
K(t) = int_0^inf w(a)/(2a) exp(-t/(4a)) da with w(a) = r0^{-1} erfcx(sqrt(a)/r0), t = r^2
(formal_cert/Autoresearch/KeldyshCM.lean, definitions keldysh and w), for r0 = 1, against the Coulomb law 1/r.
Right: the mixture weight m(a) = w(a)/(2a) (every weight positive), for r0 = 1.
Checks (asserts): the two forms agree on the plotted grid; the audit value at r0 = 0.7, r = 1.3
(papers/ar_keldysh_tmd/AUDIT.md section 3: 0.66931236059094...); the chapter's pencil value
e^{-t} - 2 e^{-2t} = -2/9 at t = ln(3/2) (signedMix negative control of the paper).
Run: .venv/bin/python -I papers/discovery_journal_2026/code/fig10.py
"""
from __future__ import annotations

from math import exp, log
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mpmath as mp
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "papers" / "discovery_journal_2026" / "figures"
OKABE = {"orange": "#E69F00", "bleu_ciel": "#56B4E9", "vert": "#009E73", "jaune": "#F0E442",
         "bleu": "#0072B2", "vermillon": "#D55E00", "pourpre": "#CC79A7", "noir": "#000000"}
IVOIRE = "#FFFFF0"
mp.mp.dps = 25


def style() -> None:
    plt.rcParams.update({"font.family": "serif", "font.serif": ["DejaVu Serif"], "font.size": 9,
                         "axes.facecolor": IVOIRE, "figure.facecolor": IVOIRE, "savefig.facecolor": IVOIRE,
                         "axes.edgecolor": "#555555", "axes.linewidth": 0.6, "axes.grid": True,
                         "grid.color": "#dddddd", "grid.linewidth": 0.5, "axes.spines.top": False,
                         "axes.spines.right": False})


def virgule(x: float, _pos: int) -> str:
    return f"{x:g}".replace(".", ",")


def v_struve(r0: float, r: float) -> mp.mpf:
    x = mp.mpf(r) / r0
    return mp.pi / (2 * r0) * (mp.struveh(0, x) - mp.bessely(0, x))


def weight(r0: float, a: mp.mpf) -> mp.mpf:
    """m(a) = w(a)/(2a), w(a) = r0^{-1} erfcx(sqrt(a)/r0), erfcx(x) = e^{x^2} erfc(x)."""
    x = mp.sqrt(a) / r0
    return mp.exp(x * x) * mp.erfc(x) / r0 / (2 * a)


def v_mixture(r0: float, r: float) -> mp.mpf:
    t = mp.mpf(r) ** 2
    return mp.quad(lambda a: weight(r0, a) * mp.exp(-t / (4 * a)), [0, t / 4, t, 10 * t, mp.inf])


def main() -> None:
    style()
    ref = v_struve(0.7, 1.3)
    assert abs(ref - mp.mpf("0.66931236059094967")) < mp.mpf("1e-15"), ref
    assert abs(v_mixture(0.7, 1.3) - mp.mpf("0.66931236059094957")) < mp.mpf("1e-14")
    t0 = log(1.5)
    signed = exp(-t0) - 2 * exp(-2 * t0)
    assert abs(signed + 2 / 9) < 1e-15
    print("audit point r0=0.7 r=1.3:", ref, " signedMix(ln 3/2) =", signed)

    r0 = 1.0
    rs = np.geomspace(0.02, 50, 70)
    vs = np.array([float(v_struve(r0, r)) for r in rs])
    vm = np.array([float(v_mixture(r0, r)) for r in rs])
    rel = np.max(np.abs(vm - vs) / vs)
    assert rel < 1e-10, rel
    assert np.all(vs > 0) and np.all(np.diff(vs) < 0)
    assert abs(vs[-1] * rs[-1] - 1) < 0.01  # Coulomb-like at large r
    print("max relative difference Struve vs mixture on grid:", rel, " r*V at r=50:", vs[-1] * rs[-1])

    aa = np.geomspace(1e-3, 1e3, 200)
    ma = np.array([float(weight(r0, mp.mpf(a))) for a in aa])
    assert np.all(ma > 0)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.9))
    ax1.plot(rs, vs, color=OKABE["bleu"], lw=1.8, label="forme classique")
    ax1.plot(rs[::4], vm[::4], "o", ms=3, mfc="none", color=OKABE["vermillon"], label="mélange de gaussiennes")
    ax1.plot(rs, 1 / rs, color=OKABE["noir"], lw=0.9, ls="--", label="loi de Coulomb $1/r$")
    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_xlabel(r"distance $r$ (en unités de $r_0$)")
    ax1.set_ylabel(r"potentiel $V(r)$ (pour $r_0=1$)")
    ax1.set_title("Deux écritures, une même force", fontsize=9)
    ax1.xaxis.set_major_formatter(plt.FuncFormatter(virgule))
    ax1.legend(fontsize=7, frameon=False, loc="lower left")

    ax2.plot(aa, ma, color=OKABE["vert"], lw=1.6)
    ax2.fill_between(aa, ma, 1e-6, color=OKABE["vert"], alpha=0.2, lw=0)
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_ylim(1e-5, None)
    ax2.set_xlabel(r"largeur $a$ de la cloche $e^{-r^2/(4a)}$")
    ax2.set_ylabel("poids dans le mélange")
    ax2.set_title("Tous les poids sont positifs", fontsize=9)
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(virgule))
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "c10_keldysh.pdf", dpi=300)
    fig.savefig(OUT / "c10_keldysh.png", dpi=300)
    print("wrote", OUT / "c10_keldysh.pdf")


if __name__ == "__main__":
    main()
