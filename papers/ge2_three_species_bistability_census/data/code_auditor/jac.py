"""Independent JAC-rule recomputation (sympy) + numerical falsification attempt."""
import json, sys, os, random, collections
import sympy as sp
import numpy as np
from scipy.optimize import fsolve
BASE = sys.argv[1]
rows = [json.loads(l) for l in open(os.path.join(BASE, "census.jsonl"))]

def parse(s):
    v = [0, 0, 0]
    for t in s.split("+"):
        c = 1
        if t[0].isdigit(): c = int(t[0]); t = t[1:]
        v["XYZ".index(t)] += c
    return v

x = sp.symbols("x0:3", positive=True); r = sp.symbols("r0:3", positive=True); A = sp.symbols("a0:3", positive=True)
def field(edges):
    ks = sp.symbols(f"k0:{len(edges)}", positive=True)
    f = [A[i] - r[i] * x[i] for i in range(3)]
    for (al, be), k in zip(edges, ks):
        m = k * x[0] ** al[0] * x[1] ** al[1] * x[2] ** al[2]
        for i in range(3): f[i] += (be[i] - al[i]) * m
    return f, ks

def jac_nonneg(edges):
    f, ks = field(edges)
    J = sp.Matrix(f).jacobian(x)
    d = sp.Poly(sp.expand((-J).det()), *x, *r, *ks)
    coeffs = d.coeffs()
    return all(c >= 0 for c in coeffs), d.coeff_monomial(r[0] * r[1] * r[2])

rng = random.Random(20261111)
mono_rows = [q for q in rows if q["verdict"] == "MONOSTATIONARY_JAC"]
other = [q for q in rows if q["verdict"] != "MONOSTATIONARY_JAC"]
s60 = rng.sample(mono_rows, 60); s40 = rng.sample(other, 40)
ok = sum(1 for q in s60 if jac_nonneg([tuple(map(parse, e.split("->"))) for e in q["edges"]])[0])
neg = sum(1 for q in s40 if not jac_nonneg([tuple(map(parse, e.split("->"))) for e in q["edges"]])[0])
print(f"JAC rows recomputed nonneg: {ok}/60; non-JAC rows with a negative coeff: {neg}/40")
print("consistency: jac flag vs verdict", collections.Counter((q["jac"], q["verdict"]) for q in rows))

# numerical falsification on 30 JAC rows
nprng = np.random.default_rng(7)
hits = []
for q in s60[:30]:
    edges = [tuple(map(parse, e.split("->"))) for e in q["edges"]]
    f, ks = field(edges)
    F = sp.lambdify([x, A, r, ks], f, "numpy")
    for trial in range(40):
        av = 10 ** nprng.uniform(-2, 2, 3); rv = 10 ** nprng.uniform(-2, 2, 3); kv = 10 ** nprng.uniform(-2, 2, len(edges))
        roots = []
        for s in range(30):
            x0 = 10 ** nprng.uniform(-3, 3, 3)
            sol, info, ier, _ = fsolve(lambda z: F(z, av, rv, kv), x0, full_output=True)
            if ier == 1 and np.all(sol > 1e-9) and np.max(np.abs(F(sol, av, rv, kv))) < 1e-9 * (1 + np.max(np.abs(sol))):
                if not any(np.all(np.abs(np.log(sol) - np.log(z)) < 1e-2) for z in roots): roots.append(sol)
        if len(roots) > 1: hits.append((q["id"], q["edges"], [list(z) for z in roots])); break
print("numerical falsification: networks 30 x 40 param draws x 30 starts; rows with >=2 positive roots:", len(hits), hits[:3])
