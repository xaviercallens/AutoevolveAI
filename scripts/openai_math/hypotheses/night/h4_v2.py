#!/usr/bin/env python3
"""H4 v2: limit cycles of classical Lienard systems x' = y - F(x), y' = -x, slow-fast regime.

Hypothesis H4 (lab, conjecture b): degree-6 classical Lienard systems have at most 4 limit
cycles. Upstream openai/math family 143 (a claim by another model, Lean-stated, not compiled
here): degree <= 5 has at most 2.

What changed from v1 (scripts/openai_math/hypotheses/h4_lienard.py)
1. Integration is a hand-driven step loop over scipy's OdeSolver classes (Radau, DOP853,
   LSODA). The wall-clock deadline and a step cap are checked after EVERY step, so a stiff
   sample returns status "timeout" instead of hanging. Timeouts are recorded, never counted.
2. Two-sided shooting. For a start (0, Y) on the positive y-axis we integrate forward and
   backward in time to the first landing on the negative y-axis {x = 0, y < 0}. Every periodic
   orbit of a classical Lienard system surrounds the origin and meets each half-axis once, so
   periodic orbits through (0, Y) are exactly the zeros of D(Y) = fwd(Y) - bwd(Y). Forward
   time crosses the attracting slow branch (x > 0), backward time crosses the repelling slow
   branch (x < 0) where reverse time is contracting; neither direction integrates against an
   exponentially expanding branch. (A forward-only return map would.)
3. Slow-fast family (De Maesschalck-Dumortier 2011 mechanism, reconstructed: the paper's PDF
   was not reachable, see the preregistration). x' = y - (a x + F0(x)), y' = -eps x with
   F0(0) = F0'(0) = 0, F0''(0) = 1. With Y = y / sqrt(eps), s = sqrt(eps) t this is the
   CLASSICAL Lienard system x' = Y - F(x), Y' = -x with F = (a x + F0(x)) / sqrt(eps), same
   degree. Canard cycles (one fast orbit at height F0(x_R) from x_L < 0 to x_R > 0, slow
   segment through the turning point) are governed by the slow divergence integral
   I(x_R) = int_{x_L}^{x_R} F0'(x)^2 / x dx, F0(x_L) = F0(x_R). k simple zeros of I give k + 1
   limit cycles for eps small and a tuned in an exponentially thin window.
4. Tuning of the breaking parameter a is a 1-D root find, not a sample: A(Y) is the value of a
   for which the cycle through (0, Y) exists (D(Y; a) = 0). The number of cycles at a fixed a*
   equals the number of solutions of A(Y) = a*; a* is chosen from the A curve and then the
   cycles at that ONE parameter point are counted and confirmed directly. Cycles found at
   different values of a are never added up.

Confirmation of a cycle (grid bracket [Y1, Y2] of a sign change of D; the root is then
located by bisection, but the checks below run at the GRID ends, where |D| is not ~0):
* primary: Radau rtol 1e-10, atol 1e-12;
* the signs of D at Y1 and Y2 are recomputed with DOP853 rtol 1e-12, atol 1e-14 and with
  Radau rtol 1e-11, atol 1e-13; all three must agree;
* |D| at both ends must exceed 10 x the largest |difference| between the three evaluations.
A cycle failing any check is "unconfirmed" and not counted.

This is a lower-bound instrument: semistable cycles (even-order zeros of D) are invisible.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np
from numpy.polynomial import polynomial as P
from scipy.integrate import DOP853, LSODA, Radau
from scipy.optimize import brentq

REPO = Path(__file__).resolve().parents[4]
LANE = REPO / "results" / "openai_math" / "hypotheses" / "night_2026-10-07" / "H4"

SOLVERS = {"Radau": Radau, "DOP853": DOP853, "LSODA": LSODA}
PRIMARY = ("Radau", 1e-10, 1e-12)
CHECKS = (("DOP853", 1e-12, 1e-14), ("Radau", 1e-11, 1e-13))
BLOWUP = 1e6


# --------------------------------------------------------------------------- integration

@dataclass
class Landing:
    status: str  # "ok" | "timeout" | "max_steps" | "blowup" | "failed" | "no_return"
    y: float = math.nan
    steps: int = 0
    seconds: float = 0.0


def land(coeffs: np.ndarray, y_start: float, time_dir: int, method: str = "Radau",
         rtol: float = 1e-10, atol: float = 1e-12, deadline_s: float = 20.0,
         max_steps: int = 2_000_000, t_bound: float = 1e5) -> Landing:
    """Integrate x' = y - F(x), y' = -x from (0, y_start) in time direction time_dir (+1/-1)
    until the orbit first returns to the line x = 0 from the side it left. Returns the y of
    that landing. The deadline is checked after every solver step."""
    c = np.asarray(coeffs, dtype=float)
    dc = P.polyder(c)
    s = float(time_dir)

    def fun(_t: float, z: np.ndarray) -> np.ndarray:
        return s * np.array([z[1] - P.polyval(z[0], c), -z[0]])

    def jac(_t: float, z: np.ndarray) -> np.ndarray:
        return s * np.array([[-P.polyval(z[0], dc), 1.0], [-1.0, 0.0]])

    kwargs: dict = {"rtol": rtol, "atol": atol}
    if method in ("Radau", "LSODA"):
        kwargs["jac"] = jac
    t0 = time.monotonic()
    solver = SOLVERS[method](fun, 0.0, np.array([0.0, float(y_start)]), t_bound, **kwargs)
    side = 0.0
    steps = 0
    while True:
        if time.monotonic() - t0 > deadline_s:
            return Landing("timeout", steps=steps, seconds=time.monotonic() - t0)
        if steps >= max_steps:
            return Landing("max_steps", steps=steps, seconds=time.monotonic() - t0)
        if solver.status != "running":
            return Landing("no_return" if solver.status == "finished" else "failed",
                           steps=steps, seconds=time.monotonic() - t0)
        x_prev = float(solver.y[0])
        solver.step()
        steps += 1
        if solver.status == "failed":
            return Landing("failed", steps=steps, seconds=time.monotonic() - t0)
        x_new, y_new = float(solver.y[0]), float(solver.y[1])
        if not (math.isfinite(x_new) and math.isfinite(y_new)) or abs(x_new) + abs(y_new) > BLOWUP:
            return Landing("blowup", steps=steps, seconds=time.monotonic() - t0)
        if side == 0.0:
            # the side the orbit leaves to (x' = y_start - F(0) = y_start at the start)
            if x_new != 0.0:
                side = math.copysign(1.0, x_new)
            continue
        if side * x_prev > 0.0 and side * x_new <= 0.0:
            dense = solver.dense_output()
            ta, tb = solver.t_old, solver.t
            fa = float(dense(ta)[0])
            fb = float(dense(tb)[0])
            if fa * fb > 0.0:
                tstar = tb
            else:
                tstar = brentq(lambda t: float(dense(t)[0]), ta, tb, xtol=1e-15, rtol=1e-14)
            yl = float(dense(tstar)[1])
            return Landing("ok", y=yl, steps=steps, seconds=time.monotonic() - t0)


def two_sided(coeffs: np.ndarray, y0: float, method: str = "Radau", rtol: float = 1e-10,
              atol: float = 1e-12, deadline_s: float = 20.0) -> tuple[float, str]:
    """D(y0) = forward landing - backward landing on the negative y-axis.

    Outside the outermost attracting (repelling) cycle the backward (forward) orbit can escape
    to infinity in finite time and never land. Then the same-sign surrogate is used: with P the
    forward return map of the positive y-axis (increasing) and the second half-map decreasing,
    sign(D(y)) = -sign(P(y) - y) = sign(P^{-1}(y) - y). Status "ok" = two-sided, "ok_fr" /
    "ok_br" = forward / backward full-return surrogate."""
    f = land(coeffs, y0, +1, method, rtol, atol, deadline_s)
    b = land(coeffs, y0, -1, method, rtol, atol, deadline_s)
    if f.status == "ok" and b.status == "ok":
        if not (f.y < 0.0 and b.y < 0.0):
            return math.nan, "bad_side"
        return f.y - b.y, "ok"
    if "timeout" in (f.status, b.status):
        return math.nan, ("fwd_" + f.status) if f.status == "timeout" else ("bwd_" + b.status)
    if f.status == "ok":
        g = land(coeffs, f.y, +1, method, rtol, atol, deadline_s)
        if g.status == "ok" and g.y > 0.0:
            return -(g.y - y0), "ok_fr"
        return math.nan, "fr_" + g.status
    if b.status == "ok":
        g = land(coeffs, b.y, -1, method, rtol, atol, deadline_s)
        if g.status == "ok" and g.y > 0.0:
            return g.y - y0, "ok_br"
        return math.nan, "br_" + g.status
    return math.nan, "fwd_" + f.status + "_bwd_" + b.status


def full_return(coeffs: np.ndarray, y0: float, method: str = "DOP853", rtol: float = 1e-12,
                atol: float = 1e-14, deadline_s: float = 20.0) -> tuple[float, str]:
    """v1-style displacement P(y0) - y0 via two forward half-turns (cross-check only)."""
    h1 = land(coeffs, y0, +1, method, rtol, atol, deadline_s)
    if h1.status != "ok":
        return math.nan, "h1_" + h1.status
    h2 = land(coeffs, h1.y, +1, method, rtol, atol, deadline_s)
    if h2.status != "ok":
        return math.nan, "h2_" + h2.status
    return h2.y - y0, "ok"


# --------------------------------------------------------------------------- counting

@dataclass
class CycleCount:
    confirmed: list[float] = field(default_factory=list)
    evidence: list[dict] = field(default_factory=list)
    unconfirmed: list[dict] = field(default_factory=list)
    grid_points: int = 0
    statuses: dict[str, int] = field(default_factory=dict)
    seconds: float = 0.0
    hit_count_deadline: bool = False

    @property
    def n(self) -> int:
        return len(self.confirmed)


def _bump(d: dict[str, int], k: str) -> None:
    d[k] = d.get(k, 0) + 1


def confirm_bracket(coeffs: np.ndarray, ya: float, yb: float, deadline_s: float) -> tuple[bool, dict]:
    ev: dict = {"ya": ya, "yb": yb}
    vals_a, vals_b = [], []
    for m, r, a in (PRIMARY,) + CHECKS:
        da, sa = two_sided(coeffs, ya, m, r, a, deadline_s)
        db, sb = two_sided(coeffs, yb, m, r, a, deadline_s)
        ev[f"{m}_{r:g}"] = [da, db, sa, sb]
        vals_a.append(da)
        vals_b.append(db)
    if not all(math.isfinite(v) for v in vals_a + vals_b):
        ev["reason"] = "non_finite"
        return False, ev
    sa_set = {math.copysign(1.0, v) for v in vals_a}
    sb_set = {math.copysign(1.0, v) for v in vals_b}
    if len(sa_set) != 1 or len(sb_set) != 1 or sa_set == sb_set:
        ev["reason"] = "sign_disagreement"
        return False, ev
    err_a = max(vals_a) - min(vals_a)
    err_b = max(vals_b) - min(vals_b)
    ev["err"] = [err_a, err_b]
    if min(abs(v) for v in vals_a) <= 10 * err_a or min(abs(v) for v in vals_b) <= 10 * err_b:
        ev["reason"] = "below_error_margin"
        return False, ev
    return True, ev


def count_cycles(coeffs: np.ndarray, y_lo: float, y_hi: float, grid: int = 120,
                 deadline_s: float = 20.0, count_deadline_s: float = 400.0,
                 bisect_rel: float = 1e-9, method: str = "Radau", confirm: bool = True,
                 ys: np.ndarray | None = None) -> CycleCount:
    """Confirmed sign changes of the two-sided displacement on a log grid in [y_lo, y_hi]."""
    t0 = time.monotonic()
    out = CycleCount()
    m, r, a = PRIMARY if method == "Radau" else (method, 1e-12, 1e-14)
    ys = np.geomspace(y_lo, y_hi, grid) if ys is None else np.asarray(ys, dtype=float)
    out.grid_points = len(ys)
    ds = []
    for y in ys:
        if time.monotonic() - t0 > count_deadline_s:
            out.hit_count_deadline = True
            ds.append(math.nan)
            _bump(out.statuses, "count_deadline")
            continue
        d, st = two_sided(coeffs, float(y), m, r, a, deadline_s)
        _bump(out.statuses, st)
        ds.append(d)
    for i in range(len(ys) - 1):
        ya, yb, da, db = float(ys[i]), float(ys[i + 1]), ds[i], ds[i + 1]
        if not (math.isfinite(da) and math.isfinite(db)) or da * db >= 0:
            continue
        ga, gb = ya, yb  # grid bracket: confirmation is done here, where |D| is not ~0
        for _ in range(80):
            if (yb - ya) / yb < bisect_rel:
                break
            mid = math.sqrt(ya * yb)
            dm, st = two_sided(coeffs, mid, m, r, a, deadline_s)
            if not math.isfinite(dm):
                break
            if da * dm < 0:
                yb, db = mid, dm
            else:
                ya, da = mid, dm
        if not confirm:
            out.confirmed.append(math.sqrt(ya * yb))
            continue
        ok, ev = confirm_bracket(coeffs, ga, gb, deadline_s)
        ev["root"] = math.sqrt(ya * yb)
        if ok:
            out.confirmed.append(math.sqrt(ya * yb))
            out.evidence.append(ev)
        else:
            out.unconfirmed.append(ev)
    out.seconds = round(time.monotonic() - t0, 2)
    return out


# --------------------------------------------------------------------------- controls (v1)

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
    n_odd = (degree - 1) // 2
    roots = np.sort(rng.uniform(0.3, 3.0, n_odd)) ** 2
    ucoef = np.poly(roots)[::-1]
    cfac = {1: 0.5, 3: 3 / 8, 5: 5 / 16, 7: 35 / 128}
    c = np.zeros(degree + 1)
    for j, uc in enumerate(ucoef):
        c[2 * j + 1] = uc / cfac[2 * j + 1]
    even = rng.standard_normal(degree + 1)
    even[1::2] = 0.0
    even[0] = 0.0
    return eps * (c + rng.uniform(0, 2) * even)


# --------------------------------------------------------------------------- slow-fast

def f0_poly(c_high: list[float]) -> np.ndarray:
    """F0 = x^2/2 + c3 x^3 + ... (ascending coefficients)."""
    return np.array([0.0, 0.0, 0.5, *[float(v) for v in c_high]])


def classical_coeffs(f0: np.ndarray, a: float, eps: float) -> np.ndarray:
    """Classical Lienard F = (a x + F0(x)) / sqrt(eps); same degree as F0."""
    c = np.array(f0, dtype=float).copy()
    c[1] += a
    return c / math.sqrt(eps)


def sdi_domain(f0: np.ndarray, x_max: float = 3.0, n: int = 30001) -> tuple[float, float]:
    """(x_left_lim, x_right_lim): F0' < 0 on (x_left_lim, 0), F0' > 0 on (0, x_right_lim)."""
    df = P.polyder(f0)
    xr = np.linspace(0.0, x_max, n)[1:]
    xl = np.linspace(0.0, -x_max, n)[1:]
    pr = np.where(P.polyval(xr, df) <= 0)[0]
    pl = np.where(P.polyval(xl, df) >= 0)[0]
    return (float(xl[pl[0]]) if pl.size else -x_max, float(xr[pr[0]]) if pr.size else x_max)


SDI_X_MAX = 3.0
SDI_NOISE = 1e-9
CANARD_BEYOND = 1.1  # canard family searched up to 1.1 x the last SDI zero


def sdi(f0: np.ndarray, x_r: float, x_max: float = SDI_X_MAX,
        domain: tuple[float, float] | None = None) -> tuple[float, float, float]:
    """(I(x_R), x_L, J(x_R)) with I = int_{x_L}^{x_R} F0'(x)^2/x dx computed exactly as a
    polynomial integral (F0'(x) = x Q(x), integrand x Q(x)^2) and J = int |x| Q^2 dx its
    absolute scale (|I| <= SDI_NOISE * J is treated as numerically zero); nan if x_R is not
    admissible (F0' must keep its sign on [x_L, 0) and (0, x_R], both inside |x| < x_max)."""
    lo, hi = sdi_domain(f0, x_max) if domain is None else domain
    if not (0.0 < x_r < hi):
        return math.nan, math.nan, math.nan
    fr = float(P.polyval(x_r, f0))
    g = lambda x: float(P.polyval(x, f0)) - fr  # noqa: E731
    if g(lo) < 0.0:
        return math.nan, math.nan, math.nan
    x_l = brentq(g, lo, -1e-14, xtol=1e-15, rtol=1e-15)
    q = P.polydiv(P.polyder(f0), np.array([0.0, 1.0]))[0]
    integrand = P.polymul(np.array([0.0, 1.0]), P.polymul(q, q))
    anti = P.polyint(integrand)
    a0 = float(P.polyval(0.0, anti))
    val = float(P.polyval(x_r, anti) - P.polyval(x_l, anti))
    scale = float((P.polyval(x_r, anti) - a0) + (P.polyval(x_l, anti) - a0))
    return val, x_l, scale


def sdi_profile(f0: np.ndarray, n: int = 400, x_max: float = SDI_X_MAX) -> dict:
    """Sign changes of I on a grid of admissible x_R (values below the noise floor dropped)."""
    lo, hi = sdi_domain(f0, x_max)
    xs = np.linspace(hi * 1e-3, hi * 0.999, n)
    trip = [sdi(f0, float(x), x_max, (lo, hi)) for x in xs]
    vals = np.array([t[0] for t in trip])
    scl = np.array([t[2] for t in trip])
    fin = np.isfinite(vals)
    sig = fin & (np.abs(vals) > SDI_NOISE * np.where(np.isfinite(scl), scl, np.inf))
    xs_f, v_f = xs[sig], vals[sig]
    zeros = []
    for i in range(len(v_f) - 1):
        if v_f[i] * v_f[i + 1] < 0:
            zeros.append(float(brentq(lambda x: sdi(f0, x, x_max, (lo, hi))[0], xs_f[i], xs_f[i + 1])))
    extrema = []
    for k in range(len(zeros) + 1):
        lo_x = zeros[k - 1] if k > 0 else xs_f[0] if xs_f.size else math.nan
        hi_x = zeros[k] if k < len(zeros) else xs_f[-1] if xs_f.size else math.nan
        seg = v_f[(xs_f >= lo_x) & (xs_f <= hi_x)] if xs_f.size else np.array([])
        if seg.size:
            extrema.append(float(seg[np.argmax(np.abs(seg))]))
    adm = float(xs[fin][-1]) if fin.any() else math.nan
    x_hi = min(0.97 * adm, CANARD_BEYOND * zeros[-1]) if zeros else 0.97 * adm
    j_hi = sdi(f0, x_hi, x_max, (lo, hi))[2] if math.isfinite(x_hi) else math.nan
    k = len(zeros)
    strength = (min(abs(v) for v in extrema[:k]) / j_hi
                if k and len(extrema) >= k and math.isfinite(j_hi) and j_hi > 0 else 0.0)
    return {"x_right_lim": hi, "x_left_lim": lo, "admissible_points": int(fin.sum()),
            "significant_points": int(sig.sum()), "sign_changes": k, "zeros_xR": zeros,
            "segment_extrema_I": extrema, "x_hi": x_hi, "J_hi": j_hi, "strength": float(strength),
            "max_abs_I": float(np.max(np.abs(v_f))) if v_f.size else math.nan}


def sdi_balance(prof: dict) -> float:
    """min/max of |I| over the segment extrema that precede the last zero (the segments a
    level line must cross twice); 1 = perfectly balanced, 0 = some feature negligible."""
    k = prof["sign_changes"]
    ext = [abs(v) for v in prof["segment_extrema_I"][:k]]
    if k == 0 or not ext or max(ext) == 0:
        return 0.0
    return float(min(ext) / max(ext))


def sdi_design(degree: int, seed: int, trials: int, scale: float = 1.0,
               center: list[float] | None = None, polish: int = 0) -> dict:
    """Random search in (c3..c_degree) for the most SDI sign changes, then (polish > 0) a
    random-walk hill climb on (sign_changes, strength). strength = min |I| over the segment
    extrema before the last zero divided by J(x_hi) = int |x| Q^2 over the largest searched
    canard: the canard window in a is ~exp(-J/eps) wide and must stay above double precision
    (J/eps <~ 30) while the SDI structure needs |I_ext|/eps >> 1. Theory only, no ODE."""
    rng = np.random.default_rng(seed)
    base = np.array([1.0, 1.0, 0.5, 0.3, 0.2][: degree - 2]) * scale
    cen = np.zeros(degree - 2) if center is None else np.array(center, dtype=float)
    best: dict = {"sign_changes": -1, "strength": 0.0, "balance": 0.0}
    hist: dict[int, int] = {}

    def score(c: np.ndarray) -> dict | None:
        if degree % 2 == 0 and c[-1] <= 0:
            return None
        prof = sdi_profile(f0_poly(c.tolist()), n=150)
        if prof["admissible_points"] < 40:
            return None
        return {"sign_changes": prof["sign_changes"], "strength": prof["strength"],
                "balance": sdi_balance(prof), "c_high": c.tolist(), "profile": prof}

    def better(s: dict, b: dict) -> bool:
        return (s["sign_changes"], s["strength"]) > (b["sign_changes"], b["strength"])

    if center is not None:
        s0 = score(cen)
        if s0 is not None:
            best = s0
    for _ in range(trials):
        s = score(cen + rng.standard_normal(degree - 2) * base)
        if s is None:
            continue
        hist[s["sign_changes"]] = hist.get(s["sign_changes"], 0) + 1
        if better(s, best):
            best = s
    step = 0.05
    for it in range(polish):
        if "c_high" not in best:
            break
        s = score(np.array(best["c_high"]) + rng.standard_normal(degree - 2) * step * np.abs(base))
        if s is not None and s["sign_changes"] >= best["sign_changes"] and better(s, best):
            best = s
        if it % 200 == 199:
            step *= 0.7
    return {"degree": degree, "seed": seed, "trials": trials, "polish": polish,
            "histogram": hist, "best": best}


CURVE_SOLVER = ("DOP853", 1e-12, 1e-14)


def canard_x_hi(f0: np.ndarray, beyond: float = CANARD_BEYOND) -> float:
    """Largest x_R of the canard family that is searched: `beyond` x the last SDI zero (or
    97% of the admissible range when I has no zero), never past the admissible range."""
    dom = sdi_domain(f0)
    lim = dom[1]
    xs = np.linspace(lim * 1e-3, lim * 0.999, 400)
    ok = [float(x) for x in xs if math.isfinite(sdi(f0, float(x), SDI_X_MAX, dom)[0])]
    adm = max(ok) if ok else lim
    zeros = sdi_profile(f0)["zeros_xR"]
    return min(adm * 0.97, beyond * zeros[-1]) if zeros else adm * 0.97


def canard_y_range(f0: np.ndarray, eps: float, frac_lo: float = 0.02, frac_hi: float = 1.0) -> tuple[float, float]:
    """Classical Y range of the canard family: Y = F0(x_R)/sqrt(eps), x_R in
    [frac_lo, frac_hi] x canard_x_hi."""
    hi = canard_x_hi(f0)
    y_lo = float(P.polyval(frac_lo * hi, f0)) / math.sqrt(eps)
    y_hi = float(P.polyval(frac_hi * hi, f0)) / math.sqrt(eps)
    return y_lo, y_hi


def _d_at(f0: np.ndarray, eps: float, a: float, y_t: float, deadline_s: float) -> tuple[float, str]:
    m, r, at = CURVE_SOLVER
    return two_sided(classical_coeffs(f0, a, eps), y_t, m, r, at, deadline_s)


def a_root(f0: np.ndarray, eps: float, y_t: float, a_lo: float, a_hi: float,
           deadline_s: float = 20.0, iters: int = 70) -> dict:
    """Bisection in a for D(y_t; a) = 0 (the cycle through (0, y_t) exists). Search aid only,
    run with CURVE_SOLVER; cycle counts are confirmed separately at one fixed a."""
    dl, sl = _d_at(f0, eps, a_lo, y_t, deadline_s)
    dh, sh = _d_at(f0, eps, a_hi, y_t, deadline_s)
    if not (math.isfinite(dl) and math.isfinite(dh)) or dl * dh >= 0:
        return {"y": y_t, "a": math.nan, "status": f"no_bracket:{sl}:{sh}:{dl:.3g}:{dh:.3g}"}
    lo, hi = a_lo, a_hi
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if mid in (lo, hi):
            break
        dm, sm = _d_at(f0, eps, mid, y_t, deadline_s)
        if not math.isfinite(dm):
            return {"y": y_t, "a": math.nan, "status": "mid_" + sm}
        if dm * dl < 0:
            hi, dh = mid, dm
        else:
            lo, dl = mid, dm
    return {"y": y_t, "a": 0.5 * (lo + hi), "a_lo": lo, "a_hi": hi, "status": "ok"}


def a_bracket(f0: np.ndarray, eps: float, y_t: float, a_grid: np.ndarray,
              deadline_s: float = 20.0) -> tuple[tuple[float, float] | None, int]:
    """First sign change of D(y_t; a) on a_grid, and the number of sign changes seen."""
    vals = [_d_at(f0, eps, float(a), y_t, deadline_s)[0] for a in a_grid]
    found = None
    n = 0
    for i in range(len(a_grid) - 1):
        if math.isfinite(vals[i]) and math.isfinite(vals[i + 1]) and vals[i] * vals[i + 1] < 0:
            n += 1
            if found is None:
                found = (float(a_grid[i]), float(a_grid[i + 1]))
    return found, n


def ranked_levels(curve: list[dict], top: int = 3) -> list[tuple[float, int]]:
    """Up to `top` distinct levels a (midpoints between sorted sampled A values), ranked by how
    often the sampled A(Y) curve crosses them (ties -> the level met first in sorted order).
    Levels with the same crossing count that are adjacent midpoints are one level (the first)."""
    a = np.array([c["a"] for c in curve if math.isfinite(c["a"])])
    if a.size < 2:
        return []
    srt = np.unique(a)
    cands = 0.5 * (srt[1:] + srt[:-1])
    counts = []
    for lv in cands:
        sg = np.sign(a - lv)
        counts.append(int(np.sum(sg[1:] * sg[:-1] < 0)))
    runs: list[tuple[float, int]] = []
    for j, (lv, n) in enumerate(zip(cands, counts)):
        if j > 0 and counts[j - 1] == n:
            continue
        runs.append((float(lv), n))
    runs.sort(key=lambda t: -t[1])
    return runs[:top]


def best_level(curve: list[dict]) -> tuple[float, int]:
    """Level a* that the sampled A(Y) curve crosses most often (midpoints between values)."""
    r = ranked_levels(curve, 1)
    return r[0] if r else (math.nan, 0)


def a_resolution_ulps(curve: list[dict]) -> float:
    """(max A - min A) / ulp(median A): below 64 the A curve is at double-precision noise."""
    a = np.array([c["a"] for c in curve if math.isfinite(c["a"])])
    if a.size < 2:
        return math.nan
    return float((a.max() - a.min()) / np.spacing(abs(float(np.median(a)))))


# --------------------------------------------------------------------------- stages

def _write(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=float) + "\n")


POSITIVE_CONTROLS = {"vdp": (van_der_pol, 1e-3, 50.0, 1), "avg_quintic": (averaged_two_cycle, 0.05, 10.0, 2)}


def negative_samples(seed: int, n: int) -> list[tuple[int, np.ndarray]]:
    """The preregistered random degree-3/4 negative-control samples (v1 generator)."""
    rng = np.random.default_rng(seed)
    out = []
    for i in range(n):
        deg = 3 + (i % 2)
        out.append((deg, melnikov_poly(rng, deg, 0.05) if i % 3 == 0 else random_poly(rng, deg, 1.0)))
    return out


def stage_control_part(out: Path, part: str, seed: int, n_negative: int, idx: list[int],
                       deadline_s: float) -> dict:
    """One resumable piece of the instrument controls. Every count is run with the primary
    Radau two-sided map (with confirmation) AND with DOP853 two-sided (no confirmation)."""
    res: dict = {"part": part, "seed": seed}
    t0 = time.monotonic()
    if part in POSITIVE_CONTROLS:
        mk, lo, hi, expect = POSITIVE_CONTROLS[part]
        c = mk()
        r = count_cycles(c, lo, hi, grid=100, deadline_s=deadline_s, count_deadline_s=420.0)
        d = count_cycles(c, lo, hi, grid=100, deadline_s=deadline_s, method="DOP853", confirm=False)
        fr = [[full_return(c, y * (1 - 1e-4))[0], full_return(c, y * (1 + 1e-4))[0]] for y in r.confirmed]
        res.update({"expect": expect, "radau_confirmed": r.confirmed, "dop853": d.confirmed,
                    "unconfirmed": r.unconfirmed, "statuses": r.statuses,
                    "hit_count_deadline": r.hit_count_deadline, "full_return_at_roots": fr})
        res["pass"] = (len(r.confirmed) == expect and len(d.confirmed) == expect
                       and not r.hit_count_deadline
                       and all(abs(x - y) / y < 1e-6 for x, y in zip(r.confirmed, d.confirmed))
                       and all(fa * fb < 0 for fa, fb in fr))
    elif part == "negative":
        samples = negative_samples(seed, n_negative)
        neg = []
        for i in idx:
            deg, c = samples[i]
            r = count_cycles(c, 1e-3, 50.0, grid=60, deadline_s=deadline_s, count_deadline_s=200.0)
            d = count_cycles(c, 1e-3, 50.0, grid=60, deadline_s=deadline_s, count_deadline_s=200.0,
                             method="DOP853", confirm=False)
            neg.append({"i": i, "deg": deg, "coeffs": c.tolist(), "radau": r.n, "dop853": d.n,
                        "radau_unconfirmed": len(r.unconfirmed), "statuses": r.statuses,
                        "hit_count_deadline": r.hit_count_deadline})
        res["negative"] = neg
        res["pass"] = all(q["radau"] <= 1 and q["dop853"] <= 1 for q in neg)
    else:
        raise ValueError(part)
    res["seconds"] = round(time.monotonic() - t0, 1)
    _write(out, res)
    return res


def stage_curve(out: Path, f0: np.ndarray, eps: float, n_y: int, a_half_width: float,
                deadline_s: float, idx: list[int]) -> dict:
    """A(Y) samples for grid indices idx (resumable: one file per chunk)."""
    y_lo, y_hi = canard_y_range(f0, eps)
    ys = np.geomspace(y_lo, y_hi, n_y)
    a_grid = np.linspace(-a_half_width, a_half_width, 41)
    pts = []
    t0 = time.monotonic()
    for i in idx:
        y = float(ys[i])
        br, n_sc = a_bracket(f0, eps, y, a_grid, deadline_s)
        if br is None:
            pts.append({"i": i, "y": y, "a": math.nan, "status": "no_bracket_on_grid"})
            continue
        r = a_root(f0, eps, y, br[0], br[1], deadline_s)
        r["i"] = i
        r["a_grid_sign_changes"] = n_sc
        pts.append(r)
    res = {"eps": eps, "f0": f0.tolist(), "n_y": n_y, "y_lo": y_lo, "y_hi": y_hi,
           "a_half_width": a_half_width, "points": pts, "seconds": round(time.monotonic() - t0, 1)}
    _write(out, res)
    return res


def stage_count(out: Path, coeffs: np.ndarray, y_lo: float, y_hi: float, grid: int,
                deadline_s: float, count_deadline_s: float, meta: dict) -> dict:
    r = count_cycles(coeffs, y_lo, y_hi, grid=grid, deadline_s=deadline_s,
                     count_deadline_s=count_deadline_s)
    res = {**meta, "classical_coeffs": coeffs.tolist(), "degree": int(len(coeffs) - 1),
           "y_lo": y_lo, "y_hi": y_hi, "grid": grid, "confirmed": r.confirmed, "n_confirmed": r.n,
           "evidence": r.evidence,
           "unconfirmed": r.unconfirmed, "statuses": r.statuses, "seconds": r.seconds,
           "hit_count_deadline": r.hit_count_deadline}
    _write(out, res)
    return res


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    p = argparse.ArgumentParser(description="H4 v2 Lienard instrument")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("controls")
    c.add_argument("--part", choices=["vdp", "avg_quintic", "negative"], required=True)
    c.add_argument("--seed", type=int, default=2026)
    c.add_argument("--n-negative", type=int, default=20)
    c.add_argument("--idx", type=str, default="0:0")
    c.add_argument("--deadline-s", type=float, default=20.0)
    c.add_argument("--out", type=str, required=True)
    s = sub.add_parser("sdi-design")
    s.add_argument("--degree", type=int, required=True)
    s.add_argument("--seed", type=int, required=True)
    s.add_argument("--trials", type=int, default=1000)
    s.add_argument("--scale", type=float, default=1.0)
    s.add_argument("--center", type=str, default="")
    s.add_argument("--polish", type=int, default=0)
    s.add_argument("--out", type=str, required=True)
    k = sub.add_parser("curve")
    k.add_argument("--c-high", type=str, required=True)
    k.add_argument("--eps", type=float, required=True)
    k.add_argument("--n-y", type=int, default=48)
    k.add_argument("--a-half-width", type=float, default=0.2)
    k.add_argument("--deadline-s", type=float, default=20.0)
    k.add_argument("--idx", type=str, required=True, help="start:stop")
    k.add_argument("--out", type=str, required=True)
    n = sub.add_parser("count")
    n.add_argument("--c-high", type=str, required=True)
    n.add_argument("--eps", type=float, required=True)
    n.add_argument("--a", type=float, required=True)
    n.add_argument("--grid", type=int, default=160)
    n.add_argument("--deadline-s", type=float, default=20.0)
    n.add_argument("--count-deadline-s", type=float, default=480.0)
    n.add_argument("--out", type=str, required=True)
    pf = sub.add_parser("profile")
    pf.add_argument("--c-high", type=str, required=True)
    pf.add_argument("--ratios", type=str, default="[5, 10, 20, 30]")
    pf.add_argument("--out", type=str, required=True)
    lv = sub.add_parser("level")
    lv.add_argument("--curves", type=str, nargs="+", required=True)
    lv.add_argument("--out", type=str, required=True)
    args = p.parse_args()
    out = Path(args.out)
    if out.exists():
        print(json.dumps({"skip": str(out)}))
        return 0
    if args.cmd == "controls":
        i0, i1 = (int(v) for v in args.idx.split(":"))
        res = stage_control_part(out, args.part, args.seed, args.n_negative,
                                 list(range(i0, min(i1, args.n_negative))), args.deadline_s)
        print(json.dumps({k: v for k, v in res.items() if k in ("part", "pass", "seconds",
                                                                 "radau_confirmed", "dop853")}))
        return 0 if res["pass"] else 3
    if args.cmd == "level":
        pts: list[dict] = []
        meta: dict = {}
        for f in args.curves:
            d = json.loads(Path(f).read_text())
            meta = {k: d[k] for k in ("eps", "f0", "n_y", "y_lo", "y_hi")}
            pts.extend(d["points"])
        pts.sort(key=lambda q: q["i"])
        a_star, n_pred = best_level(pts)
        res_ulps = a_resolution_ulps(pts)
        res = {**meta, "curve_files": args.curves, "n_points": len(pts),
               "n_ok": sum(1 for q in pts if q["status"] == "ok"),
               "a_star": a_star, "predicted_crossings": n_pred,
               "top_levels": ranked_levels(pts, 3),
               "A_spread_ulps": res_ulps,
               "below_double_resolution": bool(not math.isfinite(res_ulps) or res_ulps < 64),
               "A_curve": [[q["y"], q["a"]] for q in pts]}
        _write(out, res)
        print(json.dumps({"a_star": a_star, "predicted_crossings": n_pred, "n_ok": res["n_ok"],
                          "top_levels": res["top_levels"], "A_spread_ulps": res_ulps}))
        return 0
    if args.cmd == "sdi-design":
        center = json.loads(args.center) if args.center else None
        res = sdi_design(args.degree, args.seed, args.trials, args.scale, center, args.polish)
        _write(out, res)
        print(json.dumps({"histogram": res["histogram"], "best_k": res["best"].get("sign_changes"),
                          "strength": res["best"].get("strength"), "balance": res["best"].get("balance"),
                          "c_high": res["best"].get("c_high")}))
        return 0
    f0 = f0_poly(json.loads(args.c_high))
    if args.cmd == "profile":
        prof = sdi_profile(f0)
        ratios = json.loads(args.ratios)
        j = prof["J_hi"]
        res = {"f0": f0.tolist(), "profile": prof, "ratios_J_over_eps": ratios,
               "eps_grid": [j / r for r in ratios] if math.isfinite(j) else [],
               "min_abs_I_ext_over_eps": [prof["strength"] * r for r in ratios]}
        _write(out, res)
        print(json.dumps({"eps_grid": res["eps_grid"], "strength": prof["strength"],
                          "zeros": prof["zeros_xR"]}))
        return 0
    if args.cmd == "curve":
        a0, a1 = (int(v) for v in args.idx.split(":"))
        res = stage_curve(out, f0, args.eps, args.n_y, args.a_half_width, args.deadline_s,
                          list(range(a0, min(a1, args.n_y))))
        print(json.dumps({"n": len(res["points"]), "seconds": res["seconds"],
                          "ok": sum(1 for q in res["points"] if q["status"] == "ok")}))
        return 0
    if args.cmd == "count":
        y_lo, y_hi = canard_y_range(f0, args.eps, 0.005, 1.0)
        coeffs = classical_coeffs(f0, args.a, args.eps)
        res = stage_count(out, coeffs, y_lo, y_hi, args.grid, args.deadline_s,
                          args.count_deadline_s, {"eps": args.eps, "a": args.a, "f0": f0.tolist()})
        print(json.dumps({"n_confirmed": res["n_confirmed"], "confirmed": res["confirmed"],
                          "n_unconfirmed": len(res["unconfirmed"]), "seconds": res["seconds"]}))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
