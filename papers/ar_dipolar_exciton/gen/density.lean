theorem triangular_dipolar_optimal_any_density {d : ℝ} (hd : 0 < d) {ρ : ℝ} (hρ : 0 < ρ) :
    LocallyFinite ((Real.sqrt ρ)⁻¹ • A) ∧ TriangularDensity.DensityRho ρ ((Real.sqrt ρ)⁻¹ • A) ∧
      ∀ C : Set Plane, LocallyFinite C → TriangularDensity.DensityRho ρ C →
        energy (AutoresearchDipolar.g d) ((Real.sqrt ρ)⁻¹ • A) ≤ energy (AutoresearchDipolar.g d) C := -- proof elided

lemma g_scaled_le (d : ℝ) {ρ : ℝ} (hρ : 0 < ρ) {t : ℝ} (ht : 0 < t) :
    AutoresearchDipolar.g d (ρ⁻¹ * t) ≤ (d ^ 2 * (ρ⁻¹) ^ (-((3 : ℝ) / 2))) * riesz 3 t := -- proof elided

theorem latticeEnergy_dipolar_scaled_lt_top (d : ℝ) {ρ : ℝ} (hρ : 0 < ρ) :
    latticeEnergy (fun t => AutoresearchDipolar.g d (ρ⁻¹ * t)) < ⊤ := -- proof elided

theorem energy_dipolar_any_density_lt_top {d : ℝ} (hd : 0 < d) {ρ : ℝ} (hρ : 0 < ρ) :
    energy (AutoresearchDipolar.g d) ((Real.sqrt ρ)⁻¹ • A) < ⊤ := -- proof elided
