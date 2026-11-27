"""Independent GF(9) / PG(2,9) / causal-code recheck library for arXiv 2610.10108.
Own code; the authors' repository is not used. Elements of F9 = F3[t]/(t^2+c) are ints a+3b (a+b*t)."""
from __future__ import annotations

import hashlib
import itertools
from collections import deque
from typing import Optional

import numpy as np


def build_field(rel: int = 2) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Tables (ADD, MUL, NEG, INV) for F3[t]/(t^2 + c) with t^2 = -c; rel=1 gives t^2 = -1 (paper: t^2+1)."""
    # t^2 = -c mod 3 where c = rel_c; paper: c=1, t^2 = -1 = 2.
    t2 = (-rel) % 3
    add = np.zeros((9, 9), dtype=np.uint8)
    mul = np.zeros((9, 9), dtype=np.uint8)
    for x in range(9):
        a, b = x % 3, x // 3
        for y in range(9):
            c, d = y % 3, y // 3
            add[x, y] = ((a + c) % 3) + 3 * ((b + d) % 3)
            # (a+bt)(c+dt) = ac + (ad+bc)t + bd t^2
            re = (a * c + b * d * t2) % 3
            im = (a * d + b * c) % 3
            mul[x, y] = re + 3 * im
    neg = np.array([((-(x % 3)) % 3) + 3 * ((-(x // 3)) % 3) for x in range(9)], dtype=np.uint8)
    inv = np.zeros(9, dtype=np.uint8)
    for x in range(1, 9):
        for y in range(1, 9):
            if mul[x, y] == 1:
                inv[x] = y
    return add, mul, neg, inv


ADD, MUL, NEG, INV = build_field(1)


def check_field(add: np.ndarray, mul: np.ndarray, neg: np.ndarray, inv: np.ndarray) -> dict[str, bool]:
    """Exact verification of field axioms on all triples (9^3 = 729)."""
    r = range(9)
    res: dict[str, bool] = {}
    res["add_assoc"] = all(add[add[a, b], c] == add[a, add[b, c]] for a in r for b in r for c in r)
    res["mul_assoc"] = all(mul[mul[a, b], c] == mul[a, mul[b, c]] for a in r for b in r for c in r)
    res["distrib"] = all(mul[a, add[b, c]] == add[mul[a, b], mul[a, c]] for a in r for b in r for c in r)
    res["comm"] = all(add[a, b] == add[b, a] and mul[a, b] == mul[b, a] for a in r for b in r)
    res["add_id_neg"] = all(add[a, 0] == a and add[a, neg[a]] == 0 for a in r)
    res["mul_id"] = all(mul[a, 1] == a for a in r)
    res["no_zero_divisors"] = all(mul[a, b] != 0 for a in range(1, 9) for b in range(1, 9))
    res["inverses"] = all(mul[a, inv[a]] == 1 for a in range(1, 9))
    # multiplicative group cyclic of order 8: find generator
    def order(g: int) -> int:
        x, n = g, 1
        while x != 1:
            x = int(mul[x, g]); n += 1
            if n > 9:
                return 99
        return n
    res["cyclic_order8"] = any(order(g) == 8 for g in range(1, 9)) if res["no_zero_divisors"] else False
    res["char3"] = all(add[add[a, a], a] == 0 for a in r)
    return res


def dot(x: tuple[int, int, int], y: tuple[int, int, int]) -> int:
    s = 0
    for a, b in zip(x, y):
        s = int(ADD[s, MUL[a, b]])
    return s


def build_T() -> list[tuple[int, int, int]]:
    """Ordered list of 91 normalized triples exactly as in the paper (eta_r = r code)."""
    T = [(0, 0, 1)]
    for r in range(9):
        T.append((0, 1, r))
    for r in range(9):
        for s in range(9):
            T.append((1, r, s))
    return T


def build_graph(T: list[tuple[int, int, int]]) -> tuple[list[tuple[int, int]], list[list[int]]]:
    """Candidate edges e_{10i+r} = (i, 91+j_{i,r}) with neighbours increasing; returns edges and line lists."""
    edges: list[tuple[int, int]] = []
    nbrs: list[list[int]] = []
    for i, p in enumerate(T):
        js = [j for j, l in enumerate(T) if dot(p, l) == 0]
        nbrs.append(js)
        for j in js:
            edges.append((i, 91 + j))
    return edges, nbrs


def rref(M: np.ndarray) -> tuple[np.ndarray, list[int]]:
    """Reduced row echelon form over F9 (vectorised row ops)."""
    A = M.copy()
    rows, cols = A.shape
    piv: list[int] = []
    r = 0
    for c in range(cols):
        if r >= rows:
            break
        nz = np.nonzero(A[r:, c])[0]
        if nz.size == 0:
            continue
        p = r + int(nz[0])
        if p != r:
            A[[r, p]] = A[[p, r]]
        A[r] = MUL[INV[A[r, c]], A[r]]
        f = A[:, c].copy()
        f[r] = 0
        idx = np.nonzero(f)[0]
        if idx.size:
            sub = MUL[NEG[f[idx]][:, None], A[r][None, :]]
            A[idx] = ADD[A[idx], sub]
        piv.append(c)
        r += 1
    return A, piv


def rank(M: np.ndarray) -> int:
    return len(rref(M)[1])


def nullspace(M: np.ndarray) -> np.ndarray:
    """Basis (rows) of {x : M x = 0}."""
    A, piv = rref(M)
    n = M.shape[1]
    free = [c for c in range(n) if c not in set(piv)]
    out = np.zeros((len(free), n), dtype=np.uint8)
    for k, fcol in enumerate(free):
        out[k, fcol] = 1
        for ri, pc in enumerate(piv):
            out[k, pc] = NEG[A[ri, fcol]]
    return out


def mpow(x: int, n: int) -> int:
    r = 1
    for _ in range(n):
        r = int(MUL[r, x])
    return r


def local_data(T: list[tuple[int, int, int]], edges: list[tuple[int, int]], renorm_bug: Optional[int] = None, scale_bug: Optional[int] = None) -> tuple[list[list[int]], list[np.ndarray], list[np.ndarray]]:
    """For each vertex v: incident edge indices, evaluation matrix Mv (10x5), parity check Hv (5x10).
    renorm_bug: if given, vertex index whose (lambda,mu) are renormalised (negative control)."""
    inc: list[list[int]] = [[] for _ in range(182)]
    for q, (a, b) in enumerate(edges):
        inc[a].append(q)
        inc[b].append(q)
    Ms: list[np.ndarray] = []
    Hs: list[np.ndarray] = []
    for v in range(182):
        z = T[v % 91 if v >= 91 else v]
        ortho = [y for y in T if dot(z, y) == 0]
        u, w = ortho[0], ortho[1]
        M = np.zeros((10, 5), dtype=np.uint8)
        for k, q in enumerate(inc[v]):
            a, b = edges[q]
            other = b - 91 if v == a else a
            y = T[other]
            found = None
            for lam in range(9):
                for mu in range(9):
                    cand = tuple(int(ADD[MUL[lam, u[c]], MUL[mu, w[c]]]) for c in range(3))
                    if cand == y:
                        found = (lam, mu)
            assert found is not None
            lam, mu = found
            if renorm_bug is not None and v == renorm_bug:
                s = lam if lam != 0 else mu
                si = int(INV[s]); lam = int(MUL[lam, si]); mu = int(MUL[mu, si])
            if v >= 91:  # line vertex: cube
                lam, mu = mpow(lam, 3), mpow(mu, 3)
            for r in range(5):
                M[k, r] = MUL[mpow(lam, 4 - r), mpow(mu, r)]
        if scale_bug is not None and v == scale_bug:
            M[0] = MUL[3, M[0]]
        Ms.append(M)
        Hs.append(nullspace(M.T.copy()))  # rows h with h . M[:,r] = 0 for all r
    return inc, Ms, Hs


def parity_matrix(inc: list[list[int]], Hs: list[np.ndarray]) -> np.ndarray:
    rows = []
    for v in range(182):
        for h in Hs[v]:
            row = np.zeros(910, dtype=np.uint8)
            row[inc[v]] = h
            rows.append(row)
    return np.array(rows, dtype=np.uint8)


def bfs_dist(adj: list[list[int]], s: int) -> list[int]:
    d = [-1] * len(adj)
    d[s] = 0
    dq = deque([s])
    while dq:
        x = dq.popleft()
        for y in adj[x]:
            if d[y] < 0:
                d[y] = d[x] + 1
                dq.append(y)
    return d


def solve_known(M: np.ndarray, known: list[int], fvals: list[int]) -> Optional[np.ndarray]:
    """Given 5 known positions and values, return the full codeword (len 10) or None if the 5x5 is singular."""
    sub = M[known]
    aug = np.concatenate([sub, np.array(fvals, dtype=np.uint8)[:, None]], axis=1)
    A, piv = rref(aug)
    if piv != [0, 1, 2, 3, 4]:
        return None
    coef = A[:5, 5]
    out = np.zeros(10, dtype=np.uint8)
    for k in range(10):
        s = 0
        for r in range(5):
            s = int(ADD[s, MUL[M[k, r], coef[r]]])
        out[k] = s
    return out


def causal_run(edges: list[tuple[int, int]], inc: list[list[int]], Ms: list[np.ndarray], Hs: list[np.ndarray],
               R: list[int], PI: list[int], C: list[int], J: list[int], x: dict[int, int],
               perturb: Optional[tuple[int, int]] = None) -> dict:
    """Run the pi-ordered interpolation. Returns dict with fail reasons, decode correctness, final-assignment check.
    perturb=(edge, delta): add delta to the value sent on that physical edge (negative control)."""
    pos = {v: i for i, v in enumerate(PI)}
    Rs, Cs, Js = set(R), set(C), set(J)
    Bs = [q for q in R if q not in Cs and q not in Js]
    val: dict[int, int] = {}
    outputs: dict[int, int] = {}
    fails: list[str] = []
    for v in PI:
        known_pos: list[int] = []
        known_val: list[int] = []
        for k, q in enumerate(inc[v]):
            a, b = edges[q]
            other = b if v == a else a
            earlier = pos[v] < pos[other]  # v earlier than other
            if q not in Rs:
                if not earlier:  # incoming physical
                    if q not in val:
                        fails.append(f"v{v}: incoming physical edge {q} not yet computed")
                        continue
                    known_pos.append(k); known_val.append(val[q])
            else:
                # deleted edge oriented later->earlier: v earlier => head (incoming); v later => tail (outgoing)
                if q in Cs:
                    known_pos.append(k); known_val.append(0)
                elif q in Js:
                    pass  # unknown at both ends at this time; computed by later endpoint
                else:
                    if earlier:  # source side: knows x_q
                        known_pos.append(k); known_val.append(x[q])
        if len(known_pos) != 5:
            fails.append(f"v{v}: {len(known_pos)} known values (need 5)")
            continue
        cw = solve_known(Ms[v], known_pos, known_val)
        if cw is None:
            fails.append(f"v{v}: singular 5x5 interpolation system")
            continue
        for k, q in enumerate(inc[v]):
            a, b = edges[q]
            other = b if v == a else a
            earlier = pos[v] < pos[other]
            if q not in Rs and earlier:
                t = int(cw[k])
                if perturb is not None and perturb[0] == q:
                    t = int(ADD[t, perturb[1]])
                val[q] = t
            elif q in Rs and not earlier:
                if q in Js:
                    val[q] = int(cw[k])
                elif q not in Cs:
                    outputs[q] = int(cw[k])
    decode_ok = all(outputs.get(q) == x[q] for q in Bs)
    # final assignment W-membership
    full = np.zeros(910, dtype=np.uint8)
    complete = True
    for q in range(910):
        if q in Cs:
            full[q] = 0
        elif q in Bs:
            full[q] = x[q]
        elif q in val:
            full[q] = val[q]
        else:
            complete = False
    inW = False
    if complete:
        inW = True
        for v in range(182):
            f = full[inc[v]]
            for h in Hs[v]:
                s = 0
                for hh, ff in zip(h, f):
                    s = int(ADD[s, MUL[hh, ff]])
                if s != 0:
                    inW = False
                    break
            if not inW:
                break
    return {"fails": fails, "decode_ok": bool(decode_ok), "complete": complete, "in_W": bool(inW), "assignment": full}


def sha(obj: object) -> str:
    return hashlib.sha256(repr(obj).encode()).hexdigest()
