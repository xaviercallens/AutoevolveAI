import Programmes.CompletelyMonotone.Examples

/-!
# Programme P3: mathematical negative controls (each hypothesis of the library is needed / the definitions bite)

* `cos_not_cm`: the definition is not vacuous (`cos π < 0`).
* `sqrt_not_cm`: `√` is Bernstein but not completely monotone; `expNeg_not_bernstein`: `e^{-t}` is completely
  monotone but not Bernstein. So the two classes are distinct.
* Subordination needs the inner function to be Bernstein: `t ↦ t⁻¹` is completely monotone and positive but not
  Bernstein (`inv_not_bernstein`), and `e^{-1/t}` is not completely monotone (`expNegInv_not_cm`).
* Subordination needs `ψ > 0` (junk values at `0`): `junk` is completely monotone, `0` is Bernstein, `junk ∘ 0` is
  not completely monotone (`junk_comp_zero_not_cm`).
* Mixtures need nonnegative weights: `e^{-t} - 2 e^{-2t}` is not completely monotone (`signedMix_not_cm`).
-/

namespace ProgCM

open Set Filter Topology IsCompletelyMonotoneOn

theorem cos_not_cm : ¬ IsCompletelyMonotoneOn Real.cos := by
  intro h
  have := h.nonneg Real.pi_pos
  rw [Real.cos_pi] at this
  norm_num at this

theorem sqrt_not_cm : ¬ IsCompletelyMonotoneOn Real.sqrt := by
  intro h
  have h1 := h.sign 1 one_pos
  rw [iteratedDeriv_one, (Real.hasDerivAt_sqrt one_ne_zero).deriv, Real.sqrt_one] at h1
  norm_num at h1

theorem expNeg_not_bernstein : ¬ IsBernsteinOn (fun t => Real.exp (-(1 * t))) := by
  intro h
  have h1 := h.2.2.nonneg one_pos
  have hd : HasDerivAt (fun t : ℝ => Real.exp (-(1 * t))) (Real.exp (-(1 * (1 : ℝ))) * -(1 * 1)) 1 :=
    (((hasDerivAt_id (1 : ℝ)).const_mul 1).neg).exp
  rw [hd.deriv] at h1
  have hp := Real.exp_pos (-(1 * (1 : ℝ)))
  have e : Real.exp (-(1 * (1 : ℝ))) * -(1 * 1) = -Real.exp (-(1 * (1 : ℝ))) := by ring
  rw [e] at h1
  linarith

theorem inv_not_bernstein : ¬ IsBernsteinOn (fun t : ℝ => t⁻¹) := by
  intro h
  have h1 := h.2.2.nonneg one_pos
  rw [(hasDerivAt_inv (one_ne_zero : (1 : ℝ) ≠ 0)).deriv] at h1
  norm_num at h1

theorem expNegInv_not_cm : ¬ IsCompletelyMonotoneOn (fun t : ℝ => Real.exp (-(1 * t⁻¹))) := by
  intro h
  have h1 := h.sign 1 one_pos
  have hd : HasDerivAt (fun t : ℝ => Real.exp (-(1 * t⁻¹)))
      (Real.exp (-(1 * (1 : ℝ)⁻¹)) * -(1 * -((1 : ℝ) ^ 2)⁻¹)) 1 :=
    (((hasDerivAt_inv (one_ne_zero : (1 : ℝ) ≠ 0)).const_mul 1).neg).exp
  rw [iteratedDeriv_one, hd.deriv] at h1
  have hp := Real.exp_pos (-(1 * (1 : ℝ)⁻¹))
  have e : (-1 : ℝ) ^ 1 * (Real.exp (-(1 * (1 : ℝ)⁻¹)) * -(1 * -((1 : ℝ) ^ 2)⁻¹)) =
      -Real.exp (-(1 * (1 : ℝ)⁻¹)) := by ring
  rw [e] at h1
  linarith

/-- A completely monotone function whose junk value at `0` is negative. -/
noncomputable def junk (t : ℝ) : ℝ := if 0 < t then t⁻¹ else -1

theorem junk_cm : IsCompletelyMonotoneOn junk :=
  inv_cm.congr' fun t ht => by simp [junk, ht]

theorem zero_bernstein : IsBernsteinOn (fun _ => (0 : ℝ)) := by
  simpa using IsBernsteinOn.affine (le_refl (0 : ℝ)) (le_refl (0 : ℝ))

theorem junk_comp_zero_not_cm : ¬ IsCompletelyMonotoneOn (fun t => junk ((fun _ : ℝ => (0 : ℝ)) t)) := by
  intro h
  have := h.nonneg one_pos
  simp [junk] at this
  linarith

theorem signedMix_not_cm : ¬ IsCompletelyMonotoneOn AutoresearchKeldysh.signedMix :=
  fun h => AutoresearchKeldysh.signedMix_not_admissible h.admissible

end ProgCM

#print axioms ProgCM.cos_not_cm
#print axioms ProgCM.sqrt_not_cm
#print axioms ProgCM.expNeg_not_bernstein
#print axioms ProgCM.inv_not_bernstein
#print axioms ProgCM.expNegInv_not_cm
#print axioms ProgCM.junk_cm
#print axioms ProgCM.zero_bernstein
#print axioms ProgCM.junk_comp_zero_not_cm
#print axioms ProgCM.signedMix_not_cm
