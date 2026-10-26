/-- The charges `+1, -2, +1` in layers `0, d, 2d` give shifts `0, d², 4d²` in `t = r²`; unit case `d = 1`. -/
noncomputable def quadrupole (t : ℝ) : ℝ := t ^ (-(1 / 2 : ℝ)) - 2 * (t + 1) ^ (-(1 / 2 : ℝ)) + (t + 4) ^ (-(1 / 2 : ℝ))

/-- **Negative result.** The (unit) charge-quadrupole combination is not completely monotone. -/
theorem quadrupole_not_cm : ¬ IsCompletelyMonotoneOn quadrupole := fun h => by
  have := h.nonneg (t := 3) (by norm_num)
  linarith [quadrupole_neg_at_three]

/-- **Negative result at every layer spacing** `c > 0`: reduced to `c = 1` by the scaling `t ↦ c t`
(`comp_affine`). -/
theorem quadrupoleC_not_cm {c : ℝ} (hc : 0 < c) : ¬ IsCompletelyMonotoneOn (quadrupoleC c) := -- proof elided

/-- Pair interaction of two aligned `+1, -2, +1` quadrupoles for a pair potential `f` (in `t = r²`, `c = d²`). -/
noncomputable def quadrupolarPair (f : ℝ → ℝ) (c t : ℝ) : ℝ := 2 * (3 * f t - 4 * f (t + c) + f (t + 4 * c))

/-- **Quadrupolar exciton-exciton interaction** is completely monotone for every completely monotone pair potential. -/
theorem quadrupolarPair_cm {f : ℝ → ℝ} (hf : IsCompletelyMonotoneOn f) {c : ℝ} (hc : 0 ≤ c) :
    IsCompletelyMonotoneOn (quadrupolarPair f c) := by
  have hg := hf.sub_comp_add_const hc
  have h1 := hg.sub_comp_add_const hc
  have h2 := hg.sub_comp_add_const (by linarith : (0 : ℝ) ≤ 2 * c)
  have h3 := hg.sub_comp_add_const (by linarith : (0 : ℝ) ≤ 3 * c)
  refine (((h1.add h2).add h3).const_mul zero_le_two).congr' fun t _ => ?_
  simp only [quadrupolarPair, Pi.add_apply]
  ring_nf

/-- Unscreened (Coulomb pair potential `t^{-1/2}`) quadrupolar exciton interaction, `c = d²`. -/
theorem quadrupolarCoulomb_cm (d : ℝ) :
    IsCompletelyMonotoneOn (quadrupolarPair (fun t => t ^ (-(1 / 2 : ℝ))) (d ^ 2)) :=
  quadrupolarPair_cm (rpow_neg (by norm_num : (0 : ℝ) ≤ 1 / 2)) (sq_nonneg d)
