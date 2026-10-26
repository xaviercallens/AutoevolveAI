"""N1 control: f(x) = (1 - cos x)/x^2 = int_0^1 (1 - u) cos(u x) du (sympy, exact), and the Arb helpers f_thin /
f_ball of n1_certify.py contain finely sampled float values of f, f' over random balls (Tier X sampling check).

usage: python -I n1_fcheck.py
"""

from __future__ import annotations

import math
import os
import random
import sys

import mpmath
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n1_certify as m  # noqa: E402


mpmath.mp.dps = 40


def f(x: float) -> float:
    X = mpmath.mpf(x)
    return 0.5 if x == 0 else float((1 - mpmath.cos(X)) / (X * X))


def fp(x: float) -> float:
    X = mpmath.mpf(x)
    return 0.0 if x == 0 else float((X * mpmath.sin(X) - 2 * (1 - mpmath.cos(X))) / X**3)


def main() -> None:
    u, x = sp.symbols("u x", positive=True)
    rep = sp.simplify(sp.integrate((1 - u) * sp.cos(u * x), (u, 0, 1)) - (1 - sp.cos(x)) / x**2)
    print("integral representation residual (sympy):", rep)
    rng = random.Random(1)
    bad = 0
    for _ in range(3000):
        c = rng.uniform(-25, 25)
        r = rng.choice([1e-4, 1e-3, 1e-2, 0.1, 0.5])
        F, F1 = m.f_ball(m.arb(c, r))
        for k in range(11):
            y = c - r + 2 * r * k / 10
            if not (F.lower() <= f(y) <= F.upper()):
                bad += 1
                print("f fail", c, r, y, f(y), F)
            if not (float(F1.lower()) - 1e-15 <= fp(y) <= float(F1.upper()) + 1e-15):
                bad += 1
                print("f' fail", c, r, y, fp(y), F1)
    print("sampled containment failures:", bad)


if __name__ == "__main__":
    main()
