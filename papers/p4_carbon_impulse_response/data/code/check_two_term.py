"""Tier X: IRF h = a0 + a1 exp(-t/tau) (two terms) with the staircase recipe, plus a tiny sweep of how many maxima appear."""
import sys
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
from k3lib import IRF, Path as P

irf = IRF(F(1, 2), [F(1, 2)], [F(50)])
for B, z3 in [(F(95, 100), 400), (F(98, 100), 600), (F(8, 10), 300)]:
    p = P(steps=[(F(0), F(1)), (F(10), -B), (F(z3), -(1 - B))])
    ts = np.linspace(0.01, z3 + 400, 8000)
    u = np.array([p.u_float(irf, t) for t in ts])
    d = np.diff(u)
    print("B", B, "z3", z3, "maxima at", [round(float(ts[i + 1]), 1) for i in range(len(d) - 1) if d[i] > 0 >= d[i + 1]],
          "minima at", [round(float(ts[i + 1]), 1) for i in range(len(d) - 1) if d[i] < 0 <= d[i + 1]])
