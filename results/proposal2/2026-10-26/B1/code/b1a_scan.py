"""B1a part 2: global competitors of the triangular lattice for E = E_static + Lam E_zp (harmonic).

usage: python -I b1a_scan.py OUTDIR a1 [a2 ...]

Because E is linear in Lam, the triangular lattice is the minimiser over a set S of dynamically stable shapes iff
Lam < Lam_1 = inf_{tau in S, dE_zp(tau) < 0} dE_static(tau) / (-dE_zp(tau)). Near rho the ratio tends to the local
spinodal hbar* along every direction, with a linear correction from the cubic (D3-invariant) term, so generically
Lam_1 < hbar* (first-order transition: a finite jump of tau). This script
 * samples tau on a 0.005 grid of the region 0.15 <= x <= 0.5, max(sqrt(1-x^2), 0.80) <= y <= 1.15 of the fundamental
   domain (contains every stable lattice found by P2), E_zp by Duffy N = 32, stability by a half-shifted 48x48 grid
   + 72 long-wave directions (screen), then
 * re-verifies the 12 lowest-ratio stable shapes and the argmin of E(Lam) for a ladder of Lam with the full P2
   stability optimiser (seeds on n = 192 + Nelder-Mead + long-wave rows) and Duffy N = 64;
 * also writes the two mirror-line paths through rho (Re tau = 1/2 upward; arc |tau| = 1 toward i) with Duffy N = 64.
"""

import csv
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import b1_lib as L  # noqa: E402


def scan(a: float) -> list[dict]:
    rows = []
    x0, y0 = L.RHO
    es0 = L.e_static(a, x0, y0)
    ez0 = L.e_zp(a, x0, y0, 32)
    for x in np.round(np.arange(0.15, 0.5000001, 0.005), 6):
        ylo = max(math.sqrt(1 - x * x), 0.80)
        for y in np.round(np.arange(math.ceil(ylo / 0.005) * 0.005, 1.1500001, 0.005), 6):
            if abs(x - x0) < 1e-9 and abs(y - y0) < 3e-3:
                continue
            ok, r = L.quick_stable(a, float(x), float(y))
            row = {"x": float(x), "y": float(y), "stable_screen": ok, "min_ratio_screen": r}
            if ok:
                es = L.e_static(a, float(x), float(y))
                ez = L.e_zp(a, float(x), float(y), 32)
                row.update({"dEs": es - es0, "dEzp": ez - ez0})
            rows.append(row)
    return rows


def path(a: float, kind: str) -> list[dict]:
    x0, y0 = L.RHO
    es0, ez0 = L.e_static(a, x0, y0), L.e_zp(a, x0, y0, 64)
    out = []
    for t in np.linspace(0.0025, 0.2, 80):
        if kind == "line_up":
            x, y = 0.5, y0 + t
        else:  # arc |tau| = 1 toward i, parametrised by angle
            ang = math.pi / 3 + t
            x, y = math.cos(ang), math.sin(ang)
        r = math.hypot(x - x0, y - y0) / y0
        ok, mr = L.quick_stable(a, x, y)
        es, ez = L.e_static(a, x, y), L.e_zp(a, x, y, 64)
        out.append({"x": x, "y": y, "r": r, "stable_screen": ok, "min_ratio_screen": mr, "dEs": es - es0, "dEzp": ez - ez0,
                    "ratio": (es - es0) / (ez0 - ez) if ez < ez0 else None})
    return out


def main() -> None:
    outdir = sys.argv[1]
    for a in [float(s) for s in sys.argv[2:]]:
        t0 = time.time()
        rows = scan(a)
        with open(os.path.join(outdir, f"scan_a{a:g}.csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["x", "y", "stable_screen", "min_ratio_screen", "dEs", "dEzp"])
            w.writeheader()
            for r in rows:
                w.writerow(r)
        st = [r for r in rows if r["stable_screen"]]
        cand = [r for r in st if r["dEzp"] < 0]
        for r in cand:
            r["ratio"] = r["dEs"] / (-r["dEzp"])
        cand.sort(key=lambda r: r["ratio"])
        ver = []
        for r in cand[:12]:
            fs = L.full_stability(a, r["x"], r["y"])
            es = L.e_static(a, r["x"], r["y"]) - L.e_static(a, *L.RHO)
            ez = L.e_zp(a, r["x"], r["y"], 64) - L.e_zp(a, *L.RHO, 64)
            ver.append({"x": r["x"], "y": r["y"], "ratio_N32": r["ratio"], "dEs": es, "dEzp_N64": ez,
                        "ratio_N64": es / (-ez) if ez < 0 else None, "full_stability": fs})
        lam1 = None
        for v in ver:
            if v["full_stability"]["stable"] and v["ratio_N64"] is not None:
                lam1 = v
                break
        # argmin of E over the screened-stable sample along a Lam ladder
        ladder = []
        for lam in (0.02, 0.04, 0.06, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.15, 0.2, 0.3):
            best = min(st, key=lambda r: r["dEs"] + lam * r["dEzp"])
            dE = best["dEs"] + lam * best["dEzp"]
            ladder.append({"lam": lam, "argmin_x": best["x"], "argmin_y": best["y"], "dE_min": dE, "tri_is_min": dE >= 0})
        paths = {k: path(a, k) for k in ("line_up", "arc_to_i")}
        res = {"a": a, "n_points": len(rows), "n_stable_screen": len(st), "n_candidates": len(cand), "verified": ver,
               "Lam_1": lam1, "ladder": ladder, "paths": paths, "seconds": round(time.time() - t0, 1)}
        json.dump(res, open(os.path.join(outdir, f"scan_a{a:g}.json"), "w"), indent=1)
        print(json.dumps({"a": a, "n_stable": len(st), "Lam_1": None if lam1 is None else [lam1["x"], lam1["y"], lam1["ratio_N64"], lam1["full_stability"]["min_ratio_lam_over_k2"]],
                          "ladder": [(l["lam"], l["argmin_x"], l["argmin_y"], l["dE_min"]) for l in ladder], "s": res["seconds"]}), flush=True)


if __name__ == "__main__":
    main()
