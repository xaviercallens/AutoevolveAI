"""Auditor's exact verifier: ML over Cordella Lemma 2.2's full candidate set (sums, differences, peaks),
Fractions only. Also reports all optimal times. Independent of the producer's verify.py (which uses sums+peaks)."""
import sys
import json
import random
from fractions import Fraction
from math import gcd
from functools import reduce
from itertools import combinations


def dist(x: Fraction) -> Fraction:
    f = x - (x.numerator // x.denominator)
    return min(f, 1 - f)


def ml_full(v: tuple[int, ...]) -> tuple[Fraction, list[Fraction]]:
    dens = set(2 * a for a in v)
    for a, b in combinations(v, 2):
        dens.add(a + b)
        if a != b:
            dens.add(abs(a - b))
    best = Fraction(0)
    times: list[Fraction] = []
    for L in dens:
        for m in range(L):
            t = Fraction(m, L)
            val = min(dist(t * x) for x in v)
            if val > best:
                best, times = val, [t]
            elif val == best and t not in times:
                times.append(t)
    return best, sorted(times)


def main() -> None:
    tuples = [(1, 2, 3, 4, 5, 7, 18), (1, 3, 4, 5, 7, 13, 18), (1, 3, 4, 5, 7, 11, 30), (2, 7, 9, 11, 13, 20, 54),
              (8, 3, 11, 19), (5, 6, 11, 17, 23, 28)]
    res = []
    for v in tuples:
        ml, ts = ml_full(tuple(sorted(v)))
        n = len(v)
        res.append({"v": v, "gcd": reduce(gcd, v), "ML": str(ml), "ML<1/n": ml < Fraction(1, n),
                    "k": ml.denominator - n * ml.numerator, "optimal_times": [str(t) for t in ts[:6]]})
    # sample of rows from given files
    rng = random.Random(20261101)
    sample_stats = {}
    for path in sys.argv[1:]:
        rows = [tuple(map(int, l.split())) for l in open(path) if l.strip()]
        pick = rows if len(rows) <= 40 else rng.sample(rows, 40)
        bad = 0
        for r in pick:
            vs, p, q, k = r[:-3], r[-3], r[-2], r[-1]
            ml, _ = ml_full(vs)
            if not (ml == Fraction(p, q) and q - len(vs) * p == k and reduce(gcd, vs) == 1 and ml < Fraction(1, len(vs))):
                bad += 1
        sample_stats[path] = {"checked": len(pick), "of": len(rows), "bad": bad}
    print(json.dumps({"named": res, "samples": sample_stats}, indent=1))


if __name__ == "__main__":
    main()
