import Programmes.CompletelyMonotone.Basic

/-!
# Programme P3: limits of completely monotone functions

* `of_tendsto_iteratedDeriv` (hypothesis-heavy): if the limit `f` is already known to be `C^∞` on `(0, ∞)` and every
  derivative converges pointwise, then `f` is completely monotone (closedness of `[0, ∞)`).
* `of_tendstoLocallyUniformlyOn` (the useful one): if for every `n` the `n`-th derivatives of a sequence of
  completely monotone functions converge locally uniformly on `(0, ∞)` to some `G n`, and `f = G 0` on `(0, ∞)`, then
  `f` is completely monotone and `f^{(n)} = G n` on `(0, ∞)`. Smoothness of the limit is *derived* (Mathlib's
  `hasDerivAt_of_tendstoLocallyUniformlyOn`), not assumed.

Not proved: the classical statement that a merely *pointwise* limit of completely monotone functions is completely
monotone (it needs Bernstein–Widder / Helly selection or a difference-operator characterisation).
-/

namespace ProgCM

open Set Filter Topology IsCompletelyMonotoneOn

/-- Pointwise limits of all derivatives, smooth limit assumed. -/
theorem of_tendsto_iteratedDeriv {ι : Type*} {l : Filter ι} [l.NeBot] {F : ι → ℝ → ℝ} {f : ℝ → ℝ}
    (hF : ∀ i, IsCompletelyMonotoneOn (F i)) (hf : ContDiffOn ℝ (⊤ : ℕ∞) f (Ioi 0))
    (hlim : ∀ (n : ℕ) (t : ℝ), 0 < t →
      Tendsto (fun i => iteratedDeriv n (F i) t) l (𝓝 (iteratedDeriv n f t))) :
    IsCompletelyMonotoneOn f :=
  ⟨hf, fun n t ht => ge_of_tendsto ((hlim n t ht).const_mul _) (Eventually.of_forall fun i => (hF i).2 n t ht)⟩

/-- **Locally uniform limits.** -/
theorem of_tendstoLocallyUniformlyOn {F G : ℕ → ℝ → ℝ} {f : ℝ → ℝ}
    (hF : ∀ k, IsCompletelyMonotoneOn (F k))
    (hG : ∀ n : ℕ, TendstoLocallyUniformlyOn (fun k => iteratedDeriv n (F k)) (G n) atTop (Ioi 0))
    (hf : EqOn f (G 0) (Ioi 0)) :
    IsCompletelyMonotoneOn f ∧ ∀ n : ℕ, EqOn (iteratedDeriv n f) (G n) (Ioi 0) := by
  have hderiv : ∀ (n : ℕ) (t : ℝ), 0 < t → HasDerivAt (G n) (G (n + 1) t) t := fun n t ht =>
    hasDerivAt_of_tendstoLocallyUniformlyOn (f := fun k => iteratedDeriv n (F k))
      (f' := fun k => iteratedDeriv (n + 1) (F k)) isOpen_Ioi (hG (n + 1))
      (Eventually.of_forall fun k x hx => (hF k).hasDerivAt_iteratedDeriv n hx)
      (fun x hx => (hG n).tendsto_at hx) ht
  have hiter : ∀ n : ℕ, EqOn (iteratedDeriv n (G 0)) (G n) (Ioi 0) := by
    intro n
    induction n with
    | zero => intro t _; simp
    | succ n ih =>
      intro t ht
      rw [iteratedDeriv_succ]
      have hev : iteratedDeriv n (G 0) =ᶠ[𝓝 t] G n :=
        Filter.eventuallyEq_of_mem (isOpen_Ioi.mem_nhds ht) ih
      rw [hev.deriv_eq]
      exact (hderiv n t ht).deriv
  have hcont : ∀ (N n : ℕ), ContDiffOn ℝ N (G n) (Ioi 0) := by
    intro N
    induction N with
    | zero =>
      intro n
      rw [Nat.cast_zero, contDiffOn_zero]
      exact fun t ht => (hderiv n t ht).continuousAt.continuousWithinAt
    | succ N ih =>
      intro n
      rw [Nat.cast_succ, contDiffOn_succ_iff_deriv_of_isOpen isOpen_Ioi]
      refine ⟨fun t ht => (hderiv n t ht).differentiableAt.differentiableWithinAt, ?_, ?_⟩
      · intro hω
        exact absurd hω (by simp)
      · exact (ih (n + 1)).congr (fun t ht => (hderiv n t ht).deriv)
  have hG0 : IsCompletelyMonotoneOn (G 0) := by
    refine ⟨contDiffOn_infty.mpr fun N => hcont N 0, fun n t ht => ?_⟩
    rw [hiter n ht]
    exact ge_of_tendsto (((hG n).tendsto_at ht).const_mul _) (Eventually.of_forall fun k => (hF k).2 n t ht)
  refine ⟨hG0.congr fun t ht => (hf ht).symm, fun n t ht => ?_⟩
  rw [hf.iteratedDeriv_of_isOpen isOpen_Ioi n ht]
  exact hiter n ht

end ProgCM

#print axioms ProgCM.of_tendsto_iteratedDeriv
#print axioms ProgCM.of_tendstoLocallyUniformlyOn
