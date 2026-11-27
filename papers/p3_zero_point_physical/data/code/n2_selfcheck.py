"""N2 self-checks (Tier X): lambdified g-derivative sources (dyadic constants only), and the closed-form t-derivatives
of the Hessian along the shear against central finite differences.

usage: python -I n2_selfcheck.py
"""

import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n2_certify as n  # noqa: E402
from flint import arb  # noqa: E402


def main() -> None:
    for pot, par in (("yukawa", "1"), ("yukawa", "2"), ("gauss", "1"), ("gauss", "2")):
        V = n.Potential(pot, par)
        print(pot, par, "Cj =", [str(x)[:24] for x in V.Cj])
        for f in V.fn:
            print("    ", inspect.getsource(f).split("return")[1].strip()[:160])
        X0, Y0 = arb(1.3), arb(-0.7)
        h = arb(1e-4)
        t = arb(0.2)
        Hp = n.hess_derivs(V, n.path_R(X0, Y0, t + h))[0]
        Hm = n.hess_derivs(V, n.path_R(X0, Y0, t - h))[0]
        H = n.hess_derivs(V, n.path_R(X0, Y0, t))
        e1 = max(abs(float(((a - b) / (2 * h) - c).mid())) for a, b, c in zip(Hp, Hm, H[1]))
        e2 = max(abs(float(((a - 2 * b + c) / (h * h) - d).mid())) for a, b, c, d in zip(Hp, H[0], Hm, H[2]))
        print(f"    FD check: max |H' - FD| = {e1:.2e}, max |H'' - FD| = {e2:.2e}")


if __name__ == "__main__":
    main()
