#!/usr/bin/env python3
"""Night lane H5 (2026-10-07): try to beat C* = 5/2 for the dyadic triangular Hilbert form.

Hypothesis H5' (preregistered in results/openai_math/hypotheses/preregistration.json): the best
constant C* in  sum_k sum_{I in A_k} |L_I| <= C* prod_v ||F_v||_3  equals 5/2.
Decision rule: REFUTED if any certified ratio > 5/2 + 1e-9.

Definitions and the reduction to finite matrices are those of ../h5_dyadic.py (imported here,
read-only; only its pure functions are called, never its run()/main(), which write elsewhere).

What this file adds
* An exact integer certifier for ANY integer-valued input (not only +-1): with integer cells
  q_v on the 2^-N grid, ratio = S / (size * P^(1/3)), S = |T_int| + sum_k m_k sum_I |int_I|,
  P = prod_v sum |q_v|^3, so  ratio > c  <=>  S^3 den^3 > num^3 P size^3  for c = num/den,
  decided in Python integers. A real-valued candidate is quantized to integers first; the
  quantized array is itself a valid input, so a certified quantized ratio is a rigorous bound.
* Initialisations: Kronecker lifts of the N=4 witness with Walsh (XOR-character) blocks in
  either order, Walsh x Walsh tensors, multi-scale random sign products, multi-scale Gaussian
  sums, continuation N -> N+1 from committed witnesses, plain Gaussian.
* Exhaustive +-1 search at N=1 and N=2: with F0, F1 fixed every term is linear in F2, so
  max_{F2 in {+-1}} sum_t |<c_t, F2>| = max_{s in {+-1}^t, s_0=+1} || sum_t s_t c_t ||_1.
* A per-scale / per-triple decomposition and 2D Walsh spectrum of a witness ("explain").
* A frozen campaign table of chunks; every chunk runs the controls, writes its own JSON,
  records the code sha256, and is skipped on rerun if its JSON exists.

Usage: python3 h5_multiscale.py {controls|chunk ID|list|explain NPZ|summary}
"""

from __future__ import annotations

import os

for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_var] = "1"

import argparse  # noqa: E402
import hashlib  # noqa: E402
import importlib.util  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from fractions import Fraction  # noqa: E402
from pathlib import Path  # noqa: E402
from types import ModuleType  # noqa: E402
from typing import Any  # noqa: E402

import numpy as np  # noqa: E402

REPO = Path(__file__).resolve().parents[4]
HYP = REPO / "scripts" / "openai_math" / "hypotheses"
LANE = REPO / "results" / "openai_math" / "hypotheses" / "night_2026-10-07" / "H5"
CHUNK_DIR = LANE / "chunks"
WITNESS_DIR = REPO / "results" / "openai_math" / "hypotheses" / "H5"
FIVE_HALVES = Fraction(5, 2)
THRESHOLD = FIVE_HALVES + Fraction(1, 10**9)
N8_SWEEP_LIMIT_S = 8.0
CHUNK_BUDGET_S = 420.0
SEED_BASE = 20261007_000
N2_STEP = 1024
HP_SCALE_BITS = 53


def _load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


h5d = _load("h5_dyadic_night", HYP / "h5_dyadic.py")
h5x = _load("h5_exact_night", HYP / "h5_exact.py")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code_hashes() -> dict[str, str]:
    return {
        "h5_multiscale.py": sha256_file(Path(__file__).resolve()),
        "h5_dyadic.py": sha256_file(HYP / "h5_dyadic.py"),
        "h5_exact.py": sha256_file(HYP / "h5_exact.py"),
    }


def input_hashes() -> dict[str, str]:
    return {f"best_inputs_N{n}.npz": sha256_file(WITNESS_DIR / f"best_inputs_N{n}.npz") for n in (4, 5, 6, 7)}


# ----------------------------------------------------------------------------- exact integers


def _signs(b: int, haar: bool) -> np.ndarray:
    if not haar:
        return np.ones(b, dtype=np.int64)
    return np.concatenate([np.ones(b // 2, dtype=np.int64), -np.ones(b - b // 2, dtype=np.int64)])


def triple_ints(q: list[np.ndarray], haar: bool = True) -> dict[str, np.ndarray]:
    """Signed integer value of T ("T", shape (1,1)) and of every triple at each scale k (shape (m,m))."""
    a = [np.asarray(x, dtype=np.int64) for x in q]
    size = a[0].shape[0]
    n_res = size.bit_length() - 1
    if 2**n_res != size or any(x.shape != (size, size) for x in a):
        raise ValueError("inputs must be square of side 2^N")
    peak = max(int(np.abs(x).max()) for x in a)
    if peak**3 * size**3 >= 2**62:
        raise OverflowError(f"int64 bound exceeded: max|q|={peak}, size={size}")
    out: dict[str, np.ndarray] = {"T": np.array([[int(np.einsum("ij,jk,ki->", a[0], a[1], a[2]))]], dtype=np.int64)}
    for k in range(-n_res + 1, 1):
        m = 2 ** (-k)
        b = size // m
        s = _signs(b, haar)
        blocks = [x.reshape(m, b, m, b).transpose(0, 2, 1, 3) for x in a]
        n0 = np.arange(m)[:, None]
        n1 = np.arange(m)[None, :]
        n2 = n0 ^ n1
        x0 = blocks[0][n0, n1] * s[:, None] * s[None, :]
        x1 = blocks[1][n1, n2] * s[None, :]
        x2 = blocks[2][n2, n0]
        out[str(k)] = np.einsum("pqij,pqjk,pqki->pq", x0, x1, x2)
    return out


def _weight(key: str) -> int:
    return 1 if key == "T" else 2 ** (-int(key))


def int_parts(q: list[np.ndarray], haar: bool = True) -> tuple[int, dict[str, int]]:
    """S = |T_int| + sum_k m_k sum_I |int_I| for integer inputs (exact, overflow-guarded)."""
    parts = {key: _weight(key) * int(np.abs(v).sum()) for key, v in triple_ints(q, haar).items()}
    return sum(parts.values()), parts


def limb_bits(n_res: int) -> int:
    """Largest limb width whose cubes stay inside the int64 guard of triple_ints."""
    return (62 - 3 * n_res) // 3 - 1


def big_parts(q: list[np.ndarray], haar: bool = True) -> tuple[int, dict[str, int]]:
    """Exact S for arbitrary Python-int inputs (object arrays): sign-magnitude limb split, int64 per
    limb combination, recombined per triple in Python ints before the absolute value."""
    size = q[0].shape[0]
    n_res = size.bit_length() - 1
    bits = limb_bits(n_res)
    mask = (1 << bits) - 1
    peak = max(abs(int(v)) for x in q for v in np.asarray(x, dtype=object).ravel())
    limbs = max(1, -(-max(peak.bit_length(), 1) // bits))
    split: list[list[np.ndarray]] = []
    for x in q:
        xo = np.asarray(x, dtype=object)
        sign = np.where(xo < 0, -1, 1).astype(np.int64)
        mag = np.abs(xo)
        split.append([sign * np.array((mag >> (l * bits)) & mask, dtype=np.int64) for l in range(limbs)])
    total: dict[str, np.ndarray] = {}
    for l0, l1, l2 in itertools.product(range(limbs), repeat=3):
        shift = 1 << (bits * (l0 + l1 + l2))
        for key, v in triple_ints([split[0][l0], split[1][l1], split[2][l2]], haar).items():
            contrib = v.astype(object) * shift
            total[key] = total[key] + contrib if key in total else contrib
    parts = {key: _weight(key) * int(sum(abs(int(t)) for t in v.ravel())) for key, v in total.items()}
    return sum(parts.values()), parts


def certify_big(q: list[np.ndarray], threshold: Fraction = THRESHOLD, haar: bool = True) -> dict[str, Any]:
    """certify() for arbitrary-size Python-int inputs (exact; used for the high-precision fallback)."""
    size = q[0].shape[0]
    s_int, parts = big_parts(q, haar)
    p_int = 1
    for x in q:
        p_int *= int(sum(abs(int(v)) ** 3 for v in np.asarray(x, dtype=object).ravel()))
    if p_int == 0:
        return {"exceeds": False, "ratio_float": 0.0, "ratio_cubed": "0"}
    cubed = Fraction(s_int**3, p_int * size**3)
    return {"exceeds": bool(cubed > threshold**3), "threshold": str(threshold), "ratio_float": float(cubed) ** (1.0 / 3.0), "ratio_cubed": str(cubed)}


def quantize_hp(a: list[np.ndarray], scale_bits: int = HP_SCALE_BITS) -> list[np.ndarray]:
    """x / max|x| * 2^scale_bits rounded to Python ints: exact float scaling, no precision lost below 2^-53."""
    out = []
    for x in a:
        peak = float(np.abs(x).max())
        y = np.rint(np.ldexp(np.asarray(x, dtype=float) / peak, scale_bits)) if peak > 0 else np.zeros_like(x)
        out.append(np.array([[int(v) for v in row] for row in y], dtype=object))
    return out


def certify(q: list[np.ndarray], threshold: Fraction = THRESHOLD, haar: bool = True) -> dict[str, Any]:
    """Exact decision ratio(q) > threshold for integer q, plus the exact ratio^3."""
    a = [np.asarray(x, dtype=np.int64) for x in q]
    size = a[0].shape[0]
    s_int, parts = int_parts(a, haar)
    p_int = 1
    for x in a:
        p_int *= int(np.sum(np.abs(x) ** 3))
    if p_int == 0:
        return {"exceeds": False, "ratio_float": 0.0, "ratio_cubed": "0", "parts": parts}
    cubed = Fraction(s_int**3, p_int * size**3)
    exceeds = cubed > threshold**3
    ratio_float = float(s_int) / size / float(p_int) ** (1.0 / 3.0)
    return {
        "exceeds": bool(exceeds),
        "threshold": str(threshold),
        "ratio_float": ratio_float,
        "ratio_cubed": str(cubed),
        "S_int": s_int,
        "parts_int": {k: int(v) for k, v in parts.items()},
    }


def quantize(a: list[np.ndarray], bits: int | None = None) -> list[np.ndarray]:
    """Round each input to integers with max |q| = 2^bits - 1 (largest bits safe for int64)."""
    size = a[0].shape[0]
    n_res = size.bit_length() - 1
    if bits is None:
        bits = (62 - 3 * n_res) // 3 - 1
    out = []
    for x in a:
        peak = float(np.abs(x).max())
        scale = (2**bits - 1) / peak if peak > 0 else 0.0
        out.append(np.rint(np.asarray(x) * scale).astype(np.int64))
    return out


def certify_candidate(a: list[np.ndarray], haar: bool = True) -> dict[str, Any]:
    """Certify a real-valued candidate: quantized (full precision) and sign-rounded versions."""
    quant = certify(quantize(a), haar=haar)
    signs = [np.where(x >= 0, 1, -1).astype(np.int64) for x in a]
    sign_cert = certify(signs, haar=haar)
    out: dict[str, Any] = {"quantized": quant, "sign": sign_cert}
    if haar:
        exact, parts = h5x.exact_ratio(signs)
        out["sign_h5_exact"] = {"exact_ratio": str(exact), "parts": parts}
        out["sign_agrees_with_h5_exact"] = Fraction(sign_cert["ratio_cubed"]) == exact**3
    n_res = a[0].shape[0].bit_length() - 1
    hp_exceeds = False
    if h5d.ratio(a, n_res, haar) > float(FIVE_HALVES) - 1e-6:
        hp = certify_big(quantize_hp(a), haar=haar)
        out["high_precision"] = hp
        hp_exceeds = bool(hp["exceeds"])
    out["certified_exceeds"] = bool(quant["exceeds"] or sign_cert["exceeds"] or hp_exceeds)
    return out


# ----------------------------------------------------------------------------- float ascent


def gradient(a: list[np.ndarray], n_res: int, haar: bool = True) -> np.ndarray:
    """d/dA0 of sign(T) T + sum_I sign(L_I) L_I with signs frozen (Haar or Haar-free form)."""
    size = 2**n_res
    w = 1.0 / size
    t = h5d.total_term(a, n_res)
    grad = np.sign(t) * w**3 * (a[1] @ a[2]).T
    for k in range(-n_res + 1, 1):
        m = 2 ** (-k)
        b = size // m
        s = h5d.haar_signs(b, haar)
        sig = np.sign(h5d.scale_terms(a, n_res, k, haar))
        blocks1 = a[1].reshape(m, b, m, b).transpose(0, 2, 1, 3)
        blocks2 = a[2].reshape(m, b, m, b).transpose(0, 2, 1, 3)
        n0 = np.arange(m)[:, None]
        n1 = np.arange(m)[None, :]
        n2 = n0 ^ n1
        mm = (s[None, None, :, None] * blocks1[n1, n2] * s[None, None, None, :]) @ (
            blocks2[n2, n0] * s[None, None, None, :]
        )
        g_blocks = (2.0 ** (-k)) * w**3 * sig[:, :, None, None] * np.swapaxes(mm, -1, -2)
        grad = grad + g_blocks.transpose(0, 2, 1, 3).reshape(size, size)
    return grad


def ascend_timed(
    a: list[np.ndarray], n_res: int, sweeps: int, deadline: float, haar: bool = True
) -> tuple[list[np.ndarray], float, int, bool]:
    """Monotone alternating Hoelder ascent; stops at convergence, `sweeps`, or `deadline`."""
    a = [x / h5d.l3_norm(x, n_res) for x in a]
    best = h5d.ratio(a, n_res, haar)
    done = 0
    converged = False
    for _ in range(sweeps):
        if time.time() > deadline:
            break
        for _ in range(3):
            a[0] = h5d.hoelder_step(gradient(a, n_res, haar), n_res)
            a = [a[1], a[2], a[0]]
        done += 1
        r = h5d.ratio(a, n_res, haar)
        if r <= best * (1 + 1e-10):
            best = max(best, r)
            converged = True
            break
        best = r
    return a, best, done, converged


# ----------------------------------------------------------------------------- initialisations


def walsh_matrix(n: int) -> np.ndarray:
    """Sylvester-Hadamard: H[i, j] = (-1)^popcount(i & j), order 2^n."""
    idx = np.arange(2**n)
    pc = np.vectorize(lambda v: bin(int(v)).count("1"))(idx[:, None] & idx[None, :])
    return np.where(pc % 2 == 0, 1, -1).astype(np.int64)


def walsh_block(n: int, r: int, c: int) -> np.ndarray:
    h = walsh_matrix(n)
    return np.outer(h[r], h[c])


def witness_signs(n_res: int) -> list[np.ndarray]:
    z = np.load(WITNESS_DIR / f"best_inputs_N{n_res}.npz")
    return [np.where(z[f] >= 0, 1, -1).astype(np.int64) for f in z.files]


def witness_float(n_res: int) -> list[np.ndarray]:
    z = np.load(WITNESS_DIR / f"best_inputs_N{n_res}.npz")
    return [np.asarray(z[f], dtype=float) for f in z.files]


def kron_lift(coarse: list[np.ndarray], fine: list[np.ndarray]) -> list[np.ndarray]:
    """F_v = coarse_v (x) fine_v: coarse_v on the top bits, fine_v inside each cell."""
    return [np.kron(c, f) for c, f in zip(coarse, fine)]


def upsample(x: np.ndarray, n_res: int) -> np.ndarray:
    rep = 2**n_res // x.shape[0]
    return np.kron(x, np.ones((rep, rep), dtype=x.dtype))


def multiscale_signs(rng: np.random.Generator, n_res: int) -> list[np.ndarray]:
    """F_v = prod over a random nonempty subset of levels j of an upsampled random +-1 matrix."""
    out = []
    for _ in range(3):
        levels = [j for j in range(1, n_res + 1) if rng.random() < 0.5] or [n_res]
        f = np.ones((2**n_res, 2**n_res), dtype=np.int64)
        for j in levels:
            f = f * upsample(rng.choice(np.array([-1, 1], dtype=np.int64), size=(2**j, 2**j)), n_res)
        out.append(f)
    return out


def multiscale_gauss(rng: np.random.Generator, n_res: int, decay: float) -> list[np.ndarray]:
    out = []
    for _ in range(3):
        f = np.zeros((2**n_res, 2**n_res))
        for j in range(n_res + 1):
            f += decay**j * upsample(rng.standard_normal((2**j, 2**j)), n_res)
        out.append(f)
    return out


def walsh_choice(rng: np.random.Generator, d: int, coupled: bool) -> tuple[tuple[int, int], ...]:
    """Walsh indices (r_v, c_v) for the three blocks; coupled = shared characters on shared variables."""
    top = 2**d
    if coupled:
        u, v, t = (int(x) for x in rng.integers(top, size=3))
        return ((u, v), (v, t), (t, u))
    return tuple((int(rng.integers(top)), int(rng.integers(top))) for _ in range(3))


def walsh_lift(w: list[np.ndarray], d: int, idx: tuple[tuple[int, int], ...], order: str) -> list[np.ndarray]:
    blocks = [walsh_block(d, r, c) for r, c in idx]
    return kron_lift(w, blocks) if order == "witness_coarse" else kron_lift(blocks, w)


# ----------------------------------------------------------------------------- exhaustive +-1


def term_vectors(n_res: int) -> list[tuple[int, np.ndarray, np.ndarray, np.ndarray]]:
    """(weight, g0, g1, g2) for T and every admissible triple; int_t = sum q0 q1 q2 g0 g1 g2."""
    size = 2**n_res
    terms = [(1, np.ones(size, dtype=np.int64), np.ones(size, dtype=np.int64), np.ones(size, dtype=np.int64))]
    for k in range(-n_res + 1, 1):
        m = 2 ** (-k)
        b = size // m

        def g(n: int) -> np.ndarray:
            v = np.zeros(size, dtype=np.int64)
            v[n * b : n * b + b // 2] = 1
            v[n * b + b // 2 : (n + 1) * b] = -1
            return v

        for n0 in range(m):
            for n1 in range(m):
                terms.append((m, g(n0), g(n1), g(n0 ^ n1)))
    return terms


def coefficient_vectors(q0: np.ndarray, q1_batch: np.ndarray, n_res: int) -> np.ndarray:
    """c[b, t, k*size + i]: int_t = sum_{k,i} c[b,t,k,i] q2[k,i] (exact int64)."""
    size = 2**n_res
    q1f = q1_batch.astype(np.float64)
    cs = []
    for wt, g0, g1, g2 in term_vectors(n_res):
        a = (q0 * g1[None, :]).astype(np.float64)
        prod = np.matmul(a[None, :, :], q1f)  # [b, i, k]; small integers, exact in float64
        c = wt * g0[None, :, None] * g2[None, None, :] * prod  # [b, i, k]
        cs.append(np.swapaxes(c, 1, 2).reshape(q1_batch.shape[0], size * size))
    out = np.rint(np.stack(cs, axis=1)).astype(np.int64)
    return out


def sign_patterns(t: int) -> np.ndarray:
    rows = [(1,) + p for p in itertools.product((1, -1), repeat=t - 1)]
    return np.array(rows, dtype=np.int64)


def all_sign_matrices(n_res: int, fix_first: bool) -> np.ndarray:
    size = 2**n_res
    cells = size * size
    count = 2 ** (cells - 1) if fix_first else 2**cells
    idx = np.arange(count, dtype=np.int64)
    bits = (idx[:, None] >> np.arange(cells, dtype=np.int64)[None, :]) & 1
    mats = (1 - 2 * bits).reshape(count, size, size)
    if fix_first:
        mats = np.concatenate([np.ones((count, 1), dtype=np.int64), mats.reshape(count, cells)[:, : cells - 1]], axis=1)
        mats = mats.reshape(count, size, size)
    return mats


def sign_matrix_from_index(idx: int, n_res: int, fix_first: bool) -> np.ndarray:
    size = 2**n_res
    cells = size * size
    if fix_first:
        bits = [0] + [(idx >> j) & 1 for j in range(cells - 1)]
    else:
        bits = [(idx >> j) & 1 for j in range(cells)]
    return (1 - 2 * np.array(bits, dtype=np.int64)).reshape(size, size)


def best_f2_for_pairs(q0: np.ndarray, q1_batch: np.ndarray, n_res: int, q1f: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """For each q1 in the batch: max over q2 in {+-1} of S, and the argmax pattern index."""
    size = 2**n_res
    cells = size * size
    basis = np.eye(cells, dtype=np.int64).reshape(cells, size, size)
    kmap = coefficient_vectors(q0, basis, n_res)  # [cells(q1 entry), t, cells(q2 entry)], linear in q1
    pats = sign_patterns(kmap.shape[1])  # [p, t]
    kp = np.einsum("pt,ytx->ypx", pats, kmap).reshape(cells, -1)  # [q1 entry, p*x]
    if int(np.abs(kp).sum(axis=0).max()) * cells >= 2**24:
        raise OverflowError("float32 exactness bound exceeded")
    if q1f is None:
        q1f = q1_batch.reshape(q1_batch.shape[0], cells).astype(np.float32)
    lin = q1f @ kp.astype(np.float32)  # [b, p*x]; integers < 2^24, exact in float32
    np.abs(lin, out=lin)
    sums = (lin.reshape(-1, cells) @ np.ones(cells, dtype=np.float32)).reshape(q1_batch.shape[0], pats.shape[0])
    sums = np.rint(sums).astype(np.int64)
    return sums.max(axis=1), sums.argmax(axis=1)


def exhaust_range(n_res: int, f0_lo: int, f0_hi: int, deadline: float) -> dict[str, Any]:
    """Exact max of S over all +-1 (F0, F1, F2) with F0 index in [f0_lo, f0_hi) (F0[0,0]=F1[0,0]=+1)."""
    size = 2**n_res
    q1_all = all_sign_matrices(n_res, fix_first=True)
    q1f = q1_all.reshape(q1_all.shape[0], size * size).astype(np.float32)
    pats = sign_patterns(len(term_vectors(n_res)))
    best_s, best_cfg = -1, None
    done_hi = f0_lo
    for f0 in range(f0_lo, f0_hi):
        if time.time() > deadline:
            break
        q0 = sign_matrix_from_index(f0, n_res, fix_first=True)
        vals, arg = best_f2_for_pairs(q0, q1_all, n_res, q1f)
        b = int(vals.argmax())
        if int(vals[b]) > best_s:
            best_s = int(vals[b])
            c = coefficient_vectors(q0, q1_all[b : b + 1], n_res)[0]
            v = pats[int(arg[b])] @ c
            q2 = np.where(v >= 0, 1, -1).reshape(size, size)
            best_cfg = [q0, q1_all[b], q2]
        done_hi = f0 + 1
    out: dict[str, Any] = {"n_res": n_res, "f0_lo": f0_lo, "f0_hi_done": done_hi, "f0_hi_target": f0_hi}
    out["complete"] = done_hi == f0_hi
    out["max_S"] = best_s
    out["max_ratio"] = str(Fraction(best_s, size**3)) if best_s >= 0 else None
    if best_cfg is not None:
        exact, parts = h5x.exact_ratio(best_cfg)
        out["argmax_recheck_h5_exact"] = str(exact)
        out["argmax_recheck_agrees"] = exact == Fraction(best_s, size**3)
        out["argmax"] = [x.tolist() for x in best_cfg]
    return out


# ----------------------------------------------------------------------------- explain


def walsh_spectrum(x: np.ndarray) -> np.ndarray:
    n = x.shape[0].bit_length() - 1
    h = walsh_matrix(n)
    return (h @ np.asarray(x, dtype=np.int64) @ h) / x.size


def explain(signs: list[np.ndarray]) -> dict[str, Any]:
    """Per-scale and per-triple exact decomposition, and the 2D Walsh spectrum of each F_v."""
    a = [np.asarray(x, dtype=np.int64) for x in signs]
    size = a[0].shape[0]
    n_res = size.bit_length() - 1
    w3 = Fraction(1, size**3)
    total, parts = h5x.exact_ratio(a)
    triples: dict[str, list[dict[str, Any]]] = {}
    for k in range(-n_res + 1, 1):
        m = 2 ** (-k)
        b = size // m
        s = _signs(b, True)
        rows = []
        for n0 in range(m):
            for n1 in range(m):
                n2 = n0 ^ n1
                x0 = a[0][n0 * b : (n0 + 1) * b, n1 * b : (n1 + 1) * b] * s[:, None] * s[None, :]
                x1 = a[1][n1 * b : (n1 + 1) * b, n2 * b : (n2 + 1) * b] * s[None, :]
                x2 = a[2][n2 * b : (n2 + 1) * b, n0 * b : (n0 + 1) * b]
                val = int(np.einsum("ij,jk,ki->", x0, x1, x2))
                max_abs = b**3
                rows.append({"n0": n0, "n1": n1, "n2": n2, "int": val, "L": str(m * val * w3), "saturates": abs(val) == max_abs})
        triples[str(k)] = rows
    spectra = []
    for x in a:
        sp = walsh_spectrum(x)
        nz = np.argwhere(np.abs(sp) > 1e-12)
        spectra.append({"support_size": int(len(nz)), "coeffs": [[int(i), int(j), float(sp[i, j])] for i, j in nz]})
    return {"n_res": n_res, "exact_ratio": str(total), "parts": parts, "triples": triples, "walsh_spectra": spectra, "signs": [x.tolist() for x in a]}


# ----------------------------------------------------------------------------- controls


def exhaust_crosscheck(rng: np.random.Generator) -> dict[str, Any]:
    """Independent checks of the exhaustive kernel at N=2 (term list vs int_parts; pattern max vs all 2^16 F2)."""
    terms = term_vectors(2)
    agree = True
    for _ in range(3):
        q = [rng.choice(np.array([-1, 1], dtype=np.int64), size=(4, 4)) for _ in range(3)]
        direct = sum(wt * abs(int(np.einsum("ij,jk,ki,i,j,k->", q[0], q[1], q[2], g0, g1, g2))) for wt, g0, g1, g2 in terms)
        agree = agree and direct == int_parts(q)[0]
    q0 = rng.choice(np.array([-1, 1], dtype=np.int64), size=(4, 4))
    q1 = rng.choice(np.array([-1, 1], dtype=np.int64), size=(4, 4))
    q2_all = all_sign_matrices(2, fix_first=False)
    brute = np.zeros(q2_all.shape[0], dtype=np.int64)
    for wt, g0, g1, g2 in terms:
        brute += wt * np.abs(np.einsum("ij,jk,bki,i,j,k->b", q0, q1, q2_all, g0, g1, g2))
    val, _ = best_f2_for_pairs(q0, q1[None], 2)
    return {"term_sum_equals_int_parts": bool(agree), "pattern_max_equals_bruteforce_max": int(val[0]) == int(brute.max()), "n_terms_N2": len(terms)}


def controls() -> dict[str, Any]:
    """Positive and negative controls run inside every chunk; `pass` must be True to count."""
    out: dict[str, Any] = {}
    ones3 = [np.ones((8, 8), dtype=np.int64)] * 3
    c1 = certify(ones3, threshold=Fraction(1))
    out["const_ratio_cubed"] = c1["ratio_cubed"]
    ok = c1["ratio_cubed"] == "1" and not c1["exceeds"]
    w4 = witness_signs(4)
    exact4, _ = h5x.exact_ratio(w4)
    above = certify(w4, threshold=THRESHOLD)
    below = certify(w4, threshold=FIVE_HALVES - Fraction(1, 10**9))
    out["witness_N4_exact"] = str(exact4)
    out["witness_N4_exceeds_threshold"] = above["exceeds"]
    out["witness_N4_exceeds_5/2-1e-9"] = below["exceeds"]
    ok = ok and exact4 == FIVE_HALVES and not above["exceeds"] and below["exceeds"]
    lift = certify(kron_lift(w4, [np.ones((2, 2), dtype=np.int64)] * 3), threshold=FIVE_HALVES)
    out["ones_lift_N5_ratio_cubed"] = lift["ratio_cubed"]
    ok = ok and Fraction(lift["ratio_cubed"]) == FIVE_HALVES**3
    rng = np.random.default_rng(424242)
    maxrel = 0.0
    for n in (2, 3):
        q = [rng.integers(-50, 51, size=(2**n, 2**n)) for _ in range(3)]
        c = certify(q)
        f = h5d.ratio([x.astype(float) for x in q], n)
        maxrel = max(maxrel, abs(c["ratio_float"] - f) / f)
    out["int_vs_float_maxrel"] = maxrel
    ok = ok and maxrel < 1e-12
    q = [rng.integers(-5, 6, size=(4, 4)) for _ in range(3)]
    s_int, _ = int_parts(q)
    brute = abs(float(np.einsum("ij,jk,ki->", *[x.astype(float) for x in q]))) / 64.0
    for k in (-1, 0):
        m = 2 ** (-k)
        for i0 in range(m):
            for i1 in range(m):
                brute += abs(h5d.brute_force_term([x.astype(float) for x in q], 2, k, i0, i1))
    out["int_vs_bruteforce_absdiff_N2"] = abs(s_int / 64.0 - brute)
    ok = ok and abs(s_int / 64.0 - brute) < 1e-12
    a = [rng.standard_normal((8, 8)) for _ in range(3)]
    gdiff = float(np.abs(gradient(a, 3, True) - h5d.gradient_first(a, 3)).max())
    out["gradient_vs_h5_dyadic_maxdiff"] = gdiff
    ok = ok and gdiff < 1e-14
    hf3 = certify(ones3, threshold=Fraction(4), haar=False)
    hf6 = certify([np.ones((64, 64), dtype=np.int64)] * 3, threshold=Fraction(7), haar=False)
    out["haarfree_const_ratio_cubed_N3_N6"] = [hf3["ratio_cubed"], hf6["ratio_cubed"]]
    ok = ok and Fraction(hf3["ratio_cubed"]) == 64 and Fraction(hf6["ratio_cubed"]) == 343
    xs = exhaust_crosscheck(rng)
    out["exhaust_crosscheck"] = xs
    ok = ok and xs["term_sum_equals_int_parts"] and xs["pattern_max_equals_bruteforce_max"]
    out["pass"] = bool(ok)
    return out


# ----------------------------------------------------------------------------- campaign


def _spec(kind: str, **kw: Any) -> dict[str, Any]:
    return {"kind": kind, **kw}


def campaign() -> dict[str, dict[str, Any]]:
    """Frozen chunk table (hashed in the preregistration). Seeds are SEED_BASE + offset."""
    c: dict[str, dict[str, Any]] = {}
    c["C00_controls"] = _spec("controls")
    c["P01_power_haarfree_N4"] = _spec("ascent", n_res=4, init="gauss", haar=False, seeds=list(range(100, 104)), sweeps=200)
    c["E01_exhaust_N1"] = _spec("exhaust", n_res=1, lo=0, hi=2**3)
    n2_reps = 2**15
    step = N2_STEP
    for i in range(n2_reps // step):
        c[f"E2_{i:02d}_exhaust_N2"] = _spec("exhaust", n_res=2, lo=i * step, hi=(i + 1) * step)
    for n, d in ((5, 1), (6, 2)):
        for order in ("witness_coarse", "witness_fine"):
            c[f"W_N{n}_{order}_enum"] = _spec("walsh_enum", n_res=n, d=d, order=order)
    for n, d, count in ((7, 3, 1500), (8, 4, 400)):
        for order in ("witness_coarse", "witness_fine"):
            c[f"W_N{n}_{order}_sample"] = _spec("walsh_sample", n_res=n, d=d, order=order, count=count, seed=200 + n + (0 if order == "witness_coarse" else 10))
    c["W_N8_witness_x_witness"] = _spec("ww_tensor")
    c["S_N5_multiscale_signs_exact"] = _spec("sign_sample", n_res=5, count=3000, seed=300)
    c["S_N6_multiscale_signs_exact"] = _spec("sign_sample", n_res=6, count=1500, seed=301)
    for n, k in ((5, 8), (6, 8), (7, 3)):
        for order in ("witness_coarse", "witness_fine"):
            c[f"A_N{n}_{order}_walsh_top"] = _spec("ascent", n_res=n, init="walsh_top", source=f"W_N{n}_{order}_{'enum' if n < 7 else 'sample'}", top=k, noise=0.05, seeds=list(range(400 + 10 * n, 400 + 10 * n + k)), sweeps=200)
    c["A_N5_multiscale_signs"] = _spec("ascent", n_res=5, init="multiscale_signs", noise=0.05, seeds=list(range(500, 530)), sweeps=200)
    c["A_N6_multiscale_signs"] = _spec("ascent", n_res=6, init="multiscale_signs", noise=0.05, seeds=list(range(530, 550)), sweeps=200)
    c["A_N6_multiscale_gauss"] = _spec("ascent", n_res=6, init="multiscale_gauss", decay=0.7, seeds=list(range(550, 570)), sweeps=200)
    c["A_N7_multiscale_signs"] = _spec("ascent", n_res=7, init="multiscale_signs", noise=0.05, seeds=list(range(570, 576)), sweeps=200)
    c["A_N7_multiscale_gauss"] = _spec("ascent", n_res=7, init="multiscale_gauss", decay=0.7, seeds=list(range(576, 582)), sweeps=200)
    for n in (5, 6, 7):
        for sigma in (0.05, 0.2, 0.5):
            c[f"A_N{n}_continuation_s{sigma}"] = _spec("ascent", n_res=n, init="continuation", noise=sigma, seeds=list(range(600 + 100 * n + int(100 * sigma), 600 + 100 * n + int(100 * sigma) + (5 if n < 7 else 2))), sweeps=200)
    for i, sigma in enumerate((0.1, 0.3)):
        c[f"A_N8_continuation_s{sigma}"] = _spec("ascent", n_res=8, init="continuation", noise=sigma, seeds=[900 + i], sweeps=200)
    for i in range(2):
        c[f"A_N8_gauss_{i}"] = _spec("ascent", n_res=8, init="gauss", seeds=[910 + i], sweeps=200)
    c["A_N8_witness_coarse_walsh_top"] = _spec("ascent", n_res=8, init="walsh_top", source="W_N8_witness_coarse_sample", top=1, noise=0.05, seeds=[920], sweeps=200)
    return c


def _init(spec: dict[str, Any], seed: int, rank: int) -> list[np.ndarray] | None:
    n = spec["n_res"]
    rng = np.random.default_rng(SEED_BASE + seed)
    init = spec["init"]
    noise = float(spec.get("noise", 0.0))
    if init == "gauss":
        base = [rng.standard_normal((2**n, 2**n)) for _ in range(3)]
        return base
    if init == "multiscale_signs":
        base = [x.astype(float) for x in multiscale_signs(rng, n)]
    elif init == "multiscale_gauss":
        return multiscale_gauss(rng, n, float(spec["decay"]))
    elif init == "continuation":
        prev = witness_float(n - 1)
        prev = [x / np.abs(x).max() for x in prev]
        base = [upsample(x, n) for x in prev]
    elif init == "walsh_top":
        src = CHUNK_DIR / f"{spec['source']}.json"
        if not src.exists():
            return None
        top = json.loads(src.read_text())["top"]
        if rank >= len(top):
            return None
        base = [x.astype(float) for x in walsh_lift(witness_signs(4), top[rank]["d"], tuple(tuple(p) for p in top[rank]["idx"]), top[rank]["order"])]
    else:
        raise ValueError(init)
    return [x + noise * rng.standard_normal(x.shape) for x in base]


def _walsh_eval(n: int, d: int, order: str, combos: list[tuple[tuple[int, int], ...]], deadline: float) -> dict[str, Any]:
    w4 = witness_signs(4)
    rows = []
    for idx in combos:
        if time.time() > deadline:
            break
        f = walsh_lift(w4, d, idx, order)
        cert = certify(f)
        rows.append({"idx": [list(p) for p in idx], "d": d, "order": order, "ratio_cubed": cert["ratio_cubed"], "ratio_float": cert["ratio_float"], "exceeds": cert["exceeds"]})
    rows.sort(key=lambda r: -Fraction(r["ratio_cubed"]))
    exceed = [r for r in rows if r["exceeds"]]
    return {"evaluated": len(rows), "planned": len(combos), "top": rows[:10], "max_ratio_float": rows[0]["ratio_float"] if rows else None, "certified_exceedances": exceed}


def run_chunk(cid: str, spec: dict[str, Any]) -> dict[str, Any]:
    t0 = time.time()
    deadline = t0 + CHUNK_BUDGET_S
    ctrl = controls()
    out: dict[str, Any] = {"chunk": cid, "spec": spec, "code_sha256": code_hashes(), "input_sha256": input_hashes(), "controls": ctrl, "date": "2026-10-07"}
    if not ctrl["pass"]:
        out["status"] = "crash"
        return out
    kind = spec["kind"]
    if kind == "controls":
        out["status"] = "ok"
    elif kind == "exhaust":
        out["result"] = exhaust_range(spec["n_res"], spec["lo"], spec["hi"], deadline)
        out["status"] = "ok" if out["result"]["complete"] else "incomplete"
    elif kind == "walsh_enum":
        top = 4 ** spec["d"]
        combos = list(itertools.product(itertools.product(range(2 ** spec["d"]), repeat=2), repeat=3))
        assert len(combos) == top**3
        out["result"] = _walsh_eval(spec["n_res"], spec["d"], spec["order"], combos, deadline)
        out["status"] = "ok" if out["result"]["evaluated"] == len(combos) else "incomplete"
    elif kind == "walsh_sample":
        rng = np.random.default_rng(SEED_BASE + spec["seed"])
        combos = [walsh_choice(rng, spec["d"], coupled=(i % 2 == 0)) for i in range(spec["count"])]
        out["result"] = _walsh_eval(spec["n_res"], spec["d"], spec["order"], combos, deadline)
        out["status"] = "ok" if out["result"]["evaluated"] == len(combos) else "incomplete"
    elif kind == "ww_tensor":
        w4 = witness_signs(4)
        rows = []
        for rot in range(3):
            inner = w4[rot:] + w4[:rot]
            for flip in ((1, 1, 1), (1, 1, -1), (1, -1, 1), (-1, 1, 1)):
                f = kron_lift(w4, [s * x for s, x in zip(flip, inner)])
                cert = certify(f)
                rows.append({"rot": rot, "flip": list(flip), "ratio_cubed": cert["ratio_cubed"], "ratio_float": cert["ratio_float"], "exceeds": cert["exceeds"]})
        out["result"] = {"rows": rows, "max_ratio_float": max(r["ratio_float"] for r in rows), "certified_exceedances": [r for r in rows if r["exceeds"]]}
        out["status"] = "ok"
    elif kind == "sign_sample":
        rng = np.random.default_rng(SEED_BASE + spec["seed"])
        best: dict[str, Any] | None = None
        exceed = []
        evaluated = 0
        for _ in range(spec["count"]):
            if time.time() > deadline:
                break
            f = multiscale_signs(rng, spec["n_res"])
            cert = certify(f)
            evaluated += 1
            if cert["exceeds"]:
                exceed.append({"signs": [x.tolist() for x in f], "cert": cert})
            if best is None or Fraction(cert["ratio_cubed"]) > Fraction(best["ratio_cubed"]):
                best = {"ratio_cubed": cert["ratio_cubed"], "ratio_float": cert["ratio_float"]}
        out["result"] = {"evaluated": evaluated, "planned": spec["count"], "best": best, "certified_exceedances": exceed}
        out["status"] = "ok" if evaluated == spec["count"] else "incomplete"
    elif kind == "ascent":
        out["result"] = _run_ascent(cid, spec, deadline)
        out["status"] = out["result"].pop("_status")
    else:
        raise ValueError(kind)
    out["elapsed_s"] = round(time.time() - t0, 2)
    return out


def _run_ascent(cid: str, spec: dict[str, Any], deadline: float) -> dict[str, Any]:
    n = spec["n_res"]
    haar = bool(spec.get("haar", True))
    res: dict[str, Any] = {"restarts": []}
    if n >= 8:
        rng = np.random.default_rng(SEED_BASE + 999)
        probe = [rng.standard_normal((2**n, 2**n)) for _ in range(3)]
        tp = time.time()
        for _ in range(3):
            probe[0] = h5d.hoelder_step(gradient(probe, n, haar), n)
            probe = [probe[1], probe[2], probe[0]]
        h5d.ratio(probe, n, haar)
        res["probe_sweep_s"] = round(time.time() - tp, 3)
        if res["probe_sweep_s"] > N8_SWEEP_LIMIT_S:
            res["_status"] = "skipped_by_preregistered_timing_rule"
            return res
    best_val, best_a = 0.0, None
    for rank, seed in enumerate(spec["seeds"]):
        if time.time() > deadline:
            res["restarts"].append({"seed": seed, "status": "not_started_budget"})
            continue
        a0 = _init(spec, seed, rank)
        if a0 is None:
            res["restarts"].append({"seed": seed, "status": "blocked_missing_source"})
            continue
        start = h5d.ratio(a0, n, haar)
        reserve = 75.0 if n >= 8 else 15.0  # time kept for exact + high-precision certification
        a, val, sweeps, conv = ascend_timed(a0, n, spec["sweeps"], deadline - reserve, haar)
        cert = certify_candidate(a, haar)
        row = {"seed": seed, "start_ratio": start, "final_ratio": val, "sweeps": sweeps, "converged": conv, "float_exceeds": val > float(THRESHOLD), "certified_exceeds": cert["certified_exceeds"], "quantized_ratio_float": cert["quantized"]["ratio_float"], "sign_ratio_float": cert["sign"]["ratio_float"]}
        if haar:
            row["sign_agrees_with_h5_exact"] = cert["sign_agrees_with_h5_exact"]
        if cert["certified_exceeds"]:
            row["certificate"] = cert
        res["restarts"].append(row)
        if val > best_val:
            best_val, best_a = val, a
    if best_a is not None:
        CHUNK_DIR.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(CHUNK_DIR / f"{cid}_best.npz", *best_a)
    res["best_ratio"] = best_val
    statuses = [r.get("status", "done") for r in res["restarts"]]
    res["_status"] = "ok" if all(s == "done" for s in statuses) else ("blocked" if all(s == "blocked_missing_source" for s in statuses) else "incomplete")
    return res


def summary() -> dict[str, Any]:
    hashes = code_hashes()
    inputs = input_hashes()
    table = campaign()
    rows: dict[str, Any] = {}
    certified: list[dict[str, Any]] = []
    uncertified: list[dict[str, Any]] = []
    best_float = 0.0
    n2_parts = []
    n1_max: str | None = None
    for cid in table:
        path = CHUNK_DIR / f"{cid}.json"
        if not path.exists():
            rows[cid] = "missing"
            continue
        d = json.loads(path.read_text())
        if d["code_sha256"] != hashes or d.get("input_sha256") != inputs:
            rows[cid] = "sha_mismatch (excluded)"
            continue
        if not d["controls"]["pass"]:
            rows[cid] = "crash (excluded)"
            continue
        rows[cid] = d["status"]
        r = d.get("result", {})
        if d["spec"]["kind"] == "ascent":
            for row in r.get("restarts", []):
                if "final_ratio" not in row:
                    continue
                if d["spec"].get("haar", True):
                    best_float = max(best_float, row["final_ratio"])
                    if row["certified_exceeds"]:
                        certified.append({"chunk": cid, "seed": row["seed"]})
                    elif row["float_exceeds"]:
                        uncertified.append({"chunk": cid, "seed": row["seed"], "final_ratio": row["final_ratio"]})
        elif d["spec"]["kind"] == "exhaust":
            if r.get("max_ratio") and Fraction(r["max_ratio"]) > THRESHOLD:
                certified.append({"chunk": cid, "exhaustive_max_ratio": r["max_ratio"]})
            if d["spec"]["n_res"] == 2:
                n2_parts.append(r)
            else:
                n1_max = r.get("max_ratio") if r.get("complete") and r.get("argmax_recheck_agrees") else None
        else:
            for e in r.get("certified_exceedances", []):
                certified.append({"chunk": cid, "entry": e.get("idx", e.get("rot"))})
            if r.get("max_ratio_float") is not None:
                best_float = max(best_float, r["max_ratio_float"])
            if r.get("best"):
                best_float = max(best_float, r["best"]["ratio_float"])
    power = json.loads((CHUNK_DIR / "P01_power_haarfree_N4.json").read_text()) if (CHUNK_DIR / "P01_power_haarfree_N4.json").exists() else None
    power_ok = bool(power and power["controls"]["pass"] and any(rw.get("certified_exceeds") for rw in power["result"]["restarts"]))
    n2_complete = len(n2_parts) == 2**15 // N2_STEP and all(p["complete"] and p.get("argmax_recheck_agrees", False) for p in n2_parts)
    n2_max = max((Fraction(p["max_ratio"]) for p in n2_parts if p["max_ratio"]), default=None)
    if not power_ok:
        verdict = "CRASH (power control did not certify an exceedance on the Haar-free form)"
    elif certified:
        verdict = "REFUTED"
    else:
        verdict = "NOT_REFUTED"
    return {
        "hypothesis": "H5'",
        "code_sha256": hashes,
        "chunks": rows,
        "power_control_pass": power_ok,
        "certified_exceedances": certified,
        "uncertified_float_exceedances": uncertified,
        "best_float_ratio_haar": best_float,
        "exhaustive_N1_max_ratio": n1_max,
        "exhaustive_N2_complete": n2_complete,
        "exhaustive_N2_max_ratio": str(n2_max) if n2_max is not None else None,
        "verdict": verdict,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="night lane H5: multi-scale search against C* = 5/2")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("controls")
    sub.add_parser("list")
    pc = sub.add_parser("chunk")
    pc.add_argument("ids", nargs="+")
    pe = sub.add_parser("explain")
    pe.add_argument("npz", type=Path)
    pe.add_argument("--out", type=Path, required=True)
    sub.add_parser("summary")
    args = p.parse_args()
    if args.cmd == "controls":
        print(json.dumps(controls()))
        return 0
    table = campaign()
    if args.cmd == "list":
        for cid, spec in table.items():
            done = (CHUNK_DIR / f"{cid}.json").exists()
            print(cid, "done" if done else "todo", json.dumps(spec))
        return 0
    if args.cmd == "chunk":
        CHUNK_DIR.mkdir(parents=True, exist_ok=True)
        for cid in args.ids:
            path = CHUNK_DIR / f"{cid}.json"
            if path.exists():
                print(json.dumps({"chunk": cid, "skipped": "exists"}))
                continue
            out = run_chunk(cid, table[cid])
            path.write_text(json.dumps(out, indent=1) + "\n")
            print(json.dumps({"chunk": cid, "status": out["status"], "elapsed_s": out.get("elapsed_s")}))
        return 0
    if args.cmd == "explain":
        z = np.load(args.npz)
        signs = [np.where(z[f] >= 0, 1, -1).astype(np.int64) for f in z.files]
        out_path = args.out.resolve()
        if LANE not in out_path.parents:
            raise SystemExit("explain output must be inside the lane directory")
        out_path.write_text(json.dumps(explain(signs), indent=1) + "\n")
        print(json.dumps({"written": str(out_path)}))
        return 0
    s = summary()
    (LANE / "summary.json").write_text(json.dumps(s, indent=1) + "\n")
    print(json.dumps({k: s[k] for k in ("verdict", "power_control_pass", "best_float_ratio_haar", "exhaustive_N2_max_ratio")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
