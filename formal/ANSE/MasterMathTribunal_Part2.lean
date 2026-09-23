/-
  ANSE.MasterMathTribunal_Part2 — Problems 11 to 20 Formally Verified in Lean 4
  Rigorous formal proofs with Mathlib4 premise selection.
  Zero-sorry, zero-axiomatic hallucination, fail-closed sound verification.
-/

import Mathlib.Data.Real.Basic
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Topology.MetricSpace.Contracting
import Mathlib.Topology.Order.IntermediateValue
import Mathlib.LinearAlgebra.Matrix.Charpoly.Basic
import Mathlib.Algebra.Polynomial.AlgebraMap
import Mathlib.Order.Zorn
import Mathlib.Topology.Baire.Lemmas
import Mathlib.Data.Set.Basic
import Mathlib.Data.Nat.Prime.Basic
import Mathlib.Data.Nat.Prime.Infinite
import Mathlib.NumberTheory.Real.Irrational
import Mathlib.Topology.MetricSpace.Defs
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith

namespace ANSE.MasterMathTribunalPart2

open Set Polynomial

/-- P11: Intermediate Value Theorem (IVT) -/
theorem problem_11_ivt (f : ℝ → ℝ) (a b y : ℝ) (hab : a ≤ b) 
    (hf : ContinuousOn f (Icc a b)) (hy : f a ≤ y ∧ y ≤ f b) : 
    ∃ x ∈ Icc a b, f x = y := by
  have h_sub := intermediate_value_Icc hab hf
  have hy_icc : y ∈ Icc (f a) (f b) := hy
  have h_mem := h_sub hy_icc
  rcases h_mem with ⟨x, hx, hfx⟩
  exact ⟨x, hx, hfx⟩

/-- P12: Cayley-Hamilton Theorem -/
theorem problem_12_cayley_hamilton {n : Type*} [DecidableEq n] [Fintype n] {R : Type*} [CommRing R] 
    (M : Matrix n n R) : aeval M M.charpoly = 0 :=
  Matrix.aeval_self_charpoly M

/-- P13: Zorn's Lemma -/
theorem problem_13_zorns_lemma {α : Type*} [PartialOrder α] 
    (h : ∀ (c : Set α), IsChain (· ≤ ·) c → BddAbove c) : 
    ∃ m : α, IsMax m :=
  zorn_le h

/-- P14: Baire Category Theorem -/
theorem problem_14_baire_category {X : Type*} [TopologicalSpace X] [BaireSpace X] 
    (s : ℕ → Set X) (ho : ∀ n, IsOpen (s n)) (hd : ∀ n, Dense (s n)) : 
    Dense (⋂ n, s n) :=
  BaireSpace.baire_property s ho hd

/-- P15: Cantor's Theorem -/
theorem problem_15_cantors_theorem {α : Type*} (f : α → Set α) : ¬ Function.Surjective f := by
  intro h
  let s : Set α := {x | x ∉ f x}
  obtain ⟨x, hx⟩ := h s
  by_cases hxs : x ∈ s
  · have hx_not : x ∉ f x := hxs
    rw [hx] at hx_not
    exact hx_not hxs
  · have hx_in : x ∈ f x := by
      by_contra hc
      exact hxs hc
    rw [hx] at hx_in
    exact hxs hx_in

/-- P16: Infinitude of Primes -/
theorem problem_16_infinitude_primes (n : ℕ) : ∃ p, n ≤ p ∧ Nat.Prime p :=
  Nat.exists_infinite_primes n

/-- P17: AM-GM Inequality for 2 Variables -/
theorem problem_17_am_gm_2 (x y : ℝ) (hx : 0 ≤ x) (hy : 0 ≤ y) : 
    Real.sqrt (x * y) ≤ (x + y) / 2 := by
  have h : 0 ≤ (Real.sqrt x - Real.sqrt y) ^ 2 := sq_nonneg (Real.sqrt x - Real.sqrt y)
  have h_exp : (Real.sqrt x - Real.sqrt y) ^ 2 = (Real.sqrt x)^2 - 2 * (Real.sqrt x * Real.sqrt y) + (Real.sqrt y)^2 := by ring
  rw [Real.sq_sqrt hx, Real.sq_sqrt hy] at h_exp
  have h_mul : Real.sqrt x * Real.sqrt y = Real.sqrt (x * y) := by rw [Real.sqrt_mul hx]
  rw [h_mul] at h_exp
  linarith

/-- P18: Irrationality of Sqrt(2) -/
theorem problem_18_sqrt_2_irrational : Irrational (Real.sqrt 2) :=
  irrational_sqrt_two

/-- P19: 2 is Prime -/
theorem problem_19_prime_two : Nat.Prime 2 :=
  Nat.prime_two

/-- P20: Triangle Inequality in Metric Spaces -/
theorem problem_20_triangle_inequality {X : Type*} [MetricSpace X] (x y z : X) : 
    dist x z ≤ dist x y + dist y z :=
  dist_triangle x y z

end ANSE.MasterMathTribunalPart2
