#!/usr/bin/env python3
"""Exact Lyapunov certificates that the roots of q (rho = (z-1) q) lie strictly inside the unit disc.

For monic q of degree d with companion matrix C (so C v = z v for v = (1, z, .., z^{d-1}) whenever
q(z) = 0), solve  C^T P C - P = -I  EXACTLY over Q for symmetric P, then certify P > 0 by a sum of
squares that ends in the pure coordinate v_0 (so with v_0 = 1 the form is at least the last pivot):
    v^T P v = sum_i d_i (v_i + sum_{j<i} u_ij v_j)^2 ,   d_i > 0 .
If z is a root: (Cv)^* P (Cv) = |z|^2 v^* P v, and (Cv)^* P (Cv) = v^* P v - v^* v, hence
    (1 - |z|^2) v^* P v = v^* v >= 1 .
With v^* P v >= d_0 > 0 this forces |z| < 1. Everything here is exact rational arithmetic.
"""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kge_bdf_pilot import bdf, solve_exact  # noqa: E402


def deflate(a: list[Fraction]) -> list[Fraction] | None:
    """q with  sum a_j z^j = (z - 1) q(z); None if 1 is not a root. Coefficients low-to-high."""
    if sum(a) != 0:
        return None
    n = len(a) - 1
    q = [Fraction(0)] * n
    acc = Fraction(0)
    for i in range(n, 0, -1):
        acc = a[i] + acc
        q[i - 1] = acc
    return q


def companion(q: list[Fraction]) -> list[list[Fraction]]:
    d = len(q) - 1
    c = [[Fraction(0)] * d for _ in range(d)]
    for i in range(d - 1):
        c[i][i + 1] = Fraction(1)
    for j in range(d):
        c[d - 1][j] = -q[j] / q[d]
    return c


def lyapunov(C: list[list[Fraction]]) -> list[list[Fraction]] | None:
    """Exact symmetric P with C^T P C - P = -I."""
    d = len(C)
    idx = [(i, j) for i in range(d) for j in range(i, d)]
    pos = {p: n for n, p in enumerate(idx)}

    def var(i, j):
        return pos[(min(i, j), max(i, j))]

    rows, rhs = [], []
    for (a, b) in idx:
        row = [Fraction(0)] * len(idx)
        for i in range(d):
            for j in range(d):
                if C[i][a] != 0 and C[j][b] != 0:
                    row[var(i, j)] += C[i][a] * C[j][b]
        row[var(a, b)] -= 1
        rows.append(row)
        rhs.append(Fraction(-1) if a == b else Fraction(0))
    sol = solve_exact(rows, rhs)
    if sol is None:
        return None
    P = [[Fraction(0)] * d for _ in range(d)]
    for (i, j), n in pos.items():
        P[i][j] = P[j][i] = sol[n]
    return P


def sos_from_last(P: list[list[Fraction]]):
    """v^T P v = sum_i d_i (v_i + sum_{j<i} u_ij v_j)^2, eliminating v_{d-1} first. None if a pivot <= 0."""
    d = len(P)
    S = [row[:] for row in P]
    ds, us = [None] * d, [None] * d
    for i in range(d - 1, -1, -1):
        piv = S[i][i]
        if piv <= 0:
            return None
        ds[i] = piv
        us[i] = [S[i][j] / piv for j in range(i)]
        for a in range(i):
            for b in range(i):
                S[a][b] -= S[a][i] * S[i][b] / piv
    return ds, us


def certificate(k: int):
    a, _ = bdf(k)
    q = deflate(a)
    if q is None:
        return None
    if len(q) == 1:
        return {"k": k, "d": 0, "q": q, "trivial": True}
    C = companion(q)
    P = lyapunov(C)
    if P is None:
        return {"k": k, "d": len(q) - 1, "q": q, "P": None, "reason": "Lyapunov system singular"}
    sos = sos_from_last(P)
    return {"k": k, "d": len(q) - 1, "q": q, "C": C, "P": P, "sos": sos}


if __name__ == "__main__":
    for k in range(1, 9):
        c = certificate(k)
        if c.get("trivial"):
            print(f"BDF{k}: q is a constant; rho = (z-1)*q, the only root is z = 1")
            continue
        if c["P"] is None:
            print(f"BDF{k}: {c['reason']}")
            continue
        ok = c["sos"] is not None
        print(f"BDF{k}: d={c['d']}  P exact, positive definite (all pivots > 0): {ok}"
              + (f"   min pivot d_0={float(c['sos'][0][0]):.4g}" if ok else "   <-- NO certificate"))
