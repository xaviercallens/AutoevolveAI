theorem sBog_sq {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k ^ 2 = k ^ 2 / (ks ^ 2 + k ^ 2) := ... -- proof elided

theorem sBog_le_sqrt {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k ≤ Real.sqrt (k / (2 * ks)) := by
  rw [← Real.sqrt_sq (sBog_pos hhc hk hks).le]
  apply Real.sqrt_le_sqrt
  rw [sBog_sq hhc hk hks, div_le_div_iff₀ (by positivity) (by positivity)]
  nlinarith [mul_nonneg hk.le (sq_nonneg (k - ks))]
