import Mathlib
/-! A2 fidelity probes: what the notations in the challenge statement elaborate to. -/
open ContDiff Set InnerProductSpace MeasureTheory
open scoped Laplacian

-- `∞` under `open ContDiff`: smooth (C^∞ = ↑(⊤ : ℕ∞)), not analytic (ω = ⊤ : WithTop ℕ∞)?
set_option pp.all true in
#check (∞ : WithTop ℕ∞)
example : (∞ : WithTop ℕ∞) = ((⊤ : ℕ∞) : WithTop ℕ∞) := rfl
example : (∞ : WithTop ℕ∞) ≠ ω := by decide

-- Laplacian and gradient definitions as used in the statement
#print Laplacian.laplacian
#check @InnerProductSpace.laplacian
#print gradient
#print LinearMap.trace
#check @iteratedFDerivWithin
#check @MemLp
-- which norm is on a product ℝ³ × ℝ (sup norm)
example (x : EuclideanSpace ℝ (Fin 3)) (t : ℝ) : ‖(x, t)‖ = max ‖x‖ ‖t‖ := rfl
