import Mathlib.Tactic

/-! N2 negative control (must FAIL to compile): claim that the Gaussian a = 2 enclosure's upper endpoint
`M_hi = 4463084749303/10^12` (runs/negctl_g2_N64.json) is negative. -/

theorem gauss2_false_cert : (4463084749303 / 1000000000000 : ℝ) < 0 := by
  norm_num
