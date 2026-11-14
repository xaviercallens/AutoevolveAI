"""Annexe F, exemple 1 : la formule de Poisson pour les gaussiennes (Niveau X, jamais une preuve).

1. En dimension 1 : sum_n exp(-pi a (n+x)^2) = a^(-1/2) sum_k exp(-pi k^2/a) cos(2 pi k x).
2. En dimension 2 : Theta_A(a) = a^(-1) Theta_A(1/a) pour le reseau triangulaire A de covolume 1
   (son dual est une rotation de lui-meme).
Temoin positif : l'egalite tient a 1e-13 pres. Temoin negatif : sans le facteur a^(-1/2) (ou a^(-1)),
l'ecart est d'ordre 1. Figure : figures/appF_poisson.pdf. Usage : python -I f01_poisson.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import appF_style as st  # noqa: E402

import numpy as np  # noqa: E402

A2 = 2.0 / math.sqrt(3.0)  # carre du pas du reseau triangulaire de covolume 1


def theta1(a: float, x: float, nmax: int) -> float:
    """Somme directe sum_{|n|<=nmax} exp(-pi a (n+x)^2)."""
    n = np.arange(-nmax, nmax + 1)
    return float(np.exp(-math.pi * a * (n + x) ** 2).sum())


def theta1_dual(a: float, x: float, kmax: int) -> float:
    """Cote dual de Poisson : a^(-1/2) sum_{|k|<=kmax} exp(-pi k^2/a) cos(2 pi k x)."""
    k = np.arange(-kmax, kmax + 1)
    return float((np.exp(-math.pi * k**2 / a) * np.cos(2 * math.pi * k * x)).sum() / math.sqrt(a))


def theta_tri(a: float, nmax: int = 40) -> float:
    """Theta_A(a) = sum_{v in A} exp(-pi a |v|^2), |v|^2 = A2 (m^2 + m n + n^2)."""
    m, n = np.meshgrid(np.arange(-nmax, nmax + 1), np.arange(-nmax, nmax + 1))
    return float(np.exp(-math.pi * a * A2 * (m * m + m * n + n * n)).sum())


def main() -> int:
    ok = True
    print("== dimension 1 : sum_n exp(-pi a (n+x)^2) ==")
    for a, x in ((0.1, 0.0), (0.1, 0.3), (3.0, 0.3), (7.0, 0.5)):
        lhs, rhs = theta1(a, x, 200), theta1_dual(a, x, 200)
        bad = rhs * math.sqrt(a)  # temoin negatif : facteur a^(-1/2) oublie
        ok = ok and abs(lhs - rhs) < 1e-13 and abs(lhs - bad) > 1e-2
        print(f"a={a:<4} x={x:<4} direct={lhs:.15f} dual={rhs:.15f} ecart={abs(lhs - rhs):.1e}"
              f" | sans facteur: ecart={abs(lhs - bad):.2e}")
    print("== dimension 2 : Theta_A(a) = a^-1 Theta_A(1/a) ==")
    for a in (0.25, 0.5, 2.0):
        lhs, rhs = theta_tri(a), theta_tri(1.0 / a) / a
        ok = ok and abs(lhs - rhs) < 1e-12 and abs(lhs - a * rhs) > 1e-2
        print(f"a={a:<4} Theta_A(a)={lhs:.13f}  Theta_A(1/a)/a={rhs:.13f}  ecart={abs(lhs - rhs):.1e}"
              f" | sans facteur: ecart={abs(lhs - a * rhs):.2e}")
    print("== nombre de termes pour une erreur < 1e-12 a a=0.01, x=0.3 ==")
    exact = theta1_dual(0.01, 0.3, 50)
    errs_d = [abs(theta1(0.01, 0.3, n) - exact) for n in range(0, 61)]
    errs_p = [abs(theta1_dual(0.01, 0.3, k) - exact) for k in range(0, 4)]
    n_direct = next(n for n, e in enumerate(errs_d) if e < 1e-12 * exact)
    k_dual = next(k for k, e in enumerate(errs_p) if e < 1e-12 * exact)
    print(f"cote direct: nmax={n_direct}   cote dual: kmax={k_dual}   valeur={exact:.12f}")
    plot(errs_d, exact)
    print("temoins conformes:", ok)
    return 0 if ok else 1


def plot(errs_d: list[float], exact: float) -> None:
    plt = st.setup()
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.4))
    aa = np.logspace(-1.3, 1.3, 120)
    ax[0].loglog(aa, [theta_tri(a) for a in aa], color=st.BLUE, label=r"$\Theta_A(a)$")
    ax[0].loglog(aa, [theta_tri(1 / a) / a for a in aa], "o", ms=3, mfc="white", mec=st.ORANGE,
                 markevery=6, label=r"$a^{-1}\,\Theta_A(1/a)$")
    ax[0].loglog(aa, [theta_tri(1 / a) for a in aa], "--", color=st.GREY, lw=1,
                 label=r"$\Theta_A(1/a)$ (témoin négatif)")
    ax[0].set_xlabel("a")
    ax[0].set_title("(a) réseau triangulaire : les deux côtés de Poisson")
    ax[0].legend()
    n = np.arange(len(errs_d))
    rel = np.maximum(np.array(errs_d) / exact, 1e-17)
    ax[1].semilogy(n, rel, "s-", color=st.BLUE, ms=3, label="somme directe, a = 0,01")
    ax[1].axhline(1e-12, color=st.GREY, lw=1, ls="--")
    ax[1].text(1, 2e-12, r"$10^{-12}$", color=st.GREY, fontsize=8)
    ax[1].set_xlabel(r"nombre de termes $n_{\max}$")
    ax[1].set_ylabel("erreur relative")
    ax[1].set_title("(b) la somme directe converge lentement quand a est petit")
    ax[1].legend()
    fig.tight_layout()
    print("figure:", st.save(fig, "appF_poisson").name)


if __name__ == "__main__":
    sys.exit(main())
