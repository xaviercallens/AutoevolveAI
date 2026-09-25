theorem problem_36_planck_radiation_positivity
    (hbar nu c _kB _T : ℝ)
    (hh : 0 < hbar) (hnu : 0 < nu) (hc : 0 < c) (_hk : 0 < _kB) (_hT : 0 < _T)
    (denom : ℝ) (h_denom : 0 < denom) :
    0 < (2 * hbar * nu^3 / c^2) / denom := by
  have h_num : 0 < 2 * hbar * nu^3 / c^2 := by positivity
  exact div_pos h_num h_denom