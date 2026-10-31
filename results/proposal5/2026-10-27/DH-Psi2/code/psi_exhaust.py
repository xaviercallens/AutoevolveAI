#!/usr/bin/env python3
"""DH-Psi2 (Proposal 5, item 4): exhaustive max of Psi = H + 3|T| over all sign inputs at resolution 2.

Extension of the 2026-10-07 night-lane exhaustive R kernel
(scripts/openai_math/hypotheses/night/h5_multiscale.py, read-only, NOT edited: its sha256 is pinned
in published chunk files) to a weighted objective

    S_w(F) = n^3 * ( w_T |T(F)| + H(F) ),   n = 4,

with w_T = 1 (R), 3 (Psi), 4 (planted negative control), and Haar or Haar-free (all signs +1) forms.
Psi <= 3  <=>  S_3 <= 3 * 64 = 192.

Reduction (same as the R run): every term is trilinear in (F0, F1, F2), so F_v -> -F_v leaves every
|term| unchanged; we fix F0[0,0] = F1[0,0] = +1 (2^15 * 2^15 pairs). For fixed (F0, F1) each term is
linear in F2, so  max_{F2 in {+-1}^16} sum_t w_t |<c_t, F2>| = max_{s in {+-1}^6, s_0=+1} || sum_t s_t w_t c_t ||_1.

Arithmetic: coefficient vectors are int64; the batched product uses float32 matmul, exact because every
partial sum is an integer below 2^24 (guard raises otherwise). An independent pure-int64 C enumeration
(psi_exhaust.c) is the full second enumeration.

Usage:
  psi_exhaust.py chunk MODE LO HI OUT.json      (F0 index range [LO, HI) of 2^15)
  psi_exhaust.py controls OUT.json              (term/reduction cross-checks, seed values)
MODE in {R, PSI, PLANT4, HF_R, HF_PSI}.
"""

from __future__ import annotations

import os

for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_var] = "1"

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

REPO = Path(__file__).resolve().parents[5]
HYP = REPO / "scripts" / "openai_math" / "hypotheses"
N_RES = 2
SIZE = 4
CELLS = 16
SCALE = SIZE**3  # 64
MODES: dict[str, tuple[int, bool]] = {
    "R": (1, True),
    "PSI": (3, True),
    "PLANT4": (4, True),
    "HF_R": (1, False),
    "HF_PSI": (3, False),
}
THRESHOLD_S = 3 * SCALE  # 192 : the bound "<= 3" in units of 1/64


def _load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


h5x = _load("h5_exact_psi2", HYP / "h5_exact.py")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def haar_vec(n: int, b: int, haar: bool) -> np.ndarray:
    """Haar sign vector of block n of length b on the 4-cell axis (all +1 on the block if not haar)."""
    v = np.zeros(SIZE, dtype=np.int64)
    if haar:
        v[n * b : n * b + b // 2] = 1
        v[n * b + b // 2 : (n + 1) * b] = -1
    else:
        v[n * b : (n + 1) * b] = 1
    return v


def term_vectors(w_t: int, haar: bool) -> list[tuple[int, np.ndarray, np.ndarray, np.ndarray]]:
    """(weight in units of 1/64, g0, g1, g2): term_t = sum_{ijk} F0[i,j]F1[j,k]F2[k,i] g0[i] g1[j] g2[k]."""
    one = np.ones(SIZE, dtype=np.int64)
    terms = [(w_t, one, one, one)]
    for level in range(N_RES):
        m = 2**level
        b = SIZE // m
        for p in range(m):
            for q in range(m):
                terms.append((m, haar_vec(p, b, haar), haar_vec(q, b, haar), haar_vec(p ^ q, b, haar)))
    return terms


def coeff_basis(q0: np.ndarray, terms: list[tuple[int, np.ndarray, np.ndarray, np.ndarray]]) -> np.ndarray:
    """K[y, t, x]: weighted term t = sum_{y,x} F1_flat[y] K[y,t,x] F2_flat[x]  (y = j*4+k, x = k*4+i)."""
    k = np.zeros((CELLS, len(terms), CELLS), dtype=np.int64)
    for t, (wt, g0, g1, g2) in enumerate(terms):
        for j in range(SIZE):
            for kk in range(SIZE):
                for i in range(SIZE):
                    k[j * SIZE + kk, t, kk * SIZE + i] += wt * q0[i, j] * g0[i] * g1[j] * g2[kk]
    return k


def sign_patterns(t: int) -> np.ndarray:
    return np.array([(1,) + p for p in itertools.product((1, -1), repeat=t - 1)], dtype=np.int64)


def sign_matrix(idx: int) -> np.ndarray:
    bits = [0] + [(idx >> j) & 1 for j in range(CELLS - 1)]
    return (1 - 2 * np.array(bits, dtype=np.int64)).reshape(SIZE, SIZE)


def all_f1() -> np.ndarray:
    return np.stack([sign_matrix(i) for i in range(2 ** (CELLS - 1))])


def best_f2(q0: np.ndarray, q1f: np.ndarray, terms: list[tuple[int, np.ndarray, np.ndarray, np.ndarray]], pats: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    kmap = coeff_basis(q0, terms)
    kp = np.einsum("pt,ytx->ypx", pats, kmap).reshape(CELLS, -1)
    if int(np.abs(kp).sum(axis=0).max()) * CELLS >= 2**24:
        raise OverflowError("float32 exactness bound exceeded")
    lin = q1f @ kp.astype(np.float32)
    np.abs(lin, out=lin)
    sums = lin.reshape(q1f.shape[0], pats.shape[0], CELLS).sum(axis=2, dtype=np.float64)
    sums_i = np.rint(sums).astype(np.int64)
    return sums_i.max(axis=1), sums_i.argmax(axis=1)


def f2_from_pattern(q0: np.ndarray, q1: np.ndarray, terms: list[tuple[int, np.ndarray, np.ndarray, np.ndarray]], pat: np.ndarray) -> np.ndarray:
    kmap = coeff_basis(q0, terms)  # [y,t,x]
    c = np.einsum("y,ytx->tx", q1.reshape(CELLS), kmap)
    v = pat @ c
    return np.where(v >= 0, 1, -1).reshape(SIZE, SIZE)


def direct_value(q: list[np.ndarray], w_t: int, haar: bool) -> int:
    """Independent of the kernel: 64*(w_t|T| + H) straight from eq. (trace) by block slicing."""
    a = [np.asarray(x, dtype=np.int64) for x in q]
    total = w_t * abs(int(np.trace(a[0] @ a[1] @ a[2])))
    for level in range(N_RES):
        m = 2**level
        b = SIZE // m
        s = np.diag(np.array([1] * (b // 2) + [-1] * (b // 2), dtype=np.int64) if haar else np.ones(b, dtype=np.int64))
        for p in range(m):
            for qq in range(m):
                r = p ^ qq
                b0 = a[0][p * b : (p + 1) * b, qq * b : (qq + 1) * b]
                b1 = a[1][qq * b : (qq + 1) * b, r * b : (r + 1) * b]
                b2 = a[2][r * b : (r + 1) * b, p * b : (p + 1) * b]
                total += m * abs(int(np.trace(s @ b0 @ s @ b1 @ s @ b2)))
    return total


def h5_exact_value(q: list[np.ndarray], w_t: int) -> int:
    """Second evaluator (preregistered): h5_exact.exact_ratio gives R and T; S_w = 64 * (R + (w_t - 1) T)."""
    total, parts = h5x.exact_ratio(q)
    val = (total + (w_t - 1) * Fraction(parts["T"])) * SCALE
    assert val.denominator == 1
    return int(val)


def run_chunk(mode: str, lo: int, hi: int) -> dict[str, Any]:
    w_t, haar = MODES[mode]
    terms = term_vectors(w_t, haar)
    pats = sign_patterns(len(terms))
    q1_all = all_f1()
    q1f = q1_all.reshape(-1, CELLS).astype(np.float32)
    hist = np.zeros(4096, dtype=np.int64)
    best_s, best_cfg = -1, None
    n_viol_pairs = 0
    viol_f0 = 0
    recheck_ok, recheck_n = 0, 0
    t0 = time.time()
    for f0 in range(lo, hi):
        q0 = sign_matrix(f0)
        vals, arg = best_f2(q0, q1f, terms, pats)
        hist += np.bincount(vals, minlength=4096)[:4096]
        nv = int((vals > THRESHOLD_S).sum())
        n_viol_pairs += nv
        viol_f0 += int(nv > 0)
        b = int(vals.argmax())
        q2 = f2_from_pattern(q0, q1_all[b], terms, pats[int(arg[b])])
        cfg = [q0, q1_all[b], q2]
        d = direct_value(cfg, w_t, haar)
        ok = d == int(vals[b])
        if haar:
            ok = ok and h5_exact_value(cfg, w_t) == int(vals[b])
        recheck_n += 1
        recheck_ok += int(ok)
        if int(vals[b]) > best_s:
            best_s, best_cfg = int(vals[b]), cfg
    nz = {str(i): int(c) for i, c in enumerate(hist) if c}
    return {
        "mode": mode,
        "w_T": w_t,
        "haar": haar,
        "f0_lo": lo,
        "f0_hi": hi,
        "pairs": (hi - lo) * 2 ** (CELLS - 1),
        "max_S": best_s,
        "max_value": str(Fraction(best_s, SCALE)),
        "threshold_S": THRESHOLD_S,
        "violating_pairs": n_viol_pairs,
        "violating_f0": viol_f0,
        "hist_maxS_per_pair": nz,
        "argmax_rechecks": recheck_n,
        "argmax_rechecks_agree": recheck_ok,
        "argmax": [x.tolist() for x in best_cfg] if best_cfg is not None else None,
        "elapsed_s": round(time.time() - t0, 2),
        "code_sha256": sha256_file(Path(__file__).resolve()),
        "h5_exact_sha256": sha256_file(HYP / "h5_exact.py"),
    }


def bruteforce_check(rng: np.random.Generator, mode: str, n_pairs: int) -> dict[str, Any]:
    """Kernel pattern max vs explicit max over all 2^16 F2 (direct trace formula, vectorised)."""
    w_t, haar = MODES[mode]
    terms = term_vectors(w_t, haar)
    pats = sign_patterns(len(terms))
    idx = np.arange(2**CELLS, dtype=np.int64)
    f2_all = (1 - 2 * ((idx[:, None] >> np.arange(CELLS)[None, :]) & 1)).reshape(-1, SIZE, SIZE)
    agree = 0
    for _ in range(n_pairs):
        q0 = rng.choice(np.array([-1, 1], dtype=np.int64), size=(SIZE, SIZE))
        q1 = rng.choice(np.array([-1, 1], dtype=np.int64), size=(SIZE, SIZE))
        # brute force: each weighted term is linear in F2 with coefficient matrix M_t[k,i]
        tot = np.zeros(f2_all.shape[0], dtype=np.int64)
        for wt, g0, g1, g2 in terms:
            mt = (g0[:, None] * q0 * g1[None, :]) @ (q1 * g2[None, :])  # [i,k]
            tot += wt * np.abs(np.einsum("ik,bki->b", mt, f2_all))
        val, _ = best_f2(q0, q1.reshape(1, CELLS).astype(np.float32), terms, pats)
        agree += int(int(val[0]) == int(tot.max()))
    return {"mode": mode, "pairs": n_pairs, "agree": agree}


def controls() -> dict[str, Any]:
    rng = np.random.default_rng(20261028)
    out: dict[str, Any] = {}
    rigor = json.loads((REPO / "results/openai_math/hypotheses/tensor/rigor.json").read_text())
    g = [np.array(m, dtype=np.int64) for m in rigor["seeds"]["g2_lane_witness"]["matrices"]]
    ones = [np.ones((SIZE, SIZE), dtype=np.int64)] * 3
    tot_g, parts_g = h5x.exact_ratio(g)
    out["seed_g_source"] = "results/openai_math/hypotheses/tensor/rigor.json seeds.g2_lane_witness"
    out["seed_g_R_h5_exact"] = str(tot_g)
    out["seed_g_T_h5_exact"] = parts_g["T"]
    out["seed_g_H_h5_exact"] = str(tot_g - Fraction(parts_g["T"]))
    out["seed_g_Psi"] = str(Fraction(direct_value(g, 3, True), SCALE))
    out["seed_g_Psi_h5_exact"] = str(Fraction(h5_exact_value(g, 3), SCALE))
    out["const_Psi"] = str(Fraction(direct_value(ones, 3, True), SCALE))
    out["const_R"] = str(Fraction(direct_value(ones, 1, True), SCALE))
    out["const_HF_R"] = str(Fraction(direct_value(ones, 1, False), SCALE))
    out["const_HF_Psi"] = str(Fraction(direct_value(ones, 3, False), SCALE))
    out["const_PLANT4"] = str(Fraction(direct_value(ones, 4, True), SCALE))
    # evaluator agreement on random sign inputs (direct vs h5_exact), all Haar weights
    agree = 0
    for _ in range(2000):
        q = [rng.choice(np.array([-1, 1], dtype=np.int64), size=(SIZE, SIZE)) for _ in range(3)]
        agree += int(all(direct_value(q, w, True) == h5_exact_value(q, w) for w in (1, 3, 4)))
    out["direct_vs_h5_exact_random"] = {"n": 2000, "agree": agree}
    out["bruteforce_l1_reduction"] = [bruteforce_check(rng, m, 300) for m in MODES]
    ok = (
        out["seed_g_R_h5_exact"] == "2"
        and out["seed_g_T_h5_exact"] == "1/2"
        and out["seed_g_H_h5_exact"] == "3/2"
        and out["seed_g_Psi"] == "3"
        and out["seed_g_Psi_h5_exact"] == "3"
        and out["const_Psi"] == "3"
        and out["const_HF_R"] == "3"
        and out["const_HF_Psi"] == "5"
        and out["const_PLANT4"] == "4"
        and agree == 2000
        and all(b["agree"] == b["pairs"] for b in out["bruteforce_l1_reduction"])
    )
    out["pass"] = bool(ok)
    out["code_sha256"] = sha256_file(Path(__file__).resolve())
    return out


def main() -> int:
    cmd = sys.argv[1]
    if cmd == "chunk":
        mode, lo, hi, path = sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), Path(sys.argv[5])
        res = run_chunk(mode, lo, hi)
        path.write_text(json.dumps(res, indent=1))
        print(json.dumps({k: res[k] for k in ("mode", "f0_lo", "f0_hi", "max_value", "violating_pairs", "argmax_rechecks_agree", "elapsed_s")}))
        return 0
    if cmd == "controls":
        res = controls()
        Path(sys.argv[2]).write_text(json.dumps(res, indent=1))
        print(json.dumps({"pass": res["pass"]}))
        return 0 if res["pass"] else 1
    raise SystemExit(f"unknown command {cmd}")


if __name__ == "__main__":
    raise SystemExit(main())
