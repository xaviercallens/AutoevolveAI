"""B1 library: harmonic and self-consistent-harmonic (SCHA) lattice energies of the 2D Gaussian-core crystal.

Units: V(r) = exp(-pi a r^2) (eps = 1), unit density (covolume 1), m = 1, hbar_eff = Lam.
Per particle, harmonic:  E(tau) = E_static(tau) + Lam * E_zp(tau),
  E_static = (1/2) sum_{R != 0} V(R),  E_zp = (1/2) < sum_s sqrt(lam_s(D(k))) >_BZ,
  D(k) = sum_{R != 0} (1 - cos k.R) Hess V(R)  (dimensionless; omega = Lam-free sqrt(lam) in units sqrt(eps/(m l^2))).
Mean-square displacement (T = 0): <|u|^2> = (Lam / 2) < tr D(k)^{-1/2} >_BZ  (units l^2).

Lattice shape tau = x + i y, basis a1 = (1/sqrt y, 0), a2 = (x/sqrt y, sqrt y).
D(k) is evaluated in reciprocal space (Poisson form, PoissonGauss of the P2 gate script phonon_poisson_check.py);
BZ averages use the Duffy-Gauss rule (four triangles with apex at Gamma), which removes the |k| (E_zp) and 1/|k|
(<u^2>) singularities at Gamma.
"""

from __future__ import annotations

import math
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import numpy as np  # noqa: E402

P2_SCRIPTS = "/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-p2/crates/qf-yukawa-crystal/scripts"
sys.path.insert(0, P2_SCRIPTS)
from phonon_poisson_check import PoissonGauss, bases, duffy_nodes, invariants, lattice_points, omega_sum, stability  # noqa: E402

PI = math.pi
S3 = math.sqrt(3.0)
RHO = (0.5, S3 / 2)
A_NN = math.sqrt(2.0 / S3)  # nearest-neighbour distance of the unit-density triangular lattice
TOL_EXP = 41.0

_NODE_CACHE: dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}


def nodes(N: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if N not in _NODE_CACHE:
        _NODE_CACHE[N] = duffy_nodes(N)
    return _NODE_CACHE[N]


def realspace_R(a: float, x: float, y: float, widen: float = 1.0) -> np.ndarray:
    """Lattice vectors R != 0 with pi a |R|^2 / widen < TOL_EXP."""
    A, _ = bases(x, y)
    R = lattice_points(A, math.sqrt(TOL_EXP * widen / (PI * a)) + 1.0)
    r2 = (R**2).sum(1)
    return R[r2 > 1e-24]


def e_static(a: float, x: float, y: float) -> float:
    R = realspace_R(a, x, y)
    return 0.5 * float(np.exp(-PI * a * (R**2).sum(1)).sum())


def lap_static_exact(a: float, x: float = RHO[0], y: float = RHO[1]) -> float:
    """Hyperbolic Laplacian y^2 (d_xx + d_yy) of E_static: (1/2) sum h(|R|^2), h(u) = (u^2 f')' for f = e^{-pi a u}."""
    R = realspace_R(a, x, y)
    u = (R**2).sum(1)
    h = (-2 * PI * a * u + PI * PI * a * a * u * u) * np.exp(-PI * a * u)
    return 0.5 * float(h.sum())


def D_nodes(a: float, x: float, y: float, N: int) -> tuple[np.ndarray, np.ndarray]:
    u, v, w = nodes(N)
    pg = PoissonGauss(a, x, y)
    return pg.D(pg.kappa(u, v)), w


def e_zp(a: float, x: float, y: float, N: int = 48) -> float:
    D, w = D_nodes(a, x, y, N)
    return 0.5 * float((w * omega_sum(D)).sum())


def tr_inv_sqrt(D: np.ndarray) -> np.ndarray:
    """tr D^{-1/2} = (sqrt l1 + sqrt l2) / sqrt(l1 l2) for 2x2 SPD D given as (N,3) [xx, xy, yy]."""
    _, P, _ = invariants(D)
    return omega_sum(D) / np.sqrt(np.maximum(P, 1e-300))


def u2_harmonic_per_lam(a: float, x: float, y: float, N: int = 64) -> float:
    """<|u|^2> / Lam = (1/2) < tr D^{-1/2} >_BZ."""
    D, w = D_nodes(a, x, y, N)
    return 0.5 * float((w * tr_inv_sqrt(D)).sum())


def harmonic_energy(a: float, x: float, y: float, lam: float, N: int = 48) -> float:
    return e_static(a, x, y) + lam * e_zp(a, x, y, N)


def lap_stencil(F, x0: float, y0: float, hs: tuple[float, float] = (2e-3, 1e-3)) -> dict:
    vals = {}
    f0 = F(x0, y0)
    for h in hs:
        fxx = (F(x0 + h, y0) - 2 * f0 + F(x0 - h, y0)) / h**2
        fyy = (F(x0, y0 + h) - 2 * f0 + F(x0, y0 - h)) / h**2
        vals[h] = (y0 * y0 * (fxx + fyy), fxx, fyy)
    h1, h2 = hs
    lap = ((h1 / h2) ** 2 * vals[h2][0] - vals[h1][0]) / ((h1 / h2) ** 2 - 1)
    return {"lap": lap, "lap_coarse": vals[h1][0], "lap_fine": vals[h2][0], "fxx": vals[h2][1], "fyy": vals[h2][2]}


def quick_stable(a: float, x: float, y: float, n: int = 48) -> tuple[bool, float]:
    """Cheap stability screen: min lam_lo/|k|^2 over a half-shifted n x n grid plus 72 long-wave directions."""
    pg = PoissonGauss(a, x, y)
    idx = ((np.arange(n) + 0.5) / n + 0.5) % 1.0 - 0.5
    uu, vv = np.meshgrid(idx, idx, indexing="ij")
    K = pg.kappa(uu.ravel(), vv.ravel())
    th = np.linspace(0, 2 * PI, 72, endpoint=False)
    K = np.vstack([K, (1e-2 / (2 * PI)) * np.stack([np.cos(th), np.sin(th)], 1)])
    _, _, lo = invariants(pg.D(K))
    k2 = (2 * PI) ** 2 * (K**2).sum(1)
    r = float((lo / k2).min())
    return r > 0, r


def full_stability(a: float, x: float, y: float) -> dict:
    return stability(PoissonGauss(a, x, y))


# ---------------------------------------------------------------------------------------------------------------------
# Self-consistent harmonic approximation (T = 0), Gaussian potential: all averages closed form.
#   trial: harmonic with dynamical matrix Deff(k) (SPD); pair-relative displacement covariance
#   C_R = Lam < (1 - cos k.R) Deff(k)^{-1/2} >_BZ.
#   <V(R + w)>_{w ~ N(0, C)} = det(I + 2 pi a C)^{-1/2} exp(-pi a R^T (I + 2 pi a C)^{-1} R)
#   <Hess V(R + w)> = Hess of that smoothed function:  Vc [ (2 pi a M R)(2 pi a M R)^T - 2 pi a M ],  M = (I + 2pi a C)^-1
#   Deff(k) = sum_R (1 - cos k.R) <Hess V(R + w_R)>   (stationarity of the variational energy)
#   E_SCHA = (Lam / 4) < tr Deff^{1/2} > + (1/2) sum_R <V(R + w_R)>.
# Harmonic limit: E_SCHA = E_static + Lam E_zp + O(Lam^2).
# ---------------------------------------------------------------------------------------------------------------------


def mat_sqrt_inv_and_sqrt(D: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """For (N,3) SPD D return (N,3) components of D^{-1/2}, tr D^{1/2}, lam_lo."""
    T, P, lo = invariants(D)
    sdet = np.sqrt(np.maximum(P, 1e-300))
    s = np.sqrt(np.maximum(T + 2 * sdet, 1e-300))  # tr D^{1/2}
    # D^{1/2} = (D + sqrt(det) I) / s ; D^{-1/2} = (D^{1/2})^{-1} = adj(D^{1/2}) / det(D^{1/2}), det(D^{1/2}) = sqrt(det D)
    Sxx = (D[:, 0] + sdet) / s
    Sxy = D[:, 1] / s
    Syy = (D[:, 2] + sdet) / s
    inv = np.stack([Syy / sdet, -Sxy / sdet, Sxx / sdet], 1)
    return inv, s, lo


class SCHA:
    def __init__(self, a: float, x: float, y: float, N: int = 32, widen: float = 4.0) -> None:
        self.a, self.x, self.y = a, x, y
        self.R = realspace_R(a, x, y, widen=widen)
        u, v, self.w = nodes(N)
        _, Xi = bases(x, y)
        self.K = 2 * PI * (u.reshape(-1, 1) * Xi[0] + v.reshape(-1, 1) * Xi[1])  # absolute k
        self.oneminuscos = 1.0 - np.cos(self.K @ self.R.T)  # (Nk, NR)
        self.pg = PoissonGauss(a, x, y)
        self.Kappa = self.K / (2 * PI)

    def smoothed(self, C: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """C: (NR,3) covariances. Returns <V> (NR,) and <Hess V> (NR,3)."""
        a = self.a
        Axx = 1 + 2 * PI * a * C[:, 0]
        Axy = 2 * PI * a * C[:, 1]
        Ayy = 1 + 2 * PI * a * C[:, 2]
        det = Axx * Ayy - Axy * Axy
        Mxx, Mxy, Myy = Ayy / det, -Axy / det, Axx / det
        Rx, Ry = self.R[:, 0], self.R[:, 1]
        q = Mxx * Rx * Rx + 2 * Mxy * Rx * Ry + Myy * Ry * Ry
        Vc = np.exp(-PI * a * q) / np.sqrt(det)
        gx = 2 * PI * a * (Mxx * Rx + Mxy * Ry)
        gy = 2 * PI * a * (Mxy * Rx + Myy * Ry)
        H = np.stack([Vc * (gx * gx - 2 * PI * a * Mxx), Vc * (gx * gy - 2 * PI * a * Mxy), Vc * (gy * gy - 2 * PI * a * Myy)], 1)
        return Vc, H

    def solve(self, lam: float, tol: float = 1e-13, maxit: int = 400, mix: float = 0.6, D0: np.ndarray | None = None) -> dict:
        D = self.pg.D(self.Kappa) if D0 is None else D0.copy()
        hist = []
        E_old = None
        status = "max_iter"
        for it in range(maxit):
            inv, trs, lo = mat_sqrt_inv_and_sqrt(D)
            k2 = (self.K**2).sum(1)
            if float((lo / k2).min()) <= 0:
                status = "unstable_trial"
                break
            C = lam * ((self.w[:, None] * self.oneminuscos).T @ inv)  # (NR,3)
            Vc, H = self.smoothed(C)
            E = lam / 4 * float((self.w * trs).sum()) + 0.5 * float(Vc.sum())
            Dnew = self.oneminuscos @ H
            hist.append(E)
            if E_old is not None and abs(E - E_old) < tol and float(np.abs(Dnew - D).max()) < 1e-10:
                D = Dnew
                status = "converged"
                break
            E_old = E
            D = mix * Dnew + (1 - mix) * D
        inv, trs, lo = mat_sqrt_inv_and_sqrt(D)
        k2 = (self.K**2).sum(1)
        C = lam * ((self.w[:, None] * self.oneminuscos).T @ inv)
        Vc, H = self.smoothed(C)
        self.C, self.H = C, H
        E = lam / 4 * float((self.w * trs).sum()) + 0.5 * float(Vc.sum())
        u2 = 0.5 * lam * float((self.w * (inv[:, 0] + inv[:, 2])).sum())
        return {"E": E, "status": status, "iters": len(hist), "min_ratio_nodes": float((lo / k2).min()), "u2": u2, "D": D,
                "E_kin": lam / 4 * float((self.w * trs).sum()), "E_pot": 0.5 * float(Vc.sum())}

    def D_eff_at(self, Kabs: np.ndarray) -> np.ndarray:
        """Effective dynamical matrix at arbitrary absolute k (after solve)."""
        return (1.0 - np.cos(Kabs @ self.R.T)) @ self.H

    def stability_eff(self, n: int = 64) -> float:
        """min lam_lo(Deff)/|k|^2 over a half-shifted n x n grid plus 72 long-wave directions."""
        _, Xi = bases(self.x, self.y)
        idx = ((np.arange(n) + 0.5) / n + 0.5) % 1.0 - 0.5
        uu, vv = np.meshgrid(idx, idx, indexing="ij")
        K = 2 * PI * (uu.reshape(-1, 1) * Xi[0] + vv.reshape(-1, 1) * Xi[1])
        th = np.linspace(0, 2 * PI, 72, endpoint=False)
        K = np.vstack([K, 1e-2 * np.stack([np.cos(th), np.sin(th)], 1)])
        _, _, lo = invariants(self.D_eff_at(K))
        return float((lo / (K**2).sum(1)).min())
