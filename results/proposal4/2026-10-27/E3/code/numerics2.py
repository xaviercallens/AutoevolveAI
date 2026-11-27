"""Engine-level random check of Eq.(1) (exact Fractions), root form vs brute force, N2 perturbations, E3x derivative landscape.
Run from repo root: taskset -c 2,3 python3 results/proposal4/2026-10-27/E3/code/numerics2.py"""
import json
import math
import random
import sys
from fractions import Fraction as Fr

import mpmath as mp
import numpy as np

sys.path.insert(0, "results/proposal4/2026-10-27/E3/code")
from link_funcs import root_form  # noqa: E402

random.seed(31102026)
out = {}

# 1. engine-level: exact rational engines; Eq.(1) with sqrt evaluated in 50-digit mpmath
mp.mp.dps = 50
n = 0
viol = 0
viol_pert = 0
maxlhs = mp.mpf(0)
for _ in range(20000):
    a = Fr(random.randint(1, 200), 50)
    b = Fr(random.randint(1, 200), 50)
    q = Fr(random.randint(1, 200), 20)
    c = Fr(random.randint(1, 99), 100)
    th = Fr(random.randint(1, 4000), 100)
    tc = Fr(random.randint(1, 4000), 100)
    W = q - a * a / th - b * b / tc
    if W <= 0:
        continue
    P = W / (th + tc)
    den = q / c - a * a / th
    if den <= 0:
        continue
    e = W / den
    Pt = 4 * (a + b) ** 2 * P / (q * q)
    assert Pt <= 1
    Ptm = mp.mpf(Pt.numerator) / Pt.denominator
    s = mp.sqrt(1 - Ptm)
    cm = mp.mpf(c.numerator) / c.denominator
    em = mp.mpf(e.numerator) / e.denominator
    lhs = em / cm + (1 - cm) * Ptm / (2 * (1 + s) - cm * Ptm)
    n += 1
    maxlhs = max(maxlhs, lhs)
    if lhs > 1 + mp.mpf(10) ** -30:
        viol += 1
    lhs_p = em / cm + (1 + cm) * Ptm / (2 * (1 + s) - cm * Ptm)  # perturbed eq (1): (1-c) -> (1+c)
    if lhs_p > 1 + mp.mpf(10) ** -30:
        viol_pert += 1
out["engine"] = {"engines": n, "violations_eq1": viol, "max_lhs": mp.nstr(maxlhs, 12),
                 "perturbed_eq1_violations (N, (1-c)->(1+c))": viol_pert}


# 2. root form is a tight upper bound on the true engine optimum (float brute force, Tier X)
def brute(c, P, z, n=40001):
    Mh = (1 + z) ** 2 / 4
    Mc = (1 - z) ** 2 / 4
    q = 1.0
    Pt = P * q * q / 4
    best = -1.0
    for th in np.geomspace(1e-3, 1e4, n):
        A_, B_, C_ = -Pt, q - Mh / th - Pt * th, -Mc
        disc = B_ * B_ - 4 * A_ * C_
        if disc < 0:
            continue
        for sg in (1, -1):
            tc = (-B_ + sg * math.sqrt(disc)) / (2 * A_)
            if tc <= 0:
                continue
            W = q - Mh / th - Mc / tc
            best = max(best, W / (q / c - Mh / th) / c)
    return best


rows = []
for c, P, z in [(0.5, 0.5, 0.0), (0.5, 0.5, 0.5), (0.5, 0.5, 1.0), (0.5, 0.5, -1.0), (0.1, 0.9, 0.3), (0.9, 0.2, -0.4), (0.3, 0.05, 0.7), (0.8, 0.95, -0.8)]:
    r = float(root_form(mp.mpf(c), mp.mpf(P), mp.mpf(z)))
    b = brute(c, P, z)
    rows.append({"c": c, "P": P, "zeta": z, "root_form": r, "brute_force_max": b, "root_minus_brute": r - b})
out["brute"] = rows
out["brute_all_root_ge_brute"] = all(x["root_minus_brute"] >= -1e-9 for x in rows)


# 3. N2 perturbations of F: which are caught by the grid (some pair with non-increasing efficiency)?
def eta_from(c, P, z, mode):
    s = mp.sqrt(1 - P)
    K = 2 / (1 - s)
    if mode == "true":
        A, B, C = K / c - (1 + z) ** 2 / 4, (1 - z * z) / 2, (1 - z) ** 2 / 4 + K * (1 - c) / c
    elif mode == "swap":
        A, B, C = K / c - (1 - z) ** 2 / 4, (1 - z * z) / 2, (1 + z) ** 2 / 4 + K * (1 - c) / c
    elif mode == "Bflip":
        A, B, C = K / c - (1 + z) ** 2 / 4, -(1 - z * z) / 2, (1 - z) ** 2 / 4 + K * (1 - c) / c
    elif mode == "Khalf":
        K = K / 2
        A, B, C = K / c - (1 + z) ** 2 / 4, (1 - z * z) / 2, (1 - z) ** 2 / 4 + K * (1 - c) / c
    elif mode == "Csign":
        A, B, C = K / c - (1 + z) ** 2 / 4, (1 - z * z) / 2, -(1 - z) ** 2 / 4 + K * (1 - c) / c
    disc = B * B + 4 * A * C
    if disc < 0 or A <= 0:
        return None
    w = (B + mp.sqrt(disc)) / (2 * A)
    return (1 - w * w) / c


mp.mp.dps = 30
res = {}
for mode in ["true", "swap", "Bflip", "Khalf", "Csign"]:
    bad = 0
    tot = 0
    undefined = 0
    first = None
    for ci in range(1, 20):
        c = mp.mpf(ci) / 20
        for pi in range(1, 21):
            P = mp.mpf(pi) / 20
            prev = None
            for zi in range(0, 41):
                z = -1 + mp.mpf(zi) / 20
                u = eta_from(c, P, z, mode)
                if u is None:
                    undefined += 1
                    prev = None
                    continue
                if prev is not None:
                    tot += 1
                    if not u > prev:
                        bad += 1
                        if first is None:
                            first = [float(c), float(P), float(z)]
                prev = u
    res[mode] = {"pairs": tot, "non_increasing": bad, "undefined": undefined, "first_bad": first}
out["N2"] = res


# 4. E3x: derivative landscape du/dzeta (float, implicit differentiation)
def dudz(c, P, z):
    s = math.sqrt(1 - P)
    K = 2 / (1 - s)
    A = K / c - (1 + z) ** 2 / 4
    B = (1 - z * z) / 2
    C = (1 - z) ** 2 / 4 + K * (1 - c) / c
    w = (B + math.sqrt(B * B + 4 * A * C)) / (2 * A)
    T = (1 - z) + (1 + z) * w
    Gz = c * T * (1 - w) / 2
    Gw = 2 * K * w - c * T * (1 + z) / 2
    dw = -Gz / Gw
    return -2 * w * dw / c, w


grid = []
for c in np.linspace(0.01, 0.99, 99):
    for P in np.linspace(0.01, 1.0, 100):
        for z in np.linspace(-1, 1, 81):
            d, w = dudz(c, P, z)
            grid.append((d, c, P, z))
arr = np.array(grid)
imin = int(np.argmin(arr[:, 0]))
imax = int(np.argmax(arr[:, 0]))
out["E3x"] = {"grid_points": len(grid), "min_dudz": float(arr[imin, 0]), "argmin (c,P,zeta)": [float(x) for x in arr[imin, 1:]],
              "max_dudz": float(arr[imax, 0]), "argmax (c,P,zeta)": [float(x) for x in arr[imax, 1:]],
              "all_positive": bool(np.all(arr[:, 0] > 0)),
              "dudz at P=0.5,zeta=0 for c=0.01,0.1,0.5,0.9": [[float(c), float(dudz(c, 0.5, 0.0)[0])] for c in (0.01, 0.1, 0.5, 0.9)]}
json.dump(out, open("results/proposal4/2026-10-27/E3/data/numerics2.json", "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
