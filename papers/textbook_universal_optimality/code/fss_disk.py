"""Finite-size scaling of upstream's closed-disk energy for a lattice (textbook v2, Section fss).

The configuration is a lattice L of covolume one with points p(j, k), j, k integers, and squared norm
|p(j, k)|^2 = s * Q(j, k) with an integer quadratic form Q:
  triangular A:  Q = j^2 + j k + k^2,  s = 1/b,  b = sqrt(3)/2   (Chapter 1's parametrisation)
  square Z^2:    Q = j^2 + k^2,        s = 1
The potential is the Gaussian g(t) = exp(-pi alpha t) of t = r^2 (admissible). Upstream's disk energy counts
ORDERED pairs inside the closed disk of radius R centred at 0 and divides by the count:
  e(R) = (1/n(R)) sum_{x in D_R} sum_{y in D_R, y != x} g(|x - y|^2),
whose limit for the lattice is theta_L(alpha) - 1 (ordered pairs: no factor 1/2).

Disk membership is decided in exact integer arithmetic (Q(x) <= Qmax), so no lattice point is ever
mis-classified by rounding. Each radius is taken half-way between two shells, R^2 = (Qmax + 1/2) s, so no
lattice point lies on the circle. Pair sums use all offsets v with |v|^2 <= 40, whose neglected tail is below
exp(-40 pi) ~ 4e-55 per pair. Everything printed is Tier X (floating point).

Usage:  python -I fss_disk.py [figure.pdf]
"""

from __future__ import annotations

import math
import sys

import numpy as np

ALPHA = 1.0
B = math.sqrt(3.0) / 2.0
V2MAX = 40.0  # offsets with |v|^2 <= V2MAX


def lattice_points(form: str, kmax: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Integer coordinates (j, k) with |j|, |k| <= kmax and the integer norm form Q(j, k)."""
    r = np.arange(-kmax, kmax + 1, dtype=np.int64)
    j, k = np.meshgrid(r, r, indexing="ij")
    j, k = j.ravel(), k.ravel()
    q = j * j + j * k + k * k if form == "tri" else j * j + k * k
    return j, k, q


def scale(form: str) -> float:
    """s with |p|^2 = s * Q (covolume one)."""
    return 1.0 / B if form == "tri" else 1.0


def theta_minus_one(form: str, alpha: float, kmax: int = 40) -> float:
    """sum_{a != 0} exp(-pi alpha |a|^2), the exact (to rounding) limit of the ordered-pair disk energy."""
    _, _, q = lattice_points(form, kmax)
    q = q[q > 0]
    return math.fsum(np.exp(-math.pi * alpha * scale(form) * q).tolist())


class Disk:
    """Points of the lattice in the disk Q <= qmax, with offsets for the pair sum."""

    def __init__(self, form: str, qmax_largest: int) -> None:
        self.form = form
        self.s = scale(form)
        kmax = int(math.isqrt(int(4 * qmax_largest)) + 3)  # Q >= (j^2 + k^2)/2 for both forms
        j, k, q = lattice_points(form, kmax)
        keep = q <= qmax_largest
        order = np.argsort(q[keep], kind="stable")
        self.j, self.k, self.q = j[keep][order], k[keep][order], q[keep][order]
        vk = int(math.isqrt(int(2 * V2MAX / self.s)) + 2)
        vj, vkk, vq = lattice_points(form, vk)
        sel = (vq > 0) & (self.s * vq <= V2MAX)
        self.vj, self.vk = vj[sel], vkk[sel]
        self.w = np.exp(-math.pi * ALPHA * self.s * vq[sel])

    def count(self, qmax: int) -> int:
        return int(np.searchsorted(self.q, qmax, side="right"))

    def energy(self, qmax: int) -> tuple[int, float]:
        """(n, e) for the closed disk Q <= qmax: ordered-pair energy per particle."""
        n = self.count(qmax)
        j, k = self.j[:n], self.k[:n]
        terms = []
        for vj, vk, w in zip(self.vj, self.vk, self.w):
            jj, kk = j + vj, k + vk
            qq = jj * jj + jj * kk + kk * kk if self.form == "tri" else jj * jj + kk * kk
            terms.append(float(w) * int(np.count_nonzero(qq <= qmax)))
        return n, math.fsum(terms) / n

    def brute(self, qmax: int) -> tuple[int, float]:
        """Same quantity by the O(n^2) definition with float coordinates (positive control)."""
        n = self.count(qmax)
        j, k = self.j[:n].astype(float), self.k[:n].astype(float)
        if self.form == "tri":
            x, y = (j + k / 2.0) / math.sqrt(B), k * B / math.sqrt(B)
        else:
            x, y = j, k
        d2 = (x[:, None] - x[None, :]) ** 2 + (y[:, None] - y[None, :]) ** 2
        np.fill_diagonal(d2, np.inf)
        return n, float(np.exp(-math.pi * ALPHA * d2).sum()) / n


def fit(n: np.ndarray, e: np.ndarray, powers: list[float]) -> np.ndarray:
    """Least squares e = c0 + sum_p c_p n^(-p)."""
    a = np.column_stack([np.ones_like(n)] + [n ** (-p) for p in powers])
    coef, *_ = np.linalg.lstsq(a, e, rcond=None)
    return coef


def radii_q(form: str, r_lo: float, r_hi: float, num: int) -> np.ndarray:
    """Distinct qmax with R = sqrt((qmax + 1/2) s) roughly geometric between r_lo and r_hi."""
    s = scale(form)
    r = np.geomspace(r_lo, r_hi, num)
    return np.unique(np.floor(r * r / s).astype(np.int64))


def main() -> None:
    fig_path = sys.argv[1] if len(sys.argv) > 1 else ""
    exact = theta_minus_one("tri", ALPHA)
    exact_sq = theta_minus_one("sq", ALPHA)
    print(f"exact limit theta_A(1)-1 = {exact:.15f}   theta_Z2(1)-1 = {exact_sq:.15f}")

    qs = radii_q("tri", 4.0, 130.0, 400)
    disk = Disk("tri", int(qs[-1]))
    print(f"offsets used: {len(disk.w)}  (|v|^2 <= {V2MAX}); radii: {len(qs)} distinct disks")

    # Positive control 1: the offset sum equals the O(n^2) definition.
    for qm in qs[[0, 40, 80, 120]]:
        n1, e1 = disk.energy(int(qm))
        _, e2 = disk.brute(int(qm))
        print(f"control brute vs offsets: n={n1:5d}  e_offsets={e1:.15f}  e_brute={e2:.15f}  diff={e1 - e2:.1e}")

    s = scale("tri")
    rad = np.sqrt((qs + 0.5) * s)
    data = np.array([disk.energy(int(q)) for q in qs])
    n, e = data[:, 0], data[:, 1]
    delta = n - math.pi * rad * rad  # Gauss-circle count error, evaluated between shells
    beta = math.fsum((disk.w * np.sqrt(s * (disk.vj**2 + disk.vj * disk.vk + disk.vk**2))).tolist()) / math.pi
    c_pred = -2.0 * math.sqrt(math.pi) * beta

    print("\n   R        n      e(R)               e(R)-e_inf      (n-pi R^2)/R")
    for i in np.linspace(0, len(qs) - 1, 9).astype(int):
        print(f"{rad[i]:7.2f} {int(n[i]):6d}  {e[i]:.15f}  {e[i] - exact:+.6e}  {delta[i] / rad[i]:+.4f}")
    print(f"max |n - pi R^2|/R over all disks: {np.max(np.abs(delta) / rad):.4f};"
          f" for R > 60: {np.max(np.abs(delta[rad > 60]) / rad[rad > 60]):.4f}")
    print(f"edge prediction (Tier C): beta = {beta:.6f},  c_pred = -2 sqrt(pi) beta = {c_pred:.6f}")

    print("\nfits over disks with n >= nmin (Tier X):")
    for nmin in (100, 1000):
        m = n >= nmin
        c3 = fit(n[m], e[m], [0.5, 1.0])
        c2 = fit(n[m], e[m], [0.5])
        c1 = fit(n[m], e[m], [1.0])
        r3 = e[m] - (c3[0] + c3[1] * n[m] ** -0.5 + c3[2] / n[m])
        print(f" nmin={nmin:5d} ({int(m.sum())} disks, n up to {int(n[m].max())})")
        print(f"   e_inf + c/sqrt(N) + d/N : e_inf={c3[0]:.9f} bias={c3[0] - exact:+.2e} c={c3[1]:.5f} d={c3[2]:.4f}"
              f"  rms resid={np.sqrt(np.mean(r3**2)):.2e}")
        print(f"   e_inf + c/sqrt(N)       : e_inf={c2[0]:.9f} bias={c2[0] - exact:+.2e} c={c2[1]:.5f}")
        print(f"   e_inf + d/N  (neg ctrl) : e_inf={c1[0]:.9f} bias={c1[0] - exact:+.2e} d={c1[1]:.4f}")

    # Negative control 2: the same pipeline on Z^2 must extrapolate to theta_Z2(1)-1, not to theta_A(1)-1.
    qz = radii_q("sq", 4.0, 130.0, 400)
    dz = Disk("sq", int(qz[-1]))
    dat = np.array([dz.energy(int(q)) for q in qz])
    mz = dat[:, 0] >= 100
    cz = fit(dat[mz, 0], dat[mz, 1], [0.5, 1.0])
    print(f"\nsquare lattice Z^2, 3-term fit (n >= 100): e_inf={cz[0]:.9f}  minus theta_Z2-1: {cz[0] - exact_sq:+.2e}"
          f"  minus theta_A-1: {cz[0] - exact:+.3e}")

    if fig_path:
        import matplotlib

        matplotlib.use("pdf")
        import matplotlib.pyplot as plt

        m = n >= 100
        c3 = fit(n[m], e[m], [0.5, 1.0])
        c1 = fit(n[m], e[m], [1.0])
        x = np.linspace(0.0, 0.14, 200)
        fig, ax = plt.subplots(1, 2, figsize=(9.0, 3.4))
        ax[0].plot(n ** -0.5, e - exact, "o", ms=2.5, color="#2166ac", label="disk energy (A, $\\alpha=1$)")
        ax[0].plot(x, c3[0] - exact + c3[1] * x + c3[2] * x * x, "-", lw=1.5, color="#1b7837",
                   label="fit $e_\\infty+c/\\sqrt{N}+d/N$")
        ax[0].plot(x, c1[0] - exact + c1[1] * x * x, "--", lw=1.5, color="#b35806", label="fit $e_\\infty+d/N$ only")
        ax[0].axhline(0.0, color="0.6", lw=0.8)
        ax[0].set_xlabel("$N^{-1/2}$")
        ax[0].set_ylabel("$e(N)-(\\theta_A(1)-1)$")
        ax[0].set_xlim(0.0, 0.14)
        ax[0].set_ylim(-0.03, 0.003)
        ax[0].legend(fontsize=7, frameon=False, loc="lower left")
        ax[1].plot(rad, delta / rad, "o", ms=2.0, color="#762a83")
        ax[1].axhline(0.0, color="0.6", lw=0.8)
        ax[1].set_xlabel("$R$")
        ax[1].set_ylabel("$(N(R)-\\pi R^2)/R$")
        for a in ax:
            a.spines[["top", "right"]].set_visible(False)
        fig.tight_layout()
        fig.savefig(fig_path)
        print(f"figure written: {fig_path}")


if __name__ == "__main__":
    main()
