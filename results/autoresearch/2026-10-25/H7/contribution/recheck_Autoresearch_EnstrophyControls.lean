/- Planted controls for H7: the axiom audit must flag both. -/
import ShellHamiltonian

namespace QuantumFluids.AutoresearchEnstrophyControls

/-- Planted `sorry`: must show `sorryAx`. -/
theorem ctl_sorry (v : ℕ → ℂ) (N : ℕ) :
    ∑ n ∈ Finset.range (N + 2), (4 : ℝ) ^ n * Complex.normSq (v n) ≤ 0 := by
  sorry

/-- Planted axiom: must show `ctl_cheat`. -/
axiom ctl_cheat : ∀ (v : ℕ → ℂ) (N : ℕ),
  ∑ n ∈ Finset.range (N + 2), (4 : ℝ) ^ n * Complex.normSq (v n) ≤ 0

theorem ctl_axiom (v : ℕ → ℂ) (N : ℕ) :
    ∑ n ∈ Finset.range (N + 2), (4 : ℝ) ^ n * Complex.normSq (v n) ≤ 0 := ctl_cheat v N

end QuantumFluids.AutoresearchEnstrophyControls

#print axioms QuantumFluids.AutoresearchEnstrophyControls.ctl_sorry
#print axioms QuantumFluids.AutoresearchEnstrophyControls.ctl_axiom
