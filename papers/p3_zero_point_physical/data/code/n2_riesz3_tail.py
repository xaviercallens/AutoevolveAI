"""N2 obstacle measurement: size of the rigorous real-space tail bound (the n2_certify.py shell bound, |g^(j)|
decreasing, Voronoi counting) of the scaled dynamical matrix B = D/s^2 for V = r^-3, over the annulus Rc <= |R| < 2 Rc
only (a lower bound for the full tail bound), compared with lambda_min(B) ~ (2 pi)^2 * 0.39 * |v|^2 >= 3.9 (Tier X).

usage: python -I n2_riesz3_tail.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n2_certify as n  # noqa: E402
from flint import arb  # noqa: E402


class Riesz:
    def __init__(self, s: int) -> None:
        self.s = arb(s) / 2

    def g(self, j: int, q: arb) -> arb:
        c = arb(1)
        for i in range(j):
            c = c * (-self.s - i)
        return c * q ** (-self.s - j)


def main() -> None:
    V = Riesz(3)
    t0 = n.q_arb("1/100000")
    delta = arb(1) / 2
    for Rc in (10, 25, 50, 100, 200):
        r = arb(Rc)
        acc = arb(0)
        while bool(r < 2 * Rc):
            ro = r + delta
            cnt = n.PI * ((ro + n.RHO_V) ** 2 - (r - n.RHO_V) ** 2)
            th = 2 * n.PI * ro / n.C
            bH = n.point_bounds(V, r, ro, t0, None)[0]
            acc += cnt * th * th * bH
            r = r + delta
        print(f"Rc={Rc}: tail bound of B entries over [Rc, 2Rc) >= {float(acc.mid()):.3e}  (need << 3.9)")


if __name__ == "__main__":
    main()
