"""Chapter 5, use case U4: the sigma = 3 dispersive shell model and its enstrophy bound along trajectories.

Steps:
  1. Data: Hugging Face polymathic-ai/turbulent_radiative_layer_2D (The Well, CC-BY-4.0), revision 2ee77565...,
     file data/test/turbulent_radiative_layer_tcool_0.32.hdf5. If the file is on disk its sha256 is checked.
     The dyadic shell moduli of 4 snapshots (well_amps.txt) were derived from it by the crate script
     results/sigma3/scripts/well_spectrum.py + make_amps.py (needs h5py, absent from the AutoevolveAI .venv);
     this script reads them from the crate.
  2. rusty-SUNDIALS qf-shell-cascade, binary sigma3_study `full`: CVODE (BDF, analytic Jacobian) runs of
     P1 (positive control: conservation converges with rtol), N1 (negative control: a perturbed coupling breaks
     conservation at a level that does not shrink with rtol), S3 (sigma = 3 truncation sweep), C2 (sigma = 2 versus
     sigma = 3 on top-shell data) and W (24 runs initialised from The Well).
  3. Checks: every sigma = 3 run has sup_t 2 D Omega(t) / (H_3(0) + S(0)^{3/2}) <= 1 (the Lean bound); the
     sigma = 2 control exceeds 1 and grows with n_max.
  4. Figure figures/ch5_U4_shell.pdf and a JSON summary.

Usage: python -I ch5_U4_shell.py OUT_DIR [--bin DIR] [--crate DIR] [--hdf5 PATH]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path("/home/callensxavier_gmail_com")
WELL_REV = "2ee7756575ff6f90981d0308cbcb6a2ab5995bdc"
HDF5_SHA = "06cbd36c1dbea84e70906a363d20143b228765ee37850ec65351e247cf7df747"
DEFAULT_HDF5 = HOME / "hf-data/sigma3_enstrophy/data/test/turbulent_radiative_layer_tcool_0.32.hdf5"
DEFAULT_CRATE = HOME / "rusty-SUNDIALS-wt-tb2ch5/crates/qf-shell-cascade"
FIG = Path(__file__).resolve().parent.parent / "figures" / "ch5_U4_shell.pdf"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out", type=Path)
    ap.add_argument("--bin", type=Path, default=HOME / "rusty-target-ar" / "release")
    ap.add_argument("--crate", type=Path, default=DEFAULT_CRATE)
    ap.add_argument("--hdf5", type=Path, default=DEFAULT_HDF5)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    amps = a.out / "well_amps.txt"
    shutil.copy(a.crate / "results/sigma3/well_amps.txt", amps)
    hdf5_ok = sha256(a.hdf5) == HDF5_SHA if a.hdf5.is_file() else None
    study = a.out / "sigma3_study.json"
    subprocess.run([str(a.bin / "sigma3_study"), "full", str(study), str(amps), "textbook-ch5-rerun"], check=True,
                   capture_output=True)
    d = json.loads(study.read_text())
    s3 = [r for r in d["S3_sigma3_sweep"]] + [r for r in d["C2_sigma2_vs_sigma3"] if r["sigma"] == 3.0]
    w = d["W_well_data"]
    c2 = [r for r in d["C2_sigma2_vs_sigma3"] if r["sigma"] == 2.0]
    p1 = [(r["n_max"], r["rtol"], r["max_rel_dS"], r["max_rel_dH"]) for r in d["P1_positive_convergence"]]
    n1 = [(r["n_max"], r["rtol"], r["max_rel_dS"], r["max_rel_dH"]) for r in d["N1_negative_perturbed"]]
    res = {"dataset": {"repo": "polymathic-ai/turbulent_radiative_layer_2D", "revision": WELL_REV,
                       "file": "data/test/turbulent_radiative_layer_tcool_0.32.hdf5", "sha256_ok": hdf5_ok,
                       "license": "CC-BY-4.0"},
           "D": d["D"], "total_wall_s": d["total_wall_s"],
           "sigma3_max_ratio": max(r["sup_ratio"] for r in s3), "sigma3_n_runs": len(s3),
           "well_n_runs": len(w), "well_max_ratio": max(r["sup_ratio"] for r in w),
           "well_max_dS": max(r["max_rel_dS"] for r in w), "well_max_dH": max(r["max_rel_dH"] for r in w),
           "sigma2_ratio_by_nmax": {r["n_max"]: r["sup_ratio"] for r in c2},
           "sigma3_top_ratio_by_nmax": {r["n_max"]: r["sup_ratio"] for r in d["C2_sigma2_vs_sigma3"]
                                        if r["sigma"] == 3.0},
           "P1_positive": p1, "N1_negative": n1}
    ok = (res["sigma3_max_ratio"] <= 1.0 and res["well_max_ratio"] <= 1.0
          and max(res["sigma2_ratio_by_nmax"].values()) > 1.0
          and min(x[3] for x in n1) > 100 * max(x[3] for x in p1 if x[1] == 1e-10))
    res["all_checks_pass"] = ok
    figure(amps, d)
    (a.out / "ch5_U4_result.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
    if not ok:
        sys.exit(1)


def figure(amps: Path, d: dict) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = [list(map(float, l.split())) for l in amps.read_text().splitlines() if l.strip() and not l.startswith("#")]
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.5))
    cols = ["#2a78d6", "#eb6834", "#1baf7a", "#6250d6"]
    for k, r in enumerate(rows):
        e = [x * x for x in r[1:]]
        s = sum(e)
        ax[0].semilogy(range(len(e)), [v / s for v in e], "o-", color=cols[k], ms=5, lw=1.5, label=f"t = {int(r[0])}")
    ax[0].set_xlabel("couche n  ($k_x \\in [2^n, 2^{n+1})$)")
    ax[0].set_ylabel(r"$|v_n|^2 / S$")
    ax[0].set_title("(a) spectres dyadiques, The Well", fontsize=9)
    ax[0].legend(frameon=False, fontsize=8)
    c2 = d["C2_sigma2_vs_sigma3"]
    for sig, colr, mk in ((2.0, "#eb6834", "s"), (3.0, "#2a78d6", "o")):
        pts = [(r["n_max"], r["sup_ratio"]) for r in c2 if r["sigma"] == sig]
        ax[1].semilogy([p[0] for p in pts], [p[1] for p in pts], mk + "-", color=colr, ms=6, lw=1.5,
                       label=rf"$\sigma={sig:g}$")
    ax[1].axhline(1.0, color="#52514e", lw=1, ls="--")
    ax[1].text(2, 1.3, "borne de Lean (rapport = 1)", fontsize=8, color="#52514e")
    ax[1].set_xlabel(r"troncature $n_{\max}$")
    ax[1].set_ylabel(r"$\sup_t 2D\Omega / (H_3(0)+S^{3/2})$")
    ax[1].set_title("(b) témoin négatif : $\\sigma=2$ croît", fontsize=9)
    ax[1].legend(frameon=False, fontsize=8)
    run = max(d["W_well_data"], key=lambda r: r["sup_ratio"])
    tr = run["trace_t_S_H_Omega"]
    ax[2].plot([x[0] for x in tr], [2 * d["D"] * x[3] / run["bound_rhs"] for x in tr], "-", color="#2a78d6", lw=2)
    ax[2].axhline(1.0, color="#52514e", lw=1, ls="--")
    ax[2].set_ylim(0, 1.1)
    ax[2].set_xlabel("t")
    ax[2].set_ylabel(r"$2D\Omega(t) / (H_3(0)+S^{3/2})$")
    ax[2].set_title(f"(c) trajectoire {run['label']}, $n_{{\\max}}$={run['n_max']}", fontsize=9)
    for x in ax:
        x.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG)


if __name__ == "__main__":
    main()
