import Mathlib.Tactic

/-! M1 negative control (must FAIL to compile): claim that the Gaussian a = 2 upper endpoint produced by the M1
certifier, `M_hi = 4463084749303/10^12` (`results/proposal4/2026-10-27/M1/data/negctl_gauss2.json`), is negative. -/

theorem m1_gauss2_false_cert : (4463084749303 / 1000000000000 : ℝ) < 0 := by
  norm_num
