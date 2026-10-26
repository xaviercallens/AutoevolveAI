"""Exact (sympy) shape speed of the two strain paths at the triangular point: tau(t) = (b1.b2 + i det)/|b1|^2 for the
basis b1 = P_t c(1, 0), b2 = P_t c(1/2, sqrt3/2), and the factor k = |tau'(0)|^2 / y^2 with which, for an isotropic
C^2 function at rho, E''(0) = (k/2) Lap E(rho), Lap = y^2 (d_xx + d_yy).
"""

import sympy as sp


def main() -> None:
    t = sp.symbols("t", real=True)
    c = sp.sqrt(2 / sp.sqrt(3))
    for name, P in (("shear", sp.Matrix([[1, t], [t, 1 + t**2]])), ("diag", sp.Matrix([[1 + t, 0], [0, 1 / (1 + t)]]))):
        b1 = P * sp.Matrix([c, 0])
        b2 = P * sp.Matrix([c / 2, c * sp.sqrt(3) / 2])
        n1 = (b1.T * b1)[0]
        x = (b1.T * b2)[0] / n1
        y = (b1[0] * b2[1] - b1[1] * b2[0]) / n1
        x0, y0 = sp.simplify(x.subs(t, 0)), sp.simplify(y.subs(t, 0))
        dx, dy = sp.simplify(sp.diff(x, t).subs(t, 0)), sp.simplify(sp.diff(y, t).subs(t, 0))
        k = sp.nsimplify(sp.simplify((dx**2 + dy**2) / y0**2))
        print(name, "tau(0) =", x0, "+ i", y0, " tau'(0) =", dx, "+ i", dy, " k = |tau'|^2/y^2 =", k)
        assert sp.simplify(x0 - sp.Rational(1, 2)) == 0 and sp.simplify(y0 - sp.sqrt(3) / 2) == 0


if __name__ == "__main__":
    main()
