"""Chapter 5, use case U2: planar Yukawa crystals (dusty plasmas, colloids), V(r) = exp(-kappa r)/r.

Steps:
  1. Provenance of the disordered initial conditions: Hugging Face colabfit/OC20_IS2RES_val_id (CC-BY-4.0), shard
     co/co_10.parquet. If the shard is on disk, its sha256 is checked against the Hub LFS hash at revision
     6a1dfef1... and the OC20 configuration ids listed in provenance.json are looked up in it.
     No dusty-plasma or colloid dataset exists on the Hub (absence by search, 2026-10-25): OC20 supplies disorder only.
  2. rusty-SUNDIALS qf-yukawa-crystal, binary yukawa_crystal:
       exact-refs            exact lattice energies (rigorous tail bound), Ewald cross-check, shifted-force values;
       exact-relax 2 1 0 0   kappa = 2: CVODE (BDF) relaxation of one OC20 start, one uniform random start, and one
                             incommensurate 17x17 box (negative control), under the exact image-summed potential.
  3. Positive control: an independent Python direct lattice sum agrees with the Rust value.
     Negative controls: the shifted-force (r_c = 8) energies miss the exact value by far more than 1e-9; the
     incommensurate box, which cannot hold the triangular lattice, stays above it.
  4. Figure figures/ch5_U2_yukawa.pdf and a JSON summary.

Usage: python -I ch5_U2_yukawa.py OUT_DIR [--bin DIR] [--crate DIR] [--shard PATH] [--skip-relax]
--crate is a qf-yukawa-crystal crate directory (for data/initial/*.csv); its files are copied, never written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

HOME = Path("/home/callensxavier_gmail_com")
SHARD_SHA = "9e4249ba20cf4cdc46f69e7fe6deb19be286dd19c9f1cf85d350816d2b1e748b"
OC_REV = "6a1dfef12aec878b4cda99edd54b16a6a254e135"
DEFAULT_SHARD = Path("/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/hf_datasets/oc20_is2res_val_id/co_10.parquet")
DEFAULT_CRATE = HOME / "rusty-SUNDIALS-wt-tb2ch5/crates/qf-yukawa-crystal"
FIG = Path(__file__).resolve().parent.parent / "figures" / "ch5_U2_yukawa.pdf"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def provenance(crate: Path, shard: Path) -> dict:
    prov = json.loads((crate / "data/initial/provenance.json").read_text())
    item = next(x for x in prov["items"] if x["file"] == "oc20_tri_box_00.csv")
    out = {"dataset": prov["dataset"], "license": prov["license"], "doi": prov["doi"], "shard": prov["shard"],
           "revision": OC_REV, "seed": item["seed"], "structures_used": item["structures_used"]}
    if shard.is_file():
        out["shard_sha256_ok"] = sha256(shard) == SHARD_SHA
        import pyarrow.parquet as pq

        ids = set(pq.read_table(shard, columns=["configuration_id"]).column(0).to_pylist())
        want = [s["configuration_id"] for s in item["first_structures"]]
        out["configuration_ids_found"] = sum(w in ids for w in want)
        out["configuration_ids_listed"] = len(want)
    else:
        out["shard_sha256_ok"] = None
    return out


def direct_lattice(kappa: float, basis: list[list[float]], big_r: float) -> float:
    m = int(big_r / 0.9) + 2
    i, j = np.meshgrid(np.arange(-m, m + 1), np.arange(-m, m + 1), indexing="ij")
    x = i * basis[0][0] + j * basis[1][0]
    y = i * basis[0][1] + j * basis[1][1]
    r = np.hypot(x, y).ravel()
    r = r[(r > 0) & (r < big_r)]
    return 0.5 * float(np.sort(np.exp(-kappa * r) / r).sum())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out", type=Path)
    ap.add_argument("--bin", type=Path, default=HOME / "rusty-target-ar" / "release")
    ap.add_argument("--crate", type=Path, default=DEFAULT_CRATE)
    ap.add_argument("--shard", type=Path, default=DEFAULT_SHARD)
    ap.add_argument("--skip-relax", action="store_true", help="read the relaxation record instead of re-running it")
    a = ap.parse_args()
    work = a.out / "crate"
    (work / "data/initial").mkdir(parents=True, exist_ok=True)
    for f in ("oc20_tri_box_00.csv", "oc20_square_box_00.csv", "provenance.json"):
        shutil.copy(a.crate / "data/initial" / f, work / "data/initial" / f)
    prov = provenance(a.crate, a.shard)
    env = dict(os.environ, YUKAWA_THREADS="2")
    subprocess.run([str(a.bin / "yukawa_crystal"), "exact-refs", str(work)], check=True, env=env,
                   capture_output=True)
    if a.skip_relax:
        shutil.copy(a.crate / "results/exact/exact_relax_kappa2_a0_f0.jsonl",
                    work / "results/exact/exact_relax_kappa2_a0_f0.jsonl")
    else:
        subprocess.run([str(a.bin / "yukawa_crystal"), "exact-relax", str(work), "2", "1", "0", "0"], check=True,
                       env=env, capture_output=True)
    refs = [json.loads(x) for x in (work / "results/exact/exact_refs.jsonl").read_text().splitlines() if x.strip()]
    lat = {r["kappa"]: r for r in refs if r["kind"] == "lattice"}
    relax = [json.loads(x) for x in
             (work / "results/exact/exact_relax_kappa2_a0_f0.jsonl").read_text().splitlines() if x.strip()]
    s3 = math.sqrt(3.0)
    a_sp = math.sqrt(2.0 / s3)
    tri = [[a_sp, 0.0], [0.5 * a_sp, 0.5 * s3 * a_sp]]
    sq = [[1.0, 0.0], [0.0, 1.0]]
    pos = {}
    for kappa, big_r in ((1.0, 40.0), (2.0, 20.0)):
        for name, basis in (("tri", tri), ("square", sq)):
            py = direct_lattice(kappa, basis, big_r)
            rust = lat[kappa][name]["exact_partial"]
            pos[f"k{kappa:g}_{name}"] = {"python": py, "rust": rust, "rel_diff": abs(py - rust) / rust,
                                         "shifted_force_minus_exact": lat[kappa][name]["shifted_force_rc8"] - rust}
    rows = []
    for r in relax:
        q = r["quench"]
        rows.append({"label": r["label"], "family": r["family"], "n": r["n"], "exact_gap": q["exact_gap"],
                     "exact_rel_gap": q["exact_rel_gap"], "defects": q["exact_defects"],
                     "hess_negative": q["hess_negative"], "converged": q["converged"], "cvode_steps": q["cvode_steps"]})
    ok = (all(v["rel_diff"] < 1e-12 for v in pos.values())
          and all(abs(v["shifted_force_minus_exact"]) > 1e-9 for v in pos.values())
          and all(x["exact_gap"] > 0 and x["converged"] and x["hess_negative"] == 0 for x in rows))
    figure(work, rows, lat[2.0]["gap_exact"])
    result = {"provenance": prov, "lattice": {k: {"tri": v["tri"]["exact_partial"], "square": v["square"]["exact_partial"],
                                                  "gap_exact": v["gap_exact"], "gap_sf_rc8": v["gap_sf_rc8"],
                                                  "tail_bound_tri": v["tri"]["tail_bound"]} for k, v in lat.items()},
              "positive_control_python": pos, "relax_kappa2": rows, "all_controls_pass": ok}
    (a.out / "ch5_U2_result.json").write_text(json.dumps(result, indent=1))
    print(json.dumps(result, indent=1))
    if not ok:
        sys.exit(1)


def figure(work: Path, rows: list[dict], sq_gap: float) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    xy = np.loadtxt(work / "data/initial/oc20_tri_box_00.csv", delimiter=",")
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8), gridspec_kw={"width_ratios": [1.1, 1]})
    ax[0].plot(xy[:, 0], xy[:, 1], "o", ms=3, color="#2a78d6")
    ax[0].set_aspect("equal")
    ax[0].set_title("(a) condition initiale OC20 projetée (288 particules)", fontsize=9)
    ax[0].set_xlabel("x")
    ax[0].set_ylabel("y")
    names = {"hf_oc20": "départ OC20", "uniform": "départ uniforme", "ctl_neg_incommensurate_box": "boite 17x17\n(témoin nég.)"}
    labels = [names[r["family"]] for r in rows] + ["réseau carré"]
    vals = [r["exact_gap"] for r in rows] + [sq_gap]
    cols = ["#2a78d6", "#1baf7a", "#eb6834", "#52514e"]
    ax[1].barh(range(len(vals)), vals, color=cols, height=0.55)
    ax[1].set_xscale("log")
    ax[1].set_yticks(range(len(vals)), labels, fontsize=8)
    for k, v in enumerate(vals):
        ax[1].text(v * 1.08, k, f"{v:.2e}", va="center", fontsize=8, color="#52514e")
    ax[1].set_xlabel(r"$e - e_{\rm tri}$ (potentiel exact, $\kappa=2$)")
    ax[1].set_title("(b) états relaxés par CVODE, tous au-dessus du triangulaire", fontsize=9)
    ax[1].set_xlim(1e-4, 3e-2)
    for x in ax:
        x.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG)


if __name__ == "__main__":
    main()
