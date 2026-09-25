import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Topology.ContinuousLinearMap.Basic

class QuantumGaugeTheory (H : Type) [NormedAddCommGroup H] [InnerProductSpace ℂ H] [CompleteSpace H] where
  Hamiltonian : H →L[ℂ] H
  vacuum : H

def has_strict_mass_gap {H : Type} [NormedAddCommGroup H] [InnerProductSpace ℂ H] [CompleteSpace H] (Q : QuantumGaugeTheory H) : Prop :=
  ∃ (Δ : ℝ), Δ > 0 ∧ ∀ (ψ : H) (E : ℝ),
    Q.Hamiltonian ψ = (E : ℂ) • ψ → ψ ≠ Q.vacuum → E ≥ Δ
