/- Planted controls for H7 stage 1 (flow conservation): the axiom audit must flag both.
They state a FALSE version of the rate identity (rate = 1 instead of 0) for the dispersive shell vector field. -/
import ShellHamiltonian

namespace QuantumFluids.AutoresearchEnstrophyFlowControls

open QuantumFluids.ShellComplex

noncomputable def Fc (k ω : ℕ → ℝ) (v : ℕ → ℂ) (n : ℕ) : ℂ :=
  shellBc k n v - Complex.I * (ω n : ℂ) * v n

/-- Planted `sorry`: must show `sorryAx`. -/
theorem ctl_sorry (k ω : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ) :
    ∑ n ∈ Finset.range (N + 2), 2 * ((starRingEnd ℂ) (v n) * Fc k ω v n).re = 1 := by
  sorry

/-- Planted axiom: must show `ctl_flow_cheat`. -/
axiom ctl_flow_cheat : ∀ (k ω : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ),
  ∑ n ∈ Finset.range (N + 2), 2 * ((starRingEnd ℂ) (v n) * Fc k ω v n).re = 1

theorem ctl_axiom (k ω : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ) :
    ∑ n ∈ Finset.range (N + 2), 2 * ((starRingEnd ℂ) (v n) * Fc k ω v n).re = 1 :=
  ctl_flow_cheat k ω v N

end QuantumFluids.AutoresearchEnstrophyFlowControls

#print axioms QuantumFluids.AutoresearchEnstrophyFlowControls.ctl_sorry
#print axioms QuantumFluids.AutoresearchEnstrophyFlowControls.ctl_axiom
