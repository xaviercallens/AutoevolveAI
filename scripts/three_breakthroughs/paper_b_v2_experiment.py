"""Paper B, edition 2: which quadratic quantity does the scale-dual Navier-Stokes model conserve?

Model (edition 1, Sec. 2.1 and 2.4) on T^3 = [0, 2 pi]^3, div u = 0:
    d_t u = -P[(u . grad)(M u)] + nu Lap u,      (M u)^(k) = m(|k|^2) u^(k),
    piecewise  m = k_eff/|k| = min(1, 1/(alpha |k|^2))      (edition-1 operator kEff)
    smooth     m = k_smooth/|k| = 1/(1 + alpha |k|^2)        (= the modified Leray-alpha model of
                                                               Ilyin, Lunasin & Titi 2006)
    control    m = 1                                          (Navier-Stokes)
Edition 1 (Theorem 2.5) asserted E(t) = 1/2 sum |u_k|^2 <= E0. The Lean file
formal/ANSE/PaperB_EnergyBudget.lean proves that the nonlinear invariant is instead
Q = 1/2 sum m |u_k|^2 and that L2 conservation for all skew triad tensors holds iff m is constant.

Pre-registered design (fixed before the first run of this script, 2026-10-21)
-----------------------------------------------------------------------------
A. Exact arithmetic over Q(i) (Python ints and Fractions, no floating point):
   A1. The edition-1-audit triad at alpha = 1/4 (modes (1,0,0), (0,2,0), (-1,-2,0)); E0, Q0,
       inviscid dE/dt and dQ/dt for NS, piecewise, smooth; total dE/dt at nu = 1/100.
   A2. The triad (5,0,0), (0,1,0), (-5,-1,0) at the paper's alpha = 1/25: nonlinear rate R,
       true enstrophy Omega, growth threshold lambda* = 2 nu Omega / R at nu = 1/100.
   A3. Sweep: every triad p + q + r = 0 with p in the fundamental domain a >= b >= c >= 0 of the
       cube group, all |k|^2 <= K2MAX(alpha), amplitudes u_k = k x a + i k x b (integer, exactly
       solenoidal) from a seeded RNG. Count triads with dQ/dt != 0 (must be 0) and dE/dt != 0.
B. Float pseudospectral Galerkin (2/3 dealiased, RK4 with exact viscous integrating factor):
   B1. Code validation: the float rates of the A1/A2 fields must equal the exact rationals to 1e-10.
   B2. Ensemble: kinds {ns, piecewise, smooth} x alpha {1/4, 1/16, 1/25} x nu {0, 1/400, 1/100}
       x 10 seeds at N = 32, dt = 0.005, T = 3, random solenoidal data with spectrum
       k^4 exp(-2 (k/4)^2), E0 = 1/2. Record E/E0, Q/Q0, alpha Omega_eff/Q0, alpha Omega/E0.
   B3. Convergence at the paper's (alpha, nu) = (1/25, 1/100), seeds 0-2: N = 64 (zero-padded
       identical initial data) and dt = 0.0025 at N = 32, for E0 = 1/2 and E0 = 32.
   B4. Amplitude scan at the paper's (alpha, nu): E0 in {2, 8, 32}, seeds 0-4, all three kinds
       (edition 1 fixes no amplitude, and the exact A2 threshold shows the sign of dE/dt depends on it).
       (B4 and the E0 = 32 part of B3 were added to the design after a 0.5-time-unit smoke run of one
       seed at E0 = 1/2 showed E decreasing; no ensemble result had been computed at that point.)
Controls (must behave as stated or the model numbers are not reported):
   positive: NS (m = 1) exact triad dE/dt = dQ/dt = 0; NS float rate |dE/dt| < 1e-10;
             inviscid NS ensemble max |E/E0 - 1| < 1e-6 (RK4 time error only);
             every exact model triad has dQ/dt = 0; Omega_eff alpha/Q0 <= 1 (Lean ceiling).
   negative: NS with a non-solenoidal mode must give exact dE/dt != 0; an aliased (not
             dealiased) inviscid NS run must drift in E by more than 10x the dealiased control.
Falsification (stated before running):
   The edition-2 claim "E is not a Lyapunov functional of the scale-dual model; Q is" is
   FALSIFIED if any exact divergence-free field gives dQ/dt != 0, or if every exact triad with
   non-constant weights gives dE/dt = 0.
   Edition-1 Theorem 2.5 (E(t) <= E0) is REFUTED at the paper's (alpha, nu) = (1/25, 1/100) if the
   exact A2 rate is positive for some amplitude AND in B2/B3 max_t E/E0 - 1 exceeds 10x the NS
   control's max_t E/E0 - 1 (floored at 1e-12) and persists under N -> 64 and dt -> dt/2.
   If the exact rate is positive but E(t) <= E0 holds in all runs, the result is reported as
   "instantaneous growth only; the edition-1 proof is invalid, the bound itself is not violated".

Output: papers/three_breakthroughs/paper_b/paper_b_v2_results.json
Run:    .venv/bin/python scripts/three_breakthroughs/paper_b_v2_experiment.py
"""

from __future__ import annotations

import json
import os
import platform
import sys
import time
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path
from typing import Any

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np
import scipy.fft as sfft

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "papers" / "three_breakthroughs" / "paper_b" / "paper_b_v2_results.json"

Vec = tuple[int, int, int]
GInt = tuple[int, int]  # Gaussian integer a + b i
Weight = Callable[[int], Fraction]

KINDS: tuple[str, ...] = ("ns", "piecewise", "smooth")
ALPHAS: tuple[Fraction, ...] = (Fraction(1, 4), Fraction(1, 16), Fraction(1, 25))
NUS: tuple[Fraction, ...] = (Fraction(0), Fraction(1, 400), Fraction(1, 100))
SEEDS: tuple[int, ...] = tuple(range(10))
N_GRID = 32
DT = 0.005
T_MAX = 3.0
N_SAMPLES = 60
KPEAK = 4.0
E_TARGET = 0.5
SWEEP_SEED = 20261021
AMP_E0: tuple[float, ...] = (2.0, 8.0, 32.0)
AMP_SEEDS: tuple[int, ...] = (0, 1, 2, 3, 4)
CONV_E0: tuple[float, ...] = (0.5, 32.0)
PAPER_ALPHA = Fraction(1, 25)
PAPER_NU = Fraction(1, 100)


# --------------------------------------------------------------------------------------------
# A. exact arithmetic
# --------------------------------------------------------------------------------------------
def exact_weight(kind: str, alpha: Fraction) -> Weight:
    """Multiplier m(|k|^2) as an exact rational function of the integer |k|^2 > 0."""
    if kind == "ns":
        return lambda k2: Fraction(1)
    if kind == "piecewise":
        return lambda k2: min(Fraction(1), 1 / (alpha * k2))
    if kind == "smooth":
        return lambda k2: 1 / (1 + alpha * k2)
    raise ValueError(f"unknown kind {kind!r}")


def gmul(x: GInt, y: GInt) -> GInt:
    return (x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def gconj(x: GInt) -> GInt:
    return (x[0], -x[1])


def norm2(k: Vec) -> int:
    return k[0] * k[0] + k[1] * k[1] + k[2] * k[2]


def neg(k: Vec) -> Vec:
    return (-k[0], -k[1], -k[2])


def hermitian_field(modes: dict[Vec, tuple[GInt, GInt, GInt]]) -> dict[Vec, tuple[GInt, GInt, GInt]]:
    """Complete a set of modes with u_{-k} = conj(u_k) so that the physical field is real."""
    full: dict[Vec, tuple[GInt, GInt, GInt]] = {}
    for k, a in modes.items():
        if k in full or neg(k) in full or k == (0, 0, 0):
            raise ValueError("modes must be distinct, nonzero and not paired with their negatives")
        full[k] = a
        full[neg(k)] = (gconj(a[0]), gconj(a[1]), gconj(a[2]))
    return full


def divergence(k: Vec, a: tuple[GInt, GInt, GInt]) -> GInt:
    return (sum(k[i] * a[i][0] for i in range(3)), sum(k[i] * a[i][1] for i in range(3)))


def exact_rates(modes: dict[Vec, tuple[GInt, GInt, GInt]], m: Weight) -> dict[str, Fraction]:
    """Exact inviscid dE/dt = -<u,(u.grad)Mu> and dQ/dt = -<Mu,(u.grad)Mu> (volume means)."""
    u = hermitian_field(modes)
    sE = [Fraction(0), Fraction(0)]
    sQ = [Fraction(0), Fraction(0)]
    for p, up in u.items():
        for q, uq in u.items():
            r = neg((p[0] + q[0], p[1] + q[1], p[2] + q[2]))
            ur = u.get(r)
            if ur is None:
                continue
            c = (0, 0)
            for j in range(3):
                if q[j] == 0:
                    continue
                dq = gmul(up[j], (0, q[j]))  # u_p[j] * (i q_j)
                for i in range(3):
                    t = gmul(gmul(dq, uq[i]), ur[i])
                    c = (c[0] + t[0], c[1] + t[1])
            if c == (0, 0):
                continue
            mq, mr = m(norm2(q)), m(norm2(r))
            sE[0] += mq * c[0]
            sE[1] += mq * c[1]
            sQ[0] += mq * mr * c[0]
            sQ[1] += mq * mr * c[1]
    e0 = Fraction(sum(sum(x[0] ** 2 + x[1] ** 2 for x in a) for a in u.values()), 2)
    q0 = sum((m(norm2(k)) * sum(x[0] ** 2 + x[1] ** 2 for x in a) for k, a in u.items()), Fraction(0)) / 2
    om = Fraction(sum(norm2(k) * sum(x[0] ** 2 + x[1] ** 2 for x in a) for k, a in u.items()), 2)
    return {"E0": e0, "Q0": q0, "Omega_true": om, "dE_dt": -sE[0], "dE_dt_imag": -sE[1],
            "dQ_dt": -sQ[0], "dQ_dt_imag": -sQ[1]}


def cross(k: Vec, a: Vec) -> Vec:
    return (k[1] * a[2] - k[2] * a[1], k[2] * a[0] - k[0] * a[2], k[0] * a[1] - k[1] * a[0])


def solenoidal_amplitude(k: Vec, a: Vec, b: Vec) -> tuple[GInt, GInt, GInt]:
    """u_k = k x a + i (k x b): integer and exactly divergence-free."""
    ra, rb = cross(k, a), cross(k, b)
    return ((ra[0], rb[0]), (ra[1], rb[1]), (ra[2], rb[2]))


AUDIT_TRIAD_1_4: dict[Vec, tuple[GInt, GInt, GInt]] = {
    (1, 0, 0): ((0, 0), (1, 0), (1, 0)),
    (0, 2, 0): ((1, 0), (0, 0), (0, 1)),
    (-1, -2, 0): ((2, 0), (-1, 0), (1, 1)),
}
PAPER_TRIAD_1_25: dict[Vec, tuple[GInt, GInt, GInt]] = {
    (5, 0, 0): ((0, 0), (1, 0), (1, 0)),
    (0, 1, 0): ((1, 0), (0, 0), (0, 1)),
    (-5, -1, 0): ((1, 0), (-5, 0), (1, 1)),
}


def frac(x: Fraction) -> dict[str, Any]:
    return {"exact": f"{x.numerator}/{x.denominator}" if x.denominator != 1 else str(x.numerator),
            "float": float(x)}


def exact_section() -> dict[str, Any]:
    out: dict[str, Any] = {}
    # A1
    a1: dict[str, Any] = {"alpha": frac(Fraction(1, 4)), "modes": {str(k): v for k, v in AUDIT_TRIAD_1_4.items()}}
    for k, a in AUDIT_TRIAD_1_4.items():
        assert divergence(k, a) == (0, 0)
    for kind in KINDS:
        r = exact_rates(AUDIT_TRIAD_1_4, exact_weight(kind, Fraction(1, 4)))
        a1[kind] = {key: frac(v) for key, v in r.items()}
        a1[kind]["dE_dt_total_nu_1_100"] = frac(r["dE_dt"] - 2 * PAPER_NU * r["Omega_true"])
    out["A1_triad_alpha_1_4"] = a1
    # A2
    m = exact_weight("piecewise", PAPER_ALPHA)
    r = exact_rates(PAPER_TRIAD_1_25, m)
    rate, om = r["dE_dt"], r["Omega_true"]
    a2: dict[str, Any] = {"alpha": frac(PAPER_ALPHA), "nu": frac(PAPER_NU),
                          "weights": {str(k): frac(m(norm2(k))) for k in PAPER_TRIAD_1_25}}
    a2.update({key: frac(v) for key, v in r.items()})
    if rate > 0:
        lam_star = 2 * PAPER_NU * om / rate
        a2["lambda_star_growth_threshold"] = frac(lam_star)
        a2["lambda_star_over_nu"] = frac(2 * om / rate)
        a2["dE_dt_total_at_lambda_34"] = frac(34 ** 3 * rate - 34 ** 2 * 2 * PAPER_NU * om)
        a2["dE_dt_total_at_lambda_33"] = frac(33 ** 3 * rate - 33 ** 2 * 2 * PAPER_NU * om)
    a2["ns_control"] = {key: frac(v) for key, v in exact_rates(PAPER_TRIAD_1_25, exact_weight("ns", PAPER_ALPHA)).items()}
    out["A2_triad_alpha_1_25"] = a2
    # negative control: non-solenoidal mode under NS
    bad = dict(AUDIT_TRIAD_1_4)
    bad[(1, 0, 0)] = ((1, 0), (1, 0), (1, 0))
    rb = exact_rates(bad, exact_weight("ns", Fraction(1)))
    out["negative_control_ns_nonsolenoidal"] = {"divergence_of_mode_(1,0,0)": divergence((1, 0, 0), bad[(1, 0, 0)]),
                                                "dE_dt": frac(rb["dE_dt"])}
    out["A3_sweep"] = {f"alpha_{a.numerator}_{a.denominator}": triad_sweep(a, k2max)
                       for a, k2max in ((Fraction(1, 4), 12), (Fraction(1, 25), 36))}
    return out


def triad_sweep(alpha: Fraction, k2max: int) -> dict[str, Any]:
    rng = np.random.default_rng(SWEEP_SEED)
    lat = [(x, y, z) for x in range(-6, 7) for y in range(-6, 7) for z in range(-6, 7)
           if 0 < x * x + y * y + z * z <= k2max]
    fund = [k for k in lat if k[0] >= k[1] >= k[2] >= 0]
    counts: dict[str, dict[str, int]] = {kind: {"triads": 0, "dQ_nonzero": 0, "dE_nonzero": 0, "dE_positive": 0,
                                                "nonconstant_weights": 0, "nonconstant_and_dE_nonzero": 0,
                                                "constant_and_dE_nonzero": 0} for kind in KINDS}
    max_rel: dict[str, float] = {kind: 0.0 for kind in KINDS}
    weights = {kind: exact_weight(kind, alpha) for kind in KINDS}
    for p in fund:
        for q in lat:
            r = neg((p[0] + q[0], p[1] + q[1], p[2] + q[2]))
            if norm2(r) == 0 or norm2(r) > k2max:
                continue
            if len({p, q, r, neg(p), neg(q), neg(r)}) < 6:
                continue
            modes = {}
            for k in (p, q, r):
                a = tuple(int(v) for v in rng.integers(-3, 4, size=3))
                b = tuple(int(v) for v in rng.integers(-3, 4, size=3))
                modes[k] = solenoidal_amplitude(k, a, b)  # type: ignore[arg-type]
            if any(all(c == (0, 0) for c in modes[k]) for k in modes):
                continue
            for kind in KINDS:
                m = weights[kind]
                res = exact_rates(modes, m)
                c = counts[kind]
                c["triads"] += 1
                nonconst = len({m(norm2(k)) for k in (p, q, r)}) > 1
                c["nonconstant_weights"] += int(nonconst)
                if res["dQ_dt"] != 0 or res["dQ_dt_imag"] != 0:
                    c["dQ_nonzero"] += 1
                if res["dE_dt"] != 0:
                    c["dE_nonzero"] += 1
                    c["nonconstant_and_dE_nonzero"] += int(nonconst)
                    c["constant_and_dE_nonzero"] += int(not nonconst)
                    max_rel[kind] = max(max_rel[kind], abs(float(res["dE_dt"])) / float(res["E0"]) ** 1.5
                                        / max(norm2(k) for k in (p, q, r)) ** 0.5)
                c["dE_positive"] += int(res["dE_dt"] > 0)
    return {"k2max": k2max, "kstar_sq": frac(1 / alpha), "n_fundamental_p": len(fund), "counts": counts,
            "max_abs_dEdt_over_E0^1.5_kmax": max_rel,
            "note": "dE/dt is cubic in u, so its sign flips under u -> -u; dE_positive is not a growth "
                    "probability. dE_nonzero counts triads that move L2 energy at all."}


# --------------------------------------------------------------------------------------------
# B. pseudospectral Galerkin
# --------------------------------------------------------------------------------------------
def float_weight(kind: str, k2: np.ndarray, alpha: float) -> np.ndarray:
    if kind == "ns":
        return np.ones_like(k2)
    if kind == "piecewise":
        return np.where(k2 > 0, np.minimum(1.0, 1.0 / (alpha * np.where(k2 > 0, k2, 1.0))), 1.0)
    if kind == "smooth":
        return 1.0 / (1.0 + alpha * k2)
    raise ValueError(kind)


class Galerkin:
    """2/3-dealiased Fourier-Galerkin model d_t u = -P[(u.grad)(M u)] + nu Lap u on T^3."""

    def __init__(self, n: int, alpha: float, kind: str, nu: float, dealias: bool = True) -> None:
        self.n = n
        k1 = np.fft.fftfreq(n, 1.0 / n)
        kz1 = np.fft.rfftfreq(n, 1.0 / n)
        self.kx, self.ky, self.kz = np.meshgrid(k1, k1, kz1, indexing="ij")
        self.k2 = self.kx ** 2 + self.ky ** 2 + self.kz ** 2
        self.alpha = alpha
        self.kind = kind
        self.m = float_weight(kind, self.k2, alpha)
        self.nu = nu
        kmax = n // 3
        if dealias:
            self.mask = (np.abs(self.kx) < kmax) & (np.abs(self.ky) < kmax) & (np.abs(self.kz) < kmax)
        else:
            self.mask = np.abs(self.kx) < n // 2  # drop only the Nyquist planes
            self.mask &= np.abs(self.ky) < n // 2
            self.mask &= np.abs(self.kz) < n // 2
        self.k2safe = np.where(self.k2 > 0, self.k2, 1.0)
        w = np.full(self.k2.shape, 2.0)
        w[..., 0] = 1.0
        if n % 2 == 0:
            w[..., -1] = 1.0
        self.w = w / float(n ** 3) ** 2
        self.shape = (n, n, n)

    def proj(self, uh: np.ndarray) -> np.ndarray:
        kd = (self.kx * uh[0] + self.ky * uh[1] + self.kz * uh[2]) / self.k2safe
        return np.stack([uh[0] - self.kx * kd, uh[1] - self.ky * kd, uh[2] - self.kz * kd])

    def advection(self, uh: np.ndarray) -> np.ndarray:
        """(u . grad)(M u) in Fourier space, unprojected and untruncated."""
        u = sfft.irfftn(uh, s=self.shape, axes=(1, 2, 3))
        vh = self.m * uh
        grads = np.empty((3, 3) + uh.shape[1:], dtype=complex)
        for j, kj in enumerate((self.kx, self.ky, self.kz)):
            grads[j] = 1j * kj * vh
        g = sfft.irfftn(grads.reshape((9,) + uh.shape[1:]), s=self.shape, axes=(1, 2, 3)).reshape((3, 3) + self.shape)
        prod = u[0] * g[0] + u[1] * g[1] + u[2] * g[2]  # prod[i] = sum_j u_j d_j (M u)_i
        return sfft.rfftn(prod, axes=(1, 2, 3))

    def nonlinear(self, uh: np.ndarray) -> np.ndarray:
        return -self.proj(self.advection(uh) * self.mask)

    def quad(self, uh: np.ndarray, weight: np.ndarray) -> float:
        return 0.5 * float(np.sum(self.w * weight * np.sum(np.abs(uh) ** 2, axis=0)))

    def diagnostics(self, uh: np.ndarray) -> dict[str, float]:
        nl = self.nonlinear(uh)
        rate = np.real(np.sum(np.conj(uh) * nl, axis=0))
        return {"E": self.quad(uh, np.ones_like(self.k2)), "Q": self.quad(uh, self.m),
                "Omega_eff": self.quad(uh, self.k2 * self.m ** 2), "Omega_true": self.quad(uh, self.k2),
                "dE_dt_nl": float(np.sum(self.w * rate)), "dQ_dt_nl": float(np.sum(self.w * self.m * rate))}

    def step(self, uh: np.ndarray, dt: float) -> np.ndarray:
        e = np.exp(-self.nu * self.k2 * dt / 2)
        a = self.nonlinear(uh)
        b = self.nonlinear(e * (uh + dt / 2 * a))
        c = self.nonlinear(e * uh + dt / 2 * b)
        d = self.nonlinear(e * e * uh + dt * e * c)
        return e * e * uh + dt / 6 * (e * e * a + 2 * e * (b + c) + d)

    def kmax2_resolved(self) -> float:
        return float(np.max(self.k2[self.mask]))


def field_from_modes(g: Galerkin, modes: dict[Vec, tuple[GInt, GInt, GInt]], scale: float = 1.0) -> np.ndarray:
    n = g.n
    u = np.zeros((3, n, n, n), dtype=complex)
    for k, a in hermitian_field(modes).items():
        idx = tuple(c % n for c in k)
        u[(slice(None),) + idx] += scale * np.array([complex(x[0], x[1]) for x in a])
    phys = np.real(np.fft.ifftn(u, axes=(1, 2, 3))) * n ** 3
    return np.fft.rfftn(phys, axes=(1, 2, 3))


def random_field(g: Galerkin, seed: int, e0: float = E_TARGET) -> np.ndarray:
    rng = np.random.default_rng(seed)
    shape = (3,) + g.k2.shape
    uh = rng.standard_normal(shape) + 1j * rng.standard_normal(shape)
    k = np.sqrt(g.k2)
    uh = uh * np.sqrt(k ** 4 * np.exp(-2.0 * (k / KPEAK) ** 2)) * g.mask
    uh[:, 0, 0, 0] = 0
    uh = g.proj(uh)
    uh = np.fft.rfftn(np.fft.irfftn(uh, s=g.shape, axes=(1, 2, 3)), axes=(1, 2, 3))
    uh = g.proj(uh * g.mask)
    return uh * np.sqrt(e0 / g.quad(uh, np.ones_like(g.k2)))


def pad_field(uh: np.ndarray, n_from: int, n_to: int) -> np.ndarray:
    """Zero-pad an rfft field from n_from^3 to n_to^3 (identical physical field)."""
    out = np.zeros((3, n_to, n_to, n_to // 2 + 1), dtype=complex)
    k1 = np.fft.fftfreq(n_from, 1.0 / n_from).astype(int)
    for ix, kx in enumerate(k1):
        if abs(kx) >= n_from // 2:
            continue
        for iy, ky in enumerate(k1):
            if abs(ky) >= n_from // 2:
                continue
            out[:, kx % n_to, ky % n_to, : n_from // 2] = uh[:, ix, iy, : n_from // 2]
    return out * (n_to ** 3 / n_from ** 3)


def run_case(spec: dict[str, Any]) -> dict[str, Any]:
    t0 = time.time()
    n, kind, alpha, nu, dt, seed = spec["n"], spec["kind"], spec["alpha"], spec["nu"], spec["dt"], spec["seed"]
    g = Galerkin(n, alpha, kind, nu, dealias=spec.get("dealias", True))
    if spec.get("init") == "triad_1_4":
        uh = field_from_modes(g, AUDIT_TRIAD_1_4)
    elif n == N_GRID:
        uh = random_field(g, seed, spec.get("e0", E_TARGET))
    else:
        base = Galerkin(N_GRID, alpha, kind, nu)
        uh = pad_field(random_field(base, seed, spec.get("e0", E_TARGET)), N_GRID, n)
    tmax = spec.get("tmax", T_MAX)
    nsteps = int(round(tmax / dt))
    every = max(1, nsteps // N_SAMPLES)
    rows = [{"t": 0.0, **g.diagnostics(uh)}]
    finite = True
    for s in range(1, nsteps + 1):
        uh = g.step(uh, dt)
        if s % every == 0 or s == nsteps:
            d = g.diagnostics(uh)
            if not np.isfinite(d["E"]):
                finite = False
                break
            rows.append({"t": s * dt, **d})
    E0, Q0 = rows[0]["E"], rows[0]["Q"]
    E = np.array([r["E"] for r in rows])
    Q = np.array([r["Q"] for r in rows])
    Oe = np.array([r["Omega_eff"] for r in rows])
    Ot = np.array([r["Omega_true"] for r in rows])
    kmax2 = g.kmax2_resolved()
    return {**spec, "finite": finite, "wall_s": round(time.time() - t0, 2),
            "t": [r["t"] for r in rows], "E_over_E0": (E / E0).tolist(), "Q_over_Q0": (Q / Q0).tolist(),
            "alpha_Omega_eff_over_Q0": (alpha * Oe / Q0).tolist(), "alpha_Omega_true_over_E0": (alpha * Ot / E0).tolist(),
            "maxE_over_E0": float(E.max() / E0), "t_at_maxE": rows[int(E.argmax())]["t"],
            "max_abs_E_over_E0_minus_1": float(np.max(np.abs(E / E0 - 1))),
            "maxQ_over_Q0_minus_1": float(Q.max() / Q0 - 1), "Q_end_over_Q0": float(Q[-1] / Q0),
            "max_abs_Q_over_Q0_minus_1": float(np.max(np.abs(Q / Q0 - 1))),
            "max_alpha_Omega_eff_over_Q0": float((alpha * Oe / Q0).max()),
            "max_alpha_Omega_true_over_E0": float((alpha * Ot / E0).max()),
            "Galerkin_bound_E_le_max1_alphaN2_Q_holds": bool(np.all(E <= max(1.0, alpha * kmax2) * Q * (1 + 1e-12))),
            "dE_dt_nl_t0": rows[0]["dE_dt_nl"], "dQ_dt_nl_t0": rows[0]["dQ_dt_nl"]}


def validation_section() -> dict[str, Any]:
    out: dict[str, Any] = {}
    for kind in KINDS:
        for n in (16, 32):
            g = Galerkin(n, 0.25, kind, 0.0)
            d = g.diagnostics(field_from_modes(g, AUDIT_TRIAD_1_4))
            ex = exact_rates(AUDIT_TRIAD_1_4, exact_weight(kind, Fraction(1, 4)))
            out[f"triad_1_4_{kind}_N{n}"] = {"dE_dt_float": d["dE_dt_nl"], "dE_dt_exact": float(ex["dE_dt"]),
                                             "abs_err": abs(d["dE_dt_nl"] - float(ex["dE_dt"])),
                                             "dQ_dt_float": d["dQ_dt_nl"], "E_float": d["E"], "E_exact": float(ex["E0"])}
    g = Galerkin(32, 1 / 25, "piecewise", 0.0)
    d = g.diagnostics(field_from_modes(g, PAPER_TRIAD_1_25))
    ex = exact_rates(PAPER_TRIAD_1_25, exact_weight("piecewise", PAPER_ALPHA))
    out["triad_1_25_piecewise_N32"] = {"dE_dt_float": d["dE_dt_nl"], "dE_dt_exact": float(ex["dE_dt"]),
                                       "abs_err": abs(d["dE_dt_nl"] - float(ex["dE_dt"])),
                                       "Omega_float": d["Omega_true"], "Omega_exact": float(ex["Omega_true"])}
    out["max_abs_err"] = max(v["abs_err"] for v in out.values() if isinstance(v, dict))
    return out


def run_all(specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    with ProcessPoolExecutor(max_workers=max(1, (os.cpu_count() or 2) - 1)) as ex:
        return list(ex.map(run_case, specs, chunksize=1))


def main() -> int:
    t_start = time.time()
    results: dict[str, Any] = {
        "meta": {"script": "scripts/three_breakthroughs/paper_b_v2_experiment.py", "date": "2026-10-21",
                 "python": sys.version.split()[0], "numpy": np.__version__, "platform": platform.platform(),
                 "N": N_GRID, "dt": DT, "T": T_MAX, "kpeak": KPEAK, "E0": E_TARGET, "seeds": list(SEEDS),
                 "lean_files": ["formal/ANSE/PaperB_EnergyBudget.lean", "formal/ANSE/PaperB_ScaleDualEd2.lean"]},
    }
    print("A: exact arithmetic", flush=True)
    results["exact"] = exact_section()
    print("B1: validation", flush=True)
    results["validation"] = validation_section()

    ensemble = [{"group": "ensemble", "n": N_GRID, "kind": kind, "alpha": float(a), "alpha_exact": str(a),
                 "nu": float(nu), "nu_exact": str(nu), "dt": DT, "seed": s, "e0": E_TARGET}
                for kind in KINDS for a in (ALPHAS if kind != "ns" else (Fraction(1, 25),))
                for nu in NUS for s in SEEDS]
    paper = {"alpha": float(PAPER_ALPHA), "alpha_exact": str(PAPER_ALPHA), "nu": float(PAPER_NU), "nu_exact": str(PAPER_NU)}
    amp = [{"group": "amplitude_scan", "n": N_GRID, "kind": kind, "dt": DT, "seed": s, "e0": e0, **paper}
           for e0 in AMP_E0 for kind in KINDS for s in AMP_SEEDS]
    conv = []
    for e0 in CONV_E0:
        for kind in KINDS:
            for s in (0, 1, 2):
                base = {"kind": kind, "seed": s, "e0": e0, **paper}
                conv.append({"group": "conv_N64", "n": 64, "dt": DT, **base})
                conv.append({"group": "conv_dt_half", "n": N_GRID, "dt": DT / 2, **base})
    extra = [
        {"group": "aliased_ns_negative_control", "n": N_GRID, "kind": "ns", "alpha": 0.04, "alpha_exact": "1/25",
         "nu": 0.0, "nu_exact": "0", "dt": DT, "seed": 0, "dealias": False},
        {"group": "inviscid_N64_piecewise", "n": 64, "kind": "piecewise", "alpha": 0.04, "alpha_exact": "1/25",
         "nu": 0.0, "nu_exact": "0", "dt": DT, "seed": 0},
    ]
    for kind in KINDS:
        for nu in (0.0, 0.01):
            extra.append({"group": "triad_1_4_evolution", "init": "triad_1_4", "n": N_GRID, "kind": kind, "alpha": 0.25,
                          "alpha_exact": "1/4", "nu": nu, "nu_exact": "0" if nu == 0 else "1/100", "dt": 0.002,
                          "tmax": 2.0, "seed": -1})
    specs = conv + ensemble + amp + extra  # longest runs first
    print(f"B2/B3: {len(specs)} runs", flush=True)
    runs = run_all(specs)
    results["runs"] = runs
    results["summary"] = summarize(results, runs)
    results["meta"]["wall_s"] = round(time.time() - t_start, 1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=1, default=str))
    print(json.dumps(results["summary"], indent=1, default=str))
    print(f"wrote {OUT}")
    return 0


def _stats(xs: list[float]) -> dict[str, float]:
    a = np.array(xs)
    return {"mean": float(a.mean()), "std": float(a.std(ddof=1)) if a.size > 1 else 0.0,
            "min": float(a.min()), "max": float(a.max()), "n": int(a.size)}


def summarize(results: dict[str, Any], runs: list[dict[str, Any]]) -> dict[str, Any]:
    ens = [r for r in runs if r["group"] == "ensemble"]
    table: dict[str, Any] = {}
    for r in ens:
        key = f"{r['kind']}|alpha={r['alpha_exact']}|nu={r['nu_exact']}"
        table.setdefault(key, []).append(r)
    tab_out = {}
    for key, rs in table.items():
        tab_out[key] = {"maxE_over_E0": _stats([r["maxE_over_E0"] for r in rs]),
                        "t_at_maxE": _stats([r["t_at_maxE"] for r in rs]),
                        "max_abs_Q_over_Q0_minus_1": _stats([r["max_abs_Q_over_Q0_minus_1"] for r in rs]),
                        "maxQ_over_Q0_minus_1": _stats([r["maxQ_over_Q0_minus_1"] for r in rs]),
                        "Q_end_over_Q0": _stats([r["Q_end_over_Q0"] for r in rs]),
                        "max_alpha_Omega_eff_over_Q0": _stats([r["max_alpha_Omega_eff_over_Q0"] for r in rs]),
                        "max_alpha_Omega_true_over_E0": _stats([r["max_alpha_Omega_true_over_E0"] for r in rs]),
                        "dE_dt_nl_t0": _stats([r["dE_dt_nl_t0"] for r in rs]),
                        "n_runs_E_exceeds_E0": sum(int(r["maxE_over_E0"] > 1 + 1e-9) for r in rs),
                        "all_finite": all(r["finite"] for r in rs),
                        "galerkin_bound_holds_all": all(r["Galerkin_bound_E_le_max1_alphaN2_Q_holds"] for r in rs)}
    ex = results["exact"]
    a1, a2 = ex["A1_triad_alpha_1_4"], ex["A2_triad_alpha_1_25"]
    sweeps = ex["A3_sweep"]
    model_runs = [r for r in ens if r["kind"] != "ns"]
    # controls
    ns_inv = [r for r in ens if r["kind"] == "ns" and r["nu"] == 0.0]
    aliased = [r for r in runs if r["group"] == "aliased_ns_negative_control"][0]
    pos = {
        "exact_ns_triad_dE_dt_zero": a1["ns"]["dE_dt"]["exact"] == "0" and a1["ns"]["dQ_dt"]["exact"] == "0",
        "exact_ns_triad_1_25_dE_dt_zero": a2["ns_control"]["dE_dt"]["exact"] == "0",
        "exact_sweep_ns_dE_nonzero_count": {k: v["counts"]["ns"]["dE_nonzero"] for k, v in sweeps.items()},
        "exact_sweep_constant_weight_triads_dE_nonzero": {k: {kind: v["counts"][kind]["constant_and_dE_nonzero"] for kind in KINDS} for k, v in sweeps.items()},
        "float_validation_max_abs_err": results["validation"]["max_abs_err"],
        "inviscid_ns_max_abs_E_drift": max(r["max_abs_E_over_E0_minus_1"] for r in ns_inv),
        "model_inviscid_max_abs_Q_drift": max(r["max_abs_Q_over_Q0_minus_1"] for r in model_runs if r["nu"] == 0.0),
        "model_viscous_max_Q_increase": max(r["maxQ_over_Q0_minus_1"] for r in model_runs if r["nu"] > 0.0),
        "max_alpha_Omega_eff_over_Q0_all_model_runs": max(r["max_alpha_Omega_eff_over_Q0"] for r in model_runs),
    }
    pos["passed"] = bool(pos["exact_ns_triad_dE_dt_zero"] and pos["exact_ns_triad_1_25_dE_dt_zero"]
                         and all(v == 0 for v in pos["exact_sweep_ns_dE_nonzero_count"].values())
                         and pos["float_validation_max_abs_err"] < 1e-10
                         and pos["inviscid_ns_max_abs_E_drift"] < 1e-6
                         and pos["max_alpha_Omega_eff_over_Q0_all_model_runs"] <= 1 + 1e-12)
    negc = {
        "exact_ns_nonsolenoidal_dE_dt": ex["negative_control_ns_nonsolenoidal"]["dE_dt"],
        "aliased_ns_max_abs_E_drift": aliased["max_abs_E_over_E0_minus_1"],
        "dealiased_ns_max_abs_E_drift_same_seed": [r for r in ns_inv if r["seed"] == 0][0]["max_abs_E_over_E0_minus_1"],
        "ns_true_enstrophy_exceeds_E0_over_alpha_runs": sum(int(r["max_alpha_Omega_true_over_E0"] > 1) for r in ens if r["kind"] == "ns"),
    }
    negc["passed"] = bool(negc["exact_ns_nonsolenoidal_dE_dt"]["exact"] != "0"
                          and negc["aliased_ns_max_abs_E_drift"] > 10 * max(negc["dealiased_ns_max_abs_E_drift_same_seed"], 1e-12))
    # falsification of the edition-2 claim
    dq_nonzero = sum(v["counts"][kind]["dQ_nonzero"] for v in sweeps.values() for kind in KINDS)
    a1_dq = [a1[k]["dQ_dt"]["exact"] for k in KINDS]
    nonconst_dE = {k: {kind: v["counts"][kind]["nonconstant_and_dE_nonzero"] for kind in ("piecewise", "smooth")} for k, v in sweeps.items()}
    ed2_falsified = dq_nonzero > 0 or any(x != "0" for x in a1_dq) or all(x == 0 for d in nonconst_dE.values() for x in d.values())
    # edition-1 Theorem 2.5 at the paper's parameters, for every pre-registered amplitude E0
    paper_key = lambda kind: f"{kind}|alpha=1/25|nu=1/100"  # noqa: E731
    amp_runs = [r for r in runs if r["group"] == "amplitude_scan"]
    verdicts: dict[str, Any] = {}
    for e0 in (E_TARGET,) + AMP_E0:
        pool = ens if e0 == E_TARGET else amp_runs
        sel = [r for r in pool if r["e0"] == e0 and r["alpha_exact"] == "1/25" and r["nu_exact"] == "1/100"]
        ns_sel = [r for r in sel if r["kind"] == "ns"]
        ns_excess = max(max(r["maxE_over_E0"] - 1 for r in ns_sel), 1e-12)
        vd: dict[str, Any] = {"ns_control_max_excess": ns_excess,
                              "ns_maxE_over_E0": _stats([r["maxE_over_E0"] for r in ns_sel])}
        for kind in ("piecewise", "smooth"):
            base = [r for r in sel if r["kind"] == kind]
            exceed = [r["maxE_over_E0"] - 1 for r in base]
            persist = []
            if e0 in CONV_E0:
                for s in (0, 1, 2):
                    b = [r for r in base if r["seed"] == s][0]
                    r64 = [r for r in runs if r["group"] == "conv_N64" and r["kind"] == kind and r["e0"] == e0 and r["seed"] == s][0]
                    rdt = [r for r in runs if r["group"] == "conv_dt_half" and r["kind"] == kind and r["e0"] == e0 and r["seed"] == s][0]
                    persist.append({"seed": s, "maxE_N32": b["maxE_over_E0"], "maxE_N64": r64["maxE_over_E0"],
                                    "maxE_dt_half": rdt["maxE_over_E0"],
                                    "rel_change_N64": abs(r64["maxE_over_E0"] - b["maxE_over_E0"]) / b["maxE_over_E0"],
                                    "rel_change_dt_half": abs(rdt["maxE_over_E0"] - b["maxE_over_E0"]) / b["maxE_over_E0"],
                                    "exceeds_in_all_three": all(x - 1 > 10 * ns_excess for x in (b["maxE_over_E0"], r64["maxE_over_E0"], rdt["maxE_over_E0"]))})
            vd[kind] = {"n_seeds_maxE_exceeds_10x_ns_control": sum(int(x > 10 * ns_excess) for x in exceed),
                        "n_seeds": len(base), "maxE_over_E0": _stats([r["maxE_over_E0"] for r in base]),
                        "t_at_maxE": _stats([r["t_at_maxE"] for r in base]),
                        "max_alpha_Omega_eff_over_Q0": _stats([r["max_alpha_Omega_eff_over_Q0"] for r in base]),
                        "persistence": persist}
        verdicts[f"E0={e0:g}"] = vd
    exact_positive = a2.get("lambda_star_growth_threshold") is not None
    refuted = {kind: [e for e, vd in verdicts.items()
                      if exact_positive and vd[kind]["n_seeds_maxE_exceeds_10x_ns_control"] > 0
                      and any(p["exceeds_in_all_three"] for p in vd[kind]["persistence"])]
               for kind in ("piecewise", "smooth")}
    return {"ensemble_table": tab_out, "positive_controls": pos, "negative_controls": negc,
            "falsification": {"edition2_claim_Q_invariant_E_not": "FALSIFIED" if ed2_falsified else "NOT FALSIFIED",
                              "exact_dQ_nonzero_fields": dq_nonzero, "exact_nonconstant_triads_with_dE_nonzero": nonconst_dE,
                              "edition1_thm25_E_le_E0_at_alpha_1_25_nu_1_100": {
                                  "exact_rate_positive_for_some_amplitude": exact_positive,
                                  "piecewise": ("REFUTED at " + ", ".join(refuted["piecewise"])) if refuted["piecewise"] else ("INSTANTANEOUS ONLY" if exact_positive else "NOT REFUTED"),
                                  "smooth": ("E(t) > E0 persists at " + ", ".join(refuted["smooth"])) if refuted["smooth"] else "no persistent E(t) > E0",
                                  "details": verdicts}},
            "triad_1_4_evolution": {f"{r['kind']}_nu{r['nu_exact']}": {"maxE_over_E0": r["maxE_over_E0"], "t_at_maxE": r["t_at_maxE"],
                                                                     "max_abs_Q_over_Q0_minus_1": r["max_abs_Q_over_Q0_minus_1"],
                                                                     "Q_end_over_Q0": r["Q_end_over_Q0"]}
                                    for r in runs if r["group"] == "triad_1_4_evolution"},
            "inviscid_piecewise_N32_vs_N64_seed0": {
                "N32": [r for r in ens if r["kind"] == "piecewise" and r["alpha_exact"] == "1/25" and r["nu"] == 0.0 and r["seed"] == 0][0]["maxE_over_E0"],
                "N64": [r for r in runs if r["group"] == "inviscid_N64_piecewise"][0]["maxE_over_E0"]}}


if __name__ == "__main__":
    raise SystemExit(main())
