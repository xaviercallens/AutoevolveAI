"""N2 debugging aid (Tier X): print the lattice sums and positivity quantities of one Duffy cell.

usage: python -I n2_debug_cell.py POT PARAM QMAX TRI S0 T0 H
"""

import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n2_certify as n  # noqa: E402
from flint import arb  # noqa: E402


def main() -> None:
    pot, par, qmax = sys.argv[1], sys.argv[2], int(sys.argv[3])
    tri, s0, t0_, h = int(sys.argv[4]), Fraction(sys.argv[5]), Fraction(sys.argv[6]), Fraction(sys.argv[7])
    V = n.Potential(pot, par)
    model = n.Model(V, n.q_arb("1/100000"), qmax)
    sc, tc = arb(float(s0 + h / 2)), arb(float(t0_ + h / 2))
    sb, tb = arb(float(s0 + h / 2), float(h / 2)), arb(float(t0_ + h / 2), float(h / 2))
    Sc = model.sums(tri, sc, tc)
    Sb = model.sums(tri, sb, tb)
    for k in range(18):
        print(k, "centre", Sc[k].v.str(5), " box", Sb[k].v.str(5), " d/ds", Sb[k].s.str(4), " d/dt", Sb[k].t.str(4))
    print(model.cell(tri, s0, t0_, h))


if __name__ == "__main__":
    main()
