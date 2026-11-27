"""Pipeline controls on small known graphs. usage: python controls_small.py <out_dir>"""
from __future__ import annotations

import itertools
import json
import os
import sys

import satlib as S


def complete(n: int) -> list[tuple[int, int]]:
    return list(itertools.combinations(range(n), 2))


def grotzsch() -> tuple[int, list[tuple[int, int]]]:
    # Mycielskian of C5: vertices 0-4 cycle, 5-9 shadows, 10 apex
    e = [(i, (i + 1) % 5) for i in range(5)]
    e = [(min(a, b), max(a, b)) for a, b in e]
    for i in range(5):
        for j in ((i + 1) % 5, (i - 1) % 5):
            e.append((min(5 + i, j), max(5 + i, j)))
        e.append((5 + i, 10))
    return 11, sorted(set(e))


def moser() -> tuple[int, list[tuple[int, int]]]:
    e = [(0, 1), (0, 2), (1, 2), (0, 3), (0, 4), (3, 4), (1, 5), (2, 5), (3, 6), (4, 6), (5, 6)]
    return 7, e


def petersen() -> tuple[int, list[tuple[int, int]]]:
    e = [(i, (i + 1) % 5) for i in range(5)] + [(i, i + 5) for i in range(5)] + [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
    return 10, sorted({(min(a, b), max(a, b)) for a, b in e})


def check(name: str, n: int, edges: list[tuple[int, int]], k: int, expect_sat: bool, out: str) -> dict:
    res: dict = {"name": name, "n": n, "m": len(edges), "k": k, "expect_sat": expect_sat}
    cl = S.encode_a(n, edges, k, sym=True)
    cnf = os.path.join(out, f"ctl_{name}_k{k}.cnf")
    prf = os.path.join(out, f"ctl_{name}_k{k}.drup")
    sat, model, _ = S.solve_glucose_proof(cl, prf, cnf)
    res["glucose_sat"] = sat
    if sat:
        res["glucose_colouring_valid"] = S.valid_colouring(S.decode_a(model, n, k), edges, k)
    else:
        ok, txt = S.drat_trim(cnf, prf)
        res["drat_trim_verified"] = ok
    cb = S.encode_b(n, edges, k)
    sb, mb, _ = S.solve_plain(cb, "cadical195")
    res["cadical_encB_sat"] = sb
    if sb:
        res["cadical_colouring_valid"] = S.valid_colouring(S.decode_b(mb, n, k), edges, k)
    d, col, nodes = S.dsatur_colourable(n, edges, k)
    res["dsatur_colourable"] = d
    res["dsatur_nodes"] = nodes
    if d:
        res["dsatur_colouring_valid"] = S.valid_colouring(col, edges, k)
    agree = (sat == sb == d == expect_sat)
    valid = all(res.get(x, True) for x in ("glucose_colouring_valid", "cadical_colouring_valid", "dsatur_colouring_valid"))
    drat = res.get("drat_trim_verified", True)
    res["PASS"] = bool(agree and valid and drat)
    return res


def main() -> None:
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    tests = [
        ("K5", 5, complete(5), 4, False),
        ("K4", 4, complete(4), 4, True),
        ("K4", 4, complete(4), 3, False),
        ("K6", 6, complete(6), 5, False),
        ("Grotzsch", *grotzsch(), 3, False),
        ("Grotzsch", *grotzsch(), 4, True),
        ("Moser", *moser(), 3, False),
        ("Moser", *moser(), 4, True),
        ("Petersen", *petersen(), 3, True),
        ("Petersen", *petersen(), 2, False),
    ]
    results = [check(nm, n, e, k, ex, out) for nm, n, e, k, ex in tests]
    for r in results:
        print(r)
    with open(os.path.join(out, "controls_small.json"), "w") as f:
        json.dump(results, f, indent=1)
    print("ALL_PASS", all(r["PASS"] for r in results))


if __name__ == "__main__":
    main()
