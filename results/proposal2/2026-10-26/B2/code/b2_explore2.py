"""B2 Tier X: U''(0) and E''(0) along the symmetric shear P_t = [[1, t], [t, 1 + t^2]] (det 1), plus a check of the
closed-form second derivative H''_n of the Gaussian Hessian against finite differences.

usage: python -I b2_explore2.py A [N]
Floating point only (Tier X).
"""

import math
import sys

import os

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b2_explore import PI, duffy, lattice, trsqrt


def hess_t(a: float, X0: np.ndarray, Y0: np.ndarray, t: float) -> tuple[np.ndarray, ...]:
    Rx, Ry = X0 + t * Y0, t * X0 + (1 + t * t) * Y0
    e = np.exp(-PI * a * (Rx * Rx + Ry * Ry))
    k = 4 * PI**2 * a * a
    return e * (k * Rx * Rx - 2 * PI * a), e * (k * Rx * Ry), e * (k * Ry * Ry - 2 * PI * a)


def hess_tt(a: float, X0: np.ndarray, Y0: np.ndarray, t: float) -> tuple[np.ndarray, ...]:
    """Closed form d^2/dt^2 of Hess exp(-pi a |P_t R0|^2)."""
    Rx, Ry = X0 + t * Y0, t * X0 + (1 + t * t) * Y0
    dx, dy = Y0, X0 + 2 * t * Y0
    ddx, ddy = 0 * X0, 2 * Y0
    q1 = 2 * (Rx * dx + Ry * dy)
    q2 = 2 * (dx * dx + dy * dy + Rx * ddx + Ry * ddy)
    e = np.exp(-PI * a * (Rx * Rx + Ry * Ry))
    k = 4 * PI**2 * a * a
    pa = PI * a
    out = []
    for (Ri, Rj, di, dj, ddi, ddj, dl) in ((Rx, Rx, dx, dx, ddx, ddx, 1.0), (Rx, Ry, dx, dy, ddx, ddy, 0.0), (Ry, Ry, dy, dy, ddy, ddy, 1.0)):
        M = k * Ri * Rj - 2 * pa * dl
        M1 = k * (di * Rj + Ri * dj)
        M2 = k * (ddi * Rj + 2 * di * dj + Ri * ddj)
        out.append(e * ((pa * pa * q1 * q1 - pa * q2) * M - 2 * pa * q1 * M1 + M2))
    return tuple(out)


def main() -> None:
    a = float(sys.argv[1])
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 48
    pts = lattice(60.0 / (PI * a))
    X0, Y0 = pts[:, 2], pts[:, 3]
    h = 1e-4
    fd = [(p - 2 * q + r) / h**2 for p, q, r in zip(hess_t(a, X0, Y0, 0.3 + h), hess_t(a, X0, Y0, 0.3), hess_t(a, X0, Y0, 0.3 - h))]
    cf = hess_tt(a, X0, Y0, 0.3)
    print("closed-form H'' vs finite difference, max abs diff:", max(float(np.abs(x - y).max()) for x, y in zip(fd, cf)))
    u, v, w = duffy(N)
    ph = 1 - np.cos(2 * PI * (np.outer(u, pts[:, 0]) + np.outer(v, pts[:, 1])))

    def D(t: float) -> tuple[np.ndarray, ...]:
        return tuple(ph @ x for x in hess_t(a, X0, Y0, t))

    d11, d12, d22 = D(0.0)
    dl = np.sqrt(d11 * d22 - d12 * d12)
    tau = np.sqrt(d11 + d22 + 2 * dl)
    w11, w12, w22 = (d22 + dl) / (dl * tau), -d12 / (dl * tau), (d11 + dl) / (dl * tau)
    g11, g12, g22 = (ph @ x for x in hess_tt(a, X0, Y0, 0.0))
    Upp = 0.25 * float((w * (w11 * g11 + 2 * w12 * g12 + w22 * g22)).sum())
    E = lambda t: 0.5 * float((w * trsqrt(*D(t))).sum())  # noqa: E731
    U = lambda t: 0.25 * float((w * (tau + w11 * D(t)[0] + 2 * w12 * D(t)[1] + w22 * D(t)[2])).sum())  # noqa: E731
    print(f"a={a} N={N} E0={E(0):.15f} U''(0) quadrature={Upp:.8f}")
    for hh in (1e-2, 3e-3):
        print(f"h={hh}: (U(h)+U(-h)-2U0)/h^2={(U(hh)+U(-hh)-2*U(0))/hh**2:.8f} (E(h)+E(-h)-2E0)/h^2={(E(hh)+E(-hh)-2*E(0))/hh**2:.8f} E(h)-E(-h)={E(hh)-E(-hh):.2e}")
    lam_min = (d11 + d22 - np.sqrt((d11 - d22) ** 2 + 4 * d12 * d12)) / 2
    k2 = (2 * PI) ** 2 * (u * u + v * v)
    print("min lam_min/|kappa|^2 (reduced, on nodes):", float((lam_min / k2).min()))
    print("(1/4) int tr W:", 0.25 * float((w * (w11 + w22)).sum()))


if __name__ == "__main__":
    main()
