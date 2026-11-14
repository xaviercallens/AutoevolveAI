"""N1 Tier X (floating point only): the exact second variation E''(0) of the harmonic zero-point energy along the
symmetric shear P_t = [[1, t], [t, 1 + t^2]], from the closed form tr sqrt(D) = sqrt(tr D + 2 sqrt det D) (2x2),
compared with finite differences of E, and the linear-response majorant curvature U''(0) of B2, for a list of a.

usage: python -I n1_explore.py N A1 [A2 ...]
"""

from __future__ import annotations

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "proposal2",
                                "2026-10-26", "B2", "code"))
from b2_explore import PI, duffy, lattice, trsqrt  # noqa: E402


def hess_derivs(a: float, X0: np.ndarray, Y0: np.ndarray, t: float) -> tuple[list[np.ndarray], ...]:
    """H, H', H'' (t-derivatives) of Hess exp(-pi a |P_t R0|^2), entries (11, 12, 22)."""
    Rx, Ry = X0 + t * Y0, t * X0 + (1 + t * t) * Y0
    dx, dy = Y0, X0 + 2 * t * Y0
    ddx, ddy = 0 * X0, 2 * Y0
    q1 = 2 * (Rx * dx + Ry * dy)
    q2 = 2 * (dx * dx + dy * dy + Rx * ddx + Ry * ddy)
    pa = PI * a
    k = 4 * pa * pa
    e = np.exp(-pa * (Rx * Rx + Ry * Ry))
    H, H1, H2 = [], [], []
    for (Ri, Rj, di, dj, ddi, ddj, dl) in ((Rx, Rx, dx, dx, ddx, ddx, 1.0), (Rx, Ry, dx, dy, ddx, ddy, 0.0),
                                          (Ry, Ry, dy, dy, ddy, ddy, 1.0)):
        M = k * Ri * Rj - 2 * pa * dl
        M1 = k * (di * Rj + Ri * dj)
        M2 = k * (ddi * Rj + 2 * di * dj + Ri * ddj)
        H.append(e * M)
        H1.append(e * (-pa * q1 * M + M1))
        H2.append(e * ((pa * pa * q1 * q1 - pa * q2) * M - 2 * pa * q1 * M1 + M2))
    return H, H1, H2


def tau_dd(B: list[np.ndarray], B1: list[np.ndarray], B2: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """tau = tr sqrt(B) and its second t-derivative tau'' from B, B', B''."""
    T, T1, T2 = B[0] + B[2], B1[0] + B1[2], B2[0] + B2[2]
    det = B[0] * B[2] - B[1] ** 2
    det1 = B1[0] * B[2] + B[0] * B1[2] - 2 * B[1] * B1[1]
    det2 = B2[0] * B[2] + 2 * B1[0] * B1[2] + B[0] * B2[2] - 2 * (B1[1] ** 2 + B[1] * B2[1])
    dl = np.sqrt(det)
    dl1 = det1 / (2 * dl)
    dl2 = det2 / (2 * dl) - det1 ** 2 / (4 * dl ** 3)
    tau = np.sqrt(T + 2 * dl)
    tau2 = (T2 + 2 * dl2) / (2 * tau) - (T1 + 2 * dl1) ** 2 / (4 * tau ** 3)
    return tau, tau2


def run(a: float, N: int) -> dict:
    pts = lattice(70.0 / (PI * a))
    X0, Y0 = pts[:, 2], pts[:, 3]
    u, v, w = duffy(N)
    ph = 1 - np.cos(2 * PI * (np.outer(u, pts[:, 0]) + np.outer(v, pts[:, 1])))
    H, H1, H2 = hess_derivs(a, X0, Y0, 0.0)
    D = [ph @ x for x in H]
    D1 = [ph @ x for x in H1]
    D2 = [ph @ x for x in H2]
    tau, tau2 = tau_dd(D, D1, D2)
    Epp = 0.5 * float((w * tau2).sum())
    det = D[0] * D[2] - D[1] ** 2
    dl = np.sqrt(det)
    w11, w12, w22 = (D[2] + dl) / (dl * tau), -D[1] / (dl * tau), (D[0] + dl) / (dl * tau)
    Upp = 0.25 * float((w * (w11 * D2[0] + 2 * w12 * D2[1] + w22 * D2[2])).sum())

    def E(t: float) -> float:
        Ht, _, _ = hess_derivs(a, X0, Y0, t)
        return 0.5 * float((w * trsqrt(*[ph @ x for x in Ht])).sum())

    h = 2e-3
    fd = (E(h) + E(-h) - 2 * E(0.0)) / h ** 2
    return {"a": a, "Epp_closed": Epp, "Epp_fd": fd, "Upp": Upp, "c_equiv": Epp / 8, "E0": E(0.0)}


def main() -> None:
    N = int(sys.argv[1])
    for s in sys.argv[2:]:
        r = run(float(s), N)
        print(" ".join(f"{k}={v:.6f}" for k, v in r.items()), flush=True)


if __name__ == "__main__":
    main()
