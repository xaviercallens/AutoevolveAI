noncomputable def Q (m n x y : ℝ) : ℝ := ((m + n * x) ^ 2 + n ^ 2 * y ^ 2) / y

theorem hasDerivAt_Q_x (m n x y : ℝ) :
    HasDerivAt (fun t => Q m n t y) (2 * n * (m + n * x) / y) x := ... -- proof elided

theorem hasDerivAt_Q_y (m n x y : ℝ) (hy : y ≠ 0) :
    HasDerivAt (fun t => Q m n x t) (n ^ 2 - (m + n * x) ^ 2 / y ^ 2) y := ... -- proof elided

theorem hasDerivAt_Qx_x (m n x y : ℝ) :
    HasDerivAt (fun t => 2 * n * (m + n * t) / y) (2 * n ^ 2 / y) x := ... -- proof elided

theorem hasDerivAt_Qy_y (m n x y : ℝ) (hy : y ≠ 0) :
    HasDerivAt (fun t => n ^ 2 - (m + n * x) ^ 2 / t ^ 2) (2 * (m + n * x) ^ 2 / y ^ 3) y := ... -- proof elided
