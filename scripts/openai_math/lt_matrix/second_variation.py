#!/usr/bin/env python3
"""H-LT3: second variation of log R at the embedded scalar extremiser B* = diag(sqrt(r+1) sech(r x), 0, ..., 0).

R[W] = Tr(-d^2 - W)_-^gamma / int tr W^(gamma+1/2),  W = B^dagger B,  r = 1/(gamma - 1/2)  (see instrument.py).
Parameters theta = (Re c, Im c, log kappa, x0) of ONE Blobs blob (K = 1): B_ab(x) = sech(z) sum_p c_abp T_p(tanh z),
z = kappa (x - x0).  theta0 = B*.

Hessian of log R at theta0 by torch autograd.  Why a surrogate is needed (and why it is exact to second order):
at theta0 the zero channels are degenerate (eigh/eigvalsh double backward divides by zero gaps) and tr W^p has a
non-smooth eigenvalue structure at W = rank one.  So the objective differentiated is

  numerator:  sum over the negative eigenpairs (E_k, v_k) of the base Galerkin matrix H0 of (-E_k)^gamma, with E_k(theta) the
              Rayleigh quotient of the FIRST-ORDER perturbed vector  v_k + S_k (H(theta) - H0) v_k,
              S_k = sum_{j != k} |j><j| / (E_k - E_j).  A Rayleigh quotient of a vector correct to first order is correct to third
              order in the perturbation, so value, gradient and Hessian at theta0 are those of the exact eigenvalue.
  denominator: int (a + |b|^2 / a)^p,  a = W_11, b = W_{j1} (j >= 2): the Schur-complement top eigenvalue of W(x), exact to
              second order; the omitted lesser eigenvalues of W are O(eps^2) and contribute O(eps^(2p)), 2p > 2.5: they
              add a NON-NEGATIVE term to the true denominator, so the surrogate can only OVERESTIMATE R: conservative for a kill test.

The surrogate is validated against the true eigen-based R by central finite differences (rank-one directions: exact).
"""

from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):  # LAPACK threads leak past torch.set_num_threads
    os.environ.setdefault(_v, "2")

import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path
from typing import Callable

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from instrument import Grid, numerator_denominator, sharp_constant  # noqa: E402

torch.set_default_dtype(torch.float64)
HERE = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------- parametrisation
def n_params(m: int, P: int) -> int:
    return 2 * m * m * (P + 1) + 2


def unpack(theta: torch.Tensor, m: int, P: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    s = m * m * (P + 1)
    cr = theta[:s].reshape(m, m, P + 1)
    ci = theta[s : 2 * s].reshape(m, m, P + 1)
    return cr, ci, theta[2 * s], theta[2 * s + 1]


def idx_c(m: int, P: int, a: int, b: int, p: int, imag: bool) -> int:
    s = m * m * (P + 1)
    return (s if imag else 0) + (a * m + b) * (P + 1) + p


def idx_logk(m: int, P: int) -> int:
    return 2 * m * m * (P + 1)


def idx_x0(m: int, P: int) -> int:
    return 2 * m * m * (P + 1) + 1


def B_of(theta: torch.Tensor, x: torch.Tensor, m: int, P: int) -> torch.Tensor:
    """(Q, m, m) complex B(x); identical to Blobs.B for K = 1 (asserted in the tests)."""
    cr, ci, logk, x0 = unpack(theta, m, P)
    z = torch.exp(logk) * (x - x0)
    s, t = 1.0 / torch.cosh(z), torch.tanh(z)
    cheb = [torch.ones_like(t), t]
    for _ in range(2, P + 1):
        cheb.append(2 * t * cheb[-1] - cheb[-2])
    Tp = torch.stack(cheb[: P + 1], dim=1).to(torch.complex128)
    c = torch.complex(cr, ci)
    return s[:, None, None].to(torch.complex128) * torch.einsum("qp,abp->qab", Tp, c)


def W_of(theta: torch.Tensor, x: torch.Tensor, m: int, P: int) -> torch.Tensor:
    B = B_of(theta, x, m, P)
    return B.conj().transpose(1, 2) @ B


def theta_star(gamma: float, m: int, P: int) -> torch.Tensor:
    r = 1.0 / (gamma - 0.5)
    th = torch.zeros(n_params(m, P))
    th[idx_c(m, P, 0, 0, 0, False)] = math.sqrt(r + 1)
    th[idx_logk(m, P)] = math.log(r)
    return th


def flat_directions(gamma: float, m: int, P: int) -> dict[str, torch.Tensor]:
    """Exactly flat directions of log R at theta0.  trans/dil: the scalar symmetries (the two named in the preregistration);
    the rest are symmetry-orbit tangents (left gauge B -> V B, right rotation B -> B U) listed for the extended control."""
    r = 1.0 / (gamma - 0.5)
    amp = math.sqrt(r + 1)
    n = n_params(m, P)
    out: dict[str, torch.Tensor] = {}
    v = torch.zeros(n); v[idx_x0(m, P)] = 1.0; out["translation"] = v
    v = torch.zeros(n); v[idx_logk(m, P)] = 1.0; v[idx_c(m, P, 0, 0, 0, False)] = amp; out["dilation"] = v
    sym: dict[str, torch.Tensor] = {}
    for j in range(m):
        for imag in (False, True):
            if j == 0 and not imag:
                continue  # real A_00 is not anti-Hermitian (it is the dilation amplitude)
            v = torch.zeros(n); v[idx_c(m, P, j, 0, 0, imag)] = amp; sym[f"left_gauge_row{j}_{'im' if imag else 're'}"] = v
    for b in range(1, m):
        for imag in (False, True):
            v = torch.zeros(n); v[idx_c(m, P, 0, b, 0, imag)] = amp; sym[f"right_rot_col{b}_{'im' if imag else 're'}"] = v
    out.update(sym)
    return out


# ---------------------------------------------------------------- objective(s)
def build_H(W: torch.Tensor, grid: Grid) -> torch.Tensor:
    """Same Galerkin matrix as instrument.numerator_denominator (re-derived to expose H; checked against it in the tests)."""
    m = W.shape[1]
    phi = grid.phi.to(W.dtype)
    wq = grid.w.to(W.dtype)
    blocks = [[phi.T @ ((wq * W[:, a, b])[:, None] * phi) for b in range(m)] for a in range(m)]
    V = torch.stack([torch.stack([blocks[a][b] for b in range(m)], dim=-1) for a in range(m)], dim=1)
    n = grid.M * m
    return torch.diag_embed(grid.T.repeat_interleave(m).to(W.dtype)) - V.reshape(n, n)


def log_ratio_true(theta: torch.Tensor, gamma: float, m: int, P: int, grid: Grid) -> float:
    """log R from the frozen instrument (eigen-based, exact structure of the problem)."""
    with torch.no_grad():
        num, den, _ = numerator_denominator(W_of(theta, grid.x, m, P), gamma, grid)
    return float(torch.log(num) - torch.log(den))


class Surrogate:
    """Smooth objective whose value/gradient/Hessian at theta0 equal those of log R (see module docstring)."""

    def __init__(self, gamma: float, m: int, P: int, grid: Grid, theta0: torch.Tensor) -> None:
        self.gamma, self.m, self.P, self.grid = gamma, m, P, grid
        self.theta0 = theta0.clone()
        with torch.no_grad():
            H0 = build_H(W_of(theta0, grid.x, m, P), grid)
            E, V = torch.linalg.eigh(H0)
        self.H0 = H0
        self.k = int((E < 0).sum())
        if self.k == 0:
            raise ValueError("no negative eigenvalue at theta0")
        self.E = E
        self.V = V
        Eneg = E[: self.k]
        gap = Eneg[None, :] - E[:, None]  # (n, k): E_k - E_j
        D = torch.zeros_like(gap)
        for k in range(self.k):
            mask = torch.ones(E.shape[0], dtype=torch.bool)
            mask[k] = False
            D[mask, k] = 1.0 / gap[mask, k]
        self.D = D
        self.Vneg = V[:, : self.k]
        self.min_gap = float(gap.abs()[~torch.eye(E.shape[0], self.k, dtype=torch.bool)].min())

    def energies(self, theta: torch.Tensor) -> torch.Tensor:
        W = W_of(theta, self.grid.x, self.m, self.P)
        H = build_H(W, self.grid)
        dHv = (H - self.H0) @ self.Vneg
        coef = (self.V.conj().T @ dHv) * self.D
        u = self.Vneg + self.V @ coef
        Hu = H @ u
        return ((u.conj() * Hu).sum(0) / (u.conj() * u).sum(0)).real

    def log_ratio(self, theta: torch.Tensor) -> torch.Tensor:
        Es = self.energies(theta)
        num = ((-Es) ** self.gamma).sum()
        B = B_of(theta, self.grid.x, self.m, self.P)
        W = B.conj().transpose(1, 2) @ B
        a = W[:, 0, 0].real
        lam = a
        if self.m > 1:
            bj = W[:, 1:, 0]
            lam = a + (bj.real**2 + bj.imag**2).sum(1) / a  # not abs()**2: abs has zero gradient at 0 and would drop this term from the Hessian
        den = (self.grid.w * lam ** (self.gamma + 0.5)).sum()
        return torch.log(num) - torch.log(den)


def autograd_hessian(f: Callable[[torch.Tensor], torch.Tensor], theta0: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    th = theta0.clone().requires_grad_(True)
    val = f(th)
    (g,) = torch.autograd.grad(val, th, create_graph=True)
    rows = []
    for i in range(th.numel()):
        (row,) = torch.autograd.grad(g[i], th, retain_graph=True)
        rows.append(row)
    H = torch.stack(rows)
    return 0.5 * (H + H.T).detach(), g.detach()


def fd_second(f: Callable[[torch.Tensor], float], theta0: torch.Tensor, v: torch.Tensor, eps: float) -> float:
    v = v / v.norm()
    return (f(theta0 + eps * v) + f(theta0 - eps * v) - 2 * f(theta0)) / eps**2


def complement_basis(flats: list[torch.Tensor]) -> torch.Tensor:
    """Orthonormal basis (columns) of the Euclidean orthogonal complement of span(flats)."""
    n = flats[0].numel()
    F = torch.stack(flats, dim=1)
    Q, _ = torch.linalg.qr(F, mode="complete")
    return Q[:, F.shape[1] :]


# ---------------------------------------------------------------- one cell
def run_cell(gamma: float, m: int, P: int, grid: Grid, eps_list: list[float], tol_abs: float, tol_rel: float, seed: int = 7) -> dict:
    t0 = time.time()
    L1 = sharp_constant(gamma)
    theta0 = theta_star(gamma, m, P)
    sur = Surrogate(gamma, m, P, grid, theta0)
    f_sur = lambda th: sur.log_ratio(th)
    H, g = autograd_hessian(f_sur, theta0)
    flats = flat_directions(gamma, m, P)
    trans, dil = flats["translation"], flats["dilation"]
    Z = complement_basis([trans / trans.norm(), dil / dil.norm()])
    Hr = Z.T @ H @ Z
    ev, evec = torch.linalg.eigh(0.5 * (Hr + Hr.T))
    hnorm = float(ev.abs().max())
    thr = max(tol_rel * hnorm, tol_abs)
    lam_max = float(ev[-1])
    # control (b): Hessian along exactly flat directions
    ctrl_b = {}
    for name, v in flats.items():
        u = v / v.norm()
        ctrl_b[name] = {"quad": float(u @ H @ u), "Hv_norm": float((H @ u).norm())}
    quad_td = max(abs(ctrl_b["translation"]["quad"]), abs(ctrl_b["dilation"]["quad"]))
    quad_sym = max(abs(d["quad"]) for d in ctrl_b.values())
    # value/gradient diagnostics
    val_sur = float(f_sur(theta0))
    val_true = log_ratio_true(theta0, gamma, m, P, grid)
    # finite differences of the TRUE objective along the top eigenvectors and rank-one (row 0) random directions
    f_true = lambda th: log_ratio_true(th, gamma, m, P, grid)
    f_sur_float = lambda th: float(sur.log_ratio(th))
    rng = torch.Generator().manual_seed(seed)
    top_dirs = [Z @ evec[:, -1 - i] for i in range(min(3, evec.shape[1]))]
    row0 = []
    for _ in range(3):
        v = torch.zeros(theta0.numel())
        for b in range(m):
            for imag in (False, True):
                for p in range(P + 1):
                    v[idx_c(m, P, 0, b, p, imag)] = float(torch.randn((), generator=rng))
        v[idx_logk(m, P)] = float(torch.randn((), generator=rng))
        v[idx_x0(m, P)] = float(torch.randn((), generator=rng))
        row0.append(v / v.norm())
    fd_report = []
    for label, dirs in (("top_eigenvector", top_dirs), ("row0_random", row0)):
        for i, v in enumerate(dirs):
            h_ad = float(v @ H @ v)
            ent = {"set": label, "i": i, "autograd_quad": h_ad, "fd_true": {}, "fd_surrogate": {}}
            for e in eps_list:
                ent["fd_true"][str(e)] = fd_second(f_true, theta0, v, e)
                ent["fd_surrogate"][str(e)] = fd_second(f_sur_float, theta0, v, e)
            fd_report.append(ent)
    row0_ok = all(abs(e["fd_true"][str(eps_list[0])] - e["autograd_quad"]) <= 1e-4 * max(1.0, abs(e["autograd_quad"]))
                  for e in fd_report if e["set"] == "row0_random")
    sur_ok = all(abs(e["fd_surrogate"][str(eps_list[0])] - e["autograd_quad"]) <= 1e-4 * max(1.0, abs(e["autograd_quad"])) for e in fd_report)
    # finite-eps confirmation of every eigenvector with lambda > thr, plus the top 3 regardless, on the refined grid
    g2 = grid.refined()
    base2 = log_ratio_true(theta0, gamma, m, P, g2)
    confirm = []
    cand = [i for i in range(ev.numel()) if float(ev[i]) > thr]
    cand = sorted(set(cand[-6:] + list(range(ev.numel() - 3, ev.numel()))))
    for i in cand:
        v = Z @ evec[:, i]
        ent = {"eigenvalue": float(ev[i]), "positive_beyond_threshold": bool(float(ev[i]) > thr), "delta_logR_refined": {}, "ratio_to_quadratic": {}}
        for e in eps_list:
            d = log_ratio_true(theta0 + e * v, gamma, m, P, g2) - base2
            d_minus = log_ratio_true(theta0 - e * v, gamma, m, P, g2) - base2
            ent["delta_logR_refined"][str(e)] = {"plus": d, "minus": d_minus}
            ent["ratio_to_quadratic"][str(e)] = (0.5 * (d + d_minus)) / (0.5 * float(ev[i]) * e**2) if abs(float(ev[i])) > 0 else float("nan")
        confirm.append(ent)
    n_pos = int((ev > thr).sum())
    n_zero = int((ev.abs() <= thr).sum())
    n_neg = int((ev < -thr).sum())
    confirmed = [c for c in confirm if c["positive_beyond_threshold"]
                 and all(c["delta_logR_refined"][str(e)]["plus"] > 1e-12 and c["delta_logR_refined"][str(e)]["minus"] > 1e-12
                         for e in eps_list[:2])]
    return {
        "gamma": gamma, "m": m, "P": P, "grid": {"L": grid.L, "M": grid.M, "Q": grid.Q}, "L1": L1,
        "value_true_logR": val_true, "value_surrogate_logR": val_sur, "excess_over_L1_at_theta0": math.exp(val_true) / L1 - 1.0,
        "gradient_norm": float(g.norm()), "base_logR_refined_grid": base2, "refined_excess_over_L1": math.exp(base2) / L1 - 1.0,
        "n_negative_bound_states_at_theta0": sur.k, "min_gap_used": sur.min_gap,
        "hessian_threshold": thr, "hessian_spectral_norm_restricted": hnorm,
        "spectrum_restricted": [float(x) for x in ev],
        "lambda_max_restricted": lam_max, "n_positive_beyond_thr": n_pos, "n_zero_within_thr": n_zero, "n_negative_beyond_thr": n_neg,
        "control_b_flat_directions": ctrl_b,
        "control_b_quad_translation_dilation_max": quad_td, "control_b_quad_all_symmetry_max": quad_sym,
        "fd_vs_autograd": fd_report, "control_d_rank_one_fd_matches_autograd": bool(row0_ok),
        "control_d_surrogate_fd_matches_autograd": bool(sur_ok),
        "finite_eps_confirmation": confirm, "n_confirmed_positive": len(confirmed),
        "elapsed_s": round(time.time() - t0, 1),
    }


def cell_verdict(cell: dict, tol_flat: float, negative_control: bool = False, tol_grad: float = 1e-6) -> str:
    """Mechanical verdict.  Positive cells (gamma < 3/2): gates first (FD agreement, criticality, flatness), then the spectrum.
    Negative control (gamma = 3): theta0 is NOT critical there, so only the FD-agreement gate and 'a confirmed positive direction' count."""
    if not (cell["control_d_rank_one_fd_matches_autograd"] and cell["control_d_surrogate_fd_matches_autograd"]):
        return "VOID_FD_DISAGREES"
    if negative_control:
        return "NEGATIVE_CONTROL_PASS" if cell["n_confirmed_positive"] > 0 else "NEGATIVE_CONTROL_FAIL"
    if cell.get("gradient_norm", 0.0) > tol_grad:
        return "VOID_NOT_CRITICAL"
    if cell["control_b_quad_translation_dilation_max"] > tol_flat:
        return "VOID_FLAT_DIRECTION_NOT_FLAT"
    if cell["n_positive_beyond_thr"] == 0:
        return "NONPOSITIVE_SECOND_VARIATION"
    return "POSITIVE_CONFIRMED_KILLS_H_LT3" if cell["n_confirmed_positive"] > 0 else "UNDECIDED_POSITIVE_UNCONFIRMED"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gamma", type=float, required=True)
    ap.add_argument("--m", type=int, required=True)
    ap.add_argument("--P", type=int, default=8)
    ap.add_argument("--L", type=float, default=24.0)
    ap.add_argument("--M", type=int, default=160)
    ap.add_argument("--Q", type=int, default=1200)
    ap.add_argument("--eps", type=float, nargs="+", default=[1e-3, 2e-3, 4e-3])
    ap.add_argument("--tol-abs", type=float, default=1e-8)
    ap.add_argument("--tol-rel", type=float, default=1e-6)
    ap.add_argument("--tol-flat", type=float, default=1e-8)
    ap.add_argument("--tol-grad", type=float, default=1e-6)
    ap.add_argument("--negative-control", action="store_true")
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    grid = Grid(a.L, a.M, a.Q)
    cell = run_cell(a.gamma, a.m, a.P, grid, a.eps, a.tol_abs, a.tol_rel)
    cell["verdict"] = cell_verdict(cell, a.tol_flat, a.negative_control, a.tol_grad)
    cell["second_variation_sha256"] = sha(HERE / "second_variation.py")
    cell["instrument_sha256"] = sha(HERE / "instrument.py")
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(cell, indent=2) + "\n")
    print(json.dumps({k: cell[k] for k in ("gamma", "m", "verdict", "lambda_max_restricted", "n_positive_beyond_thr", "n_confirmed_positive",
                                            "control_b_quad_translation_dilation_max", "gradient_norm", "elapsed_s")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
