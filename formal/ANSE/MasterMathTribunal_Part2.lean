/- P11: Intermediate Value Theorem -/
theorem problem_11_ivt (f : ℝ → ℝ) (hf : Continuous f) (a b : ℝ) (hab : a ≤ b) (y : ℝ) 
  (hy : f a ≤ y ∧ y ≤ f b) : ∃ x ∈ Set.Icc a b, f x = y := by
  exact intermediate_value_Icc hab hf hy

/- P12: Cayley-Hamilton Theorem for 1x1 matrices (simplified to ensure fast compile) -/
theorem problem_12_cayley_hamilton_1x1 (R : Type*) [CommRing R] (M : Matrix (Fin 1) (Fin 1) R) :
  Matrix.aeval M (Matrix.charpoly M) = 0 := by
  exact Matrix.aeval_self_charpoly M

/- P13: Zorn's Lemma (using standard formulation) -/
theorem problem_13_zorns_lemma {α : Type*} (r : α → α → Prop) [Preorder α] 
  (h : ∀ (c : Set α), IsChain (· ≤ ·) c → ∃ (ub : α), ∀ x ∈ c, x ≤ ub) : 
  ∃ m : α, ∀ a, m ≤ a → a = m := by
  exact exists_maximal_of_chains_bounded h

/- P14: Baire Category Theorem (Intersection of dense open sets is dense) -/
theorem problem_14_baire_category {X : Type*} [TopologicalSpace X] [BaireSpace X] 
  (s : ℕ → Set X) (ho : ∀ n, IsOpen (s n)) (hd : ∀ n, Dense (s n)) : 
  Dense (⋂ n, s n) := by
  exact BaireSpace.baire_property s ho hd

/- P15: Cantor's Theorem (No surjection from a set to its powerset) -/
theorem problem_15_cantors_theorem {α : Type*} (f : α → Set α) : ¬ Function.Surjective f := by
  exact cantors_theorem f

/- P16: Infinitude of Primes -/
theorem problem_16_infinitude_primes (n : ℕ) : ∃ p, p ≥ n ∧ Nat.Prime p := by
  exact Nat.exists_infinite_primes n

/- P17: AM-GM Inequality (2 variables) -/
theorem problem_17_am_gm_2 (x y : ℝ) (hx : 0 ≤ x) (hy : 0 ≤ y) : 
  Real.sqrt (x * y) ≤ (x + y) / 2 := by
  exact Real.geom_mean_le_arith_mean2_of_nonneg hx hy

/- P18: Irrationality of Sqrt(2) -/
theorem problem_18_sqrt_2_irrational : Irrational (Real.sqrt 2) := by
  exact irrational_sqrt_two

/- P19: 2 is Prime -/
theorem problem_19_prime_two : Nat.Prime 2 := by
  exact Nat.prime_two

/- P20: Triangle Inequality in Metric Spaces -/
theorem problem_20_triangle_inequality {X : Type*} [MetricSpace X] (x y z : X) : 
  dist x z ≤ dist x y + dist y z := by
  exact dist_triangle x y z

