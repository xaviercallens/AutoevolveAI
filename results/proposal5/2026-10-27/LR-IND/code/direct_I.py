#!/usr/bin/env python3
"""Direct brute force of I(k, p, l) (Def. 2.1, no sieve, no equivalence except sign/permutation) for tiny cases.

A tuple u in (Z_{lp} minus pZ)^k is improper iff no time a in [1, lp/2] has (k+1)*||a u_i||_N >= N for all i
and there is no i with gcd(l, u_j : j != i) > 1.  Sign flips u_i -> N - u_i and permutations preserve both
conditions, so it suffices to scan multisets over [1, N/2].
Usage: direct_I.py k p l
"""
from __future__ import annotations

import itertools
import json
import math
import sys


def main() -> int:
    k, p, l = (int(x) for x in sys.argv[1:4])
    n = l * p
    vals = [u for u in range(1, n // 2 + 1) if u % p]
    good = {u: frozenset(a for a in range(1, n // 2 + 1) if (k + 1) * min(a * u % n, n - a * u % n) >= n) for u in vals}
    improper = []
    for t in itertools.combinations_with_replacement(vals, k):
        common = good[t[0]]
        for u in t[1:]:
            common = common & good[u]
            if not common:
                break
        if common:
            continue
        if any(math.gcd(l, *[t[j] for j in range(k) if j != i]) > 1 for i in range(k)):
            continue
        improper.append(t)
    print(json.dumps({"k": k, "p": p, "l": l, "multisets_scanned": math.comb(len(vals) + k - 1, k),
                      "improper_multisets": len(improper), "examples": improper[:5]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
