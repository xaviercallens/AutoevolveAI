"""Exact rational primal certificate for max concurrent flow = 147/157 (shortest-path-DAG restricted feasibility)."""
import json, time
from collections import defaultdict, deque
from fractions import Fraction
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from sage.all import QQ, matrix, vector
t0 = time.time()
def log(*a): print(f"[{time.time()-t0:6.1f}s]", *a, flush=True)
D = json.load(open("/tmp/muc9audit/work/graph.json"))
phys = [tuple(e) for e in D["phys"]]
sess = [tuple(v) for v in D["sess"].values()]
adj = [[] for _ in range(182)]
eid = {}
for k, (a, b) in enumerate(phys):
    adj[a].append(b); adj[b].append(a); eid[(a, b)] = k; eid[(b, a)] = k
def bfs(s):
    d = [-1]*182; d[s] = 0; Q = deque([s])
    while Q:
        u = Q.popleft()
        for w in adj[u]:
            if d[w] < 0: d[w] = d[u] + 1; Q.append(w)
    return d
dist = [bfs(v) for v in range(182)]
r = Fraction(147, 157)
groups = defaultdict(lambda: defaultdict(int))
for s, t in sess: groups[s][t] += 1
gl = sorted(groups)
var = []  # (g, u, v)
for gi, s in enumerate(gl):
    ds = dist[s]
    for u in range(182):
        for v in adj[u]:
            if ds[v] == ds[u] + 1 and any(ds[u] + 1 + dist[v][t] == ds[t] for t in groups[s]):
                var.append((gi, u, v))
nv = len(var); ng = len(gl)
log("groups", ng, "DAG arc vars", nv)
rows, cols, vals = [], [], []
for k, (gi, u, v) in enumerate(var):
    rows += [gi*182 + u, gi*182 + v]; cols += [k, k]; vals += [1.0, -1.0]
beq = np.zeros(ng*182 + len(phys)); bex = [Fraction(0)]*(ng*182 + len(phys))
for gi, s in enumerate(gl):
    tot = sum(groups[s].values())
    bex[gi*182 + s] = r*tot
    for t, m in groups[s].items(): bex[gi*182 + t] = -r*m
for k, (gi, u, v) in enumerate(var):
    rows.append(ng*182 + eid[(u, v)]); cols.append(k); vals.append(1.0)
for i in range(len(phys)): bex[ng*182 + i] = Fraction(1)   # all edges saturated (forced: total load = 785 r = 735)
beq = np.array([float(b) for b in bex])
A = coo_matrix((vals, (rows, cols)), shape=(len(bex), nv)).tocsr()
res = linprog(np.zeros(nv), A_eq=A, b_eq=beq, bounds=(0, None), method="highs-ds")
log("HiGHS feasibility status", res.status, res.message)
xf = res.x
S = [k for k in range(nv) if xf[k] > 1e-10]
log("support size", len(S))
Ad = A[:, S].tocoo()
M = matrix(QQ, A.shape[0], len(S), {(int(i), int(j)): QQ(int(round(v))) for i, j, v in zip(Ad.row, Ad.col, Ad.data)}, sparse=True)
bq = vector(QQ, [QQ(b.numerator)/QQ(b.denominator) for b in bex])
log("support column rank", M.rank(), "of", len(S))
xs = M.solve_right(bq)
assert M*xs == bq
log("exact solve: min", min(xs), "max", max(xs), "all >= 0", all(c >= 0 for c in xs))
# independent exact re-check in Fractions
fx = {var[S[i]]: Fraction(int(xs[i].numerator()), int(xs[i].denominator())) for i in range(len(S))}
load = [Fraction(0)]*len(phys); net = defaultdict(Fraction)
for (gi, u, v), f in fx.items():
    assert f >= 0
    load[eid[(u, v)]] += f; net[(gi, u)] += f; net[(gi, v)] -= f
ok_cap = all(l <= 1 for l in load)
ok_cons = all(net[(gi, w)] == bex[gi*182 + w] for gi in range(ng) for w in range(182))
log("Fraction check: capacity<=1", ok_cap, "conservation with demand 147/157 each session", ok_cons, "max denom", max(f.denominator for f in fx.values()))
# dual / upper bound: any feasible flow of rate r has load >= r * sum dist
sd = sum(dist[s][t] for s, t in sess)
log("sum dist", sd, "upper bound", Fraction(len(phys), sd), "== 147/157", Fraction(len(phys), sd) == r)
import hashlib
cert = {"r": "147/157", "flows": [[gl[gi], u, v, str(f)] for (gi, u, v), f in sorted(fx.items())]}
s = json.dumps(cert, sort_keys=True)
open("/tmp/muc9audit/work/lp_certificate.json", "w").write(s)
log("certificate saved", len(cert["flows"]), "sha256", hashlib.sha256(s.encode()).hexdigest())
