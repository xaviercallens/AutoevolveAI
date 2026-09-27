/-
A faithful Lean 4 statement of the BSD rank conjecture, replacing the defective
formal/ANSE/BSD_Conjecture.lean whose `rank` was a free field untied to E(ℚ).

Honesty notes:
* Mathlib v4.34 has no Mordell–Weil theorem, so the rank is stated as the
  ℚ-dimension of E(ℚ) ⊗ℤ ℚ, which is well-defined without finite generation.
* Mathlib's `WeierstrassCurve.LFunction` is a formal Dirichlet series whose
  `LSeries` converges for re(s) > 3/2; analytic continuation to s = 1 is not
  in Mathlib, so the statement carries the entire continuation `Λ` as data
  with the agreement condition on the convergence half-plane.
-/
import Mathlib.AlgebraicGeometry.EllipticCurve.LFunction
import Mathlib.AlgebraicGeometry.EllipticCurve.Affine.Point
import Mathlib.NumberTheory.LSeries.Basic
import Mathlib.Analysis.Analytic.Basic
import Mathlib.Analysis.Calculus.IteratedDeriv.Defs
import Mathlib.LinearAlgebra.TensorProduct.Basic
import Mathlib.LinearAlgebra.Dimension.Basic

open scoped TensorProduct

namespace ANSE

noncomputable def mwRank (W : WeierstrassCurve ℚ) : Cardinal :=
  Module.rank ℚ (ℚ ⊗[ℤ] W.toAffine.Point)

/-- `Λ` vanishes to order exactly `r` at `s = 1`. -/
def vanishingOrderIs (Λ : ℂ → ℂ) (r : ℕ) : Prop :=
  (∀ k < r, iteratedDeriv k Λ 1 = 0) ∧ iteratedDeriv r Λ 1 ≠ 0

/-- BSD, rank part: the L-series of `E/ℚ` continues to an entire function whose
order of vanishing at `s = 1` equals the Mordell–Weil rank of `E(ℚ)`. -/
def BSD_RankStatement : Prop :=
  ∀ W : WeierstrassCurve ℚ, W.IsElliptic → ∃ (Λ : ℂ → ℂ) (r : ℕ),
    AnalyticOnNhd ℂ Λ Set.univ ∧
    (∀ s : ℂ, 3 / 2 < s.re →
      Λ s = LSeries (fun n => (W.LFunction n : ℂ)) s) ∧
    vanishingOrderIs Λ r ∧ mwRank W = r

end ANSE
