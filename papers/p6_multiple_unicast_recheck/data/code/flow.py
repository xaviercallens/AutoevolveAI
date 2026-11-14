"""Max concurrent multicommodity flow LP (unit capacities), sessions grouped by source (exact for flow)."""
from __future__ import annotations

from collections import defaultdict

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


def max_concurrent(nv: int, edges: list[tuple[int, int]], directed: bool, sessions: list[tuple[int, int, float]],
                   time_limit: float = 1500.0) -> tuple[float, str]:
    """Return (lambda, status). Undirected edges: both directions share capacity 1."""
    groups: dict[int, dict[int, float]] = defaultdict(lambda: defaultdict(float))
    for s, t, d in sessions:
        groups[s][t] += d
    gl = sorted(groups)
    arcs: list[tuple[int, int, int]] = []  # (u, v, edge_id)
    for e, (u, v) in enumerate(edges):
        arcs.append((u, v, e))
        if not directed:
            arcs.append((v, u, e))
    na, ng = len(arcs), len(gl)
    nvar = ng * na + 1
    lam = nvar - 1
    rows, cols, vals = [], [], []
    for gi, s in enumerate(gl):
        base = gi * na
        for ai, (u, v, _) in enumerate(arcs):
            rows += [gi * nv + u, gi * nv + v]
            cols += [base + ai, base + ai]
            vals += [1.0, -1.0]
        tot = sum(groups[s].values())
        rows.append(gi * nv + s); cols.append(lam); vals.append(-tot)
        for t, d in groups[s].items():
            rows.append(gi * nv + t); cols.append(lam); vals.append(d)
    Aeq = coo_matrix((vals, (rows, cols)), shape=(ng * nv, nvar)).tocsr()
    beq = np.zeros(ng * nv)
    r2, c2, v2 = [], [], []
    for gi in range(ng):
        for ai, (_, _, e) in enumerate(arcs):
            r2.append(e); c2.append(gi * na + ai); v2.append(1.0)
    Aub = coo_matrix((v2, (r2, c2)), shape=(len(edges), nvar)).tocsr()
    bub = np.ones(len(edges))
    c = np.zeros(nvar); c[lam] = -1.0
    res = linprog(c, A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=beq, bounds=(0, None), method="highs",
                  options={"time_limit": time_limit})
    return (float(-res.fun) if res.status == 0 else float("nan")), str(res.message)
