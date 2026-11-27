import Mathlib.Tactic
import Mathlib.Analysis.SpecialFunctions.Pow.Real

/-!
# Proposal 4, E3 (2026-10-31): monotonicity in `ζ` of the low-dissipation efficiency-at-given-power upper bound

Source: Ma, Xu, Dong, Sun, arXiv:1802.09806v4, Eq. (13) for `η̃₊(P̃, ζ, η_C)` and Appendix B ("the analytical proof of
its monotonicity is tedious and difficult. Instead [we] numerically calculate the derivative").

Model statement only (a phenomenological low-dissipation Carnot engine), NOT a claim about any real engine.

Reduction (see `results/proposal4/2026-10-27/E3/code/derivation.md`). Put `c = η_C ∈ (0,1)`, `s = √(1-P̃) ∈ [0,1)`,
`K = 2/(1-s) > 1`, `u = η/η_C`, `w = √(1-c u)`. The paper's tangency condition (total time `τ₊`) reads
`K (1-u) ≥ ((1-ζ) + (1+ζ) w)² / 4` and `η̃₊` is the largest such `u`.  Multiplying by `c`, with `1-u = (w²-(1-c))/c`:
`G c K ζ w = K (w² - (1-c)) - c ((1-ζ) + (1+ζ) w)² / 4 ≥ 0`, and `η̃₊ = (1 - w₊²)/c` where `w₊` is the positive root of
the quadratic `G c K ζ ·`.  That `η̃₊` of Eq. (13) equals this root form is checked numerically (not in Lean) in
`code/link.py`; here `etaPlus` is DEFINED as the root form, so the Lean statements are about the root form.

Results (all for `0<c<1`, `1<K`, `ζ ∈ [-1,1]`):
* `wPlus_root`, `wPlus_nonneg`, `wPlus_lt_one`: the explicit positive root and its basic properties.
* `root_unique`: any nonnegative root of `G c K ζ ·` equals `wPlus`.
* `etaPlus_strictMono`: `ζ₁ < ζ₂ → etaPlus ζ₁ < etaPlus ζ₂` (strict monotonicity in `ζ`, the Appendix B claim).
* `etaPlus_one`: `etaPlus c K 1 = (K-1)/(K-c)`; `etaPlus_le_one_value`: universal bound by the value at `ζ = 1`.
* `eq1_of_P`: with `K = 2/(1-s)`, `P = 1 - s²`: `etaPlus ≤ 1 - (1-c)P/(2(1+s) - cP)`, i.e. Eq. (1) of the paper.
-/

namespace LowDissE3

/-- Quadratic whose positive root gives `w = √(1-c u)` of the efficiency bound. -/
noncomputable def G (c K ζ w : ℝ) : ℝ := K * (w ^ 2 - (1 - c)) - c * ((1 - ζ) + (1 + ζ) * w) ^ 2 / 4

/-- Leading coefficient. -/
noncomputable def qA (c K ζ : ℝ) : ℝ := K - c * (1 + ζ) ^ 2 / 4
/-- Linear coefficient (so that `G = qA w² - qB w - qC`). -/
noncomputable def qB (c ζ : ℝ) : ℝ := c * (1 - ζ ^ 2) / 2
/-- Constant coefficient. -/
noncomputable def qC (c K ζ : ℝ) : ℝ := K * (1 - c) + c * (1 - ζ) ^ 2 / 4

theorem G_eq (c K ζ w : ℝ) : G c K ζ w = qA c K ζ * w ^ 2 - qB c ζ * w - qC c K ζ := by
  unfold G qA qB qC; ring

/-- Explicit positive root. -/
noncomputable def wPlus (c K ζ : ℝ) : ℝ :=
  (qB c ζ + Real.sqrt (qB c ζ ^ 2 + 4 * qA c K ζ * qC c K ζ)) / (2 * qA c K ζ)

/-- The efficiency bound `η̃₊` (root form), in units `η/η_C`. -/
noncomputable def etaPlus (c K ζ : ℝ) : ℝ := (1 - wPlus c K ζ ^ 2) / c

section
variable {c K ζ : ℝ}

theorem qA_pos (hc0 : 0 < c) (hc1 : c < 1) (hK : 1 < K) (h1 : -1 ≤ ζ) (h2 : ζ ≤ 1) : 0 < qA c K ζ := by
  unfold qA
  have : (1 + ζ) ^ 2 ≤ 4 := by nlinarith
  nlinarith

theorem qB_nonneg (hc0 : 0 < c) (h1 : -1 ≤ ζ) (h2 : ζ ≤ 1) : 0 ≤ qB c ζ := by
  unfold qB
  have : 0 ≤ 1 - ζ ^ 2 := by nlinarith
  positivity

theorem qC_pos (hc0 : 0 < c) (hc1 : c < 1) (hK : 1 < K) : 0 < qC c K ζ := by
  unfold qC
  have : 0 < K * (1 - c) := mul_pos (by linarith) (by linarith)
  have : 0 ≤ c * (1 - ζ) ^ 2 / 4 := by positivity
  linarith

theorem wPlus_root (hc0 : 0 < c) (hc1 : c < 1) (hK : 1 < K) (h1 : -1 ≤ ζ) (h2 : ζ ≤ 1) :
    G c K ζ (wPlus c K ζ) = 0 := by
  have hA := qA_pos hc0 hc1 hK h1 h2
  have hB := qB_nonneg hc0 h1 h2
  have hC := qC_pos (ζ := ζ) hc0 hc1 hK
  have hD : 0 ≤ qB c ζ ^ 2 + 4 * qA c K ζ * qC c K ζ := by positivity
  have hs := Real.sq_sqrt hD
  rw [G_eq]
  unfold wPlus
  set r := Real.sqrt (qB c ζ ^ 2 + 4 * qA c K ζ * qC c K ζ)
  field_simp
  nlinarith [hs]

theorem wPlus_nonneg (hc0 : 0 < c) (hc1 : c < 1) (hK : 1 < K) (h1 : -1 ≤ ζ) (h2 : ζ ≤ 1) :
    0 ≤ wPlus c K ζ := by
  have hA := qA_pos hc0 hc1 hK h1 h2
  have hB := qB_nonneg hc0 h1 h2
  unfold wPlus
  positivity

/-- Any nonnegative root is `< 1`. -/
theorem root_lt_one (hc0 : 0 < c) (hc1 : c < 1) (hK : 1 < K) (h1 : -1 ≤ ζ) (h2 : ζ ≤ 1) {w : ℝ}
    (hw : 0 ≤ w) (hG : G c K ζ w = 0) : w < 1 := by
  by_contra hcon
  rw [not_lt] at hcon
  unfold G at hG
  have hT : (1 - ζ) + (1 + ζ) * w ≤ 2 * w := by nlinarith
  have hT0 : 0 ≤ (1 - ζ) + (1 + ζ) * w := by nlinarith
  have hT2 : ((1 - ζ) + (1 + ζ) * w) ^ 2 ≤ (2 * w) ^ 2 := by
    apply pow_le_pow_left₀ hT0 hT
  have hw2 : 1 ≤ w ^ 2 := by nlinarith
  have hKc : 0 < K - c := by linarith
  have h3 := mul_le_mul_of_nonneg_left hT2 hc0.le
  have h4 := mul_le_mul_of_nonneg_left hw2 hKc.le
  nlinarith [mul_pos hc0 (sub_pos.mpr hK)]

/-- `G` increases (strictly) in `ζ` at fixed `w ∈ [0,1)`. -/
theorem G_strict_mono_zeta (hc0 : 0 < c) {ζ₁ ζ₂ w : ℝ} (h1 : -1 ≤ ζ₁) (h12 : ζ₁ < ζ₂) (h2 : ζ₂ ≤ 1)
    (hw0 : 0 ≤ w) (hw1 : w < 1) : G c K ζ₁ w < G c K ζ₂ w := by
  unfold G
  have hT1 : 0 ≤ (1 - ζ₁) + (1 + ζ₁) * w := by nlinarith
  have hT2 : 0 ≤ (1 - ζ₂) + (1 + ζ₂) * w := by nlinarith
  have hd : ((1 - ζ₂) + (1 + ζ₂) * w) < ((1 - ζ₁) + (1 + ζ₁) * w) := by nlinarith
  have hsq : ((1 - ζ₂) + (1 + ζ₂) * w) ^ 2 < ((1 - ζ₁) + (1 + ζ₁) * w) ^ 2 := by
    nlinarith
  nlinarith [mul_lt_mul_of_pos_left hsq hc0]

/-- Difference of `G` at two points of the same parameter. -/
theorem G_sub (c K ζ w₁ w₂ : ℝ) :
    G c K ζ w₁ - G c K ζ w₂ = (w₁ - w₂) * (qA c K ζ * (w₁ + w₂) - qB c ζ) := by
  rw [G_eq, G_eq]; ring

/-- Key lemma: the nonnegative roots are strictly antitone in `ζ`. -/
theorem root_strict_anti (hc0 : 0 < c) (hc1 : c < 1) (hK : 1 < K) {ζ₁ ζ₂ w₁ w₂ : ℝ}
    (h1 : -1 ≤ ζ₁) (h12 : ζ₁ < ζ₂) (h2 : ζ₂ ≤ 1) (hw1 : 0 ≤ w₁) (hw2 : 0 ≤ w₂)
    (hG1 : G c K ζ₁ w₁ = 0) (hG2 : G c K ζ₂ w₂ = 0) : w₂ < w₁ := by
  by_contra hcon
  rw [not_lt] at hcon
  have hw1lt : w₁ < 1 := root_lt_one hc0 hc1 hK h1 (by linarith) hw1 hG1
  have hpos : 0 < G c K ζ₂ w₁ := by
    have := G_strict_mono_zeta (c := c) (K := K) hc0 h1 h12 h2 hw1 hw1lt
    linarith
  have hA := qA_pos hc0 hc1 hK (by linarith : -1 ≤ ζ₂) h2
  have hC := qC_pos (ζ := ζ₂) hc0 hc1 hK
  -- w₂ > 0 because the constant term is positive
  have hw2pos : 0 < w₂ := by
    rcases hw2.lt_or_eq with h | h
    · exact h
    · exfalso
      have := hG2
      rw [G_eq, ← h] at this
      linarith
  -- qA * w₂ > qB
  have hAB : qB c ζ₂ < qA c K ζ₂ * w₂ := by
    have := hG2
    rw [G_eq] at this
    nlinarith
  have hfac : 0 < qA c K ζ₂ * (w₁ + w₂) - qB c ζ₂ := by
    nlinarith
  have hsub := G_sub c K ζ₂ w₁ w₂
  rw [hG2] at hsub
  have : (w₁ - w₂) * (qA c K ζ₂ * (w₁ + w₂) - qB c ζ₂) ≤ 0 :=
    mul_nonpos_of_nonpos_of_nonneg (by linarith) hfac.le
  linarith

/-- Uniqueness of the nonnegative root. -/
theorem root_unique (hc0 : 0 < c) (hc1 : c < 1) (hK : 1 < K) (h1 : -1 ≤ ζ) (h2 : ζ ≤ 1) {w : ℝ}
    (hw : 0 ≤ w) (hG : G c K ζ w = 0) : w = wPlus c K ζ := by
  have hp := wPlus_root hc0 hc1 hK h1 h2
  have hp0 := wPlus_nonneg hc0 hc1 hK h1 h2
  have hA := qA_pos hc0 hc1 hK h1 h2
  have hC := qC_pos (ζ := ζ) hc0 hc1 hK
  have hsub := G_sub c K ζ w (wPlus c K ζ)
  rw [hG, hp] at hsub
  have hwp : 0 < w := by
    rcases hw.lt_or_eq with h | h
    · exact h
    · exfalso
      have := hG
      rw [G_eq, ← h] at this
      linarith
  have hAB : qB c ζ < qA c K ζ * w := by
    have := hG
    rw [G_eq] at this
    nlinarith
  have hfac : 0 < qA c K ζ * (w + wPlus c K ζ) - qB c ζ := by nlinarith
  have : (w - wPlus c K ζ) * (qA c K ζ * (w + wPlus c K ζ) - qB c ζ) = 0 := by linarith
  rcases mul_eq_zero.mp this with h | h
  · linarith
  · linarith

theorem etaPlus_strictMono (hc0 : 0 < c) (hc1 : c < 1) (hK : 1 < K) {ζ₁ ζ₂ : ℝ}
    (h1 : -1 ≤ ζ₁) (h12 : ζ₁ < ζ₂) (h2 : ζ₂ ≤ 1) : etaPlus c K ζ₁ < etaPlus c K ζ₂ := by
  have hlt := root_strict_anti (c := c) (K := K) hc0 hc1 hK h1 h12 h2
    (wPlus_nonneg hc0 hc1 hK h1 (by linarith)) (wPlus_nonneg hc0 hc1 hK (by linarith) h2)
    (wPlus_root hc0 hc1 hK h1 (by linarith)) (wPlus_root hc0 hc1 hK (by linarith) h2)
  have h0 := wPlus_nonneg hc0 hc1 hK (by linarith : -1 ≤ ζ₂) h2
  unfold etaPlus
  apply div_lt_div_of_pos_right _ hc0
  nlinarith

theorem etaPlus_mono (hc0 : 0 < c) (hc1 : c < 1) (hK : 1 < K) {ζ₁ ζ₂ : ℝ}
    (h1 : -1 ≤ ζ₁) (h12 : ζ₁ ≤ ζ₂) (h2 : ζ₂ ≤ 1) : etaPlus c K ζ₁ ≤ etaPlus c K ζ₂ := by
  rcases h12.lt_or_eq with h | h
  · exact (etaPlus_strictMono hc0 hc1 hK h1 h h2).le
  · rw [h]

/-- At `ζ = 1` the bound is `(K-1)/(K-c)`. -/
theorem etaPlus_one (hc0 : 0 < c) (hc1 : c < 1) (hK : 1 < K) : etaPlus c K 1 = (K - 1) / (K - c) := by
  have hroot := wPlus_root hc0 hc1 hK (by norm_num : (-1 : ℝ) ≤ 1) le_rfl
  have hKc : 0 < K - c := by linarith
  have hw2 : (K - c) * wPlus c K 1 ^ 2 = K * (1 - c) := by
    unfold G at hroot; nlinarith
  unfold etaPlus
  rw [div_eq_div_iff hc0.ne' hKc.ne']
  nlinarith

/-- Universal bound: `η̃₊(ζ) ≤ η̃₊(1) = (K-1)/(K-c)`. -/
theorem etaPlus_le_one_value (hc0 : 0 < c) (hc1 : c < 1) (hK : 1 < K) (h1 : -1 ≤ ζ) (h2 : ζ ≤ 1) :
    etaPlus c K ζ ≤ (K - 1) / (K - c) := by
  rw [← etaPlus_one hc0 hc1 hK]
  exact etaPlus_mono hc0 hc1 hK h1 h2 le_rfl

/-- Eq. (1) of Ma et al.: with `K = 2/(1-s)`, `P = 1 - s²`, `s ∈ [0,1)`:
`η̃₊(ζ) + (1-c) P / (2 (1+s) - c P) ≤ 1`. -/
theorem eq1_of_P (hc0 : 0 < c) (hc1 : c < 1) {s : ℝ} (hs0 : 0 ≤ s) (hs1 : s < 1)
    (h1 : -1 ≤ ζ) (h2 : ζ ≤ 1) :
    etaPlus c (2 / (1 - s)) ζ + (1 - c) * (1 - s ^ 2) / (2 * (1 + s) - c * (1 - s ^ 2)) ≤ 1 := by
  have hs1' : 0 < 1 - s := by linarith
  have hK : 1 < 2 / (1 - s) := by
    rw [lt_div_iff₀ hs1']; linarith
  have hb := etaPlus_le_one_value hc0 hc1 hK h1 h2
  have hden : 0 < 2 * (1 + s) - c * (1 - s ^ 2) := by nlinarith
  have hval : (2 / (1 - s) - 1) / (2 / (1 - s) - c) + (1 - c) * (1 - s ^ 2) / (2 * (1 + s) - c * (1 - s ^ 2)) = 1 := by
    have h3 : 2 / (1 - s) - c = (2 - c * (1 - s)) / (1 - s) := by field_simp
    have h4 : 2 / (1 - s) - 1 = (1 + s) / (1 - s) := by field_simp; ring
    have h5 : 0 < 2 - c * (1 - s) := by nlinarith
    rw [h3, h4, div_div_div_cancel_right₀ hs1'.ne']
    rw [div_add_div _ _ h5.ne' hden.ne', div_eq_one_iff_eq (mul_ne_zero h5.ne' hden.ne')]
    ring
  have := add_le_add_right hb ((1 - c) * (1 - s ^ 2) / (2 * (1 + s) - c * (1 - s ^ 2)))
  linarith

end

end LowDissE3
