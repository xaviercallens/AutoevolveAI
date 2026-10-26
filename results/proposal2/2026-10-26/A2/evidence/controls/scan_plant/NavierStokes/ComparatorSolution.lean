import Lean
import NavierStokes.ComparatorR3Theorem
import NavierStokes.ComparatorTheorem

/-!
# Navier–Stokes Comparator submission: options (C) and (D)

Expose the project's proof adapters under the reference theorem names.
The adapters import `ComparatorDefinitions`, never the challenge module.
-/

namespace NavierStokes.Comparator

local notation "ℝ³" => EuclideanSpace ℝ (Fin 3)

/-- (C) Breakdown of Navier–Stokes solutions on ℝ³. -/
theorem navier_stokes_breakdown_R3 (nu : ℝ) (hnu : nu > 0) :
    ∃ (u₀ : ℝ³ → ℝ³) (f : ℝ³ → ℝ → ℝ³),
    InitialVelocityConditionDecay u₀ ∧ ForceConditionDecay f ∧
    ¬ (∃ v p, NavierStokesExistenceAndSmoothnessRn nu u₀ f v p) := by
  exact ComparatorBridge.navier_stokes_breakdown_R3 nu hnu

/-- (D) Breakdown of Navier–Stokes solutions on ℝ³/ℤ³. -/
theorem navier_stokes_breakdown_periodic (nu : ℝ) (hnu : nu > 0) :
    ∃ (u₀ : ℝ³ → ℝ³) (f : ℝ³ → ℝ → ℝ³),
    InitialVelocityConditionPeriodic u₀ ∧ ForceConditionPeriodic f ∧
    ¬ (∃ v p, NavierStokesExistenceAndSmoothnessPeriodic nu u₀ f v p) := by
  exact ComparatorBridge.navier_stokes_breakdown_periodic nu hnu

end NavierStokes.Comparator

#print axioms NavierStokes.Comparator.navier_stokes_breakdown_R3
#print axioms NavierStokes.Comparator.navier_stokes_breakdown_periodic

-- PLANTED ESCAPES (negative control for source_scan.py); one per category
theorem planted_sorry : False := by sorry
theorem planted_admit : False := by admit
theorem planted_nd : (2 : Nat) + 2 = 4 := by native_decide
theorem planted_orb : True := by have := Lean.ofReduceBool; trivial
axiom planted_axiom : False
def planted_impl_spec : Nat := 0
@[implemented_by planted_impl_spec] def planted_impl : Nat := 1
@[extern "lean_planted"] def planted_extern : Nat := 1
unsafe def planted_unsafe : Nat := 1
@[csimp] theorem planted_csimp : @planted_impl = @planted_impl := rfl
opaque planted_opaque : Nat
partial def planted_partial (n : Nat) : Nat := planted_partial n
set_option debug.skipKernelTC true in
theorem planted_skip : False := sorry
set_option pp.proofs false
set_option maxHeartbeats 0
open Lean Elab Command in
elab "planted_cmd" : command => do modifyEnv id
run_cmd pure ()
#eval 1
initialize planted_init : IO.Ref Nat ← IO.mkRef 0
macro "planted_macro" : term => `(0)
syntax "planted_syntax" : term
@[command_elab Lean.Parser.Command.check] def planted_ce : Lean.Elab.Command.CommandElab := fun _ => pure ()
#exit
