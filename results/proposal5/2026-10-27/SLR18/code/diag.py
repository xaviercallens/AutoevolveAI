"""Diagnostic: does chain-LP descent recover the published optimum for [6] from small perturbations?"""
from __future__ import annotations

import os
import random
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from search import descend, float_gap  # noqa: E402


def main() -> None:
    v = np.arange(1, 7, dtype=float)
    s = np.array([0, 39, 37, 51, 62, 54]) / 67.0
    print("gap at published s", float_gap(v, s), 9 / 67)
    rng = random.Random(3)
    for sc in (0.001, 0.005, 0.02, 0.05):
        res = []
        for _ in range(10):
            s0 = np.mod(s + np.array([rng.gauss(0, sc) for _ in range(6)]), 1)
            _, d = descend(v, s0, rng)
            res.append(round(d, 5))
        print(sc, sorted(res))


if __name__ == "__main__":
    main()
