/- Planted controls for the H8 shape file: the axiom audit must flag both.
Self-contained (re-declares `sBog` locally) so it does not need the claimed module's .olean. -/
import DualLength

namespace QuantumFluids.AutoresearchSkBoundShapeControls

open QuantumFluids.DualLength

noncomputable def sBog (hc ks k : ℝ) : ℝ :=
  (hc * k ^ 2 / ks) / Real.sqrt (bogoliubovSq hc ks k)

/-- Planted `sorry` on a FALSE shape claim (S_B ≥ 1): must show `sorryAx`. -/
theorem ctl_sorry {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    1 ≤ sBog hc ks k := by
  sorry

/-- Planted axiom asserting the false claim that S_B is antitone: must show `ctl_cheat`. -/
axiom ctl_cheat : ∀ hc ks : ℝ, StrictAntiOn (sBog hc ks) (Set.Ioi 0)

theorem ctl_axiom {hc ks : ℝ} : StrictAntiOn (sBog hc ks) (Set.Ioi 0) := ctl_cheat hc ks

end QuantumFluids.AutoresearchSkBoundShapeControls

#print axioms QuantumFluids.AutoresearchSkBoundShapeControls.ctl_sorry
#print axioms QuantumFluids.AutoresearchSkBoundShapeControls.ctl_axiom
