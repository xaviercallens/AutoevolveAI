import Mathlib.Analysis.Calculus.IteratedDeriv.Lemmas
import Mathlib.Analysis.Calculus.Deriv.MeanValue
import Mathlib.Analysis.Calculus.ParametricIntegral
import Mathlib.Analysis.SpecialFunctions.Pow.Deriv
import Mathlib.Analysis.SpecialFunctions.Sqrt
import Mathlib.Analysis.SpecialFunctions.ExpDeriv
import Mathlib.Analysis.Complex.Exponential
import Mathlib.RingTheory.Polynomial.Pochhammer

/-!
# Programme P3: Mathlib-only core of the completely monotone / Bernstein library

The same definitions as `ProgCM` (`Programmes.CompletelyMonotone.Basic` / `.Bernstein`), with **only specific Mathlib
imports** (no openai/math, no repo modules). The three ingredients that `Basic` takes from repo/upstream modules are
re-proved natively: the Leibniz sign lemma `mul_sign`, `exp_neg_mul` and `rpow_neg`. The analytic core of the Laplace
lemma (differentiation under the integral, from `Autoresearch/KeldyshCM.lean`) is ported here as well.
`MathlibOnlyBridge.lean` checks that the definitions coincide with `ProgCM`'s (`Iff.rfl`).
-/

namespace ProgCMCore

open Set Filter Topology MeasureTheory

/-- `f` is completely monotone on `(0, ∞)`. -/
def IsCompletelyMonotoneOn (f : ℝ → ℝ) : Prop :=
  ContDiffOn ℝ (⊤ : ℕ∞) f (Set.Ioi 0) ∧
  ∀ (n : ℕ) (t : ℝ), 0 < t → 0 ≤ (-1 : ℝ) ^ n * iteratedDeriv n f t

/-- `g` is a Bernstein function on `(0, ∞)`. -/
def IsBernsteinOn (g : ℝ → ℝ) : Prop :=
  ContDiffOn ℝ (⊤ : ℕ∞) g (Set.Ioi 0) ∧ (∀ t : ℝ, 0 < t → 0 ≤ g t) ∧ IsCompletelyMonotoneOn (deriv g)

/-- Pointwise Leibniz sign lemma. -/
lemma mul_sign {f h : ℝ → ℝ} {t : ℝ} (r : ℕ) (hf : ContDiffAt ℝ r f t) (hh : ContDiffAt ℝ r h t)
    (Hf : ∀ i ≤ r, 0 ≤ (-1 : ℝ) ^ i * iteratedDeriv i f t)
    (Hh : ∀ i ≤ r, 0 ≤ (-1 : ℝ) ^ i * iteratedDeriv i h t) :
    0 ≤ (-1 : ℝ) ^ r * iteratedDeriv r (f * h) t := by
  rw [iteratedDeriv_mul hf hh, Finset.mul_sum]
  refine Finset.sum_nonneg fun i hi => ?_
  have hir : i ≤ r := Nat.lt_succ_iff.mp (Finset.mem_range.mp hi)
  have hpow : (-1 : ℝ) ^ r = (-1) ^ i * (-1) ^ (r - i) := by
    rw [← pow_add, Nat.add_sub_cancel' hir]
  have h1 := Hf i hir
  have h2 := Hh (r - i) (Nat.sub_le r i)
  have hc : (0 : ℝ) ≤ (r.choose i : ℝ) := Nat.cast_nonneg _
  calc (0 : ℝ) ≤ (r.choose i : ℝ) *
        (((-1) ^ i * iteratedDeriv i f t) * ((-1) ^ (r - i) * iteratedDeriv (r - i) h t)) :=
        mul_nonneg hc (mul_nonneg h1 h2)
    _ = (-1 : ℝ) ^ r * ((r.choose i : ℝ) * iteratedDeriv i f t * iteratedDeriv (r - i) h t) := by
        rw [hpow]; ring

namespace IsCompletelyMonotoneOn

variable {f g : ℝ → ℝ}

theorem nonneg (hf : IsCompletelyMonotoneOn f) {t : ℝ} (ht : 0 < t) : 0 ≤ f t := by
  simpa using hf.2 0 t ht

theorem contDiffAt (hf : IsCompletelyMonotoneOn f) {t : ℝ} (ht : 0 < t) (n : ℕ) : ContDiffAt ℝ n f t :=
  (hf.1.contDiffAt (Ioi_mem_nhds ht)).of_le (by exact_mod_cast le_top)

theorem differentiableAt (hf : IsCompletelyMonotoneOn f) {t : ℝ} (ht : 0 < t) : DifferentiableAt ℝ f t :=
  (hf.contDiffAt ht 1).differentiableAt (by simp)

theorem hasDerivAt_iteratedDeriv (hf : IsCompletelyMonotoneOn f) (n : ℕ) {t : ℝ} (ht : 0 < t) :
    HasDerivAt (iteratedDeriv n f) (iteratedDeriv (n + 1) f t) t := by
  have h1 : DifferentiableOn ℝ (iteratedDerivWithin n f (Ioi 0)) (Ioi 0) :=
    hf.1.differentiableOn_iteratedDerivWithin (by exact_mod_cast ENat.natCast_lt_top n) (uniqueDiffOn_Ioi 0)
  have h2 : DifferentiableOn ℝ (iteratedDeriv n f) (Ioi 0) :=
    h1.congr (fun x hx => (iteratedDerivWithin_of_isOpen isOpen_Ioi hx).symm)
  rw [iteratedDeriv_succ]
  exact (h2.differentiableAt (Ioi_mem_nhds ht)).hasDerivAt

theorem congr' (hf : IsCompletelyMonotoneOn f) (heq : ∀ t, 0 < t → f t = g t) : IsCompletelyMonotoneOn g := by
  refine ⟨hf.1.congr (fun x hx => (heq x hx).symm), fun n t ht => ?_⟩
  have hEq : EqOn f g (Ioi 0) := fun x hx => heq x hx
  rw [← hEq.iteratedDeriv_of_isOpen isOpen_Ioi n ht]
  exact hf.2 n t ht

theorem const_mul (hf : IsCompletelyMonotoneOn f) {c : ℝ} (hc : 0 ≤ c) :
    IsCompletelyMonotoneOn (fun t => c * f t) := by
  refine ⟨contDiffOn_const.mul hf.1, fun n t ht => ?_⟩
  have e : iteratedDeriv n (fun t => c * f t) t = c * iteratedDeriv n f t := by
    rw [iteratedDeriv_const_mul_field]
  rw [e, mul_left_comm]
  exact mul_nonneg hc (hf.2 n t ht)

theorem add (hf : IsCompletelyMonotoneOn f) (hg : IsCompletelyMonotoneOn g) :
    IsCompletelyMonotoneOn (f + g) := by
  refine ⟨hf.1.add hg.1, fun n t ht => ?_⟩
  rw [iteratedDeriv_add (hf.contDiffAt ht n) (hg.contDiffAt ht n), mul_add]
  exact add_nonneg (hf.2 n t ht) (hg.2 n t ht)

theorem mul (hf : IsCompletelyMonotoneOn f) (hg : IsCompletelyMonotoneOn g) :
    IsCompletelyMonotoneOn (f * g) :=
  ⟨hf.1.mul hg.1, fun n t ht => mul_sign n (hf.contDiffAt ht n) (hg.contDiffAt ht n)
    (fun i _ => hf.2 i t ht) (fun i _ => hg.2 i t ht)⟩

theorem comp_add_const (hf : IsCompletelyMonotoneOn f) {c : ℝ} (hc : 0 ≤ c) :
    IsCompletelyMonotoneOn (fun t => f (t + c)) := by
  have hmaps : MapsTo (fun t : ℝ => t + c) (Ioi 0) (Ioi 0) := fun t ht => by
    simp only [mem_Ioi] at ht ⊢
    linarith
  refine ⟨hf.1.comp (contDiffOn_id.add contDiffOn_const) hmaps, fun n t ht => ?_⟩
  rw [iteratedDeriv_comp_add_const]
  exact hf.2 n (t + c) (by linarith)

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

theorem const {c : ℝ} (hc : 0 ≤ c) : IsCompletelyMonotoneOn (fun _ => c) := by
  refine ⟨contDiffOn_const, fun n t _ => ?_⟩
  rw [iteratedDeriv_const]
  split_ifs with h
  · subst h
    simpa using hc
  · simp

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

lemma deriv_exp_neg_mul (a : ℝ) : deriv (fun t => Real.exp (-(a * t))) = fun t => -a * Real.exp (-(a * t)) := by
  refine funext fun t => ?_
  have h1 : HasDerivAt (fun t : ℝ => -(a * t)) (-a) t := by
    simpa using (hasDerivAt_id' t).const_mul (-a)
  show deriv _ t = -a * Real.exp (-(a * t))
  rw [h1.exp.deriv]
  ring

lemma iteratedDeriv_exp_neg_mul (a : ℝ) (n : ℕ) :
    iteratedDeriv n (fun t => Real.exp (-(a * t))) = fun t => (-a) ^ n * Real.exp (-(a * t)) := by
  induction n with
  | zero => funext t; simp
  | succ n ih =>
    funext t
    rw [iteratedDeriv_succ', deriv_exp_neg_mul, iteratedDeriv_const_mul_field, ih]
    simp only [pow_succ]
    ring

/-- `e^{-a t}` is completely monotone for `a ≥ 0` (native proof). -/
theorem exp_neg_mul {a : ℝ} (ha : 0 ≤ a) : IsCompletelyMonotoneOn (fun t => Real.exp (-(a * t))) := by
  refine ⟨by fun_prop, fun n t _ => ?_⟩
  rw [iteratedDeriv_exp_neg_mul]
  show 0 ≤ (-1 : ℝ) ^ n * ((-a) ^ n * Real.exp (-(a * t)))
  have e : (-1 : ℝ) ^ n * ((-a) ^ n * Real.exp (-(a * t))) = a ^ n * Real.exp (-(a * t)) := by
    rw [← mul_assoc, ← mul_pow]
    ring
  rw [e]
  exact mul_nonneg (pow_nonneg ha n) (Real.exp_pos _).le

/-- `t^{-s}` is completely monotone for `s ≥ 0` (native proof, Pochhammer form of the derivatives). -/
theorem rpow_neg {s : ℝ} (hs : 0 ≤ s) : IsCompletelyMonotoneOn (fun t => t ^ (-s)) := by
  rcases hs.lt_or_eq with hs | rfl
  · refine ⟨fun x hx => (Real.contDiffAt_rpow_const_of_ne (ne_of_gt hx)).contDiffWithinAt, fun r t ht => ?_⟩
    rw [iteratedDeriv_eq_iterate, Real.iter_deriv_rpow_const]
    have hasc := ascPochhammer_eval_neg_eq_descPochhammer (R := ℝ) (-s) r
    rw [neg_neg] at hasc
    have h1 : ((-1 : ℝ) ^ r) * ((-1) ^ r) = 1 := by rw [← mul_pow]; norm_num
    have hdesc : (descPochhammer ℝ r).eval (-s) = (-1) ^ r * (ascPochhammer ℝ r).eval s := by
      calc (descPochhammer ℝ r).eval (-s)
          = ((-1) ^ r * (-1) ^ r) * (descPochhammer ℝ r).eval (-s) := by rw [h1, one_mul]
        _ = (-1) ^ r * (ascPochhammer ℝ r).eval s := by rw [hasc]; ring
    rw [hdesc]
    have hpos := ascPochhammer_pos r s hs
    have hpow := Real.rpow_pos_of_pos ht (-s - r)
    calc (0 : ℝ) ≤ (ascPochhammer ℝ r).eval s * t ^ (-s - r) := by positivity
      _ = (-1) ^ r * ((-1) ^ r * (ascPochhammer ℝ r).eval s * t ^ (-s - r)) := by
        rw [← mul_assoc, ← mul_assoc, h1, one_mul]
  · exact (const zero_le_one).congr' fun t _ => by simp

/-! ## Bernstein functions and subordination -/

namespace IsBernsteinOn

variable {g : ℝ → ℝ}

theorem contDiffAt (hg : IsBernsteinOn g) {t : ℝ} (ht : 0 < t) (n : ℕ) : ContDiffAt ℝ n g t :=
  (hg.1.contDiffAt (Ioi_mem_nhds ht)).of_le (by exact_mod_cast le_top)

theorem hasDerivAt (hg : IsBernsteinOn g) {t : ℝ} (ht : 0 < t) : HasDerivAt g (deriv g t) t :=
  ((hg.contDiffAt ht 1).differentiableAt (by simp)).hasDerivAt

theorem comp_sign (hg : IsBernsteinOn g) (hpos : ∀ t, 0 < t → 0 < g t) :
    ∀ n : ℕ, ∀ f : ℝ → ℝ, IsCompletelyMonotoneOn f → ∀ m ≤ n, ∀ t : ℝ, 0 < t →
      0 ≤ (-1 : ℝ) ^ m * iteratedDeriv m (fun t => f (g t)) t := by
  intro n
  induction n with
  | zero =>
    intro f hf m hm t ht
    rw [Nat.le_zero.mp hm]
    simpa using hf.nonneg (hpos t ht)
  | succ n ih =>
    intro f hf m hm t ht
    rcases Nat.lt_or_eq_of_le hm with hlt | rfl
    · exact ih f hf m (Nat.lt_succ_iff.mp hlt) t ht
    · have hF : IsCompletelyMonotoneOn (fun u => -deriv f u) := hf.neg_deriv
      have hEq : EqOn (deriv (fun t => f (g t)))
          (-((fun t => -deriv f (g t)) * deriv g)) (Ioi 0) := by
        intro s hs
        have h1 : HasDerivAt f (deriv f (g s)) (g s) := (hf.differentiableAt (hpos s hs)).hasDerivAt
        have h3 : HasDerivAt (fun t => f (g t)) (deriv f (g s) * deriv g s) s :=
          h1.comp s (hg.hasDerivAt hs)
        rw [h3.deriv]
        simp
      rw [iteratedDeriv_succ', hEq.iteratedDeriv_of_isOpen isOpen_Ioi n ht, iteratedDeriv_neg]
      have hFg : ContDiffOn ℝ (⊤ : ℕ∞) (fun t => -deriv f (g t)) (Ioi 0) :=
        hF.1.comp hg.1 (fun s hs => hpos s hs)
      have key : 0 ≤ (-1 : ℝ) ^ n * iteratedDeriv n ((fun t => -deriv f (g t)) * deriv g) t :=
        mul_sign n ((hFg.contDiffAt (Ioi_mem_nhds ht)).of_le (by exact_mod_cast le_top))
          (hg.2.2.contDiffAt ht n) (fun i hi => ih (fun u => -deriv f u) hF i hi t ht)
          (fun i _ => hg.2.2.2 i t ht)
      calc (0 : ℝ) ≤ (-1) ^ n * iteratedDeriv n ((fun t => -deriv f (g t)) * deriv g) t := key
        _ = (-1) ^ (n + 1) * -iteratedDeriv n ((fun t => -deriv f (g t)) * deriv g) t := by ring

theorem affine {a b : ℝ} (ha : 0 ≤ a) (hb : 0 ≤ b) : IsBernsteinOn (fun t => a * t + b) := by
  have hd : deriv (fun t : ℝ => a * t + b) = fun _ => a := by
    funext t
    have h : HasDerivAt (fun t : ℝ => a * t + b) a t := by
      simpa using ((hasDerivAt_id t).const_mul a).add_const b
    exact h.deriv
  refine ⟨by fun_prop, fun t ht => add_nonneg (mul_nonneg ha ht.le) hb, ?_⟩
  rw [hd]
  exact const ha

theorem rpow {α : ℝ} (h0 : 0 ≤ α) (h1 : α ≤ 1) : IsBernsteinOn (fun t => t ^ α) := by
  refine ⟨fun t ht => (Real.contDiffAt_rpow_const_of_ne (ne_of_gt ht)).contDiffWithinAt,
    fun t ht => Real.rpow_nonneg (le_of_lt ht) _, ?_⟩
  have hcm : IsCompletelyMonotoneOn (fun t => α * t ^ (-(1 - α))) := (rpow_neg (by linarith)).const_mul h0
  refine hcm.congr' fun t ht => ?_
  rw [(Real.hasDerivAt_rpow_const (Or.inl ht.ne')).deriv, show -(1 - α) = α - 1 by ring]

theorem sqrt : IsBernsteinOn Real.sqrt := by
  have h : Real.sqrt = fun t => t ^ (1 / (2 : ℝ)) := funext Real.sqrt_eq_rpow
  rw [h]
  exact rpow (by norm_num) (by norm_num)

end IsBernsteinOn

/-- **Subordination.** CM ∘ positive Bernstein is CM. -/
theorem IsCompletelyMonotoneOn.comp_bernstein {f g : ℝ → ℝ} (hf : IsCompletelyMonotoneOn f)
    (hg : IsBernsteinOn g) (hpos : ∀ t, 0 < t → 0 < g t) : IsCompletelyMonotoneOn (fun t => f (g t)) :=
  ⟨hf.1.comp hg.1 (fun s hs => hpos s hs), fun n t ht => hg.comp_sign hpos n f hf n le_rfl t ht⟩

/-! ## Laplace mixtures (analytic core ported from `Autoresearch/KeldyshCM.lean`) -/

section Laplace

variable {α : Type*} [MeasurableSpace α] {μ : Measure α} {k m : α → ℝ}

/-- The candidate `n`-th derivative `∫ (-k)^n e^{-t k} m dμ`. -/
noncomputable def G (μ : Measure α) (k m : α → ℝ) (n : ℕ) (t : ℝ) : ℝ :=
  ∫ x, (-(k x)) ^ n * Real.exp (-(t * k x)) * m x ∂μ

lemma pow_mul_exp_neg_le {u c : ℝ} (hu : 0 ≤ u) (hc : 0 < c) (N : ℕ) :
    u ^ N * Real.exp (-(c * u)) ≤ (N.factorial : ℝ) / c ^ N := by
  have hE := Real.pow_div_factorial_le_exp _ (mul_nonneg hc.le hu) N
  have hf : (0 : ℝ) < N.factorial := by exact_mod_cast Nat.factorial_pos N
  have hcN : 0 < c ^ N := pow_pos hc N
  rw [div_le_iff₀ hf, mul_pow] at hE
  rw [Real.exp_neg, le_div_iff₀ hcN]
  have hex := Real.exp_pos (c * u)
  calc u ^ N * (Real.exp (c * u))⁻¹ * c ^ N = (c ^ N * u ^ N) * (Real.exp (c * u))⁻¹ := by ring
    _ ≤ (Real.exp (c * u) * N.factorial) * (Real.exp (c * u))⁻¹ :=
        mul_le_mul_of_nonneg_right hE (inv_nonneg.mpr hex.le)
    _ = N.factorial := by field_simp

/-- Hypotheses of the Laplace lemma: only exponential integrability is assumed. -/
structure LaplaceData (μ : Measure α) (k m : α → ℝ) : Prop where
  k_meas : Measurable k
  m_meas : Measurable m
  k_nonneg : ∀ᵐ x ∂μ, 0 ≤ k x
  m_nonneg : ∀ᵐ x ∂μ, 0 ≤ m x
  integrable : ∀ c : ℝ, 0 < c → Integrable (fun x => Real.exp (-(c * k x)) * m x) μ

lemma integrand_meas (h : LaplaceData μ k m) (n : ℕ) (t : ℝ) :
    AEStronglyMeasurable (fun x => (-(k x)) ^ n * Real.exp (-(t * k x)) * m x) μ := by
  have hk := h.k_meas
  have hm := h.m_meas
  exact (by fun_prop : Measurable fun x => (-(k x)) ^ n * Real.exp (-(t * k x)) * m x).aestronglyMeasurable

lemma norm_integrand {n : ℕ} {t kx mx : ℝ} (hk : 0 ≤ kx) (hm : 0 ≤ mx) :
    ‖(-kx) ^ n * Real.exp (-(t * kx)) * mx‖ = kx ^ n * Real.exp (-(t * kx)) * mx := by
  rw [Real.norm_eq_abs, abs_mul, abs_mul, abs_pow, abs_neg, abs_of_nonneg hk, abs_of_nonneg hm,
    abs_of_pos (Real.exp_pos _)]

/-- All moments from exponential integrability. -/
lemma integrable_pow_mul (h : LaplaceData μ k m) (n : ℕ) {c : ℝ} (hc : 0 < c) :
    Integrable (fun x => k x ^ n * Real.exp (-(c * k x)) * m x) μ := by
  have hk := h.k_meas
  have hm := h.m_meas
  have hc2 : 0 < c / 2 := by linarith
  refine ((h.integrable (c / 2) hc2).const_mul ((n.factorial : ℝ) / (c / 2) ^ n)).mono'
    (by fun_prop : Measurable fun x => k x ^ n * Real.exp (-(c * k x)) * m x).aestronglyMeasurable ?_
  filter_upwards [h.k_nonneg, h.m_nonneg] with x hkx hmx
  have hnn : 0 ≤ k x ^ n * Real.exp (-(c * k x)) * m x :=
    mul_nonneg (mul_nonneg (pow_nonneg hkx n) (Real.exp_pos _).le) hmx
  rw [Real.norm_eq_abs, abs_of_nonneg hnn]
  have hsplit : Real.exp (-(c * k x)) = Real.exp (-(c / 2 * k x)) * Real.exp (-(c / 2 * k x)) := by
    rw [← Real.exp_add]
    congr 1
    ring
  have hb := pow_mul_exp_neg_le hkx hc2 n
  calc k x ^ n * Real.exp (-(c * k x)) * m x
      = (k x ^ n * Real.exp (-(c / 2 * k x))) * (Real.exp (-(c / 2 * k x)) * m x) := by
        rw [hsplit]
        ring
    _ ≤ ((n.factorial : ℝ) / (c / 2) ^ n) * (Real.exp (-(c / 2 * k x)) * m x) :=
        mul_le_mul_of_nonneg_right hb (mul_nonneg (Real.exp_pos _).le hmx)

lemma integrable_integrand (h : LaplaceData μ k m) (n : ℕ) {t : ℝ} (ht : 0 < t) :
    Integrable (fun x => (-(k x)) ^ n * Real.exp (-(t * k x)) * m x) μ := by
  refine (integrable_pow_mul h n ht).mono' (integrand_meas h n t) ?_
  filter_upwards [h.k_nonneg, h.m_nonneg] with x hkx hmx
  exact (norm_integrand hkx hmx).le

lemma hasDerivAt_G (h : LaplaceData μ k m) (n : ℕ) {t : ℝ} (ht : 0 < t) :
    HasDerivAt (G μ k m n) (G μ k m (n + 1) t) t := by
  have hs : Ioi (t / 2) ∈ 𝓝 t := Ioi_mem_nhds (by linarith)
  have key := hasDerivAt_integral_of_dominated_loc_of_deriv_le (μ := μ) (x₀ := t)
    (F := fun s x => (-(k x)) ^ n * Real.exp (-(s * k x)) * m x)
    (F' := fun s x => (-(k x)) ^ (n + 1) * Real.exp (-(s * k x)) * m x)
    (bound := fun x => k x ^ (n + 1) * Real.exp (-(t / 2 * k x)) * m x) hs
    (Eventually.of_forall fun s => integrand_meas h n s)
    (integrable_integrand h n ht)
    (integrand_meas h (n + 1) t)
    (by
      filter_upwards [h.k_nonneg, h.m_nonneg] with x hkx hmx
      intro s hs'
      rw [norm_integrand hkx hmx]
      have hst : t / 2 * k x ≤ s * k x := mul_le_mul_of_nonneg_right (le_of_lt hs') hkx
      have he : Real.exp (-(s * k x)) ≤ Real.exp (-(t / 2 * k x)) := Real.exp_le_exp.mpr (by linarith)
      have hp : 0 ≤ k x ^ (n + 1) := pow_nonneg hkx _
      exact mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left he hp) hmx)
    (integrable_pow_mul h (n + 1) (by linarith : 0 < t / 2))
    (Eventually.of_forall fun x s _ => by
      have h1 : HasDerivAt (fun y => -(y * k x)) (-(k x)) s := (hasDerivAt_mul_const (k x)).neg
      have h2 := (h1.exp.const_mul ((-(k x)) ^ n)).mul_const (m x)
      convert h2 using 1
      ring)
  exact key.2

lemma contDiffOn_G (h : LaplaceData μ k m) : ∀ (N n : ℕ), ContDiffOn ℝ N (G μ k m n) (Ioi 0) := by
  intro N
  induction N with
  | zero =>
    intro n
    rw [Nat.cast_zero, contDiffOn_zero]
    exact fun t ht => (hasDerivAt_G h n ht).continuousAt.continuousWithinAt
  | succ N ih =>
    intro n
    rw [Nat.cast_succ, contDiffOn_succ_iff_deriv_of_isOpen isOpen_Ioi]
    refine ⟨fun t ht => (hasDerivAt_G h n ht).differentiableAt.differentiableWithinAt, ?_, ?_⟩
    · intro hω
      exact absurd hω (by simp)
    · exact (ih (n + 1)).congr (fun t ht => (hasDerivAt_G h n ht).deriv)

lemma iteratedDeriv_G (h : LaplaceData μ k m) :
    ∀ n : ℕ, EqOn (iteratedDeriv n (G μ k m 0)) (G μ k m n) (Ioi 0) := by
  intro n
  induction n with
  | zero => intro t _; simp
  | succ n ih =>
    intro t ht
    rw [iteratedDeriv_succ]
    have hev : iteratedDeriv n (G μ k m 0) =ᶠ[𝓝 t] G μ k m n :=
      Filter.eventuallyEq_of_mem (isOpen_Ioi.mem_nhds ht) ih
    rw [hev.deriv_eq]
    exact (hasDerivAt_G h n ht).deriv

lemma G_sign (h : LaplaceData μ k m) (n : ℕ) (t : ℝ) : 0 ≤ (-1 : ℝ) ^ n * G μ k m n t := by
  unfold G
  rw [← integral_const_mul]
  refine integral_nonneg_of_ae ?_
  filter_upwards [h.k_nonneg, h.m_nonneg] with x hkx hmx
  have e1 : (-1 : ℝ) ^ n * (-(k x)) ^ n = k x ^ n := by rw [← mul_pow]; simp
  have : (-1 : ℝ) ^ n * ((-(k x)) ^ n * Real.exp (-(t * k x)) * m x) =
      k x ^ n * Real.exp (-(t * k x)) * m x := by rw [← e1]; ring
  simp only [Pi.zero_apply]
  rw [this]
  exact mul_nonneg (mul_nonneg (pow_nonneg hkx _) (Real.exp_pos _).le) hmx

/-- **Laplace mixtures.** `t ↦ ∫ e^{-t k} m dμ` is completely monotone under `LaplaceData`. -/
theorem laplace (h : LaplaceData μ k m) :
    IsCompletelyMonotoneOn (fun t => ∫ x, Real.exp (-(t * k x)) * m x ∂μ) := by
  have hg : (fun t => ∫ x, Real.exp (-(t * k x)) * m x ∂μ) = G μ k m 0 := by
    funext t
    simp [G]
  rw [hg]
  refine ⟨contDiffOn_infty.mpr (fun N => contDiffOn_G h N 0), fun r t ht => ?_⟩
  rw [iteratedDeriv_G h r ht]
  exact G_sign h r t

end Laplace

end ProgCMCore

#print axioms ProgCMCore.mul_sign
#print axioms ProgCMCore.IsCompletelyMonotoneOn.nonneg
#print axioms ProgCMCore.IsCompletelyMonotoneOn.contDiffAt
#print axioms ProgCMCore.IsCompletelyMonotoneOn.differentiableAt
#print axioms ProgCMCore.IsCompletelyMonotoneOn.hasDerivAt_iteratedDeriv
#print axioms ProgCMCore.IsCompletelyMonotoneOn.congr'
#print axioms ProgCMCore.IsCompletelyMonotoneOn.const_mul
#print axioms ProgCMCore.IsCompletelyMonotoneOn.add
#print axioms ProgCMCore.IsCompletelyMonotoneOn.mul
#print axioms ProgCMCore.IsCompletelyMonotoneOn.comp_add_const
#print axioms ProgCMCore.IsCompletelyMonotoneOn.neg_deriv
#print axioms ProgCMCore.IsCompletelyMonotoneOn.antitoneOn_sign
#print axioms ProgCMCore.IsCompletelyMonotoneOn.sub_comp_add_const
#print axioms ProgCMCore.const
#print axioms ProgCMCore.sum
#print axioms ProgCMCore.deriv_exp_neg_mul
#print axioms ProgCMCore.iteratedDeriv_exp_neg_mul
#print axioms ProgCMCore.exp_neg_mul
#print axioms ProgCMCore.rpow_neg
#print axioms ProgCMCore.IsBernsteinOn.contDiffAt
#print axioms ProgCMCore.IsBernsteinOn.hasDerivAt
#print axioms ProgCMCore.IsBernsteinOn.comp_sign
#print axioms ProgCMCore.IsBernsteinOn.affine
#print axioms ProgCMCore.IsBernsteinOn.rpow
#print axioms ProgCMCore.IsBernsteinOn.sqrt
#print axioms ProgCMCore.IsCompletelyMonotoneOn.comp_bernstein
#print axioms ProgCMCore.pow_mul_exp_neg_le
#print axioms ProgCMCore.integrand_meas
#print axioms ProgCMCore.norm_integrand
#print axioms ProgCMCore.integrable_pow_mul
#print axioms ProgCMCore.integrable_integrand
#print axioms ProgCMCore.hasDerivAt_G
#print axioms ProgCMCore.contDiffOn_G
#print axioms ProgCMCore.iteratedDeriv_G
#print axioms ProgCMCore.G_sign
#print axioms ProgCMCore.laplace
