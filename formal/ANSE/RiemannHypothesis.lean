import Mathlib.NumberTheory.LSeries.RiemannZeta

open Complex

/-- The Critical Strip 0 < Re(s) < 1 in the complex plane -/
def InCriticalStrip (s : ℂ) : Prop :=
  0 < s.re ∧ s.re < 1

/-- Millennium Prize Problem: The Riemann Hypothesis.
    All non-trivial zeros of the Riemann zeta function have real part equal to 1/2. -/
def RiemannHypothesis : Prop :=
  ∀ (s : ℂ), InCriticalStrip s → riemannZeta s = 0 → s.re = (1 / 2 : ℝ)
