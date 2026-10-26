"""Figures for the P6 preprint, generated from data/*.csv and data/results.json (no hand-typed values).

fig_he4.pdf   : (a) Donnelly-Barenghi Table 14.1 S(Q) against the Bogoliubov envelope sqrt(Q/2k*) and S_B; (b) margin S - bound.
fig_bec.pdf   : (a) Stamper-Kurn Fig. 3a points (Tier X) against the trapped-gas LDA model and the LDA-averaged bound;
                (b) the trapped-gas positive control: S_LDA / bound for four candidate comparators.
Run: /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I make_figures.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
D = HERE / "data"
COL = {"CONSISTENT": "#1b7837", "UNDECIDED": "#e08214", "REFUTED": "#b2182b"}


def rd(name: str) -> list[dict[str, str]]:
    return list(csv.DictReader((D / name).open()))


def fig_he4() -> None:
    R = json.loads((D / "results.json").read_text())
    ks = R["he4"]["kstar_inv_A"]
    dds = R["he4"]["peak"]["delta_ds"]
    rows = rd("test_he4.csv")
    Q = np.array([float(r["Q_invA"]) for r in rows]); S = np.array([float(r["S"]) for r in rows])
    key = np.array([r["key"] for r in rows]); ver = np.array([r["verdict"] for r in rows])
    bound = np.array([float(r["bound"]) for r in rows]); sb = np.array([float(r["S_bogoliubov_homog"]) for r in rows])
    qq = np.linspace(0.01, 7.0, 700)
    fig, ax = plt.subplots(1, 2, figsize=(10.4, 3.9))
    a = ax[0]
    a.plot(qq, np.sqrt(qq / (2 * ks)), color="k", lw=1.4, label=r"bound $\sqrt{Q/2k_*}$")
    a.plot(qq, qq / np.sqrt(ks ** 2 + qq ** 2), color="0.45", lw=1.2, ls="--", label=r"Bogoliubov $S_B$")
    a.axhline(1.0, color="0.7", lw=0.8, ls=":"); a.axvline(2 * ks, color="0.7", lw=0.8, ls=":")
    a.text(2 * ks + 0.05, 0.05, r"$2k_*$", color="0.4", fontsize=9)
    for v in ["CONSISTENT", "UNDECIDED", "REFUTED"]:
        for k, mk in [("1", "o"), ("2", "s")]:
            m = (ver == v) & (key == k)
            if m.any():
                a.scatter(Q[m], S[m], marker=mk, s=22, facecolors="none" if k == "1" else COL[v], edgecolors=COL[v], lw=1.1,
                          label=f"{v.lower()}, {'X-ray' if k == '1' else 'neutron'}")
    a.set_xlabel(r"$Q$ ($\mathrm{\AA}^{-1}$)"); a.set_ylabel(r"$S(Q)$"); a.set_xlim(0, 6.9); a.set_ylim(0, 1.6)
    a.legend(fontsize=6.5, loc="upper right", ncol=2, frameon=False); a.set_title(r"(a) $^4$He, $T=1.4$--$4$ K [Tier L data, Tier X test]", fontsize=9)
    b = ax[1]
    for v in ["CONSISTENT", "UNDECIDED", "REFUTED"]:
        m = ver == v
        b.scatter(Q[m], (S - bound)[m], s=18, color=COL[v], label=v.lower())
    b.axhline(0, color="k", lw=1.0); b.axhline(dds, color="k", lw=0.9, ls="--")
    b.text(0.2, dds + 0.015, rf"$\Delta_{{ds}}={dds:.3f}$ (post hoc)", fontsize=8)
    b.axvline(2 * ks, color="0.7", lw=0.8, ls=":")
    b.set_xlabel(r"$Q$ ($\mathrm{\AA}^{-1}$)"); b.set_ylabel(r"$S(Q)-B(Q)$"); b.set_xlim(0, 6.9)
    b.legend(fontsize=7, frameon=False, loc="upper right"); b.set_title("(b) margin over the bound", fontsize=9)
    fig.tight_layout(); fig.savefig(D / "fig_he4.pdf"); fig.savefig(D / "fig_he4.png", dpi=140); plt.close(fig)


def fig_bec() -> None:
    sk = rd("bec_stamper_kurn_fig3a_tierX.csv"); cur = rd("bec_model_curve_stamper_kurn_q.csv")
    mu = np.array([float(r["mu_over_h_kHz"]) for r in cur])
    col = lambda n: np.array([float(r[n]) for r in cur])
    fig, ax = plt.subplots(1, 2, figsize=(10.4, 3.9))
    a = ax[0]
    a.plot(mu, col("S_lda"), color="k", lw=1.4, label=r"trapped Bogoliubov (LDA) $S_{\rm LDA}$")
    a.plot(mu, col("bound_lda_avg"), color="#2166ac", lw=1.4, ls="--", label=r"LDA-averaged bound $B_{\rm LDA}$ (valid)")
    a.plot(mu, col("bound_peak"), color="#b2182b", lw=1.1, ls=":", label=r"single-$k_*$ bound, peak $c$ (fails control)")
    x = np.array([float(r["mu_over_h_kHz"]) for r in sk]); y = np.array([float(r["S"]) for r in sk]); e = np.array([float(r["sigma"]) for r in sk])
    a.errorbar(x, y, yerr=e, fmt="o", color="#e08214", capsize=3, label="Stamper-Kurn Fig. 3a (Tier X)")
    a.set_xlabel(r"$\mu/h$ (kHz)"); a.set_ylabel(r"$S(q)$, $q=2.506\ \mu\mathrm{m}^{-1}$"); a.set_xlim(0, 12.2); a.set_ylim(0, 1.0)
    a.legend(fontsize=6.5, frameon=False); a.set_title("(a) Na BEC, three absolute points", fontsize=9)
    b = ax[1]
    S = col("S_lda")
    for n, lab, c, ls in [("bound_lda_avg", r"$B_{\rm LDA}$", "#2166ac", "-"), ("bound_peak", r"peak $c$", "#b2182b", "-"),
                          ("bound_c_eff", r"$c_{\rm eff}=0.68\sqrt{\mu/m}$", "#e08214", "--"),
                          ("bound_mean_density", r"mean-density $c$", "#762a83", "--")]:
        b.plot(mu, S / col(n), color=c, ls=ls, lw=1.3, label=lab)
    b.axhline(1.0, color="k", lw=1.0); b.set_xlabel(r"$\mu/h$ (kHz)"); b.set_ylabel(r"$S_{\rm LDA}/\mathrm{bound}$")
    b.set_xlim(0, 12.2); b.legend(fontsize=7, frameon=False, loc="lower left"); b.set_title("(b) positive control: a valid bound stays $\\leq1$", fontsize=9)
    fig.tight_layout(); fig.savefig(D / "fig_bec.pdf"); fig.savefig(D / "fig_bec.png", dpi=140); plt.close(fig)


def main() -> int:
    fig_he4(); fig_bec()
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
