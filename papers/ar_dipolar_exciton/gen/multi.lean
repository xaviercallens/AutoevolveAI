theorem shiftDiff_admissible {s c : ℝ} (hs : 0 < s) (hc : 0 ≤ c) : AdmissiblePotential (shiftDiff s c) := -- proof elided

lemma admissible_const_mul {f : ℝ → ℝ} (hf : AdmissiblePotential f) {k : ℝ} (hk : 0 ≤ k) :
    AdmissiblePotential (fun t => k * f t) := -- proof elided

lemma g_eq_shiftDiff (d : ℝ) : AutoresearchDipolar.g d = fun t => 2 * shiftDiff 1 (d ^ 2) t := -- proof elided

theorem dipolar_admissible_all (d : ℝ) : AdmissiblePotential (AutoresearchDipolar.g d) := -- proof elided

theorem shiftDiff_neg_of_neg {s c : ℝ} (hs : 0 < s) (hc : c < 0) : shiftDiff s c (-2 * c) < 0 := -- proof elided

theorem shiftDiff_not_admissible_of_neg {s c : ℝ} (hs : 0 < s) (hc : c < 0) :
    ¬ AdmissiblePotential (shiftDiff s c) := -- proof elided

theorem triangular_shiftDiff_optimal {s c : ℝ} (hs : 0 < s) (hc : 0 ≤ c) (C : Set Plane) (hC : LocallyFinite C)
    (hdens : DensityOne C) : latticeEnergy (shiftDiff s c) ≤ energy (shiftDiff s c) C := -- proof elided
