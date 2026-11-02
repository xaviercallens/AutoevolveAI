"""Headline checks A1-A10 for AIC-MUC9 (own code). Run after controls.py."""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
import time
from collections import Counter
from fractions import Fraction

import numpy as np

HERE = "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal6/2026-11-03/AIC-MUC9"
sys.path.insert(0, HERE + "/code")
sys.path.insert(0, "/home/callensxavier_gmail_com/muc9_thirdparty")

from appendixA_transcribed import C, J, PI, R  # noqa: E402
from checks import degree_conditions, distances, trials  # noqa: E402
from muc9lib import (ADD, MUL, NEG, INV, build_T, build_field, build_graph, check_field, dot, local_data,  # noqa: E402
                     parity_matrix, rank, bfs_dist)

t0 = time.time()
res: dict = {}


def log(k: str, v: object) -> None:
    res[k] = v
    print(k, "=", json.dumps(v, default=str)[:600], f"[{time.time()-t0:.0f}s]", flush=True)


# A1
f = check_field(ADD, MUL, NEG, INV)
log("A1_field_axioms", {"checks": {k: bool(v) for k, v in f.items()}, "PASS": all(f.values()),
                        "theta_squared_equals_minus1": bool(MUL[3, 3] == 2)})
# A2
T = build_T()
def normalized(t):
    for c in t:
        if c != 0:
            return c == 1
    return False
allproj = set()
for t in itertools.product(range(9), repeat=3):
    if t != (0, 0, 0):
        s = next(c for c in t if c)
        si = int(INV[s])
        allproj.add(tuple(int(MUL[si, c]) for c in t))
log("A2_T", {"len": len(T), "distinct": len(set(T)) == 91, "all_normalized": all(normalized(t) for t in T),
             "equals_set_of_projective_points": set(T) == allproj, "PASS": len(T) == 91 and set(T) == allproj})
# A3
edges, nbrs = build_graph(T)
deg = Counter()
for a, b in edges:
    deg[a] += 1; deg[b] += 1
pt_lines = [set(n) for n in nbrs]
common = Counter(len(pt_lines[i] & pt_lines[j]) for i in range(91) for j in range(i + 1, 91))
line_pts = [set(i for i in range(91) if j in pt_lines[i]) for j in range(91)]
common_l = Counter(len(line_pts[i] & line_pts[j]) for i in range(91) for j in range(i + 1, 91))
adj_full: list[list[int]] = [[] for _ in range(182)]
for a, b in edges:
    adj_full[a].append(b); adj_full[b].append(a)
# girth: shortest cycle via BFS from every vertex
def girth(adj):
    best = 10**9
    for s in range(len(adj)):
        d = {s: 0}; par = {s: -1}; q = [s]
        for x in q:
            for y in adj[x]:
                if y not in d:
                    d[y] = d[x] + 1; par[y] = x; q.append(y)
                elif par[x] != y:
                    best = min(best, d[x] + d[y] + 1)
    return best
g6 = girth(adj_full)
log("A3_PG29", {"V": 182, "E": len(edges), "all_degree_10": all(deg[v] == 10 for v in range(182)),
                "two_points_common_lines": dict(common), "two_lines_common_points": dict(common_l), "girth": g6,
                "PASS": len(edges) == 910 and all(deg[v] == 10 for v in range(182)) and set(common) == {1}
                and set(common_l) == {1} and g6 == 6})
# A4
Rs, Cs, Js = set(R), set(C), set(J)
B = [q for q in R if q not in Cs and q not in Js]
log("A4_lists", {"R_len": len(R), "R_distinct": len(Rs) == 175, "R_in_range": all(0 <= q < 910 for q in R),
                 "C_J_disjoint_subsets": bool(Cs <= Rs and Js <= Rs and not (Cs & Js) and len(C) == 9 and len(J) == 9),
                 "B_len": len(B), "pi_is_permutation": sorted(PI) == list(range(182)),
                 "PASS": len(Rs) == 175 and len(R) == 175 and len(B) == 157 and sorted(PI) == list(range(182))
                 and Cs <= Rs and Js <= Rs and not (Cs & Js)})
# A5
dc = degree_conditions(edges, R, PI, C, J)
log("A5_degrees", {"E_after_deletion": 910 - len(R), "bad_degree_vertices": dc["bad_degree"], "bad_C_J_vertices": dc["bad_cj"],
                   "PASS": (910 - len(R) == 735) and not dc["bad_degree"] and not dc["bad_cj"]})
# local codes
inc, Ms, Hs = local_data(T, edges)
mds = True; bad = 0
for v in range(182):
    assert rank(Ms[v]) == 5 and Hs[v].shape == (5, 10)
    for h in Hs[v]:
        for r in range(5):
            s = 0
            for k in range(10):
                s = int(ADD[s, MUL[h[k], Ms[v][k, r]]])
            assert s == 0
    for sub in itertools.combinations(range(10), 5):
        if rank(Ms[v][list(sub)]) != 5:
            mds = False; bad += 1
log("A6_local_codes", {"each_rank5": True, "parity_checks_annihilate": True, "MDS_all_252_subsets_all_182_vertices": mds,
                       "bad_subsets": bad, "PASS": mds})
# A7
P = parity_matrix(inc, Hs)
rk = rank(P)
dimW = 910 - rk
cols_noC = [q for q in range(910) if q not in Cs]
dimWC = len(cols_noC) - rank(P[:, cols_noC])
cols_free = [q for q in range(910) if q not in Cs and q not in set(B)]  # physical + J
rk_free = rank(P[:, cols_free])
log("A7_rank", {"P_shape": list(P.shape), "rank_P": rk, "dim_W": dimW, "dim_W_C": dimWC,
                "restriction_to_B_injective": bool(rk_free == len(cols_free)), "free_cols": len(cols_free), "rank_free": rk_free,
                "PASS": dimW >= 166 and dimWC >= 157 and rk_free == len(cols_free)})
# A8
tr = trials(edges, inc, Ms, Hs, R, PI, C, J, 1000, 12345)
log("A8_causal_trials", {**tr, "PASS": tr["ok"] == tr["trials"]})
# also all-basis-vector inputs (spans linear code): 157 unit inputs + zero
ok_basis = 0
from muc9lib import causal_run  # noqa: E402
for q0 in B:
    x = {q: (1 if q == q0 else 0) for q in B}
    r = causal_run(edges, inc, Ms, Hs, R, PI, C, J, x)
    ok_basis += (not r["fails"]) and r["decode_ok"] and r["in_W"]
log("A8b_unit_inputs", {"unit_vectors_ok": ok_basis, "of": len(B), "PASS": ok_basis == len(B)})
# A9
dd = distances(edges, R, PI, C, J)
dist = [v[2] for v in dd["pairs"].values()]
log("A9_distances", {"pairs": len(dist), "min": min(dist), "histogram": dict(Counter(dist)), "sum": sum(dist),
                     "all_odd": all(d % 2 == 1 for d in dist), "PASS": min(dist) >= 5 and len(dist) == 157})
# A10
bound = Fraction(735, 785)
S = sum(dist)
log("A10_flow_bound", {"E": 735, "sessions": 157, "sum_dist": S, "bound_735_over_sumdist": str(Fraction(735, S)),
                       "735_over_785": str(bound), "equals_147_over_157": bound == Fraction(147, 157),
                       "735_lt_785": 735 < 785, "PASS": bound == Fraction(147, 157) and S >= 785})
# hashes
def h(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=lambda o: o.tolist()).encode()).hexdigest()
phys_edges = [list(edges[q]) for q in range(910) if q not in Rs]
res["hashes"] = {
    "T_ordered": h(T), "candidate_edges_910": h(edges), "physical_edges_735": h(phys_edges),
    "R_list": h(R), "pi_list": h(PI), "C": h(C), "J": h(J),
    "local_eval_matrices": h([m.tolist() for m in Ms]), "local_parity_checks": h([x.tolist() for x in Hs]),
    "sessions_B_endpoints": h({str(q): list(v) for q, v in dd["pairs"].items()}),
}
res["ALL_A1_A10_PASS"] = all(res[k]["PASS"] for k in res if k.startswith("A") and isinstance(res[k], dict) and "PASS" in res[k])
print(json.dumps(res["hashes"], indent=1))
print("ALL_A1_A10_PASS", res["ALL_A1_A10_PASS"])
json.dump(res, open(HERE + "/data/main_results.json", "w"), indent=1, default=str)
json.dump({str(q): v for q, v in dd["pairs"].items()}, open("/home/callensxavier_gmail_com/muc9_thirdparty/sessions_B_derived.json", "w"))
