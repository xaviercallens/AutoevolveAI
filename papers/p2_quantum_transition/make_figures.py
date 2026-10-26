"""Figures for the B1 paper, generated from data/ only (copies of the B1 records). Run with the repo venv: python -I make_figures.py."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import checks

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
FIG = HERE / "fig"
FIG.mkdir(exist_ok=True)
C = {"blue": "#1f5fa8", "orange": "#d9730d", "green": "#2a8a4a", "red": "#b3261e", "grey": "#666666", "black": "#111111"}
plt.rcParams.update({"font.size": 8.5, "axes.labelsize": 9, "legend.fontsize": 7.5, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.dpi": 150, "savefig.dpi": 220})


def load(name: str):
    return json.loads((DATA / name).read_text())


def fig_phase() -> None:
    tab = load("result_numbers.json")["hbar_star_table"]
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.9), constrained_layout=True)
    a_all = [r["a"] for r in tab]
    s = [(r["a"], r["hbar_star"]) for r in tab if r["hbar_star"] is not None]
    ax[0].plot(*zip(*s), "o-", color=C["blue"], ms=3.5, label=r"harmonic spinodal $\hbar^*$")
    e = [(r["a"], r["Lam_1_edge"]["Lam1"]) for r in tab if r["Lam_1_edge"]]
    ax[0].plot(*zip(*e), "s-", color=C["orange"], ms=3.5, label=r"first-order point $\Lambda_1$ (stability edge)")
    m = [(r["a"], r["Lam_1_margin_0.01"][0]) for r in tab if r["Lam_1_margin_0.01"]]
    ax[0].plot(*zip(*m), "^--", color=C["green"], ms=3.5, label=r"$\Lambda_1$, margin $\geq 0.01$")
    lam = lambda g: [r["Lam_Lindemann"][g] for r in tab]
    ax[0].fill_between(a_all, lam("0.23"), lam("0.28"), color=C["grey"], alpha=0.30, lw=0, label=r"harmonic Lindemann, $\gamma_c\in[0.23,0.28]$")
    ax[0].plot(a_all, lam("0.3"), ":", color=C["grey"], lw=1.0, label=r"$\gamma_c=0.30$")
    sc = [(r["a"], r["scha"]["lam_star_scha"]) for r in tab if r["scha"] and r["scha"]["lam_star_scha"]]
    ax[0].plot(*zip(*sc), "D", color=C["black"], ms=4, label=r"SCHA spinodal")
    s1 = load("result_numbers.json")["scha"]["1"]
    lo = max(q["lam"] for q in s1["lap_ladder"] if q["lap"] > 0)
    hi = min(p[0] for p in s1["profiles_min_dE_stable"] if p[2] < 0)
    ax[0].errorbar([1.0], [0.5 * (lo + hi)], yerr=[[0.5 * (hi - lo)], [0.5 * (hi - lo)]], fmt="D", color=C["black"], ms=4, capsize=2)
    ax[0].axvspan(0.37668, 1.58148, color=C["blue"], alpha=0.05, lw=0)
    ax[0].set_ylim(0, 0.68)
    ax[0].set_xlim(0.28, 2.05)
    ax[0].set_xlabel(r"Gaussian width parameter $a$   ($V=\varepsilon e^{-\pi a r^2/l^2}$)")
    ax[0].set_ylabel(r"$\hbar_{\mathrm{eff}}$")
    ax[0].legend(loc="upper left", frameon=False, fontsize=6.6)
    ax[0].set_title("(a) transition couplings", loc="left", fontsize=9)
    g1 = [(r["a"], r["gamma_at_Lam_1_edge"]) for r in tab if r["gamma_at_Lam_1_edge"]]
    gs = [(r["a"], r["gamma_at_hbar_star"]) for r in tab if r["gamma_at_hbar_star"]]
    ax[1].plot(*zip(*gs), "o-", color=C["blue"], ms=3.5, label=r"$\gamma$ at $\hbar^*$")
    ax[1].plot(*zip(*g1), "s-", color=C["orange"], ms=3.5, label=r"$\gamma$ at $\Lambda_1$")
    ax[1].axhspan(0.23, 0.28, color=C["grey"], alpha=0.30, lw=0)
    ax[1].axhline(0.30, color=C["grey"], ls=":", lw=1.0)
    ax[1].set_ylim(0.2, 0.8)
    ax[1].set_xlabel(r"$a$")
    ax[1].set_ylabel(r"harmonic Lindemann ratio $\gamma$")
    ax[1].legend(loc="upper center", frameon=False)
    ax[1].set_title("(b) Lindemann ratio at the transition", loc="left", fontsize=9)
    fig.savefig(FIG / "fig_phase.png")
    plt.close(fig)


def fig_rays() -> None:
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.7), constrained_layout=True)
    for k, (a, nm) in enumerate([("1", "a = 1"), ("0.5", "a = 0.5")]):
        d = load(f"scan_a{a}.json")
        for key, col, lab in (("line_up", C["blue"], r"ray $\mathrm{Re}\,\tau=1/2$ (up)"), ("arc_to_i", C["orange"], r"ray $|\tau|=1$ (towards $i$)")):
            pts = [(abs(checks.disk_w(p["x"], p["y"])), p["ratio"]) for p in d["paths"][key] if p["stable_screen"]]
            ax[k].plot(*zip(*pts), ".", color=col, ms=3, label=lab)
        hs = next(r["hbar_star"] for r in load("result_numbers.json")["hbar_star_table"] if r["a"] == float(a))
        ax[k].axhline(hs, color=C["grey"], ls=":", lw=1, label=r"$\hbar^*$")
        sl = checks.ray_slopes()[a]
        w = np.linspace(0, 0.06, 20)
        ax[k].plot(w, sl["line_up"]["intercept"] + sl["line_up"]["slope"] * w, "-", color=C["blue"], lw=0.8, alpha=0.7)
        ax[k].plot(w, sl["arc_to_i"]["intercept"] + sl["arc_to_i"]["slope"] * w, "-", color=C["orange"], lw=0.8, alpha=0.7)
        ax[k].set_xlabel(r"$|w|$,  $w=(\tau-\rho)/(\tau-\bar\rho)$")
        ax[k].set_ylabel(r"tie coupling $\Delta E_{\mathrm{static}}/(-\Delta E_{\mathrm{zp}})$")
        ax[k].set_title(f"({'ab'[k]}) {nm}", loc="left", fontsize=9)
        ax[k].legend(frameon=False, loc="lower left" if a == "1" else "best")
    fig.savefig(FIG / "fig_rays.png")
    plt.close(fig)


def fig_scha() -> None:
    num = load("result_numbers.json")
    tab = {r["a"]: r for r in num["hbar_star_table"]}
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.8), constrained_layout=True)
    cols = [C["blue"], C["orange"], C["green"], C["red"]]
    for col, a in zip(cols, ("0.5", "0.7", "1", "1.3")):
        lad = num["scha"][a]["lap_ladder"]
        x = [q["lam"] for q in lad]
        y = [q["lap"] for q in lad]
        ax[0].plot(x, y, "o-", color=col, ms=3, label=f"SCHA, $a={a}$")
        r = tab[float(a)]
        xs = np.linspace(0, 0.5, 50)
        ax[0].plot(xs, 4 * (r["c_static"] + xs * r["c_zp"]), "--", color=col, lw=0.9)
    ax[0].axhline(0, color="k", lw=0.6)
    ax[0].set_ylim(-1.2, 0.6)
    ax[0].set_xlim(0, 0.52)
    ax[0].set_xlabel(r"$\hbar_{\mathrm{eff}}$")
    ax[0].set_ylabel(r"$\Delta E(\rho)$ (Laplacian; $>0$: local minimum)")
    ax[0].legend(frameon=False, loc="lower left", fontsize=6.8)
    ax[0].set_title("(a) SCHA (solid) vs harmonic (dashed)", loc="left", fontsize=9)
    sl = load("scha_slope_control.json")
    lam = np.array(sorted(float(k) for k in sl))
    slope = np.array([sl[str(k)]["slope_from_0"] if str(k) in sl else sl[f"{k:g}"]["slope_from_0"] for k in lam])
    c1 = np.polyfit(lam, slope, 1)
    xs = np.linspace(0, 0.012, 20)
    ax[1].plot(lam, slope, "o", color=C["blue"], ms=4, label="SCHA, finite differences ($a=1$)")
    ax[1].plot(xs, np.polyval(c1, xs), "-", color=C["blue"], lw=0.8)
    h = 4 * tab[1.0]["c_zp"]
    ax[1].axhline(h, color=C["red"], ls="--", lw=1, label=r"harmonic $4c_{\mathrm{zp}}$")
    ax[1].set_xlabel(r"$\hbar_{\mathrm{eff}}$")
    ax[1].set_ylabel(r"$(\Delta E_{\mathrm{SCHA}}-\Delta E_{\mathrm{static}})/\hbar_{\mathrm{eff}}$")
    ax[1].legend(frameon=False, loc="upper right")
    ax[1].set_title("(b) small-$\\hbar_{\\mathrm{eff}}$ slope control", loc="left", fontsize=9)
    fig.savefig(FIG / "fig_scha.png")
    plt.close(fig)


def fig_ft() -> None:
    kk = np.linspace(0, 8, 400)
    sh = checks.hankel(kk, lambda r: 1.0 / (1.0 + r ** 6), 400.0, 8000)
    ga = checks.hankel(kk, lambda r: np.exp(-r * r), 12.0, 400)
    fig, ax = plt.subplots(figsize=(3.4, 2.4), constrained_layout=True)
    ax.plot(kk, sh / sh[0], color=C["orange"], label=r"soft shoulder $1/(1+(r/R_c)^6)$")
    ax.plot(kk, ga / ga[0], color=C["blue"], label=r"Gaussian $e^{-r^2/R_c^2}$")
    ax.axhline(0, color="k", lw=0.6)
    ax.set_xlabel(r"$kR_c$")
    ax.set_ylabel(r"$\tilde u(k)/\tilde u(0)$")
    ax.legend(frameon=False, fontsize=6.8)
    fig.savefig(FIG / "fig_ft.png")
    plt.close(fig)


def main() -> int:
    fig_phase()
    fig_rays()
    fig_scha()
    fig_ft()
    print("figures written to", FIG)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
