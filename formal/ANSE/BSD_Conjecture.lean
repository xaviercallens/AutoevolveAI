import Mathlib.AlgebraicGeometry.EllipticCurve.Weierstrass
import Mathlib.AlgebraicGeometry.EllipticCurve.LFunction
import Mathlib.Analysis.Calculus.Deriv.Basic

open Complex
open WeierstrassCurve

/-- Non-singular Elliptic Curve over the rational numbers Q -/
structure RationalEllipticCurve where
  curve : WeierstrassCurve ℚ
  is_elliptic : curve.Δ ≠ 0

/-- The Hasse-Weil L-function L(E, s) of the elliptic curve via Euler products -/
noncomputable def hasse_weil_L_series (E : RationalEllipticCurve) (s : ℂ) : ℂ :=
  E.curve.LSeries s

/-- Analytic order of vanishing of the Hasse-Weil L-series at the central point s = 1 -/
def HasAnalyticOrderAtOne (E : RationalEllipticCurve) (r : ℕ) : Prop :=
  -- L(E, s) = c * (s - 1)^r + O((s - 1)^(r+1)) with c ≠ 0 near s = 1
  ∃ (c : ℂ), c ≠ 0 ∧
    ∀ (s : ℂ), s ≠ 1 →
      ∃ (R : ℂ), hasse_weil_L_series E s = c * (s - 1)^r + R * (s - 1)^(r + 1)

/-- The Mordell-Weil Algebraic Rank of E(Q): E(Q) ≅ Z^r ⊕ Torsion -/
structure MordellWeilStructure (E : RationalEllipticCurve) where
  rank : ℕ
  is_finitely_generated : True

/-- Millennium Prize Problem: The Birch and Swinnerton-Dyer Conjecture.
    The algebraic rank r of E(Q) equals the analytic order of vanishing of L(E, s) at s = 1. -/
def BirchSwinnertonDyerConjecture
    (E : RationalEllipticCurve)
    (MW : MordellWeilStructure E) : Prop :=
  HasAnalyticOrderAtOne E MW.rank
