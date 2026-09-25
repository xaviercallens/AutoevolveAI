theorem problem_43_klein_gordon_energy_momentum
    (E p_norm m : ℝ) (h_onshell : E^2 - p_norm^2 = m^2) :
    E^2 = p_norm^2 + m^2 := by
  linarith