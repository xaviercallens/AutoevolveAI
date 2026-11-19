#!/usr/bin/env python3
"""Generate Lean 4 proofs that BDF-k (k = 1..6) satisfies the Dahlquist ROOT CONDITION.

For rho = (z - 1) q with q monic of degree d, the proof that every root of q lies strictly
inside the unit disc is a Lyapunov argument made elementary. With w = conj z, and P the exact
rational solution of C^T P C - P = -I (C the companion matrix of q), whenever q(z) = 0 = q(w):

    sum_{i<d} (z w)^i  =  (1 - z w) * Pform(z, w)                       -- (*)

(a polynomial identity: LHS - RHS is an explicit combination A*q(z) + B*q(w), checked by Lean's
`linear_combination`). Pform is written as a sum of squares  sum_i d_i l_i(z) l_i(w)  with d_i > 0
and l_0 = 1, so with z w = |z|^2 and l_i(z) l_i(w) = |l_i(z)|^2 >= 0 we get Pform >= d_0 > 0 and
LHS >= 1 > 0, hence 1 - |z|^2 > 0. Every numeral is produced by exact Fraction arithmetic.

Also proved per k: rho(z) = (z - 1) q(z) (so a root is 1 or a root of q), and rho'(1) != 0
(the root at 1 is simple). Together: all roots in the closed disc, and the only unit-circle root,
z = 1, is simple -- the root condition. NOT proved here: the Dahlquist equivalence between the
root condition and boundedness of solutions.
"""

from __future__ import annotations

import re
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kge_bdf_pilot import bdf  # noqa: E402
from kge_lyapunov_cert import certificate  # noqa: E402


def num(x: Fraction) -> str:
    return f"({x.numerator} : ℂ)" if x.denominator == 1 else f"(({x.numerator} : ℂ) / {x.denominator})"


def poly_in(var: str, coeffs: list[Fraction], monic_top: bool = True) -> str:
    d = len(coeffs) - 1
    terms = [num(coeffs[0])] if coeffs[0] != 0 else []
    for i in range(1, d):
        terms.append(f"{num(coeffs[i])} * {var} ^ {i}" if i > 1 else f"{num(coeffs[i])} * {var}")
    terms.append(f"{var} ^ {d}" if d > 1 else var)
    return " + ".join(terms)


def l_expr(var: str, i: int, u: list[Fraction]) -> str:
    if i == 0:
        return "(1 : ℂ)"
    terms = [num(u[0])] if u[0] != 0 else []
    for j in range(1, i):
        if u[j] != 0:
            terms.append(f"{num(u[j])} * {var} ^ {j}" if j > 1 else f"{num(u[j])} * {var}")
    terms.append(f"{var} ^ {i}" if i > 1 else var)
    return "(" + " + ".join(terms) + ")"


def rho_def(k: int, a: list[Fraction]) -> str:
    poly = f"X ^ {k}" + "".join(
        f" + C {num(a[j])} * X ^ {j}" if j > 1 else (f" + C {num(a[1])} * X" if j == 1 else f" + C {num(a[0])}")
        for j in range(k - 1, -1, -1))
    return poly


def gen_k(k: int) -> list[str]:
    a, b = bdf(k)
    c = certificate(k)
    r = f"rho{k}"
    out = [f"/-! ## BDF{k}: the root condition -/", "",
           f"noncomputable def {r} : ℂ[X] := {rho_def(k, a)}", ""]
    q = c["q"]
    d = c["d"]
    qz = poly_in("z", q) if d >= 1 else "1"
    out += [f"theorem {r}_eval (z : ℂ) : {r}.eval z = (z - 1) * ({qz}) := by",
            f"  simp only [{r}, eval_add, eval_mul, eval_pow, eval_C, eval_X]", "  ring", ""]
    if d == 0:
        out += [f"theorem bdf{k}_roots (z : ℂ) (h : {r}.IsRoot z) : z = 1 ∨ ‖z‖ < 1 := by",
                f"  left", f"  rw [IsRoot.def, {r}_eval] at h", "  linear_combination h", ""]
    else:
        P = c["P"]
        ds, us = c["sos"]
        e = poly_in("z", q)
        f = poly_in("w", q)
        lhs = " + ".join("1" if i == 0 else (f"(z * w) ^ {i}" if i > 1 else "z * w") for i in range(d))
        sos = " + ".join(f"{num(ds[i])} * ({l_expr('z', i, us[i])} * {l_expr('w', i, us[i])})" for i in range(d))
        A = " + ".join((f"{num(P[i][d-1])} * w ^ {i+1}" if i + 1 > 1 else f"{num(P[i][d-1])} * w") for i in range(d)) \
            + f" - {num(P[d-1][d-1])} * ({f})"
        B = " + ".join((f"{num(P[d-1][j])} * z ^ {j+1}" if j + 1 > 1 else f"{num(P[d-1][j])} * z") for j in range(d))
        m_terms = " + ".join(f"{num(ds[i])} * m{i}" for i in range(d))
        out += [f"theorem bdf{k}_deflated_inside (z : ℂ) (hq : {e} = 0) : ‖z‖ < 1 := by",
                "  set w : ℂ := (starRingEnd ℂ) z with hw",
                f"  have hqw : {f} = 0 := by",
                "    have h := congrArg (starRingEnd ℂ) hq",
                "    simpa [hw, map_add, map_mul, map_pow, map_div₀, map_neg, map_ofNat, map_one, map_zero, map_natCast] using h",
                f"  have key : {lhs} = (1 - z * w) * ({sos}) := by",
                f"    linear_combination ({A}) * hq + ({B}) * hqw"]
        MAPS = "map_add, map_mul, map_pow, map_div₀, map_neg, map_ofNat, map_one, map_zero, map_natCast"
        for i in range(d):
            li_z, li_w = l_expr("z", i, us[i]), l_expr("w", i, us[i])
            out += [f"  have h{i} : {li_w} = (starRingEnd ℂ) {li_z} := by",
                    f"    simp [hw, {MAPS}]",
                    f"  have p{i} : {li_z} * {li_w} = ((Complex.normSq {li_z} : ℝ) : ℂ) := by",
                    f"    have := Complex.mul_conj {li_z}",
                    f"    rw [← h{i}] at this",
                    "    exact this"]
        out += ["  have hn : z * w = ((Complex.normSq z : ℝ) : ℂ) := Complex.mul_conj z"]
        for i in range(d):
            out.append(f"  rw [p{i}] at key")
        out += ["  rw [hn] at key"]
        lhs_r = " + ".join("1" if i == 0 else (f"(Complex.normSq z) ^ {i}" if i > 1 else "Complex.normSq z") for i in range(d))
        rhs_r = " + ".join(f"({ds[i].numerator} / {ds[i].denominator} : ℝ) * Complex.normSq {l_expr('z', i, us[i])}" for i in range(d))
        out += [f"  have real : ({lhs_r} : ℝ) = (1 - Complex.normSq z) * ({rhs_r}) := by",
                "    apply Complex.ofReal_injective",
                "    push_cast",
                "    linear_combination key",
                "  have hone : Complex.normSq (1 : ℂ) = 1 := by simp",
                "  rw [hone, mul_one] at real",
                "  have hn_nn : 0 ≤ Complex.normSq z := Complex.normSq_nonneg z"]
        for i in range(1, d):
            out.append(f"  have t{i} : 0 ≤ ({ds[i].numerator} / {ds[i].denominator} : ℝ) * Complex.normSq {l_expr('z', i, us[i])} := "
                       f"mul_nonneg (by norm_num) (Complex.normSq_nonneg _)")
        S = f"({ds[0].numerator} / {ds[0].denominator} : ℝ)" + "".join(
            f" + ({ds[i].numerator} / {ds[i].denominator} : ℝ) * Complex.normSq {l_expr('z', i, us[i])}" for i in range(1, d))
        out += ["  by_contra hge",
                "  push Not at hge",
                "  have hn1 : 1 ≤ Complex.normSq z := by",
                "    rw [Complex.normSq_eq_norm_sq]; nlinarith [norm_nonneg z]",
                f"  have hS : (0 : ℝ) < {S} := by",
                "    have : (0 : ℝ) < " + f"{ds[0].numerator} / {ds[0].denominator}" + " := by norm_num",
                "    linarith" if d == 1 else "    linarith [" + ", ".join(f"t{i}" for i in range(1, d)) + "]",
                f"  have hR : (1 - Complex.normSq z) * ({S}) ≤ 0 :=",
                "    mul_nonpos_of_nonpos_of_nonneg (by linarith) hS.le",
                "  have hL : (1 : ℝ) ≤ " + lhs_r + " := by",
                "    norm_num" if d == 1 else "    linarith [" + ", ".join([f"pow_nonneg hn_nn {i}" for i in range(2, d)] + ["hn_nn"]) + "]",
                "  linarith", ""]
        out += [f"theorem bdf{k}_roots (z : ℂ) (h : {r}.IsRoot z) : z = 1 ∨ ‖z‖ < 1 := by",
                f"  rw [IsRoot.def, {r}_eval] at h",
                "  rcases mul_eq_zero.1 h with h1 | h2",
                "  · left; linear_combination h1",
                f"  · right; exact bdf{k}_deflated_inside z h2", ""]
    out += [f"theorem bdf{k}_root_one_simple : (derivative {r}).eval 1 ≠ 0 := by",
            f"  norm_num [{r}, derivative_X_pow, derivative_C, derivative_mul]", ""]
    return out


def main() -> None:
    ks = [int(x) for x in sys.argv[2:]]
    path = Path(sys.argv[1])
    head = ["import Mathlib.Analysis.Complex.Polynomial.Basic",
            "import Mathlib.Algebra.Polynomial.Derivative",
            "import Mathlib.Tactic.Positivity", "import Mathlib.Tactic.Linarith", "",
            "/-!", "# The root condition for BDF1–6, by an exact Lyapunov certificate",
            "Generated by `scripts/kge_gen_stability_inside_lean.py`; see that file for the argument.", "-/", "",
            "set_option linter.unusedSimpArgs false", "set_option maxHeartbeats 1000000", "",
            "open Polynomial", "", "namespace ANSE.Alix.Stab", ""]
    body = []
    for k in ks:
        body += gen_k(k)
    text = "\n".join(head + body + ["end ANSE.Alix.Stab", ""])
    names = re.findall(r"^theorem ([A-Za-z0-9_']+)", text, flags=re.M)
    text += "\n".join(f"#print axioms ANSE.Alix.Stab.{n}" for n in names) + "\n"
    path.write_text(text)
    print(f"wrote {path}: {len(names)} theorems")


if __name__ == "__main__":
    main()
