"""M1x (Tier X, floating point only): harmonic Lindemann ratios of the triangular crystal in the model units of N2/P2
(hbar = m = 1, unit covolume, lattice constant a = sqrt(2/sqrt3), potential as in n2_explore.py), T = 0, gamma = 0.

  <|u|^2>        = (1/2) < tr D(k)^(-1/2) >_BZ                      eta   = sqrt(<|u|^2>) / a
  <|u_n - u_0|^2> = < (1 - cos k.a1) tr D(k)^(-1/2) >_BZ  (nearest neighbour)   eta_m = sqrt(...) / a

These numbers are in the model's own units: a physical Lindemann ratio needs the physical mass, dipole strength and
lattice constant, which are not part of M1. Real-space sum |R| <= RC plus the continuum tail of D, as in n2_explore.

usage: python -I m1x_lindemann.py POT PARAM [N] [RC]
"""
from __future__ import annotations

import math
import sys

import numpy as np

sys.path.insert(0, "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal3/2026-10-26/N2/code")
import n2_explore as X  # noqa: E402


def main() -> None:
    pot, p = sys.argv[1], float(sys.argv[2])
    N = int(sys.argv[3]) if len(sys.argv) > 3 else 48
    rc = float(sys.argv[4]) if len(sys.argv) > 4 else 100.0
    fns = X.radial(pot, p)
    pts = X.lattice(rc)
    u, v, w = X.duffy(N)
    H = X.hess(fns, pts[:, 2], pts[:, 3])
    D = [np.zeros(len(u)) for _ in range(3)]
    for i in range(0, len(pts), 4000):
        sl = slice(i, i + 4000)
        ph = 1 - np.cos(2 * math.pi * (np.outer(u, pts[sl, 0]) + np.outer(v, pts[sl, 1])))
        for j in range(3):
            D[j] += ph @ H[j][sl]
    tail = -math.pi * rc * fns[1](rc)
    D[0] += tail
    D[2] += tail
    det = D[0] * D[2] - D[1] ** 2
    sq = np.sqrt(det)
    tau = np.sqrt(D[0] + D[2] + 2 * sq)
    trinv_sqrt = tau / sq  # tr D^(-1/2) = tr D^(1/2) / sqrt(det D) for 2x2
    a = X.C
    u2 = 0.5 * float((w * trinv_sqrt).sum())
    nn = float((w * (1 - np.cos(2 * math.pi * u)) * trinv_sqrt).sum())
    print(f"{pot}:{p} N={N} rc={rc} <u^2>={u2:.6f} eta={math.sqrt(u2) / a:.5f} <(u_n-u_0)^2>={nn:.6f} "
          f"eta_m={math.sqrt(nn) / a:.5f}  (model units hbar=m=1, a={a:.5f})")


if __name__ == "__main__":
    main()
