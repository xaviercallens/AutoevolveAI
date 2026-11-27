"""B1c extension: SCHA beyond the harmonic stability edge, by continuation.

usage: python -I b1c_scha_extend.py OUT.json

The plain SCHA solve starts from the bare harmonic D and therefore rejects every harmonically unstable shape. Here
each shape is seeded with the converged D_eff of its neighbour (same reduced Duffy nodes), so shapes that are
SCHA-stable but harmonically unstable can be reached:
 * the arc |tau| = 1 from rho to i (angle step 0.01),
 * the line Re tau = 1/2 from rho up to y = 1.30 (step 0.01),
 * a strip x in [0.15, 0.30] (step 0.025), y from the arc up to 1.12 (step 0.02), each column seeded from the arc
   point with the same x and marched upward.
A point counts only if the SCHA iteration converged and min lam_lo(D_eff)/|k|^2 > 0 (stability_eff, 64^2 grid +
long-wave directions). Cases: a = 0.5, 1.0 at hbar_eff = harmonic Lam_1, harmonic hbar*, 0.2.
"""

import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import b1_lib as L  # noqa: E402

N_NODES = 32


def solve(a: float, x: float, y: float, lam: float, D0: np.ndarray | None) -> tuple[dict, np.ndarray | None]:
    s = L.SCHA(a, x, y, N=N_NODES)
    r = s.solve(lam, tol=1e-14, maxit=1500, D0=D0)
    ok = r["status"] == "converged"
    st = s.stability_eff() if ok else None
    D = r.pop("D")
    r["stab_eff"] = st
    r["good"] = bool(ok and st is not None and st > 0)
    return r, (D if r["good"] else None)


def march(a: float, lam: float, pts: list[tuple[float, float]], D0: np.ndarray, e0: float, kind: str) -> tuple[list[dict], dict]:
    out = []
    seeds = {}
    D = D0
    for (x, y) in pts:
        r, Dn = solve(a, x, y, lam, D)
        if Dn is None and D is not D0:
            r2, Dn2 = solve(a, x, y, lam, D0)  # retry from the triangular solution
            if Dn2 is not None:
                r, Dn = r2, Dn2
        out.append({"kind": kind, "x": x, "y": y, "dE": r["E"] - e0, "good": r["good"], "status": r["status"], "stab_eff": r["stab_eff"], "u2": r["u2"]})
        seeds[(round(x, 6), round(y, 6))] = Dn
        if Dn is not None:
            D = Dn
    return out, seeds


def main() -> None:
    out = sys.argv[1]
    B = os.path.dirname(out)
    curv = {round(r["a"], 6): r for r in json.load(open(os.path.join(B, "b1a_curvature.json")))["rows"]}
    res = []
    x0, y0 = L.RHO
    for a in (1.0, 0.5):
        sj = json.load(open(os.path.join(B, f"scan_a{a:g}.json")))
        for lam in (sj["Lam_1"]["ratio_N64"], curv[round(a, 6)]["hbar_star"], 0.2):
            t0 = time.time()
            r0, Drho = solve(a, x0, y0, lam, None)
            e0 = r0["E"]
            arc = [(math.cos(math.pi / 3 + t), math.sin(math.pi / 3 + t)) for t in np.arange(0.01, math.pi / 6 + 1e-9, 0.01)]
            arc.append((0.0, 1.0))
            line = [(0.5, y) for y in np.arange(y0 + 0.01, 1.3 + 1e-9, 0.01)]
            pa, seeds = march(a, lam, arc, Drho, e0, "arc")
            pl, _ = march(a, lam, line, Drho, e0, "line")
            strip = []
            for x in np.arange(0.15, 0.30 + 1e-9, 0.025):
                # seed: arc point with nearest x
                best = min(seeds.items(), key=lambda kv: abs(kv[0][0] - x))
                Dseed = best[1] if best[1] is not None else Drho
                ys = [y for y in np.arange(math.sqrt(1 - x * x) + 0.005, 1.12 + 1e-9, 0.02)]
                ps, _ = march(a, lam, [(float(x), float(y)) for y in ys], Dseed, e0, "strip")
                strip += ps
            pts = pa + pl + strip
            good = [p for p in pts if p["good"]]
            hstab = {}
            for p in good:
                hstab[(p["x"], p["y"])] = L.quick_stable(a, p["x"], p["y"])[0]
            beyond = [p for p in good if not hstab[(p["x"], p["y"])]]
            low = min(good, key=lambda p: p["dE"]) if good else None
            row = {"a": a, "lam": lam, "gamma_rho": math.sqrt(r0["u2"]) / L.A_NN, "n_points": len(pts), "n_scha_stable": len(good),
                   "n_scha_stable_but_harmonically_unstable": len(beyond),
                   "min_dE": None if low is None else {k: low[k] for k in ("kind", "x", "y", "dE", "stab_eff")},
                   "min_dE_beyond_harmonic_edge": None if not beyond else {k: min(beyond, key=lambda p: p["dE"])[k] for k in ("kind", "x", "y", "dE", "stab_eff")},
                   "n_below_triangular": sum(1 for p in good if p["dE"] < 0), "points": pts, "seconds": round(time.time() - t0, 1)}
            res.append(row)
            print(json.dumps({k: v for k, v in row.items() if k != "points"}), flush=True)
            json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
