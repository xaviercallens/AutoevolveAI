"""Validate a 4-colouring of the 2029 longest pairs (decoded and checked edge by edge)."""
import json
import sys

import pycosat

sys.path.insert(0, "/tmp/galeaudit/scripts")
G = json.load(open(sys.argv[1]))
order = [tuple(e) for e in G["order7"]]
N = 101


def log_cnf(edges):
    cls = []
    for (u, v) in edges:
        for c in range(4):
            cls.append([(-(2 * x + 1 + b) if (c >> b) & 1 else (2 * x + 1 + b)) for x in (u, v) for b in range(2)])
    return cls


pre = order[:2029]
m = pycosat.solve(log_cnf(pre))
s = set(l for l in m if l > 0)
col = [((2 * v + 2) in s) * 2 + ((2 * v + 1) in s) for v in range(N)]
ok = all(col[u] != col[v] for u, v in pre)
# max part diameter ratio^2 of this colouring equals the 2030th pair? check the longest monochromatic pair rank
mono_ranks = [i for i, (u, v) in enumerate(order) if col[u] == col[v]]
print("prefix2029 colouring proper:", ok, "colour classes:", [col.count(c) for c in range(4)],
      "longest monochromatic pair rank (1-based):", mono_ranks[0] + 1 if mono_ranks else None)
