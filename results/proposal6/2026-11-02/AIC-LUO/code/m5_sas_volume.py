"""M5 (floating point, Tier C-numeric): circle-valued angle structures SAS(T) of the paper's triangulation and the maxima of the volume.
Method: many random starts; feasibility by least squares on the periodic constraints, then SLSQP maximisation of vol on the feasible set.
This is NOT a proof of clause (iv)."""
import json, os, sys, math
import numpy as np
from scipy.optimize import least_squares, minimize
import mpmath as mp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from luo_lib import *
from m12_structure import PAIRINGS

gl = spec_from_pairings(PAIRINGS)
I = np.array(I_matrix(gl), dtype=float)
M = np.vstack([np.array([[1, 1, 1, 0, 0, 0], [0, 0, 0, 1, 1, 1]], float), I])
b = np.array([math.pi, math.pi, 0, 0, 0])


def lob(th):
    return float(mp.clsin(2, 2 * th) / 2)


def vol(th):
    return sum(lob(t) for t in th)


def resid(th):
    r = M @ th - b
    return np.concatenate([np.cos(r) - 1, np.sin(r)])


rng = np.random.default_rng(12345)
found = []
for trial in range(300):
    th0 = rng.uniform(-math.pi, math.pi, 6)
    sol = least_squares(resid, th0, xtol=1e-14, ftol=1e-14)
    if np.linalg.norm(sol.fun) > 1e-9:
        continue
    cons = {"type": "eq", "fun": resid}
    r = minimize(lambda t: -vol(t), sol.x, constraints=[cons], method="SLSQP", options={"maxiter": 200, "ftol": 1e-13})
    if np.linalg.norm(resid(r.x)) < 1e-8:
        found.append((vol(r.x), np.mod(r.x, 2 * math.pi)))
found.sort(key=lambda x: -x[0])
res = {"n_starts": 300, "n_feasible_optimised": len(found)}
if found:
    top = found[0][0]
    res["max_volume_found"] = top
    near = [f for f in found if f[0] > top - 1e-6]
    res["n_runs_reaching_max"] = len(near)
    pts = []
    for v, t in near[:6]:
        pts.append({"vol": v, "theta_over_pi": [round(float(x / math.pi), 6) for x in t],
                    "min_dist_to_0_or_pi": float(min(min(abs(math.sin(x))) if False else abs(math.sin(x)) for x in t))})
    res["max_points_sample"] = pts
    res["max_points_smooth(all u != +-1; |sin theta|>1e-6)"] = all(p["min_dist_to_0_or_pi"] > 1e-6 for p in pts)
    # distinct local volume values
    vals = sorted({round(f[0], 6) for f in found}, reverse=True)
    res["distinct_optimised_volume_values"] = vals[:10]
    # smallest |sin| over all optimised points with volume within 1e-6 of max
    res["feasible_points_with_some_u_pm1_and_their_volumes"] = sorted({round(f[0], 6) for f in found if min(abs(math.sin(x)) for x in f[1]) < 1e-6}, reverse=True)[:5]
print(json.dumps(res, indent=1))
