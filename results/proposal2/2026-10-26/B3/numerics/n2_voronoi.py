"""N2: Voronoi combinatorics of 3D configurations, with energies.

Checks, per configuration: mean faces per cell f, mean sum_F (6 - n_F) (Euler weight; = 12 exactly for a
simple polytope, > 12 for a non-simple one), separation, normalized second moment G about the site,
and jellium energy per particle (unit density).
Positive controls: bcc truncated octahedron f = 14, Euler weight 12; A15 (Weaire-Phelan) f = 13.5;
C15 f = 13.333; sum of cell volumes = N.
Negative control: exact fcc (rhombic dodecahedron, non-simple) must give Euler weight 24, not 12.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ewald3d as ew  # noqa: E402

OUT = Path(__file__).resolve().parent / "n2_voronoi.json"


def separation(st: ew.Structure) -> float:
    X = st.cart()
    L = ew._images(st.A, 3.0)
    best = np.inf
    for i in range(st.n):
        d = np.linalg.norm(X[i] - X[:, None, :] - L[None, :, :], axis=2)
        d = d[d > 1e-12]
        best = min(best, float(d.min()))
    return best


def analyse(st: ew.Structure, energy: bool = True) -> dict[str, float]:
    cells = ew.voronoi_cells(st)
    stats = [ew.cell_stats(c) for c in cells]
    f = np.array([s["faces"] for s in stats], dtype=float)
    ew_ = np.array([s["euler_weight"] for s in stats], dtype=float)
    vol = np.array([s["volume"] for s in stats])
    m2 = np.array([s["second_moment_site"] for s in stats])
    out = {
        "N": st.n,
        "mean_faces": float(f.mean()),
        "min_faces": float(f.min()),
        "max_faces": float(f.max()),
        "mean_euler_weight": float(ew_.mean()),
        "max_euler_weight": float(ew_.max()),
        "sum_volume_over_N": float(vol.sum() / st.n),
        # G = (1/3) int |x - site|^2 / V^(5/3), averaged with the quantizer convention sum m2 / (3 N Vbar^(5/3))
        "G_site": float(m2.sum() / (3.0 * st.n * (vol.mean()) ** (5.0 / 3.0))),
        "max_centroid_offset": float(max(s["centroid_offset"] for s in stats)),
        "separation": separation(st),
    }
    if energy:
        out["e_per_particle"] = ew.ewald_energy_per_particle(st, alpha=None)
    return out


def main() -> None:
    res: dict[str, dict[str, float]] = {}
    base = {"bcc": ew.bcc(), "fcc": ew.fcc(), "hcp": ew.hcp(), "sc": ew.sc(), "A15": ew.a15(), "C15": ew.c15()}
    for k, st in base.items():
        res[k] = analyse(st)
        print(k, res[k], flush=True)
    sup = {
        "bcc": ew.supercell(ew.bcc(), (4, 4, 4)),
        "fcc": ew.supercell(ew.fcc(), (4, 4, 4)),
        "hcp": ew.supercell(ew.hcp(), (4, 4, 3)),
    }
    for k, st in sup.items():
        for amp in (0.002, 0.01, 0.03, 0.06):
            for seed in (1, 2):
                p = ew.perturbed(st, amp, seed)
                key = f"{k}_pert_amp{amp}_seed{seed}"
                res[key] = analyse(p)
                print(key, res[key], flush=True)
    for seed in (1, 2):
        p = ew.poisson(400, seed)
        key = f"poisson400_seed{seed}"
        res[key] = analyse(p, energy=True)
        print(key, res[key], flush=True)
    OUT.write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
