"""Exact geometry for the GALE-101 recheck. Integer arithmetic only.

usage: python geom.py <appendixA_raw.txt> <out_dir>
"""
from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from itertools import combinations
from math import isqrt

SCALE = 10**7
THR_NUM, THR_DEN = 88928, 100000  # threshold exactly 0.88928


def parse_points(path: str) -> list[tuple[int, int, int]]:
    """Parse decimals with exactly 7 digits into integers scaled by 1e7."""
    toks = open(path, encoding="utf-8").read().split()
    if len(toks) != 303:
        raise ValueError(f"expected 303 numbers, got {len(toks)}")
    vals: list[int] = []
    for t in toks:
        sign = -1 if t.startswith("-") else 1
        body = t.lstrip("-")
        ip, fp = body.split(".")
        if len(fp) != 7 or ip != "0":
            raise ValueError(f"bad token {t}")
        vals.append(sign * int(ip + fp))
    return [(vals[3 * i], vals[3 * i + 1], vals[3 * i + 2]) for i in range(101)]


def sqd(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
    return sum((x - y) ** 2 for x, y in zip(a, b))


def edges_at(pts: list[tuple[int, int, int]], num: int, den: int) -> tuple[list[tuple[int, int]], int]:
    """Edges = pairs with d^2 * den^2 > num^2 * D^2 (exact)."""
    d2 = {(i, j): sqd(pts[i], pts[j]) for i, j in combinations(range(len(pts)), 2)}
    D2 = max(d2.values())
    e = [(i, j) for (i, j), v in d2.items() if v * den * den > num * num * D2]
    return e, D2


def main() -> None:
    raw, out = sys.argv[1], sys.argv[2]
    pts = parse_points(raw)
    assert len(set(pts)) == 101, "duplicate points"
    n = len(pts)
    d2 = {(i, j): sqd(pts[i], pts[j]) for i, j in combinations(range(n), 2)}
    D2 = max(d2.values())
    argD = sorted(k for k, v in d2.items() if v == D2)
    T2 = Fraction(THR_NUM, THR_DEN) ** 2
    ratios2 = {k: Fraction(v, D2) for k, v in d2.items()}
    inc = {k: r for k, r in ratios2.items() if r > T2}
    exc = {k: r for k, r in ratios2.items() if r <= T2}
    mn_inc = min(inc.values())
    mx_exc = max(exc.values())
    deg = [0] * n
    for i, j in inc:
        deg[i] += 1
        deg[j] += 1
    # 4-core: repeatedly drop vertices of degree < 4
    adj = {v: set() for v in range(n)}
    for i, j in inc:
        adj[i].add(j)
        adj[j].add(i)
    alive = set(range(n))
    ch = True
    while ch:
        ch = False
        for v in list(alive):
            if len(adj[v] & alive) < 4:
                alive.discard(v)
                ch = True
    # exact comparison 0.88928 > sqrt((3+sqrt3)/6):  T2 > (3+sqrt3)/6  <=> 6*T2-3 > sqrt3
    lhs = 6 * T2 - 3  # Fraction
    # lhs > sqrt3 <=> lhs>0 and lhs^2 > 3
    gale_ok = lhs > 0 and lhs * lhs > 3
    sigma3_sq_float = (3 + 3 ** 0.5) / 6
    res = {
        "n_points": n,
        "distinct": len(set(pts)),
        "coordinate_scale": SCALE,
        "D2_scaled_1e14": D2,
        "D_float": (D2 ** 0.5) / SCALE,
        "pairs_at_D": [list(k) for k in argD],
        "n_pairs": len(d2),
        "threshold": f"{THR_NUM}/{THR_DEN}",
        "edges_exact": len(inc),
        "min_included_ratio2": f"{mn_inc.numerator}/{mn_inc.denominator}",
        "min_included_ratio_float": float(mn_inc) ** 0.5,
        "max_excluded_ratio2": f"{mx_exc.numerator}/{mx_exc.denominator}",
        "max_excluded_ratio_float": float(mx_exc) ** 0.5,
        "gap_included_minus_T2_float": float(mn_inc - T2),
        "gap_T2_minus_excluded_float": float(T2 - mx_exc),
        "min_included_ratio2_minus_T2_exact_positive": bool(mn_inc > T2),
        "degree_min": min(deg),
        "degree_max": max(deg),
        "isolated": sum(1 for d in deg if d == 0),
        "core4_size": len(alive),
        "core4_edges": sum(1 for i, j in inc if i in alive and j in alive),
        "gale_exact_088928_gt_sigma3": bool(gale_ok),
        "sigma3_float": sigma3_sq_float ** 0.5,
    }
    import os
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "points_scaled1e7.json"), "w") as f:
        json.dump(pts, f)
    with open(os.path.join(out, "edges_088928.json"), "w") as f:
        json.dump(sorted(inc), f)
    with open(os.path.join(out, "geometry_summary.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
    # sorted ratios near threshold
    near = sorted(ratios2.items(), key=lambda kv: kv[1])
    ordered = [float(v) ** 0.5 for _, v in near]
    idx = max(i for i, (k, v) in enumerate(near) if v <= T2)
    print("ratios around threshold:", [round(x, 8) for x in ordered[idx - 3 : idx + 5]])


if __name__ == "__main__":
    main()
