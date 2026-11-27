"""M3 third, floating-point (Tier X) implementation: kappa* as the root of the paper's characterisation (1.4),
  F(kappa) = int_1^inf D(t) [t^{-1/2} e^{-c/t} - e^{-c t}] dt,  c = kappa^2/(4 pi),  D(t) = Theta(t, L_B) - Theta(t, L_F),
evaluated by mpmath quadrature (dps 40) over theta functions built from the enumerated shells, plus a plain
IEEE double direct real-space sum (numpy) of G(kappa) = sum_B e^{-k r}/r - sum_F e^{-k r}/r.
Neither uses erfc, the Ewald kernels I/J, or Arb.  Floating point: supports nothing on its own.

usage: python -I m3_float.py SHELLS.json OUT.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import mpmath as mp
import numpy as np

mp.mp.dps = 40


def main() -> int:
    sh = json.loads(Path(sys.argv[1]).read_text())
    fcc = {int(k): v for k, v in sh["fcc_N"].items() if int(k) <= 200}
    bcc = {int(k): v for k, v in sh["bcc_M"].items() if int(k) <= 600}
    s3 = mp.cbrt(2)
    qf = {n: s3 * n for n in fcc}
    qb = {ell: ell / (2 * s3) for ell in bcc}

    def D(t: mp.mpf) -> mp.mpf:
        return mp.fsum(m * mp.exp(-mp.pi * t * qb[ell]) for ell, m in bcc.items()) - \
            mp.fsum(nn * mp.exp(-mp.pi * t * qf[n]) for n, nn in fcc.items())

    def F(kap: mp.mpf) -> mp.mpf:
        c = kap ** 2 / (4 * mp.pi)
        return mp.quad(lambda t: D(t) * (t ** -0.5 * mp.exp(-c / t) - mp.exp(-c * t)), [1, 1.5, 2.5, 5, 12, mp.inf])

    d1 = D(mp.mpf(1))
    root = mp.findroot(F, (mp.mpf("1.7179218684"), mp.mpf("1.7179218685")), solver="secant", tol=mp.mpf(10) ** -32)

    # IEEE double direct sum
    big = json.loads(Path(sys.argv[1]).read_text())
    nf = np.array([int(k) for k in big["fcc_N"]], dtype=np.float64)
    cf = np.array(list(big["fcc_N"].values()), dtype=np.float64)
    nb = np.array([int(k) for k in big["bcc_M"]], dtype=np.float64)
    cb = np.array(list(big["bcc_M"].values()), dtype=np.float64)
    rf = np.sqrt(2.0 ** (1 / 3) * nf)
    rb = np.sqrt(nb / (2 * 2.0 ** (1 / 3)))

    def G(k: float) -> float:
        return float(np.sum(cb * np.exp(-k * rb) / rb) - np.sum(cf * np.exp(-k * rf) / rf))

    lo, hi = 1.70, 1.74
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if G(mid) < 0:
            lo = mid
        else:
            hi = mid
    out = {"D(1)_should_be_0": mp.nstr(d1, 10), "kappa_star_eq14_mpmath": mp.nstr(root, 30),
           "kappa_star_double_direct": repr(0.5 * (lo + hi)),
           "F_at_903": mp.nstr(F(mp.mpf("1.717921868469903")), 10), "F_at_904": mp.nstr(F(mp.mpf("1.717921868469904")), 10)}
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
