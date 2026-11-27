"""Positive control for the numerical falsifier: it must find >=2 roots on a known witness."""
import json, sys
from fractions import Fraction
import numpy as np
from scipy.optimize import fsolve
w = json.load(open(sys.argv[1]))
def parse(s):
    v = [0, 0, 0]
    for t in s.split("+"):
        c = 1
        if t[0].isdigit(): c = int(t[0]); t = t[1:]
        v["XYZ".index(t)] += c
    return v
E = [tuple(map(parse, e.split("->"))) for e in w["edges"]]
fl = lambda L: np.array([float(Fraction(s)) for s in L])
a, r, k = fl(w["parameters"]["a"]), fl(w["parameters"]["rho"]), fl(w["parameters"]["k"])
def F(x):
    f = a - r * x
    for (al, be), kk in zip(E, k):
        f = f + (np.array(be) - np.array(al)) * kk * np.prod(x ** np.array(al))
    return f
rng = np.random.default_rng(1); roots = []
for s in range(300):
    sol, info, ier, _ = fsolve(F, 10 ** rng.uniform(-3, 3, 3), full_output=True)
    if ier == 1 and np.all(sol > 0) and np.max(np.abs(F(sol))) < 1e-9 * (1 + sol.max()) and not any(np.all(np.abs(np.log(sol) - np.log(z)) < 1e-2) for z in roots):
        roots.append(sol)
print(w["id"], "distinct positive roots:", len(roots), [list(np.round(z, 5)) for z in roots])
