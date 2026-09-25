theorem problem_5_gauss_bonnet_algebraic_core
    (R : ℝ) (_hR : 0 < R) :
    let K := 1 / (R ^ 2); let Area := 4 * Real.pi * (R ^ 2);
    K * Area = 4 * Real.pi := by
  intro K Area; dsimp [K, Area]; have hRsq : R ^ 2 ≠ 0 := by positivity; field_simp [hRsq]