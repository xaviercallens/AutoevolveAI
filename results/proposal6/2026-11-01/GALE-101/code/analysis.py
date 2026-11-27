"""Minimal critical subgraph, edge-deletion control (N2), threshold sweep (N1), perturbation (N3), random subsets (N4),
tetrahedral partition sanity check (Tier X). usage: python analysis.py <data_dir> <work_dir> <out_json>"""
from __future__ import annotations

import itertools
import json
import math
import os
import random
import sys
from fractions import Fraction

import satlib as S

Edge = tuple[int, int]


def colourable(n: int, edges: list[Edge], k: int = 4) -> bool:
    r, m, _ = S.solve_plain(S.encode_a(n, edges, k, sym=False), "cadical195")
    if r:
        assert S.valid_colouring(S.decode_a(m, n, k), edges, k)
    return r


def mus(n: int, edges: list[Edge]) -> list[Edge]:
    """Deletion-based minimal unsatisfiable edge set (graph minimal non-4-colourable), starting from unsat `edges`."""
    cur = list(edges)
    rng = random.Random(1)
    rng.shuffle(cur)
    i = 0
    while i < len(cur):
        trial = cur[:i] + cur[i + 1 :]
        if not colourable(n, trial):
            cur = trial
        else:
            i += 1
    return cur


def main() -> None:
    data, work, outj = sys.argv[1:4]
    pts = [tuple(p) for p in json.load(open(os.path.join(data, "points_scaled1e7.json")))]
    edges = [tuple(e) for e in json.load(open(os.path.join(data, "edges_088928.json")))]
    n = 101
    res: dict = {}
    d2 = {(i, j): sum((a - b) ** 2 for a, b in zip(pts[i], pts[j])) for i, j in itertools.combinations(range(n), 2)}
    D2 = max(d2.values())

    # minimal critical subgraph
    core = mus(n, edges)
    verts = sorted({v for e in core for v in e})
    res["mus_edges"] = len(core)
    res["mus_vertices"] = len(verts)
    res["mus_edge_list"] = sorted(core)
    res["mus_min_degree"] = min(sum(1 for e in core if v in e) for v in verts)
    # N2: every single edge deletion makes it 4-colourable (exact validated colouring)
    res["N2_all_single_deletions_colourable"] = all(colourable(n, [e for e in core if e != x]) for x in core)
    # re-certify core with a proof-logged solver
    cl = S.encode_a(n, core, 4, sym=True)
    cnf, prf = os.path.join(work, "core_k4.cnf"), os.path.join(work, "core_k4.drup")
    sat, _, _ = S.solve_glucose_proof(cl, prf, cnf)
    ok, txt = S.drat_trim(cnf, prf)
    res["core_glucose_sat"] = sat
    res["core_drat_trim_verified"] = ok
    ds, _, nodes = S.dsatur_colourable(n, core, 4)
    res["core_dsatur_colourable"] = ds
    res["core_dsatur_nodes"] = nodes
    # minimal ratio of core edges
    core_ratios = sorted(math.sqrt(d2[e] / D2) for e in core)
    res["core_min_edge_ratio"] = core_ratios[0]
    json.dump(res, open(outj, "w"), indent=1)
    print("MUS", len(core), len(verts), res["N2_all_single_deletions_colourable"], ok, flush=True)

    # N1: threshold sweep, exact comparison on integers with rational thresholds t = a/10^6
    sweep = {}
    for tnum in (888000, 888073, 889000, 889280, 889281, 889282, 889300, 889500, 890000, 892000, 895000, 900000):
        e = [x for x, v in d2.items() if v * 10**12 > tnum**2 * D2]
        sweep[str(Fraction(tnum, 10**6))] = {"edges": len(e), "four_colourable": colourable(n, e)}
    res["N1_threshold_sweep"] = sweep
    # exact critical threshold: sort edges by ratio descending; the smallest prefix that is non-4-colourable
    order = sorted(d2.items(), key=lambda kv: -kv[1])
    lo, hi = 0, len(order)  # find minimal m with prefix[:m] non-colourable
    while lo < hi:
        mid = (lo + hi) // 2
        if colourable(n, [k for k, _ in order[:mid]]):
            lo = mid + 1
        else:
            hi = mid
    res["critical_prefix_len"] = lo
    res["critical_last_edge_ratio"] = math.sqrt(order[lo - 1][1] / D2)
    res["critical_next_ratio"] = math.sqrt(order[lo][1] / D2)
    res["prefix_before_colourable"] = colourable(n, [k for k, _ in order[: lo - 1]])
    res["prefix_at_critical_colourable"] = colourable(n, [k for k, _ in order[:lo]])
    json.dump(res, open(outj, "w"), indent=1)
    print("critical", lo, res["critical_last_edge_ratio"], flush=True)

    # N3: perturb one coordinate by +-1e-3 (units 1e4 of 1e-7) ; delete one point
    rng = random.Random(7)
    pert = []
    for t in range(20):
        p = [list(x) for x in pts]
        i = rng.randrange(n)
        a = rng.randrange(3)
        p[i][a] += rng.choice((-1, 1)) * 10_000
        pp = [tuple(x) for x in p]
        dd = {(i2, j2): sum((a2 - b2) ** 2 for a2, b2 in zip(pp[i2], pp[j2])) for i2, j2 in itertools.combinations(range(n), 2)}
        DD = max(dd.values())
        e = [x for x, v in dd.items() if v * 10**10 > 88928**2 * DD]
        pert.append({"point": i, "axis": a, "edges": len(e), "four_colourable": colourable(n, e)})
    res["N3_perturb_1e-3"] = pert
    dels = []
    for i in range(n):
        keep = [x for x in edges if i not in x]
        # relabel unnecessary: colourability unaffected by an isolated vertex
        dels.append(colourable(n, keep))
    res["N3_delete_point_four_colourable_count"] = sum(dels)
    res["N3_delete_point_total"] = n

    # N4: random 60-subsets of vertices, induced subgraph on claimed edge set
    cnt = 0
    contains_core = 0
    cs = set(verts)
    for s in range(50):
        sub = set(rng.sample(range(n), 60))
        e = [x for x in edges if x[0] in sub and x[1] in sub]
        c = colourable(n, e)
        cnt += c
        contains_core += cs <= sub
    res["N4_random60_four_colourable"] = cnt
    res["N4_random60_total"] = 50
    res["N4_random60_containing_mus_vertices"] = contains_core

    # Tier X: tetrahedral partition of the unit-diameter sphere (radius 1/2). Analytic part diameter =
    # distance from a spherical-triangle vertex to the midpoint (on the sphere) of the opposite side; plus a sampled check.
    import numpy as np
    r = 0.5
    V = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], float)
    V = r * V / np.linalg.norm(V, axis=1)[:, None]
    mid = V[1] + V[2]
    mid = r * mid / np.linalg.norm(mid)
    res["X_analytic_part_diameter"] = float(np.linalg.norm(V[0] - mid))
    rs = np.random.default_rng(3)
    X = rs.normal(size=(200000, 3))
    X = r * X / np.linalg.norm(X, axis=1)[:, None]
    part = np.argmax(X @ V.T, axis=1)
    md = 0.0
    for c in range(4):
        P = X[part == c][:2500]
        md = max(md, float(np.max(np.linalg.norm(P[:, None, :] - P[None, :, :], axis=2))))
    res["X_tetra_partition_max_part_diameter_sampled_lowerbound"] = md
    res["X_sigma3"] = math.sqrt((3 + math.sqrt(3)) / 6)
    json.dump(res, open(outj, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "mus_edge_list"}, indent=1, default=str))


if __name__ == "__main__":
    main()
