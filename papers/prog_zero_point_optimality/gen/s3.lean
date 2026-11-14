theorem lap_comp (m n x y f1 f2 : ℝ) (hy : y ≠ 0) :
    y ^ 2 * (f2 * ((2 * n * (m + n * x) / y) ^ 2 + (n ^ 2 - (m + n * x) ^ 2 / y ^ 2) ^ 2)
        + f1 * (2 * n ^ 2 / y + 2 * (m + n * x) ^ 2 / y ^ 3))
      = (Q m n x y) ^ 2 * f2 + 2 * Q m n x y * f1 := ... -- proof elided
