"""Paper A, edition 2: energy-error sign of RK4 against relaxation RK in the cubic magnetic-well model.

Question
--------
In the 2-DOF model that edition 1 actually integrated,
    H = 1/2 (p_r^2 + v^2) + mu (B0 + 1/2 beta_r r^2 + 1/2 beta_z z^2 + alpha r^2 z),
    (mu, B0, beta_r, beta_z, alpha) = (1/2, 1, 6/5, 8/5, 4/5),
the escape saddles sit at z = -3/4, r^2 = 3/2, and H* = 29/40 exactly. (The whole line z = -3/4
lies on the level V = H*.) Does fixed-step RK4 produce net energy GAIN that carries orbits started
below H* over the saddle (hypothesis H_heat, edition 1's stated motivation)?

Pre-registered design (fixed before the first run, 2026-10-21)
--------------------------------------------------------------
* Ensemble: N_ORBITS initial conditions per band, H0 uniform in the band. (r, z) are uniform on the
  allowed region {V < H0, z > -3/4, r^2 < 3/2} and the momentum angle is uniform, which is the exact
  microcanonical measure for 2 DOF. Bands: below = [H* - 0.03, H* - 0.001], above = [H* + 0.001, H* + 0.02].
  Seed SEED.
* Methods: RK4, RRK (RK4 increment relaxed by Newton so that H(u_n + gamma du) = H0), explicit
  midpoint RK2, forward Euler. dt in DTS, horizon T = T_HORIZON.
* Escape: the orbit reaches |r| > 3 or |z| > 3 (frozen from then on). Crossing: z < -3/4 at any step.
  Below H*, the exact flow can never cross z = -3/4 (V = H* on that line), so every escape or
  crossing there is spurious. Above H*, the reference is scipy DOP853 at rtol = atol = 1e-12.
* Falsification of H_heat (stated before running):
    REFUTED   if for every dt, RK4 final H_n - H0 <= 0 for >= 99 % of below-threshold orbits AND
              RK4 spurious escapes below H* are 0 / N_ORBITS.
    SUPPORTED if for some dt the spurious-escape fraction is >= 1 % or RK4 net gain occurs in >= 5 %.
    INTERMEDIATE otherwise.
* Positive controls: (i) alpha = 0 linear well, the RK4 energy matches E_r rho(y_r)^N + E_z rho(y_z)^N
  (Lean: rk4_iterate_energy) to relative 1e-10; (ii) the saddle finder returns 1/6 for Henon-Heiles,
  and DOP853 orbits at 1/6 + 0.01 escape (>= 50 %) while at 1/6 - 0.01 none do; (iii) RRK keeps
  |H_n - H0| < 1e-13 over T in the cubic well; edition-1 harness numbers reproduced as a function of N.
* Negative controls: (i) Euler and midpoint (heating, Lean: euler_harmonic_heats, midpoint_rk2_heats)
  must show median final dH > 0 and >= 1 spurious escape at every dt >= 0.1, otherwise the detector or
  the sampling is broken and the RK4 result is not reported; (ii) RRK relaxing the WRONG functional
  ||u||^2 must drift in H by > 1e-10; (iii) DOP853 above H* must escape in >= 50 % of orbits within T,
  otherwise T is doubled (up to T_MAX) for every method in the above band.

Output: papers/three_breakthroughs/paper_a/paper_a_v2_results.json
Run:    .venv/bin/python scripts/three_breakthroughs/paper_a_v2_experiment.py
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction
from multiprocessing import Pool
from pathlib import Path
from typing import Any

import mpmath
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq, root

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "papers" / "three_breakthroughs" / "paper_a" / "paper_a_v2_results.json"
HARNESS = REPO / "sub_projects" / "socrateai_scientific_fusion_energy" / "fusion_guiding_center_harness.py"

SEED = 20261021
N_ORBITS = 2000
DTS: tuple[float, ...] = (0.05, 0.1, 0.2, 0.4, 0.8)
T_HORIZON = 2000.0
T_MAX = 16000.0
ESCAPE_BOX = 3.0
H_STAR_Q = Fraction(29, 40)
H_STAR = float(H_STAR_Q)
BANDS: dict[str, tuple[float, float]] = {
    "below": (H_STAR - 0.03, H_STAR - 0.001),
    "above": (H_STAR + 0.001, H_STAR + 0.02),
}
Z_SADDLE = -0.75
R2_SADDLE = 1.5


@dataclass(frozen=True)
class Well:
    """Cubic magnetic-well model; alpha = 0 gives the linear (quadratic) well."""

    mu: float = 0.5
    b0: float = 1.0
    beta_r: float = 1.2
    beta_z: float = 1.6
    alpha: float = 0.8


CUBIC = Well()
LINEAR = Well(alpha=0.0)


def potential(r: np.ndarray, z: np.ndarray, w: Well) -> np.ndarray:
    return w.mu * (w.b0 + 0.5 * w.beta_r * r * r + 0.5 * w.beta_z * z * z + w.alpha * r * r * z)


def grad_potential(r: np.ndarray, z: np.ndarray, w: Well) -> tuple[np.ndarray, np.ndarray]:
    return (w.mu * (w.beta_r * r + 2.0 * w.alpha * r * z), w.mu * (w.beta_z * z + w.alpha * r * r))


def hamiltonian(u: np.ndarray, w: Well) -> np.ndarray:
    return 0.5 * (u[2] * u[2] + u[3] * u[3]) + potential(u[0], u[1], w)


def grad_hamiltonian(u: np.ndarray, w: Well) -> np.ndarray:
    gr, gz = grad_potential(u[0], u[1], w)
    return np.stack([gr, gz, u[2], u[3]])


def rhs(u: np.ndarray, w: Well) -> np.ndarray:
    gr, gz = grad_potential(u[0], u[1], w)
    return np.stack([u[2], u[3], -gr, -gz])


def step_euler(u: np.ndarray, h: float, w: Well) -> np.ndarray:
    return u + h * rhs(u, w)


def step_midpoint(u: np.ndarray, h: float, w: Well) -> np.ndarray:
    return u + h * rhs(u + 0.5 * h * rhs(u, w), w)


def rk4_increment(u: np.ndarray, h: float, w: Well) -> np.ndarray:
    k1 = rhs(u, w)
    k2 = rhs(u + 0.5 * h * k1, w)
    k3 = rhs(u + 0.5 * h * k2, w)
    k4 = rhs(u + h * k3, w)
    return (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def step_rk4(u: np.ndarray, h: float, w: Well) -> np.ndarray:
    return u + rk4_increment(u, h, w)


def relax(
    u: np.ndarray,
    du: np.ndarray,
    target: np.ndarray,
    func: Callable[[np.ndarray], np.ndarray],
    grad: Callable[[np.ndarray], np.ndarray],
) -> tuple[np.ndarray, np.ndarray]:
    """Newton solve of func(u + gamma du) = target, started at gamma = 1 (Ranocha et al. 2020)."""
    gamma = np.ones(u.shape[1])
    for _ in range(8):
        un = u + gamma * du
        res = func(un) - target
        deriv = np.sum(grad(un) * du, axis=0)
        ok = np.abs(deriv) > 1e-300
        gamma = np.where(ok, gamma - np.where(ok, res / np.where(ok, deriv, 1.0), 0.0), gamma)
        if float(np.max(np.abs(res))) < 2e-16:
            break
    return u + gamma * du, gamma


def make_rrk(w: Well, functional: str) -> Callable[[np.ndarray, float, np.ndarray], tuple[np.ndarray, np.ndarray]]:
    if functional == "H":
        def func(x: np.ndarray) -> np.ndarray:
            return hamiltonian(x, w)

        def grad(x: np.ndarray) -> np.ndarray:
            return grad_hamiltonian(x, w)
    elif functional == "norm2":
        def func(x: np.ndarray) -> np.ndarray:
            return np.sum(x * x, axis=0)

        def grad(x: np.ndarray) -> np.ndarray:
            return 2.0 * x
    else:
        raise ValueError(functional)

    def step(u: np.ndarray, h: float, target: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        return relax(u, rk4_increment(u, h, w), target, func, grad)

    return step


def integrate(method: str, u0: np.ndarray, dt: float, horizon: float, w: Well) -> dict[str, Any]:
    """Fixed-step integration of all orbits at once; escaped orbits are frozen."""
    n_steps = int(round(horizon / dt))
    u = u0.copy()
    h0 = hamiltonian(u0, w)
    n = u0.shape[1]
    active = np.ones(n, dtype=bool)
    escaped = np.zeros(n, dtype=bool)
    crossed = np.zeros(n, dtype=bool)
    nonfinite = np.zeros(n, dtype=bool)
    t_escape = np.full(n, np.nan)
    max_dh = np.zeros(n)
    min_dh = np.zeros(n)
    last_dh = np.zeros(n)
    gamma_sum = np.zeros(n)
    gamma_cnt = np.zeros(n)
    rrk_h = make_rrk(w, "H")
    rrk_n = make_rrk(w, "norm2")
    norm_target = np.sum(u0 * u0, axis=0)
    for k in range(1, n_steps + 1):
        if method == "rk4":
            un = step_rk4(u, dt, w)
        elif method == "rrk":
            un, g = rrk_h(u, dt, h0)
            gamma_sum += np.where(active, g, 0.0)
            gamma_cnt += active
        elif method == "rrk_wrong_functional":
            un, g = rrk_n(u, dt, norm_target)
        elif method == "midpoint":
            un = step_midpoint(u, dt, w)
        elif method == "euler":
            un = step_euler(u, dt, w)
        else:
            raise ValueError(method)
        u = np.where(active, un, u)
        fin = np.all(np.isfinite(u), axis=0)
        bad = active & ~fin
        if np.any(bad):
            nonfinite |= bad
            escaped |= bad
            t_escape = np.where(bad, k * dt, t_escape)
            active &= ~bad
        dh = np.where(fin, hamiltonian(np.where(fin, u, 0.0), w) - h0, last_dh)
        dh = np.where(active, dh, last_dh)
        last_dh = dh
        max_dh = np.maximum(max_dh, np.where(active, dh, max_dh))
        min_dh = np.minimum(min_dh, np.where(active, dh, min_dh))
        crossed |= active & (u[1] < Z_SADDLE)
        esc = active & ((np.abs(u[0]) > ESCAPE_BOX) | (np.abs(u[1]) > ESCAPE_BOX))
        if np.any(esc):
            escaped |= esc
            t_escape = np.where(esc, k * dt, t_escape)
            active &= ~esc
        if not np.any(active):
            break
    out: dict[str, Any] = {
        "final_dH": last_dh,
        "max_dH": max_dh,
        "min_dH": min_dh,
        "escaped": escaped,
        "crossed": crossed,
        "nonfinite": nonfinite,
        "t_escape": t_escape,
        "n_steps": n_steps,
    }
    if method == "rrk":
        out["mean_gamma"] = float(np.sum(gamma_sum) / max(np.sum(gamma_cnt), 1.0))
    return out


def sample_shell(n: int, band: tuple[float, float], rng: np.random.Generator, w: Well) -> np.ndarray:
    """H0 uniform in band; (r,z) uniform on {V<H0, z>-3/4, r^2<3/2}; momentum angle uniform."""
    h0 = rng.uniform(band[0], band[1], size=n)
    r = np.empty(n)
    z = np.empty(n)
    todo = np.arange(n)
    rmax = math.sqrt(R2_SADDLE)
    while todo.size:
        rc = rng.uniform(-rmax, rmax, size=todo.size)
        zc = rng.uniform(Z_SADDLE, 1.2, size=todo.size)
        ok = potential(rc, zc, w) < h0[todo]
        r[todo[ok]] = rc[ok]
        z[todo[ok]] = zc[ok]
        todo = todo[~ok]
    kin = h0 - potential(r, z, w)
    p = np.sqrt(2.0 * kin)
    th = rng.uniform(0.0, 2.0 * math.pi, size=n)
    return np.stack([r, z, p * np.cos(th), p * np.sin(th)])


# ---------------------------------------------------------------- DOP853 reference (per orbit)
def _cubic_rhs_list(t: float, u: list[float]) -> list[float]:
    r, z, pr, v = u
    return [pr, v, -0.5 * (1.2 * r + 1.6 * r * z), -0.5 * (1.6 * z + 0.8 * r * r)]


def _box_event(t: float, u: list[float]) -> float:
    return ESCAPE_BOX - max(abs(u[0]), abs(u[1]))


_box_event.terminal = True  # type: ignore[attr-defined]


def _crossing_event(t: float, u: list[float]) -> float:
    return u[1] - Z_SADDLE


def dop853_orbit(args: tuple[list[float], float]) -> tuple[bool, float, bool, float]:
    u0, horizon = args
    sol = solve_ivp(_cubic_rhs_list, (0.0, horizon), u0, method="DOP853", rtol=1e-12, atol=1e-12,
                    events=[_box_event, _crossing_event])
    esc = sol.t_events[0].size > 0
    t_esc = float(sol.t_events[0][0]) if esc else float("nan")
    crossed = bool(np.any(sol.y[1] < Z_SADDLE)) or sol.t_events[1].size > 0
    uf = sol.y[:, -1]
    dh = float(hamiltonian(uf.reshape(4, 1), CUBIC)[0] - hamiltonian(np.array(u0).reshape(4, 1), CUBIC)[0])
    return esc, t_esc, crossed, dh


def _hh_rhs(t: float, u: list[float]) -> list[float]:
    x, y, px, py = u
    return [px, py, -x - 2.0 * x * y, -y - x * x + y * y]


def _hh_event(t: float, u: list[float]) -> float:
    return 4.0 - (u[0] * u[0] + u[1] * u[1])


_hh_event.terminal = True  # type: ignore[attr-defined]


def hh_orbit(args: tuple[list[float], float]) -> bool:
    u0, horizon = args
    sol = solve_ivp(_hh_rhs, (0.0, horizon), u0, method="DOP853", rtol=1e-12, atol=1e-12, events=_hh_event)
    return sol.t_events[0].size > 0


# ---------------------------------------------------------------- saddle finder
def find_saddles(grad: Callable[[np.ndarray], np.ndarray], hess: Callable[[np.ndarray], np.ndarray],
                 pot: Callable[[np.ndarray], float], box: float) -> list[dict[str, float]]:
    pts: list[np.ndarray] = []
    for x0 in np.linspace(-box, box, 13):
        for y0 in np.linspace(-box, box, 13):
            s = root(grad, np.array([x0, y0]), tol=1e-14)
            if not s.success or np.max(np.abs(grad(s.x))) > 1e-10 or np.max(np.abs(s.x)) > 2 * box:
                continue
            if all(np.linalg.norm(s.x - q) > 1e-6 for q in pts):
                pts.append(s.x)
    out = []
    for q in pts:
        ev = np.linalg.eigvalsh(hess(q))
        kind = "saddle" if ev[0] < 0 < ev[1] else ("min" if ev[0] > 0 else "max")
        out.append({"x": float(q[0]), "y": float(q[1]), "V": float(pot(q)), "kind": kind})
    return out


def saddle_controls() -> dict[str, Any]:
    def hh_grad(q: np.ndarray) -> np.ndarray:
        x, y = q
        return np.array([x + 2 * x * y, y + x * x - y * y])

    def hh_hess(q: np.ndarray) -> np.ndarray:
        x, y = q
        return np.array([[1 + 2 * y, 2 * x], [2 * x, 1 - 2 * y]])

    def hh_pot(q: np.ndarray) -> float:
        x, y = q
        return float(0.5 * (x * x + y * y) + x * x * y - y ** 3 / 3)

    w = CUBIC

    def cw_grad(q: np.ndarray) -> np.ndarray:
        gr, gz = grad_potential(q[0], q[1], w)
        return np.array([gr, gz])

    def cw_hess(q: np.ndarray) -> np.ndarray:
        r, z = q
        return w.mu * np.array([[w.beta_r + 2 * w.alpha * z, 2 * w.alpha * r], [2 * w.alpha * r, w.beta_z]])

    def cw_pot(q: np.ndarray) -> float:
        return float(potential(q[0], q[1], w))

    hh = find_saddles(hh_grad, hh_hess, hh_pot, 1.5)
    cw = find_saddles(cw_grad, cw_hess, cw_pot, 2.0)
    hh_esc = min(p["V"] for p in hh if p["kind"] == "saddle")
    cw_esc = min(p["V"] for p in cw if p["kind"] == "saddle")
    return {"henon_heiles_critical_points": hh, "henon_heiles_escape_energy": hh_esc,
            "henon_heiles_pass": abs(hh_esc - 1 / 6) < 1e-12,
            "cubic_well_critical_points": cw, "cubic_well_escape_energy": cw_esc,
            "cubic_well_pass": abs(cw_esc - H_STAR) < 1e-12}


def hh_escape_control(rng: np.random.Generator, n: int, horizon: float, pool: Any) -> dict[str, Any]:
    """DOP853 Henon-Heiles orbits inside the saddle triangle at E = 1/6 -+ 0.01."""
    res: dict[str, Any] = {}
    for label, e in (("below", 1 / 6 - 0.01), ("above", 1 / 6 + 0.01)):
        ics: list[list[float]] = []
        while len(ics) < n:
            x, y = rng.uniform(-0.9, 0.9), rng.uniform(-0.5, 1.0)
            vv = 0.5 * (x * x + y * y) + x * x * y - y ** 3 / 3
            if y > -0.5 and y < 1 - math.sqrt(3) * abs(x) and vv < e:
                p = math.sqrt(2 * (e - vv))
                th = rng.uniform(0, 2 * math.pi)
                ics.append([x, y, p * math.cos(th), p * math.sin(th)])
        esc = pool.map(hh_orbit, [(u, horizon) for u in ics])
        res[label] = {"energy": e, "n": n, "escaped": int(sum(esc))}
    res["horizon"] = horizon
    res["pass"] = res["below"]["escaped"] == 0 and res["above"]["escaped"] >= 0.5 * n
    return res


# ---------------------------------------------------------------- positive control (i)
def rho4(y: np.ndarray) -> np.ndarray:
    return 1 - y ** 6 / 72 + y ** 8 / 576


def linear_well_control(rng: np.random.Generator) -> dict[str, Any]:
    w = LINEAR
    u0 = rng.uniform(-0.5, 0.5, size=(4, 200))
    wr, wz = math.sqrt(w.mu * w.beta_r), math.sqrt(w.mu * w.beta_z)
    er = 0.5 * u0[2] ** 2 + 0.5 * w.mu * w.beta_r * u0[0] ** 2
    ez = 0.5 * u0[3] ** 2 + 0.5 * w.mu * w.beta_z * u0[1] ** 2
    out: dict[str, Any] = {"per_dt": [], "omega_r": wr, "omega_z": wz,
                           "rho4_at_y1_numeric": float(rho4(np.array(1.0))), "rho4_at_y1_lean": 569 / 576}
    for dt in DTS:
        n_steps = int(round(T_HORIZON / dt))
        u = u0.copy()
        curve_n: list[int] = []
        curve_meas: list[float] = []
        curve_pred: list[float] = []
        marks = set(np.unique(np.geomspace(1, n_steps, 40).astype(int)).tolist())
        for k in range(1, n_steps + 1):
            u = step_rk4(u, dt, w)
            if k in marks:
                meas = hamiltonian(u, w) - w.mu * w.b0
                pred = er * rho4(np.array(wr * dt)) ** k + ez * rho4(np.array(wz * dt)) ** k
                curve_n.append(k)
                curve_meas.append(float(np.mean(meas / (er + ez))))
                curve_pred.append(float(np.mean(pred / (er + ez))))
                if k == n_steps:
                    relerr = float(np.max(np.abs(meas - pred) / pred))
        # negative-control growth: Euler and midpoint over 200 steps against (1+y^2)^N, (1+y^4/4)^N
        ue, um = u0.copy(), u0.copy()
        eu_n: list[int] = []
        eu_meas: list[float] = []
        eu_pred: list[float] = []
        mp_meas: list[float] = []
        mp_pred: list[float] = []
        for k in range(1, 201):
            ue = step_euler(ue, dt, w)
            um = step_midpoint(um, dt, w)
            if k in (1, 2, 5, 10, 20, 50, 100, 200):
                eu_n.append(k)
                eu_meas.append(float(np.mean((hamiltonian(ue, w) - w.mu * w.b0) / (er + ez))))
                pe = er * (1 + (wr * dt) ** 2) ** k + ez * (1 + (wz * dt) ** 2) ** k
                eu_pred.append(float(np.mean(pe / (er + ez))))
                mp_meas.append(float(np.mean((hamiltonian(um, w) - w.mu * w.b0) / (er + ez))))
                pm = er * (1 + (wr * dt) ** 4 / 4) ** k + ez * (1 + (wz * dt) ** 4 / 4) ** k
                mp_pred.append(float(np.mean(pm / (er + ez))))
        out["per_dt"].append({"dt": dt, "n_steps": n_steps, "max_rel_err_vs_closed_form": relerr,
                              "curve_n": curve_n, "curve_measured": curve_meas, "curve_closed_form": curve_pred,
                              "euler_n": eu_n, "euler_measured": eu_meas, "euler_closed_form": eu_pred,
                              "midpoint_measured": mp_meas, "midpoint_closed_form": mp_pred})
    out["pass"] = all(d["max_rel_err_vs_closed_form"] < 1e-10 for d in out["per_dt"])
    return out


# ---------------------------------------------------------------- edition-1 reproduction
def harness_reproduction() -> dict[str, Any]:
    sys.path.insert(0, str(HARNESS.parent))
    import fusion_guiding_center_harness as fh  # noqa: PLC0415

    rows = []
    for n in (1000, 4000, 10000):
        t = fh.run_stellarator_dual_rrk_benchmark(n_steps=n, dt=0.05)
        rows.append({"n_steps": n, "dt": 0.05, "rk4_max_drift": t.rk4_max_energy_drift,
                     "rrk_max_drift": t.dual_rrk_max_energy_drift, "mean_gamma": t.mean_relaxation_gamma})
    return {"harness_sha256": hashlib.sha256(HARNESS.read_bytes()).hexdigest(), "rows": rows}


def edition1_constant_checks() -> dict[str, Any]:
    mpmath.mp.dps = 30
    f0 = mpmath.mpf(93) / 10
    s_exact = mpmath.findroot(lambda s: s / 2 * mpmath.log((s + 1) / (s - 1)) - 1 - 1 / f0, 1.9)
    s_pade = mpmath.sqrt(mpmath.mpf(37) / 10)

    def f0_from_pade(s: float) -> float:
        return float((15 * s ** 2 - 9) / 5)  # u = 1/s^2 = 15/(9 + 5 F0)

    f0_exact_for_1852 = mpmath.findroot(lambda f: mpmath.mpf("1.851999") / 2 *
                                        mpmath.log((mpmath.mpf("1.851999") + 1) / (mpmath.mpf("1.851999") - 1))
                                        - 1 - 1 / f, 8.4)
    h0 = Fraction(1, 2) * (Fraction(3, 20) ** 2 + Fraction(1, 4) ** 2) + Fraction(1, 2) * (
        1 + Fraction(3, 5) * Fraction(1, 25) + Fraction(4, 5) * Fraction(1, 100) + Fraction(4, 5) * Fraction(1, 25) * Fraction(1, 10))
    return {
        "sqrt_37_over_10": float(s_pade),
        "edition1_claimed_c0_over_vF": 1.851999,
        "landau_F0_only_exact_root_at_F0_9.3": float(s_exact),
        "pade_relative_error": float((s_pade - s_exact) / s_exact),
        "F0_reverse_pade_for_1.851999": f0_from_pade(1.851999),
        "F0_reverse_exact_for_1.851999": float(f0_exact_for_1852),
        "two_plus_sqrt_59_over_25": float(2 + mpmath.sqrt(mpmath.mpf(59) / 25)),
        "edition1_claimed_c30_lower_bound": 4.354632,
        "harness_H0_exact": f"{h0.numerator}/{h0.denominator}",
        "harness_margin_to_Hstar": str(H_STAR_Q - h0),
    }


# ---------------------------------------------------------------- trajectories for figures
def trajectory(method: str, u0: np.ndarray, dt: float, horizon: float, w: Well, every: int) -> dict[str, list[float]]:
    u = u0.reshape(4, 1).copy()
    h0 = hamiltonian(u, w)
    rrk = make_rrk(w, "H")
    rs, zs, hs, ts = [float(u[0, 0])], [float(u[1, 0])], [float(h0[0])], [0.0]
    for k in range(1, int(round(horizon / dt)) + 1):
        if method == "rk4":
            u = step_rk4(u, dt, w)
        elif method == "rrk":
            u, _ = rrk(u, dt, h0)
        elif method == "euler":
            u = step_euler(u, dt, w)
        if k % every == 0:
            rs.append(float(u[0, 0]))
            zs.append(float(u[1, 0]))
            hs.append(float(hamiltonian(u, w)[0]))
            ts.append(k * dt)
        if abs(u[0, 0]) > ESCAPE_BOX or abs(u[1, 0]) > ESCAPE_BOX:
            break
    return {"t": ts, "r": rs, "z": zs, "H": hs}


def dop853_trajectory(u0: np.ndarray, horizon: float, n_pts: int) -> dict[str, list[float]]:
    te = np.linspace(0.0, horizon, n_pts)
    sol = solve_ivp(_cubic_rhs_list, (0.0, horizon), u0.tolist(), method="DOP853", rtol=1e-12, atol=1e-12,
                    t_eval=te, events=_box_event)
    h = hamiltonian(sol.y, CUBIC)
    return {"t": sol.t.tolist(), "r": sol.y[0].tolist(), "z": sol.y[1].tolist(), "H": h.tolist()}


def poincare(method: str, u0: np.ndarray, dt: float, horizon: float, w: Well) -> dict[str, list[float]]:
    """Section z = 0 upward (v > 0), linear interpolation between steps; (r, p_r, H) at each hit."""
    u = u0.copy()
    h0 = hamiltonian(u, w)
    rrk = make_rrk(w, "H")
    rr: list[float] = []
    pp: list[float] = []
    hh: list[float] = []
    for _ in range(int(round(horizon / dt))):
        un = step_rk4(u, dt, w) if method == "rk4" else rrk(u, dt, h0)[0]
        hit = (u[1] < 0) & (un[1] >= 0) & (un[3] > 0)
        if np.any(hit):
            s = -u[1][hit] / (un[1][hit] - u[1][hit])
            ui = u[:, hit] + s * (un[:, hit] - u[:, hit])
            rr.extend(ui[0].tolist())
            pp.extend(ui[2].tolist())
            hh.extend(hamiltonian(ui, w).tolist())
        u = un
    return {"r": rr, "p_r": pp, "H": hh}


def rnd(a: np.ndarray) -> list[float]:
    return [float(f"{x:.6e}") if np.isfinite(x) else None for x in np.asarray(a, dtype=float)]  # type: ignore[misc]


def summarize(res: dict[str, Any], n: int) -> dict[str, Any]:
    f = res["final_dH"]
    m = res["max_dH"]
    return {
        "n_orbits": n,
        "n_steps": res["n_steps"],
        "frac_final_dH_le_0": float(np.mean(f <= 0)),
        "frac_final_dH_gt_0": float(np.mean(f > 0)),
        "frac_max_dH_gt_0": float(np.mean(m > 0)),
        "final_dH_percentiles_1_50_99": [float(x) for x in np.nanpercentile(f, [1, 50, 99])],
        "median_final_dH": float(np.nanmedian(f)),
        "max_abs_dH": float(np.nanmax(np.maximum(np.abs(res["max_dH"]), np.abs(res["min_dH"])))),
        "escaped": int(np.sum(res["escaped"])),
        "crossed_z_saddle": int(np.sum(res["crossed"])),
        "nonfinite": int(np.sum(res["nonfinite"])),
    }


def main() -> int:
    t_start = time.time()
    rng = np.random.default_rng(SEED)
    code_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    results: dict[str, Any] = {
        "script": "scripts/three_breakthroughs/paper_a_v2_experiment.py",
        "script_sha256": code_hash,
        "numpy": np.__version__,
        "seed": SEED,
        "model": {"H": "1/2(p_r^2+v^2) + mu(B0 + 1/2 beta_r r^2 + 1/2 beta_z z^2 + alpha r^2 z)",
                  "params": CUBIC.__dict__, "H_star": str(H_STAR_Q), "saddles": "z=-3/4, r^2=3/2",
                  "escape": f"|r|>{ESCAPE_BOX} or |z|>{ESCAPE_BOX}", "bands": BANDS,
                  "sampling": "H0 uniform in band; (r,z) uniform on {V<H0, z>-3/4, r^2<3/2}; angle uniform",
                  "dts": DTS, "n_orbits": N_ORBITS},
        "preregistered_criterion": {
            "REFUTED": "for every dt: RK4 frac(final dH <= 0) >= 0.99 on below band AND RK4 spurious escapes == 0",
            "SUPPORTED": "for some dt: RK4 spurious escapes >= 1% (>=20/2000) OR RK4 frac(final dH > 0) >= 0.05",
            "INTERMEDIATE": "otherwise"},
    }
    with Pool(8) as pool:
        print("[1] edition-1 harness reproduction", flush=True)
        results["edition1_harness_reproduction"] = harness_reproduction()
        results["edition1_constant_checks"] = edition1_constant_checks()
        print("[2] positive control (i): linear well closed form", flush=True)
        results["positive_control_linear_well"] = linear_well_control(rng)
        print("[3] positive control (ii): saddle finder + Henon-Heiles escape", flush=True)
        sc = saddle_controls()
        sc["henon_heiles_escape"] = hh_escape_control(rng, 100, T_HORIZON, pool)
        results["positive_control_saddles"] = sc

        ics = {b: sample_shell(N_ORBITS, BANDS[b], rng, CUBIC) for b in BANDS}
        h0s = {b: hamiltonian(ics[b], CUBIC) for b in BANDS}
        results["initial_H0"] = {b: rnd(h0s[b]) for b in BANDS}

        print("[4] DOP853 reference, above band", flush=True)
        horizon_above = T_HORIZON
        while True:
            ref = pool.map(dop853_orbit, [(ics["above"][:, i].tolist(), horizon_above) for i in range(N_ORBITS)],
                           chunksize=8)
            frac = float(np.mean([x[0] for x in ref]))
            print(f"    T={horizon_above}: DOP853 escape fraction {frac:.4f}", flush=True)
            if frac >= 0.5 or horizon_above >= T_MAX:
                break
            horizon_above *= 2
        print("[5] DOP853 sanity subset, below band (200 orbits)", flush=True)
        ref_b = pool.map(dop853_orbit, [(ics["below"][:, i].tolist(), T_HORIZON) for i in range(200)], chunksize=8)
    ref_esc = np.array([x[0] for x in ref])
    results["dop853_reference"] = {
        "above": {"horizon": horizon_above, "escaped": int(ref_esc.sum()), "frac_escaped": float(ref_esc.mean()),
                  "t_escape": rnd(np.array([x[1] for x in ref])), "escaped_flags": [bool(x) for x in ref_esc],
                  "max_abs_dH_non_escaped": float(max([abs(x[3]) for x in ref if not x[0]] or [0.0]))},
        "below_subset": {"n": 200, "horizon": T_HORIZON, "escaped": int(sum(x[0] for x in ref_b)),
                         "crossed": int(sum(x[2] for x in ref_b)),
                         "max_abs_dH": float(max(abs(x[3]) for x in ref_b))},
        "negative_control_iii_pass": float(ref_esc.mean()) >= 0.5,
    }

    print("[6] fixed-step ensembles", flush=True)
    runs: list[dict[str, Any]] = []
    for band in ("below", "above"):
        horizon = T_HORIZON if band == "below" else horizon_above
        for method in ("rk4", "rrk", "midpoint", "euler", "rrk_wrong_functional"):
            for dt in DTS:
                if method == "rrk_wrong_functional" and (band == "above" or dt not in (0.05, 0.2)):
                    continue
                t0 = time.time()
                res = integrate(method, ics[band], dt, horizon, CUBIC)
                s = summarize(res, N_ORBITS)
                s.update({"band": band, "method": method, "dt": dt, "horizon": horizon,
                          "wall_s": round(time.time() - t0, 1)})
                if "mean_gamma" in res:
                    s["mean_gamma"] = res["mean_gamma"]
                if band == "above":
                    e = res["escaped"]
                    s["spurious_trapping_frac"] = float(np.mean(ref_esc & ~e))
                    s["spurious_escape_frac_vs_ref"] = float(np.mean(~ref_esc & e))
                    s["escape_frac"] = float(np.mean(e))
                s["per_orbit"] = {"final_dH": rnd(res["final_dH"]), "max_dH": rnd(res["max_dH"]),
                                  "escaped": [bool(x) for x in res["escaped"]], "t_escape": rnd(res["t_escape"])}
                runs.append(s)
                print(f"    {band:5s} {method:20s} dt={dt:<5} esc={s['escaped']:5d} "
                      f"gain={s['frac_final_dH_gt_0']:.4f} med={s['median_final_dH']:.3e} ({s['wall_s']}s)",
                      flush=True)
    results["runs"] = runs

    def get(band: str, method: str, dt: float) -> dict[str, Any]:
        return next(r for r in runs if r["band"] == band and r["method"] == method and r["dt"] == dt)

    # controls evaluation
    neg_i = {f"{m}@{dt}": {"median_final_dH": get("below", m, dt)["median_final_dH"],
                           "escaped": get("below", m, dt)["escaped"]}
             for m in ("euler", "midpoint") for dt in DTS if dt >= 0.1}
    results["negative_control_heating_methods"] = {
        "detail": neg_i, "pass": all(v["median_final_dH"] > 0 and v["escaped"] >= 1 for v in neg_i.values())}
    wf = {str(dt): get("below", "rrk_wrong_functional", dt)["max_abs_dH"] for dt in (0.05, 0.2)}
    results["negative_control_wrong_functional"] = {"max_abs_dH": wf, "pass": all(v > 1e-10 for v in wf.values())}
    rrk_max = max(get("below", "rrk", dt)["max_abs_dH"] for dt in DTS)
    results["positive_control_rrk_conservation"] = {"max_abs_dH_below_all_dt": rrk_max, "pass": rrk_max < 1e-13,
                                                    "above_band_max_abs_dH_per_dt":
                                                        {str(dt): get("above", "rrk", dt)["max_abs_dH"] for dt in DTS}}

    controls_ok = (results["positive_control_linear_well"]["pass"] and sc["henon_heiles_pass"]
                   and sc["cubic_well_pass"] and sc["henon_heiles_escape"]["pass"]
                   and results["negative_control_heating_methods"]["pass"]
                   and results["negative_control_wrong_functional"]["pass"]
                   and results["dop853_reference"]["negative_control_iii_pass"])
    rk4 = [get("below", "rk4", dt) for dt in DTS]
    refuted = all(r["frac_final_dH_le_0"] >= 0.99 and r["escaped"] == 0 for r in rk4)
    supported = any(r["escaped"] >= 0.01 * N_ORBITS or r["frac_final_dH_gt_0"] >= 0.05 for r in rk4)
    outcome = "REFUTED" if refuted else ("SUPPORTED" if supported else "INTERMEDIATE")
    results["falsification"] = {
        "hypothesis": "H_heat: RK4 secular heating causes spurious loss of orbits with H0 < H*",
        "controls_all_pass": bool(controls_ok),
        "outcome": outcome if controls_ok else f"NOT REPORTABLE (controls failed); raw outcome {outcome}",
        "rk4_below_per_dt": [{"dt": r["dt"], "frac_final_dH_le_0": r["frac_final_dH_le_0"],
                              "frac_max_dH_gt_0": r["frac_max_dH_gt_0"], "escaped": r["escaped"],
                              "crossed": r["crossed_z_saddle"], "median_final_dH": r["median_final_dH"]}
                             for r in rk4],
    }

    print("[7] trajectories for figures", flush=True)
    i_near = int(np.argmax(h0s["below"]))
    u_near = ics["below"][:, i_near]
    results["figure_trajectory"] = {
        "u0": u_near.tolist(), "H0": float(h0s["below"][i_near]), "dt": 0.4, "horizon": 400.0,
        "dop853": dop853_trajectory(u_near, 400.0, 4001),
        "rk4": trajectory("rk4", u_near, 0.4, 400.0, CUBIC, 1),
        "rrk": trajectory("rrk", u_near, 0.4, 400.0, CUBIC, 1),
        "euler": trajectory("euler", u_near, 0.4, 400.0, CUBIC, 1),
    }
    sel = ics["below"][:, :12]
    results["figure_poincare"] = {"dt": 0.4, "horizon": T_HORIZON, "orbits": 12,
                                  "rk4": poincare("rk4", sel, 0.4, T_HORIZON, CUBIC),
                                  "rrk": poincare("rrk", sel, 0.4, T_HORIZON, CUBIC)}
    results["wall_seconds"] = round(time.time() - t_start, 1)
    OUT.write_text(json.dumps(results, indent=1))
    print(f"wrote {OUT} ({OUT.stat().st_size / 1e6:.1f} MB); outcome: {results['falsification']['outcome']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
