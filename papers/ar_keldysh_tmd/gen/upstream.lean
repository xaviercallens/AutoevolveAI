def AdmissiblePotential (g : ℝ → ℝ) : Prop :=
  ContDiffOn ℝ (⊤ : ℕ∞) g (Set.Ioi 0) ∧
  (∀ t : ℝ, 0 < t → 0 ≤ g t) ∧
  ∀ (r : ℕ) (t : ℝ), 0 < t → 0 ≤ (-1 : ℝ) ^ r * iteratedDeriv r g t

theorem universal_energy_minimum (g : ℝ → ℝ) (C : Set Plane)
    (hg : AdmissiblePotential g) (_hC : LocallyFinite C) (hd : DensityOne C) :
    latticeEnergy g ≤ energy g C ∧ latticeEnergy g = energy g A := -- proof elided
