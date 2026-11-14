"""Control: d Lap E_SCHA(rho) / d hbar_eff at hbar_eff -> 0 must equal the harmonic slope 4 c_zp (a = 1: -3.848)."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b1_lib as L  # noqa: E402
import b1c_scha as C  # noqa: E402

out = {}
lap0 = L.lap_static_exact(1.0)
for lam in (0.0025, 0.005, 0.01):
    lp = C.lap_scha(1.0, lam)
    out[str(lam)] = {"lap_scha": lp, "lap_harmonic": lap0 + lam * (-3.847937409595658), "slope_from_0": (lp - lap0) / lam}
    print(lam, out[str(lam)], flush=True)
json.dump(out, open(sys.argv[1], "w"), indent=1)
