theorem problem_45_virial_bound_state_energy
    (T_avg V_avg E_tot : ℝ)
    (h_virial : 2 * T_avg + V_avg = 0)
    (h_energy : E_tot = T_avg + V_avg) :
    E_tot = -T_avg := by
  linarith