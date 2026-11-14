"""Design probe (not a lane result): can a degree-6 F0 with F0'(0)=0, F0''(0)>0 have a
slow divergence integral with 3 sign changes? Pure quadrature, no ODE, no cycle count."""

from __future__ import annotations

import json
import sys

import numpy as np
from numpy.polynomial import polynomial as P
from scipy.integrate import quad
from scipy.optimize import brentq


def sdi_curve(c: np.ndarray, xr_grid: np.ndarray) -> np.ndarray:
    f = np.array([0.0, 0.0, 0.5, *c])
    df = P.polyder(f)
    out = []
    xs = np.linspace(0.0, -10.0, 20001)
    dfv = P.polyval(xs, df)
    bad = np.where(dfv[1:] >= 0)[0]
    lim = bad[0] + 1 if bad.size else len(xs)
    for xr in xr_grid:
        if np.any(P.polyval(np.linspace(1e-9, xr, 400), df) <= 0):
            out.append(np.nan)
            continue
        fr = P.polyval(xr, f)
        gv = P.polyval(xs, f) - fr
        hit = np.where(gv[1:lim] > 0)[0]
        if hit.size == 0:
            out.append(np.nan)
            continue
        k = hit[0] + 1
        xl = brentq(lambda x: P.polyval(x, f) - fr, xs[k], xs[k - 1])
        val = quad(lambda x: P.polyval(x, df) ** 2 / x if x != 0 else 0.0, xl, xr,
                   limit=200, points=[0.0])[0]
        out.append(val)
    return np.array(out)


def nzeros(v: np.ndarray) -> int:
    v = v[np.isfinite(v)]
    return int(np.sum(np.sign(v[1:]) * np.sign(v[:-1]) < 0))


def main() -> int:
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
    rng = np.random.default_rng(seed)
    grid = np.linspace(0.02, 3.0, 150)
    best: dict = {"zeros": 0}
    scale = np.array([1.0, 1.0, 0.5, 0.3]) * (float(sys.argv[3]) if len(sys.argv) > 3 else 1.0)
    center = np.array(json.loads(sys.argv[4])) if len(sys.argv) > 4 else np.zeros(4)
    for trial in range(trials):
        c = center + rng.standard_normal(4) * scale
        v = sdi_curve(c, grid)
        if np.isfinite(v).sum() < 60:
            continue
        z = nzeros(v)
        if z > best["zeros"]:
            best = {"zeros": z, "trial": trial, "c3456": c.tolist()}
            print(json.dumps(best), flush=True)
        if z >= 3:
            break
    print("FINAL", json.dumps(best))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
