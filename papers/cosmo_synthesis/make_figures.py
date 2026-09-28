"""Figures for cosmo_synthesis.tex, drawn only from the result JSONs.

fig_pulls.pdf : pull (ours - published)/sigma_published for every numeric target of
                the four runs, with each target's own preregistered tolerance drawn
                as a grey band (none for the DR1 run, which was not preregistered).
fig_h0.pdf    : BAO+BBN H0, primary (exact CAMB r_d) and secondary (fitting formula,
                identical to the hash-locked first attempt) against the DESI values,
                with the preregistered strict and soft windows.

Run: /mnt/disks/disk-socrateai-local-1/venv-cosmo/bin/python make_figures.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#e4e3df"
BAND = "#e9e8e4"
SERIES = {"DR1": "#2a78d6", "DR2": "#eb6834", "H0": "#1baf7a", "eBOSS": "#eda100"}
MARK = {"DR1": "o", "DR2": "s", "H0": "D", "eBOSS": "^"}


def load(rel: str) -> Any:
    return json.loads((ROOT / rel).read_text())


def pull_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    d1 = load("results/bao_flcdm/desi_dr1_flcdm_fit.json")
    t = d1["external_validation_target"]
    f = d1["fit_manual_quad"]
    rows.append({"run": "DR1", "label": r"DR1 $\Omega_m$ ($\chi^2$-min)", "pull": (f["Om_m"] - t["Om_m"][0]) / t["Om_m"][1], "tol": None, "flag": False})
    rows.append({"run": "DR1", "label": r"DR1 $hr_d$ ($\chi^2$-min)", "pull": (f["rd_h_Mpc"] - t["rd_h_Mpc"][0]) / t["rd_h_Mpc"][1], "tol": None, "flag": False})
    d2 = load("results/desi_dr2_bao/fit.json")
    lab2 = {"DR2_LCDM_Om": r"DR2 $\Lambda$CDM $\Omega_m$", "DR2_LCDM_hrd_Mpc": r"DR2 $\Lambda$CDM $hr_d$",
            "DR2_wCDM_Om": r"DR2 $w$CDM $\Omega_m$", "DR2_wCDM_w": r"DR2 $w$CDM $w$"}
    for r in d2["results"]:
        rows.append({"run": "DR2", "label": lab2[r["name"]], "pull": r["pull_sigma"], "tol": 0.5, "flag": False})
    h = load("results/bao_bbn_h0/fit.json")
    pre = load("results/bao_bbn_h0/preregistration.json")["tolerance"]
    tolmap = {"T1_H0": pre["strict_in_units_of_sigma_pub_T1"], "T2_H0": pre["strict_in_units_of_sigma_pub_T2"],
              "T1b_Omega_m": 0.25, "T2b_Omega_m": 0.25, "G1_hrd": 0.25, "G1_Omega_m": 0.25, "G2_hrd": 0.25, "G2_Omega_m": 0.25}
    r3 = load("results/cosmo_synthesis/round3_response_checks.json")["h0_env_rerun"]
    v_rec = r3["committed"]["primary.T2_DR1"]["verdict"]
    v_re = r3["cosmo"]["summary"]["primary.T2_DR1"]["verdict"]
    t2lab = f"$H_0$ DR1+BBN ({v_rec} recorded; {v_re} on re-run)" if v_rec != v_re else f"$H_0$ DR1+BBN ({v_rec})"
    labh = {"T1_H0": r"$H_0$ DR2+BBN", "T1b_Omega_m": r"$\Omega_m$ DR2+BBN", "T2_H0": t2lab,
            "T2b_Omega_m": r"$\Omega_m$ DR1+BBN", "G1_hrd": r"gate G1 $hr_d$", "G1_Omega_m": r"gate G1 $\Omega_m$",
            "G2_hrd": r"gate G2 $hr_d$", "G2_Omega_m": r"gate G2 $\Omega_m$"}
    for p in h["pulls"]:
        if p["analysis"] == "secondary":
            continue
        rows.append({"run": "H0", "label": labh[p["target"]], "pull": p["pull_sigma"], "tol": tolmap[p["target"]], "flag": False})
    e = load("results/eboss_vs_desi/fit.json")
    tole = load("results/eboss_vs_desi/preregistration.json")["tolerance_sigma"]
    labe = {"SDSS_Om": r"SDSS $\Omega_m$", "SDSS_hrd_Mpc": r"SDSS $hr_d$ (secondary-sourced)",
            "DESI_DR2_Om": r"DESI DR2 $\Omega_m$ (eBOSS run)", "DESI_DR2_hrd_Mpc": r"DESI DR2 $hr_d$ (eBOSS run)"}
    for p in e["pulls"]:
        rows.append({"run": "eBOSS", "label": labe[p["name"]], "pull": p["pull_sigma"], "tol": tole,
                     "flag": not p["counts_toward_within_tolerance"]})
    return rows


def style(ax: plt.Axes) -> None:
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.xaxis.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def fig_pulls() -> None:
    rows = pull_rows()
    n = len(rows)
    fig, ax = plt.subplots(figsize=(6.4, 0.24 * n + 0.9))
    style(ax)
    ys = list(range(n))[::-1]
    for y, r in zip(ys, rows):
        if r["tol"] is not None:
            ax.fill_betweenx([y - 0.32, y + 0.32], -r["tol"], r["tol"], color=BAND, lw=0)
        c = SERIES[r["run"]]
        ax.plot([r["pull"]], [y], marker=MARK[r["run"]], ms=6.5, mfc="white" if r["flag"] else c, mec=c, mew=1.6, ls="none")
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks(ys)
    ax.set_yticklabels([r["label"] for r in rows], fontsize=7.5, color=INK)
    ax.set_xlim(-0.62, 0.62)
    ax.set_xlabel(r"pull = (ours $-$ published) / $\sigma_{\rm published}$", fontsize=8.5, color=INK)
    handles = [plt.Line2D([], [], marker=MARK[k], color=SERIES[k], ls="none", ms=6, label=lab) for k, lab in
               (("DR1", "DR1 flat-ΛCDM (not preregistered)"), ("DR2", "DESI DR2"), ("H0", "BAO+BBN $H_0$ (primary)"), ("eBOSS", "eBOSS vs DESI"))]
    handles.append(plt.Rectangle((0, 0), 1, 1, color=BAND, label="preregistered tolerance"))
    ax.legend(handles=handles, fontsize=7, frameon=False, loc="upper center", bbox_to_anchor=(0.4, -0.09 - 1.2 / n), ncol=3)
    fig.tight_layout()
    fig.savefig(HERE / "fig_pulls.pdf", bbox_inches="tight")
    fig.savefig(HERE / "fig_pulls.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def fig_h0() -> None:
    h = load("results/bao_bbn_h0/fit.json")
    pre = load("results/bao_bbn_h0/preregistration.json")
    tg = {t["id"]: t for t in pre["targets"]}
    r3 = load("results/cosmo_synthesis/round3_response_checks.json")["h0_env_rerun"]
    strict = pre["tolerance"]["strict_H0_km_s_Mpc"]
    soft = pre["tolerance"]["soft_H0_km_s_Mpc"]
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.4), sharey=True)
    for ax, (tid, vk, title) in zip(axes, (("T1", "verdict_T1", "DESI DR2 BAO + BBN"), ("T2", "verdict_T2", "DESI DR1 BAO + BBN"))):
        style(ax)
        t = tg[tid]
        ax.axvspan(t["value"] - soft, t["value"] + soft, color=BAND, lw=0)
        ax.axvspan(t["value"] - strict, t["value"] + strict, color="#d6d5d0", lw=0)
        pts = [(2, "DESI published", t["value"], t["sigma"], INK2, "o"),
               (1, "primary: exact CAMB $r_d$", h["primary"][vk]["H0"], h["primary"][vk]["sigma_H0"], SERIES["H0"], "D"),
               (0, "secondary = locked 1st attempt\n(fitting formula)", h["secondary"][vk]["H0"], h["secondary"][vk]["sigma_H0"], SERIES["DR1"], "s")]
        for y, lab, v, s, c, mk in pts:
            ax.errorbar([v], [y], xerr=[[s], [s]], fmt=mk, color=c, ms=6, lw=1.4, capsize=0)
        rr = r3["cosmo"]["summary"][f"primary.{'T1_DR2' if tid == 'T1' else 'T2_DR1'}"]
        ax.plot([rr["H0_mean"]], [1], marker="D", mfc="none", mec=SERIES["H0"], ms=8, lw=0)
        v_rec, v_re = h["primary"][vk]["verdict"], rr["verdict"]
        vt = v_rec if v_rec == v_re else f"{v_rec} (recorded run) / {v_re} (re-run)"
        ax.set_title(f"{title}\n{vt}", fontsize=8.5, color=INK)
        ax.set_xlabel(r"$H_0$ [km s$^{-1}$ Mpc$^{-1}$]", fontsize=8, color=INK)
        ax.set_yticks([2, 1, 0])
        ax.set_yticklabels([p[1] for p in pts], fontsize=7.2, color=INK)
        ax.set_ylim(-0.6, 2.6)
    fig.tight_layout()
    fig.savefig(HERE / "fig_h0.pdf", bbox_inches="tight")
    fig.savefig(HERE / "fig_h0.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    fig_pulls()
    fig_h0()
    print("wrote fig_pulls.pdf, fig_h0.pdf")


if __name__ == "__main__":
    main()
