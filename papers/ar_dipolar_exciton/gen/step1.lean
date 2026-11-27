theorem g_sqrt (d t : ℝ) (ht : 0 < t) :
    AutoresearchDipolar.g d t = 2 * (1 / Real.sqrt t - 1 / Real.sqrt (t + d ^ 2)) := -- proof elided

theorem g_inplane (d r : ℝ) (hr : 0 < r) :
    AutoresearchDipolar.g d (r ^ 2) = 2 * (1 / r - 1 / Real.sqrt (r ^ 2 + d ^ 2)) := -- proof elided

theorem g_inplane_pos (d r : ℝ) (hd : d ≠ 0) (hr : 0 < r) : 0 < AutoresearchDipolar.g d (r ^ 2) := -- proof elided
