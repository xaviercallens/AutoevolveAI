/-
Annexe C, exemple 4 : lire un énoncé de Mathlib, puis s'en servir.
#check affiche l'énoncé exact (hypothèses implicites comprises) ; on l'applique ensuite comme une fonction.
-/
import Mathlib.Analysis.Complex.Exponential
import Mathlib.Tactic.Linarith

#check @Real.exp_pos
#check @Real.add_one_le_exp
#check @abs_sub_comm

-- On applique les énoncés lus ci-dessus.
theorem exp_moins_positif (x : ℝ) : 0 < Real.exp (-x) := Real.exp_pos (-x)

theorem exp_minore (x : ℝ) (hx : 0 ≤ x) : 1 ≤ Real.exp x := by
  have h := Real.add_one_le_exp x
  linarith

#print axioms exp_moins_positif
#print axioms exp_minore
