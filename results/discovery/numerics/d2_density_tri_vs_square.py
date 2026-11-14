"""D2 verifier numerics: per-point energy sum_{y in L\\0} h(|y|^2) for triangular vs square lattice at density rho."""
from __future__ import annotations

import math
from typing import Callable

import numpy as np

N = 400  # index range [-N, N]^2
j, k = np.meshgrid(np.arange(-N, N + 1, dtype=np.float64), np.arange(-N, N + 1, dtype=np.float64), indexing="ij")
mask = ~((j == 0) & (k == 0))

# covolume-1 lattices (density 1); same normalisation as upstream triangularPoint: sqrt(2/sqrt3) * (j + k/2, k sqrt3/2)
tri_n2 = (2 / math.sqrt(3)) * ((j + k / 2) ** 2 + (k * math.sqrt(3) / 2) ** 2)
sq_n2 = j ** 2 + k ** 2


def energy(n2: np.ndarray, rho: float, h: Callable[[np.ndarray], np.ndarray]) -> float:
    # lattice rho^{-1/2} L : squared norms n2 / rho
    return float(h(n2[mask] / rho).sum())


gauss = lambda t: np.exp(-t)  # noqa: E731
riesz4 = lambda t: t ** -2.0  # noqa: E731  (s = 4: |y|^{-4})

# positive control: covolume of the triangular normalisation is 1 (density 1): det of basis
b1 = math.sqrt(2 / math.sqrt(3)) * np.array([1.0, 0.0])
b2 = math.sqrt(2 / math.sqrt(3)) * np.array([0.5, math.sqrt(3) / 2])
print("triangular covolume", abs(b1[0] * b2[1] - b1[1] * b2[0]))
# positive control: square Riesz-4 sum at rho=1 = 4 zeta(2) beta(2) (Catalan G); truncation tail ~ 2 pi / (2 N^2)
G = 0.915965594177219015
print("square riesz4 rho=1 numeric", energy(sq_n2, 1.0, riesz4), "closed form", 4 * (math.pi ** 2 / 6) * G)
for name, h in [("exp(-t)", gauss), ("t^-2 (s=4)", riesz4)]:
    for rho in [0.25, 0.5, 1.0, 2.0, 4.0]:
        et, es = energy(tri_n2, rho, h), energy(sq_n2, rho, h)
        eu = energy(tri_n2, 1.0, h)
        print(f"{name:11s} rho={rho:<5} tri={et:.10g} square={es:.10g} tri<square={et < es} tri/square={et/es:.6f}"
              f" unscaled_tri={eu:.10g} unscaled<=tri_rho={eu <= et}")
# negative control: a deliberately worse lattice (rectangular 1 x ... covolume 1, aspect 2) must not beat triangular
rect_n2 = (j * math.sqrt(2)) ** 2 + (k / math.sqrt(2)) ** 2
for rho in [0.5, 2.0, 4.0]:
    print("rect(aspect2) exp rho", rho, energy(rect_n2, rho, gauss), ">= tri", energy(rect_n2, rho, gauss) >= energy(tri_n2, rho, gauss))
