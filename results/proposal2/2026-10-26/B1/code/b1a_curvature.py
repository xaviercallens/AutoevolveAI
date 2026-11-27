"""B1a part 1: static and zero-point curvatures at rho and the harmonic spinodal hbar*(a) = -c_static / c_zp.

usage: python -I b1a_curvature.py OUT.json

c = Lap F / 4 (Lap = y^2 (d_xx + d_yy)), F(tau) - F(rho) = c |tau - rho|^2 / y_rho^2 + O(r^3) (isotropic by the
order-3 stabiliser of rho, P2 PROOF.md 3.1). c_static from the exact pair sum of h(u) = (u^2 f')'; c_zp from a
Richardson-combined five-point stencil (h = 2e-3, 1e-3) on Duffy N = 48 E_zp (converged to ~1e-15, see t_smoke.py).
Control: the stencil applied to E_static must reproduce the exact c_static.
Negative controls: a = 0.30 and a = 2.0 (outside (a1, a2) = (0.37668, 1.58148)) must give c_zp > 0, i.e. no hbar*.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b1_lib as L  # noqa: E402

A_LIST = [0.30, 0.378, 0.38, 0.39, 0.40, 0.42, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00, 1.05,
          1.10, 1.15, 1.20, 1.25, 1.30, 1.35, 1.40, 1.45, 1.50, 1.55, 1.57, 1.58, 2.00]


def main() -> None:
    out = sys.argv[1]
    x0, y0 = L.RHO
    rows = []
    for a in A_LIST:
        t0 = time.time()
        lap_s = L.lap_static_exact(a)
        st = L.lap_stencil(lambda x, y: L.e_static(a, x, y), x0, y0)
        zp = L.lap_stencil(lambda x, y: L.e_zp(a, x, y, 48), x0, y0)
        zp64 = L.lap_stencil(lambda x, y: L.e_zp(a, x, y, 64), x0, y0)
        c_s = lap_s / 4
        c_z = zp["lap"] / 4
        row = {
            "a": a,
            "rho_sigma2": 1 / (3.141592653589793 * a),
            "c_static": c_s,
            "c_static_stencil": st["lap"] / 4,
            "c_static_stencil_relerr": abs(st["lap"] / 4 - c_s) / abs(c_s),
            "c_zp": c_z,
            "c_zp_N64": zp64["lap"] / 4,
            "c_zp_stencil_h_spread": abs(zp["lap_fine"] - zp["lap_coarse"]) / 4,
            "isotropy_fxx_minus_fyy_rel": abs(zp["fxx"] - zp["fyy"]) / abs(zp["fxx"]),
            "E_static_rho": L.e_static(a, x0, y0),
            "E_zp_rho": L.e_zp(a, x0, y0, 64),
            "u2_per_lam_rho": L.u2_harmonic_per_lam(a, x0, y0, 64),
            "u2_per_lam_rho_N96": L.u2_harmonic_per_lam(a, x0, y0, 96),
            "hbar_star": (-c_s / c_z) if c_z < 0 else None,
            "seconds": round(time.time() - t0, 2),
        }
        rows.append(row)
        print(json.dumps(row), flush=True)
    json.dump({"rows": rows, "note": "c = Lap/4 at rho; hbar_star = -c_static/c_zp when c_zp < 0 (harmonic spinodal)"}, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
