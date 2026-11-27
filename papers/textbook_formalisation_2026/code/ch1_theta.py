"""Chapitre 1 : verifications numeriques (Niveau X, jamais une preuve).

1. Formule de Poisson : Theta_L(a) = a^-1 Theta_{L*}(1/a) pour Z^2 et pour le reseau triangulaire A.
   Controle positif : l'egalite tient a 1e-12. Controle negatif : sans le facteur a^-1 elle echoue.
2. Comparaison Theta_A(a) <= Theta_{Z^2}(a) (theoreme de Montgomery, Niveau L) sur une grille de a.
3. Comptage des points de A dans le disque de rayon R : N(R)/(pi R^2) -> 1.
4. Signes (-1)^n d^n/dt^n exp(-sqrt t) > 0 pour n <= 8 (sympy), controle negatif : cos t.
"""
from __future__ import annotations

import math

import sympy as sp

A2 = 2.0 / math.sqrt(3.0)  # a^2 pour la covolume 1 : a^2 * sqrt(3)/2 = 1


def theta_z2(alpha: float, nmax: int = 40) -> float:
    s = sum(math.exp(-math.pi * alpha * n * n) for n in range(-nmax, nmax + 1))
    return s * s


def theta_tri(alpha: float, nmax: int = 60) -> float:
    total = 0.0
    for m in range(-nmax, nmax + 1):
        for n in range(-nmax, nmax + 1):
            total += math.exp(-math.pi * alpha * A2 * (m * m + m * n + n * n))
    return total


def count_tri(radius: float) -> int:
    nmax = int(radius * 2) + 3
    r2 = radius * radius
    return sum(
        1
        for m in range(-nmax, nmax + 1)
        for n in range(-nmax, nmax + 1)
        if A2 * (m * m + m * n + n * n) <= r2
    )


def main() -> None:
    print("== Poisson (controle positif / negatif) ==")
    for a in (0.5, 1.0, 2.0, 3.0):
        lhs = theta_tri(a)
        rhs = theta_tri(1.0 / a) / a
        wrong = theta_tri(1.0 / a)
        print(f"A   a={a}: Theta={lhs:.12f}  a^-1 Theta(1/a)={rhs:.12f}  diff={abs(lhs-rhs):.2e}  sans facteur diff={abs(lhs-wrong):.2e}")
        lz, rz = theta_z2(a), theta_z2(1.0 / a) / a
        print(f"Z^2 a={a}: Theta={lz:.12f}  a^-1 Theta(1/a)={rz:.12f}  diff={abs(lz-rz):.2e}")
    print("== Theta_A <= Theta_Z2 ==")
    ok = True
    for a in (0.1, 0.3, 0.5, 0.8, 1.0, 1.5, 2.0, 5.0):
        ta, tz = theta_tri(a), theta_z2(a)
        ok = ok and ta <= tz + 1e-12
        print(f"a={a}: Theta_A={ta:.9f}  Theta_Z2={tz:.9f}  A<=Z2: {ta <= tz + 1e-12}")
    print("all ok:", ok)
    print("== comptage N(R)/(pi R^2) ==")
    for r in (5.0, 20.0, 80.0):
        print(f"R={r}: N={count_tri(r)}  ratio={count_tri(r) / (math.pi * r * r):.6f}")
    print("== signes des derivees ==")
    t = sp.symbols("t", positive=True)
    for name, f in (("exp(-sqrt t)", sp.exp(-sp.sqrt(t))), ("cos t (controle negatif)", sp.cos(t))):
        signs = []
        for n in range(0, 9):
            d = (-1) ** n * sp.diff(f, t, n)
            signs.append(all(float(d.subs(t, v)) >= 0 for v in (0.01, 0.5, 1, 3, 10, 50)))
        print(name, signs)


if __name__ == "__main__":
    main()
