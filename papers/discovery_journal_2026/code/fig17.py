"""Figure c17 (G-RUSTY): why a stiff solver exists, on the test equation y' = -50 (y - cos t), y(0) = 0.

This is an illustrative Python computation, NOT output of rusty-SUNDIALS. It shows the phenomenon that CVODE-type
implicit (BDF) solvers are built for.
Left: explicit Euler with step h = 0.05 (lambda h = -2.5, amplification |1 - 2.5| = 1.5 per step: explodes),
explicit Euler with h = 0.01 (lambda h = -0.5: stable, positive control), implicit (backward) Euler with h = 0.05,
and scipy's variable-order BDF integrator, against the exact solution
    y(t) = (2500 cos t + 50 sin t)/2501 - (2500/2501) exp(-50 t).
Right: error at t = 1.5 against the step size for explicit and implicit Euler; the explicit method is only usable below
h = 2/50 = 0.04.
Pencil numbers of the chapter (asserts): on y' = -50 y with h = 0.05, explicit factor -1.5, implicit factor 1/3.5,
exact factor exp(-2.5).
Run: .venv/bin/python -I papers/discovery_journal_2026/code/fig17.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "papers" / "discovery_journal_2026" / "figures"
OKABE = {"orange": "#E69F00", "bleu_ciel": "#56B4E9", "vert": "#009E73", "jaune": "#F0E442",
         "bleu": "#0072B2", "vermillon": "#D55E00", "pourpre": "#CC79A7", "noir": "#000000"}
IVOIRE = "#FFFFF0"
LAM = 50.0
T_END = 1.5


def style() -> None:
    plt.rcParams.update({"font.family": "serif", "font.serif": ["DejaVu Serif"], "font.size": 9,
                         "axes.facecolor": IVOIRE, "figure.facecolor": IVOIRE, "savefig.facecolor": IVOIRE,
                         "axes.edgecolor": "#555555", "axes.linewidth": 0.6, "axes.grid": True,
                         "grid.color": "#dddddd", "grid.linewidth": 0.5, "axes.spines.top": False,
                         "axes.spines.right": False, "pdf.fonttype": 42, "mathtext.fontset": "dejavuserif"})


def virgule(x: float, _pos: int) -> str:
    return f"{x:g}".replace(".", ",")


def exact(t: np.ndarray) -> np.ndarray:
    return (2500 * np.cos(t) + 50 * np.sin(t)) / 2501 - 2500 / 2501 * np.exp(-LAM * t)


def rhs(t: float, y: np.ndarray) -> np.ndarray:
    return -LAM * (y - np.cos(t))


def explicit_euler(h: float) -> tuple[np.ndarray, np.ndarray]:
    n = int(round(T_END / h))
    t = np.linspace(0.0, n * h, n + 1)
    y = np.zeros(n + 1)
    for k in range(n):
        y[k + 1] = y[k] + h * (-LAM * (y[k] - np.cos(t[k])))
    return t, y


def implicit_euler(h: float) -> tuple[np.ndarray, np.ndarray]:
    n = int(round(T_END / h))
    t = np.linspace(0.0, n * h, n + 1)
    y = np.zeros(n + 1)
    for k in range(n):
        # y_{k+1} = y_k + h * (-LAM (y_{k+1} - cos t_{k+1}))  solved exactly (linear)
        y[k + 1] = (y[k] + h * LAM * np.cos(t[k + 1])) / (1 + h * LAM)
    return t, y


def main() -> None:
    style()
    h = 0.05
    assert abs((1 - LAM * h) - (-1.5)) < 1e-12
    assert abs(1 / (1 + LAM * h) - 1 / 3.5) < 1e-12
    print("pencil factors: explicit", 1 - LAM * h, "implicit", 1 / (1 + LAM * h), "exact", np.exp(-LAM * h))

    te, ye = explicit_euler(0.05)
    ts, ys = explicit_euler(0.01)
    ti, yi = implicit_euler(0.05)
    bdf = solve_ivp(rhs, (0.0, T_END), [0.0], method="BDF", rtol=1e-6, atol=1e-9, dense_output=True)
    assert bdf.success
    tt = np.linspace(0, T_END, 600)
    err_bdf = float(np.max(np.abs(bdf.sol(tt)[0] - exact(tt))))
    err_small = float(np.max(np.abs(ys - exact(ts))[ts >= 0.2]))  # after the fast transient
    err_imp = float(np.max(np.abs(yi - exact(ti))[ti >= 0.2]))
    assert abs(ye[-1]) > 1e3, ye[-1]
    assert err_small < 0.01 and err_imp < 0.05 and err_bdf < 1e-4, (err_small, err_imp, err_bdf)
    print(f"explicit h=0.05 final |y| = {abs(ye[-1]):.3e}; max errors for t >= 0.2: explicit h=0.01 {err_small:.2e}, "
          f"implicit h=0.05 {err_imp:.2e}, BDF {err_bdf:.2e} ({bdf.t.size - 1} steps)")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.9))
    ax1.plot(tt, exact(tt), color=OKABE["noir"], lw=1.6, label="solution exacte")
    ax1.plot(te[:8], ye[:8], "-o", ms=2.2, lw=0.8, color=OKABE["vermillon"],
             label="Euler explicite, pas 0,05 (sort du cadre)")
    ax1.plot(ts, ys, color=OKABE["bleu_ciel"], lw=1.0, ls="--", label="Euler explicite, pas 0,01")
    ax1.plot(ti, yi, "s", ms=2.6, mfc="none", color=OKABE["bleu"], label="Euler implicite, pas 0,05")
    ax1.plot(bdf.t, bdf.y[0], "^", ms=2.6, color=OKABE["vert"], label=f"BDF adaptatif ({bdf.t.size - 1} pas)")
    ax1.set_ylim(-4.5, 3.0)
    ax1.set_xlabel("temps $t$")
    ax1.set_ylabel("$y(t)$")
    ax1.set_title("$\\mathrm{d}y/\\mathrm{d}t = -50\\,(y-\\cos t)$ : la méthode naïve explose", fontsize=9)
    ax1.xaxis.set_major_formatter(plt.FuncFormatter(virgule))
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(virgule))
    ax1.legend(fontsize=6.5, loc="lower right", frameon=False)

    steps = np.array([0.001, 0.002, 0.005, 0.01, 0.02, 0.03, 0.0375, 0.0429, 0.05, 0.075, 0.1, 0.15])
    e_exp, e_imp = [], []
    for hh in steps:
        t1, y1 = explicit_euler(hh)
        t2, y2 = implicit_euler(hh)
        e_exp.append(abs(y1[-1] - exact(np.array([t1[-1]]))[0]))
        e_imp.append(abs(y2[-1] - exact(np.array([t2[-1]]))[0]))
    e_exp, e_imp = np.array(e_exp), np.array(e_imp)
    assert np.all(e_imp < 0.2) and e_exp[-1] > 1e3
    ax2.loglog(steps, e_exp, "-o", ms=3, color=OKABE["vermillon"], label="Euler explicite")
    ax2.loglog(steps, e_imp, "-s", ms=3, mfc="none", color=OKABE["bleu"], label="Euler implicite")
    ax2.axvline(2 / LAM, color=OKABE["noir"], lw=0.8, ls=":")
    ax2.text(2 / LAM * 1.06, 1e1, "seuil\n$h = 2/50$", fontsize=7)
    ax2.set_xlabel("pas de temps $h$")
    ax2.set_ylabel("erreur à $t = 1{,}5$")
    ax2.set_title("Au-delà du seuil, l'explicite diverge", fontsize=9)
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(virgule))
    ax2.legend(fontsize=7, loc="upper left", frameon=False)
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "c17_raideur.pdf", dpi=300)
    fig.savefig(OUT / "c17_raideur.png", dpi=300)
    print("errors explicit:", dict(zip(steps.tolist(), np.round(e_exp, 6).tolist())))
    print("wrote", OUT / "c17_raideur.pdf")


if __name__ == "__main__":
    main()
