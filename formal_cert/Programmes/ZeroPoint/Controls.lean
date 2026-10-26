import Programmes.ZeroPoint.Basic

/-!
# P2 zero-point: planted controls (must be CAUGHT by the axiom gate; never import this file)

`ctl_sorry` and `ctl_axiom` "prove" the false identity `y² (Qₓₓ + Qᵧᵧ) = Q` (the factor 2 of `lap_Q` dropped) for all
`m n x y` with `y ≠ 0`. The file compiles with exit code 0; only `#print axioms` exposes the cheats (`sorryAx`,
resp. `ProgZeroPoint.ctl_cheat`). `lap_wrong_false` is an honest theorem showing that the planted statement is indeed
false (instance `m = 1, n = 0, x = 0, y = 1`, where `Q = 1` and `y² (Qₓₓ + Qᵧᵧ) = 2`).
-/

namespace ProgZeroPoint

theorem ctl_sorry : ∀ m n x y : ℝ, y ≠ 0 →
    y ^ 2 * (2 * n ^ 2 / y + 2 * (m + n * x) ^ 2 / y ^ 3) = Q m n x y := sorry

axiom ctl_cheat : False

theorem ctl_axiom : ∀ m n x y : ℝ, y ≠ 0 →
    y ^ 2 * (2 * n ^ 2 / y + 2 * (m + n * x) ^ 2 / y ^ 3) = Q m n x y := ctl_cheat.elim

theorem lap_wrong_false : ¬ (∀ m n x y : ℝ, y ≠ 0 →
    y ^ 2 * (2 * n ^ 2 / y + 2 * (m + n * x) ^ 2 / y ^ 3) = Q m n x y) := by
  intro h
  have := h 1 0 0 1 one_ne_zero
  norm_num [Q] at this

end ProgZeroPoint

#print axioms ProgZeroPoint.ctl_sorry
#print axioms ProgZeroPoint.ctl_axiom
#print axioms ProgZeroPoint.lap_wrong_false
