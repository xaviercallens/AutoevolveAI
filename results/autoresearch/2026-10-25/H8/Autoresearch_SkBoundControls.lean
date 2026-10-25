/- Planted controls for H8: the axiom audit must flag both. -/
import DualLength

namespace QuantumFluids.AutoresearchSkBoundControls

open QuantumFluids.DualLength

/-- Planted `sorry`: must show `sorryAx`. -/
theorem ctl_sorry {ks k : ℝ} (hk : 0 < k) (hks : 0 < ks) : (1 : ℝ) ≤ Real.sqrt (k / (2 * ks)) := by
  sorry

/-- Planted axiom: must show `ctl_cheat`. -/
axiom ctl_cheat : ∀ ks k : ℝ, (1 : ℝ) ≤ Real.sqrt (k / (2 * ks))

theorem ctl_axiom {ks k : ℝ} : (1 : ℝ) ≤ Real.sqrt (k / (2 * ks)) := ctl_cheat ks k

end QuantumFluids.AutoresearchSkBoundControls

#print axioms QuantumFluids.AutoresearchSkBoundControls.ctl_sorry
#print axioms QuantumFluids.AutoresearchSkBoundControls.ctl_axiom
