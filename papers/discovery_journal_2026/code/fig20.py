"""Figure c20 (L-STELLARATOR): RK4 cools at resolved steps; its real failure is spurious trapping.

Left (computed here): one step of forward Euler, explicit midpoint (RK2) and classical RK4 applied to the harmonic
oscillator x' = p, p' = -x from (x, p) = (1, 0) with step y = omega * dt; the plotted quantity is the energy ratio
E_1 / E_0. Asserted against the closed forms proved in Lean in the record (doi:10.5281/zenodo.23532458):
Euler 1 + y^2, midpoint 1 + y^4/4, RK4 rho_4(y) = 1 - y^6/72 + y^8/576, with rho_4(1) = 569/576 and rho_4 = 1 at y^2 = 8.
Right (read from the record): fraction of the 2000 orbits started above the escape energy H* = 29/40 that escape
before T = 2000, for RK4 and relaxation RK (RRK), against the DOP853 reference, computed from the escape counts in
paper_a_v2_results.json (Zenodo record 23532458, copied unchanged to
papers/discovery_journal_2026/data/zenodo23532458_paper_a_v2_results.json; sha256 asserted). Asserted against the
published 0.618, 0.464 (dt = 0.4), 0.0905 (dt = 0.8); and the below-threshold controls: RK4 0 escapes at every dt,
forward Euler 2000 of 2000 at every dt (the control that must fail does fail).
Run: .venv/bin/python -I papers/discovery_journal_2026/code/fig20.py
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
BOOK = ROOT / "papers" / "discovery_journal_2026"
OUT = BOOK / "figures"
DATA = BOOK / "data" / "zenodo23532458_paper_a_v2_results.json"
SHA = "0a981862ffa73648fc0a15f90734786bada9cc280f83bb15ffb53759656939d9"
OKABE = {"orange": "#E69F00", "bleu_ciel": "#56B4E9", "vert": "#009E73", "jaune": "#F0E442",
         "bleu": "#0072B2", "vermillon": "#D55E00", "pourpre": "#CC79A7", "noir": "#000000"}
IVOIRE = "#FFFFF0"


def style() -> None:
    plt.rcParams.update({"font.family": "serif", "font.serif": ["DejaVu Serif"], "font.size": 9,
                         "axes.facecolor": IVOIRE, "figure.facecolor": IVOIRE, "savefig.facecolor": IVOIRE,
                         "axes.edgecolor": "#555555", "axes.linewidth": 0.6, "axes.grid": True,
                         "grid.color": "#dddddd", "grid.linewidth": 0.5, "axes.spines.top": False,
                         "axes.spines.right": False, "pdf.fonttype": 42, "mathtext.fontset": "dejavuserif"})


def virgule(x: float, _pos: int) -> str:
    return f"{x:g}".replace(".", ",")


def f(u: np.ndarray) -> np.ndarray:
    return np.array([u[1], -u[0]])


def step(method: str, u: np.ndarray, h: float) -> np.ndarray:
    if method == "euler":
        return u + h * f(u)
    if method == "midpoint":
        return u + h * f(u + h / 2 * f(u))
    k1 = f(u)
    k2 = f(u + h / 2 * k1)
    k3 = f(u + h / 2 * k2)
    k4 = f(u + h * k3)
    return u + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def ratio(method: str, h: float) -> float:
    u0 = np.array([1.0, 0.0])
    u1 = step(method, u0, h)
    return float((u1 @ u1) / (u0 @ u0))


def main() -> None:
    style()
    ys = np.linspace(0.0, 3.0, 301)
    r = {m: np.array([ratio(m, y) for y in ys]) for m in ("euler", "midpoint", "rk4")}
    assert np.allclose(r["euler"], 1 + ys ** 2, atol=1e-12)
    assert np.allclose(r["midpoint"], 1 + ys ** 4 / 4, atol=1e-12)
    assert np.allclose(r["rk4"], 1 - ys ** 6 / 72 + ys ** 8 / 576, atol=1e-10)
    rho1 = Fraction(1) - Fraction(1, 72) + Fraction(1, 576)
    assert rho1 == Fraction(569, 576) and abs(ratio("rk4", 1.0) - float(rho1)) < 1e-15
    assert abs(ratio("rk4", np.sqrt(8.0)) - 1.0) < 1e-12
    print("rho4(1) =", rho1, "=", float(rho1), "; Euler(1) =", ratio("euler", 1.0))

    raw = DATA.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SHA
    d = json.loads(raw)
    n = d["model"]["n_orbits"]
    assert n == 2000 and d["model"]["H_star"] == "29/40" and d["falsification"]["outcome"] == "REFUTED"
    ref = d["dop853_reference"]["above"]["escaped"] / n
    runs = {(x["method"], x["band"], x["dt"]): x for x in d["runs"]}
    dts = d["model"]["dts"]
    frac = {m: [runs[(m, "above", dt)]["escaped"] / n for dt in dts] for m in ("rk4", "rrk")}
    assert abs(ref - 0.618) < 1e-12
    assert abs(frac["rk4"][dts.index(0.4)] - 0.464) < 1e-12 and abs(frac["rk4"][dts.index(0.8)] - 0.0905) < 1e-12
    for dt in dts:
        assert runs[("rk4", "below", dt)]["escaped"] == 0
        assert runs[("rk4", "below", dt)]["frac_final_dH_le_0"] == 1.0
        assert runs[("euler", "below", dt)]["escaped"] == n
    mid_below = [runs[("midpoint", "below", dt)]["escaped"] for dt in dts]
    print("DOP853 reference escape fraction:", ref)
    print("RK4 above:", dict(zip(dts, frac["rk4"])), " RRK above:", dict(zip(dts, frac["rrk"])))
    print("below H*: RK4 escapes 0 at every dt; Euler", n, "of", n, "; midpoint", dict(zip(dts, mid_below)))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.9))
    ax1.plot(ys, r["euler"], color=OKABE["vermillon"], lw=1.2, label="Euler : $1+y^2$ (chauffe)")
    ax1.plot(ys, r["midpoint"], color=OKABE["orange"], lw=1.2, ls="--", label="point milieu : $1+y^4/4$ (chauffe)")
    ax1.plot(ys, r["rk4"], color=OKABE["bleu"], lw=1.6, label="RK4 : $\\rho_4(y)$ (refroidit si $y^2<8$)")
    ax1.axhline(1.0, color=OKABE["noir"], lw=0.7)
    ax1.axvline(np.sqrt(8.0), color=OKABE["noir"], lw=0.7, ls=":")
    ax1.text(np.sqrt(8.0) - 0.05, 1.9, "$y^2=8$", ha="right", fontsize=7)
    ax1.set_ylim(0.0, 2.6)
    ax1.set_xlabel("pas réduit $y = \\omega\\,\\Delta t$")
    ax1.set_ylabel("énergie après un pas / avant")
    ax1.set_title("Oscillateur simple : qui chauffe, qui refroidit", fontsize=9)
    ax1.xaxis.set_major_formatter(plt.FuncFormatter(virgule))
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(virgule))
    ax1.legend(fontsize=6.5, loc="lower left", frameon=False)

    ax2.axhline(ref, color=OKABE["noir"], lw=1.0, ls="--", label="référence précise (DOP853) : 0,618")
    ax2.plot(dts, frac["rk4"], "-o", ms=3.5, color=OKABE["bleu"], label="RK4")
    ax2.plot(dts, frac["rrk"], "-s", ms=3.5, mfc="none", color=OKABE["vert"], label="RK à relaxation")
    ax2.set_xscale("log")
    ax2.set_xticks(dts)
    ax2.set_xticklabels([virgule(x, 0) for x in dts])
    ax2.minorticks_off()
    ax2.set_ylim(0.0, 0.8)
    ax2.set_xlabel("pas de temps $\\Delta t$")
    ax2.set_ylabel("fraction qui s'échappe (sur 2000)")
    ax2.set_title("Au-dessus du seuil : RK4 retient à tort", fontsize=9)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(virgule))
    ax2.legend(fontsize=6.5, loc="lower left", frameon=False)
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "c20_rk4.pdf", dpi=300)
    fig.savefig(OUT / "c20_rk4.png", dpi=300)
    print("wrote", OUT / "c20_rk4.pdf")


if __name__ == "__main__":
    main()
