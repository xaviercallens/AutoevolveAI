theorem negPi_admissibleBg_iff (b : ℝ) : AdmissibleBg b ∅ negPi ↔ b = 2 * Real.pi := -- proof elided
theorem negPi_admissible : Admissible ∅ negPi := -- proof elided
theorem negPi_not_admissible_noBackground : ¬ AdmissibleBg 0 ∅ negPi := -- proof elided
theorem negPi_not_admissible_wrongSign : ¬ AdmissibleBg (-(2 * Real.pi)) ∅ negPi := -- proof elided
theorem negPi_hasLocalEnergy {χ : Plane → ℝ} (hχ : Continuous χ) (hs : HasCompactSupport χ) :
    HasLocalEnergy ∅ negPi χ ((1 / 2) * ∫ x, χ x * ‖negPi x‖ ^ 2) := -- proof elided
theorem competitor_nonvacuous {χ : ℝ → Plane → ℝ} (hχ : IsSquareCutoffFamily χ) :
    ∃ (Λ : Set Plane) (E : Plane → Plane) (w : ℝ → ℝ), Admissible Λ E ∧
      ∀ R : ℝ, 1 < R → HasLocalEnergy Λ E (χ R) (w R) := -- proof elided
theorem triBasis_covolume : triScale ^ 2 * (e₁ 0 * e₂ 1 - e₁ 1 * e₂ 0) = 1 := -- proof elided
theorem ssBasis_covolume {m : ℝ} (hm : 0 < m) :
    Real.sqrt (4 * Real.pi / (m * Real.sqrt 3)) ^ 2 * (e₁ 0 * e₂ 1 - e₁ 1 * e₂ 0) = 2 * Real.pi / m := -- proof elided
theorem exists_squareCutoffFamily : ∃ χ, IsSquareCutoffFamily χ := -- proof elided
theorem exists_ballCutoffFamily : ∃ χ, IsBallCutoffFamily χ := -- proof elided
