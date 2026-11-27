lemma exists_le_weighted_mean {ι : Type*} [Fintype ι] (w l : ι → ℝ) (hw : ∀ i, 0 ≤ w i)
    (hpos : 0 < ∑ i, w i) : ∃ i, 0 < w i ∧ l i * ∑ j, w j ≤ ∑ j, w j * l j := ... -- proof elided

lemma rayleigh_expansion (hH : H.IsSymmetric) (x : E) :
    (⟪x, H x⟫_ℂ).re = ∑ i, ‖⟪hH.eigenvectorBasis rfl i, x⟫_ℂ‖ ^ 2 * hH.eigenvalues rfl i := ... -- proof elided

theorem sector_eigenvalue_le (hH : H.IsSymmetric) (φ : E) (hφ : φ ≠ 0) :
    ∃ i, ⟪hH.eigenvectorBasis rfl i, φ⟫_ℂ ≠ 0 ∧
      hH.eigenvalues rfl i ≤ (⟪φ, H φ⟫_ℂ).re / ‖φ‖ ^ 2 := ... -- proof elided
