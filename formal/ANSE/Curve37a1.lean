/-
H6: a concrete, kernel-checkable elliptic-curve fact against the local
Mathlib subset. 37a1 : y² + y = x³ − x is the canonical rank-1 curve
(Gross–Zagier's first example); (0, 0) generates its Mordell–Weil group.
Here we verify formally that (0,0) satisfies the Weierstrass equation.
-/
import Mathlib.AlgebraicGeometry.EllipticCurve.Weierstrass
import Mathlib.AlgebraicGeometry.EllipticCurve.Affine.Point
import Mathlib.Tactic.Ring

/-- The Weierstrass model of curve 37a1: (a₁,a₂,a₃,a₄,a₆) = (0,0,1,−1,0). -/
def W37 : WeierstrassCurve ℚ := ⟨0, 0, 1, -1, 0⟩

theorem gen_on_W37 : W37.toAffine.Equation 0 0 := by
  rw [WeierstrassCurve.Affine.equation_iff]
  simp [W37]

#print axioms gen_on_W37
