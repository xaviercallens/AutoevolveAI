theorem problem_55_jarzynski_work_dissipation
    (W_avg Delta_F : ℝ) (h_diss : 0 ≤ W_avg - Delta_F) :
    Delta_F ≤ W_avg := by
  linarith