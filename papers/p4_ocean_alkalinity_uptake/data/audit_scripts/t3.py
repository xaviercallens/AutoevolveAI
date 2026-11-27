"""Point exploration: corners, sign combos for U1/U2, grid interior scan, monotone trends, PyCO2SYS cross-check."""
import sys, itertools, random, json
sys.path.insert(0, '/tmp/k2audit')
from model import *
import numpy as np
mp.dps = 30
BOX = {"T": (0.0, 30.0), "S": (30.0, 38.0), "f": (280.0, 560.0), "TA35": (2200.0, 2400.0)}
out = {}
corners = list(itertools.product(*[BOX[k] for k in ("T", "S", "f", "TA35")]))
cv = sorted((float(eta_point(*c)[0]), c) for c in corners)
out["corner_min"], out["corner_max"] = cv[0], cv[-1]
# interior grid scan
g = {k: np.linspace(*BOX[k], 7) for k in BOX}
vals = []
for T in g["T"]:
    for S in g["S"]:
        for f in g["f"]:
            for ta in g["TA35"]:
                vals.append(float(eta_point(T, S, f, ta)[0]))
out["grid_range"] = [min(vals), max(vals)]
# monotone trends: sign of finite differences along each axis on a 5^4 grid
g5 = {k: np.linspace(*BOX[k], 5) for k in BOX}
signs = {k: set() for k in BOX}
for T in g5["T"]:
    for S in g5["S"]:
        for f in g5["f"]:
            for ta in g5["TA35"]:
                base = eta_point(T, S, f, ta)[0]
                for k, d in (("T", 0.01), ("S", 0.01), ("f", 0.1), ("TA35", 0.1)):
                    p = {"T": T, "S": S, "f": f, "TA35": ta}
                    p[k] = p[k] + d if p[k] + d <= BOX[k][1] else p[k] - d
                    sgn = (eta_point(p["T"], p["S"], p["f"], p["TA35"])[0] - base) * (1 if p[k] > {"T": T, "S": S, "f": f, "TA35": ta}[k] else -1)
                    signs[k].add(int(mp.sign(sgn)))
out["finite_diff_signs"] = {k: sorted(v) for k, v in signs.items()}
# U1/U2 sign combos at the two extreme corners
names = ["K0", "K1", "K2", "KB", "KW"]
for ns in (1, 2):
    ext = []
    for corner in (cv[0][1], cv[-1][1]):
        for sg in itertools.product((-1, 1), repeat=5):
            dpk = {n: s*ns*SIG[n] for n, s in zip(names, sg)}
            ext.append(float(eta_point(*corner, dpk=dpk)[0]))
    out[f"U{ns}_corner_signcombo_range"] = [min(ext), max(ext)]
# KW and BT variants (PyCO2SYS-like: KW const 148.9802, BT 0.0004157) at extremes
for corner in (cv[0][1], cv[-1][1]):
    a = float(eta_point(*corner)[0])
    b = float(eta_point(*corner, kw_const_shift=mpf("0.015"))[0])
    c = float(eta_point(*corner, bt_coef="0.0004157")[0])
    d = float(eta_point(*corner, bt_coef="0.0004326")[0])  # Lee et al 2010 (0.0004326 S/35)
    out[f"variants_{corner}"] = {"base": a, "KW+0.015": b - a, "BT U74 0.0004157": c - a, "BT Lee2010 0.0004326": d - a}
print(json.dumps(out, indent=1, default=str))
