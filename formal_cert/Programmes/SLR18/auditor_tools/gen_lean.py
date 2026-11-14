#!/usr/bin/env python3
"""Generate a Lean 4 file proving the covering statement for one certificate.

Statement: for all real t there are i and an integer k with |s_i + v_i t - k| < 1/(n+1),
plus injectivity and positivity of v. Proof: reduce t to u = t - floor t in [0,1), split [0,1) by a chain of
arc right endpoints b_1 < ... < b_m (computed here in exact rationals, untrusted: the kernel re-checks every case).
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from math import ceil, floor


def chain(v: list[int], s: list[F], delta: F) -> list[tuple[int, int, F, F]]:
    arcs = []
    for i, (vi, si) in enumerate(zip(v, s)):
        for k in range(floor(si - delta) - 1, ceil(si + vi + delta) + 2):
            c = (k - si) / vi
            lo, hi = c - delta / vi, c + delta / vi
            if hi > 0 and lo < 1:
                arcs.append((i, k, lo, hi))
    out = []
    cur = F(0)
    first = True
    while True:
        cand = [a for a in arcs if a[2] < cur and a[3] > cur]
        if not cand:
            raise SystemExit(f"gap at {cur}")
        best = max(cand, key=lambda a: a[3])
        out.append(best)
        if best[3] >= 1:
            return out
        cur = best[3]


def q(x: F) -> str:
    return f"({x.numerator} / {x.denominator} : ℝ)" if x.denominator != 1 else f"({x.numerator} : ℝ)"


def main() -> None:
    cert = json.load(open(sys.argv[1]))
    name = sys.argv[2]
    n, v, a, D = cert["n"], cert["v"], cert["a"], cert["D"]
    delta = F(1, n + 1)
    s = [F(x, D) for x in a]
    ch = chain(v, s, delta)
    L = []
    L.append("import Mathlib.Tactic")
    L.append("")
    L.append("set_option linter.unusedSimpArgs false")
    L.append("set_option maxHeartbeats 0")
    L.append(f"namespace SLRAudit.{name}")
    L.append("")
    L.append(f"/-- velocities of certificate n = {n} -/")
    L.append(f"def v : Fin {n} → ℕ := ![{', '.join(map(str, v))}]")
    L.append(f"/-- shifts s_i = a_i / {D} -/")
    L.append(f"def s : Fin {n} → ℚ := ![{', '.join(f'{x}/{D}' for x in a)}]")
    L.append("")
    L.append("theorem v_injective : Function.Injective v := by decide")
    L.append("theorem v_pos : ∀ i, 0 < v i := by decide")
    L.append("")
    L.append(f"/-- covering: for every real t some runner is within distance < 1/{n+1} of an integer. -/")
    L.append(f"theorem cover : ∀ t : ℝ, ∃ i : Fin {n}, ∃ k : ℤ, |((s i : ℚ) : ℝ) + ((v i : ℕ) : ℝ) * t - (k : ℝ)| < 1 / {n+1} := by")
    L.append("  intro t")
    L.append("  have h0 : (0 : ℝ) ≤ t - ⌊t⌋ := by have := Int.floor_le t; linarith")
    L.append("  have h1 : t - ⌊t⌋ < (1 : ℝ) := by have := Int.lt_floor_add_one t; linarith")
    prev = "h0"
    for j, (i, k, lo, hi) in enumerate(ch):
        last = j == len(ch) - 1
        vi = v[i]
        wit = f"  refine ⟨{i}, {k} + {vi} * ⌊t⌋, ?_⟩"
        tac = [wit,
               "  simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *",
               "  rw [abs_lt]",
               "  push_cast",
               f"  constructor <;> linarith only [{prev}, {'h1' if last else f'c{j}'}]"]
        if last:
            L += tac
        else:
            L.append(f"  rcases lt_or_ge (t - ⌊t⌋) {q(hi)} with c{j} | c{j}")
            L.append("  ·" + tac[0][1:])
            L += ["   " + x[1:] for x in tac[1:]]
            prev = f"c{j}"
    L.append("")
    L.append("#print axioms cover")
    L.append("#print axioms v_injective")
    L.append("#print axioms v_pos")
    L.append(f"end SLRAudit.{name}")
    print("\n".join(L))
    print(f"-- chain length {len(ch)}", file=sys.stderr)


if __name__ == "__main__":
    main()
