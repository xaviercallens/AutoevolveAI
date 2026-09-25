theorem problem_49_bekenstein_bound_nonneg
    (kB R E hbar c : ℝ)
    (hk : 0 < kB) (hR : 0 ≤ R) (hE : 0 ≤ E) (hh : 0 < hbar) (hc : 0 < c) :
    0 ≤ (2 * Real.pi * kB * R * E) / (hbar * c) := by
  have hpi : 0 < Real.pi := Real.pi_pos
  positivity