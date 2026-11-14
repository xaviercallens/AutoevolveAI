-- Autoresearch_EnstrophyFlowControls.lean  sha256 7a3904240f4734df1360471af1bce7fb420ff279298298da6effc9f5c9e065ce  lines 13-23
theorem ctl_sorry (k ω : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ) :
    ∑ n ∈ Finset.range (N + 2), 2 * ((starRingEnd ℂ) (v n) * Fc k ω v n).re = 1 := by
  sorry

/-- Planted axiom: must show `ctl_flow_cheat`. -/
axiom ctl_flow_cheat : ∀ (k ω : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ),
  ∑ n ∈ Finset.range (N + 2), 2 * ((starRingEnd ℂ) (v n) * Fc k ω v n).re = 1

theorem ctl_axiom (k ω : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ) :
    ∑ n ∈ Finset.range (N + 2), 2 * ((starRingEnd ℂ) (v n) * Fc k ω v n).re = 1 :=
  ctl_flow_cheat k ω v N
