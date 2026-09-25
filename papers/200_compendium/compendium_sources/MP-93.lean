theorem problem_93_lindblad_trace_preservation
    (tr_jump tr_anti : ℝ)
    (h_cyclic : tr_jump = tr_anti) :
    tr_jump - (1 / 2 : ℝ) * (tr_anti + tr_anti) = 0 := by
  linarith