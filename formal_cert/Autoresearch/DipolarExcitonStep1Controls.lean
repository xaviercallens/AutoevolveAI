import Autoresearch.DipolarExcitonStep1

/-! Planted controls for the H1 stage-5 Step-1 module: `ctl1_sorry` and `ctl1_axiom` must be flagged by
`#print axioms` (`sorryAx`, the planted axiom); the claimed theorems must show only `propext`, `Classical.choice`,
`Quot.sound`. Also a wrong-sign statement that must NOT be provable is checked as a negative example below. -/

namespace AutoresearchDipolarStep1Controls

theorem ctl1_sorry : (1 : ℕ) = 2 := sorry

axiom ctl1_cheat : False

theorem ctl1_axiom : (1 : ℕ) = 2 := ctl1_cheat.elim

/-- Negative check: with the wrong sign of the cross term the in-plane form fails at r = 1, d = 1
(`2 (1 + 1/sqrt 2) ≠ g 1 1`), so `g_inplane` is not vacuous about the sign. -/
theorem ctl1_wrong_sign_false :
    ¬ (AutoresearchDipolar.g 1 ((1 : ℝ) ^ 2) = 2 * (1 / (1 : ℝ) + 1 / Real.sqrt ((1 : ℝ) ^ 2 + 1 ^ 2))) := by
  rw [AutoresearchDipolarStep1.g_inplane 1 1 one_pos]
  intro h
  have hs : 0 < 1 / Real.sqrt ((1 : ℝ) ^ 2 + 1 ^ 2) := by positivity
  linarith

end AutoresearchDipolarStep1Controls

#print axioms AutoresearchDipolarStep1Controls.ctl1_sorry
#print axioms AutoresearchDipolarStep1Controls.ctl1_axiom
#print axioms AutoresearchDipolarStep1Controls.ctl1_wrong_sign_false
#print axioms AutoresearchDipolarStep1.g_sqrt
#print axioms AutoresearchDipolarStep1.g_inplane
#print axioms AutoresearchDipolarStep1.g_inplane_pos
