/- header /- nested -/ comment -/
import Mathlib

namespace OAI

namespace ElementaryPositivity

structure NaturalUnitIntervalGraph (n : ℕ) where
    h : Fin n → Fin n  -- control comment
    increasing : Monotone h  -- control comment
    extensive : ∀ i, i ≤ h i  -- control comment

namespace NaturalUnitIntervalGraph

variable {n : ℕ} (G : NaturalUnitIntervalGraph n)

def Edge (i j : Fin n) : Prop :=
    (i < j ∧ j ≤ G.h i) ∨ (j < i ∧ i ≤ G.h j)  -- control comment

instance (i j : Fin n) : Decidable (G.Edge i j) :=
    inferInstanceAs (Decidable ((_ ∧ _) ∨ (_ ∧ _)))  -- control comment

def Nondescent (σ : Equiv.Perm (Fin n)) : Prop :=
    ∀ i j : Fin n, i.val + 1 = j.val → σ j < σ i → G.Edge (σ i) (σ j)  -- control comment

instance (σ : Equiv.Perm (Fin n)) : Decidable (G.Nondescent σ) :=
    inferInstanceAs (Decidable (∀ i j : Fin n,  -- control comment
    i.val + 1 = j.val → σ j < σ i → G.Edge (σ i) (σ j)))  -- control comment

def graphInversions (σ : Equiv.Perm (Fin n)) : ℕ :=
    (Finset.univ.filter fun ij : Fin n × Fin n =>  -- control comment
    ij.1 < ij.2 ∧ σ ij.2 < σ ij.1 ∧ G.Edge (σ ij.1) (σ ij.2)).card  -- control comment

def Proper {r : ℕ} (f : Fin n → Fin r) : Prop :=
    ∀ i j : Fin n, G.Edge i j → f i ≠ f j  -- control comment

instance {r : ℕ} (f : Fin n → Fin r) : Decidable (G.Proper f) :=
    inferInstanceAs (Decidable (∀ i j : Fin n, G.Edge i j → f i ≠ f j))  -- control comment

def coloringAscents {r : ℕ} (f : Fin n → Fin r) : ℕ :=
    (Finset.univ.filter fun ij : Fin n × Fin n =>  -- control comment
    ij.1 < ij.2 ∧ G.Edge ij.1 ij.2 ∧ f ij.1 < f ij.2).card  -- control comment

noncomputable def chromatic (r : ℕ) : MvPolynomial (Fin r) (Polynomial ℕ) :=
    ∑ f ∈ Finset.univ.filter (G.Proper (r := r)),  -- control comment
    MvPolynomial.C (Polynomial.X ^ G.coloringAscents f) *  -- control comment
    ∏ i : Fin n, MvPolynomial.X (f i)  -- control comment

structure PermutationWitness where
    theta : {σ : Equiv.Perm (Fin n) // G.Nondescent σ} → Nat.Partition n  -- control comment
    expansion : ∀ r : ℕ, G.chromatic r =  -- control comment
    ∑ σ : {σ : Equiv.Perm (Fin n) // G.Nondescent σ},  -- control comment
    MvPolynomial.C (Polynomial.X ^ G.graphInversions σ.val) *  -- control comment
    MvPolynomial.esymmPart (Fin r) (Polynomial ℕ) (theta σ)  -- control comment

end NaturalUnitIntervalGraph
end ElementaryPositivity

def elementaryPositivityWitness (n : ℕ)
    (G : ElementaryPositivity.NaturalUnitIntervalGraph n) :  -- control comment
    G.PermutationWitness := by  -- control comment
    sorry  -- control comment

end OAI
