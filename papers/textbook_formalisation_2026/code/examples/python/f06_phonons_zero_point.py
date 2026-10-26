"""Annexe F, exemple 6 : phonons et energie de point zero du reseau triangulaire, potentiel gaussien (Niveau X).

Reseau de forme tau = x + i y, base a1 = (1/sqrt y, 0), a2 = (x/sqrt y, sqrt y) (covolume 1), masse 1, hbar = 1,
V(r) = exp(-pi a r^2). Matrice dynamique et energie de point zero harmonique :
  D(k) = sum_{R != 0} (1 - cos k.R) Hess V(R),  Hess V(R) = (-2 pi a I + 4 pi^2 a^2 R R^T) exp(-pi a |R|^2),
  E_zp(tau) = 1/2 < omega_1(k) + omega_2(k) >_ZB,  omega_j = sqrt(lambda_j(D(k))).
La moyenne sur la zone de Brillouin est prise sur une grille n x n de points milieux de la maille reciproque,
la meme grille fractionnaire pour toutes les formes tau, pour que l'erreur de grille se compense dans les differences.
Temoins positifs (programme P2, a = 1) : E_zp(rho) = 1,5033523522 et, pour le losange tau = 0,5 + 0,966025 i,
E_zp(tau) = 1,4902783183 < E_zp(rho) : le contre-exemple numerique a la conjecture QU-1. Courbure c(a) = (1/4) y^2 (d_xx + d_yy) E_zp
en rho = exp(i pi/3) par differences finies : negative (maximum local !) pour a = 0,5 et 1, positive pour a = 0,25 et 2
(valeurs P2 : -0,461, -0,962, +0,188, +0,495). Usage : python -I f06_phonons_zero_point.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import appF_style as st  # noqa: E402

import numpy as np  # noqa: E402

RHO = complex(0.5, math.sqrt(3) / 2)


def lattice(tau: complex, a: float) -> tuple[np.ndarray, np.ndarray]:
    """Vecteurs R != 0 avec exp(-pi a |R|^2) > 1e-19, et la base reciproque (b_i . a_j = 2 pi delta_ij)."""
    x, y = tau.real, tau.imag
    a1, a2 = np.array([1 / math.sqrt(y), 0.0]), np.array([x / math.sqrt(y), math.sqrt(y)])
    m = int(math.sqrt(14.0 / a) * 2 / min(1 / math.sqrt(y), math.sqrt(y))) + 2
    i, j = np.meshgrid(np.arange(-m, m + 1), np.arange(-m, m + 1))
    r = np.stack([i.ravel(), j.ravel()], axis=1) @ np.stack([a1, a2])
    r2 = (r * r).sum(axis=1)
    r = r[(r2 > 0) & (r2 < 14.0 / a)]
    recip = 2 * math.pi * np.linalg.inv(np.stack([a1, a2])).T
    return r, recip


def dyn_eigs(k: np.ndarray, r: np.ndarray, a: float) -> np.ndarray:
    """Valeurs propres (nk, 2) de D(k) pour les vecteurs d'onde k (nk, 2)."""
    e = np.exp(-math.pi * a * (r * r).sum(axis=1))
    hxx = (-2 * math.pi * a + 4 * math.pi**2 * a * a * r[:, 0] ** 2) * e
    hyy = (-2 * math.pi * a + 4 * math.pi**2 * a * a * r[:, 1] ** 2) * e
    hxy = 4 * math.pi**2 * a * a * r[:, 0] * r[:, 1] * e
    c = 1.0 - np.cos(k @ r.T)
    dxx, dyy, dxy = c @ hxx, c @ hyy, c @ hxy
    mid, rad = 0.5 * (dxx + dyy), np.sqrt(0.25 * (dxx - dyy) ** 2 + dxy**2)
    return np.stack([mid - rad, mid + rad], axis=1)


def ezp(tau: complex, a: float, n: int) -> float:
    r, recip = lattice(tau, a)
    u = (np.arange(n) + 0.5) / n
    uu, vv = np.meshgrid(u, u)
    k = np.stack([uu.ravel(), vv.ravel()], axis=1) @ recip
    lam = dyn_eigs(k, r, a)
    if lam.min() < -1e-9 * lam.max():
        raise ValueError(f"reseau dynamiquement instable en tau = {tau}")
    return 0.5 * float(np.sqrt(np.clip(lam, 0.0, None)).sum(axis=1).mean())


def curvature(a: float, n: int, h: float = 0.01) -> float:
    e0 = ezp(RHO, a, n)
    lap = sum(ezp(RHO + d, a, n) for d in (h, -h, 1j * h, -1j * h)) - 4 * e0
    return 0.25 * RHO.imag**2 * lap / h**2


def main() -> int:
    ok = True
    print("== a = 1 : triangulaire rho contre le losange tau = 0.5 + 0.966025 i (convergence en grille) ==")
    tau = complex(0.5, 0.966025)
    for n in (48, 96, 192):
        e, f = ezp(RHO, 1.0, n), ezp(tau, 1.0, n)
        print(f"n={n:<4} E_zp(rho) = {e:.10f} (P2: 1.5033523522)  E_zp(tau) = {f:.10f} (P2: 1.4902783183)"
              f"  difference = {f - e:+.4e}")
    ok = ok and abs(e - 1.5033523522) < 1e-6 and abs(f - 1.4902783183) < 1e-6 and f < e
    print("== courbure c(a) = Delta E_zp(rho)/4 (h = 0.01) ==")
    ref = {0.25: 0.188, 0.5: -0.461, 1.0: -0.962, 2.0: 0.495}
    for a, cref in ref.items():
        cs = [curvature(a, n) for n in (48, 96)]
        ok = ok and math.copysign(1, cs[-1]) == math.copysign(1, cref) and abs(cs[-1] - cref) < 0.02
        kind = "MAXIMUM local" if cs[-1] < 0 else "minimum local"
        print(f"a={a:<5} c(n=48)={cs[0]:+.4f}  c(n=96)={cs[1]:+.4f}  P2: {cref:+.3f}  -> rho est un {kind}")
    plot()
    print("temoins conformes:", ok)
    return 0 if ok else 1


def plot() -> None:
    plt = st.setup()
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.5))
    r, recip = lattice(RHO, 1.0)
    gamma, m_pt = np.zeros(2), 0.5 * recip[0]
    k_pt = (2 * recip[0] + recip[1]) / 3
    path, ticks = [], [0]
    for p, q in ((gamma, m_pt), (m_pt, k_pt), (k_pt, gamma)):
        s = np.linspace(0, 1, 80)[:, None]
        path.append(p + s * (q - p))
        ticks.append(ticks[-1] + float(np.linalg.norm(q - p)))
    kp = np.concatenate(path)
    dist = np.concatenate([ticks[i] + np.linspace(0, 1, 80) * (ticks[i + 1] - ticks[i]) for i in range(3)])
    w = np.sqrt(np.clip(dyn_eigs(kp, r, 1.0), 0, None))
    ax[0].plot(dist, w[:, 0], color=st.BLUE, label="branche basse")
    ax[0].plot(dist, w[:, 1], "--", color=st.ORANGE, label="branche haute")
    ax[0].set_xticks(ticks, [r"$\Gamma$", "M", "K", r"$\Gamma$"])
    for t in ticks:
        ax[0].axvline(t, color=st.GREY, lw=0.5)
    ax[0].set_ylabel(r"$\omega(\mathbf{k})$")
    ax[0].set_title(r"(a) phonons du réseau triangulaire, $V=e^{-\pi r^2}$")
    ax[0].legend(fontsize=7)
    xs = np.linspace(-0.04, 0.04, 17)
    for a, col, mk in ((0.25, st.GREEN, "^"), (1.0, st.BLUE, "o"), (2.0, st.ORANGE, "s")):
        e0 = ezp(RHO, a, 96)
        ax[1].plot(xs, [1e4 * (ezp(RHO + x, a, 96) - e0) / e0 for x in xs], marker=mk, ms=4, color=col,
                   label=f"a = {a:g}")
    ax[1].axhline(0, color=st.GREY, lw=0.5)
    ax[1].set_xlabel(r"déformation : $\tau=\rho+x$")
    ax[1].set_ylabel(r"$10^4\,(E_{zp}(\tau)-E_{zp}(\rho))/E_{zp}(\rho)$")
    ax[1].set_title(r"(b) pour a = 1, $\rho$ est un maximum local de $E_{zp}$")
    ax[1].legend()
    fig.tight_layout()
    print("figure:", st.save(fig, "appF_phonons").name)


if __name__ == "__main__":
    sys.exit(main())
