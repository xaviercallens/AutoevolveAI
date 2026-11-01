"""Cross-check the paper's rounded Appendix A against the author's repo points.csv (17 digits), and
recompute the edge set INDEPENDENTLY with Decimal (separate code path from geom.py), plus P2/P3 controls.
usage: python crosscheck.py <appendixA_raw.txt> <repo_points.csv> <repo_witness_edges.csv> <edges_088928.json> <out_json>"""
from __future__ import annotations

import itertools
import json
import sys
from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal, getcontext

getcontext().prec = 60


def decimal_edges(P: list[list[Decimal]], thr: Decimal) -> tuple[set[tuple[int, int]], Decimal]:
    n = len(P)
    d2 = {}
    for i, j in itertools.combinations(range(n), 2):
        d2[(i, j)] = sum((P[i][a] - P[j][a]) ** 2 for a in range(3))
    D2 = max(d2.values())
    return {k for k, v in d2.items() if v > thr * thr * D2}, D2


def main() -> None:
    raw, rp, rw, ej, out = sys.argv[1:6]
    res: dict = {}
    toks = open(raw).read().split()
    P = [[Decimal(t) for t in toks[3 * i : 3 * i + 3]] for i in range(101)]
    R = [[Decimal(x) for x in line.strip().split(",")] for line in open(rp) if line.strip()]
    res["repo_points"] = len(R)
    res["paper_equals_repo_rounded_half_even_in_order"] = all(
        Decimal(x).quantize(Decimal("1e-7"), rounding=ROUND_HALF_EVEN) == p
        for r, pr in zip(R, P) for x, p in zip(r, pr)
    )
    res["paper_equals_repo_rounded_half_up_in_order"] = all(
        Decimal(x).quantize(Decimal("1e-7"), rounding=ROUND_HALF_UP) == p
        for r, pr in zip(R, P) for x, p in zip(r, pr)
    )
    res["max_abs_coordinate_difference_paper_vs_repo"] = float(max(abs(a - b) for r, pr in zip(R, P) for a, b in zip(r, pr)))
    mine = {tuple(e) for e in json.load(open(ej))}
    E1, D2 = decimal_edges(P, Decimal("0.88928"))
    res["P3_decimal_edge_count"] = len(E1)
    res["P3_decimal_edges_equal_integer_edges"] = (E1 == mine)
    repo_e = {tuple(sorted(map(int, l.strip().split(",")))) for l in open(rw) if l.strip()}
    res["repo_witness_edges"] = len(repo_e)
    res["repo_witness_equals_my_edges_for_rounded_points"] = (repo_e == mine)
    res["repo_witness_minus_mine"] = len(repo_e - mine)
    res["mine_minus_repo_witness"] = len(mine - repo_e)
    # edge set of repo 17-digit points at the same threshold 0.88928
    E2, D2r = decimal_edges(R, Decimal("0.88928"))
    res["repo_points_edges_at_088928"] = len(E2)
    res["repo_points_edges_equal_rounded_edges"] = (E2 == mine)
    res["repo_D_float"] = float(D2r) ** 0.5
    # P2: regular tetrahedron: D^2 = 8 (vertices of cube), all 6 pairs at distance D, so all are edges for t<1 and none at t=1
    T = [[Decimal(a) for a in v] for v in ([1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1])]
    e, d = decimal_edges(T, Decimal("0.99"))
    e1, _ = decimal_edges(T, Decimal("1"))
    res["P2_tetra_D2"] = int(d)
    res["P2_tetra_edges_t0.99"] = len(e)
    res["P2_tetra_edges_t1"] = len(e1)
    # P2b: unit square side 1 in the plane with its diagonals: diam sqrt2; edges at t=0.8: diagonals only (2)
    Q = [[Decimal(a), Decimal(b), Decimal(0)] for a, b in ((0, 0), (1, 0), (1, 1), (0, 1))]
    e, _ = decimal_edges(Q, Decimal("0.8"))
    res["P2_square_edges_t0.8"] = len(e)
    res["P2_PASS"] = bool(res["P2_tetra_D2"] == 8 and res["P2_tetra_edges_t0.99"] == 6 and res["P2_tetra_edges_t1"] == 0 and res["P2_square_edges_t0.8"] == 2)
    # P3 pass: independent code agrees AND that code is also exercised on a random set vs a float reimplementation
    import random
    rng = random.Random(5)
    S = [[Decimal(rng.randrange(0, 10**6)) / Decimal(10**6) for _ in range(3)] for _ in range(60)]
    eS, _ = decimal_edges(S, Decimal("0.6"))
    import numpy as np
    A = np.array([[float(x) for x in p] for p in S])
    dd = ((A[:, None, :] - A[None, :, :]) ** 2).sum(2)
    Dm = dd.max()
    ef = {(i, j) for i in range(60) for j in range(i + 1, 60) if dd[i, j] > 0.36 * Dm}
    res["P3_random_set_decimal_vs_float_equal"] = (eS == ef)
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
