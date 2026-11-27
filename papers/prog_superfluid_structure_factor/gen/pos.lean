theorem gap_witness {e0 e1 : E} (h0 : ‖e0‖ = 1) (h1 : ‖e1‖ = 1) (h01 : ⟪e0, e1⟫_ℂ = 0) :
    (ketBra e1 e1).IsSymmetric ∧
    ketBra e1 e1 e0 = ((0 : ℝ) : ℂ) • e0 ∧
    (∀ x : E, (0 : ℝ) * ‖x‖ ^ 2 ≤ (⟪x, ketBra e1 e1 x⟫_ℂ).re) ∧
    (∀ v : E, ketBra e1 e1 v = ((0 : ℝ) : ℂ) • v →
      ⟪v, (ketBra e1 e0 + ketBra e0 e1) e0⟫_ℂ = 0) ∧
    (1 : ℝ) = ‖(ketBra e1 e0 + ketBra e0 e1) e0‖ ^ 2 / 1 ∧
    ⟪e0, comm (adjoint (ketBra e1 e0 + ketBra e0 e1))
        (comm (ketBra e1 e1) (ketBra e1 e0 + ketBra e0 e1)) e0⟫_ℂ
      = (((1 : ℝ) * 1 ^ 2 * 1 ^ 2 / (1 / 2) : ℝ) : ℂ) ∧
    excess (ketBra e1 e1) 0 e0 (adjoint (ketBra e1 e0 + ketBra e0 e1))
      = excess (ketBra e1 e1) 0 e0 (ketBra e1 e0 + ketBra e0 e1) ∧
    ketBra e1 e1 ((ketBra e1 e0 + ketBra e0 e1) e0)
      = (((1 : ℝ) ^ 2 * 1 ^ 2 / (2 * (1 / 2) * 1) : ℝ) : ℂ) • ((ketBra e1 e0 + ketBra e0 e1) e0) := ... -- proof elided

theorem gap_witness_applies {e0 e1 : E} (h0 : ‖e0‖ = 1) (h1 : ‖e1‖ = 1) (h01 : ⟪e0, e1⟫_ℂ = 0) :
    ∃ i, ⟪(ketBra_self_symm e1).eigenvectorBasis rfl i,
          (ketBra e1 e0 + ketBra e0 e1) e0⟫_ℂ ≠ 0 ∧
      0 < (ketBra_self_symm e1).eigenvalues rfl i - 0 ∧
      (ketBra_self_symm e1).eigenvalues rfl i - 0 ≤ (1 : ℝ) ^ 2 * 1 ^ 2 / (2 * (1 / 2) * 1) := ... -- proof elided

theorem orthonormal_pair_fin2 :
    ∃ e0 e1 : EuclideanSpace ℂ (Fin 2), ‖e0‖ = 1 ∧ ‖e1‖ = 1 ∧ ⟪e0, e1⟫_ℂ = 0 := ... -- proof elided
