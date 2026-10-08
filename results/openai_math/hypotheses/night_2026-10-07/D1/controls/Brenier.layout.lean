/- header /- nested -/ comment -/
import Mathlib

namespace OAI

noncomputable section

open MeasureTheory
open scoped BigOperators ENNReal

namespace Problem358

abbrev E (dimension : ℕ) := EuclideanSpace ℝ (Fin dimension)

def uniformMeasure {dimension : ℕ} (source : Set (E dimension)) : Measure (E dimension) :=
    (volume source)⁻¹ • volume.restrict source  -- control comment

def IsSupported {dimension : ℕ} (measure : Measure (E dimension))
    (container : Set (E dimension)) : Prop :=  -- control comment
    measure (containerᶜ) = 0  -- control comment

def IsCoupling {dimension : ℕ} (source target : Measure (E dimension))
    (plan : Measure (E dimension × E dimension)) : Prop :=  -- control comment
    IsProbabilityMeasure plan ∧  -- control comment
    Measure.map Prod.fst plan = source ∧  -- control comment
    Measure.map Prod.snd plan = target  -- control comment

def quadraticPlanCost {dimension : ℕ} (plan : Measure (E dimension × E dimension)) :
    ℝ≥0∞ :=  -- control comment
    ∫⁻ pair, ENNReal.ofReal (‖pair.1 - pair.2‖ ^ 2) ∂plan  -- control comment

def wasserstein2 {dimension : ℕ} (source target : Measure (E dimension)) : ℝ :=
    Real.sqrt  -- control comment
    (ENNReal.toReal  -- control comment
    (sInf {cost : ℝ≥0∞ |  -- control comment
    ∃ plan : Measure (E dimension × E dimension),  -- control comment
    IsCoupling source target plan ∧ quadraticPlanCost plan = cost}))  -- control comment

def graphPlan {dimension : ℕ} (source : Measure (E dimension))
    (transport : E dimension → E dimension) : Measure (E dimension × E dimension) :=  -- control comment
    Measure.map (fun point => (point, transport point)) source  -- control comment

def IsQuadraticOptimalMap {dimension : ℕ} (source target : Measure (E dimension))
    (transport : E dimension → E dimension) : Prop :=  -- control comment
    Measurable transport ∧  -- control comment
    Measure.map transport source = target ∧  -- control comment
    ∀ plan : Measure (E dimension × E dimension),  -- control comment
    IsCoupling source target plan →  -- control comment
    quadraticPlanCost (graphPlan source transport) ≤ quadraticPlanCost plan  -- control comment

def IsUniqueQuadraticOptimalMap {dimension : ℕ} (source target : Measure (E dimension))
    (transport : E dimension → E dimension) : Prop :=  -- control comment
    IsQuadraticOptimalMap source target transport ∧  -- control comment
    ∀ plan : Measure (E dimension × E dimension),  -- control comment
    IsCoupling source target plan →  -- control comment
    quadraticPlanCost plan ≤ quadraticPlanCost (graphPlan source transport) →  -- control comment
    plan = graphPlan source transport  -- control comment

def mapL2Dist {dimension : ℕ} (source : Measure (E dimension))
    (first second : E dimension → E dimension) : ℝ :=  -- control comment
    Real.sqrt (∫ point, ‖first point - second point‖ ^ 2 ∂source)  -- control comment

def cube (dimension : ℕ) : Set (E dimension) :=
    {point | ∀ index, |point index| ≤ 1}  -- control comment

def HasExactlyThreeAtoms {dimension : ℕ} (measure : Measure (E dimension))
    (container : Set (E dimension)) : Prop :=  -- control comment
    ∃ atoms : Fin 3 → E dimension, Function.Injective atoms ∧  -- control comment
    (∀ index, atoms index ∈ container) ∧  -- control comment
    ∃ weights : Fin 3 → ℝ≥0∞, (∀ index, 0 < weights index) ∧  -- control comment
    (∑ index, weights index) = 1 ∧  -- control comment
    measure = ∑ index, weights index • Measure.dirac (atoms index)  -- control comment

theorem one_third_stability :
    ∀ (dimension : ℕ) (source container : Set (E dimension)),  -- control comment
    2 ≤ dimension → IsCompact source → Convex ℝ source → (interior source).Nonempty →  -- control comment
    IsCompact container → container.Nonempty →  -- control comment
    ∃ constant : ℝ, 0 ≤ constant ∧  -- control comment
    ∀ (first second : Measure (E dimension)),  -- control comment
    IsProbabilityMeasure first → IsProbabilityMeasure second →  -- control comment
    IsSupported first container → IsSupported second container →  -- control comment
    ∃ firstMap secondMap : E dimension → E dimension,  -- control comment
    IsUniqueQuadraticOptimalMap (uniformMeasure source) first firstMap ∧  -- control comment
    IsUniqueQuadraticOptimalMap (uniformMeasure source) second secondMap ∧  -- control comment
    mapL2Dist (uniformMeasure source) firstMap secondMap ≤  -- control comment
    constant * Real.rpow (wasserstein2 first second) (1 / 3 : ℝ) := by  -- control comment
    sorry  -- control comment

theorem one_third_exponent_is_sharp :
    ∀ (dimension : ℕ), 2 ≤ dimension → ∀ exponent : ℝ, (1 / 3 : ℝ) < exponent →  -- control comment
    ∀ constant : ℝ, 0 < constant →  -- control comment
    ∃ (first second : Measure (E dimension)) (firstMap secondMap : E dimension → E dimension),  -- control comment
    IsProbabilityMeasure first ∧ IsProbabilityMeasure second ∧  -- control comment
    IsSupported first (cube dimension) ∧ IsSupported second (cube dimension) ∧  -- control comment
    HasExactlyThreeAtoms first (cube dimension) ∧  -- control comment
    HasExactlyThreeAtoms second (cube dimension) ∧  -- control comment
    first ≠ second ∧  -- control comment
    IsUniqueQuadraticOptimalMap (uniformMeasure (cube dimension)) first firstMap ∧  -- control comment
    IsUniqueQuadraticOptimalMap (uniformMeasure (cube dimension)) second secondMap ∧  -- control comment
    0 < wasserstein2 first second ∧  -- control comment
    constant * Real.rpow (wasserstein2 first second) exponent <  -- control comment
    mapL2Dist (uniformMeasure (cube dimension)) firstMap secondMap := by  -- control comment
    sorry  -- control comment

end Problem358

end

end OAI
