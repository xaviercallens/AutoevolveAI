"""Tier X: random search for two positive sinks in every orbit representative (model F, rho free).
Two sinks <=> two downward crossings of h(x)=f(x,phi(x)) (trace<0 always at equilibria, Lemma 3 rederived: f_x,g_y<0)."""
import sys, json, time
import numpy as np
from fractions import Fraction as Fr
from bistab import *
from exact import analyse

part, nparts = int(sys.argv[1]), int(sys.argv[2])
S = int(sys.argv[3])      # samples per network
seed = int(sys.argv[4])
NG = 500
XS = np.logspace(-5, 5, NG)
lab, reps = enumerate_all()
rng = np.random.default_rng(seed)
LO, HI = -3.0, 3.0


def crossings(es, P):
    """P: dict of arrays (S,) a,b,rho,k0..k2 -> number of downward crossings of h per sample."""
    n = len(P["a"])
    X = XS[None, :]
    fc, gc = {}, {}  # coefficient arrays by monomial (p,q)
    def add(d, key, val):
        d[key] = d.get(key, 0) + val
    add(fc, (0, 0), P["a"][:, None] * np.ones_like(X)); add(fc, (1, 0), -P["rho"][:, None] * np.ones_like(X))
    add(gc, (0, 0), P["b"][:, None] * np.ones_like(X)); add(gc, (0, 1), -np.ones((n, NG)))
    for i, e in enumerate(es):
        s, t = EDGES[e]
        k = P[f"k{i}"][:, None] * np.ones_like(X)
        add(fc, CX[s], k * (CX[t][0] - CX[s][0]))
        add(gc, CX[s], k * (CX[t][1] - CX[s][1]))
    def coef_y(d, q):  # coefficient of y^q as function of x
        r = 0
        for (p, qq), v in d.items():
            if qq == q:
                r = r + v * X ** p
        return r
    c0, c1, c2 = coef_y(gc, 0), coef_y(gc, 1), coef_y(gc, 2)
    with np.errstate(all="ignore"):
        disc = c1 * c1 - 4 * c2 * c0
        den = -c1 + np.sqrt(np.maximum(disc, 0))
        sq = np.sqrt(np.maximum(disc, 0))
        phi = np.where(c1 <= 0, 2 * c0 / (-c1 + sq), (c1 + sq) / (-2 * c2))
        ok = np.isfinite(phi) & (phi > 0) & (disc >= 0)
        h = 0
        for (p, qq), v in fc.items():
            h = h + v * X ** p * phi ** qq
        h = np.where(ok, h, np.nan)
    sg = np.sign(h)
    down = (sg[:, :-1] > 0) & (sg[:, 1:] < 0)
    return down.sum(axis=1), h


results = {}
t0 = time.time()
for idx, r in enumerate(reps):
    if idx % nparts != part:
        continue
    m = len(r)
    P = {"a": 10 ** rng.uniform(LO, HI, S), "b": 10 ** rng.uniform(LO, HI, S), "rho": 10 ** rng.uniform(LO, HI, S)}
    for i in range(m):
        P[f"k{i}"] = 10 ** rng.uniform(LO, HI, S)
    nd, _ = crossings(r, P)
    hits = np.where(nd >= 2)[0]
    rec = dict(edges=r, n_samples=S, n_candidate_hits=int(len(hits)), verified=0, unverified=0, verified_examples=[])
    for j in hits[:20]:
        vals = {k: Fr(float(f"{v[j]:.8g}")) for k, v in P.items()}
        res = analyse(r, [vals[f"k{i}"] for i in range(m)], vals["a"], vals["b"], vals["rho"], eps=Fr(1, 10 ** 20))
        if res.get("status") == "ok" and res["n_sinks"] >= 2 and res["undecided"] == 0:
            rec["verified"] += 1
            if len(rec["verified_examples"]) < 1:
                rec["verified_examples"].append({k: str(v) for k, v in vals.items()})
        else:
            rec["unverified"] += 1
    results[idx] = rec
    if idx % 20 == part or len(hits):
        print(idx, r, "cand", rec["n_candidate_hits"], "verified", rec["verified"], round(time.time() - t0), flush=True)
json.dump(results, open(f"../data/p6_search_seed{seed}_part{part}.json", "w"))
