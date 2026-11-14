"""B1 summary: hbar*(a), Lam_1(a) with stability-margin thresholds, Lindemann ratios, figures.

usage: python -I b1_summary.py B1DIR

Reads data/b1a_curvature.json, data/scan_a*.json/.csv, data/scha.json (optional); writes data/summary.json and
figures/*.png. Lam_1(m) = min over sampled shapes with screened stability margin min(lam_lo/|k|^2) >= m and
dE_zp < 0 of dE_static/(-dE_zp) (N = 32 Duffy, scan grid 0.005). m = 0 is the harmonic edge value; m > 0 keeps only
shapes away from the dynamical-stability boundary (the triangular lattice itself has margin ~0.03 at a = 1).
Lindemann: gamma(Lam) = sqrt(Lam <|u|^2>/Lam) / a_nn at the triangular lattice, harmonic; Lam_L(gamma_c) =
gamma_c^2 a_nn^2 / (<|u|^2>/Lam) is the harmonic Lindemann melting estimate (scales like gamma_c^2).
"""

import csv
import glob
import json
import math
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b1_lib as L  # noqa: E402

MARGINS = (0.0, 0.005, 0.01, 0.02)
GAMMAS = (0.20, 0.23, 0.25, 0.28, 0.30)


def main() -> None:
    d = sys.argv[1]
    curv = {round(r["a"], 6): r for r in json.load(open(os.path.join(d, "data", "b1a_curvature.json")))["rows"]}
    scha = {}
    sp = os.path.join(d, "data", "scha.json")
    if os.path.exists(sp):
        scha = json.load(open(sp))
    rows = []
    for f in sorted(glob.glob(os.path.join(d, "data", "scan_a*.json")), key=lambda s: float(os.path.basename(s)[6:-5])):
        sj = json.load(open(f))
        a = sj["a"]
        pts = list(csv.DictReader(open(f[:-5] + ".csv")))
        tri_margin = L.quick_stable(a, *L.RHO)[1]
        lam1 = {}
        for m in MARGINS:
            best = None
            for p in pts:
                if p["stable_screen"] != "True" or float(p["min_ratio_screen"]) < m:
                    continue
                dz = float(p["dEzp"])
                if dz >= 0:
                    continue
                ratio = float(p["dEs"]) / (-dz)
                if best is None or ratio < best[0]:
                    best = (ratio, float(p["x"]), float(p["y"]), float(p["min_ratio_screen"]))
            lam1[f"{m:g}"] = best
        c = curv.get(round(a, 6))
        u2l = c["u2_per_lam_rho"] if c else L.u2_harmonic_per_lam(a, *L.RHO, 64)
        hs = c["hbar_star"] if c else None
        g = (lambda lam: math.sqrt(lam * u2l) / L.A_NN)
        v = sj["Lam_1"]
        row = {
            "a": a, "rho_sigma2": 1 / (math.pi * a), "c_static": c["c_static"] if c else None, "c_zp": c["c_zp"] if c else None,
            "hbar_star": hs, "tri_margin": tri_margin,
            "Lam1_verified_full_stability": None if v is None else {"x": v["x"], "y": v["y"], "Lam1": v["ratio_N64"], "margin_full": v["full_stability"]["min_ratio_lam_over_k2"]},
            "Lam1_by_margin": lam1, "u2_per_lam": u2l,
            "gamma_at_hbar_star": g(hs) if hs else None,
            "gamma_at_Lam1_edge": g(v["ratio_N64"]) if v else None,
            "Lam_Lindemann": {f"{gc:g}": gc * gc * L.A_NN**2 / u2l for gc in GAMMAS},
        }
        if f"{a:g}" in scha:
            s = scha[f"{a:g}"]
            row["scha"] = {k: s.get(k) for k in ("lam_star_scha", "breakdown_lam", "gamma_at_lam_star_scha")}
        rows.append(row)
    json.dump(rows, open(os.path.join(d, "data", "summary.json"), "w"), indent=1)
    # table to stdout
    print("| a | rho sigma^2 | c_static | c_zp | hbar* | gamma(hbar*) | Lam_1 edge (tau) | Lam_1 margin>=0.01 | gamma(Lam_1 edge) | Lam_L(0.23) | Lam_L(0.28) | SCHA Lam* |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        v = r["Lam1_verified_full_stability"]
        m1 = r["Lam1_by_margin"]["0.01"]
        sc = r.get("scha", {}).get("lam_star_scha")
        print(f"| {r['a']:g} | {r['rho_sigma2']:.3f} | {r['c_static']:.5f} | {r['c_zp']:+.5f} | "
              f"{'%.4f' % r['hbar_star'] if r['hbar_star'] else 'none (c_zp>0)'} | {'%.3f' % r['gamma_at_hbar_star'] if r['gamma_at_hbar_star'] else '-'} | "
              f"{'%.4f (%.3f, %.3f)' % (v['Lam1'], v['x'], v['y']) if v else 'none'} | {'%.4f (%.3f, %.3f)' % m1[:3] if m1 else 'none'} | "
              f"{'%.3f' % r['gamma_at_Lam1_edge'] if r['gamma_at_Lam1_edge'] else '-'} | {r['Lam_Lindemann']['0.23']:.4f} | {r['Lam_Lindemann']['0.28']:.4f} | "
              f"{'%.4f' % sc if sc else '-'} |")
    # figure: hbar*(a), Lam_1(a), Lindemann band
    cr = sorted(curv.values(), key=lambda r: r["a"])
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    xs = [r["a"] for r in cr if r["hbar_star"] and r["hbar_star"] < 1]
    ax[0].plot(xs, [r["hbar_star"] for r in cr if r["hbar_star"] and r["hbar_star"] < 1], "o-", label="harmonic spinodal hbar* = -c_static/c_zp")
    ax[0].plot([r["a"] for r in rows if r["Lam1_verified_full_stability"]], [r["Lam1_verified_full_stability"]["Lam1"] for r in rows if r["Lam1_verified_full_stability"]], "s-", label="Lam_1 (first-order, harmonic-stability edge)")
    xm = [r["a"] for r in rows if r["Lam1_by_margin"]["0.01"]]
    ax[0].plot(xm, [r["Lam1_by_margin"]["0.01"][0] for r in rows if r["Lam1_by_margin"]["0.01"]], "^--", label="Lam_1, shapes with margin >= 0.01")
    xl = [r["a"] for r in cr]
    lo = [0.23**2 * L.A_NN**2 / r["u2_per_lam_rho"] for r in cr]
    hi = [0.28**2 * L.A_NN**2 / r["u2_per_lam_rho"] for r in cr]
    ax[0].fill_between(xl, lo, hi, color="grey", alpha=0.3, label="harmonic Lindemann melting, gamma_c in [0.23, 0.28]")
    sx = [r["a"] for r in rows if r.get("scha", {}).get("lam_star_scha")]
    if sx:
        ax[0].plot(sx, [r["scha"]["lam_star_scha"] for r in rows if r.get("scha", {}).get("lam_star_scha")], "D", color="k", label="SCHA spinodal")
    ax[0].set_xlabel("a  (V = exp(-pi a r^2), unit density)")
    ax[0].set_ylabel("hbar_eff")
    ax[0].set_ylim(0, 0.35)
    ax[0].axvspan(0.37668, 1.58148, color="C2", alpha=0.07)
    ax[0].legend(fontsize=7)
    # paths at a = 1
    sj = json.load(open(os.path.join(d, "data", "scan_a1.json")))
    for k, mk in (("line_up", "o"), ("arc_to_i", "s")):
        p = [q for q in sj["paths"][k] if q["ratio"] is not None]
        ax[1].plot([q["r"] for q in p], [q["ratio"] for q in p], mk + "-", ms=3, label=f"{k}: dE_static/(-dE_zp)")
        un = [q for q in p if not q["stable_screen"]]
        if un:
            ax[1].plot([q["r"] for q in un], [q["ratio"] for q in un], "x", color="r")
    ax[1].axhline(curv[1.0]["hbar_star"], color="k", lw=0.8, ls=":", label="hbar*(a=1)")
    ax[1].set_xlabel("|tau - rho| / Im rho")
    ax[1].set_ylabel("tie value of hbar_eff")
    ax[1].set_title("a = 1: harmonic tie coupling along the two mirror lines (x = unstable)")
    ax[1].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(d, "figures", "fig_b1_hbar_star.png"), dpi=150)

    # figure: SCHA Lap E(rho) vs Lam against the harmonic line 4 (c_static + Lam c_zp)
    if scha:
        fig, ax = plt.subplots(figsize=(6, 4.2))
        for i, (ak, sr) in enumerate(sorted(scha.items(), key=lambda kv: float(kv[0]))):
            a = float(ak)
            lad = sr["lap_ladder"]
            ax.plot([q["lam"] for q in lad], [q["lap"] for q in lad], "o-", color=f"C{i}", label=f"SCHA a = {a:g}")
            c = curv.get(round(a, 6))
            if c:
                lm = [0, max(q["lam"] for q in lad)]
                ax.plot(lm, [4 * (c["c_static"] + v * c["c_zp"]) for v in lm], "--", color=f"C{i}", lw=0.8)
                gl = 0.23**2 * L.A_NN**2 / c["u2_per_lam_rho"]
                ax.axvline(gl, color=f"C{i}", ls=":", lw=0.8)
        ax.axhline(0, color="k", lw=0.6)
        ax.set_xlabel("hbar_eff")
        ax.set_ylabel("Lap E(rho)  (>0: triangular local minimum)")
        ax.set_title("SCHA (solid) vs harmonic (dashed); dotted: harmonic Lindemann gamma_c = 0.23", fontsize=8)
        ax.set_ylim(-1.5, 1.0)
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(os.path.join(d, "figures", "fig_b1_scha_curvature.png"), dpi=150)

    # result.json (machine-readable verdicts; every number is read from the data files above)
    ctl = json.load(open(os.path.join(d, "data", "controls.json")))
    res = {
        "item": "B1", "date": "2026-10-26", "tier": "X (B1a-c numerics), L (B1d literature)",
        "hbar_star_table": [{k: r[k] for k in ("a", "rho_sigma2", "c_static", "c_zp", "hbar_star", "gamma_at_hbar_star")}
                             | {"Lam_1_edge": r["Lam1_verified_full_stability"], "Lam_1_margin_0.01": r["Lam1_by_margin"]["0.01"],
                                "gamma_at_Lam_1_edge": r["gamma_at_Lam1_edge"], "Lam_Lindemann": r["Lam_Lindemann"], "scha": r.get("scha")} for r in rows],
        "scha": {k: {kk: v.get(kk) for kk in ("breakdown_lam", "lap_ladder", "lam_star_scha", "gamma_at_lam_star_scha", "harmonic_Lam_1")}
                 | {"profiles_min_dE_stable": [[p["lam"], p["gamma_rho"], p["min_dE_stable"]] for p in v["profiles"]]} for k, v in scha.items()},
        "controls": {"frozen_phonon_max_rel": ctl["frozen_phonon_max_rel"], "frozen_phonon_planted_bug_rel": ctl["frozen_phonon_bug"][0]["rel"],
                     "lindemann_uniform_grid_observed_order": {str(r["a"]): r["observed_order"] for r in ctl["lindemann_quadrature"]},
                     "negative_control_a": {str(r["a"]): {"c_zp": r["c_zp"], "hbar_star": r["hbar_star"], "Lam_1": r["Lam1_verified_full_stability"]} for r in rows if r["a"] in (0.3, 2.0)}},
    }
    json.dump(res, open(os.path.join(d, "result_numbers.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
