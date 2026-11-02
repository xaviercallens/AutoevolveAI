from __future__ import annotations

import random
from typing import Optional

import numpy as np

from muc9lib import bfs_dist, causal_run


def degree_conditions(edges: list[tuple[int, int]], R: list[int], PI: list[int], C: list[int], J: list[int]) -> dict:
    """Orientation on all 910 candidate edges: physical earlier->later, deleted later->earlier.
    Returns violations of d-=d+=5 and d+_C = d-_J."""
    pos = {v: i for i, v in enumerate(PI)}
    Rs, Cs, Js = set(R), set(C), set(J)
    din = [0] * 182; dout = [0] * 182; dcout = [0] * 182; djin = [0] * 182
    for q, (a, b) in enumerate(edges):
        early, late = (a, b) if pos[a] < pos[b] else (b, a)
        if q in Rs:
            tail, head = late, early
        else:
            tail, head = early, late
        dout[tail] += 1; din[head] += 1
        if q in Cs:
            dcout[tail] += 1
        if q in Js:
            djin[head] += 1
    bad_deg = [v for v in range(182) if din[v] != 5 or dout[v] != 5]
    bad_cj = [v for v in range(182) if dcout[v] != djin[v]]
    return {"bad_degree": bad_deg, "bad_cj": bad_cj}


def distances(edges: list[tuple[int, int]], R: list[int], PI: list[int], C: list[int], J: list[int]) -> dict:
    pos = {v: i for i, v in enumerate(PI)}
    Rs = set(R)
    adj: list[list[int]] = [[] for _ in range(182)]
    for q, (a, b) in enumerate(edges):
        if q not in Rs:
            adj[a].append(b); adj[b].append(a)
    B = [q for q in R if q not in set(C) and q not in set(J)]
    ds = {}
    for q in B:
        a, b = edges[q]
        s, t = (a, b) if pos[a] < pos[b] else (b, a)
        ds[q] = (s, t, bfs_dist(adj, s)[t])
    return {"B": B, "pairs": ds, "adj": adj}


def trials(edges, inc, Ms, Hs, R, PI, C, J, n: int, seed: int, perturb: Optional[tuple[int, int]] = None) -> dict:
    rng = random.Random(seed)
    B = [q for q in R if q not in set(C) and q not in set(J)]
    nfail_struct = 0; ndec = 0; nW = 0; nok = 0
    first_fail = None
    for _ in range(n):
        x = {q: rng.randrange(9) for q in B}
        res = causal_run(edges, inc, Ms, Hs, R, PI, C, J, x, perturb)
        s = bool(res["fails"])
        nfail_struct += s
        ndec += (not res["decode_ok"]); nW += (not res["in_W"])
        if not s and res["decode_ok"] and res["in_W"]:
            nok += 1
        elif first_fail is None:
            first_fail = res["fails"][:3]
    return {"trials": n, "structural_fail": nfail_struct, "decode_fail": ndec, "not_in_W": nW, "ok": nok,
            "first_fail": first_fail}
