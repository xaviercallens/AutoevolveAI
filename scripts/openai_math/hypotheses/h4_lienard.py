#!/usr/bin/env python3
"""H4: search for limit cycles of classical Lienard systems x' = y - F(x), y' = -x.

Anchor: openai/math family 143 (Lean-formalized, Comparator challenge QuinticLienard): every
real polynomial F of degree <= 5 gives at most 2 limit cycles, and 2 is attained. Literature
(checked 2026-10-07): Lins-de Melo-Pugh (1977) conjectured at most [(n-1)/2] for degree n;
proved for n <= 4, open for n = 5 (so the upstream claim, if right, settles it), false for
n >= 6 (De Maesschalck-Dumortier 2011: degree 6 with 4 cycles; degree n >= 6 with at least
[(n-1)/2] + 2).

Instrument. The only equilibrium is the origin (y' = -x forces x = 0, then y = F(0)); we
shift F so F(0) = 0. Every periodic orbit surrounds the origin and meets the positive y-axis
exactly once, moving right (x' = y > 0 there). So limit cycles are the isolated zeros of the
displacement d(y0) = P(y0) - y0, where P is the first return to the positive y-axis. We
count sign changes of d on a log-spaced grid and confirm each by bisection to |interval| <
1e-7 relative. This is a LOWER bound: semistable cycles (even-order zeros), cycles outside
the grid and canard cycles at tiny parameters are missed.

Controls (preregistered):
* positive: F = 0.5 (x^3/3 - x) has exactly 1 limit cycle (van der Pol); the averaging-built
  F = eps (8x - 40/3 x^3 + 16/5 x^5), eps = 0.01, has 2 cycles of amplitude ~1 and ~2
  (first-order averaged function r/2 a1 + 3/8 a3 r^3 + 5/16 a5 r^5 = 4r - 5r^3 + r^5).
* negative: degree <= 4 has at most 1 limit cycle (theorem, Li-Llibre 2012 for degree 4);
  the instrument must never report 2 on any random degree-3/4 sample. A report of 2 means
  the instrument manufactures cycles.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
from numpy.polynomial import polynomial as P
from scipy.integrate import solve_ivp

REPO = Path(__file__).resolve().parents[3]
OUT_DIR = REPO / "results" / "openai_math" / "hypotheses" / "H4"


def return_map(coeffs: np.ndarray, y0: float, t_max: float = 400.0) -> float:
    """y-coordinate of the first return to the positive y-axis, or nan."""

    def rhs(_t: float, z: np.ndarray) -> list[float]:
        return [z[1] - P.polyval(z[0], coeffs), -z[0]]

    def cross(_t: float, z: np.ndarray) -> float:
        return z[0]

    cross.direction = 1.0  # type: ignore[attr-defined]
    cross.terminal = True  # type: ignore[attr-defined]

    def blowup(_t: float, z: np.ndarray) -> float:
        return 1e6 - abs(z[0]) - abs(z[1])

    blowup.terminal = True  # type: ignore[attr-defined]
    # start just right of the axis so the t=0 crossing is not detected
    sol = solve_ivp(rhs, (0.0, t_max), [1e-12 * max(1.0, y0), y0], method="DOP853",
                    rtol=1e-11, atol=1e-13, events=(cross, blowup))
    if sol.t_events[0].size == 0:
        return math.nan
    z = sol.y_events[0][0]
    return float(z[1]) if z[1] > 0 else math.nan


def displacement(coeffs: np.ndarray, y0: float) -> float:
    return return_map(coeffs, y0) - y0


def count_cycles(coeffs: np.ndarray, y_lo: float = 1e-3, y_hi: float = 50.0, grid: int = 160) -> list[float]:
    """Amplitudes (y-axis crossing) of confirmed sign changes of the displacement."""
    ys = np.geomspace(y_lo, y_hi, grid)
    ds = np.array([displacement(coeffs, y) for y in ys])
    roots: list[float] = []
    for i in range(grid - 1):
        a, b, da, db = ys[i], ys[i + 1], ds[i], ds[i + 1]
        if not (math.isfinite(da) and math.isfinite(db)) or da * db >= 0:
            continue
        for _ in range(60):
            mid = math.sqrt(a * b)
            dm = displacement(coeffs, mid)
            if not math.isfinite(dm):
                break
            if da * dm < 0:
                b, db = mid, dm
            else:
                a, da = mid, dm
            if (b - a) / b < 1e-7:
                break
        if math.isfinite(da) and math.isfinite(db) and da * db < 0:
            roots.append(math.sqrt(a * b))
    return roots


def van_der_pol() -> np.ndarray:
    return np.array([0.0, -0.5, 0.0, 0.5 / 3.0])


def averaged_two_cycle(eps: float = 0.01) -> np.ndarray:
    return eps * np.array([0.0, 8.0, 0.0, -40.0 / 3.0, 0.0, 16.0 / 5.0])


def random_poly(rng: np.random.Generator, degree: int, scale: float) -> np.ndarray:
    c = rng.standard_normal(degree + 1) * scale
    c[0] = 0.0
    if abs(c[degree]) < 1e-3:
        c[degree] = 1e-3
    return c


def melnikov_poly(rng: np.random.Generator, degree: int, eps: float) -> np.ndarray:
    """Odd part chosen so the first-order averaged function has prescribed simple zeros."""
    n_odd = (degree - 1) // 2  # number of positive roots we can prescribe
    roots = np.sort(rng.uniform(0.3, 3.0, n_odd)) ** 2  # in u = r^2
    poly_u = np.poly1d(np.poly(roots))  # monic, degree n_odd in u
    # averaged: sum_j a_{2j+1} c_{2j+1} r^{2j+1}, c_1=1/2, c_3=3/8, c_5=5/16, c_7=35/128
    cfac = {1: 0.5, 3: 3 / 8, 5: 5 / 16, 7: 35 / 128}
    c = np.zeros(degree + 1)
    ucoef = poly_u.coeffs[::-1]  # ascending in u
    for j, uc in enumerate(ucoef):
        c[2 * j + 1] = uc / cfac[2 * j + 1]
    even = rng.standard_normal(degree + 1)
    even[1::2] = 0.0
    even[0] = 0.0
    return eps * (c + rng.uniform(0, 2) * even)


@dataclass
class H4Result:
    budget_s: float
    elapsed_s: float
    positive_vdp_cycles: int
    positive_averaged_deg5_cycles: int
    negative_max_cycles_deg3_4: int
    negative_samples: int
    controls_pass: bool
    max_cycles: dict[str, int] = field(default_factory=dict)
    witnesses: dict[str, list[float]] = field(default_factory=dict)
    samples: dict[str, int] = field(default_factory=dict)
    contradicts_upstream_quintic: bool = False
    refutes_h4_degree6: bool = False


def run(budget_s: float, seed: int, n_negative: int) -> H4Result:
    t0 = time.time()
    rng = np.random.default_rng(seed)
    vdp = len(count_cycles(van_der_pol()))
    avg5 = len(count_cycles(averaged_two_cycle(), y_lo=0.05, y_hi=10.0))
    neg_max = 0
    for i in range(n_negative):
        deg = 3 + (i % 2)
        coeffs = melnikov_poly(rng, deg, 0.05) if i % 3 == 0 else random_poly(rng, deg, 1.0)
        neg_max = max(neg_max, len(count_cycles(coeffs, grid=80)))
    ok = vdp == 1 and avg5 == 2 and neg_max <= 1
    res = H4Result(budget_s, 0.0, vdp, avg5, neg_max, n_negative, ok)
    if ok:
        for deg in (5, 6):
            res.max_cycles[str(deg)] = 0
            res.samples[str(deg)] = 0
        i = 0
        while time.time() - t0 < budget_s:
            deg = 5 if i % 2 == 0 else 6
            mode = i % 4
            if mode < 2:
                coeffs = melnikov_poly(rng, deg, float(10 ** rng.uniform(-3, -0.5)))
            else:
                coeffs = random_poly(rng, deg, float(10 ** rng.uniform(-1, 0.5)))
            roots = count_cycles(coeffs, grid=100)
            res.samples[str(deg)] += 1
            if len(roots) > res.max_cycles[str(deg)]:
                res.max_cycles[str(deg)] = len(roots)
                res.witnesses[str(deg)] = [float(x) for x in coeffs] + [float("nan")] + roots
            i += 1
        res.contradicts_upstream_quintic = res.max_cycles["5"] >= 3
        res.refutes_h4_degree6 = res.max_cycles["6"] >= 5
    res.elapsed_s = round(time.time() - t0, 1)
    return res


def main() -> int:
    p = argparse.ArgumentParser(description="H4 Lienard limit-cycle search")
    p.add_argument("--budget-s", type=float, default=600.0)
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--n-negative", type=int, default=40)
    args = p.parse_args()
    res = run(args.budget_s, args.seed, args.n_negative)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"result_seed{args.seed}.json").write_text(json.dumps(asdict(res), indent=2) + "\n")
    print(json.dumps({k: v for k, v in asdict(res).items() if k != "witnesses"}))
    return 0 if res.controls_pass else 3


if __name__ == "__main__":
    raise SystemExit(main())
