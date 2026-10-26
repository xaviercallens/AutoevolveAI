/-
Annexe C, exemple 3 : récurrence, simp et decide.
La somme 0 + 1 + ... + (n-1), multipliée par 2, vaut n (n - 1), et un calcul fini décidé par le noyau.
-/
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Tactic.Ring

open Finset

-- Récurrence sur n ; `simp` déplie la somme, `ring` conclut.
theorem double_somme (n : ℕ) : 2 * (∑ i ∈ range n, i) + n = n * n := by
  induction n with
  | zero => simp
  | succ k ih =>
    rw [sum_range_succ]
    ring_nf
    ring_nf at ih
    omega

-- decide : la proposition est décidable et close ; le noyau l'évalue.
theorem petit_calcul : (∑ i ∈ range 11, i) = 55 := by
  decide

-- simp avec une liste de lemmes : réécriture jusqu'à une forme normale.
theorem simp_exemple (l : List ℕ) : (l ++ []).length = l.length := by
  simp

#print axioms double_somme
#print axioms petit_calcul
#print axioms simp_exemple
