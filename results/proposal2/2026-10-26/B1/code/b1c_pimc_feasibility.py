"""B1c PIMC feasibility: finite-size error of the energy differences a periodic N = M x M PIMC cell would see.

usage: python -I b1c_pimc_feasibility.py OUT.json

A PIMC cell of M x M primitive cells samples exactly the Gamma-centred M x M k-grid. The harmonic E_zp on that grid
(Gamma excluded: zero modes, i.e. the centre-of-mass mode, carry no zero-point energy) differs from the
thermodynamic limit; we compare that finite-size shift of dE_zp = E_zp(competitor) - E_zp(rho) with the
thermodynamic-limit dE_zp and with the total energy gap at hbar_eff near the harmonic Lam_1. Also the
thermal-shape-fluctuation criterion: a shape free energy difference N |dE| must exceed k_B T by a wide margin, and
k_B T must be below the lowest phonon of the cell for a ground-state estimate.
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import b1_lib as L  # noqa: E402


def ezp_grid(a: float, x: float, y: float, M: int) -> tuple[float, float]:
    pg = L.PoissonGauss(a, x, y)
    idx = np.arange(M) / M
    uu, vv = np.meshgrid(idx, idx, indexing="ij")
    uu = (uu + 0.5) % 1.0 - 0.5
    vv = (vv + 0.5) % 1.0 - 0.5
    K = pg.kappa(uu.ravel(), vv.ravel())
    D = pg.D(K)
    om = L.omega_sum(D)
    # lowest nonzero phonon frequency of the cell
    _, _, lo = L.invariants(D)
    k2 = (K**2).sum(1)
    wmin = float(np.sqrt(np.maximum(lo[k2 > 1e-20], 0)).min())
    return 0.5 * float(om.sum()) / (M * M), wmin


def main() -> None:
    out = sys.argv[1]
    res = []
    for a, comp, lam in ((1.0, (0.3, 0.96), 0.10), (1.0, (0.4201, 0.9075), 0.115), (0.5, (0.305, 0.955), 0.075)):
        x0, y0 = L.RHO
        dzp_inf = L.e_zp(a, *comp, 64) - L.e_zp(a, x0, y0, 64)
        des = L.e_static(a, *comp) - L.e_static(a, x0, y0)
        row = {"a": a, "competitor": comp, "lam": lam, "dEzp_inf": dzp_inf, "dEs": des, "dE_total_inf": des + lam * dzp_inf, "cells": []}
        for M in (6, 8, 10, 12, 16, 24):
            e1, w1 = ezp_grid(a, *comp, M)
            e0, w0 = ezp_grid(a, x0, y0, M)
            dz = e1 - e0
            row["cells"].append({"M": M, "N": M * M, "dEzp_M": dz, "finite_size_shift_of_dE_total": lam * (dz - dzp_inf), "dE_total_M": des + lam * dz,
                                 "lowest_phonon_hbar_omega_tri": lam * w0, "N_times_abs_dE_total_inf": M * M * abs(des + lam * dzp_inf)})
        res.append(row)
        print(json.dumps(row), flush=True)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
