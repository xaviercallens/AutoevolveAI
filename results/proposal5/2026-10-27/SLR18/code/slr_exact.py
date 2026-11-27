"""Exact checker 1 (Python, integer sweep) for shifted lonely runner certificates.

A certificate is (v, a, D, delta) with s_i = a_i / D and delta = p/q rational.
Claim checked: the OPEN bad arcs B_i = {t in R/Z : ||s_i + v_i t|| < delta}
cover the whole circle R/Z.  Equivalently max_t min_i ||s_i + v_i t|| < delta.

Method (checker 1): every arc endpoint is rational,
    t = (k - s_i -+ delta) / v_i ,
so after multiplying by the common denominator M = lcm(v) * D * q all endpoints
are integers.  The arcs (as integer open intervals on the line, all lifts that
meet [0, M]) are swept greedily: the closed segment [0, M] (a fundamental domain
of the circle, 0 ~ M) is covered by open intervals iff the greedy reach starting
at 0 advances strictly past every point.

Also provided: an exact evaluator of gamma(v; s) = max_t min_i ||s_i + v_i t||
(Fractions, candidate breakpoints), used only for the small positive controls.
"""
from __future__ import annotations

import json
import math
from fractions import Fraction
from typing import Iterable, Sequence


def lcm_list(xs: Iterable[int]) -> int:
    out = 1
    for x in xs:
        out = out * x // math.gcd(out, x)
    return out


def integer_arcs(v: Sequence[int], a: Sequence[int], D: int, dp: int, dq: int) -> tuple[int, list[tuple[int, int]]]:
    """Return (M, arcs) where arcs are open integer intervals (lo, hi) on the
    line, scaled by M, covering every lift of every bad arc that meets [0, M]."""
    L = lcm_list(v)
    M = L * D * dq
    arcs: list[tuple[int, int]] = []
    for vi, ai in zip(v, a):
        f = L // vi  # M / (vi * D * dq) == f
        # t*M = (k*D*dq - ai*dq -+ dp*D) * f
        base = -ai * dq * f
        half = dp * D * f
        step = D * dq * f  # = M / vi
        # centers base + k*step ; need lifts meeting [0, M]
        kmin = (-(base + half)) // step - 1
        kmax = (M - base + half) // step + 1
        for k in range(kmin, kmax + 1):
            c = base + k * step
            lo, hi = c - half, c + half
            if hi > 0 and lo < M:
                arcs.append((lo, hi))
    return M, arcs


def covers_open(v: Sequence[int], a: Sequence[int], D: int, dp: int, dq: int) -> tuple[bool, int, int | None]:
    """Checker 1. Returns (covered, M, first_uncovered_scaled_point_or_None)."""
    if len(set(v)) != len(v) or min(v) <= 0:
        raise ValueError("velocities must be distinct positive integers")
    if not (0 < dp * 2 < dq):
        raise ValueError("need 0 < delta < 1/2")
    M, arcs = integer_arcs(v, a, D, dp, dq)
    arcs.sort()
    cur = 0  # point that must lie strictly inside an arc
    idx = 0
    best = None
    nA = len(arcs)
    while cur <= M:
        # all arcs with lo < cur are candidates; take max hi
        while idx < nA and arcs[idx][0] < cur:
            h = arcs[idx][1]
            if best is None or h > best:
                best = h
            idx += 1
        if best is None or best <= cur:
            return False, M, cur
        cur = best
    return True, M, None


def dist_int(x: Fraction) -> Fraction:
    f = x - math.floor(x)
    return min(f, 1 - f)


def gamma_exact(v: Sequence[int], s: Sequence[Fraction]) -> tuple[Fraction, Fraction]:
    """Exact gamma(v; s) = max_t min_i ||s_i + v_i t|| and an argmax t in [0,1).

    The function F(t) = min_i ||s_i + v_i t|| is piecewise linear; a local max
    of F is either a peak of one runner (s_i + v_i t = 1/2 mod 1) or a crossing
    of two runners' distance graphs: s_i + v_i t = +-(s_j + v_j t) mod 1.
    All these candidate t are enumerated in [0,1) and F is evaluated exactly.
    """
    n = len(v)
    cands: set[Fraction] = set()
    half = Fraction(1, 2)
    for i in range(n):
        for k in range(v[i]):
            cands.add(((half + k - s[i]) / v[i]) % 1)
    for i in range(n):
        for j in range(i + 1, n):
            for w, rhs in ((v[i] - v[j], s[j] - s[i]), (v[i] + v[j], -(s[i] + s[j]))):
                if w == 0:
                    continue
                ww = abs(w)
                r = rhs if w > 0 else -rhs
                # also crossings at the half-integer level are peaks; integer level covers both branches
                for k in range(ww):
                    cands.add(((r + k) / ww) % 1)
                    cands.add(((r + k + half) / ww) % 1)
    best = Fraction(-1)
    arg = Fraction(0)
    for t in cands:
        m = min(dist_int(s[i] + v[i] * t) for i in range(n))
        if m > best:
            best, arg = m, t
    return best, arg


def load_cert(path: str) -> dict:
    with open(path) as fh:
        return json.load(fh)


def check_cert_file(path: str) -> dict:
    c = load_cert(path)
    v = [int(x) for x in c["v"]]
    a = [int(x) for x in c["a"]]
    D = int(c["D"])
    dp, dq = int(c["delta_num"]), int(c["delta_den"])
    n = len(v)
    assert int(c["n"]) == n, "n mismatch"
    assert len(a) == n, "a length mismatch"
    ok, M, bad = covers_open(v, a, D, dp, dq)
    return {"file": path, "n": n, "covered": ok, "M_digits": len(str(M)), "first_uncovered": None if bad is None else str(Fraction(bad, M))}


if __name__ == "__main__":
    import sys

    for p in sys.argv[1:]:
        r = check_cert_file(p)
        print(json.dumps(r))
