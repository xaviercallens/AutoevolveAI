"""N1 Tier X: size of the a-derivative of the E'' Duffy integrand, int |d g/da| vs |d E''/da| (floating point).

usage: python -I n1_explore_da.py N A [A ...]
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from n1_explore import PI, duffy, hess_derivs, lattice, tau_dd  # noqa: E402


def gvals(a: float, pts: np.ndarray, ph: np.ndarray) -> np.ndarray:
    H, H1, H2 = hess_derivs(a, pts[:, 2], pts[:, 3], 0.0)
    _, tau2 = tau_dd([ph @ x for x in H], [ph @ x for x in H1], [ph @ x for x in H2])
    return 0.5 * tau2


def main() -> None:
    N = int(sys.argv[1])
    u, v, w = duffy(N)
    for s in sys.argv[2:]:
        a = float(s)
        pts = lattice(70.0 / (PI * a * 0.9))
        ph = 1 - np.cos(2 * PI * (np.outer(u, pts[:, 0]) + np.outer(v, pts[:, 1])))
        h = 1e-4
        ga = (gvals(a + h, pts, ph) - gvals(a - h, pts, ph)) / (2 * h)
        print(f"a={a} dE''/da={float((w * ga).sum()):.4f} int|g_a|={float((w * np.abs(ga)).sum()):.4f} "
              f"max|g_a|={float(np.abs(ga).max()):.2f}", flush=True)


if __name__ == "__main__":
    main()
