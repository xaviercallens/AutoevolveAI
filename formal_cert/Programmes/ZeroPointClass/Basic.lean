import Programmes.ZeroPointCert.Basic
import Mathlib.Analysis.Convex.Deriv
import Mathlib.Topology.Order.IntermediateValue
import Mathlib.Tactic

/-!
# N1 (proposal 3, 2026-10-26): zero-point classification for Gaussian potentials — the kernel-checked logic

Setting (fixed in `results/proposal3/2026-10-26/N1/CLASSIFICATION.md`). For the Gaussian `exp(-π a r²)` let
`E a t` be the harmonic zero-point energy of `L_t = P_t L_ρ` (`P_t` the unimodular shear of B2) and
`F a t = ∂²ₜ E a t` its exact second variation along the path. The ball-arithmetic code `n1_certify.py` produces,
for a list of `a`-intervals, two-sided rational enclosures of `F a t` valid for every `a` in the interval and every
`|t| ≤ t₀`.

What is in this file (Tier A, all kernel-checked; no numbers):

* `window_upper`, `window_lower` : a second derivative bounded above (below) by `B` on `[-t₀, t₀]` gives
  `E t + E (-t) - 2 E 0 ≤ B t²` (`≥`). Proofs via concavity / convexity of `E - B t²/2` (Mathlib
  `concaveOn_of_hasDerivWithinAt2_nonpos`, `convexOn_of_hasDerivWithinAt2_nonneg`).
* `not_localMin_of_curv_neg`, `strict_gt_of_curv_pos` : with the mirror symmetry `E (-t) = E t`, `F < 0` on the
  window gives `¬ IsLocalMin E 0` and `E t < E 0` for `0 < |t| ≤ t₀`; `F > 0` gives `E 0 < E t` along the path.
* `Rec`, `chainFrom`, `covers_of_chain` : a list of rational `a`-intervals whose endpoints chain from `A` to `B`
  covers `[A, B]` (`chainFrom` is a `Bool` the kernel evaluates by `decide`).
* `neg_on_of_chain`, `pos_on_of_chain` : chained intervals whose enclosures all have negative upper (positive lower)
  ends give a sign of `F` on all of `[A, B]` and the whole window.
* `root_in_gap` : intermediate value theorem in `a` between a certified-positive and a certified-negative point.
-/

namespace ProgZeroPointClass

open Set

/-! ## 1. Along-path window lemmas -/

theorem window_upper {E E' E'' : ℝ → ℝ} {t0 B : ℝ}
    (hE : ∀ t ∈ Icc (-t0) t0, HasDerivAt E (E' t) t) (hE' : ∀ t ∈ Icc (-t0) t0, HasDerivAt E' (E'' t) t)
    (hB : ∀ t ∈ Icc (-t0) t0, E'' t ≤ B) {t : ℝ} (ht : t ∈ Icc (-t0) t0) :
    E t + E (-t) - 2 * E 0 ≤ B * t ^ 2 := by
  set D : Set ℝ := Icc (-t0) t0
  have hsub : interior D ⊆ D := interior_subset
  have hg : HasDerivAt (fun u => B / 2 * u ^ 2) (B * t) t := by
    have := (hasDerivAt_pow 2 t).const_mul (B / 2)
    convert this using 1
    ring
  have hcont : ContinuousOn (fun u => E u - B / 2 * u ^ 2) D := by
    intro u hu
    exact ((hE u hu).continuousAt.sub (by fun_prop)).continuousWithinAt
  have hd1 : ∀ u ∈ interior D, HasDerivWithinAt (fun u => E u - B / 2 * u ^ 2) (E' u - B * u) (interior D) u := by
    intro u hu
    have h2 : HasDerivAt (fun u => B / 2 * u ^ 2) (B * u) u := by
      have := (hasDerivAt_pow 2 u).const_mul (B / 2)
      convert this using 1
      ring
    exact ((hE u (hsub hu)).sub h2).hasDerivWithinAt
  have hd2 : ∀ u ∈ interior D, HasDerivWithinAt (fun u => E' u - B * u) (E'' u - B) (interior D) u := by
    intro u hu
    have h2 : HasDerivAt (fun u => B * u) B u := by
      simpa using (hasDerivAt_id u).const_mul B
    exact ((hE' u (hsub hu)).sub h2).hasDerivWithinAt
  have hneg : ∀ u ∈ interior D, E'' u - B ≤ 0 := fun u hu => by linarith [hB u (hsub hu)]
  have hconc := concaveOn_of_hasDerivWithinAt2_nonpos (convex_Icc (-t0) t0) hcont hd1 hd2 hneg
  have hmt : -t ∈ D := ⟨by linarith [ht.2], by linarith [ht.1]⟩
  have key := hconc.2 ht hmt (by norm_num : (0 : ℝ) ≤ 1 / 2) (by norm_num : (0 : ℝ) ≤ 1 / 2) (by norm_num)
  simp only [smul_eq_mul] at key
  have h0 : 1 / 2 * t + 1 / 2 * -t = (0 : ℝ) := by ring
  rw [h0] at key
  nlinarith [key]

theorem window_lower {E E' E'' : ℝ → ℝ} {t0 B : ℝ}
    (hE : ∀ t ∈ Icc (-t0) t0, HasDerivAt E (E' t) t) (hE' : ∀ t ∈ Icc (-t0) t0, HasDerivAt E' (E'' t) t)
    (hB : ∀ t ∈ Icc (-t0) t0, B ≤ E'' t) {t : ℝ} (ht : t ∈ Icc (-t0) t0) :
    B * t ^ 2 ≤ E t + E (-t) - 2 * E 0 := by
  have hnE : ∀ t ∈ Icc (-t0) t0, HasDerivAt (fun u => -E u) (-E' t) t := fun t ht => (hE t ht).neg
  have hnE' : ∀ t ∈ Icc (-t0) t0, HasDerivAt (fun u => -E' u) (-E'' t) t := fun t ht => (hE' t ht).neg
  have := window_upper (E := fun u => -E u) (E' := fun u => -E' u) (E'' := fun u => -E'' u) (B := -B) hnE hnE'
    (fun u hu => by linarith [hB u hu]) ht
  linarith

/-- Negative curvature on the window: the triangular point is not a local minimum along the path, and the energy
strictly drops for every `0 < t ≤ t₀` (mirror symmetry `E (-t) = E t`). -/
theorem not_localMin_of_curv_neg {E E' E'' : ℝ → ℝ} {t0 B : ℝ} (ht0 : 0 < t0) (hBneg : B < 0)
    (hE : ∀ t ∈ Icc (-t0) t0, HasDerivAt E (E' t) t) (hE' : ∀ t ∈ Icc (-t0) t0, HasDerivAt E' (E'' t) t)
    (hB : ∀ t ∈ Icc (-t0) t0, E'' t ≤ B) (hsym : ∀ t, E (-t) = E t) :
    ¬ IsLocalMin E 0 ∧ ∀ t, 0 < t → t ≤ t0 → E t < E 0 := by
  have hw : ∀ t, 0 < t → t ≤ t0 → E t + E (-t) - 2 * E 0 ≤ t ^ 2 * B := by
    intro t ht htt
    have := window_upper hE hE' hB (t := t) ⟨by linarith, htt⟩
    linarith
  refine ⟨ProgZeroPointCert.not_isLocalMin_of_majorant (U := E) ht0 hBneg (fun t _ => le_refl _) rfl hw,
    fun t ht htt => ProgZeroPointCert.lt_of_majorant_window_symm (U := E) hBneg (fun t _ => le_refl _) rfl hw hsym
      ht htt⟩

/-- Positive curvature on the window: `E 0 < E t` for every `0 < |t| ≤ t₀` along the path. -/
theorem strict_gt_of_curv_pos {E E' E'' : ℝ → ℝ} {t0 B : ℝ} (hBpos : 0 < B)
    (hE : ∀ t ∈ Icc (-t0) t0, HasDerivAt E (E' t) t) (hE' : ∀ t ∈ Icc (-t0) t0, HasDerivAt E' (E'' t) t)
    (hB : ∀ t ∈ Icc (-t0) t0, B ≤ E'' t) (hsym : ∀ t, E (-t) = E t) :
    ∀ t, t ≠ 0 → |t| ≤ t0 → E 0 < E t := by
  intro t ht0 htt
  have hmem : t ∈ Icc (-t0) t0 := ⟨by linarith [neg_abs_le t], le_trans (le_abs_self t) htt⟩
  have h := window_lower hE hE' hB hmem
  rw [hsym t] at h
  have : 0 < B * t ^ 2 := mul_pos hBpos (by positivity)
  linarith

/-! ## 2. Covering an `a`-range by chained rational intervals -/

/-- One certified record (from one run of `n1_certify2.py`, possibly restricted to a sub-interval): for every
`a ∈ [lo, hi]` and `|t| ≤ t₀` there is `d ∈ [dlo, dhi]` with `F a t - (a - ac) d ∈ [qlo, qhi]` (the affine form
`F ∈ Q + R + (a - a_c) D` of the engine, `qlo = (Q + R).lo`, `qhi = (Q + R).hi`). -/
structure Rec where
  lo : ℚ
  hi : ℚ
  ac : ℚ
  qlo : ℚ
  qhi : ℚ
  dlo : ℚ
  dhi : ℚ

/-- The largest of the four corner values of `(a - ac) d` on `[lo, hi] × [dlo, dhi]`. -/
def Rec.cmax (r : Rec) : ℚ :=
  max (max ((r.lo - r.ac) * r.dlo) ((r.lo - r.ac) * r.dhi)) (max ((r.hi - r.ac) * r.dlo) ((r.hi - r.ac) * r.dhi))
/-- The smallest of the four corner values. -/
def Rec.cmin (r : Rec) : ℚ :=
  min (min ((r.lo - r.ac) * r.dlo) ((r.lo - r.ac) * r.dhi)) (min ((r.hi - r.ac) * r.dlo) ((r.hi - r.ac) * r.dhi))

/-- The intervals of the list start at `x`, are consecutive (`hi` of one = `lo` of the next), and the last one ends
at `B`. -/
def chainFrom : ℚ → ℚ → List Rec → Bool
  | _, _, [] => false
  | x, B, r :: rs => decide (r.lo = x) && decide (r.lo ≤ r.hi) && (decide (r.hi = B) || chainFrom r.hi B rs)

theorem covers_of_chain : ∀ (L : List Rec) (A B : ℚ), chainFrom A B L = true →
    ∀ a : ℝ, (A : ℝ) ≤ a → a ≤ (B : ℝ) → ∃ r ∈ L, (r.lo : ℝ) ≤ a ∧ a ≤ (r.hi : ℝ)
  | [], _, _, h, _, _, _ => by simp [chainFrom] at h
  | r :: rs, A, B, h, a, hA, hB => by
    simp only [chainFrom, Bool.and_eq_true, Bool.or_eq_true, decide_eq_true_eq] at h
    obtain ⟨⟨hlo, _⟩, hrest⟩ := h
    by_cases hle : a ≤ (r.hi : ℝ)
    · exact ⟨r, List.mem_cons_self, by rw [hlo]; exact hA, hle⟩
    · push Not at hle
      rcases hrest with hend | hch
      · exact absurd hB (by rw [← hend]; exact not_le.2 hle)
      · obtain ⟨r', hr', h1, h2⟩ := covers_of_chain rs r.hi B hch a hle.le hB
        exact ⟨r', List.mem_cons_of_mem r hr', h1, h2⟩

/-- A product over a box is bounded by its corner values. -/
theorem mul_le_corners {x y x1 x2 y1 y2 : ℝ} (hx1 : x1 ≤ x) (hx2 : x ≤ x2) (hy1 : y1 ≤ y) (hy2 : y ≤ y2) :
    x * y ≤ max (max (x1 * y1) (x1 * y2)) (max (x2 * y1) (x2 * y2)) := by
  have hA : x * y ≤ max (x1 * y) (x2 * y) := by
    rcases le_total 0 y with h | h
    · exact le_max_of_le_right (mul_le_mul_of_nonneg_right hx2 h)
    · exact le_max_of_le_left (mul_le_mul_of_nonpos_right hx1 h)
  have hB : ∀ z : ℝ, z * y ≤ max (z * y1) (z * y2) := by
    intro z
    rcases le_total 0 z with h | h
    · exact le_max_of_le_right (mul_le_mul_of_nonneg_left hy2 h)
    · exact le_max_of_le_left (mul_le_mul_of_nonpos_left hy1 h)
  have h1 := hB x1
  have h2 := hB x2
  rcases le_total (x1 * y) (x2 * y) with h | h
  · rw [max_eq_right h] at hA
    exact le_trans hA (le_trans h2 (le_max_right _ _))
  · rw [max_eq_left h] at hA
    exact le_trans hA (le_trans h1 (le_max_left _ _))

theorem corners_le_mul {x y x1 x2 y1 y2 : ℝ} (hx1 : x1 ≤ x) (hx2 : x ≤ x2) (hy1 : y1 ≤ y) (hy2 : y ≤ y2) :
    min (min (x1 * y1) (x1 * y2)) (min (x2 * y1) (x2 * y2)) ≤ x * y := by
  have := mul_le_corners (x := x) (y := -y) hx1 hx2 (neg_le_neg hy2) (neg_le_neg hy1)
  have e : max (max (x1 * -y2) (x1 * -y1)) (max (x2 * -y2) (x2 * -y1))
      = -(min (min (x1 * y1) (x1 * y2)) (min (x2 * y1) (x2 * y2))) := by
    simp only [mul_neg, max_neg_neg, neg_inj]
    rw [min_comm (x1 * y1), min_comm (x2 * y1)]
  rw [e] at this
  linarith [show x * -y = -(x * y) by ring]

/-- Every record certifies `F < 0` on its sub-interval: `qhi + cmax < 0`. -/
def allNeg (L : List Rec) : Bool := L.all (fun r => decide (r.qhi + r.cmax < 0))
/-- Every record certifies `F > 0` on its sub-interval: `0 < qlo + cmin`. -/
def allPos (L : List Rec) : Bool := L.all (fun r => decide (0 < r.qlo + r.cmin))

/-- The enclosure hypothesis for a list (this is the Tier C-ball input). -/
def Encloses (F : ℝ → ℝ → ℝ) (t0 : ℝ) (L : List Rec) : Prop :=
  ∀ r ∈ L, ∀ a : ℝ, (r.lo : ℝ) ≤ a → a ≤ (r.hi : ℝ) → ∀ t : ℝ, |t| ≤ t0 →
    ∃ d : ℝ, (r.dlo : ℝ) ≤ d ∧ d ≤ (r.dhi : ℝ) ∧ (r.qlo : ℝ) ≤ F a t - (a - r.ac) * d ∧
      F a t - (a - r.ac) * d ≤ (r.qhi : ℝ)

theorem Encloses.left {F : ℝ → ℝ → ℝ} {t0 : ℝ} {L1 L2 : List Rec} (h : Encloses F t0 (L1 ++ L2)) :
    Encloses F t0 L1 := fun r hr => h r (List.mem_append_left L2 hr)

theorem Encloses.right {F : ℝ → ℝ → ℝ} {t0 : ℝ} {L1 L2 : List Rec} (h : Encloses F t0 (L1 ++ L2)) :
    Encloses F t0 L2 := fun r hr => h r (List.mem_append_right L1 hr)

theorem allPos_left {L1 L2 : List Rec} (h : allPos (L1 ++ L2) = true) : allPos L1 = true := by
  simp only [allPos, List.all_append, Bool.and_eq_true] at h ⊢
  exact h.1

theorem allPos_right {L1 L2 : List Rec} (h : allPos (L1 ++ L2) = true) : allPos L2 = true := by
  simp only [allPos, List.all_append, Bool.and_eq_true] at h ⊢
  exact h.2

theorem allNeg_left {L1 L2 : List Rec} (h : allNeg (L1 ++ L2) = true) : allNeg L1 = true := by
  simp only [allNeg, List.all_append, Bool.and_eq_true] at h ⊢
  exact h.1

theorem allNeg_right {L1 L2 : List Rec} (h : allNeg (L1 ++ L2) = true) : allNeg L2 = true := by
  simp only [allNeg, List.all_append, Bool.and_eq_true] at h ⊢
  exact h.2

theorem rec_upper (F : ℝ → ℝ → ℝ) (_t0 : ℝ) (r : Rec) {a t : ℝ} (h1 : (r.lo : ℝ) ≤ a) (h2 : a ≤ (r.hi : ℝ))
    (hd : ∃ d : ℝ, (r.dlo : ℝ) ≤ d ∧ d ≤ (r.dhi : ℝ) ∧ (r.qlo : ℝ) ≤ F a t - (a - r.ac) * d ∧
      F a t - (a - r.ac) * d ≤ (r.qhi : ℝ)) : F a t ≤ ((r.qhi + r.cmax : ℚ) : ℝ) := by
  obtain ⟨d, hd1, hd2, _, hq⟩ := hd
  have hc := mul_le_corners (x := a - r.ac) (y := d) (x1 := (r.lo : ℝ) - r.ac) (x2 := (r.hi : ℝ) - r.ac)
    (by linarith) (by linarith) hd1 hd2
  have hcast : ((r.qhi + r.cmax : ℚ) : ℝ) = (r.qhi : ℝ) + max (max (((r.lo : ℝ) - r.ac) * r.dlo)
      (((r.lo : ℝ) - r.ac) * r.dhi)) (max (((r.hi : ℝ) - r.ac) * r.dlo) (((r.hi : ℝ) - r.ac) * r.dhi)) := by
    simp only [Rec.cmax]
    push_cast
    rfl
  rw [hcast]
  linarith

theorem rec_lower (F : ℝ → ℝ → ℝ) (_t0 : ℝ) (r : Rec) {a t : ℝ} (h1 : (r.lo : ℝ) ≤ a) (h2 : a ≤ (r.hi : ℝ))
    (hd : ∃ d : ℝ, (r.dlo : ℝ) ≤ d ∧ d ≤ (r.dhi : ℝ) ∧ (r.qlo : ℝ) ≤ F a t - (a - r.ac) * d ∧
      F a t - (a - r.ac) * d ≤ (r.qhi : ℝ)) : ((r.qlo + r.cmin : ℚ) : ℝ) ≤ F a t := by
  obtain ⟨d, hd1, hd2, hq, _⟩ := hd
  have hc := corners_le_mul (x := a - r.ac) (y := d) (x1 := (r.lo : ℝ) - r.ac) (x2 := (r.hi : ℝ) - r.ac)
    (by linarith) (by linarith) hd1 hd2
  have hcast : ((r.qlo + r.cmin : ℚ) : ℝ) = (r.qlo : ℝ) + min (min (((r.lo : ℝ) - r.ac) * r.dlo)
      (((r.lo : ℝ) - r.ac) * r.dhi)) (min (((r.hi : ℝ) - r.ac) * r.dlo) (((r.hi : ℝ) - r.ac) * r.dhi)) := by
    simp only [Rec.cmin]
    push_cast
    rfl
  rw [hcast]
  linarith

theorem neg_on_of_chain (F : ℝ → ℝ → ℝ) (t0 : ℝ) (L : List Rec) (A B : ℚ) (hch : chainFrom A B L = true)
    (hneg : allNeg L = true) (henc : Encloses F t0 L) :
    ∀ a : ℝ, (A : ℝ) ≤ a → a ≤ (B : ℝ) → ∃ c : ℚ, c < 0 ∧ ∀ t : ℝ, |t| ≤ t0 → F a t ≤ (c : ℝ) := by
  intro a hA hB
  obtain ⟨r, hr, h1, h2⟩ := covers_of_chain L A B hch a hA hB
  have hc : r.qhi + r.cmax < 0 := by
    have := List.all_eq_true.1 hneg r hr
    simpa using this
  exact ⟨r.qhi + r.cmax, hc, fun t ht => rec_upper F t0 r h1 h2 (henc r hr a h1 h2 t ht)⟩

theorem pos_on_of_chain (F : ℝ → ℝ → ℝ) (t0 : ℝ) (L : List Rec) (A B : ℚ) (hch : chainFrom A B L = true)
    (hpos : allPos L = true) (henc : Encloses F t0 L) :
    ∀ a : ℝ, (A : ℝ) ≤ a → a ≤ (B : ℝ) → ∃ c : ℚ, 0 < c ∧ ∀ t : ℝ, |t| ≤ t0 → (c : ℝ) ≤ F a t := by
  intro a hA hB
  obtain ⟨r, hr, h1, h2⟩ := covers_of_chain L A B hch a hA hB
  have hc : 0 < r.qlo + r.cmin := by
    have := List.all_eq_true.1 hpos r hr
    simpa using this
  exact ⟨r.qlo + r.cmin, hc, fun t ht => rec_lower F t0 r h1 h2 (henc r hr a h1 h2 t ht)⟩

/-- Sign on every record of a list (no chaining needed): each record certifies its own `a`-interval (a point when
`lo = hi`). -/
theorem pos_of_mem (F : ℝ → ℝ → ℝ) (t0 : ℝ) (L : List Rec) (hpos : allPos L = true) (henc : Encloses F t0 L) :
    ∀ r ∈ L, ∀ a : ℝ, (r.lo : ℝ) ≤ a → a ≤ (r.hi : ℝ) → ∀ t : ℝ, |t| ≤ t0 → 0 < F a t := by
  intro r hr a h1 h2 t ht
  have hc : 0 < r.qlo + r.cmin := by
    have := List.all_eq_true.1 hpos r hr
    simpa using this
  have hc' : (0 : ℝ) < ((r.qlo + r.cmin : ℚ) : ℝ) := by exact_mod_cast hc
  linarith [rec_lower F t0 r h1 h2 (henc r hr a h1 h2 t ht)]

theorem neg_of_mem (F : ℝ → ℝ → ℝ) (t0 : ℝ) (L : List Rec) (hneg : allNeg L = true) (henc : Encloses F t0 L) :
    ∀ r ∈ L, ∀ a : ℝ, (r.lo : ℝ) ≤ a → a ≤ (r.hi : ℝ) → ∀ t : ℝ, |t| ≤ t0 → F a t < 0 := by
  intro r hr a h1 h2 t ht
  have hc : r.qhi + r.cmax < 0 := by
    have := List.all_eq_true.1 hneg r hr
    simpa using this
  have hc' : ((r.qhi + r.cmax : ℚ) : ℝ) < 0 := by exact_mod_cast hc
  linarith [rec_upper F t0 r h1 h2 (henc r hr a h1 h2 t ht)]

/-! ## 3. A root between a positive and a negative point (intermediate value theorem in `a`) -/

theorem root_in_gap (f : ℝ → ℝ) {aL aR : ℝ} (hlt : aL < aR) (hf : ContinuousOn f (Icc aL aR))
    (hL : 0 < f aL) (hR : f aR < 0) : ∃ a ∈ Ioo aL aR, f a = 0 := by
  have := intermediate_value_Ioo' hlt.le hf (show (0 : ℝ) ∈ Ioo (f aR) (f aL) from ⟨hR, hL⟩)
  obtain ⟨a, ha, hfa⟩ := this
  exact ⟨a, ha, hfa⟩

theorem root_in_gap' (f : ℝ → ℝ) {aL aR : ℝ} (hlt : aL < aR) (hf : ContinuousOn f (Icc aL aR))
    (hL : f aL < 0) (hR : 0 < f aR) : ∃ a ∈ Ioo aL aR, f a = 0 := by
  obtain ⟨a, ha, hfa⟩ := root_in_gap (fun x => -f x) hlt hf.neg (by linarith) (by linarith)
  exact ⟨a, ha, by linarith⟩

end ProgZeroPointClass

#print axioms ProgZeroPointClass.window_upper
#print axioms ProgZeroPointClass.window_lower
#print axioms ProgZeroPointClass.not_localMin_of_curv_neg
#print axioms ProgZeroPointClass.strict_gt_of_curv_pos
#print axioms ProgZeroPointClass.covers_of_chain
#print axioms ProgZeroPointClass.mul_le_corners
#print axioms ProgZeroPointClass.corners_le_mul
#print axioms ProgZeroPointClass.Encloses.left
#print axioms ProgZeroPointClass.Encloses.right
#print axioms ProgZeroPointClass.allPos_left
#print axioms ProgZeroPointClass.allPos_right
#print axioms ProgZeroPointClass.allNeg_left
#print axioms ProgZeroPointClass.allNeg_right
#print axioms ProgZeroPointClass.rec_upper
#print axioms ProgZeroPointClass.rec_lower
#print axioms ProgZeroPointClass.neg_on_of_chain
#print axioms ProgZeroPointClass.pos_on_of_chain
#print axioms ProgZeroPointClass.pos_of_mem
#print axioms ProgZeroPointClass.neg_of_mem
#print axioms ProgZeroPointClass.root_in_gap
#print axioms ProgZeroPointClass.root_in_gap'
