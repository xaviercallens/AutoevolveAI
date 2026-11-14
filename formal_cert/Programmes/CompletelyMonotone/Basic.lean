import Autoresearch.KeldyshCM

/-!
# Programme P3 (2026-10-25): completely monotone functions on `(0, ∞)`

`IsCompletelyMonotoneOn f` means: `f` is `C^∞` on `(0, ∞)` and `(-1)^n f^{(n)}(t) ≥ 0` for every `n : ℕ` and
every `t > 0` (the case `n = 0` is `f ≥ 0`). The domain is fixed to the open half-line `(0, ∞)`; translation by
`c ≥ 0` is `comp_add_const`.

* `isCompletelyMonotoneOn_iff_admissible`: the definition is *equivalent* to upstream's (openai/math)
  `OAI.AtomicTriangular.AdmissiblePotential`, whose third clause is the same sign condition and whose second
  clause (`g ≥ 0`) is the `n = 0` instance.
* Closure: `congr` (only values on `(0, ∞)` matter), `zero`, `const`, `const_mul` (`c ≥ 0`), `add`, `sum`
  (finite nonnegative combinations), `mul` (Leibniz, reusing `AutoresearchYukawa.mul_sign`), `comp_add_const`
  (translation by `c ≥ 0`), `neg_deriv` (`-f'` is CM), `antitoneOn_sign` (each `(-1)^n f^{(n)}` is antitone),
  `sub_comp_add_const` (`f(t) - f(t + c)` is CM for `c ≥ 0`).
* Basic examples: `exp_neg_mul` (`e^{-a t}`, `a ≥ 0`), `rpow_neg` (`t^{-s}`, `s ≥ 0`).

The bridge and the Riesz / exponential examples go through modules of this repository that import upstream
openai/math (AI-generated, not peer reviewed); the closure lemmas themselves use only Mathlib.
-/

namespace ProgCM

open Set Filter Topology

/-- `f` is completely monotone on `(0, ∞)`: `C^∞` there, and `(-1)^n f^{(n)} ≥ 0` there for every `n`. -/
def IsCompletelyMonotoneOn (f : ℝ → ℝ) : Prop :=
  ContDiffOn ℝ (⊤ : ℕ∞) f (Set.Ioi 0) ∧
  ∀ (n : ℕ) (t : ℝ), 0 < t → 0 ≤ (-1 : ℝ) ^ n * iteratedDeriv n f t

/-- **Bridge (exact equivalence).** Complete monotonicity on `(0, ∞)` is upstream's `AdmissiblePotential`. -/
theorem isCompletelyMonotoneOn_iff_admissible {f : ℝ → ℝ} :
    IsCompletelyMonotoneOn f ↔ OAI.AtomicTriangular.AdmissiblePotential f := by
  constructor
  · intro h
    refine ⟨h.1, fun t ht => ?_, h.2⟩
    simpa using h.2 0 t ht
  · intro h
    exact ⟨h.1, h.2.2⟩

namespace IsCompletelyMonotoneOn

variable {f g : ℝ → ℝ}

theorem of_admissible (h : OAI.AtomicTriangular.AdmissiblePotential f) : IsCompletelyMonotoneOn f :=
  isCompletelyMonotoneOn_iff_admissible.2 h

theorem admissible (h : IsCompletelyMonotoneOn f) : OAI.AtomicTriangular.AdmissiblePotential f :=
  isCompletelyMonotoneOn_iff_admissible.1 h

theorem sign (hf : IsCompletelyMonotoneOn f) (n : ℕ) {t : ℝ} (ht : 0 < t) :
    0 ≤ (-1 : ℝ) ^ n * iteratedDeriv n f t :=
  hf.2 n t ht

theorem nonneg (hf : IsCompletelyMonotoneOn f) {t : ℝ} (ht : 0 < t) : 0 ≤ f t := by
  simpa using hf.2 0 t ht

theorem contDiffAt (hf : IsCompletelyMonotoneOn f) {t : ℝ} (ht : 0 < t) (n : ℕ) : ContDiffAt ℝ n f t :=
  (hf.1.contDiffAt (Ioi_mem_nhds ht)).of_le (by exact_mod_cast le_top)

theorem differentiableAt (hf : IsCompletelyMonotoneOn f) {t : ℝ} (ht : 0 < t) : DifferentiableAt ℝ f t :=
  (hf.contDiffAt ht 1).differentiableAt (by simp)

theorem differentiableAt_iteratedDeriv (hf : IsCompletelyMonotoneOn f) (n : ℕ) {t : ℝ} (ht : 0 < t) :
    DifferentiableAt ℝ (iteratedDeriv n f) t := by
  have h1 : DifferentiableOn ℝ (iteratedDerivWithin n f (Ioi 0)) (Ioi 0) :=
    hf.1.differentiableOn_iteratedDerivWithin (by exact_mod_cast ENat.natCast_lt_top n) (uniqueDiffOn_Ioi 0)
  have h2 : DifferentiableOn ℝ (iteratedDeriv n f) (Ioi 0) :=
    h1.congr (fun x hx => (iteratedDerivWithin_of_isOpen isOpen_Ioi hx).symm)
  exact h2.differentiableAt (Ioi_mem_nhds ht)

theorem hasDerivAt_iteratedDeriv (hf : IsCompletelyMonotoneOn f) (n : ℕ) {t : ℝ} (ht : 0 < t) :
    HasDerivAt (iteratedDeriv n f) (iteratedDeriv (n + 1) f t) t := by
  rw [iteratedDeriv_succ]
  exact (hf.differentiableAt_iteratedDeriv n ht).hasDerivAt

/-- Only the values on `(0, ∞)` matter. -/
theorem congr (hf : IsCompletelyMonotoneOn f) (heq : EqOn f g (Ioi 0)) : IsCompletelyMonotoneOn g := by
  refine ⟨hf.1.congr (fun x hx => (heq hx).symm), fun n t ht => ?_⟩
  rw [← heq.iteratedDeriv_of_isOpen isOpen_Ioi n ht]
  exact hf.2 n t ht

theorem congr' (hf : IsCompletelyMonotoneOn f) (heq : ∀ t, 0 < t → f t = g t) : IsCompletelyMonotoneOn g :=
  hf.congr fun t ht => heq t ht

/-- A nonnegative multiple. -/
theorem const_mul (hf : IsCompletelyMonotoneOn f) {c : ℝ} (hc : 0 ≤ c) :
    IsCompletelyMonotoneOn (fun t => c * f t) := by
  refine ⟨contDiffOn_const.mul hf.1, fun n t ht => ?_⟩
  have e : iteratedDeriv n (fun t => c * f t) t = c * iteratedDeriv n f t := by
    rw [iteratedDeriv_const_mul_field]
  rw [e, mul_left_comm]
  exact mul_nonneg hc (hf.2 n t ht)

/-- The sum of two completely monotone functions. -/
theorem add (hf : IsCompletelyMonotoneOn f) (hg : IsCompletelyMonotoneOn g) :
    IsCompletelyMonotoneOn (f + g) := by
  refine ⟨hf.1.add hg.1, fun n t ht => ?_⟩
  rw [iteratedDeriv_add (hf.contDiffAt ht n) (hg.contDiffAt ht n), mul_add]
  exact add_nonneg (hf.2 n t ht) (hg.2 n t ht)

/-- **Product (Leibniz).** The product of two completely monotone functions is completely monotone. -/
theorem mul (hf : IsCompletelyMonotoneOn f) (hg : IsCompletelyMonotoneOn g) :
    IsCompletelyMonotoneOn (f * g) :=
  ⟨hf.1.mul hg.1, fun n t ht => AutoresearchYukawa.mul_sign n (hf.contDiffAt ht n) (hg.contDiffAt ht n)
    (fun i _ => hf.2 i t ht) (fun i _ => hg.2 i t ht)⟩

/-- **Translation.** `t ↦ f (t + c)` is completely monotone for `c ≥ 0`. -/
theorem comp_add_const (hf : IsCompletelyMonotoneOn f) {c : ℝ} (hc : 0 ≤ c) :
    IsCompletelyMonotoneOn (fun t => f (t + c)) := by
  have hmaps : MapsTo (fun t : ℝ => t + c) (Ioi 0) (Ioi 0) := fun t ht => by
    simp only [mem_Ioi] at ht ⊢
    linarith
  refine ⟨hf.1.comp (contDiffOn_id.add contDiffOn_const) hmaps, fun n t ht => ?_⟩
  rw [iteratedDeriv_comp_add_const]
  exact hf.2 n (t + c) (by linarith)

/-- **Derivative.** `-f'` is completely monotone. -/
theorem neg_deriv (hf : IsCompletelyMonotoneOn f) : IsCompletelyMonotoneOn (fun t => -deriv f t) := by
  refine ⟨?_, fun n t ht => ?_⟩
  · have hd : ContDiffOn ℝ (⊤ : ℕ∞) (deriv f) (Ioi 0) :=
      contDiffOn_infty.mpr fun N =>
        (contDiffOn_infty.mp hf.1 (N + 1)).deriv_of_isOpen (m := ((N : ℕ) : WithTop ℕ∞)) isOpen_Ioi
          (by push_cast; exact le_rfl)
    exact hd.neg
  · have e : iteratedDeriv n (fun t => -deriv f t) t = -iteratedDeriv (n + 1) f t := by
      rw [iteratedDeriv_succ']
      exact iteratedDeriv_neg n (deriv f) t
    rw [e]
    have := hf.2 (n + 1) t ht
    calc (0 : ℝ) ≤ (-1) ^ (n + 1) * iteratedDeriv (n + 1) f t := this
      _ = (-1) ^ n * -iteratedDeriv (n + 1) f t := by ring

/-- Each `(-1)^n f^{(n)}` is antitone on `(0, ∞)`. -/
theorem antitoneOn_sign (hf : IsCompletelyMonotoneOn f) (n : ℕ) :
    AntitoneOn (fun t => (-1 : ℝ) ^ n * iteratedDeriv n f t) (Ioi 0) := by
  have hd : ∀ t ∈ Ioi (0 : ℝ), HasDerivAt (fun t => (-1 : ℝ) ^ n * iteratedDeriv n f t)
      ((-1) ^ n * iteratedDeriv (n + 1) f t) t := fun t ht =>
    (hf.hasDerivAt_iteratedDeriv n ht).const_mul _
  refine antitoneOn_of_deriv_nonpos (convex_Ioi 0) (fun t ht => (hd t ht).continuousAt.continuousWithinAt)
    ?_ ?_
  · rw [interior_Ioi]
    exact fun t ht => (hd t ht).differentiableAt.differentiableWithinAt
  · rw [interior_Ioi]
    intro t ht
    rw [(hd t ht).deriv]
    have h1 := hf.2 (n + 1) t ht
    have e : (-1 : ℝ) ^ (n + 1) * iteratedDeriv (n + 1) f t = -((-1) ^ n * iteratedDeriv (n + 1) f t) := by
      ring
    linarith

/-- Completely monotone functions are antitone on `(0, ∞)`. -/
theorem antitoneOn (hf : IsCompletelyMonotoneOn f) : AntitoneOn f (Ioi 0) := by
  intro a ha b hb hab
  have := hf.antitoneOn_sign 0 ha hb hab
  simpa using this

/-- **Difference of a translate.** `t ↦ f t - f (t + c)` is completely monotone for `c ≥ 0`. -/
theorem sub_comp_add_const (hf : IsCompletelyMonotoneOn f) {c : ℝ} (hc : 0 ≤ c) :
    IsCompletelyMonotoneOn (fun t => f t - f (t + c)) := by
  have hs := hf.comp_add_const hc
  refine ⟨hf.1.sub hs.1, fun n t ht => ?_⟩
  have htc : 0 < t + c := by linarith
  have e : iteratedDeriv n (fun t => f t - f (t + c)) t =
      iteratedDeriv n f t - iteratedDeriv n f (t + c) := by
    have h := iteratedDeriv_sub (hf.contDiffAt ht n) (hs.contDiffAt ht n)
    rw [iteratedDeriv_comp_add_const] at h
    exact h
  rw [e, mul_sub, sub_nonneg]
  exact hf.antitoneOn_sign n ht htc (by linarith)

end IsCompletelyMonotoneOn

open IsCompletelyMonotoneOn

/-- A nonnegative constant is completely monotone. -/
theorem const {c : ℝ} (hc : 0 ≤ c) : IsCompletelyMonotoneOn (fun _ => c) := by
  refine ⟨contDiffOn_const, fun n t _ => ?_⟩
  rw [iteratedDeriv_const]
  split_ifs with h
  · subst h
    simpa using hc
  · simp

theorem zero : IsCompletelyMonotoneOn (0 : ℝ → ℝ) := (const (le_refl (0 : ℝ))).congr' fun _ _ => rfl

/-- **Finite nonnegative combinations.** -/
theorem sum {ι : Type*} (s : Finset ι) (w : ι → ℝ) (F : ι → ℝ → ℝ) (hw : ∀ i ∈ s, 0 ≤ w i)
    (hF : ∀ i ∈ s, IsCompletelyMonotoneOn (F i)) :
    IsCompletelyMonotoneOn (fun t => ∑ i ∈ s, w i * F i t) := by
  classical
  induction s using Finset.induction_on with
  | empty => simpa using const (le_refl (0 : ℝ))
  | insert a s ha ih =>
    have h1 := (hF a (Finset.mem_insert_self a s)).const_mul (hw a (Finset.mem_insert_self a s))
    have h2 := ih (fun i hi => hw i (Finset.mem_insert_of_mem hi)) (fun i hi => hF i (Finset.mem_insert_of_mem hi))
    refine (h1.add h2).congr' fun t _ => ?_
    simp only [Pi.add_apply, Finset.sum_insert ha]

/-- `e^{-a t}` is completely monotone for `a ≥ 0`. -/
theorem exp_neg_mul {a : ℝ} (ha : 0 ≤ a) : IsCompletelyMonotoneOn (fun t => Real.exp (-(a * t))) :=
  of_admissible (AutoresearchKeldysh.expNeg_admissible ha)

/-- `t^{-s}` is completely monotone for `s ≥ 0`. -/
theorem rpow_neg {s : ℝ} (hs : 0 ≤ s) : IsCompletelyMonotoneOn (fun t => t ^ (-s)) := by
  rcases hs.lt_or_eq with hs | rfl
  · refine (of_admissible (TriangularRiesz.riesz_admissible (s := 2 * s) (by linarith))).congr' fun t _ => ?_
    simp only [TriangularRiesz.riesz]
    congr 1
    ring
  · exact (const zero_le_one).congr' fun t _ => by simp

/-- Upstream's universal optimality, restated for completely monotone potentials (conditional on
`OAI.AtomicTriangular.universal_energy_minimum`, AI-generated, not peer reviewed). -/
theorem triangular_optimal {g : ℝ → ℝ} (hg : IsCompletelyMonotoneOn g) (C : Set OAI.AtomicTriangular.Plane)
    (hC : OAI.AtomicTriangular.LocallyFinite C) (hd : OAI.AtomicTriangular.DensityOne C) :
    OAI.AtomicTriangular.latticeEnergy g ≤ OAI.AtomicTriangular.energy g C :=
  (OAI.AtomicTriangular.universal_energy_minimum g C hg.admissible hC hd).1

end ProgCM

#print axioms ProgCM.isCompletelyMonotoneOn_iff_admissible
#print axioms ProgCM.IsCompletelyMonotoneOn.congr
#print axioms ProgCM.IsCompletelyMonotoneOn.const_mul
#print axioms ProgCM.IsCompletelyMonotoneOn.add
#print axioms ProgCM.IsCompletelyMonotoneOn.mul
#print axioms ProgCM.IsCompletelyMonotoneOn.comp_add_const
#print axioms ProgCM.IsCompletelyMonotoneOn.neg_deriv
#print axioms ProgCM.IsCompletelyMonotoneOn.antitoneOn_sign
#print axioms ProgCM.IsCompletelyMonotoneOn.antitoneOn
#print axioms ProgCM.IsCompletelyMonotoneOn.sub_comp_add_const
#print axioms ProgCM.const
#print axioms ProgCM.zero
#print axioms ProgCM.sum
#print axioms ProgCM.exp_neg_mul
#print axioms ProgCM.rpow_neg
#print axioms ProgCM.triangular_optimal
#print axioms ProgCM.IsCompletelyMonotoneOn.of_admissible
#print axioms ProgCM.IsCompletelyMonotoneOn.admissible
#print axioms ProgCM.IsCompletelyMonotoneOn.sign
#print axioms ProgCM.IsCompletelyMonotoneOn.nonneg
#print axioms ProgCM.IsCompletelyMonotoneOn.contDiffAt
#print axioms ProgCM.IsCompletelyMonotoneOn.differentiableAt
#print axioms ProgCM.IsCompletelyMonotoneOn.differentiableAt_iteratedDeriv
#print axioms ProgCM.IsCompletelyMonotoneOn.hasDerivAt_iteratedDeriv
#print axioms ProgCM.IsCompletelyMonotoneOn.congr'
