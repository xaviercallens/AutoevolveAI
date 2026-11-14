import Programmes.CompletelyMonotone.MathlibOnly
import Programmes.CompletelyMonotone.Bernstein

/-!
# Programme P3: the Mathlib-only core has literally the same definitions as `ProgCM`

Both directions are `Iff.rfl`, so every `ProgCMCore` theorem applies verbatim to `ProgCM` (and, through
`ProgCM.isCompletelyMonotoneOn_iff_admissible`, to upstream's `AdmissiblePotential`).
-/

theorem ProgCMCore.isCompletelyMonotoneOn_iff_progCM {f : ℝ → ℝ} :
    ProgCMCore.IsCompletelyMonotoneOn f ↔ ProgCM.IsCompletelyMonotoneOn f :=
  Iff.rfl

theorem ProgCMCore.isBernsteinOn_iff_progCM {g : ℝ → ℝ} :
    ProgCMCore.IsBernsteinOn g ↔ ProgCM.IsBernsteinOn g :=
  Iff.rfl

theorem ProgCMCore.isCompletelyMonotoneOn_iff_admissible {f : ℝ → ℝ} :
    ProgCMCore.IsCompletelyMonotoneOn f ↔ OAI.AtomicTriangular.AdmissiblePotential f :=
  ProgCMCore.isCompletelyMonotoneOn_iff_progCM.trans ProgCM.isCompletelyMonotoneOn_iff_admissible

/-- Example of transfer: the Mathlib-only subordination theorem, stated for `ProgCM`. -/
theorem ProgCMCore.comp_bernstein_progCM {f g : ℝ → ℝ} (hf : ProgCM.IsCompletelyMonotoneOn f)
    (hg : ProgCM.IsBernsteinOn g) (hpos : ∀ t, 0 < t → 0 < g t) :
    ProgCM.IsCompletelyMonotoneOn (fun t => f (g t)) :=
  ProgCMCore.IsCompletelyMonotoneOn.comp_bernstein hf hg hpos

#print axioms ProgCMCore.isCompletelyMonotoneOn_iff_progCM
#print axioms ProgCMCore.isBernsteinOn_iff_progCM
#print axioms ProgCMCore.isCompletelyMonotoneOn_iff_admissible
#print axioms ProgCMCore.comp_bernstein_progCM
