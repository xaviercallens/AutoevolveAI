"""Diameter of one spherical triangle of the tetrahedral partition of the radius-1/2 sphere:
dense sampling of the whole triangle (boundary + interior), compared with sigma_3."""
import math
import random

import numpy as np

V = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1]], dtype=float) / math.sqrt(3)
rng = np.random.default_rng(1)
# boundary samples (great-circle arcs between vertices) + interior samples
pts = []
for a, b in [(0, 1), (1, 2), (0, 2)]:
    for s in np.linspace(0, 1, 2001):
        p = (1 - s) * V[a] + s * V[b]
        pts.append(p / np.linalg.norm(p))
w = rng.dirichlet([1, 1, 1], 4000)
for x in w:
    p = x @ V
    pts.append(p / np.linalg.norm(p))
P = 0.5 * np.array(pts)
best = 0.0
for i in range(0, len(P), 500):
    d = np.linalg.norm(P[i:i + 500, None, :] - P[None, :, :], axis=2)
    best = max(best, d.max())
s3 = math.sqrt((3 + math.sqrt(3)) / 6)
print("sampled diam", best, "sigma3", s3, "diff", s3 - best)
