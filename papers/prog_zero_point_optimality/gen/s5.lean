noncomputable def rho : ℂ := ⟨1 / 2, Real.sqrt 3 / 2⟩

theorem rho_sq : rho ^ 2 = rho - 1 := ... -- proof elided

theorem sqrt3_half_sq : (Real.sqrt 3 / 2) ^ 2 = 3 / 4 := ... -- proof elided

theorem gamma_fixes_rho : (rho - 1) / rho = rho := by
  rw [← rho_sq, sq, mul_div_assoc, div_self rho_ne_zero, mul_one]

theorem rho_sq_mul_rot : rho ^ 2 * (⟨-1 / 2, -(Real.sqrt 3 / 2)⟩ : ℂ) = 1 := ... -- proof elided

theorem hasDerivAt_gamma : HasDerivAt (fun τ : ℂ => (τ - 1) / τ) (1 / rho ^ 2) rho := ... -- proof elided
