"""Exact check (sympy) of the linear-combination identity used by ProgZeroPointCert.two_trace_le_of_inverse.

[tr X + tr(P S^2) - 2 tr S] - [q(y1, y2) + q(y2, y3)] = sum_ij c_ij E_ij,  E = X P - I,  Y = S - X,
q(a, b) = p11 a^2 + 2 p12 a b + p22 b^2, with c_ij = 2 s_ij - x_ij (X, S, P symmetric).
"""

import sympy as sp


def main() -> None:
    x11, x12, x22, p11, p12, p22, s11, s12, s22 = sp.symbols("x11 x12 x22 p11 p12 p22 s11 s12 s22")
    q = lambda a, b: p11 * a**2 + 2 * p12 * a * b + p22 * b**2  # noqa: E731
    y1, y2, y3 = s11 - x11, s12 - x12, s22 - x22
    trPS2 = p11 * (s11**2 + s12**2) + 2 * p12 * (s12 * (s11 + s22)) + p22 * (s12**2 + s22**2)
    lhs = (x11 + x22) + trPS2 - 2 * (s11 + s22) - (q(y1, y2) + q(y2, y3))
    E11 = x11 * p11 + x12 * p12 - 1
    E12 = x11 * p12 + x12 * p22
    E21 = x12 * p11 + x22 * p12
    E22 = x12 * p12 + x22 * p22 - 1
    combo = (2 * s11 - x11) * E11 + (2 * s12 - x12) * E12 + (2 * s12 - x12) * E21 + (2 * s22 - x22) * E22
    diff = sp.expand(lhs - combo)
    print("difference:", diff)
    assert diff == 0
    # sanity (negative control): a wrong coefficient must break the identity
    bad = sp.expand(lhs - (combo + E11))
    assert bad != 0
    print("ok")


if __name__ == "__main__":
    main()
