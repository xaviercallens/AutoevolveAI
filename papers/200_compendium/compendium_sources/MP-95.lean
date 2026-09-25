theorem problem_95_berry_phase_invariance
    (gamma : ℝ) :
    Real.cos (gamma + 2 * Real.pi) = Real.cos gamma :=
  Real.cos_add_two_pi gamma