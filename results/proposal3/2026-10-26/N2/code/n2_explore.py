"""N2 Tier X: linear-response majorant curvature U''(0) and E''(0) of the harmonic zero-point energy at the triangular
lattice along the symmetric shear P_t = [[1, t], [t, 1 + t^2]] (det 1), for radial pair potentials (B2 setting).

usage: python -I n2_explore.py POT PARAM [N] [RC]
  POT in {gauss, yukawa, riesz, dipolar};  gauss: exp(-pi a r^2); yukawa: exp(-kappa r)/r; riesz: r^-s;
  dipolar: 2/(r s (r + s)), s = sqrt(r^2 + d^2)  (= 2(1/r - 1/s)/d^2, P2 normalisation).
Floating point only (Tier X). Real-space sum over |R| <= RC plus the continuum tail -pi RC V'(RC) I of D.
"""

from __future__ import annotations

import math
import sys

import numpy as np
import sympy as sp

PI = math.pi
C = math.sqrt(2 / math.sqrt(3))


def radial(pot: str, p: float) -> tuple:
    r = sp.symbols("r", positive=True)
    if pot == "gauss":
        V = sp.exp(-sp.pi * p * r**2)
    elif pot == "yukawa":
        V = sp.exp(-p * r) / r
    elif pot == "riesz":
        V = r ** (-sp.Float(p))
    elif pot == "dipolar":
        s = sp.sqrt(r**2 + p**2)
        V = 2 / (r * s * (r + s))
    else:
        raise ValueError(pot)
    d1 = sp.diff(V, r)
    d2 = sp.diff(V, r, 2)
    return sp.lambdify(r, V, "numpy"), sp.lambdify(r, d1, "numpy"), sp.lambdify(r, d2, "numpy")


def lattice(rc: float) -> np.ndarray:
    L = int(rc / C * 1.2) + 2
    m, l = np.meshgrid(np.arange(-L, L + 1), np.arange(-L, L + 1), indexing="ij")
    m, l = m.ravel(), l.ravel()
    x, y = C * (m + l / 2), C * l * math.sqrt(3) / 2
    keep = (x * x + y * y <= rc * rc) & ((m != 0) | (l != 0))
    return np.stack([m[keep], l[keep], x[keep], y[keep]], axis=1).astype(float)


def hess(fns: tuple, X: np.ndarray, Y: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    _, d1, d2 = fns
    r = np.sqrt(X * X + Y * Y)
    a = d1(r) / r
    b = (d2(r) - a) / (r * r)
    return a + b * X * X, b * X * Y, a + b * Y * Y


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


def main() -> None:
    pot, p = sys.argv[1], float(sys.argv[2])
    N = int(sys.argv[3]) if len(sys.argv) > 3 else 32
    rc = float(sys.argv[4]) if len(sys.argv) > 4 else 60.0
    fns = radial(pot, p)
    pts = lattice(rc)
    X0, Y0 = pts[:, 2], pts[:, 3]
    u, v, w = duffy(N)
    tail = -PI * rc * fns[1](rc)

    def Hs(t: float) -> tuple[np.ndarray, ...]:
        return hess(fns, X0 + t * Y0, t * X0 + (1 + t * t) * Y0)

    h = 1e-3
    Hp, H0, Hm = Hs(h), Hs(0.0), Hs(-h)
    Hdd = tuple((a - 2 * b + c) / h**2 for a, b, c in zip(Hp, H0, Hm))
    hE = 1e-2
    HEp, HEm = Hs(hE), Hs(-hE)
    acc = {k: [np.zeros(len(u)) for _ in range(3)] for k in ("D", "G", "Dp", "Dm")}
    CH = 4000
    for i in range(0, len(pts), CH):
        sl = slice(i, i + CH)
        ph = 1 - np.cos(2 * PI * (np.outer(u, pts[sl, 0]) + np.outer(v, pts[sl, 1])))
        for key, src in (("D", H0), ("G", Hdd), ("Dp", HEp), ("Dm", HEm)):
            for j in range(3):
                acc[key][j] += ph @ src[j][sl]
    for key in ("D", "Dp", "Dm"):
        acc[key][0] += tail
        acc[key][2] += tail
    d11, d12, d22 = acc["D"]
    dl = np.sqrt(d11 * d22 - d12 * d12)
    tau = np.sqrt(d11 + d22 + 2 * dl)
    w11, w12, w22 = (d22 + dl) / (dl * tau), -d12 / (dl * tau), (d11 + dl) / (dl * tau)
    g11, g12, g22 = acc["G"]
    Upp = 0.25 * float((w * (w11 * g11 + 2 * w12 * g12 + w22 * g22)).sum())

    def trs(D: list) -> np.ndarray:
        det = np.maximum(D[0] * D[2] - D[1] * D[1], 0)
        return np.sqrt(D[0] + D[2] + 2 * np.sqrt(det))

    E0 = 0.5 * float((w * tau).sum())
    Epp = 0.5 * float((w * (trs(acc["Dp"]) + trs(acc["Dm"]) - 2 * tau)).sum()) / hE**2
    lam = (d11 + d22 - np.sqrt((d11 - d22) ** 2 + 4 * d12 * d12)) / 2
    k2 = (2 * PI) ** 2 * (u * u + v * v)
    trW = 0.25 * float((w * (w11 + w22)).sum())
    print(f"{pot}:{p} N={N} rc={rc} npts={len(pts)} E0={E0:.7f} U''(0)={Upp:.6f} E''(0)~{Epp:.5f} "
          f"min lam/|k|^2={float((lam / k2).min()):.4f} (1/4)int trW={trW:.5f}")


if __name__ == "__main__":
    main()
