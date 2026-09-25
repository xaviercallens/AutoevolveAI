theorem problem_40_continuity_charge_conservation
    (Q_dot Flux : ℝ) (h_cont : Q_dot + Flux = 0) (h_isolated : Flux = 0) :
    Q_dot = 0 := by
  linarith