#!/usr/bin/env python3
"""Independent verifier for LR-SPEC. Pure Python Fractions; no code shared with lrspec_scan.c.

ml_exact(v): max over t in candidate set of min_i ||t v_i||, candidate set = m/(vi+vj) (all m), plus peaks (2m+1)/(2 vi).
Reads scan output files (lines: v1..vn p q k) and checks every line; prints a tally as JSON.
"""
import sys, json
from fractions import Fraction
from math import gcd
from collections import Counter
from itertools import combinations


def dist(x: Fraction) -> Fraction:
    f = x - (x.numerator // x.denominator)
    return min(f, 1 - f)


def ml_exact(v):
    cands = set()
    for a, b in combinations(v, 2):
        D = a + b
        for m in range(D):
            cands.add(Fraction(m, D))
    for a in v:
        for m in range(a):
            cands.add(Fraction(2 * m + 1, 2 * a))
    best = Fraction(0)
    for t in cands:
        val = min(dist(t * x) for x in v)
        if val > best:
            best = val
    return best


def read_scan(path):
    rows = []
    with open(path) as f:
        for line in f:
            p = line.split()
            if not p:
                continue
            *vs, num, den, k = map(int, p)
            rows.append((tuple(vs), num, den, k))
    return rows


def main():
    path = sys.argv[1]
    n = int(sys.argv[2])
    do_verify = len(sys.argv) < 4 or sys.argv[3] != "noverify"
    rows = read_scan(path)
    bad = []
    kc = Counter()
    maxratio = Fraction(0)
    maxratio_t = None
    odd_form_fail = []
    for vs, p, q, k in rows:
        assert len(vs) == n and gcd(*vs) == 1 if n > 1 else True
        assert q - n * p == k and gcd(p, q) == 1
        if do_verify:
            ml = ml_exact(vs)
            if ml != Fraction(p, q) or not (ml < Fraction(1, n)):
                bad.append((vs, p, q, str(ml)))
        kc[k] += 1
        r = Fraction(max(vs), q)
        if r > maxratio:
            maxratio, maxratio_t = r, vs
        if n == 6:
            # Cordella form (P-1)/(6P), P = +-1 mod 6  <=> 6p = q - ... check q = 6P? ML = p/q
            # (P-1)/(6P) in lowest terms may be reduced; test by existence of P with p*6P == (P-1)*q
            ok = False
            # P = q*? : p/q = (P-1)/(6P)  =>  P (6p - q) = -q  =>  P = q/(q-6p) = q/k
            if k > 0 and q % k == 0:
                P = q // k
                if P % 6 in (1, 5) and 6 * P * p == (P - 1) * q:
                    ok = True
            if not ok:
                odd_form_fail.append((vs, p, q, k))
    out = {
        "n": n, "count_primitive_neartight": len(rows), "k_counts": dict(sorted(kc.items())),
        "max_k": max(kc) if kc else None, "k_gt_n": [r for r in rows if r[3] > n],
        "k_gt_half_n": [r for r in rows if 2 * r[3] > n],
        "verifier_mismatches": len(bad), "verifier_mismatch_examples": bad[:5],
        "verified_with_fractions": do_verify,
        "max_vmax_over_q": f"{maxratio.numerator}/{maxratio.denominator}" if maxratio_t else None,
        "max_vmax_over_q_tuple": maxratio_t,
    }
    if n == 6:
        out["odd_denominator_form_failures"] = odd_form_fail[:10]
        out["odd_denominator_form_failure_count"] = len(odd_form_fail)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
