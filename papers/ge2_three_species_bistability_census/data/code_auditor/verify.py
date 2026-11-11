"""Independent GE-2 auditor verifier (no producer code imported)."""
import json, sys, os, itertools, random, collections
from fractions import Fraction as F

BASE = sys.argv[1]
SP = "XYZ"

def parse_cplx(s, n):
    v = [0] * n
    for t in s.split("+"):
        t = t.strip()
        c = 1
        if t[0].isdigit():
            c = int(t[0]); t = t[1:]
        v[SP.index(t)] += c
    return tuple(v)

def parse_edge(e, n):
    a, b = e.split("->")
    return parse_cplx(a, n), parse_cplx(b, n)

def mono(al, x):
    r = F(1)
    for i, e in enumerate(al):
        r *= x[i] ** e
    return r

def rhs(edges, a, rho, k, x):
    n = len(x)
    f = [a[i] - rho[i] * x[i] for i in range(n)]
    for (al, be), ke in zip(edges, k):
        m = ke * mono(al, x)
        for i in range(n):
            f[i] += (be[i] - al[i]) * m
    return f

def jac(edges, rho, k, x):
    n = len(x)
    J = [[F(0)] * n for _ in range(n)]
    for i in range(n):
        J[i][i] -= rho[i]
    for (al, be), ke in zip(edges, k):
        for j in range(n):
            if al[j] == 0:
                continue
            al2 = list(al); al2[j] -= 1
            d = ke * al[j] * mono(al2, x)
            for i in range(n):
                J[i][j] += (be[i] - al[i]) * d
    return J

def hurwitz_ok(J):
    n = len(J)
    if n == 2:
        tr = J[0][0] + J[1][1]
        det = J[0][0] * J[1][1] - J[0][1] * J[1][0]
        return tr < 0 and det > 0
    # char poly of J: l^3 + c1 l^2 + c2 l + c3
    c1 = -(J[0][0] + J[1][1] + J[2][2])
    c2 = sum(J[i][i] * J[j][j] - J[i][j] * J[j][i] for i, j in [(0, 1), (0, 2), (1, 2)])
    det = (J[0][0] * (J[1][1] * J[2][2] - J[1][2] * J[2][1])
           - J[0][1] * (J[1][0] * J[2][2] - J[1][2] * J[2][0])
           + J[0][2] * (J[1][0] * J[2][1] - J[1][1] * J[2][0]))
    c3 = -det
    return c1 > 0 and c3 > 0 and c1 * c2 > c3

census = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(BASE, "census.jsonl"))}
wdir = os.path.join(BASE, "witnesses")
res = collections.Counter(); fails = []
for fn in sorted(os.listdir(wdir)):
    w = json.load(open(os.path.join(wdir, fn)))
    n = w["species"]
    edges = [parse_edge(e, n) for e in w["edges"]]
    P = w["parameters"]
    a = [F(s) for s in P["a"]]; rho = [F(s) for s in P["rho"]]; k = [F(s) for s in P["k"]]
    p = [F(s) for s in w["equilibrium_p"]]; q = [F(s) for s in w["equilibrium_q"]]
    errs = []
    if len(k) != len(edges) or len(a) != n or len(rho) != n: errs.append("arity")
    if not all(v > 0 for v in a + rho + k): errs.append("nonpositive param")
    if not all(v > 0 for v in p + q): errs.append("nonpositive eq")
    if p == q: errs.append("p==q")
    if any(v != 0 for v in rhs(edges, a, rho, k, p)): errs.append("f(p)!=0")
    if any(v != 0 for v in rhs(edges, a, rho, k, q)): errs.append("f(q)!=0")
    if not hurwitz_ok(jac(edges, rho, k, p)): errs.append("p not Hurwitz")
    if not hurwitz_ok(jac(edges, rho, k, q)): errs.append("q not Hurwitz")
    if fn.startswith("G"):
        r = census.get(w["id"])
        if r is None: errs.append("no census row")
        else:
            if sorted(r["edges"]) != sorted(w["edges"]): errs.append("edges mismatch")
            if r["verdict"] != "BISTABLE_CERT": errs.append("census verdict " + r["verdict"])
    tag = fn[0]
    res[(tag, "fail" if errs else "pass")] += 1
    if errs: fails.append((fn, errs))
print(dict(res)); print("fails:", fails[:20])
cb = {i for i, r in census.items() if r["verdict"] == "BISTABLE_CERT"}
wg = {f[:-5] for f in os.listdir(wdir) if f.startswith("G")}
print("census bistable w/o witness:", sorted(cb - wg)[:10], "witness not in census-bistable:", sorted(wg - cb)[:10])
