"""C1c: certified comparison rho_G(r) vs rho_{K_N}(r) at explicit rational r, over the 2^N - 2 transient states.
Usage: fixation_cert.py <graph6> <out.json> <r1> [<r2> ...]   (r given as p/q)

Method: float64 dense LU proposes x~ for (I - Q) x = R (dB, uniform init) and T~ for (I - Q) T = 1;
the residuals of x~ and T~ (both dyadic rationals) are computed EXACTLY with Fractions. Since
(I - Q)^{-1} >= 0 with row sums T (expected absorption time), |x - x~|_inf <= |res_x|_inf * T_max and
T_max <= max T~ / (1 - |res_T|_inf) (needs |res_T|_inf < 1). rho_G = mean over single-mutant states.
All bounds are exact rationals; floating point only proposes."""

from __future__ import annotations

import os

os.environ["OPENBLAS_NUM_THREADS"] = "2"

import json  # noqa: E402
import sys  # noqa: E402
from fractions import Fraction  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dbcore as d  # noqa: E402


def build(adj: d.Adj, r: Fraction) -> tuple[list[int], dict[int, int], list[list[tuple[int, Fraction]]], list[Fraction]]:
    n = len(adj)
    full = (1 << n) - 1
    states = list(range(1, full))
    idx = {s: t for t, s in enumerate(states)}
    q: list[list[tuple[int, Fraction]]] = []
    rr: list[Fraction] = []
    for s in states:
        row: dict[int, Fraction] = {}
        b = Fraction(0)
        for ns, w in d._transitions_db(adj, s, r):
            if ns == full:
                b += w
            elif ns != 0:
                row[idx[ns]] = row.get(idx[ns], Fraction(0)) + w
        q.append(list(row.items()))
        rr.append(b)
    return states, idx, q, rr


def certify(adj: d.Adj, r: Fraction) -> dict[str, object]:
    n = len(adj)
    states, idx, q, rr = build(adj, r)
    ns = len(states)
    a = np.eye(ns)
    for t, row in enumerate(q):
        for c, w in row:
            a[t, c] -= float(w)
    bx = np.array([float(v) for v in rr])
    x = np.linalg.solve(a, bx)
    tt = np.linalg.solve(a, np.ones(ns))
    # one step of iterative refinement in float (still only a proposal)
    x = x + np.linalg.solve(a, bx - a @ x)
    xf = [Fraction(float(v)) for v in x]
    tf = [Fraction(float(v)) for v in tt]

    def resid(vec: list[Fraction], rhs: list[Fraction]) -> Fraction:
        worst = Fraction(0)
        for t in range(ns):
            val = vec[t] - sum((w * vec[c] for c, w in q[t]), Fraction(0)) - rhs[t]
            if abs(val) > worst:
                worst = abs(val)
        return worst

    res_x = resid(xf, rr)
    res_t = resid(tf, [Fraction(1)] * ns)
    assert res_t < 1
    tmax = max(tf) / (1 - res_t)
    err = res_x * tmax
    rho_hat = sum((xf[idx[1 << v]] for v in range(n)), Fraction(0)) / n
    rho_k = d.rho_complete_db(n, r)
    diff_lo = rho_hat - err - rho_k
    diff_hi = rho_hat + err - rho_k
    verdict = "G_above_K" if diff_lo > 0 else ("G_below_K" if diff_hi < 0 else "undecided")
    return {"r": f"{r.numerator}/{r.denominator}", "states": ns, "rho_G_hat": float(rho_hat), "rho_K": float(rho_k),
            "rho_K_exact": f"{rho_k.numerator}/{rho_k.denominator}" if rho_k.denominator < 10 ** 60 else "omitted (large)",
            "residual_x_bound": float(res_x), "residual_T_bound": float(res_t), "T_max_bound": float(tmax),
            "error_bound": float(err), "diff_interval": [float(diff_lo), float(diff_hi)],
            "ratio_hat": float(rho_hat / rho_k), "verdict": verdict}


def main() -> None:
    g6 = open(sys.argv[1]).readline().strip()
    out = sys.argv[2]
    adj = d.parse_graph6(g6)
    res = []
    for tok in sys.argv[3:]:
        p, qd = tok.split("/")
        rec = certify(adj, Fraction(int(p), int(qd)))
        print(json.dumps(rec), flush=True)
        res.append(rec)
    json.dump({"graph6": g6, "N": len(adj), "results": res}, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
