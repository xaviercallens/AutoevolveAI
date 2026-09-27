import Mathlib.GroupTheory.Index
import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Data.Real.Basic
import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith

theorem two_dvd_consec (n : ℕ) : 2 ∣ n * (n + 1) := by
  have h₁ : 2 ∣ n * (n + 1) := by
    have h₁ : n * (n + 1) % 2 = 0 := by
      have h₁ : n % 2 = 0 ∨ n % 2 = 1 := by omega
      rcases h₁ with (h₁ | h₁) <;> simp [h₁, Nat.mul_mod, Nat.add_mod]
    exact Nat.dvd_of_mod_eq_zero h₁
  exact h₁

#print axioms two_dvd_consec
