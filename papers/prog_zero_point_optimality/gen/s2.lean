theorem lap_Q (m n x y : ℝ) (hy : y ≠ 0) :
    y ^ 2 * (2 * n ^ 2 / y + 2 * (m + n * x) ^ 2 / y ^ 3) = 2 * Q m n x y := ... -- proof elided

theorem grad_Q (m n x y : ℝ) (hy : y ≠ 0) :
    y ^ 2 * ((2 * n * (m + n * x) / y) ^ 2 + (n ^ 2 - (m + n * x) ^ 2 / y ^ 2) ^ 2) = (Q m n x y) ^ 2 := ... -- proof elided
