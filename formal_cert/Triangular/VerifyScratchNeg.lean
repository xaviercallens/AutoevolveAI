import Triangular.Riesz

open OAI.AtomicTriangular

-- negative control (a'): the producer's proof of riesz_admissible, transplanted verbatim to s = -2
theorem ctl_a_sameproof : OAI.TriangularUniversal.AdmissiblePotential (TriangularRiesz.riesz (-2)) := by
  refine ⟨?_, ?_, ?_⟩
  · intro x hx
    exact (Real.contDiffAt_rpow_const_of_ne (ne_of_gt hx)).contDiffWithinAt
  · intro t ht
    exact (Real.rpow_pos_of_pos ht _).le
  · intro r t ht
    have ha : 0 < (-2:ℝ) / 2 := by positivity
    rw [iteratedDeriv_eq_iterate]
    unfold TriangularRiesz.riesz
    rw [Real.iter_deriv_rpow_const]
    have hasc := ascPochhammer_eval_neg_eq_descPochhammer (R := ℝ) (-((-2:ℝ) / 2)) r
    rw [neg_neg] at hasc
    have hdesc : (descPochhammer ℝ r).eval (-((-2:ℝ) / 2)) = (-1) ^ r * (ascPochhammer ℝ r).eval ((-2:ℝ) / 2) := by
      have h1 : ((-1 : ℝ) ^ r) * ((-1) ^ r) = 1 := by rw [← mul_pow]; norm_num
      calc (descPochhammer ℝ r).eval (-((-2:ℝ) / 2))
          = ((-1) ^ r * (-1) ^ r) * (descPochhammer ℝ r).eval (-((-2:ℝ) / 2)) := by rw [h1, one_mul]
        _ = (-1) ^ r * (ascPochhammer ℝ r).eval ((-2:ℝ) / 2) := by rw [hasc]; ring
    rw [hdesc]
    have hpos := ascPochhammer_pos r ((-2:ℝ) / 2) ha
    have hpow := Real.rpow_pos_of_pos ht (-((-2:ℝ) / 2) - r)
    have h1 : ((-1 : ℝ) ^ r) * ((-1) ^ r) = 1 := by rw [← mul_pow]; norm_num
    calc (0 : ℝ) ≤ (ascPochhammer ℝ r).eval ((-2:ℝ) / 2) * t ^ (-((-2:ℝ) / 2) - r) := by positivity
      _ = (-1) ^ r * ((-1) ^ r * (ascPochhammer ℝ r).eval ((-2:ℝ) / 2) * t ^ (-((-2:ℝ) / 2) - r)) := by
        rw [← mul_assoc, ← mul_assoc, h1, one_mul]
