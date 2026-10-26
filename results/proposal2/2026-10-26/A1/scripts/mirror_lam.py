"""Exact Python mirror of stage calcLam (grids.hpp), on top of ivmirror. Untrusted: produces chunk literals that the
Lean kernel re-derives; lambda and mu are compared with the C++ dump.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ivmirror as M  # noqa: E402

N = 45000


def pow3(x):
    return M.mul(M.mul(M.ONE, x), M.mul(x, x))


def pow2(x):
    return M.mul(M.ONE, M.mul(x, x))


def pow4(x):
    return M.mul(M.ONE, M.mul(M.mul(x, x), M.mul(x, x)))


def pow5(x):
    return M.mul(M.mul(M.ONE, x), M.mul(M.mul(x, x), M.mul(x, x)))


def calcLam(tb: M.Table) -> dict[str, object]:
    sc = tb.scal
    p, R, eps = sc["p"], sc["R"], sc["eps"]
    R2 = M.div(R, M.ofint(2))
    s0 = M.rat(1, 100)
    H = M.div(M.sub(R2, s0), M.ofint(N))
    idx = next(i for i in sorted(tb.ts) if tb.ts[i] == p)
    idx2 = next(i for i in sorted(tb.ts) if tb.ts[i][0] == R[0])
    fp, fpr = M.add(tb.pts[idx][0], eps), M.add(tb.pts[idx][1], eps)
    fr, er = M.add(tb.pts[idx2][0], eps), M.add(tb.pts[idx2][3], eps)
    B = M.sub(M.mul(M.div(p, R2), M.sub(fr, fp)), M.mul(M.div(R2, p), er))
    cf = M.sub(M.div(s0, M.ofint(2)), M.div(pow3(s0), M.mul(M.mul(M.ofint(24), p), p)))
    erl = M.div(pow5(s0), M.mul(M.ofint(80), pow4(p)))
    cf = M.add(cf, (0, erl[1]))
    radial_upper = M.sqrt(M.add(M.mul(p, p), M.mul(s0, s0)))[1]
    cells_sp = [i for i in sorted(tb.cels) if i + 1 in tb.ts and tb.ts[i + 1][1] >= p[0] and tb.ts[i][0] <= radial_upper]
    sp = None
    for i in cells_sp:
        it = M.add(tb.cels[i][2], eps)
        sp = it if sp is None else M.hull(sp, it)
    quo = M.div(p, pow2(M.add(M.sqrt(M.add(M.mul(p, p), M.mul(s0, s0))), p)))
    root = M.div(M.ONE, M.mul(M.ofint(4), p))
    coeff = M.mul((quo[0], root[1]), M.mul(M.rat(1, 6), pow3(s0)))
    B = M.add(M.add(B, M.mul(fpr, cf)), M.mul(sp, coeff))
    fterms, eterms = [], []
    for i in range(N):
        sh = M.add(s0, M.mul(H, M.add(M.ofint(i), M.rat(1, 2))))
        T = M.sqrt(M.add(M.mul(p, p), M.mul(sh, sh)))
        v = M.lookup_val(tb, T, M.window_cells(tb, T))
        fterms.append(M.mul(H, M.div(M.mul(p, M.sub(v[0], fp)), M.mul(sh, sh))))
    H2 = M.div(R2, M.ofint(N))
    for i in range(N):
        sh = M.mul(H2, M.add(M.ofint(i), M.rat(1, 2)))
        T = M.sqrt(M.add(M.mul(p, p), M.mul(sh, sh)))
        v = M.lookup_val(tb, T, M.window_cells(tb, T))
        eterms.append(M.div(M.mul(H2, v[1]), p))
    Facc, Eacc = M.ofint(0), M.ofint(0)
    for t in fterms:
        Facc = M.add(Facc, t)
    for t in eterms:
        Eacc = M.add(Eacc, t)
    cells_bnd = [i for i in sorted(tb.cels) if i + 1 in tb.ts and tb.ts[i + 1][1] >= p[0] and tb.ts[i][0] <= R[1]]
    bnd = [0] * 6
    for k in range(6):
        for i in cells_bnd:
            val = -((-M.absI(M.add(tb.cels[i][k], eps))[1]) // M.Q)
            bnd[k] = max(bnd[k], val)
    C, Cp, Ce0, Ce1 = (M.rat(max(1, bnd[j]), 1) for j in (1, 2, 4, 5))
    vpp = M.add(M.div(Cp, p), M.div(M.mul(M.ofint(8), C), M.mul(s0, s0)))
    vepp = M.add(M.div(Ce1, p), M.div(Ce0, M.mul(p, p)))
    evipp = M.absI(M.mul(M.div(M.mul(M.mul(M.sub(R2, s0), H), H), M.ofint(24)), vpp))
    eppp = M.absI(M.mul(M.div(M.mul(M.mul(R2, H2), H2), M.ofint(24)), vepp))
    Facc = M.add(Facc, (-evipp[1], evipp[1]))
    Eacc = M.add(Eacc, (-eppp[1], eppp[1]))
    B = M.add(M.add(B, Facc), Eacc)
    lam = M.div(B, M.mul(p, R2))
    mu = M.sub(M.sub(fr, M.mul(M.rat(1, 3), er)), M.div(M.mul(M.mul(lam, R), R), M.ofint(2)))
    return {"idx": idx, "idx2": idx2, "cells_sp": cells_sp, "cells_bnd": cells_bnd, "bnd": bnd, "fterms": fterms, "eterms": eterms,
            "lam": lam, "mu": mu, "H": H, "H2": H2}


if __name__ == "__main__":
    tb = M.load(Path(sys.argv[1]))
    r = calcLam(tb)
    print("idx", r["idx"], "idx2", r["idx2"], "sp cells", r["cells_sp"][0], r["cells_sp"][-1], "bnd cells", r["cells_bnd"][0], r["cells_bnd"][-1],
          "bnd", r["bnd"], "lambda_match", r["lam"] == tb.scal["lambda"], "mu_match", r["mu"] == tb.scal["mu"])
