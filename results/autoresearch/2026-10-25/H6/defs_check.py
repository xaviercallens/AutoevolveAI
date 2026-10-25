"""H6 definition check: the recursive (top-bit-peeling) definitions used in
formal_cert/Autoresearch/DyadicHilbert.lean versus the recorded direct implementation
(results/openai_math/hypotheses/night_2026-10-07/H5/verify_tensor.py::direct_parts) and the recorded
exact values (verify_tensor.json, tensor_search.json).

Lean definitions mirrored here (integer, unnormalised; n = 2^N, n^3 = 8^N):
  X 0 = Unit, X (N+1) = Bool x X N        (top bit = most significant index bit)
  restrict F b c (x, y) = F((b,x),(c,y))  (= the (b,c) block of the matrix)
  T 0 = F0 F1 F2 at the single cell;  T (N+1) = sum_{b0,b1,b2} T N (F0|b0b1, F1|b1b2, F2|b2b0)
  L0 (N+1) = sum_{b0,b1,b2} sgn b0 sgn b1 sgn b2 T N (blocks),  sgn false = 1, sgn true = -1
  H 0 = 0;  H (N+1) = |L0| + 2 sum_{b0,b1} H N (F0|b0b1, F1|b1(b0 xor b1), F2|(b0 xor b1)b0)
  S = |T| + H;  for +-1 inputs R = S / 8^N.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path
from types import ModuleType

import numpy as np

H6 = Path(__file__).resolve().parent
REPO = H6.parents[3]
H5 = REPO / "results" / "openai_math" / "hypotheses" / "night_2026-10-07" / "H5"
W4 = REPO / "results" / "openai_math" / "hypotheses" / "H5" / "best_inputs_N4.npz"
Mat = np.ndarray


def _load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def blk(f: Mat, b: int, c: int) -> Mat:
    h = f.shape[0] // 2
    return f[b * h:(b + 1) * h, c * h:(c + 1) * h]


def t_rec(f0: Mat, f1: Mat, f2: Mat, pure: bool) -> int:
    if not pure:  # closed form sum_{x0,x1,x2} F0 F1 F2 (used only to keep N=8 tractable)
        return int(((f0.astype(object) @ f1.astype(object)) * f2.T.astype(object)).sum())
    if f0.shape[0] == 1:
        return int(f0[0, 0]) * int(f1[0, 0]) * int(f2[0, 0])
    return sum(t_rec(blk(f0, b0, b1), blk(f1, b1, b2), blk(f2, b2, b0), True)
               for b0 in (0, 1) for b1 in (0, 1) for b2 in (0, 1))


def sgn(b: int) -> int:
    return -1 if b else 1


def l0_rec(f0: Mat, f1: Mat, f2: Mat, pure: bool) -> int:
    return sum(sgn(b0) * sgn(b1) * sgn(b2) * t_rec(blk(f0, b0, b1), blk(f1, b1, b2), blk(f2, b2, b0), pure)
               for b0 in (0, 1) for b1 in (0, 1) for b2 in (0, 1))


def h_rec(f0: Mat, f1: Mat, f2: Mat, pure: bool) -> int:
    if f0.shape[0] == 1:
        return 0
    acc = abs(l0_rec(f0, f1, f2, pure))
    for b0 in (0, 1):
        for b1 in (0, 1):
            b2 = b0 ^ b1
            acc += 2 * h_rec(blk(f0, b0, b1), blk(f1, b1, b2), blk(f2, b2, b0), pure)
    return acc


def rht(f: list[Mat], pure: bool) -> tuple[Fraction, Fraction, Fraction]:
    n3 = f[0].shape[0] ** 3
    t = t_rec(*f, pure)
    h = h_rec(*f, pure)
    return Fraction(abs(t) + h, n3), Fraction(h, n3), Fraction(abs(t), n3)


def main() -> int:
    vt = _load("h5_verify_tensor_ro", H5 / "verify_tensor.py")
    rec_vt = json.loads((H5 / "verify_tensor.json").read_text())
    rec_ts = json.loads((H5 / "tensor_search.json").read_text())
    e2 = json.loads((H5 / "chunks" / "E2_00_exhaust_N2.json").read_text())["result"]["argmax"]
    g2 = [np.array(x, dtype=np.int64) for x in e2]
    z = np.load(W4)
    w4 = [np.where(z[k] >= 0, 1, -1).astype(np.int64) for k in z.files]
    out: dict[str, object] = {}
    ok = True

    def cmp(name: str, f: list[Mat], pure: bool, rec: tuple[str, str, str] | None) -> None:
        nonlocal ok
        r, h, t = rht(f, pure)
        dr, dh, dt = vt.pm1_ratio(f)
        row = {"R": str(r), "H": str(h), "T": str(t), "direct_R": str(dr), "direct_H": str(dh), "direct_T": str(dt),
               "pure_recursion": pure, "S_int": str(r * f[0].shape[0] ** 3), "H_int": str(h * f[0].shape[0] ** 3),
               "T_int_signed": t_rec(*f, pure)}
        good = (r, h, t) == (dr, dh, dt)
        if rec is not None:
            row["recorded"] = list(rec)
            good = good and (str(r), str(h), str(t)) == rec
        row["agree"] = good
        ok = ok and good
        out[name] = row

    b = rec_ts["bases"]["E2_00_argmax_N2"]
    cmp("g2_N2", g2, True, (b["R"], b["H"], b["T"]))
    cmp("w4_N4", w4, True, (rec_vt["w4"]["ratio"], rec_vt["w4"]["H"], rec_vt["w4"]["T"]))
    g22 = [np.kron(a, c) for a, c in zip(g2, g2)]
    cmp("g2xg2_N4", g22, True, None)
    g24 = [np.kron(np.kron(np.kron(a0, a0), a0), a0) for a0 in g2]
    cmp("g2pow4_N8", g24, False, None)
    w44 = [np.kron(a, c) for a, c in zip(w4, w4)]
    n8 = rec_vt["N8_w4xw4"]
    cmp("w4xw4_N8", w44, False, (n8["direct"], n8["H"], n8["T"]))
    # pure recursion on random +-1 inputs at N = 3 and on random integer inputs at N = 2 (signs/weights check)
    rng = np.random.default_rng(20261025)
    rand_ok = True
    for _ in range(10):
        q = [rng.choice(np.array([-1, 1]), size=(8, 8)) for _ in range(3)]
        rand_ok = rand_ok and rht(q, True) == vt.pm1_ratio(q)
    for _ in range(10):
        q = [rng.integers(-4, 5, size=(4, 4)) for _ in range(3)]
        tt, sc = vt.direct_parts(q)
        rand_ok = rand_ok and t_rec(*q, True) == tt and h_rec(*q, True) == sum(sc)
    out["random_pm1_N3_and_int_N2_agree"] = rand_ok
    ok = ok and rand_ok
    # negative control on the checker: transposing F2 (wrong coupling) must change the value for w4
    wrong = rht([w4[0], w4[1], w4[2].T.copy()], True)[0]
    out["neg_control_transposed_F2_R"] = str(wrong)
    out["neg_control_detected"] = wrong != Fraction(5, 2)
    ok = ok and bool(out["neg_control_detected"])
    out["g2_tables"] = e2
    out["all_agree"] = ok
    (H6 / "defs_check.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "g2_tables"}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
