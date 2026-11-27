"""Brute-force control for lem.py: count maximal matchings via all edge subsets; compare with lem.matchings on n<=8."""
import sys
from itertools import combinations

sys.path.insert(0, "/tmp/msaudit")
from lem import matchings, parse_g6  # noqa: E402


def brute(n: int, adj: list[int]) -> list[int]:
    edges = [(i, j) for i, j in combinations(range(n), 2) if adj[i] >> j & 1]
    out = []
    for mask in range(1 << len(edges)):
        sel = [edges[k] for k in range(len(edges)) if mask >> k & 1]
        cov = 0
        ok = True
        for i, j in sel:
            if cov >> i & 1 or cov >> j & 1:
                ok = False
                break
            cov |= (1 << i) | (1 << j)
        if not ok:
            continue
        if any(not (cov >> i & 1) and not (cov >> j & 1) for i, j in edges):
            continue
        out.append(len(sel))
    return sorted(out)


checked = 0
bad = 0
for path in sys.argv[1:]:
    for line in open(path):
        if line.strip():
            n, adj = parse_g6(line)
            checked += 1
            bad += sorted(matchings(n, adj)) != brute(n, adj)
print("brute-force checked", checked, "graphs; mismatches", bad)
