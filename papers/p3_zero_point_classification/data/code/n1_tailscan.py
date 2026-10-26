"""N1 helper: rigorous tail bound T of n1_certify2.tail_bound versus the truncation QMAX (prints only).

usage: python -I n1_tailscan.py A_LO:A_HI:Q1,Q2,... [more specs]
"""

from __future__ import annotations

import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n1_certify2 as m  # noqa: E402


def main() -> None:
    for spec in sys.argv[1:]:
        lo_s, hi_s, qs = spec.split(":")
        lo, hi = Fraction(lo_s), Fraction(hi_s)
        alo, ahi = m.arb(lo.numerator) / lo.denominator, m.arb(hi.numerator) / hi.denominator
        for q in qs.split(","):
            t = m.tail_bound(alo, ahi, int(q), "shear", m.v1.q_arb("1/100000000"))
            print(f"a=[{lo},{hi}] qmax={q} n_half={len(m.lattice_half(int(q)))} T={float(t['T'].upper()):.3e}",
                  flush=True)


if __name__ == "__main__":
    main()
