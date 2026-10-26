"""N1: print a list of contiguous rational a-intervals A_LO:A_HI for n1_certify2.py.

usage: python -I n1_plan.py START END REL [DEN]
  intervals of relative width about REL (hi - lo = REL * lo), endpoints rounded to multiples of 1/DEN (default
  10000), from START to END exactly (rationals)
"""

from __future__ import annotations

import sys
from fractions import Fraction


def main() -> None:
    start, end, rel = Fraction(sys.argv[1]), Fraction(sys.argv[2]), Fraction(sys.argv[3])
    den = int(sys.argv[4]) if len(sys.argv) > 4 else 10000
    pts = [start]
    while pts[-1] < end:
        nxt = Fraction(round(pts[-1] * (1 + rel) * den), den)
        if nxt <= pts[-1]:
            nxt = pts[-1] + Fraction(1, den)
        if nxt > end or end - nxt < (end - pts[-1]) / 3:
            nxt = end
        pts.append(nxt)
    print(" ".join(f"{a}:{b}" for a, b in zip(pts, pts[1:])))


if __name__ == "__main__":
    main()
