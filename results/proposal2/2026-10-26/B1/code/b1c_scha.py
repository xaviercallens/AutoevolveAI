"""B1c: self-consistent harmonic approximation (T = 0) for the Gaussian-core crystal.

usage: python -I b1c_scha.py OUT.json a1 [a2 ...]

For each a:
 1. Lap E_SCHA at rho as a function of Lam (Richardson stencil, each point converged to |dE| < 1e-13); Lam*_SCHA is the
    root of Lap E_SCHA(rho; Lam) = 0 (brentq), compared with the harmonic hbar*(a).
 2. E_SCHA(tau) - E_SCHA(rho) along the arc |tau| = 1 toward i and along Re tau = 1/2 upward, and at the harmonic
    edge competitor, for a ladder of Lam; first Lam (ladder resolution) at which a sampled shape with a stable SCHA
    D_eff lies below the triangular lattice = Lam_1,SCHA (bracketed, then bisected).
 3. Breakdown: largest Lam (bisection) at which the SCHA iteration still converges to a stable D_eff at rho.
 4. Lindemann ratio gamma = sqrt(<|u|^2>)/a_nn from D_eff at those Lam.
Controls: Lam -> 0 limit equals the harmonic energy (dE ~ Lam^2, t_scha.py); D_eff is a minimiser of the variational
energy (t_scha.py: scaling and interpolation toward bare D raise E).
"""

import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scipy.optimize import brentq  # noqa: E402

import b1_lib as L  # noqa: E402

N_NODES = 32


def e_scha(a: float, x: float, y: float, lam: float) -> tuple[float, dict]:
    s = L.SCHA(a, x, y, N=N_NODES)
    r = s.solve(lam, tol=1e-14, maxit=1500)
    r["stab_eff"] = s.stability_eff() if r["status"] == "converged" else None
    r.pop("D")
    return r["E"], r


def lap_scha(a: float, lam: float) -> float:
    x0, y0 = L.RHO

    def F(x: float, y: float) -> float:
        e, r = e_scha(a, x, y, lam)
        if r["status"] != "converged":
            raise RuntimeError(f"SCHA not converged a={a} lam={lam} tau=({x},{y}): {r['status']}")
        return e

    return L.lap_stencil(F, x0, y0)["lap"]


def path_points(kind: str) -> list[tuple[float, float]]:
    x0, y0 = L.RHO
    pts = []
    for t in (0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20, 0.22):
        if kind == "line_up":
            pts.append((0.5, y0 + t))
        else:
            ang = math.pi / 3 + t
            pts.append((math.cos(ang), math.sin(ang)))
    return pts


def main() -> None:
    out = sys.argv[1]
    res = {}
    if os.path.exists(out):
        res = json.load(open(out))
    for a in [float(v) for v in sys.argv[2:]]:
        t0 = time.time()
        row: dict = {"a": a}
        x0, y0 = L.RHO
        # 3. breakdown at rho
        lo, hi = 0.01, 2.0
        _, rhi = e_scha(a, x0, y0, hi)
        if rhi["status"] == "converged" and (rhi["stab_eff"] or -1) > 0:
            row["breakdown_lam"] = None
        else:
            for _ in range(30):
                mid = 0.5 * (lo + hi)
                _, r = e_scha(a, x0, y0, mid)
                if r["status"] == "converged" and (r["stab_eff"] or -1) > 0:
                    lo = mid
                else:
                    hi = mid
            row["breakdown_lam"] = [lo, hi]
        # 1. Lap ladder and root
        lam_max = row["breakdown_lam"][0] * 0.98 if row["breakdown_lam"] else 1.0
        lad = []
        for lam in (0.02, 0.05, 0.08, 0.10, 0.12, 0.15, 0.2, 0.3, 0.5):
            if lam >= lam_max:
                break
            lad.append({"lam": lam, "lap": lap_scha(a, lam)})
            print(a, lad[-1], flush=True)
        row["lap_ladder"] = lad
        row["lam_star_scha"] = None
        for p, q in zip(lad, lad[1:]):
            if p["lap"] > 0 >= q["lap"]:
                row["lam_star_scha"] = brentq(lambda lm: lap_scha(a, lm), p["lam"], q["lam"], xtol=1e-6)
                break
        # 2. paths and edge competitor
        edge = [(0.3, 0.96), (0.3, 0.955), (0.31, 0.96)]
        sj_path = os.path.join(os.path.dirname(out), f"scan_a{a:g}.json")
        if os.path.exists(sj_path):
            sj = json.load(open(sj_path))
            edge += [(v["x"], v["y"]) for v in sj["verified"][:6] if v["full_stability"]["stable"]]
            row["harmonic_Lam_1"] = sj["Lam_1"]["ratio_N64"] if sj["Lam_1"] else None
        comps = {"arc_to_i": path_points("arc_to_i"), "line_up": path_points("line_up"), "edge": sorted(set(edge))}
        prof = []
        lam_hi = row["lam_star_scha"] if row["lam_star_scha"] else lam_max
        lams = [lam_hi * f for f in (0.5, 0.7, 0.8, 0.85, 0.9, 0.95, 1.0)]
        if row.get("harmonic_Lam_1") and row["harmonic_Lam_1"] < lam_max:
            lams.append(row["harmonic_Lam_1"])
        for lam in sorted(lams):
            e0, r0 = e_scha(a, x0, y0, lam)
            rowl = {"lam": lam, "E_rho": e0, "u2_rho": r0["u2"], "gamma_rho": math.sqrt(r0["u2"]) / L.A_NN, "points": []}
            for kind, pts in comps.items():
                for (x, y) in pts:
                    e, r = e_scha(a, x, y, lam)
                    rowl["points"].append({"kind": kind, "x": x, "y": y, "dE": e - e0, "status": r["status"], "stab_eff": r["stab_eff"]})
            good = [p for p in rowl["points"] if p["status"] == "converged" and (p["stab_eff"] or -1) > 0]
            rowl["min_dE_stable"] = min((p["dE"] for p in good), default=None)
            prof.append(rowl)
            print(a, lam, rowl["min_dE_stable"], flush=True)
        row["profiles"] = prof
        if row["lam_star_scha"]:
            _, r = e_scha(a, x0, y0, row["lam_star_scha"])
            row["gamma_at_lam_star_scha"] = math.sqrt(r["u2"]) / L.A_NN
        row["seconds"] = round(time.time() - t0, 1)
        res[f"{a:g}"] = row
        json.dump(res, open(out, "w"), indent=1)
        print(json.dumps({k: row[k] for k in row if k not in ("profiles",)}), flush=True)


if __name__ == "__main__":
    main()
