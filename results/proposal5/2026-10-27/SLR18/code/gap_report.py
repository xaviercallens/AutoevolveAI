"""Diagnostic (Tier X): list the uncovered intervals of a state file at radius rn/rd, with the
nearest small-denominator rational to each gap midpoint."""
from __future__ import annotations

import sys
from fractions import Fraction

import numpy as np

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from cover_ls import union_complement  # noqa: E402


def main() -> None:
    st, rn, rd = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    d = rn / rd
    rows = [ln.split() for ln in open(st).read().splitlines() if ln.strip()]
    v = np.array([float(r[0]) for r in rows])
    s = np.array([float(r[1]) for r in rows])
    L, H = [], []
    for vi, si in zip(v, s):
        k = np.arange(int(vi))
        c = (k - si) / vi
        c = c - np.floor(c)
        L.append(c - d / vi)
        H.append(c + d / vi)
    a, b = union_complement(np.concatenate(L), np.concatenate(H))
    print("velocities:", sorted(int(x) for x in v))
    for x, y in zip(a, b):
        m = 0.5 * (x + y)
        print(f"gap [{x:.6f},{y:.6f}] len={y-x:.2e} mid~{Fraction(m).limit_denominator(200)}")


if __name__ == "__main__":
    main()
