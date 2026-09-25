theorem problem_92_kosterlitz_thouless_free_energy
    (U S T : ℝ) (h_vortex : U - T * S ≤ 0) :
    T * S - U ≥ 0 := by
  linarith