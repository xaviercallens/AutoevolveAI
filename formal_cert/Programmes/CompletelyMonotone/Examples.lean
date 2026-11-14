import Programmes.CompletelyMonotone.Bernstein

/-!
# Programme P3: further instances

* `inv_cm`: `t ↦ t⁻¹` is completely monotone; `inv_affine_cm`: `t ↦ (a t + b)⁻¹` (`a > 0`, `b ≥ 0`).
* `IsBernsteinOn.one_sub_exp`: `1 - e^{-a t}` (`a ≥ 0`) is Bernstein.
* `IsBernsteinOn.log_one_add`: `log (1 + t)` is Bernstein.
* `one_add_rpow_neg_cm`: `(1 + t)^{-s}` (`s ≥ 0`) is completely monotone (translation of `t^{-s}`).
-/

namespace ProgCM

open Set Filter Topology IsCompletelyMonotoneOn

theorem inv_cm : IsCompletelyMonotoneOn (fun t : ℝ => t⁻¹) :=
  (rpow_neg zero_le_one).congr' fun t _ => Real.rpow_neg_one t

theorem inv_affine_cm {a b : ℝ} (ha : 0 < a) (hb : 0 ≤ b) :
    IsCompletelyMonotoneOn (fun t : ℝ => (a * t + b)⁻¹) :=
  inv_cm.comp_affine ha hb

theorem one_add_rpow_neg_cm {s : ℝ} (hs : 0 ≤ s) : IsCompletelyMonotoneOn (fun t : ℝ => (t + 1) ^ (-s)) :=
  (rpow_neg hs).comp_add_const zero_le_one

namespace IsBernsteinOn

/-- `1 - e^{-a t}` is Bernstein for `a ≥ 0`. -/
theorem one_sub_exp {a : ℝ} (ha : 0 ≤ a) : IsBernsteinOn (fun t => 1 - Real.exp (-(a * t))) := by
  have hd : ∀ t : ℝ, HasDerivAt (fun t => 1 - Real.exp (-(a * t))) (a * Real.exp (-(a * t))) t := by
    intro t
    have h1 : HasDerivAt (fun t : ℝ => -(a * t)) (-a) t := by
      simpa using (hasDerivAt_id' t).const_mul (-a)
    have h := (h1.exp).const_sub 1
    convert h using 1
    ring
  refine ⟨by fun_prop, fun t ht => ?_, ?_⟩
  · have : Real.exp (-(a * t)) ≤ 1 := Real.exp_le_one_iff.mpr (neg_nonpos.mpr (mul_nonneg ha (le_of_lt ht)))
    show 0 ≤ 1 - Real.exp (-(a * t))
    linarith
  · refine ((exp_neg_mul ha).const_mul ha).congr' fun t _ => ?_
    exact ((hd t).deriv).symm

/-- `log (1 + t)` is Bernstein. -/
theorem log_one_add : IsBernsteinOn (fun t => Real.log (1 + t)) := by
  have hd : ∀ t : ℝ, 0 < t → HasDerivAt (fun t => Real.log (1 + t)) ((t + 1)⁻¹) t := by
    intro t ht
    have h := ((hasDerivAt_id' t).const_add 1).log (show (1 : ℝ) + t ≠ 0 from ne_of_gt (by linarith))
    convert h using 1
    rw [one_div, add_comm]
  have hmaps : MapsTo (fun t : ℝ => 1 + t) (Ioi 0) ({0}ᶜ) := fun t ht => by
    simp only [mem_Ioi] at ht
    simp only [mem_compl_iff, mem_singleton_iff]
    linarith
  refine ⟨Real.contDiffOn_log.comp (contDiffOn_const.add contDiffOn_id) hmaps,
    fun t ht => Real.log_nonneg (by linarith), ?_⟩
  refine (one_add_rpow_neg_cm zero_le_one).congr' fun t ht => ?_
  rw [(hd t ht).deriv]
  exact Real.rpow_neg_one (t + 1)

end IsBernsteinOn

/-- Example of subordination with `log (1 + t)`: `e^{-a log(1 + t)}` is completely monotone. -/
theorem exp_neg_log_one_add_cm {a : ℝ} (ha : 0 ≤ a) :
    IsCompletelyMonotoneOn (fun t => Real.exp (-(a * Real.log (1 + t)))) :=
  exp_neg_comp ha IsBernsteinOn.log_one_add (fun t ht => Real.log_pos (by linarith))

end ProgCM

#print axioms ProgCM.inv_cm
#print axioms ProgCM.inv_affine_cm
#print axioms ProgCM.one_add_rpow_neg_cm
#print axioms ProgCM.IsBernsteinOn.one_sub_exp
#print axioms ProgCM.IsBernsteinOn.log_one_add
#print axioms ProgCM.exp_neg_log_one_add_cm
