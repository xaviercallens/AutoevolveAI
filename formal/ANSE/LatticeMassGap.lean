import Mathlib.Topology.MetricSpace.Basic
import Mathlib.Topology.ContinuousFunction.Basic
import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Analysis.NormedSpace.ContinuousLinearMap

noncomputable section

variable (Λ : Type*) [NormedAddCommGroup Λ] [InnerProductSpace ℂ Λ] [CompleteSpace Λ]

def LatticeHamiltonian := Λ →L[ℂ] Λ

def has_lattice_mass_gap (H : LatticeHamiltonian Λ) (Δ : ℝ) : Prop :=
  Δ > 0 ∧ ∀ ψ : Λ, H ψ ≠ 0 → ‖H ψ‖ ≥ Δ * ‖ψ‖

theorem mass_gap_pos (H : LatticeHamiltonian Λ) (Δ : ℝ) (h_gap : has_lattice_mass_gap Λ H Δ) :
  Δ > 0 := by
  exact h_gap.1
