"""A third, minimal implementation of E_zp for the Gaussian V(r) = exp(-pi a r^2) on a unit-covolume planar lattice of shape tau = x + i y.

Written for the paper (Section 2, Step 9) so a reader can reproduce the headline comparison in about 25 lines of numpy. It uses the Poisson form of the dynamical
matrix (Tier C, Step 7), a half-shifted uniform k-grid (which avoids k = 0) and an n^-3 Richardson extrapolation (the conical singularity at Gamma gives an
n^-3 error). It shares no code with the Rust crate or with the lane's Python scripts. All output is Tier X.
Run: /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I human_check.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def ezp_gauss(a: float, x: float, y: float, n: int, M: int = 7) -> tuple[float, float]:
    """Return (E_zp, min eigenvalue of D over the grid divided by |k|^2) for V = exp(-pi a r^2), half-shifted n x n k-grid."""
    b1 = np.array([math.sqrt(y), -x / math.sqrt(y)])  # dual basis, a_i . b_j = delta_ij, covolume 1
    b2 = np.array([0.0, 1.0 / math.sqrt(y)])
    i, j = np.meshgrid((np.arange(n) + 0.5) / n, (np.arange(n) + 0.5) / n, indexing="ij")
    kap = i[..., None] * b1 + j[..., None] * b2  # (n, n, 2), k = 2 pi kappa
    xi = np.array([m * b1 + p * b2 for m in range(-M, M + 1) for p in range(-M, M + 1)])  # dual lattice points
    q = xi[None, None, :, :] + kap[:, :, None, :]  # (n, n, G, 2)
    w = np.exp(-math.pi * (q**2).sum(-1) / a)
    d = np.einsum("ijg,ijga,ijgb->ijab", w, q, q)
    d0 = np.einsum("g,ga,gb->ab", np.exp(-math.pi * (xi**2).sum(-1) / a), xi, xi)
    d = (4 * math.pi**2 / a) * (d - d0)
    tr = d[..., 0, 0] + d[..., 1, 1]
    det = d[..., 0, 0] * d[..., 1, 1] - d[..., 0, 1] ** 2
    lam_min = 0.5 * (tr - np.sqrt(np.maximum(tr**2 - 4 * det, 0.0)))
    k2 = (2 * math.pi) ** 2 * (q**2).sum(-1).min(-1)  # |k|^2 for the nearest equivalent k (reduced to the Wigner-Seitz cell)
    ratio = float((lam_min / k2).min())
    e = 0.5 * np.sqrt(np.maximum(tr + 2 * np.sqrt(np.maximum(det, 0.0)), 0.0)).mean()
    return float(e), ratio


def richardson(a: float, x: float, y: float) -> tuple[float, float, float, float]:
    e1, r1 = ezp_gauss(a, x, y, 128)
    e2, r2 = ezp_gauss(a, x, y, 256)
    return e1, e2, (8 * e2 - e1) / 7, min(r1, r2)


def main() -> int:
    out = {}
    for name, (x, y) in {"triangular": (0.5, math.sqrt(3) / 2), "rhombic 0.5+0.966025i": (0.5, 0.966025403784),
                         "square (negative control)": (0.0, 1.0)}.items():
        e128, e256, ex, ratio = richardson(1.0, x, y)
        out[name] = {"x": x, "y": y, "E_n128": e128, "E_n256": e256, "E_richardson": ex, "min_lambda_over_k2_on_grid": ratio}
    out["dE_head_vs_tri"] = out["rhombic 0.5+0.966025i"]["E_richardson"] - out["triangular"]["E_richardson"]
    (HERE / "data" / "human_check.json").write_text(json.dumps(out, indent=1))
    for k, v in out.items():
        print(k, v)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
