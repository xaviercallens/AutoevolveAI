#!/usr/bin/env python3
"""H5: lower bounds for the best constant in the dyadic triangular Hilbert estimate.

Upstream (openai/math, "An L3 bound for the dyadic triangular Hilbert form", 2026-10-05,
Theorem 1.1, NOT Lean-formalized) proves, for real F0, F1, F2 on R_+^2,

    sum_{k in S} sum_{I in A_k} |L_I(F0, F1, F2)| <= 40 * prod_v ||F_v||_{L^3},

    L_I = 2^{-k} int_{I0 x I1 x I2} F0(x0,x1) F1(x1,x2) F2(x2,x0) prod_v h_{I_v}(x_v),

with A_k the triples of dyadic intervals of length 2^k whose indices XOR to 0 and h_I the
Haar function. Let C* be the best constant (all finite S). This runner computes the ratio
exactly for inputs constant on dyadic squares of side 2^-N inside [0,1)^2 and maximises it.

Reductions (each exact):
* Dyadic dilation leaves the ratio unchanged, and any compact support sits in some
  [0, 2^j)^2, so restricting to [0,1)^2 loses nothing.
* With inputs constant on 2^-N squares, only scales -N+1 <= k <= 0 see the Haar signs; every
  scale k >= 1 contributes 2^-k |T| with T = int F0 F1 F2 (only the triple (0,0,0) meets the
  support and all three Haar signs are +1 there), and sum_{k>=1} 2^-k = 1.
  Scales k <= -N vanish because h_I integrates to 0 on a constant cell.
So ratio(N) = (|T| + sum_{k=-N+1}^{0} sum_I |L_I|) / prod ||F_v||_3, and any value found is
a valid lower bound for C*.

Maximisation: alternating Hoelder ascent. With the signs s_I = sign(L_I) frozen, the
objective is linear in each F_v; its maximiser on the unit L^3 sphere is
sign(G)|G|^{1/2} (dual exponent 3/2). Updating signs can only increase sum |L_I|, so every
sweep is monotone.

Controls (preregistered, see preregister.py):
* positive: F_v = 1 on [0,1)^2 gives ratio exactly 1 (all Haar terms vanish, T = 1);
  vectorised L_I equals a direct quadruple loop at N = 2 to 1e-12.
* negative: the same instrument on the Haar-free form (h_I replaced by 1_I) must show the
  scale sum growing: ratio = N + 1 at F = 1 (one per scale), so an unbounded form is visible.
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
OUT_DIR = REPO / "results" / "openai_math" / "hypotheses" / "H5"


def haar_signs(block: int, haar: bool) -> np.ndarray:
    if not haar:
        return np.ones(block)
    half = block // 2
    return np.concatenate([np.ones(half), -np.ones(block - half)])


def scale_terms(a: list[np.ndarray], n_res: int, k: int, haar: bool = True) -> np.ndarray:
    """All L_I at scale k (k <= 0) as an (m, m) array indexed by (n0, n1); n2 = n0 ^ n1."""
    size = 2 ** n_res
    w = 1.0 / size
    m = 2 ** (-k)
    b = size // m
    s = haar_signs(b, haar)
    blocks = [x.reshape(m, b, m, b).transpose(0, 2, 1, 3) for x in a]  # [n_row, n_col, b, b]
    n0 = np.arange(m)[:, None]
    n1 = np.arange(m)[None, :]
    n2 = n0 ^ n1
    x0 = blocks[0][n0, n1] * s[:, None] * s[None, :]          # D0 A0 D1
    x1 = blocks[1][n1, n2] * s[None, :]                         # A1 D2
    x2 = blocks[2][n2, n0]                                      # A2
    prod = np.einsum("pqij,pqjk,pqki->pq", x0, x1, x2)
    return (2.0 ** (-k)) * w**3 * prod


def total_term(a: list[np.ndarray], n_res: int) -> float:
    w = 1.0 / 2**n_res
    return float(w**3 * np.einsum("ij,jk,ki->", a[0], a[1], a[2]))


def l3_norm(x: np.ndarray, n_res: int) -> float:
    w = 1.0 / 2**n_res
    return float((w * w * np.sum(np.abs(x) ** 3)) ** (1.0 / 3.0))


def form_sum(a: list[np.ndarray], n_res: int, haar: bool = True) -> float:
    total = abs(total_term(a, n_res))
    for k in range(-n_res + 1, 1):
        total += float(np.abs(scale_terms(a, n_res, k, haar)).sum())
    return total


def ratio(a: list[np.ndarray], n_res: int, haar: bool = True) -> float:
    denom = l3_norm(a[0], n_res) * l3_norm(a[1], n_res) * l3_norm(a[2], n_res)
    return form_sum(a, n_res, haar) / denom if denom > 0 else 0.0


def brute_force_term(a: list[np.ndarray], n_res: int, k: int, i0: int, i1: int) -> float:
    """Direct quadruple loop for one triple: the instrument check for scale_terms."""
    size = 2**n_res
    w = 1.0 / size
    b = size // 2 ** (-k)
    i2 = i0 ^ i1

    def h(cell: int, idx: int) -> float:
        lo = idx * b
        if not lo <= cell < lo + b:
            return 0.0
        return 1.0 if cell < lo + b // 2 else -1.0

    acc = 0.0
    for x0 in range(size):
        for x1 in range(size):
            for x2 in range(size):
                acc += a[0][x0, x1] * a[1][x1, x2] * a[2][x2, x0] * h(x0, i0) * h(x1, i1) * h(x2, i2)
    return (2.0 ** (-k)) * w**3 * acc


def gradient_first(a: list[np.ndarray], n_res: int) -> np.ndarray:
    """d/dA0 of sum_I sign(L_I) L_I + sign(T) T, signs frozen at the current point."""
    size = 2**n_res
    w = 1.0 / size
    grad = np.zeros_like(a[0])
    t = total_term(a, n_res)
    grad += np.sign(t) * w**3 * (a[1] @ a[2]).T
    for k in range(-n_res + 1, 1):
        m = 2 ** (-k)
        b = size // m
        s = haar_signs(b, True)
        terms = scale_terms(a, n_res, k)
        sig = np.sign(terms)
        blocks1 = a[1].reshape(m, b, m, b).transpose(0, 2, 1, 3)
        blocks2 = a[2].reshape(m, b, m, b).transpose(0, 2, 1, 3)
        n0 = np.arange(m)[:, None]
        n1 = np.arange(m)[None, :]
        n2 = n0 ^ n1
        # L = c * tr(D0 X D1 A1 D2 A2), dL/dX = c * (D1 A1 D2 A2 D0)^T
        mm = (s[None, None, :, None] * blocks1[n1, n2] * s[None, None, None, :]) @ (
            blocks2[n2, n0] * s[None, None, None, :]
        )
        g_blocks = (2.0 ** (-k)) * w**3 * sig[:, :, None, None] * np.swapaxes(mm, -1, -2)
        grad += g_blocks.transpose(0, 2, 1, 3).reshape(size, size)
    return grad


def hoelder_step(g: np.ndarray, n_res: int) -> np.ndarray:
    x = np.sign(g) * np.sqrt(np.abs(g))
    nrm = l3_norm(x, n_res)
    return x / nrm if nrm > 0 else x


def ascend(a: list[np.ndarray], n_res: int, sweeps: int) -> tuple[list[np.ndarray], float]:
    a = [x / l3_norm(x, n_res) for x in a]
    best = ratio(a, n_res)
    for _ in range(sweeps):
        for _ in range(3):
            a[0] = hoelder_step(gradient_first(a, n_res), n_res)
            a = [a[1], a[2], a[0]]  # cyclic symmetry: the next variable becomes first
        r = ratio(a, n_res)
        if r <= best * (1 + 1e-10):
            best = max(best, r)
            break
        best = r
    return a, best


@dataclass
class RunResult:
    n_res: int
    restarts: int
    best_ratio: float
    best_seed: int
    elapsed_s: float
    positive_control_const_ratio: float
    positive_control_bruteforce_maxdiff: float
    negative_control_haarfree_ratios: dict[str, float]
    controls_pass: bool
    exceeds_upstream_40: bool


def controls(n_res: int) -> tuple[float, float, dict[str, float], bool]:
    ones = [np.ones((2**n_res, 2**n_res)) for _ in range(3)]
    const_ratio = ratio(ones, n_res)
    rng = np.random.default_rng(0)
    tiny = [rng.standard_normal((4, 4)) for _ in range(3)]
    diffs = []
    for k in (-1, 0):
        terms = scale_terms(tiny, 2, k)
        m = 2 ** (-k)
        for i0 in range(m):
            for i1 in range(m):
                diffs.append(abs(terms[i0, i1] - brute_force_term(tiny, 2, k, i0, i1)))
    maxdiff = max(diffs)
    haar_free = {
        str(n): ratio([np.ones((2**n, 2**n)) for _ in range(3)], n, haar=False) for n in (3, 6)
    }
    ok = (
        abs(const_ratio - 1.0) < 1e-12
        and maxdiff < 1e-12
        and abs(haar_free["3"] - 4.0) < 1e-9
        and abs(haar_free["6"] - 7.0) < 1e-9
    )
    return const_ratio, maxdiff, haar_free, ok


def run(n_res: int, restarts: int, sweeps: int, budget_s: float, seed0: int) -> RunResult:
    t0 = time.time()
    const_ratio, maxdiff, haar_free, ok = controls(n_res)
    best, best_seed = 0.0, -1
    best_a: list[np.ndarray] | None = None
    for r in range(restarts):
        if time.time() - t0 > budget_s:
            break
        rng = np.random.default_rng(seed0 + r)
        a0 = [rng.standard_normal((2**n_res, 2**n_res)) for _ in range(3)]
        a, val = ascend(a0, n_res, sweeps)
        if val > best:
            best, best_seed, best_a = val, seed0 + r, a
    if best_a is not None:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(OUT_DIR / f"best_inputs_N{n_res}.npz", *best_a)
    return RunResult(
        n_res=n_res,
        restarts=restarts,
        best_ratio=best,
        best_seed=best_seed,
        elapsed_s=round(time.time() - t0, 2),
        positive_control_const_ratio=const_ratio,
        positive_control_bruteforce_maxdiff=maxdiff,
        negative_control_haarfree_ratios=haar_free,
        controls_pass=ok,
        exceeds_upstream_40=best > 40.0,
    )


def main() -> int:
    p = argparse.ArgumentParser(description="H5 dyadic triangular Hilbert constant search")
    p.add_argument("--n-res", type=int, nargs="+", default=[3, 4, 5, 6])
    p.add_argument("--restarts", type=int, default=20)
    p.add_argument("--sweeps", type=int, default=200)
    p.add_argument("--budget-s", type=float, default=300.0)
    p.add_argument("--seed0", type=int, default=1000)
    args = p.parse_args()
    results = [asdict(run(n, args.restarts, args.sweeps, args.budget_s, args.seed0)) for n in args.n_res]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "result.json").write_text(json.dumps(results, indent=2) + "\n")
    for r in results:
        print(json.dumps({k: r[k] for k in ("n_res", "best_ratio", "controls_pass", "exceeds_upstream_40", "elapsed_s")}))
    return 0 if all(r["controls_pass"] for r in results) else 3


if __name__ == "__main__":
    raise SystemExit(main())
