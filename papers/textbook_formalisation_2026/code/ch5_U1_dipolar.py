"""Chapter 5, use case U1: dipolar excitons in a TMD heterobilayer.

Steps:
  1. Hugging Face colabfit/JARVIS_DFT_3D_12_12_2022 (pinned revision), shard co/co_0.parquet: check the sha256, extract
     the semiconducting MoSe2 and WSe2 stacks and their adjacent metal-plane spacings (selection rule of the
     ar_dipolar_exciton paper, fixed before looking at the output). Proxy d = mean of the two homo-stack means.
  2. rusty-SUNDIALS qf-yukawa-crystal, binary dipolar_crystal: `refs` (exact Ewald energies at 5 values of
     d~ = d sqrt(n)) and `gaps` (41-point grid of square and honeycomb gaps relative to triangular).
  3. Positive control: an independent Python direct sum of U = 2/(r s (r+s)), s = sqrt(r^2+d~^2), over the
     triangular lattice of density one, plus the exact uniform tail 2 pi/(sqrt(R^2+d~^2)+R), agrees with the Rust
     Ewald value. Negative controls: the same sum without the tail is off by about 1e-2; the wrong-sign potential
     h_d(t) = t^-1/2 - 2 (t+d^2)^-1/2 is negative at t = d^2 (so it is not completely monotone).
  4. Physical numbers: d~ at n = 1e11, 1e12, 3e12 cm^-2 and the unscreened square-minus-triangular gap in meV
     (divide by eps_r), interpolated on the Rust grid.
  5. Figure figures/ch5_U1_dipolar.pdf and a JSON summary.

Usage: python -I ch5_U1_dipolar.py OUT_DIR [--bin DIR] [--parquet PATH]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
import urllib.request
from pathlib import Path

import numpy as np

HOME = Path("/home/callensxavier_gmail_com")
REPO = "colabfit/JARVIS_DFT_3D_12_12_2022"
REV = "f4de0085edcf92885870c67459363d2c7080c90b"
SHARD = "co/co_0.parquet"
SHARD_SHA = "9f6c21a2a3eda4316eee1f2be7dddc276eeb5f905de87dcce70f20e36132510b"
DEFAULT_PARQUET = HOME / "hf-data/dipolar_exciton/colabfit__JARVIS_DFT_3D_12_12_2022/co/co_0.parquet"
FIG = Path(__file__).resolve().parent.parent / "figures" / "ch5_U1_dipolar.pdf"
E2_EV_A = 14.399645  # e^2/(4 pi eps0) in eV * Angstrom (CODATA)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def get_parquet(path: Path) -> Path:
    if not path.is_file():
        path = HOME / "hf-data/textbook2/jarvis_dft_3d" / SHARD
        if not path.is_file():
            path.parent.mkdir(parents=True, exist_ok=True)
            url = f"https://huggingface.co/datasets/{REPO}/resolve/{REV}/{SHARD}"
            path.write_bytes(urllib.request.urlopen(url, timeout=600).read())
    if sha256(path) != SHARD_SHA:
        raise SystemExit(f"sha256 mismatch: {path}")
    return path


def metal_spacings(cell: np.ndarray, pos: np.ndarray, nums: np.ndarray) -> list[float]:
    """Adjacent metal-plane spacings along the stacking axis (the cell vector most normal to the other two)."""
    best = None
    for k in range(3):
        i, j = [q for q in range(3) if q != k]
        nrm = np.cross(cell[i], cell[j])
        nrm /= np.linalg.norm(nrm)
        comp = abs(cell[k] @ nrm)
        score = comp / (0.5 * (np.linalg.norm(cell[i]) + np.linalg.norm(cell[j])))
        if best is None or score > best[0]:
            best = (score, nrm, comp)
    _, nrm, period = best
    zm = np.sort((pos @ nrm)[nums >= 42] % period)
    return np.diff(np.concatenate([zm, [zm[0] + period]])).tolist()


def jarvis_d(parquet: Path) -> dict:
    import pyarrow.parquet as pq

    target = {(42, 34): "MoSe2", (74, 34): "WSe2"}
    seen: set[str] = set()
    out: dict[str, list[float]] = {"MoSe2": [], "WSe2": []}
    rows: dict[str, list[str]] = {"MoSe2": [], "WSe2": []}
    pf = pq.ParquetFile(parquet)
    for batch in pf.iter_batches(batch_size=4096, columns=["atomic_numbers", "cell", "positions",
                                                           "electronic_band_gap", "names"]):
        tab = batch.to_pydict()
        for r in range(len(tab["atomic_numbers"])):
            nums = np.asarray(tab["atomic_numbers"][r])
            s = set(nums.tolist())
            if len(s) != 2:
                continue
            m = [z for z in s if z in (42, 74)]
            x = [z for z in s if z == 34]
            if len(m) != 1 or len(x) != 1 or (nums == 34).sum() != 2 * (nums == m[0]).sum():
                continue
            name = target[(m[0], 34)]
            key = json.dumps(tab["names"][r], sort_keys=True)
            if key in seen or not (tab["electronic_band_gap"][r] or 0) > 0:
                continue
            seen.add(key)
            sp = metal_spacings(np.asarray(tab["cell"][r], float).reshape(3, 3),
                                np.asarray(tab["positions"][r], float).reshape(-1, 3), nums)
            vdw = [v for v in sp if 4.5 < v < 8.0]
            if (nums >= 42).sum() < 2 or not vdw or any(v < 4.5 for v in sp):
                continue
            out[name] += vdw
            rows[name].append(str(tab["names"][r][-1]))
    res = {k: {"n_spacings": len(v), "mean_A": float(np.mean(v)), "min_A": float(min(v)), "max_A": float(max(v)),
               "rows": rows[k]} for k, v in out.items()}
    res["proxy_d_A"] = 0.5 * (res["MoSe2"]["mean_A"] + res["WSe2"]["mean_A"])
    return res


def u_pot(r: np.ndarray, dt: float) -> np.ndarray:
    s = np.sqrt(r * r + dt * dt)
    return 2.0 / (r * s * (r + s))


def direct_sum(dt: float, big_r: float) -> tuple[float, float]:
    """Half lattice sum of U over the density-one triangular lattice within radius R, and the exact uniform tail."""
    a = math.sqrt(2.0 / math.sqrt(3.0))
    m = int(big_r / a * 1.2) + 2
    i, j = np.meshgrid(np.arange(-m, m + 1), np.arange(-m, m + 1), indexing="ij")
    x = a * (i + 0.5 * j)
    y = a * (math.sqrt(3.0) / 2.0) * j
    r = np.hypot(x, y).ravel()
    r = r[(r > 0) & (r < big_r)]
    part = 0.5 * float(np.sort(u_pot(r, dt)).sum())
    tail = 2.0 * math.pi / (math.sqrt(big_r * big_r + dt * dt) + big_r)
    return part, tail


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out", type=Path)
    ap.add_argument("--bin", type=Path, default=HOME / "rusty-target-ar" / "release")
    ap.add_argument("--parquet", type=Path, default=DEFAULT_PARQUET)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    pq_path = get_parquet(a.parquet)
    jd = jarvis_d(pq_path)
    for cmd in ("refs", "gaps"):
        p = subprocess.run([str(a.bin / "dipolar_crystal"), cmd, str(a.out)], capture_output=True, text=True)
        if p.returncode != 0:
            raise SystemExit(f"dipolar_crystal {cmd} failed: {p.stderr}")
    res_dir = a.out / "results" / "dipolar"
    refs = [json.loads(x) for x in (res_dir / "references.jsonl").read_text().splitlines() if x.strip()]
    grid = [json.loads(x) for x in (res_dir / "lattice_gaps.jsonl").read_text().splitlines() if x.strip()]
    # controls
    controls = []
    for ref in refs:
        if ref["d"] not in (0.066, 1.0):
            continue
        for big_r in (50.0, 100.0, 200.0):
            part, tail = direct_sum(ref["d"], big_r)
            controls.append({"d": ref["d"], "R": big_r, "rust_ewald": ref["e_tri_exact"],
                             "rel_err_with_tail": abs(part + tail - ref["e_tri_exact"]) / ref["e_tri_exact"],
                             "rel_err_without_tail": abs(part - ref["e_tri_exact"]) / ref["e_tri_exact"]})
    eta_spread = max(abs(r["e_tri_exact_eta0.6"] - r["e_tri_exact"]) / r["e_tri_exact"] for r in refs)
    h_at = {d: 1.0 / d - 2.0 / math.sqrt(2.0 * d * d) for d in (0.5, 1.0, 2.0)}  # h_d(t = d^2) < 0
    # physical window
    lg_d = np.log([g["d"] for g in grid])
    phys = {}
    for n in (1e11, 1e12, 3e12):
        dt = jd["proxy_d_A"] * 1e-8 * math.sqrt(n)
        gap_u = float(np.interp(math.log(dt), lg_d, [g["square_minus_tri"] for g in grid]))
        mev = gap_u * dt * dt * E2_EV_A * math.sqrt(n) * 1e-8 * 1e3  # V = dt^2 U, energy unit e^2/(4 pi eps0) sqrt(n)
        phys[f"{n:.0e}"] = {"d_tilde": dt, "gap_U": gap_u, "gap_meV_unscreened": mev}
    ok = (all(c["rel_err_with_tail"] < 1e-4 for c in controls if c["R"] >= 100)
          and all(c["rel_err_without_tail"] > 1e-3 for c in controls)
          and all(v < 0 for v in h_at.values())
          and all(g["rel_gap_square"] > 0 and g["rel_gap_honeycomb"] > 0 for g in grid))
    figure(grid, phys, controls)
    result = {"dataset": {"repo": REPO, "revision": REV, "file": SHARD, "sha256": SHARD_SHA, "license_on_card": "unknown"},
              "jarvis": jd, "refs": [{k: r[k] for k in ("d", "e_tri_exact", "e_square_exact", "e_honeycomb_exact",
                                                         "square_minus_tri_exact")} for r in refs],
              "grid_rel_gap_square_range": [grid[0]["rel_gap_square"], grid[-1]["rel_gap_square"]],
              "grid_rel_gap_honeycomb_range": [grid[0]["rel_gap_honeycomb"], grid[-1]["rel_gap_honeycomb"]],
              "eta_spread": eta_spread, "controls_direct_sum": controls, "h_d_at_t_eq_d2": h_at,
              "physical": phys, "all_controls_pass": ok}
    (a.out / "ch5_U1_result.json").write_text(json.dumps(result, indent=1))
    print(json.dumps({k: result[k] for k in ("jarvis", "physical", "grid_rel_gap_square_range",
                                             "grid_rel_gap_honeycomb_range", "eta_spread", "all_controls_pass")},
                     indent=1))
    print(json.dumps(controls, indent=1))
    if not ok:
        sys.exit(1)


def figure(grid: list[dict], phys: dict, controls: list[dict]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
    d = [g["d"] for g in grid]
    ax[0].loglog(d, [g["rel_gap_square"] for g in grid], "-", color="#2a78d6", lw=2, label="carré")
    ax[0].loglog(d, [g["rel_gap_honeycomb"] for g in grid], "-", color="#eb6834", lw=2, label="nid d'abeilles")
    lo, hi = phys["1e+11"]["d_tilde"], phys["3e+12"]["d_tilde"]
    ax[0].axvspan(lo, hi, color="#d9d8d4", alpha=0.6, lw=0)
    ax[0].text(lo * 1.05, 2e-3, "fenêtre\nexpérimentale", fontsize=8, color="#52514e")
    ax[0].set_xlabel(r"$\tilde d = d\sqrt{n}$")
    ax[0].set_ylabel(r"$e_{\rm reseau}/e_{\rm tri}-1$")
    ax[0].set_title("(a) écart relatif au réseau triangulaire (Ewald, Rust)", fontsize=9)
    ax[0].legend(frameon=False, fontsize=8)
    for dv, colr in ((0.066, "#2a78d6"), (1.0, "#1baf7a")):
        cs = [c for c in controls if c["d"] == dv]
        rs = [c["R"] for c in cs]
        ax[1].loglog(rs, [c["rel_err_with_tail"] for c in cs], "o-", color=colr, ms=6, lw=1.5,
                     label=rf"avec queue, $\tilde d$={dv}")
        ax[1].loglog(rs, [c["rel_err_without_tail"] for c in cs], "s--", color=colr, ms=6, lw=1.5,
                     label=rf"sans queue (témoin négatif), $\tilde d$={dv}")
    ax[1].set_xlabel("rayon de coupure R")
    ax[1].set_ylabel("écart relatif à Ewald (Rust)")
    ax[1].set_title("(b) témoins : somme directe Python", fontsize=9)
    ax[1].set_ylim(1e-7, 10)
    ax[1].legend(frameon=False, fontsize=7, loc="upper right")
    for x in ax:
        x.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG)


if __name__ == "__main__":
    main()
