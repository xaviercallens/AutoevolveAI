theorem dipolar_admissible {d : ℝ} (_hd : 0 < d) : AdmissiblePotential (g d) := -- proof elided

theorem triangular_dipolar_optimal {d : ℝ} (hd : 0 < d) (C : Set Plane) (hC : LocallyFinite C)
    (hdens : DensityOne C) : latticeEnergy (g d) ≤ energy (g d) C := -- proof elided

theorem h_neg_at {d : ℝ} (hd : 0 < d) : h d (d ^ 2) < 0 := -- proof elided

theorem h_not_admissible {d : ℝ} (hd : 0 < d) : ¬ AdmissiblePotential (h d) := -- proof elided

lemma diff_le (c : ℝ) (hc : 0 ≤ c) {t : ℝ} (ht : 0 < t) :
    t ^ (-(1 / 2 : ℝ)) - (t + c) ^ (-(1 / 2 : ℝ)) ≤ c / 2 * t ^ (-(3 / 2 : ℝ)) := -- proof elided

lemma g_le (d : ℝ) {t : ℝ} (ht : 0 < t) : g d t ≤ d ^ 2 * riesz 3 t := -- proof elided

theorem latticeEnergy_dipolar_lt_top (d : ℝ) : latticeEnergy (g d) < ⊤ := -- proof elided
