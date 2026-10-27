"""Worked example for the paper: exact Allen eq. (5),(6),(9) on tiny graphs, pure Fractions."""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F


def solve(n: int, edges: list[tuple[int, int]]) -> dict:
    adj = [[0] * n for _ in range(n)]
    for a, b in edges:
        adj[a][b] = adj[b][a] = 1
    deg = [sum(r) for r in adj]
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    idx = {p: k for k, p in enumerate(pairs)}

    def key(i: int, j: int) -> tuple[int, int]:
        return (i, j) if i < j else (j, i)

    m = len(pairs)
    A = [[F(0)] * (m + 1) for _ in range(m)]
    for (i, j), r in idx.items():
        A[r][r] += 1
        A[r][m] = F(1)
        for k in range(n):
            for (u, v) in ((i, j), (j, i)):
                if adj[u][k] and k != v:
                    A[r][idx[key(k, v)]] -= F(1, 2) * F(1, deg[u])
    for c in range(m):
        piv = next(r for r in range(c, m) if A[r][c] != 0)
        A[c], A[piv] = A[piv], A[c]
        d = A[c][c]
        A[c] = [x / d for x in A[c]]
        for r in range(m):
            if r != c and A[r][c] != 0:
                f = A[r][c]
                A[r] = [x - f * y for x, y in zip(A[r], A[c])]
    tau = {pairs[r]: A[r][m] for r in range(m)}

    def T(i: int, j: int) -> F:
        return F(0) if i == j else tau[key(i, j)]

    rem = [1 + sum(F(adj[i][j], deg[i]) * T(i, j) for j in range(n)) for i in range(n)]
    S = sum(deg)
    neff = sum(F(deg[i], S) * rem[i] for i in range(n))
    ident = 1 + sum(T(i, j) for i, j in pairs if adj[i][j]) / (S // 2)
    return {"n": n, "edges": edges, "deg": deg, "tau": {f"{i}{j}": str(v) for (i, j), v in tau.items()},
            "remeet": [str(x) for x in rem], "N_eff": str(neff), "N_eff_float": float(neff),
            "edge_identity_equal": ident == neff,
            "sum_pi2_tau": str(sum(F(deg[i], S) ** 2 * rem[i] for i in range(n)))}


def main() -> int:
    out = {
        "K3": solve(3, [(0, 1), (0, 2), (1, 2)]),
        "path3_star_S2": solve(3, [(0, 1), (0, 2)]),
        "K4_minus_edge": solve(4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3)]),
    }
    with open(sys.argv[1], "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
