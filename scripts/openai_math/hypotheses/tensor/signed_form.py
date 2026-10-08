#!/usr/bin/env python3
"""Signed per-scale form versus the absolute sum, on the tensor witnesses (exact arithmetic).

Upstream's "dyadic triangular Hilbert form" is the SIGNED form  Lam_{S,eps} = sum_k eps_k sum_{I in A_k} L_I
with |eps_k| <= 1; its sup over eps is  |T| + sum_l |S_l|  with  S_l = sum_{I in A_{-l}} L_I  (scales k >= 1
each carry 2^-k T, which sum to |T| with eps_k = sign(T)).  The paper's theorem is about the ABSOLUTE sum
|T| + sum_l sum_I |L_I|, which dominates it.  This script reports both for g^{(x)r}, so the paper can say
exactly what does and does not transfer.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h5_tensor_rigor import OUT_DIR, R_pm1, exact_T, kron, level_ints, resolution, seed_from_lane  # noqa: E402


def signed_sup(f: list[np.ndarray]) -> Fraction:
    """sup over |eps_k| <= 1 of the signed form, for +-1 step inputs: |T| + sum_l |S_l|."""
    n = f[0].shape[0]
    w3 = Fraction(1, n**3)
    total = abs(exact_T(f))
    for level in range(resolution(f[0])):
        total += abs(Fraction(int(level_ints(f, level).sum()) * 2**level) * w3)
    return total


def main() -> int:
    g = seed_from_lane()
    assert g is not None, "seed witness missing"
    rows = []
    cur = g
    for r in range(1, 5):
        if r > 1:
            cur = kron(cur, g)
        rows.append({"r": r, "N": resolution(cur[0]), "absolute_R": str(R_pm1(cur)), "signed_sup": str(signed_sup(cur)),
                     "signed_sup_float": float(signed_sup(cur))})
    out = {"note": "signed_sup = |T| + sum_l |sum_I L_I| (sup over |eps_k|<=1); absolute_R = |T| + sum_l sum_I |L_I|", "rows": rows}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "signed_form.json").write_text(json.dumps(out, indent=2) + "\n")
    for row in rows:
        print(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
