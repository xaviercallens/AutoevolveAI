import Programmes.CompletelyMonotone.Basic

/-!
# Programme P3: Bernstein functions and subordination

`IsBernsteinOn g`: `g` is `C^∞` on `(0, ∞)`, `g ≥ 0` there, and `g'` is completely monotone on `(0, ∞)`.

**Main theorem (`IsCompletelyMonotoneOn.comp_bernstein`, general).** If `f` is completely monotone and `g` is a
Bernstein function with `g > 0` on `(0, ∞)`, then `f ∘ g` is completely monotone. The positivity hypothesis cannot
be dropped in this formalisation: `f` is only constrained on `(0, ∞)`, and `g ≡ 0` is a Bernstein function, so
`f ∘ 0` would be the junk value `f 0`. The proof avoids Faà di Bruno: strong induction on the order, quantified over
*all* completely monotone `f`, using `(f ∘ g)' = -((-f') ∘ g) · g'`, the induction hypothesis for the completely
monotone `-f'`, and the Leibniz sign lemma.

Instances: `affine` (`a t + b`, `a, b ≥ 0`), `rpow` (`t^α`, `0 ≤ α ≤ 1`), `sqrt`. Closure: `add`, `const_mul`,
`comp` (Bernstein ∘ Bernstein). Corollary: `exp_neg_comp` (`e^{-a ψ}` is completely monotone).
-/

namespace ProgCM

open Set Filter Topology IsCompletelyMonotoneOn

/-- `g` is a Bernstein function on `(0, ∞)`: `C^∞`, nonnegative, with completely monotone derivative. -/
def IsBernsteinOn (g : ℝ → ℝ) : Prop :=
  ContDiffOn ℝ (⊤ : ℕ∞) g (Set.Ioi 0) ∧ (∀ t : ℝ, 0 < t → 0 ≤ g t) ∧ IsCompletelyMonotoneOn (deriv g)

namespace IsBernsteinOn

variable {f g : ℝ → ℝ}

theorem contDiffAt (hg : IsBernsteinOn g) {t : ℝ} (ht : 0 < t) (n : ℕ) : ContDiffAt ℝ n g t :=
  (hg.1.contDiffAt (Ioi_mem_nhds ht)).of_le (by exact_mod_cast le_top)

theorem hasDerivAt (hg : IsBernsteinOn g) {t : ℝ} (ht : 0 < t) : HasDerivAt g (deriv g t) t :=
  ((hg.contDiffAt ht 1).differentiableAt (by simp)).hasDerivAt

theorem nonneg (hg : IsBernsteinOn g) {t : ℝ} (ht : 0 < t) : 0 ≤ g t := hg.2.1 t ht

/-- Bernstein functions are nondecreasing on `(0, ∞)`. -/
theorem monotoneOn (hg : IsBernsteinOn g) : MonotoneOn g (Ioi 0) := by
  refine monotoneOn_of_deriv_nonneg (convex_Ioi 0) (fun t ht => (hg.hasDerivAt ht).continuousAt.continuousWithinAt)
    ?_ ?_
  · rw [interior_Ioi]
    exact fun t ht => (hg.hasDerivAt ht).differentiableAt.differentiableWithinAt
  · rw [interior_Ioi]
    exact fun t ht => hg.2.2.nonneg ht

/-- The sign statement behind the composition theorem, by strong induction on the order. -/
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
        AutoresearchYukawa.mul_sign n ((hFg.contDiffAt (Ioi_mem_nhds ht)).of_le (by exact_mod_cast le_top))
          (hg.2.2.contDiffAt ht n) (fun i hi => ih (fun u => -deriv f u) hF i hi t ht)
          (fun i _ => hg.2.2.2 i t ht)
      calc (0 : ℝ) ≤ (-1) ^ n * iteratedDeriv n ((fun t => -deriv f (g t)) * deriv g) t := key
        _ = (-1) ^ (n + 1) * -iteratedDeriv n ((fun t => -deriv f (g t)) * deriv g) t := by ring

end IsBernsteinOn

/-- **Subordination (general).** A completely monotone function composed with a positive Bernstein function is
completely monotone. -/
theorem IsCompletelyMonotoneOn.comp_bernstein {f g : ℝ → ℝ} (hf : IsCompletelyMonotoneOn f)
    (hg : IsBernsteinOn g) (hpos : ∀ t, 0 < t → 0 < g t) : IsCompletelyMonotoneOn (fun t => f (g t)) :=
  ⟨hf.1.comp hg.1 (fun s hs => hpos s hs), fun n t ht => hg.comp_sign hpos n f hf n le_rfl t ht⟩

namespace IsBernsteinOn

variable {f g : ℝ → ℝ}

/-- `t ↦ a t + b` is Bernstein for `a, b ≥ 0`. -/
theorem affine {a b : ℝ} (ha : 0 ≤ a) (hb : 0 ≤ b) : IsBernsteinOn (fun t => a * t + b) := by
  have hd : deriv (fun t : ℝ => a * t + b) = fun _ => a := by
    funext t
    have h : HasDerivAt (fun t : ℝ => a * t + b) a t := by
      simpa using ((hasDerivAt_id t).const_mul a).add_const b
    exact h.deriv
  refine ⟨by fun_prop, fun t ht => add_nonneg (mul_nonneg ha ht.le) hb, ?_⟩
  rw [hd]
  exact const ha

/-- `t ↦ t^α` is Bernstein for `0 ≤ α ≤ 1`. -/
theorem rpow {α : ℝ} (h0 : 0 ≤ α) (h1 : α ≤ 1) : IsBernsteinOn (fun t => t ^ α) := by
  refine ⟨fun t ht => (Real.contDiffAt_rpow_const_of_ne (ne_of_gt ht)).contDiffWithinAt,
    fun t ht => Real.rpow_nonneg (le_of_lt ht) _, ?_⟩
  have hcm : IsCompletelyMonotoneOn (fun t => α * t ^ (-(1 - α))) := (rpow_neg (by linarith)).const_mul h0
  refine hcm.congr' fun t ht => ?_
  rw [(Real.hasDerivAt_rpow_const (Or.inl ht.ne')).deriv, show -(1 - α) = α - 1 by ring]

/-- `√` is a Bernstein function. -/
theorem sqrt : IsBernsteinOn Real.sqrt := by
  have h : Real.sqrt = fun t => t ^ (1 / (2 : ℝ)) := funext Real.sqrt_eq_rpow
  rw [h]
  exact rpow (by norm_num) (by norm_num)

/-- Sum of Bernstein functions. -/
theorem add (hf : IsBernsteinOn f) (hg : IsBernsteinOn g) : IsBernsteinOn (f + g) := by
  refine ⟨hf.1.add hg.1, fun t ht => add_nonneg (hf.2.1 t ht) (hg.2.1 t ht), ?_⟩
  refine (hf.2.2.add hg.2.2).congr fun t ht => ?_
  exact (((hf.hasDerivAt ht).add (hg.hasDerivAt ht)).deriv).symm

/-- Nonnegative multiple of a Bernstein function. -/
theorem const_mul (hf : IsBernsteinOn f) {c : ℝ} (hc : 0 ≤ c) : IsBernsteinOn (fun t => c * f t) := by
  refine ⟨contDiffOn_const.mul hf.1, fun t ht => mul_nonneg hc (hf.2.1 t ht), ?_⟩
  refine (hf.2.2.const_mul hc).congr fun t ht => ?_
  exact (((hf.hasDerivAt ht).const_mul c).deriv).symm

/-- **Bernstein ∘ Bernstein** (inner function positive) is Bernstein. -/
theorem comp (hf : IsBernsteinOn f) (hg : IsBernsteinOn g) (hpos : ∀ t, 0 < t → 0 < g t) :
    IsBernsteinOn (fun t => f (g t)) := by
  refine ⟨hf.1.comp hg.1 (fun s hs => hpos s hs), fun t ht => hf.2.1 (g t) (hpos t ht), ?_⟩
  have h := (hf.2.2.comp_bernstein hg hpos).mul hg.2.2
  refine h.congr fun t ht => ?_
  have h3 : HasDerivAt (fun t => f (g t)) (deriv f (g t) * deriv g t) t :=
    (hf.hasDerivAt (hpos t ht)).comp t (hg.hasDerivAt ht)
  rw [h3.deriv]
  rfl

end IsBernsteinOn

/-- `t ↦ e^{-a ψ(t)}` is completely monotone for `a ≥ 0` and `ψ` a positive Bernstein function. -/
theorem exp_neg_comp {ψ : ℝ → ℝ} {a : ℝ} (ha : 0 ≤ a) (hψ : IsBernsteinOn ψ) (hpos : ∀ t, 0 < t → 0 < ψ t) :
    IsCompletelyMonotoneOn (fun t => Real.exp (-(a * ψ t))) :=
  (exp_neg_mul ha).comp_bernstein hψ hpos

/-- Special case `ψ = a t + b`: `f (a t + b)` is completely monotone for `a > 0`, `b ≥ 0`. -/
theorem IsCompletelyMonotoneOn.comp_affine {f : ℝ → ℝ} (hf : IsCompletelyMonotoneOn f) {a b : ℝ} (ha : 0 < a)
    (hb : 0 ≤ b) : IsCompletelyMonotoneOn (fun t => f (a * t + b)) :=
  hf.comp_bernstein (IsBernsteinOn.affine ha.le hb) (fun _ ht => add_pos_of_pos_of_nonneg (mul_pos ha ht) hb)

/-- Special case `ψ = √`: `f (√t)` is completely monotone. -/
theorem IsCompletelyMonotoneOn.comp_sqrt {f : ℝ → ℝ} (hf : IsCompletelyMonotoneOn f) :
    IsCompletelyMonotoneOn (fun t => f (Real.sqrt t)) :=
  hf.comp_bernstein IsBernsteinOn.sqrt (fun _ ht => Real.sqrt_pos.mpr ht)

/-- **Positive control.** `exp(-κ √t)` is completely monotone (`κ ≥ 0`): a one-line re-derivation of
`AutoresearchYukawa.phi_admissible` (which needed `κ > 0`) via subordination, replacing its bespoke induction. -/
theorem phi_cm {κ : ℝ} (hκ : 0 ≤ κ) : IsCompletelyMonotoneOn (AutoresearchYukawa.phi κ) :=
  ((exp_neg_mul hκ).comp_sqrt).congr' fun t _ => by simp only [AutoresearchYukawa.phi, neg_mul]

end ProgCM

#print axioms ProgCM.IsBernsteinOn.monotoneOn
#print axioms ProgCM.IsBernsteinOn.comp_sign
#print axioms ProgCM.IsCompletelyMonotoneOn.comp_bernstein
#print axioms ProgCM.IsBernsteinOn.affine
#print axioms ProgCM.IsBernsteinOn.rpow
#print axioms ProgCM.IsBernsteinOn.sqrt
#print axioms ProgCM.IsBernsteinOn.add
#print axioms ProgCM.IsBernsteinOn.const_mul
#print axioms ProgCM.IsBernsteinOn.comp
#print axioms ProgCM.exp_neg_comp
#print axioms ProgCM.IsCompletelyMonotoneOn.comp_affine
#print axioms ProgCM.IsCompletelyMonotoneOn.comp_sqrt
#print axioms ProgCM.phi_cm
#print axioms ProgCM.IsBernsteinOn.contDiffAt
#print axioms ProgCM.IsBernsteinOn.hasDerivAt
#print axioms ProgCM.IsBernsteinOn.nonneg
