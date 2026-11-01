"""Auditor's own geometry: exact rational arithmetic via Fraction on decimal strings."""
import csv
import json
import math
import sys
from decimal import Decimal, ROUND_HALF_EVEN
from fractions import Fraction
from itertools import combinations

EX = json.load(open(sys.argv[1]))
REPO = sys.argv[2]
PRODPTS = sys.argv[3]
PRODEDGES = sys.argv[4]
REPOEDGES = sys.argv[5]
OUT = sys.argv[6]
res: dict = {}

rows = EX["mupdf_rows"]
# row-major: each row lists triples left to right
rowmajor = []
for r in rows:
    t = r[2]
    assert len(t) % 3 == 0, r
    for k in range(0, len(t), 3):
        rowmajor.append(tuple(t[k:k + 3]))
# column-major: left column of each row first, then right column
left = [tuple(r[2][0:3]) for r in rows]
right = [tuple(r[2][3:6]) for r in rows if len(r[2]) == 6]
colmajor = left + right
pm = EX["pdfminer_tokens"]
pm_tr = [tuple(pm[k:k + 3]) for k in range(0, len(pm), 3)]
res["n_rows"] = len(rows)
res["n_points_mupdf"] = len(rowmajor)
res["pdfminer_eq_mupdf_multiset"] = sorted(pm) == sorted(t for p in rowmajor for t in p)

# repo 17-digit points, rounded half-even to 7 decimals
repo = [tuple(Decimal(x) for x in row) for row in csv.reader(open(REPO))]
rr = [tuple(str(c.quantize(Decimal("1e-7"), rounding=ROUND_HALF_EVEN)) for c in p) for p in repo]
def canon(p):
    return tuple(str(Decimal(c)) for c in p)
res["repo_rounded_eq_rowmajor_ordered"] = [canon(p) for p in rr] == [canon(p) for p in rowmajor]
res["repo_rounded_eq_colmajor_ordered"] = [canon(p) for p in rr] == [canon(p) for p in colmajor]
res["repo_rounded_eq_multiset"] = sorted(canon(p) for p in rr) == sorted(canon(p) for p in rowmajor)
maxerr = max(abs(Decimal(a) - b) for p, q in zip(rowmajor if res["repo_rounded_eq_rowmajor_ordered"] else colmajor, repo) for a, b in zip(p, q))
res["max_abs_rounding_err"] = str(maxerr)
pts_str = rowmajor if res["repo_rounded_eq_rowmajor_ordered"] else colmajor
res["order_used"] = "rowmajor" if res["repo_rounded_eq_rowmajor_ordered"] else "colmajor"

prod = json.load(open(PRODPTS))
mine_int = [[int(Decimal(c) * 10**7) for c in p] for p in pts_str]
res["producer_points_eq_mine_ordered"] = prod == mine_int
res["distinct"] = len(set(map(tuple, mine_int)))

def analyse(P, tag):
    P = [[Fraction(c) for c in p] for p in P]
    n = len(P)
    d2 = {}
    for i, j in combinations(range(n), 2):
        d2[(i, j)] = sum((P[i][k] - P[j][k]) ** 2 for k in range(3))
    D2 = max(d2.values())
    arg = [k for k, v in d2.items() if v == D2]
    t = Fraction(88928, 100000)
    T2D2 = t * t * D2
    E = sorted(k for k, v in d2.items() if v > T2D2)
    inc = min(d2[k] for k in E) / D2
    exc = max(v for k, v in d2.items() if v <= T2D2) / D2
    eq = sum(1 for v in d2.values() if v == T2D2)
    out = {
        "D2": str(D2), "D_float": math.sqrt(float(D2)), "argmax": arg, "n_edges": len(E),
        "min_included_ratio2": str(inc), "min_included_ratio": math.sqrt(float(inc)),
        "max_excluded_ratio": math.sqrt(float(exc)), "pairs_exactly_at_threshold": eq,
        "ratio2_margin_included": float(inc - t * t),
        "ratio_margin_included": math.sqrt(float(inc)) - 0.88928,
    }
    # sorted ranking for later: all pairs sorted by length desc
    order = sorted(d2, key=lambda k: d2[k], reverse=True)
    return out, E, order, d2, D2

o7, E7, order7, d2_7, D2_7 = analyse(pts_str, "7digit")
res["rounded"] = o7
res["rounded"]["D2_scaled_1e14"] = str(Fraction(o7["D2"]) * 10**14)
res["edges_eq_producer"] = sorted(map(tuple, json.load(open(PRODEDGES)))) == [tuple(e) for e in E7]
repoE = sorted(tuple(sorted(map(int, r))) for r in csv.reader(open(REPOEDGES)))
res["edges_eq_repo_witness"] = repoE == [tuple(e) for e in E7]
o17, E17, order17, d2_17, D2_17 = analyse([[str(c) for c in p] for p in repo], "17digit")
res["repo17"] = o17
res["repo17_edges_eq_rounded_edges"] = E17 == E7
res["repo17_edge_symdiff"] = len(set(E17) ^ set(E7))
# graph stats
deg = [0] * 101
for i, j in E7:
    deg[i] += 1; deg[j] += 1
res["deg_min"], res["deg_max"] = min(deg), max(deg)
# rank of the weakest edge
res["rank_weakest_edge_in_sorted_pairs"] = order7.index(min(E7, key=lambda k: d2_7[k])) + 1
# exact sigma3 comparison: 0.88928 > sqrt((3+sqrt3)/6) <=> 6 t^2 - 3 > sqrt3 (both positive) <=> (6t^2-3)^2 > 3
t = Fraction(88928, 100000)
a = 6 * t * t - 3
res["gale_exact"] = bool(a > 0 and a * a > 3)
res["sigma3"] = math.sqrt((3 + math.sqrt(3)) / 6)
json.dump({"res": res, "E7": E7, "order7": order7[:2100], "E17": E17}, open(OUT, "w"))
print(json.dumps(res, indent=1))
