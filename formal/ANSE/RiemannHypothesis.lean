import Mathlib.Data.Complex.Basic

constant riemannZeta : ℂ → ℂ

def InCriticalStrip (s : ℂ) : Prop := 0 < s.re ∧ s.re < 1

theorem riemann_hypothesis : Prop :=
  ∀ (s : ℂ), InCriticalStrip s → riemannZeta s = 0 → s.re = (1 / 2 : ℝ)
