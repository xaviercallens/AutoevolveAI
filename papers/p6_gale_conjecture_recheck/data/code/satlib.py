"""Colouring encodings, proof-logged SAT, drat-trim wrapper, exhaustive DSATUR search."""
from __future__ import annotations

import subprocess
import sys
import time
from typing import Sequence

from pysat.solvers import Solver

DRAT_TRIM = "/home/callensxavier_gmail_com/gale101_thirdparty/drat-trim/drat-trim"
sys.setrecursionlimit(10000)

Edge = tuple[int, int]
Clauses = list[list[int]]


def var(v: int, c: int, k: int) -> int:
    return v * k + c + 1


def encode_a(n: int, edges: Sequence[Edge], k: int, sym: bool = True) -> Clauses:
    """Direct encoding: ALO, pairwise AMO, edge conflicts, optional vertex 0 fixed to colour 0."""
    cl: Clauses = []
    for v in range(n):
        cl.append([var(v, c, k) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                cl.append([-var(v, c1, k), -var(v, c2, k)])
    for u, w in edges:
        for c in range(k):
            cl.append([-var(u, c, k), -var(w, c, k)])
    if sym:
        cl.append([var(0, 0, k)])
    return cl


def encode_b(n: int, edges: Sequence[Edge], k: int) -> Clauses:
    """Alternative encoding: colour = binary-ladder (order) encoding y[v][c] = 'colour(v) <= c'.
    No symmetry breaking. Variables y[v][0..k-2]; colour c holds iff y[v][c] and not y[v][c-1]."""
    def y(v: int, c: int) -> int:
        return v * (k - 1) + c + 1

    cl: Clauses = []
    for v in range(n):
        for c in range(k - 2):
            cl.append([-y(v, c), y(v, c + 1)])  # monotone

    def lit_is(v: int, c: int) -> tuple[list[int], list[int]]:
        """Return (pos, neg) literal lists describing 'colour(v)==c' as conjunction."""
        conj: list[int] = []
        if c < k - 1:
            conj.append(y(v, c))
        if c > 0:
            conj.append(-y(v, c - 1))
        return conj, []

    for u, w in edges:
        for c in range(k):
            a, _ = lit_is(u, c)
            b, _ = lit_is(w, c)
            cl.append([-x for x in a + b])
    return cl


def decode_a(model: Sequence[int], n: int, k: int) -> list[int]:
    s = {x for x in model if x > 0}
    col = []
    for v in range(n):
        cs = [c for c in range(k) if var(v, c, k) in s]
        col.append(cs[0])
    return col


def decode_b(model: Sequence[int], n: int, k: int) -> list[int]:
    s = set(model)
    col = []
    for v in range(n):
        c = 0
        while c < k - 1 and (v * (k - 1) + c + 1) not in s:
            c += 1
        col.append(c)
    return col


def valid_colouring(col: Sequence[int], edges: Sequence[Edge], k: int) -> bool:
    return all(0 <= c < k for c in col) and all(col[u] != col[w] for u, w in edges)


def solve_glucose_proof(cl: Clauses, proof_path: str, cnf_path: str) -> tuple[bool, list[int] | None, float]:
    """Glucose4 with DRUP proof. Writes CNF and proof files. Returns (sat, model, seconds)."""
    nv = max(abs(x) for c in cl for x in c)
    with open(cnf_path, "w") as f:
        f.write(f"p cnf {nv} {len(cl)}\n")
        for c in cl:
            f.write(" ".join(map(str, c)) + " 0\n")
    t = time.time()
    with Solver(name="g4", bootstrap_with=cl, with_proof=True) as s:
        r = s.solve()
        model = s.get_model() if r else None
        proof = s.get_proof() if not r else None
    dt = time.time() - t
    if proof is not None:
        with open(proof_path, "w") as f:
            for line in proof:
                f.write(line.strip() + "\n")
    return r, model, dt


def drat_trim(cnf: str, proof: str, timeout: int = 3000) -> tuple[bool, str]:
    p = subprocess.run([DRAT_TRIM, cnf, proof, "-t", str(timeout)], capture_output=True, text=True)
    out = p.stdout + p.stderr
    return ("s VERIFIED" in out), out


def solve_plain(cl: Clauses, name: str = "cadical195") -> tuple[bool, list[int] | None, float]:
    t = time.time()
    with Solver(name=name, bootstrap_with=cl) as s:
        r = s.solve()
        m = s.get_model() if r else None
    return r, m, time.time() - t


def dsatur_colourable(n: int, edges: Sequence[Edge], k: int, node_limit: int = 10**9) -> tuple[bool | None, list[int] | None, int]:
    """Exhaustive backtracking: DSATUR choice (min domain, then max degree), forward checking,
    colour-symmetry breaking (a vertex may take a new colour only if it is the lowest unused one).
    Returns (colourable, colouring, nodes); None if node_limit hit."""
    adj = [0] * n
    for u, w in edges:
        adj[u] |= 1 << w
        adj[w] |= 1 << u
    nbrs = [[j for j in range(n) if adj[i] >> j & 1] for i in range(n)]
    deg = [len(x) for x in nbrs]
    full = (1 << k) - 1
    col = [-1] * n
    nodes = 0
    sol: list[int] = []

    def rec(dom: list[int], uncol: int, used: int) -> bool | None:
        nonlocal nodes
        if uncol == 0:
            sol[:] = col
            return True
        nodes += 1
        if nodes > node_limit:
            return None
        best = -1
        bs = 99
        for v in range(n):
            if col[v] < 0:
                s = bin(dom[v]).count("1")
                if s < bs or (s == bs and deg[v] > deg[best]):
                    bs, best = s, v
        v = best
        d = dom[v]
        for c in range(k):
            if not d >> c & 1:
                continue
            if c > used:  # only the lowest unused colour (index == used) is allowed as new
                break
            bit = 1 << c
            changed: list[tuple[int, int]] = []
            ok = True
            for w in nbrs[v]:
                if col[w] < 0 and dom[w] & bit:
                    dom[w] &= ~bit
                    changed.append((w, bit))
                    if dom[w] == 0:
                        ok = False
                        break
            if ok:
                col[v] = c
                r = rec(dom, uncol - 1, max(used, c + 1))
                col[v] = -1
                if r is None:
                    for w, b in changed:
                        dom[w] |= b
                    return None
                if r:
                    return True
            for w, b in changed:
                dom[w] |= b
        return False

    dom = [full] * n
    r = rec(dom, n, 0)
    return r, (list(sol) if r else None), nodes
