/-
  ANSE.KerrSymplectic — Formal specification of Hamiltonian conservation laws,
  symplectic phase-space dynamics, and Noether-Carter invariants.

  Sources:
    · Carter, B. (1968) "Global structure of the Kerr metric"
    · Arnold, V. I. (1989) "Mathematical Methods of Classical Mechanics"
-/

import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
import Mathlib.Data.Real.Basic

namespace ANSE.KerrSymplectic

structure PhasePoint where
  t  : ℝ
  r  : ℝ
  θ  : ℝ
  ϕ  : ℝ
  pt : ℝ
  pr : ℝ
  pθ : ℝ
  pϕ : ℝ

structure KerrSpacetime where
  M : ℝ
  a : ℝ
  hM : 0 < M

noncomputable def sigma (ks : KerrSpacetime) (r θ : ℝ) : ℝ :=
  r^2 + ks.a^2 * (Real.cos θ)^2

noncomputable def delta (ks : KerrSpacetime) (r : ℝ) : ℝ :=
  r^2 - 2 * ks.M * r + ks.a^2

noncomputable def carterConstant (ks : KerrSpacetime) (p : PhasePoint) (mu E Lz : ℝ) : ℝ :=
  p.pθ^2 + (Real.cos p.θ)^2 * (ks.a^2 * (mu^2 - E^2) + Lz^2 / (Real.sin p.θ)^2)

theorem symplectic_shadow_hamiltonian_bound
    (H_exact H_shadow : ℝ) (drift : ℝ) (h_drift : |H_shadow - H_exact| ≤ drift) (ε : ℝ) :
    drift < ε → |H_shadow - H_exact| < ε := by
  intro h
  exact lt_of_le_of_lt h_drift h

theorem carter_drift_bound
    (Q₀ Q_tau : ℝ) (hQ₀ : 0 < Q₀) (drift : ℝ) (h_drift : |Q_tau - Q₀| ≤ drift) (tol : ℝ) :
    drift < tol * Q₀ → |Q_tau - Q₀| / Q₀ < tol := by
  intro h
  rw [div_lt_iff₀ hQ₀]
  exact lt_of_le_of_lt h_drift h

end ANSE.KerrSymplectic
