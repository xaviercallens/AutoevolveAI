/- header /- nested -/ comment -/
import Mathlib

namespace OAI

open MeasureTheory Filter
open scoped BigOperators Topology

namespace Rokhlin

variable {Ω : Type*} [MeasurableSpace Ω]

def timeMap (T : Ω ≃ᵐ Ω) (n : ℤ) : Ω → Ω :=
    ⇑((T.toEquiv : Equiv.Perm Ω) ^ n)  -- control comment

def IsMixing (μ : Measure Ω) (T : Ω ≃ᵐ Ω) : Prop :=
    ∀ A B : Set Ω, MeasurableSet A → MeasurableSet B →  -- control comment
    Tendsto (fun n : ℤ => μ (A ∩ timeMap T n ⁻¹' B))  -- control comment
    (comap Int.natAbs atTop) (𝓝 (μ A * μ B))  -- control comment

def layoutTime {k : ℕ} (gaps : Fin (k - 1) → ℕ+) (i : Fin k) : ℕ :=
    ∑ j : Fin (k - 1), if j.val < i.val then (gaps j : ℕ) else 0  -- control comment

def MixingOfOrder (μ : Measure Ω) (T : Ω ≃ᵐ Ω) (k : ℕ) : Prop :=
    ∀ A : Fin k → Set Ω, (∀ i, MeasurableSet (A i)) →  -- control comment
    Tendsto  -- control comment
    (fun gaps : Fin (k - 1) → ℕ+ =>  -- control comment
    μ (⋂ i : Fin k, timeMap T (layoutTime gaps i : ℤ) ⁻¹' A i))  -- control comment
    atTop (𝓝 (∏ i : Fin k, μ (A i)))  -- control comment

theorem mixing_all_finite_orders (μ : Measure Ω) [IsProbabilityMeasure μ]
    (T : Ω ≃ᵐ Ω) (h_pres : MeasurePreserving T μ μ) (h_mix : IsMixing μ T) :  -- control comment
    ∀ k : ℕ, 3 ≤ k → MixingOfOrder μ T k := by  -- control comment
    sorry  -- control comment

end Rokhlin

end OAI
