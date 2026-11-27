"""N1 developer check of one v2 cell over an a-interval (prints only).

usage: python -I n1_debug5.py A_LO A_HI TRI S0 T0 H QMAX
"""

from __future__ import annotations

import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n1_certify2 as m  # noqa: E402


def main() -> None:
    lo, hi, tri, s0, t0, h, qm = (Fraction(sys.argv[1]), Fraction(sys.argv[2]), int(sys.argv[3]), Fraction(sys.argv[4]),
                                  Fraction(sys.argv[5]), Fraction(sys.argv[6]), int(sys.argv[7]))
    mod = m.Model2(lo, hi, m.v1.q_arb("1/100000000"), qm)
    print("T", mod.tails["T"])
    sc, tc = s0 + h / 2, t0 + h / 2
    sca, tca = m.arb(sc.numerator) / sc.denominator, m.arb(tc.numerator) / tc.denominator
    ha = m.arb(h.numerator) / h.denominator
    c = mod.centre(tri, sca, tca)
    print("centre g", c[0].v, c[0].a if c else None)
    Mc = c[1]
    for M in Mc:
        print("centre entries", [(x.v, x.a) for x in M])
    sb, tb = sca + m.arb(0, 1) * ha / 2, tca + m.arb(0, 1) * ha / 2
    dS = m.arb(0, 1) * m.arb(sb.rad())
    acc = []
    for (al, be), Hs in list(zip(mod.th[tri], mod.Hb))[:3]:
        print("Hb n", [[(x[0], x[1], x[2]) for x in Hm] for Hm in Hs][0])
    print("cell", mod.cell(tri, s0, t0, h))
    mod.ball_debug = True
    gk = mod.ball(tri, sb, tb, Mc)
    print("ball g", gk if gk is None else (gk.b.v, gk.b.g, gk.b.h))


if __name__ == "__main__":
    main()
