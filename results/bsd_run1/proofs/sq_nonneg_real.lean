import Mathlib.GroupTheory.Index
import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Data.Real.Basic
import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith

theorem sq_nonneg_real (x : ℝ) : 0 ≤ x ^ 2 := by
  simp [sq]
  <;> nlinarith [sq_nonneg x]

#print axioms sq_nonneg_real
