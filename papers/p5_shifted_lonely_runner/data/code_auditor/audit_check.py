#!/usr/bin/env python3
"""Independent auditor checker for shifted-lonely-runner covering certificates.

Method A: exact interval subtraction with fractions.Fraction on [0,1] (circle, t in R/Z since v integer).
  Uncovered set starts as the closed interval [0,1]; each open arc (c-r, c+r) (all integer translates
  meeting [0,1]) is removed; covered iff nothing remains (closed pieces, including single points, count).
Method B: exact gamma(v;s) = max_t min_i ||s_i + v_i t|| by enumerating every candidate maximiser
  (pairwise crossings s_i+v_i t = +-(s_j+v_j t) mod 1 and single-runner peaks at 1/2), integer arithmetic.
Open arcs of radius delta cover iff gamma < delta.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from math import ceil, floor


def validate(cert: dict) -> list[str]:
    errs: list[str] = []
    n, v, a, D = cert["n"], cert["v"], cert["a"], cert["D"]
    if len(v) != n or len(a) != n:
        errs.append("length mismatch")
    if any((not isinstance(x, int)) or x <= 0 for x in v):
        errs.append("non-positive or non-int velocity")
    if len(set(v)) != len(v):
        errs.append("repeated velocity")
    if not isinstance(D, int) or D <= 0:
        errs.append("bad D")
    if "s" in cert:
        for ai, si in zip(a, cert["s"]):
            if F(si) != F(ai, D):
                errs.append(f"s string {si} != {ai}/{D}")
    if "delta_num" in cert and F(cert["delta_num"], cert["delta_den"]) != F(1, n + 1):
        errs.append("delta != 1/(n+1)")
    return errs


def cover_A(v: list[int], s: list[F], delta: F) -> tuple[bool, list[tuple[F, F]]]:
    unc: list[tuple[F, F]] = [(F(0), F(1))]
    for vi, si in zip(v, s):
        r = delta / vi
        kmin = floor(si - delta) - 1
        kmax = ceil(si + vi + delta) + 1
        for k in range(kmin, kmax + 1):
            c = (k - si) / vi
            lo, hi = c - r, c + r
            if hi <= 0 or lo >= 1:
                continue
            new: list[tuple[F, F]] = []
            for (x, y) in unc:
                if hi <= x or lo >= y:
                    new.append((x, y))
                    continue
                if x <= lo:
                    new.append((x, lo))
                if hi <= y:
                    new.append((hi, y))
            unc = new
            if not unc:
                return True, []
    return (len(unc) == 0), unc


def evalt(v: list[int], a: list[int], D: int, t: F) -> F:
    p, Q = t.numerator, t.denominator
    den = D * Q
    m = den
    for vm, am in zip(v, a):
        num = (am * Q + vm * p * D) % den
        d = min(num, den - num)
        if d < m:
            m = d
    return F(m, den)


def gamma_B(v: list[int], a: list[int], D: int) -> tuple[F, F]:
    n = len(v)
    best, arg = F(-1), F(0)
    seen: set[F] = set()

    def consider(p: int, Q: int) -> None:
        nonlocal best, arg
        t = F(p, Q) % 1
        if t in seen:
            return
        seen.add(t)
        val = evalt(v, a, D, t)
        if val > best:
            best, arg = val, t

    for i in range(n):
        for k in range(-1, v[i] + 1):
            consider(2 * k * D + D - 2 * a[i], 2 * D * v[i])
        for j in range(i + 1, n):
            for sgn in (1, -1):
                w = v[i] + sgn * v[j]
                if w == 0:
                    continue
                for k in range(-abs(w) - 3, abs(w) + 4):
                    p = k * D - (a[i] + sgn * a[j])
                    consider(p, D * w)
    return best, arg


def check(cert: dict, do_gamma: bool = True) -> dict:
    errs = validate(cert)
    n, v, a, D = cert["n"], cert["v"], cert["a"], cert["D"]
    delta = F(cert.get("delta_num", 1), cert.get("delta_den", n + 1))
    s = [F(x, D) for x in a]
    if any((not isinstance(x, int)) or x <= 0 for x in v):
        return {"n": n, "valid": False, "errs": errs, "coverA": None, "coverB": None}
    covA, unc = cover_A(v, s, delta)
    out: dict = {"n": n, "valid": not errs, "errs": errs, "delta": str(delta), "coverA": covA,
                 "uncovered_sample": [(str(x), str(y)) for x, y in unc[:3]]}
    if do_gamma:
        g, t = gamma_B(v, a, D)
        out.update({"gamma": str(g), "argmax": str(t), "coverB": g < delta,
                    "E_lower": float(1 / g - (n + 1)) if g > 0 else None})
    return out


if __name__ == "__main__":
    import os
    paths: list[str] = []
    for arg in sys.argv[1:]:
        if os.path.isdir(arg):
            paths += sorted(os.path.join(arg, f) for f in os.listdir(arg) if f.endswith(".json"))
        else:
            paths.append(arg)
    for path in paths:
        with open(path) as fh:
            cert = json.load(fh)
        print(json.dumps({"file": path.split("/")[-1], **check(cert)}), flush=True)
