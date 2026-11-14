"""Chapter 5, use case U3: superfluid helium-4, structure factor S(k) and the Bogoliubov envelope sqrt(k/2k*).

Data: NOT Hugging Face. No structure-factor dataset was found on the Hub (searches recorded in the
ar_bogoliubov_sk and prog_superfluid_structure_factor papers). We use the published Table 14.1 of
Donnelly and Barenghi (J. Phys. Chem. Ref. Data 27, 1217, 1998; web edition), as extracted in
papers/prog_superfluid_structure_factor/data/he4_Sk_donnelly_table14_1.csv (99 points with Q > 0, keys 1 = X-ray,
2 = neutron, temperatures 1.4-4 K, no printed error bars).

Steps:
  1. k* = 2 m4 c / hbar with c = 238.3 m/s (Godfrin et al.) and m4 = 4.0026032 g/mol.
  2. Test per point: CONSISTENT if S <= sqrt(Q/2k*); REFUTED if S - sqrt(Q/2k*) > Delta; UNDECIDED otherwise, with
     Delta = |max S(key 1) - max S(key 2)| (post hoc threshold of the P6 paper, not preregistered).
  3. Positive control: S_B(Q) = Q / sqrt(k*^2 + Q^2) never fires. Negative control: S = 1 fires for every Q < 2k*.
  4. Optional (--gpe-json): Gross-Pitaevskii linear response from rusty-SUNDIALS qf-gpe2d (example
     bogoliubov_dispersion): measured S(k) for g = 1 stays below the envelope, the g = 0 control (S = 1) exceeds it.
  5. Figure figures/ch5_U3_helium.pdf and a JSON summary.

Usage: python -I ch5_U3_helium.py OUT_DIR [--csv PATH] [--gpe-json PATH]
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # AutoevolveAI worktree root
DEFAULT_CSV = ROOT / "papers/prog_superfluid_structure_factor/data/he4_Sk_donnelly_table14_1.csv"
FIG = Path(__file__).resolve().parent.parent / "figures" / "ch5_U3_helium.pdf"
HBAR = 1.054571817e-34
NA = 6.02214076e23


def kstar(c: float) -> float:
    m4 = 4.0026032e-3 / NA
    return 2.0 * m4 * c / HBAR * 1e-10  # per Angstrom


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out", type=Path)
    ap.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    ap.add_argument("--gpe-json", type=Path, default=None)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    rows = [r for r in csv.DictReader(open(a.csv)) if float(r["Q_invA"]) > 0]
    ks = kstar(238.3)
    ks_lo, ks_hi = kstar(238.2), kstar(238.4)
    pts = [(float(r["Q_invA"]), float(r["S"]), int(r["key"])) for r in rows]
    delta = abs(max(s for q, s, k in pts if k == 1) - max(s for q, s, k in pts if k == 2))
    verdicts = []
    for q, s, k in pts:
        b = math.sqrt(q / (2 * ks))
        v = "CONSISTENT" if s <= b else ("REFUTED" if s - b > delta else "UNDECIDED")
        verdicts.append({"Q": q, "S": s, "key": k, "bound": b, "verdict": v})
    count = {v: sum(x["verdict"] == v for x in verdicts) for v in ("CONSISTENT", "UNDECIDED", "REFUTED")}
    roton = [x for x in verdicts if 1.7 <= x["Q"] <= 2.4]
    sb_fires = sum(q / math.sqrt(ks * ks + q * q) > math.sqrt(q / (2 * ks)) for q, _, _ in pts)
    free_fires = [1.0 > math.sqrt(q / (2 * ks)) for q, _, _ in pts if q < 2 * ks]
    res = {"kstar": ks, "kstar_range": [ks_lo, ks_hi], "n_points": len(pts), "delta_ds": delta, "counts": count,
           "roton_n": len(roton), "roton_all_refuted": all(x["verdict"] == "REFUTED" for x in roton),
           "roton_ratio_range": [min(x["S"] / x["bound"] for x in roton), max(x["S"] / x["bound"] for x in roton)],
           "pos_control_SB_fires": sb_fires, "neg_control_free_fires": f"{sum(free_fires)}/{len(free_fires)}"}
    gpe = None
    if a.gpe_json and a.gpe_json.is_file():
        d = json.loads(a.gpe_json.read_text())
        g1 = d["sweep_phase_g1"]
        g0 = d["sweep_phase_g0"]
        gpe = {"g1": [(r["x"], r["S_freq"], r["bound"]) for r in g1], "g0": [(r["x"], r["S_freq"], r["bound"]) for r in g0]}
        res["gpe_g1_max_S_over_bound_minus_1"] = max(s / b - 1 for _, s, b in gpe["g1"])
        res["gpe_g1_max_rel_err_vs_epsB"] = max(abs(r["rel_err_vs_eps_B_g1"]) for r in g1)
        res["gpe_g0_fires_x_lt_2"] = f"{sum(s > b for x, s, b in gpe['g0'] if x < 2)}/{sum(1 for x, _, _ in gpe['g0'] if x < 2)}"
    ok = sb_fires == 0 and all(free_fires) and (gpe is None or res["gpe_g1_max_S_over_bound_minus_1"] < 1e-4)
    res["all_controls_pass"] = ok
    figure(verdicts, ks, gpe)
    (a.out / "ch5_U3_result.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
    if not ok:
        sys.exit(1)


def figure(v: list[dict], ks: float, gpe: dict | None) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = 2 if gpe else 1
    fig, ax = plt.subplots(1, n, figsize=(5.2 * n, 3.7), squeeze=False)
    ax = ax[0]
    qs = [0.02 * k for k in range(1, 351)]
    ax[0].plot(qs, [math.sqrt(q / (2 * ks)) for q in qs], "-", color="#52514e", lw=1.5, label=r"enveloppe $\sqrt{k/2k^*}$")
    ax[0].plot(qs, [q / math.sqrt(ks * ks + q * q) for q in qs], ":", color="#52514e", lw=1.5, label=r"$S_B$ (Bogoliubov)")
    style = {"CONSISTENT": ("o", "#1baf7a"), "UNDECIDED": ("D", "#eda100"), "REFUTED": ("s", "#eb6834")}
    for lab, (mk, colr) in style.items():
        xs = [x for x in v if x["verdict"] == lab]
        ax[0].plot([x["Q"] for x in xs], [x["S"] for x in xs], mk, ms=4.5, mfc="white", mec=colr, label=lab.lower())
    ax[0].set_xlabel(r"$Q$ ($\AA^{-1}$)")
    ax[0].set_ylabel(r"$S(Q)$")
    ax[0].set_title("(a) $^4$He, Donnelly-Barenghi Table 14.1", fontsize=9)
    ax[0].legend(frameon=False, fontsize=7, loc="lower right")
    if gpe:
        for key, colr, lab in (("g1", "#2a78d6", "GP, g = 1"), ("g0", "#eb6834", "GP, g = 0 (témoin nég.)")):
            pts = gpe[key]
            ax[1].loglog([p[0] for p in pts], [p[1] for p in pts], "o", ms=5, mfc="white", mec=colr, label=lab)
        xs = sorted(p[0] for p in gpe["g1"])
        ax[1].loglog(xs, [math.sqrt(x / 2) for x in xs], "-", color="#52514e", lw=1.5, label=r"$\sqrt{k/2k_s}$")
        ax[1].set_xlabel(r"$k/k_s$")
        ax[1].set_ylabel("S mesuré (fréquence)")
        ax[1].set_title("(b) réponse linéaire GP, rusty-SUNDIALS qf-gpe2d", fontsize=9)
        ax[1].legend(frameon=False, fontsize=7)
    for x in ax:
        x.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG)


if __name__ == "__main__":
    main()
