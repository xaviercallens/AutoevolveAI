"""B2 Tier X exploration: linear-response upper bound U(s) >= E_zp(s) along a pure strain path.

usage: python -I b2_explore.py A [N]

Lattice L_s = P_s L_rho, P_s = diag(1+s, 1/(1+s)) (det 1), L_rho unit-covolume triangular with a lattice vector on the
x axis. D_s(kappa) = sum_{n != 0} (1 - cos 2 pi kappa.n) H(P_s R_n), H(R) = Hess exp(-pi a |R|^2).
E(s) = (1/2) int tr sqrt D_s dkappa;  U(s) = (1/4) int [tr X + tr X^{-1} D_s], X = sqrt D_0;  U >= E, U(0) = E(0).
U''(0) = sum_n tr(M_n H''_n(0)), M_n = (1/4) int (1 - cos 2 pi kappa.n) D_0^{-1/2} dkappa.
Floating point only (Tier X).
"""

import math
import sys

import numpy as np

PI = math.pi
C = math.sqrt(2 / math.sqrt(3))


def lattice(rmax2: float) -> np.ndarray:
    pts = []
    for m in range(-12, 13):
        for l in range(-12, 13):
            if (m, l) == (0, 0):
                continue
            x, y = C * (m + l / 2), C * l * math.sqrt(3) / 2
            if x * x + y * y <= rmax2:
                pts.append((m, l, x, y))
    return np.array(pts, dtype=float)


def hess(a: float, X: np.ndarray, Y: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    e = np.exp(-PI * a * (X * X + Y * Y))
    return e * (4 * PI**2 * a * a * X * X - 2 * PI * a), e * (4 * PI**2 * a * a * X * Y), e * (4 * PI**2 * a * a * Y * Y - 2 * PI * a)


def duffy(N: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    xg, wg = np.polynomial.legendre.leggauss(N)
    s = 0.5 * (xg + 1)
    w = 0.5 * wg
    S, T = np.meshgrid(s, s, indexing="ij")
    W = np.outer(w, w)
    S, T, W = S.ravel(), T.ravel(), W.ravel()
    us, vs, ws = [], [], []
    for sg in (1.0, -1.0):
        us += [sg * S / 2, S * (T - 0.5)]
        vs += [S * (T - 0.5), sg * S / 2]
        ws += [W * S / 2, W * S / 2]
    return np.concatenate(us), np.concatenate(vs), np.concatenate(ws)


def Dmat(a: float, pts: np.ndarray, u: np.ndarray, v: np.ndarray, s: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    X, Y = pts[:, 2] * (1 + s), pts[:, 3] / (1 + s)
    h11, h12, h22 = hess(a, X, Y)
    ph = 1 - np.cos(2 * PI * (np.outer(u, pts[:, 0]) + np.outer(v, pts[:, 1])))
    return ph @ h11, ph @ h12, ph @ h22


def trsqrt(d11: np.ndarray, d12: np.ndarray, d22: np.ndarray) -> np.ndarray:
    det = np.maximum(d11 * d22 - d12 * d12, 0)
    return np.sqrt(d11 + d22 + 2 * np.sqrt(det))


def main() -> None:
    a = float(sys.argv[1])
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 48
    pts = lattice(60.0 / (PI * a))
    u, v, w = duffy(N)
    d11, d12, d22 = Dmat(a, pts, u, v, 0.0)
    E0 = 0.5 * float((w * trsqrt(d11, d12, d22)).sum())
    det = d11 * d22 - d12 * d12
    dl = np.sqrt(det)
    tau = np.sqrt(d11 + d22 + 2 * dl)
    # W = D^{-1/2} = ((trD + delta) I - D)/(delta tau)
    w11 = (d22 + dl) / (dl * tau)
    w22 = (d11 + dl) / (dl * tau)
    w12 = -d12 / (dl * tau)

    def U(s: float) -> float:
        e11, e12, e22 = Dmat(a, pts, u, v, s)
        return 0.25 * float((w * (tau + w11 * e11 + 2 * w12 * e12 + w22 * e22)).sum()) + 0.0

    def E(s: float) -> float:
        e11, e12, e22 = Dmat(a, pts, u, v, s)
        return 0.5 * float((w * trsqrt(e11, e12, e22)).sum())

    print(f"a={a} N={N} E0={E0:.15f} U(0)={U(0):.15f} min det/|k|^4 proxy={float((det).min()):.3e}")
    for h in (1e-2, 5e-3, 2e-3):
        Upp = (U(h) + U(-h) - 2 * U(0)) / h**2
        Epp = (E(h) + E(-h) - 2 * E(0)) / h**2
        print(f"h={h}: U''~{Upp:.6f}  E''~{Epp:.6f}  U'~{(U(h)-U(-h))/(2*h):.2e} E'~{(E(h)-E(-h))/(2*h):.2e}")
    # M_n for representative n
    trW = 0.25 * float((w * (w11 + w22)).sum())
    print(f"(1/4) int tr W = {trW:.6f}")


if __name__ == "__main__":
    main()
