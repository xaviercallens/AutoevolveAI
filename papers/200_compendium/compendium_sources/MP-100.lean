theorem problem_100_autopoietic_energy_descent
    (L_p L_c T_p T_c gamma : ℝ)
    (hL : L_c ≤ L_p) (hT : T_c ≤ T_p) (hgamma : 0 ≤ gamma) :
    L_c + gamma * T_c ≤ L_p + gamma * T_p := by
  have h_time : gamma * T_c ≤ gamma * T_p := mul_le_mul_of_nonneg_left hT hgamma
  linarith