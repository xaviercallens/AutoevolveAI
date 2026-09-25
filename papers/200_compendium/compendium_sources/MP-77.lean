theorem problem_77_tknn_integer_quantization
    (n : ℤ) (e_charge h_planck sigma_xy : ℝ)
    (he : e_charge ≠ 0) (hh : h_planck ≠ 0)
    (h_tknn : sigma_xy = (n : ℝ) * (e_charge ^ 2 / h_planck)) :
    sigma_xy * (h_planck / e_charge ^ 2) = (n : ℝ) := by
  rw [h_tknn]
  have he2 : e_charge ^ 2 ≠ 0 := pow_ne_zero 2 he
  field_simp