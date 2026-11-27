"""Verification of the Kronecker-tensor exceedance (deviations.md item 7).

Independent direct implementation of the dyadic triangular Hilbert ratio, written from the
upstream definition
    L_I = 2^{-k} int_{I0 x I1 x I2} F0(x0,x1) F1(x1,x2) F2(x2,x0) h_{I0}(x0) h_{I1}(x1) h_{I2}(x2),
I_v dyadic of length 2^k inside [0,1), indices with n0 xor n1 xor n2 = 0, h_I = +1 on the left half
and -1 on the right half; scales k >= 1 add |T| in total (T = int F0 F1 F2). Triples are enumerated
as (n0, n2) with n1 = n0 xor n2, and each integral is contracted as
sum_{x0,x1} [F0 h0 h1](x0,x1) * ([F1 h2] @ F2)(x1,x0). All sums are integers < 2^53 for the inputs
used here, so float64 matmul is exact; results are returned as Python Fractions.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import time
from fractions import Fraction
from pathlib import Path
from types import ModuleType
from typing import Any

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "1"

import numpy as np  # noqa: E402

LANE = Path(__file__).resolve().parent
REPO = LANE.parents[4]
HYP = REPO / "scripts" / "openai_math" / "hypotheses"
WITNESS = REPO / "results" / "openai_math" / "hypotheses" / "H5" / "best_inputs_N4.npz"


def _load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def direct_parts(f: list[np.ndarray]) -> tuple[int, list[int]]:
    """(T_int, [m_l * sum_I |int_I| for l = 0..N-1]) for integer inputs, independent code path."""
    a = [np.asarray(x, dtype=np.float64) for x in f]
    size = a[0].shape[0]
    n_res = size.bit_length() - 1
    t_int = int(round(float(((a[0] @ a[1]) * a[2].T).sum())))
    scale_sums = []
    for level in range(n_res):
        m = 2**level
        b = size // m
        h = np.concatenate([np.ones(b // 2), -np.ones(b // 2)])
        blk = [x.reshape(m, b, m, b).transpose(0, 2, 1, 3) for x in a]  # [row block, col block, b, b]
        n0 = np.arange(m)[:, None]
        n2 = np.arange(m)[None, :]
        n1 = n0 ^ n2
        f0 = blk[0][n0, n1] * h[:, None] * h[None, :]  # (x0, x1) with h_{I0} h_{I1}
        f1 = blk[1][n1, n2] * h[None, :]  # (x1, x2) with h_{I2}
        f2 = blk[2][n2, n0]  # (x2, x0)
        inner = np.matmul(f1, f2)  # (x1, x0)
        vals = (f0 * np.swapaxes(inner, -1, -2)).sum(axis=(-1, -2))
        ints = np.rint(vals).astype(np.int64)
        if float(np.abs(vals - ints).max()) > 0:
            raise ArithmeticError("non-integer triple value: float64 exactness lost")
        scale_sums.append(m * int(np.abs(ints).sum()))
    return t_int, scale_sums


def direct_ratio_cubed(f: list[np.ndarray]) -> Fraction:
    t_int, scales = direct_parts(f)
    size = f[0].shape[0]
    s = abs(t_int) + sum(scales)
    p = 1
    for x in f:
        p *= int(np.abs(np.asarray(x, dtype=np.int64)).astype(object).__pow__(3).sum())
    return Fraction(s**3, size**3 * p)


def pm1_ratio(f: list[np.ndarray]) -> tuple[Fraction, Fraction, Fraction]:
    """(ratio, H, |T|) for +-1 inputs: ratio = H + |T| (norms are 1)."""
    t_int, scales = direct_parts(f)
    size3 = f[0].shape[0] ** 3
    return Fraction(abs(t_int) + sum(scales), size3), Fraction(sum(scales), size3), Fraction(abs(t_int), size3)


def main() -> int:
    t0 = time.time()
    hx = _load("h5_exact_ro", HYP / "h5_exact.py")
    hd = _load("h5_dyadic_ro", HYP / "h5_dyadic.py")
    z = np.load(WITNESS)
    w4 = [np.where(z[k] >= 0, 1, -1).astype(np.int64) for k in z.files]
    out: dict[str, Any] = {"exploratory_parts": "independent implementation, product rule, N=12 triple tensor (deviations.md item 7)"}
    # controls for the independent implementation
    r4, h4, t4 = pm1_ratio(w4)
    ones = [np.ones((16, 16), dtype=np.int64)] * 3
    rng = np.random.default_rng(20261008)
    agree_random = True
    for _ in range(20):
        q = [rng.integers(-5, 6, size=(8, 8)) for _ in range(3)]
        d = direct_ratio_cubed(q)
        fl = hd.ratio([x.astype(float) for x in q], 3, True) ** 3
        agree_random = agree_random and abs(float(d) - fl) <= 1e-9 * max(1.0, fl)
    haarfree_like = pm1_ratio(ones)[0]
    out["controls"] = {"w4_direct": str(r4), "w4_h5_exact": str(hx.exact_ratio(w4)[0]), "ones_N4_direct": str(haarfree_like), "direct_vs_h5_dyadic_random_int_N3": agree_random}
    out["controls"]["pass"] = r4 == Fraction(5, 2) and hx.exact_ratio(w4)[0] == Fraction(5, 2) and haarfree_like == 1 and agree_random
    out["w4"] = {"ratio": str(r4), "H": str(h4), "T": str(t4)}
    # the N=8 tensor (chunk W_N8_witness_x_witness, rot 0, flip (1,1,1))
    w44 = [np.kron(c, f) for c, f in zip(w4, w4)]
    np.savez_compressed(LANE / "witness_N8_w4xw4.npz", *w44)
    ex8, parts8 = hx.exact_ratio(w44)
    r8, h8, t8 = pm1_ratio(w44)
    fl8 = hd.ratio([x.astype(float) for x in w44], 8, True)
    out["N8_w4xw4"] = {"h5_exact": str(ex8), "h5_exact_parts": parts8, "direct": str(r8), "H": str(h8), "T": str(t8), "h5_dyadic_float": fl8, "product_rule_prediction": str(h4 + t4 * r4)}
    out["N8_w4xw4"]["all_agree"] = ex8 == r8 == h4 + t4 * r4 and abs(fl8 - float(r8)) < 1e-12
    # product rule on random +-1 pairs (fine g random at N=2, coarse f random at N=2 or the witness)
    rule_ok = True
    rows = []
    for i in range(6):
        g = [rng.choice(np.array([-1, 1]), size=(4, 4)) for _ in range(3)]
        f = w4 if i % 2 == 0 else [rng.choice(np.array([-1, 1]), size=(8, 8)) for _ in range(3)]
        rf = pm1_ratio(f)[0]
        rg, hg, tg = pm1_ratio(g)
        lhs = pm1_ratio([np.kron(c, x) for c, x in zip(f, g)])[0]
        rows.append({"lhs": str(lhs), "rhs": str(hg + tg * rf)})
        rule_ok = rule_ok and lhs == hg + tg * rf
    out["product_rule_random"] = {"rows": rows, "holds": rule_ok}
    # triple tensor at N = 12 (independent code only)
    t1 = time.time()
    w444 = [np.kron(x, y) for x, y in zip(w44, w4)]
    r12, h12, tt12 = pm1_ratio(w444)
    out["N12_w4xw4xw4"] = {"direct": str(r12), "float": float(r12), "H": str(h12), "T": str(tt12), "product_rule_prediction": str(h4 + t4 * r8), "elapsed_s": round(time.time() - t1, 2)}
    out["elapsed_s"] = round(time.time() - t0, 2)
    (LANE / "verify_tensor.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
