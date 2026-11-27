"""SCHA quick checks: stability_eff at Lam -> 0 equals the harmonic screen; timing; convergence status vs Lam at rho."""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b1_lib as L  # noqa: E402
import b1c_scha as C  # noqa: E402

x0, y0 = L.RHO
for (x, y) in ((x0, y0), (0.3, 0.96), (0.0, 1.0)):
    s = L.SCHA(1.0, x, y, N=32)
    r = s.solve(1e-6)
    print("ctl stab", x, y, s.stability_eff(n=48), L.quick_stable(1.0, x, y), r["status"])
for lam in (0.1, 0.2, 0.4, 0.8, 1.6):
    t = time.time()
    e, r = C.e_scha(1.0, x0, y0, lam)
    print(lam, e, r["status"], r["iters"], r["stab_eff"], r["u2"], round(time.time() - t, 2))
