"""M5b: explicit parametrisation of SAS(T) (derived by hand from the integer constraints, then checked numerically against M u = b mod 2pi)
and a grid + local refinement search of the volume maxima. Floating point (Tier C-numeric); not a proof of clause (iv).
Constraints: x1+x2+x3=pi, y1+y2+y3=pi, edge a: x1+y1=0, edge b: 2x2+y1+2y3=0, edge c: x1+2x3+2y2=0 (all mod 2pi).
Solution family: x1=2t, y1=-2t, x2=s, x3=pi-2t-s, y3=t-s+k*pi, y2=pi-y1-y3=pi+t+s-k*pi, with t,s in [0,2pi), k in {0,1}."""
import json, math, os, sys
import numpy as np
import mpmath as mp
from scipy.optimize import minimize
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from luo_lib import *
from m12_structure import PAIRINGS

gl = spec_from_pairings(PAIRINGS)
I = np.array(I_matrix(gl), dtype=float)
M = np.vstack([np.array([[1, 1, 1, 0, 0, 0], [0, 0, 0, 1, 1, 1]], float), I])
b = np.array([math.pi, math.pi, 0, 0, 0])


def point(t, s, k):
    return np.array([2 * t, s, math.pi - 2 * t - s, -2 * t, math.pi + t + s - k * math.pi, t - s + k * math.pi])


# verification of the parametrisation: constraint residual on random samples
rng = np.random.default_rng(1)
maxres = 0.0
for _ in range(1000):
    t, s = rng.uniform(0, 2 * math.pi, 2)
    k = int(rng.integers(0, 2))
    r = M @ point(t, s, k) - b
    maxres = max(maxres, float(np.max(np.abs(np.sin(r / 2)))))
# completeness of the family: rank and dimension check via exact integer linear algebra (sympy) in the report
import sympy as sp
Ms = sp.Matrix(M.astype(int).tolist())
SN = Ms.rank()

# Lobachevsky table
xs = np.linspace(0, math.pi, 200001)
tab = np.array([float(mp.clsin(2, 2 * x) / 2) for x in xs[::1]]) if False else None
Ls = np.array([float(mp.clsin(2, 2 * x) / 2) for x in np.linspace(0, math.pi, 20001)])
grid_x = np.linspace(0, math.pi, 20001)


def Lam(th):
    return np.interp(np.mod(th, math.pi), grid_x, Ls)


def volarr(P):
    return sum(Lam(P[i]) for i in range(6))


N = 1500
T, S = np.meshgrid(np.linspace(0, 2 * math.pi, N, endpoint=False), np.linspace(0, 2 * math.pi, N, endpoint=False), indexing="ij")
best = []
for k in (0, 1):
    P = [2 * T, S, math.pi - 2 * T - S, -2 * T, math.pi + T + S - k * math.pi, T - S + k * math.pi]
    V = volarr(P)
    idx = np.dstack(np.unravel_index(np.argsort(-V.ravel())[:40], V.shape))[0]
    for i, j in idx:
        best.append((float(V[i, j]), k, float(T[i, j]), float(S[i, j])))
best.sort(reverse=True)


def exactvol(x, k):
    return -float(sum(mp.clsin(2, 2 * a) / 2 for a in point(x[0], x[1], k)))


refined = []
seen = []
for v, k, t0, s0 in best[:60]:
    r = minimize(exactvol, [t0, s0], args=(k,), method="Nelder-Mead", options={"xatol": 1e-10, "fatol": 1e-13, "maxiter": 2000})
    refined.append((-r.fun, k, r.x))
refined.sort(key=lambda x: -x[0])
top = refined[0][0]
pts = []
for v, k, x in refined:
    if v > top - 1e-7:
        th = np.mod(point(x[0], x[1], k), 2 * math.pi)
        key = tuple(np.round(th, 4))
        if key not in seen:
            seen.append(key)
            pts.append({"vol": v, "k": k, "t": float(x[0]), "s": float(x[1]), "theta_over_pi": [round(float(a / math.pi), 6) for a in th],
                        "min_abs_sin_theta": float(min(abs(math.sin(a)) for a in th))})
res = {"param_residual_max_abs_sin_half": maxres, "rank_of_constraint_matrix": SN,
       "grid": N, "max_volume": top, "n_distinct_max_points_reported": len(pts), "max_points": pts[:8],
       "all_reported_maxima_smooth(min|sin|>1e-6)": all(p["min_abs_sin_theta"] > 1e-6 for p in pts),
       "second_best_distinct_local_value": next((v for v, k, x in refined if v < top - 1e-6), None)}
# volume at the non-smooth candidates: points where some u=+-1 (theta in {0,pi}); sample max over such sub-families
nonsmooth = []
for k in (0, 1):
    for which in range(6):
        for target in (0.0, math.pi):
            # solve theta_which = target for s given t on a fine t grid, keep best volume
            for t in np.linspace(0, 2 * math.pi, 4001):
                for s in np.linspace(0, 2 * math.pi, 4001)[:0]:
                    pass
# do it by 1D curves: for each coordinate, equation theta_i(t,s)=target (mod 2pi) is linear in s or t
def curve_max(k):
    out = -1e9
    tt = np.linspace(0, 2 * math.pi, 40001)
    for which in range(6):
        for target in (0.0, math.pi):
            for mm in (-2, -1, 0, 1, 2):
                # theta_which as function: coefficients (ct, cs, c0)
                coef = {0: (2, 0, 0), 1: (0, 1, 0), 2: (-2, -1, math.pi), 3: (-2, 0, 0),
                        4: (1, 1, math.pi - k * math.pi), 5: (1, -1, k * math.pi)}[which]
                ct, cs, c0 = coef
                if cs != 0:
                    ss = (target + 2 * math.pi * mm - c0 - ct * tt) / cs
                    P = [point(a, c, k) for a, c in zip(tt[::40], ss[::40])]
                    for a, c in zip(tt[::40], ss[::40]):
                        v = float(sum(mp.clsin(2, 2 * x) / 2 for x in point(a, c, k)))
                        out = max(out, v)
                else:
                    # theta depends on t only: t fixed values
                    tv = (target + 2 * math.pi * mm - c0) / ct if ct != 0 else None
                    if tv is None:
                        continue
                    for c in np.linspace(0, 2 * math.pi, 1001):
                        v = float(sum(mp.clsin(2, 2 * x) / 2 for x in point(tv, c, k)))
                        out = max(out, v)
    return out
res["max_volume_over_nonsmooth_sub-loci(coarse sampling)"] = max(curve_max(0), curve_max(1))
print(json.dumps(res, indent=1))
