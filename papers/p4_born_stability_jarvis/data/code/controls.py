"""Positive and negative controls for the M2 exact Born audit. Run BEFORE the dataset.

Usage: python -I controls.py <out_json>
"""
from __future__ import annotations

import json
import random
import sys
from fractions import Fraction

import numpy as np
import sympy

import born_exact as be


def cubic_rows(c11: float, c12: float, c44: float) -> list[list[float]]:
    r = [[0.0] * 6 for _ in range(6)]
    for i in range(3):
        for j in range(3):
            r[i][j] = c11 if i == j else c12
    for i in range(3, 6):
        r[i][i] = c44
    return r


def full_verdict(rows: list[list[float]]) -> dict[str, object]:
    m = be.to_matrix(rows)
    s = be.symmetrize(m)
    nominal = be.ldl_verdict(s)
    hs = be.symmetrize(be.half_widths(rows))
    arr = np.array(rows, dtype=float)
    lam = np.linalg.eigvalsh((arr + arr.T) / 2)
    return {
        "symmetric": be.is_symmetric(m),
        "exact_pd": nominal[0],
        "bareiss_pd": be.minors_pd(s),
        "pivot_index": nominal[1],
        "pivot": str(nominal[2]),
        "witness_xSx": None if nominal[3] is None else str(be.quad_form(s, nominal[3])),
        "interval": be.interval_verdict(s, hs, nominal),
        "linear_pass": be.linear_orthorhombic_pass(s),
        "float_F0": bool(lam.min() > 0),
        "lam_min_float": float(lam.min()),
    }


def main(out: str) -> int:
    res: dict[str, object] = {}
    ok_all = True

    def check(name: str, cond: bool, detail: object) -> None:
        nonlocal ok_all
        ok_all &= bool(cond)
        res[name] = {"pass": bool(cond), "detail": detail}
        print(("PASS " if cond else "FAIL ") + name, flush=True)

    # --- positive controls: textbook cubic crystals (literature room-temperature values) ---
    lit = {"Cu": (168.4, 121.4, 75.4), "Si": (165.7, 63.9, 79.6), "diamond": (1079.0, 124.0, 578.0)}
    for nm, (a, b, c) in lit.items():
        rows = cubic_rows(a, b, c)
        v = full_verdict(rows)
        born = be.born_class_verdict(be.symmetrize(be.to_matrix(rows)), "cubic")
        check(f"P_{nm}_stable", v["exact_pd"] and v["bareiss_pd"] and v["float_F0"] and born, {**v, "born_cubic": born})
        check(f"P_{nm}_interval_robust_pd", v["interval"] == "ROBUST_PD", v["interval"])

    # footnote 26 of Mouhat-Coudert 2014 (shear constants not given there: C44=C55=C66=1, labelled)
    rows = [[0.5, -1.0, 0.0, 0, 0, 0], [-1.0, 1.0, 0.0, 0, 0, 0], [0.0, 0.0, 1.0, 0, 0, 0],
            [0, 0, 0, 1.0, 0, 0], [0, 0, 0, 0, 1.0, 0], [0, 0, 0, 0, 0, 1.0]]
    v = full_verdict(rows)
    s = be.symmetrize(be.to_matrix(rows))
    born = be.born_class_verdict(s, "orthorhombic")
    nominal = be.ldl_verdict(s)
    check("P_footnote26_passes_linear_fails_exact",
          v["linear_pass"] and (not v["exact_pd"]) and (not v["bareiss_pd"]) and born is False and nominal[3] is not None
          and be.quad_form(s, nominal[3]) <= 0, {**v, "born_orthorhombic": born, "witness": [str(t) for t in nominal[3] or []]})
    check("P_footnote26_robust_not_pd", v["interval"] == "ROBUST_NOT_PD", v["interval"])

    # known-unstable cubic tensors
    for nm, args in {"C11_lt_abs_C12": (100.0, 120.0, 50.0), "negative_C44": (150.0, 50.0, -5.0),
                     "C11_lt_minus_2C12": (60.0, -40.0, 30.0)}.items():
        rows = cubic_rows(*args)
        v = full_verdict(rows)
        born = be.born_class_verdict(be.symmetrize(be.to_matrix(rows)), "cubic")
        check(f"P_unstable_{nm}", (not v["exact_pd"]) and (not v["bareiss_pd"]) and (not v["float_F0"]) and born is False, {**v, "born_cubic": born})

    # --- negative controls: corrupted tensors must flip verdicts ---
    for nm, (a, b, c) in lit.items():
        rows = cubic_rows(a, b, c)
        rows[0][0] = -rows[0][0]
        v = full_verdict(rows)
        check(f"N_{nm}_signflip_C11", (not v["exact_pd"]) and (not v["bareiss_pd"]) and v["interval"] == "ROBUST_NOT_PD", v)
        rows = cubic_rows(a, b, c)
        rows[3][3] = -rows[3][3]
        v = full_verdict(rows)
        check(f"N_{nm}_signflip_C44", not v["exact_pd"], v)
    rows = cubic_rows(*lit["Cu"])
    rows[0][1] += 0.1  # symmetry-breaking: C12 != C21
    v = full_verdict(rows)
    check("N_Cu_symmetry_break_detected", (v["symmetric"] is False), v)
    rows = cubic_rows(*lit["Cu"])
    rows[0][1] = 5000.0  # large symmetry break: stored C12 huge, C21 normal -> symmetrised C12 ~ 2560.7 > C11
    v = full_verdict(rows)
    check("N_Cu_symmetry_break_flips_verdict", (v["symmetric"] is False) and (not v["exact_pd"]), v)

    # rounding-boundary controls
    rows = cubic_rows(100.0, 100.0, 50.0)  # exactly singular (C11 = C12): d=0, not PD
    v = full_verdict(rows)
    check("N_boundary_singular_not_pd_and_ambiguous", (not v["exact_pd"]) and v["interval"] == "UNDECIDED_BY_BOUND", v)
    rows = cubic_rows(100.0, 99.9, 50.0)  # within one printed ulp of the boundary
    v = full_verdict(rows)
    check("N_near_boundary_pd_but_undecided", v["exact_pd"] and v["interval"] == "UNDECIDED_BY_BOUND", v)

    # float-vs-exact disagreement detection: singular tensor with a float lambda_min that may be +-tiny
    rows = cubic_rows(0.1 * 3, 0.30000000000000004 * 0 + 0.3, 50.0)  # 0.1*3 = 0.30000000000000004 (float), printed as such
    v = full_verdict(rows)
    res["info_float_vs_exact_probe"] = v
    print("INFO float probe", v, flush=True)

    # --- internal cross-validation on random rational matrices ---
    rng = random.Random(20261031)
    agree = 0
    n_rand = 6000
    n_pd = 0
    for t in range(n_rand):
        n = 6
        if t % 2 == 0:
            A = [[rng.randint(-4, 4) for _ in range(n)] for _ in range(n)]
            S = [[Fraction(sum(A[k][i] * A[k][j] for k in range(n)), rng.choice([1, 2, 5, 10])) + (Fraction(rng.randint(-1, 1), 10) if i == j else 0)
                  for j in range(n)] for i in range(n)]
            S = be.symmetrize(S)
        else:
            S = be.symmetrize([[Fraction(rng.randint(-30, 30), rng.choice([1, 2, 10])) for _ in range(n)] for _ in range(n)])
            for i in range(n):
                S[i][i] = abs(S[i][i]) + rng.randint(0, 30)
        a = be.is_pd(S)
        b = be.minors_pd(S)
        agree += int(a == b)
        n_pd += int(a)
        if t < 400:  # sympy leading-principal-minor determinants (third implementation) on a subset
            M = sympy.Matrix(n, n, lambda i, j: sympy.Rational(S[i][j].numerator, S[i][j].denominator))
            c = all(M[:k, :k].det() > 0 for k in range(1, n + 1))
            agree += int(a == c) - int(a == b) if False else 0
            if a != c:
                agree -= 1
        if (not a):
            ldl = be.ldl_verdict(S)
            assert ldl[3] is not None and be.quad_form(S, ldl[3]) <= 0
    check("X_ldl_vs_bareiss_vs_sympy_random", agree == n_rand, {"n": n_rand, "agree": agree, "n_pd": n_pd, "sympy_subset": 400})

    res["all_controls_pass"] = ok_all
    with open(out, "w") as f:
        json.dump(res, f, indent=1, default=str)
    print("ALL_CONTROLS_PASS", ok_all, flush=True)
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
