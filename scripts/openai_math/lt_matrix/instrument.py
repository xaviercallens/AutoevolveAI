#!/usr/bin/env python3
"""Instrument for the matrix-valued one-dimensional Lieb-Thirring inequality (openai/math family 262).

Claim under test (upstream CONTENTS.md family 262, two manuscripts dated 2026-10-05, NOT covered by the Lean
formalisation, which states the scalar case only): for 1/2 < gamma < 3/2, every m x m Hermitian W(x) >= 0,

    Tr (-d^2/dx^2 (x) 1_m - W)_-^gamma  <=  L1(gamma) * int tr W(x)^(gamma + 1/2) dx,

with L1 the scalar one-bound-state constant (Lean `sharpConstant`).  R[W] := numerator / denominator.

Design for one-sided numerical error (so that discretisation cannot manufacture a violation):
* W is truncated to the box [-L, L] (zero outside) and the operator carries Dirichlet conditions there.  Dirichlet
  domain monotonicity: every negative eigenvalue of the box problem is >= the corresponding eigenvalue of the
  whole-line problem with the same W, so |E_j|^gamma (box) <= |E_j|^gamma (line).
* The box operator is discretised by Rayleigh-Ritz in the sine basis phi_j = sqrt(1/L) sin(j pi (x+L)/(2L)).
  Rayleigh-Ritz eigenvalues are upper bounds of the box eigenvalues, so again |E|^gamma can only shrink.
So with exact matrix elements the computed numerator is a LOWER bound for the true numerator of the same W.
Remaining error: Gauss-Legendre quadrature of the matrix elements and of the denominator (checked by doubling Q).

The potentials are W = B^dagger B with  B_ab(x) = sum_k sech(kappa_k (x - x0_k)) sum_p c_kabp T_p(tanh(kappa_k (x - x0_k))),
which contains the exact scalar optimiser sqrt(r+1) sech(r x) (p = 0, kappa = r).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import torch

torch.set_default_dtype(torch.float64)


def semiclassical_constant(gamma: float) -> float:
    return math.gamma(gamma + 1) / (2 * math.sqrt(math.pi) * math.gamma(gamma + 1.5))


def sharp_constant(gamma: float) -> float:
    """Lean `sharpConstant`: 2 ((g-1/2)/(g+1/2))^(g-1/2) * semiclassicalConstant g (the one-bound-state constant for g < 3/2)."""
    return 2 * ((gamma - 0.5) / (gamma + 0.5)) ** (gamma - 0.5) * semiclassical_constant(gamma)


@dataclass
class Grid:
    L: float = 24.0
    M: int = 160
    Q: int = 1200

    def __post_init__(self) -> None:
        x, w = np.polynomial.legendre.leggauss(self.Q)
        self.x = torch.tensor(self.L * x)
        self.w = torch.tensor(self.L * w)
        j = torch.arange(1, self.M + 1, dtype=torch.float64)
        self.phi = torch.sqrt(torch.tensor(1.0 / self.L)) * torch.sin(j[None, :] * math.pi * (self.x[:, None] + self.L) / (2 * self.L))
        self.T = (j * math.pi / (2 * self.L)) ** 2

    def refined(self) -> "Grid":
        return Grid(self.L, 2 * self.M, 2 * self.Q)


def numerator_denominator(W: torch.Tensor, gamma: float, grid: Grid) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """W: (Q, m, m) Hermitian PSD at the grid's Gauss nodes.  Returns (numerator, denominator, negative |E| list)."""
    Q, m, _ = W.shape
    phi = grid.phi.to(W.dtype)
    # V[(j,a),(k,b)] = sum_q w_q phi_j(x_q) phi_k(x_q) W_ab(x_q): one (M x Q)(Q x M) matmul per (a, b), no Q x M x M intermediate.
    blocks = [[phi.T @ ((grid.w.to(W.dtype) * W[:, a, b])[:, None] * phi) for b in range(m)] for a in range(m)]
    n = grid.M * m
    # blocks[a][b] is (M, M) indexed [j, k]; arrange as V[j, a, k, b] so that reshape(n, n) has row (j, a) and column (k, b).
    V = torch.stack([torch.stack([blocks[a][b] for b in range(m)], dim=-1) for a in range(m)], dim=1)
    H = torch.diag_embed(grid.T.repeat_interleave(m).to(W.dtype)) - V.reshape(n, n)
    E = torch.linalg.eigvalsh(H)
    neg = -E[E < 0]
    numerator = (neg ** gamma).sum() if neg.numel() else torch.zeros((), dtype=torch.float64)
    lam = torch.linalg.eigvalsh(W).clamp(min=0.0)
    denominator = (grid.w[:, None] * lam ** (gamma + 0.5)).sum()
    return numerator, denominator, neg


def ratio(W: torch.Tensor, gamma: float, grid: Grid) -> float:
    num, den, _ = numerator_denominator(W, gamma, grid)
    return float(num / den)


def equality_potential(gamma: float, grid: Grid) -> torch.Tensor:
    r = 1.0 / (gamma - 0.5)
    return ((r + 1) / torch.cosh(r * grid.x) ** 2).reshape(-1, 1, 1).to(torch.complex128)


def dressed(W: torch.Tensor, U: torch.Tensor) -> torch.Tensor:
    """U W U^dagger for a constant unitary U."""
    return U @ W @ U.conj().T


class Blobs(torch.nn.Module):
    """W = B^dagger B with K blobs of Chebyshev-in-tanh polynomials times sech."""

    def __init__(self, m: int, K: int = 2, P: int = 8, seed: int = 0, spread: float = 3.0) -> None:
        super().__init__()
        g = torch.Generator().manual_seed(seed)
        self.m, self.K, self.P = m, K, P
        self.cr = torch.nn.Parameter(0.35 * torch.randn(K, m, m, P + 1, generator=g))
        self.ci = torch.nn.Parameter(0.35 * torch.randn(K, m, m, P + 1, generator=g))
        self.logk = torch.nn.Parameter(math.log(1.5) + 0.5 * torch.randn(K, generator=g))
        self.x0 = torch.nn.Parameter(spread * torch.randn(K, generator=g))

    def B(self, x: torch.Tensor) -> torch.Tensor:
        out = torch.zeros(x.shape[0], self.m, self.m, dtype=torch.complex128)
        for k in range(self.K):
            z = torch.exp(self.logk[k]) * (x - self.x0[k])
            s, t = 1.0 / torch.cosh(z), torch.tanh(z)
            cheb = [torch.ones_like(t), t]
            for _ in range(2, self.P + 1):
                cheb.append(2 * t * cheb[-1] - cheb[-2])
            Tp = torch.stack(cheb[: self.P + 1], dim=1)  # (Q, P+1)
            c = torch.complex(self.cr[k], self.ci[k])
            out = out + s[:, None, None] * torch.einsum("qp,abp->qab", Tp.to(torch.complex128), c)
        return out

    def W(self, x: torch.Tensor) -> torch.Tensor:
        B = self.B(x)
        return B.conj().transpose(1, 2) @ B


def optimise(gamma: float, m: int, grid: Grid, seed: int, K: int = 2, P: int = 8, adam_steps: int = 250, lbfgs_iters: int = 60,
             lr: float = 0.04, init: Blobs | None = None) -> tuple[float, Blobs]:
    model = init if init is not None else Blobs(m, K, P, seed)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    best = (-1.0, None)

    def loss_fn() -> torch.Tensor:
        W = model.W(grid.x)
        num, den, _ = numerator_denominator(W, gamma, grid)
        return -(torch.log(num + 1e-300) - torch.log(den + 1e-300))

    for step in range(adam_steps):
        opt.zero_grad()
        loss = loss_fn()
        if not torch.isfinite(loss):
            break
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
        opt.step()
    lb = torch.optim.LBFGS(model.parameters(), lr=0.5, max_iter=lbfgs_iters, line_search_fn="strong_wolfe")

    def closure() -> torch.Tensor:
        lb.zero_grad()
        loss = loss_fn()
        loss.backward()
        return loss

    try:
        lb.step(closure)
    except Exception:
        pass
    with torch.no_grad():
        r = ratio(model.W(grid.x), gamma, grid)
    return r, model


def verdict(r_lower: float, L1: float, tol: float = 1e-6) -> str:
    """Interval-style verdict in the spirit of the Mensura estimator: r_lower is a rigorous lower bound on the true ratio
    (up to quadrature), so only a clear excess is a violation; anything inside the tolerance band is UNDECIDED, not a pass."""
    excess = r_lower / L1 - 1.0
    if excess > tol:
        return "CANDIDATE_VIOLATION"
    if excess < -tol:
        return "BELOW"
    return "WITHIN_TOLERANCE"
