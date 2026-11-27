"""Independent auditor recomputation of arXiv 2610.10108 Section 4 (Sage GF(9) + GF(3) block cross-check)."""
import json, hashlib, random, itertools, time, sys
from collections import deque
from sage.all import GF, PolynomialRing, matrix, vector, Graph, Subsets, QQ, Matrix
t0 = time.time()
def log(*a): print(f"[{time.time()-t0:6.1f}s]", *a, flush=True)
def h(o): return hashlib.sha256(json.dumps(o, sort_keys=True).encode()).hexdigest()
L = json.load(open("/tmp/muc9audit/work/lists.json"))
R, PI, C, J = L["R"], L["pi"], L["C"], L["J"]
Rs, Cs, Js = set(R), set(C), set(J)
Bs = Rs - Cs - Js
x = PolynomialRing(GF(3), "x").gen()
F = GF(9, "t", modulus=x**2 + 1); t = F.gen()
assert (x**2 + 1).is_irreducible() and t**2 == -1
eta = [F(r % 3) + F(r // 3) * t for r in range(9)]
assert len(set(eta)) == 9
T = [(F(0), F(0), F(1))] + [(F(0), F(1), eta[r]) for r in range(9)] + [(F(1), eta[r], eta[s]) for r in range(9) for s in range(9)]
def dot(a, b): return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
# normalized check
assert len(set(T)) == 91 and all(next(c for c in v if c != 0) == 1 for v in T)
nb = [[j for j in range(91) if dot(T[i], T[j]) == 0] for i in range(91)]
edges = [(i, 91 + j) for i in range(91) for j in nb[i]]
assert len(edges) == 910
Gfull = Graph([list(range(182)), edges], format="vertices_and_edges")
log("H: n", Gfull.order(), "m", Gfull.size(), "regular", Gfull.is_regular(10), "girth", Gfull.girth(), "bipartite", Gfull.is_bipartite())
# lists
log("R", len(R), len(Rs), min(R), max(R), "C,J subset R", Cs <= Rs and Js <= Rs, "disjoint", not (Cs & Js), "|B|", len(Bs), "pi perm", sorted(PI) == list(range(182)))
pos = {v: k for k, v in enumerate(PI)}
phys = [q for q in range(910) if q not in Rs]
G = Graph([list(range(182)), [edges[q] for q in phys]], format="vertices_and_edges")
log("G: m", G.size(), "connected", G.is_connected())
# orientation degrees on all 910 candidate edges
din = [0]*182; dout = [0]*182; dCp = [0]*182; dJm = [0]*182
for q, (a, b) in enumerate(edges):
    e, l = (a, b) if pos[a] < pos[b] else (b, a)
    tail, head = (e, l) if q not in Rs else (l, e)
    dout[tail] += 1; din[head] += 1
    if q in Cs: dCp[tail] += 1
    if q in Js: dJm[head] += 1
log("deg: all din=dout=5", all(din[v] == 5 and dout[v] == 5 for v in range(182)), "dC+=dJ- all", all(dCp[v] == dJm[v] for v in range(182)))
# sessions + distances
sess = {}
for q in sorted(Bs):
    a, b = edges[q]
    s, tt = (a, b) if pos[a] < pos[b] else (b, a)
    sess[q] = (s, tt)
log("sessions hash", h({str(q): list(v) for q, v in sess.items()}))
adj = [[] for _ in range(182)]
for q in phys:
    a, b = edges[q]; adj[a].append(b); adj[b].append(a)
def bfs(s):
    d = [-1]*182; d[s] = 0; Q = deque([s])
    while Q:
        u = Q.popleft()
        for w in adj[u]:
            if d[w] < 0: d[w] = d[u] + 1; Q.append(w)
    return d
dist = {}
for q, (s, tt) in sess.items():
    dist[q] = bfs(s)[tt]
from collections import Counter
log("distances", Counter(dist.values()), "sum", sum(dist.values()), "sources", len({s for s, _ in sess.values()}))
# local codes
inc = [[] for _ in range(182)]
for q, (a, b) in enumerate(edges):
    inc[a].append(q); inc[b].append(q)
Ms, Hs = [], []
mds_ok = True
for v in range(182):
    z = T[v] if v < 91 else T[v - 91]
    perp = [k for k in range(91) if dot(z, T[k]) == 0]
    u, w = T[perp[0]], T[perp[1]]
    rows = []
    for q in inc[v]:
        other = edges[q][1] - 91 if v < 91 else edges[q][0]
        y = T[other]
        # solve y = lam u + mu w
        A = matrix(F, [[u[0], w[0]], [u[1], w[1]], [u[2], w[2]]])
        sol = A.solve_right(vector(F, y))
        assert A * sol == vector(F, y)
        lam, mu = sol
        if v >= 91: lam, mu = lam**3, mu**3
        rows.append([lam**(4 - r) * mu**r for r in range(5)])
    M = matrix(F, rows)
    if any(M.matrix_from_rows(list(S)).det() == 0 for S in itertools.combinations(range(10), 5)):
        mds_ok = False
    Hv = M.left_kernel().basis_matrix()
    assert Hv.nrows() == 5 and (Hv * M).is_zero()
    Ms.append(M); Hs.append(Hv)
log("local: all rank5 + MDS (252 subsets each)", mds_ok and all(M.rank() == 5 for M in Ms))
# global parity matrix 910 x 910
P = matrix(F, 910, 910, sparse=True)
for v in range(182):
    for i in range(5):
        for k, q in enumerate(inc[v]):
            if Hs[v][i, k] != 0: P[5*v + i, q] = Hs[v][i, k]
P = P.dense_matrix()
rk = P.rank()
log("rank P over F9", rk, "dim W", 910 - rk)
EC = matrix(F, [[1 if q == c else 0 for q in range(910)] for c in sorted(C)])
EB = matrix(F, [[1 if q == c else 0 for q in range(910)] for c in sorted(Bs)])
rC = P.stack(EC).rank(); rCB = P.stack(EC).stack(EB).rank()
log("dim W_C", 910 - rC, "rank [P;C;B]", rCB, "=> restriction to B injective", rCB == 910)
# GF(3) 2x2 block cross-check: a+bt -> [[a,-b],[b,a]]
def blk(z):
    p = z.polynomial(); a = p[0]; b = p[1]
    return [[a, -b], [b, a]]
F3 = GF(3)
P3 = matrix(F3, 1820, 1820, sparse=True)
nzp = P.dict()
for (i, j), z in nzp.items():
    bb = blk(z)
    for di in range(2):
        for dj in range(2):
            if bb[di][dj] != 0: P3[2*i + di, 2*j + dj] = F3(bb[di][dj])
r3 = P3.dense_matrix().rank()
# sanity: block map is a ring hom on F9
assert all(matrix(F3, blk(a*b)) == matrix(F3, blk(a)) * matrix(F3, blk(b)) and matrix(F3, blk(a+b)) == matrix(F3, blk(a)) + matrix(F3, blk(b)) for a in F for b in F)
log("GF(3) block rank", r3, "= 2*rank?", r3 == 2*rk)
# causal simulation, own implementation
def run(xin, Mlist=Ms):
    val = {}  # edge -> value
    for c in C: val[c] = F(0)
    out = {}
    for v in PI:
        known = []
        for k, q in enumerate(inc[v]):
            a, b = edges[q]
            other = b if a == v else a
            if q in Cs: known.append((k, F(0)))
            elif q in Bs and sess[q][0] == v: known.append((k, xin[q]))
            elif q not in Rs and pos[other] < pos[v]: known.append((k, val[q]))
        if len(known) != 5: return ("count", v, len(known))
        Mk = Mlist[v].matrix_from_rows([k for k, _ in known])
        if Mk.det() == 0: return ("singular", v)
        coef = Mk.solve_right(vector(F, [y for _, y in known]))
        allv = Mlist[v] * coef
        for k, q in enumerate(inc[v]):
            a, b = edges[q]; other = b if a == v else a
            if q not in Rs and pos[other] > pos[v]: val[q] = allv[k]
            if q in Bs and sess[q][1] == v: out[q] = allv[k]
            if q in Js: val.setdefault(("J", q), []).append(allv[k])
            if q not in Rs and pos[other] < pos[v] and allv[k] != val[q]: return ("inconsistent", v, q)
    if any(out[q] != xin[q] for q in Bs): return ("decode", sum(out[q] != xin[q] for q in Bs))
    if any(len(set(val[("J", q)])) != 1 for q in Js): return ("Jmismatch",)
    return "ok"
Bl = sorted(Bs)
unit = [run({q: (F(1) if q == q0 else F(0)) for q in Bl}) for q0 in Bl]
log("unit inputs ok", sum(r == "ok" for r in unit), "/", len(Bl))
random.seed(20261102)
elts = list(F)
rnd = [run({q: random.choice(elts) for q in Bl}) for _ in range(200)]
log("random inputs ok", sum(r == "ok" for r in rnd), "/ 200")
# negative control: swap one deleted edge back (restore R[0], delete a physical edge)
Mbad = list(Ms); Mbad[PI[0]] = Ms[PI[0]].with_row_set_to_multiple_of_row(0, 0, t)
log("neg control (first-processed vertex row scaled by t), 20 random:", [run({q: random.choice(elts) for q in Bl}, Mbad) for _ in range(20)])
json.dump({"sess": {str(q): list(v) for q, v in sess.items()}, "dist": {str(q): d for q, d in dist.items()}, "phys": [list(edges[q]) for q in phys]}, open("/tmp/muc9audit/work/graph.json", "w"))
log("done")
