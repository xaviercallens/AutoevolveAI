theorem cos_not_cm : ¬ IsCompletelyMonotoneOn Real.cos := -- proof elided

theorem sqrt_not_cm : ¬ IsCompletelyMonotoneOn Real.sqrt := -- proof elided

theorem expNeg_not_bernstein : ¬ IsBernsteinOn (fun t => Real.exp (-(1 * t))) := -- proof elided

theorem expNegInv_not_cm : ¬ IsCompletelyMonotoneOn (fun t : ℝ => Real.exp (-(1 * t⁻¹))) := -- proof elided

theorem junk_comp_zero_not_cm : ¬ IsCompletelyMonotoneOn (fun t => junk ((fun _ : ℝ => (0 : ℝ)) t)) := -- proof elided

theorem signedMix_not_cm : ¬ IsCompletelyMonotoneOn AutoresearchKeldysh.signedMix := -- proof elided
