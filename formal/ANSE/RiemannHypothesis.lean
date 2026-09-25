import Mathlib.NumberTheory.LSeries.RiemannZeta

open Complex

namespace ANSE

/-- The Critical Strip 0 < Re(s) < 1 in the complex plane -/
def InCriticalStrip (s : ℂ) : Prop :=
  0 < s.re ∧ s.re < 1

/-- Millennium Prize Problem: The Riemann Hypothesis (ANSE Critical Strip Formulation).
    All non-trivial zeros of the Riemann zeta function in the critical strip have real part equal to 1/2. -/
def RiemannHypothesisStrip : Prop :=
  ∀ (s : ℂ), InCriticalStrip s → riemannZeta s = 0 → s.re = (1 / 2 : ℝ)

/-- Canonical Mathlib4 Wikidata-annotated Riemann Hypothesis statement reference -/
def RiemannHypothesisCanonical : Prop :=
  _root_.RiemannHypothesis

end ANSE
