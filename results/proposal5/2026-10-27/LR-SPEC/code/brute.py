#!/usr/bin/env python3
"""Pure-Python brute force (no masks, no witness screen) for small boxes; compares the SET of primitive near-tight
tuples with the C scan output. usage: brute.py n N scan_output.txt"""
import sys
from itertools import combinations
from math import gcd
from functools import reduce


def ml_int(v):
    n = len(v)
    bn, bd = 0, 1
    for i in range(n):
        for j in range(i + 1, n):
            D = v[i] + v[j]
            for m in range(1, D // 2 + 1):
                mn = D
                for x in v:
                    r = (m * x) % D
                    d = r if r < D - r else D - r
                    if d < mn:
                        mn = d
                        if mn * bd <= bn * D:
                            break
                else:
                    if mn * bd > bn * D:
                        bn, bd = mn, D
    g = gcd(bn, bd)
    return bn // g, bd // g


def main():
    n, N, path = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    found = set()
    for v in combinations(range(1, N + 1), n):
        if reduce(gcd, v) != 1:
            continue
        p, q = ml_int(v)
        if p * n < q:  # ML < 1/n
            found.add((v, p, q, q - n * p))
    scan = set()
    with open(path) as f:
        for line in f:
            t = list(map(int, line.split()))
            if t:
                scan.add((tuple(t[:n]), t[n], t[n + 1], t[n + 2]))
    print({"n": n, "N": N, "brute": len(found), "scan": len(scan), "equal": found == scan,
           "only_brute": sorted(found - scan)[:5], "only_scan": sorted(scan - found)[:5]})


if __name__ == "__main__":
    main()
