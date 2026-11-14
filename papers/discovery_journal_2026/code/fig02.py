"""Figure c02: floating-point profiles of the DESI DR2 BAO (+BBN) chi^2, with the kernel-checked zones shaded.

Every plotted number is recomputed here from the exact data vector and inverse covariance stored in
results/certified_numerics/P2_likelihood/data.json and from the model formulas of the paper
(papers/certified_desi_h0/certified_desi_h0.tex). The curves are Tier X (floating point); the shaded zones are the
kernel-checked statements of results/certified_numerics/P2_likelihood/result.json and P3_h0/result.json.
Run: .venv/bin/python -I papers/discovery_journal_2026/code/fig02.py
"""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter
from scipy.integrate import quad
from scipy.optimize import brentq, minimize

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "papers" / "discovery_journal_2026" / "figures"
OKABE = {"orange": "#E69F00", "bleu_ciel": "#56B4E9", "vert": "#009E73", "jaune": "#F0E442",
         "bleu": "#0072B2", "vermillon": "#D55E00", "pourpre": "#CC79A7", "noir": "#000000"}
IVOIRE = "#FFFFF0"
C_KMS = 299792.458
Z = [0.295, 0.51, 0.51, 0.706, 0.706, 0.934, 0.934, 1.321, 1.321, 1.484, 1.484, 2.33, 2.33]
KIND = ["DV", "DM", "DH", "DM", "DH", "DM", "DH", "DM", "DH", "DM", "DH", "DH", "DM"]


def style() -> None:
    plt.rcParams.update({"font.family": "serif", "font.serif": ["DejaVu Serif"], "font.size": 9,
                         "axes.facecolor": IVOIRE, "figure.facecolor": IVOIRE, "savefig.facecolor": IVOIRE,
                         "axes.edgecolor": "#555555", "axes.linewidth": 0.6, "axes.grid": True,
                         "grid.color": "#dddddd", "grid.linewidth": 0.5, "axes.spines.top": False,
                         "axes.spines.right": False, "mathtext.fontset": "dejavuserif"})


def virgule(x: float, _pos: int) -> str:
    s = f"{x:g}"
    return s.replace(".", ",")


def load_data() -> tuple[np.ndarray, np.ndarray]:
    raw = json.loads((ROOT / "results/certified_numerics/P2_likelihood/data.json").read_text())
    d = np.array([float(Fraction(v)) for v in raw["d"]])
    p = np.zeros((13, 13))
    for i, j, v in raw["P"]:
        p[i, j] = float(Fraction(v))
    return d, p


def shapes(om: float) -> np.ndarray:
    """Predictions divided by K = c/(100 h r_d): chi, 1/E or (z chi^2 / E)^(1/3)."""
    out = []
    for z, k in zip(Z, KIND):
        e = np.sqrt(om * (1 + z) ** 3 + 1 - om)
        chi = quad(lambda x: 1.0 / np.sqrt(om * (1 + x) ** 3 + 1 - om), 0.0, z, epsabs=1e-13, epsrel=1e-13)[0]
        out.append({"DM": chi, "DH": 1.0 / e, "DV": (z * chi ** 2 / e) ** (1.0 / 3.0)}[k])
    return np.array(out)


def chi2_bao_at(om: float, kk: float, d: np.ndarray, p: np.ndarray) -> float:
    r = kk * shapes(om) - d
    return float(r @ p @ r)


def chi2_bao_prof(om: float, d: np.ndarray, p: np.ndarray) -> float:
    s = shapes(om)
    kk = (s @ p @ d) / (s @ p @ s)
    r = kk * s - d
    return float(r @ p @ r)


def rd_aubourg(om: float, h: float, ob: float) -> float:
    onu = 0.0107 * 0.06
    ocb = om * h * h - onu
    return 55.154 * np.exp(-72.3 * (onu + 0.0006) ** 2) / (ocb ** 0.25351 * ob ** 0.12807)


def chi2_tot(om: float, h: float, ob: float, d: np.ndarray, p: np.ndarray) -> float:
    kk = C_KMS / (100.0 * h * rd_aubourg(om, h, ob))
    return chi2_bao_at(om, kk, d, p) + ((ob - 0.02218) / 0.00055) ** 2


def prof_h(h: float, d: np.ndarray, p: np.ndarray) -> float:
    best = np.inf
    for om0 in (0.27, 0.30, 0.33):
        res = minimize(lambda v: chi2_tot(v[0], h, v[1], d, p), x0=[om0, 0.02218], method="Nelder-Mead",
                       options={"xatol": 1e-7, "fatol": 1e-9, "maxiter": 4000})
        best = min(best, float(res.fun))
    return best


def main() -> None:
    style()
    d, p = load_data()
    cert2 = json.loads((ROOT / "results/certified_numerics/P2_likelihood/result.json").read_text())
    cert3 = json.loads((ROOT / "results/certified_numerics/P3_h0/result.json").read_text())
    lo_fit, hi_fit = cert2["H6"]["interval"]

    # checks against the record
    fit_val = chi2_bao_prof(0.29743, d, p)
    print(f"check chi2_BAO at Om=0.29743, K profiled: {fit_val:.5f}  (record: certified [{lo_fit}, {hi_fit}], MCP 10.27106)")
    assert lo_fit <= fit_val <= hi_fit
    print(f"check EdS chi2 profiled: {chi2_bao_prof(1.0, d, p):.2f} (record: certified >= 1415.82)")
    assert chi2_bao_prof(1.0, d, p) >= 1415.82

    oms = np.linspace(0.20, 0.40, 161)
    prof = np.array([chi2_bao_prof(o, d, p) for o in oms])
    chimin = float(prof.min())
    om_best = float(oms[int(prof.argmin())])
    f = lambda o: chi2_bao_prof(o, d, p) - chimin - 25.0
    edge_lo = brentq(f, 0.21, om_best)
    edge_hi = brentq(f, om_best, 0.39)
    print(f"check floating Delta chi2 = 25 edges in Om: {edge_lo:.4f}, {edge_hi:.4f} (record: 0.2577, 0.3443)")
    assert abs(edge_lo - 0.2577) < 5e-4 and abs(edge_hi - 0.3443) < 5e-4

    hs = np.linspace(0.66, 0.75, 46)
    proft = np.array([prof_h(h, d, p) for h in hs])
    tmin = float(proft.min())
    h_best = float(hs[int(proft.argmin())])
    g = lambda h: prof_h(h, d, p) - tmin - 25.0
    h_cross = brentq(g, h_best, 0.75, xtol=1e-6)
    d73 = prof_h(0.73, d, p) - tmin
    print(f"check BAO+BBN min chi2 {tmin:.4f} at h~{h_best:.4f} (record: <= 10.2897 at h*=0.685901)")
    print(f"check Delta chi2 = 25 crossing H0 = {100*h_cross:.2f} (record ~71.6); Delta chi2 at H0=73: {d73:.1f} (record ~54.6)")
    print(f"check chi2_tot at h=0.73 profiled: {prof_h(0.73, d, p):.2f} (record: 64.91 in the threshold-65 control)")
    assert abs(100 * h_cross - 71.6) < 0.15 and abs(d73 - 54.6) < 0.6 and tmin <= 10.2897

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.3, 2.6))
    for a in (a1, a2):
        a.xaxis.set_major_formatter(FuncFormatter(virgule))
        a.yaxis.set_major_formatter(FuncFormatter(virgule))
    a1.axvspan(0.20, 0.255, color=OKABE["vermillon"], alpha=0.18, lw=0, label="zone exclue, vérifiée par le noyau")
    a1.axvspan(0.35, 0.40, color=OKABE["vermillon"], alpha=0.18, lw=0)
    a1.plot(oms, prof - chimin, color=OKABE["bleu"], lw=1.6, label="calcul flottant")
    a1.axhline(25, color=OKABE["noir"], lw=0.8, ls="--")
    a1.text(0.302, 27, "seuil 25", fontsize=8, ha="center")
    a1.set_xlim(0.20, 0.40)
    a1.set_ylim(0, 60)
    a1.set_xlabel(r"densité de matière $\Omega_m$")
    a1.set_ylabel(r"écart d'ajustement $\Delta\chi^2$")
    a1.set_title("(a) BAO seules", fontsize=9, loc="left")

    a2.axvspan(73, 75, color=OKABE["vermillon"], alpha=0.18, lw=0, label=r"$H_0\geq 73$ exclu (noyau)")
    a2.plot(100 * hs, proft - tmin, color=OKABE["bleu"], lw=1.6, label="calcul flottant")
    a2.axhline(25, color=OKABE["noir"], lw=0.8, ls="--")
    a2.plot([100 * h_cross], [25], "o", ms=5, color=OKABE["orange"], mec=IVOIRE, mew=1.2)
    a2.annotate(f"{100*h_cross:.1f}".replace(".", ","), (100 * h_cross, 25), xytext=(-30, 12),
                textcoords="offset points", fontsize=8)
    a2.set_xlim(66, 75)
    a2.set_ylim(0, 80)
    a2.set_xlabel(r"taux d'expansion $H_0$ (km/s/Mpc)")
    a2.set_title("(b) BAO + éléments légers", fontsize=9, loc="left")
    a2.set_ylabel(r"écart d'ajustement $\Delta\chi^2$")
    h1, l1 = a1.get_legend_handles_labels()
    h2, l2 = a2.get_legend_handles_labels()
    fig.legend(h1, l1, loc="lower center", ncol=2, fontsize=7.5, frameon=False)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"c02_profils.{ext}", dpi=300)
    print("wrote", OUT / "c02_profils.pdf", "and .png")
    print("record P3 verdict:", cert3["verdict"])


if __name__ == "__main__":
    main()
