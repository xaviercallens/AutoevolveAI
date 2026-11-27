/- header /- nested -/ comment -/
import Mathlib

namespace OAI

noncomputable section

open scoped BigOperators

namespace KServer

universe u

abbrev Configuration (k : ℕ) (X : Type u) := Fin k → X

def LabelDistribution (k : ℕ) :=
    {probability : Fin k → ℝ //  -- control comment
    (∀ label, 0 ≤ probability label) ∧ ∑ label, probability label = 1}  -- control comment

abbrev Policy (k : ℕ) (X : Type u) :=
    List (X × Fin k) → X → LabelDistribution k  -- control comment

def serve {k : ℕ} {X : Type u} (s : Configuration k X)
    (label : Fin k) (request : X) : Configuration k X :=  -- control comment
    Function.update s label request  -- control comment

def serviceCost {k : ℕ} {X : Type u} [MetricSpace X]
    (s : Configuration k X) : (requests : List X) → (Fin requests.length → Fin k) → ℝ  -- control comment
    | [], _ => 0  -- control comment
    | request :: requests, labels =>  -- control comment
    dist (s (labels 0)) request +  -- control comment
    serviceCost (serve s (labels 0) request) requests (fun index => labels index.succ)  -- control comment

def pathProbability {k : ℕ} {X : Type u} (A : Policy k X)
    (history : List (X × Fin k)) :  -- control comment
    (requests : List X) → (Fin requests.length → Fin k) → ℝ  -- control comment
    | [], _ => 1  -- control comment
    | request :: requests, labels =>  -- control comment
    (A history request).val (labels 0) *  -- control comment
    pathProbability A (history ++ [(request, labels 0)]) requests  -- control comment
    (fun index => labels index.succ)  -- control comment

def expectedCost {k : ℕ} {X : Type u} [MetricSpace X]
    (A : Policy k X) (s : Configuration k X) (requests : List X) : ℝ :=  -- control comment
    ∑ labels : Fin requests.length → Fin k,  -- control comment
    pathProbability A [] requests labels * serviceCost s requests labels  -- control comment

def optimalCost {k : ℕ} {X : Type u} [MetricSpace X]
    (s : Configuration k X) (requests : List X) : ℝ :=  -- control comment
    sInf (Set.range (serviceCost s requests))  -- control comment

def MainStatement : Prop :=
    ∃ C : ℝ, 0 < C ∧ ∀ (k : ℕ), 2 ≤ k →  -- control comment
    ∀ (X : Type u) (_ : MetricSpace X),  -- control comment
    (∃ embedding : Fin (k + 1) → X, Function.Injective embedding) →  -- control comment
    ∀ s : Configuration k X,  -- control comment
    ∃ A : Policy k X, ∃ B : ℝ,  -- control comment
    0 ≤ B ∧ (Function.Injective s → B = 0) ∧  -- control comment
    ∀ requests : List X,  -- control comment
    expectedCost A s requests ≤  -- control comment
    C * (Real.log (k + 1)) ^ 2 * optimalCost s requests + B  -- control comment

theorem main_theorem : MainStatement.{u} := by
    sorry  -- control comment

end KServer

end

end OAI
