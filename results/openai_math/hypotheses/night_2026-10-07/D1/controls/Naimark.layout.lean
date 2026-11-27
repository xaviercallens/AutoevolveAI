/- header /- nested -/ comment -/
import Mathlib

namespace OAI

noncomputable section

universe u v w

namespace NaimarkZFC

def IsSimpleCStar (A : Type u) [CStarAlgebra A] : Prop :=
    Nontrivial A ∧ ∀ I : TwoSidedIdeal A, IsClosed (I : Set A) → I = ⊥ ∨ I = ⊤  -- control comment

def IsState {A : Type u} [CStarAlgebra A] (f : A →L[ℂ] ℂ) : Prop :=
    ‖f‖ = 1 ∧ ∀ a : A, (f (star a * a)).im = 0 ∧ 0 ≤ (f (star a * a)).re  -- control comment

def IsFaithfulTracialState {A : Type u} [CStarAlgebra A] (f : A →L[ℂ] ℂ) : Prop :=
    IsState f ∧ (∀ a b : A, f (a * b) = f (b * a)) ∧  -- control comment
    ∀ a : A, a ≠ 0 → 0 < (f (star a * a)).re  -- control comment

def IsIrreducible {A : Type u} [CStarAlgebra A]
    {H : Type v} [NormedAddCommGroup H] [InnerProductSpace ℂ H] [CompleteSpace H]  -- control comment
    (π : A →⋆ₙₐ[ℂ] (H →L[ℂ] H)) : Prop :=  -- control comment
    π ≠ 0 ∧ ∀ M : Submodule ℂ H, IsClosed (M : Set H) →  -- control comment
    (∀ a : A, ∀ x ∈ M, π a x ∈ M) → M = ⊥ ∨ M = ⊤  -- control comment

def UnitarilyEquivalent {A : Type u} [CStarAlgebra A]
    {H : Type v} [NormedAddCommGroup H] [InnerProductSpace ℂ H] [CompleteSpace H]  -- control comment
    {K : Type w} [NormedAddCommGroup K] [InnerProductSpace ℂ K] [CompleteSpace K]  -- control comment
    (π : A →⋆ₙₐ[ℂ] (H →L[ℂ] H)) (ρ : A →⋆ₙₐ[ℂ] (K →L[ℂ] K)) : Prop :=  -- control comment
    ∃ U : H ≃ₗᵢ[ℂ] K, ∀ a : A, ∀ x : H, U (π a x) = ρ a (U x)  -- control comment

def HasUniqueIrreducibleRepresentation (A : Type u) [CStarAlgebra A] : Prop :=
    ∀ (H : Type v) [NormedAddCommGroup H] [InnerProductSpace ℂ H] [CompleteSpace H]  -- control comment
    (K : Type w) [NormedAddCommGroup K] [InnerProductSpace ℂ K] [CompleteSpace K]  -- control comment
    (π : A →⋆ₙₐ[ℂ] (H →L[ℂ] H)) (ρ : A →⋆ₙₐ[ℂ] (K →L[ℂ] K)),  -- control comment
    IsIrreducible π → IsIrreducible ρ → UnitarilyEquivalent π ρ  -- control comment

def IsIsomorphicToCompacts (A : Type u) [CStarAlgebra A]
    (H : Type v) [NormedAddCommGroup H] [InnerProductSpace ℂ H] [CompleteSpace H] : Prop :=  -- control comment
    ∃ φ : A →⋆ₙₐ[ℂ] (H →L[ℂ] H), Function.Injective φ ∧  -- control comment
    ∀ T : H →L[ℂ] H, (∃ a : A, φ a = T) ↔ IsCompactOperator T  -- control comment

theorem main :
    ∃ (A : Type u) (_ : CStarAlgebra A),  -- control comment
    IsSimpleCStar A ∧ ¬ FiniteDimensional ℂ A ∧  -- control comment
    (∃ τ : A →L[ℂ] ℂ, IsFaithfulTracialState τ) ∧  -- control comment
    HasUniqueIrreducibleRepresentation.{u, v, w} A ∧  -- control comment
    ∀ (H : Type v) [NormedAddCommGroup H] [InnerProductSpace ℂ H] [CompleteSpace H],  -- control comment
    ¬ IsIsomorphicToCompacts A H := by  -- control comment
    sorry  -- control comment

end NaimarkZFC

end

end OAI
