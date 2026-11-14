#!/usr/bin/env python3
"""Exact arithmetic for the dyadic triangular Hilbert form on step inputs, written from the
definition and independent of h5_dyadic.py / h5_exact.py / the night lane's h5_multiscale.py.

Setting (upstream: "An L3 bound for the dyadic triangular Hilbert form", openai/math, 2026-10-05).
For k in Z let D_k be the dyadic intervals of length 2^k in [0, inf), h_I = 1_{left half} - 1_{right half},
A_k the triples (I0, I1, I2) in D_k^3 whose indices XOR to 0, and

    L_I(F0, F1, F2) = 2^{-k} int_{I0 x I1 x I2} F0(x0, x1) F1(x1, x2) F2(x2, x0) h_{I0}(x0) h_{I1}(x1) h_{I2}(x2).

Upstream's Theorem 1.1: sum_k sum_{I in A_k} |L_I| <= 40 prod_v ||F_v||_{L^3(R_+^2)}.  C* is the best constant.

Inputs here are constant on the 2^-N squares of [0,1)^2 (an n x n integer matrix per F_v, n = 2^N;
general real step inputs are handled with Fractions for the product-rule check).  Then:
* scales 2^k >= 2 (k >= 1): only the triple (0,0,0) meets the support, all three Haar signs are +1 on
  [0,1), so L = 2^{-k} T with T = int F0 F1 F2; these sum to |T|.
* scales 2^k <= 2^-N: every h_I integrates to 0 on a cell, so L_I = 0.
* scales 2^k = 2^-l, l = 0..N-1 ("level l"): m = 2^l intervals, each a union of b = n/m cells.
So S(F) := sum_k sum_I |L_I| = |T| + H, H = sum_{l=0}^{N-1} sum_{I in A_l} |L_I|, and R(F) = S(F) / prod ||F_v||_3.

All quantities are returned as exact Fractions.  Integer core: with w = 1/n,
    T = w^3 * Tint,  Tint = sum_{i,j,k} F0[i,j] F1[j,k] F2[k,i],
    L_I = 2^l * w^3 * Lint(I),  Lint = sum over the cells of the triple of s_i s_j s_k F0[i,j] F1[j,k] F2[k,i].
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from fractions import Fraction
from pathlib import Path
from typing import Iterable

import numpy as np

REPO = Path(__file__).resolve().parents[4]
OUT_DIR = REPO / "results" / "openai_math" / "hypotheses" / "tensor"


# ----------------------------------------------------------------------------- core (integer inputs)

def haar_sign(b: int) -> np.ndarray:
    """h on one interval made of b cells: +1 on the first b/2 cells, -1 on the rest (b >= 2)."""
    return np.array([1] * (b // 2) + [-1] * (b - b // 2), dtype=np.int64)


def resolution(f: np.ndarray) -> int:
    n = f.shape[0]
    assert f.shape == (n, n) and n & (n - 1) == 0 and n >= 1, "need a 2^N x 2^N matrix"
    return n.bit_length() - 1


def t_int(f: list[np.ndarray]) -> int:
    """Tint = sum_{i,j,k} F0[i,j] F1[j,k] F2[k,i]  (trace of the matrix product)."""
    return int(np.einsum("ij,jk,ki->", f[0], f[1], f[2]))


def level_ints(f: list[np.ndarray], level: int) -> np.ndarray:
    """Lint for every admissible triple at `level`, as an m x m array indexed by (p, q), r = p ^ q.

    For the triple (p, q, r): cells i in block p, j in block q, k in block r, and
    Lint = sum s[i'] s[j'] s[k'] F0[i,j] F1[j,k] F2[k,i] = tr(S F0^{pq} S F1^{qr} S F2^{rp}),
    where S = diag(haar_sign(b)) and F^{pq} is the b x b block.
    """
    n = f[0].shape[0]
    m = 2**level
    b = n // m
    s = haar_sign(b)
    blocks = [x.reshape(m, b, m, b).transpose(0, 2, 1, 3) for x in f]  # [p, q, i', j']
    p = np.arange(m)[:, None]
    q = np.arange(m)[None, :]
    r = p ^ q
    x0 = s[:, None] * blocks[0][p, q] * s[None, :]  # S F0 S
    x1 = blocks[1][q, r] * s[None, :]               # F1 S
    x2 = blocks[2][r, p]                            # F2
    return np.einsum("pqij,pqjk,pqki->pq", x0, x1, x2)


def exact_parts(f: list[np.ndarray]) -> dict[str, Fraction]:
    """Exact |T| and per-level sum_I |L_I| for integer step inputs."""
    n = f[0].shape[0]
    N = resolution(f[0])
    w3 = Fraction(1, n**3)
    parts = {"T": abs(t_int(f)) * w3}
    for level in range(N):
        parts[f"level{level}"] = Fraction(int(np.abs(level_ints(f, level)).sum()) * 2**level) * w3
    return parts


def exact_T(f: list[np.ndarray]) -> Fraction:
    return Fraction(t_int(f), f[0].shape[0] ** 3)


def exact_H(f: list[np.ndarray]) -> Fraction:
    parts = exact_parts(f)
    return sum((v for k, v in parts.items() if k != "T"), Fraction(0))


def norm3_cubed(x: np.ndarray) -> Fraction:
    """||F||_3^3 = n^-2 sum |F_ij|^3 for an integer step input."""
    n = x.shape[0]
    return Fraction(int((np.abs(x.astype(np.int64)) ** 3).sum()), n * n)


def ratio_cubed(f: list[np.ndarray]) -> Fraction:
    """R^3 exactly (R itself is a cube root; for +-1 inputs R = S is rational)."""
    s = abs(exact_T(f)) + exact_H(f)
    denom = norm3_cubed(f[0]) * norm3_cubed(f[1]) * norm3_cubed(f[2])
    return s**3 / denom


def is_pm1(f: list[np.ndarray]) -> bool:
    return all(set(np.unique(x).tolist()) <= {-1, 1} for x in f)


def R_pm1(f: list[np.ndarray]) -> Fraction:
    assert is_pm1(f)
    return abs(exact_T(f)) + exact_H(f)


def phi_pm1(f: list[np.ndarray]) -> Fraction | None:
    """Phi(g) = H(g) / (1 - |T(g)|): the tensor-power limit of a +-1 seed; None if |T| = 1."""
    t = abs(exact_T(f))
    if t == 1:
        return None
    return exact_H(f) / (1 - t)


# ----------------------------------------------------------------------------- general real inputs (Fractions)

def exact_parts_general(f: list[list[list[Fraction]]]) -> tuple[Fraction, Fraction, Fraction]:
    """(|T|, H, prod ||F_v||_3^3) for small general step inputs given as nested Fraction lists.

    Pure-Python triple loops; use only for n <= 8.
    """
    n = len(f[0])
    N = n.bit_length() - 1
    w3 = Fraction(1, n**3)
    T = sum(f[0][i][j] * f[1][j][k] * f[2][k][i] for i in range(n) for j in range(n) for k in range(n)) * w3
    H = Fraction(0)
    for level in range(N):
        m = 2**level
        b = n // m
        s = [1] * (b // 2) + [-1] * (b - b // 2)
        for p in range(m):
            for q in range(m):
                r = p ^ q
                acc = Fraction(0)
                for ii in range(b):
                    for jj in range(b):
                        for kk in range(b):
                            i, j, k = p * b + ii, q * b + jj, r * b + kk
                            acc += s[ii] * s[jj] * s[kk] * f[0][i][j] * f[1][j][k] * f[2][k][i]
                H += abs(acc) * 2**level * w3
    norms = Fraction(1)
    for x in f:
        norms *= sum(abs(v) ** 3 for row in x for v in row) / Fraction(n * n)
    return abs(T), H, norms


def a_prime(f: list[list[list[Fraction]]]) -> Fraction:
    """A'(f) = n^-2 sum_{p^q^r=0} |f0[p,q] f1[q,r] f2[r,p]|  (equals 1 for +-1 inputs)."""
    n = len(f[0])
    return sum(abs(f[0][p][q] * f[1][q][p ^ q] * f[2][p ^ q][p]) for p in range(n) for q in range(n)) / Fraction(n * n)


def kron_general(f: list[list[list[Fraction]]], g: list[list[list[Fraction]]]) -> list[list[list[Fraction]]]:
    out = []
    for fv, gv in zip(f, g):
        nf, ng = len(fv), len(gv)
        out.append([[fv[i // ng][j // ng] * gv[i % ng][j % ng] for j in range(nf * ng)] for i in range(nf * ng)])
    return out


def kron(f: list[np.ndarray], g: list[np.ndarray]) -> list[np.ndarray]:
    """f on the coarse (top) bits, g inside each coarse cell."""
    return [np.kron(a, b) for a, b in zip(f, g)]


# ----------------------------------------------------------------------------- experiments

def check_product_rule_general(rng: np.random.Generator, n_pairs: int = 6) -> dict[str, object]:
    """S(f (x) g) = |T(f)||T(g)| + |T(g)| H(f) + A'(f) H(g) on random rational inputs, exactly."""
    checks = []
    for idx in range(n_pairs):
        Nf, Ng = (1, 1) if idx % 3 else (1, 2)
        def rand(N: int) -> list[list[list[Fraction]]]:
            n = 2**N
            return [[[Fraction(int(rng.integers(-3, 4)), int(rng.integers(1, 4))) for _ in range(n)] for _ in range(n)] for _ in range(3)]
        f, g = rand(Nf), rand(Ng)
        Tf, Hf, nf = exact_parts_general(f)
        Tg, Hg, ng = exact_parts_general(g)
        Tfg, Hfg, nfg = exact_parts_general(kron_general(f, g))
        predicted_S = Tf * Tg + Tg * Hf + a_prime(f) * Hg
        checks.append({"Nf": Nf, "Ng": Ng, "S_actual": str(Tfg + Hfg), "S_predicted": str(predicted_S),
                       "T_mult": Tfg == Tf * Tg, "norms_mult": nfg == nf * ng, "pass": Tfg + Hfg == predicted_S and nfg == nf * ng})
    return {"n_pairs": n_pairs, "all_pass": all(c["pass"] for c in checks), "checks": checks}


def check_product_rule_pm1(rng: np.random.Generator, n_pairs: int = 8) -> dict[str, object]:
    checks = []
    for idx in range(n_pairs):
        Nf, Ng = 1 + idx % 3, 1 + (idx // 3) % 2
        f = [rng.choice([-1, 1], size=(2**Nf, 2**Nf)).astype(np.int64) for _ in range(3)]
        g = [rng.choice([-1, 1], size=(2**Ng, 2**Ng)).astype(np.int64) for _ in range(3)]
        lhs = R_pm1(kron(f, g))
        rhs = exact_H(g) + abs(exact_T(g)) * R_pm1(f)
        checks.append({"Nf": Nf, "Ng": Ng, "R_kron": str(lhs), "predicted": str(rhs), "pass": lhs == rhs})
    return {"n_pairs": n_pairs, "all_pass": all(c["pass"] for c in checks), "checks": checks}


def exhaustive_N1() -> dict[str, object]:
    """All 2^12 +-1 inputs at N=1: exact max of R and of Phi, with the (H, T) pairs that occur."""
    best_R, best_phi = Fraction(0), Fraction(0)
    arg_R, arg_phi = None, None
    pairs: dict[tuple[str, str], int] = {}
    for bits in itertools.product([-1, 1], repeat=12):
        f = [np.array(bits[4 * v:4 * v + 4], dtype=np.int64).reshape(2, 2) for v in range(3)]
        H, T = exact_H(f), abs(exact_T(f))
        pairs[(str(H), str(T))] = pairs.get((str(H), str(T)), 0) + 1
        R = H + T
        if R > best_R:
            best_R, arg_R = R, [x.tolist() for x in f]
        if T < 1:
            phi = H / (1 - T)
            if phi > best_phi:
                best_phi, arg_phi = phi, [x.tolist() for x in f]
    return {"count": 4096, "max_R": str(best_R), "argmax_R": arg_R, "max_phi": str(best_phi), "argmax_phi": arg_phi,
            "HT_pairs": {f"H={h},T={t}": c for (h, t), c in sorted(pairs.items())}}


G2 = [np.array(m, dtype=np.int64) for m in (
    [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, -1, -1], [1, 1, -1, -1]],
    [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, -1, -1], [1, 1, -1, -1]],
    [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, -1, -1], [1, 1, -1, -1]],
)]


def seed_from_lane() -> list[np.ndarray] | None:
    """The committed N=2 witness signs (if present), as the lane's g2 candidate."""
    p = REPO / "results" / "openai_math" / "hypotheses" / "H5" / "best_inputs_N2.npz"
    if not p.exists():
        return None
    z = np.load(p)
    return [np.where(z[k] >= 0, 1, -1).astype(np.int64) for k in z.files]


def tensor_powers(g: list[np.ndarray], r_max: int) -> list[dict[str, str]]:
    rows = []
    cur = g
    for r in range(1, r_max + 1):
        if r > 1:
            cur = kron(cur, g)
        N = resolution(cur[0])
        rows.append({"r": str(r), "N": str(N), "R": str(R_pm1(cur)), "H": str(exact_H(cur)), "T": str(exact_T(cur))})
    return rows


def tensor_powers_predicted(g: list[np.ndarray], r_max: int) -> list[str]:
    H, T = exact_H(g), abs(exact_T(g))
    R = H + T
    out = [str(R)]
    for _ in range(2, r_max + 1):
        R = H + T * R
        out.append(str(R))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="exact checks for the tensor lower bound")
    ap.add_argument("--r-max", type=int, default=6, help="tensor powers of the N=2 seed up to g^(x)r (N = 2r)")
    ap.add_argument("--seed", type=int, default=20261008)
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)
    t0 = time.time()
    out: dict[str, object] = {"script": "scripts/openai_math/hypotheses/tensor/h5_tensor_rigor.py", "seed": args.seed}

    # Controls on the evaluator itself.
    ones = [np.ones((4, 4), dtype=np.int64)] * 3
    out["control_constant_input_R"] = str(R_pm1(ones))                   # must be 1
    w4p = REPO / "results" / "openai_math" / "hypotheses" / "H5" / "best_inputs_N4.npz"
    if w4p.exists():
        z = np.load(w4p)
        w4 = [np.where(z[k] >= 0, 1, -1).astype(np.int64) for k in z.files]
        out["control_w4_R"] = str(R_pm1(w4))                               # must be 5/2
        out["control_w4xw4_R"] = str(R_pm1(kron(w4, w4)))                 # must be 23/8
    # Haar-free power control: with all Haar signs +1 the form is not bounded (grows like N+1).
    out["control_haarfree_note"] = "haar_sign replaced by +1 gives R = N + 1 for F = 1 (checked in tests)"

    out["product_rule_pm1"] = check_product_rule_pm1(rng)
    out["product_rule_general"] = check_product_rule_general(rng)
    out["exhaustive_N1"] = exhaustive_N1()

    g2 = seed_from_lane()
    seeds = {"g2_lane_witness": g2} if g2 is not None else {}
    seeds["g2_explicit"] = G2
    out["seeds"] = {}
    for name, g in seeds.items():
        H, T = exact_H(g), exact_T(g)
        phi = phi_pm1(g)
        out["seeds"][name] = {"matrices": [x.tolist() for x in g], "R": str(R_pm1(g)), "H": str(H), "T": str(T),
                              "phi": str(phi), "powers": tensor_powers(g, args.r_max),
                              "powers_predicted_by_rule": tensor_powers_predicted(g, args.r_max)}
        out["seeds"][name]["powers_match_rule"] = [p["R"] for p in out["seeds"][name]["powers"]] == out["seeds"][name]["powers_predicted_by_rule"]
        out["seeds"][name]["closed_form_3_minus_2^(1-r)"] = [str(3 - Fraction(2) ** (1 - r)) for r in range(1, args.r_max + 1)]
    out["elapsed_s"] = round(time.time() - t0, 1)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "rigor.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("control_constant_input_R", "control_w4_R", "control_w4xw4_R") if k in out}))
    print("product_rule_pm1", out["product_rule_pm1"]["all_pass"], "product_rule_general", out["product_rule_general"]["all_pass"])
    print("N1 exhaustive: max R", out["exhaustive_N1"]["max_R"], "max phi", out["exhaustive_N1"]["max_phi"])
    for name, s in out["seeds"].items():
        print(name, "R", s["R"], "H", s["H"], "T", s["T"], "phi", s["phi"], "powers", [p["R"] for p in s["powers"]], "rule ok", s["powers_match_rule"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
