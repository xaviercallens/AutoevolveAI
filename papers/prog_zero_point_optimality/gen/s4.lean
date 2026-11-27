theorem gauss_f' (a u : ℝ) :
    HasDerivAt (fun v => Real.exp (-(Real.pi * a) * v)) (-(Real.pi * a) * Real.exp (-(Real.pi * a) * u)) u := ... -- proof elided

theorem gauss_h (a u : ℝ) :
    HasDerivAt (fun v => v ^ 2 * (-(Real.pi * a) * Real.exp (-(Real.pi * a) * v)))
      ((-2 * Real.pi * a * u + Real.pi ^ 2 * a ^ 2 * u ^ 2) * Real.exp (-(Real.pi * a) * u)) u := ... -- proof elided

noncomputable def m2f (a u : ℝ) : ℝ := (-4 * Real.pi * a + 4 * Real.pi ^ 2 * a ^ 2 * u) * Real.exp (-(Real.pi * a) * u)

noncomputable def m2f' (a u : ℝ) : ℝ :=
  (8 * Real.pi ^ 2 * a ^ 2 - 4 * Real.pi ^ 3 * a ^ 3 * u) * Real.exp (-(Real.pi * a) * u)

theorem m2_f' (a u : ℝ) : HasDerivAt (fun v => m2f a v) (m2f' a u) u := ... -- proof elided

theorem m2_h (a u : ℝ) :
    HasDerivAt (fun v => v ^ 2 * m2f' a v)
      ((16 * Real.pi ^ 2 * a ^ 2 * u - 20 * Real.pi ^ 3 * a ^ 3 * u ^ 2 + 4 * Real.pi ^ 4 * a ^ 4 * u ^ 3)
        * Real.exp (-(Real.pi * a) * u)) u := ... -- proof elided
