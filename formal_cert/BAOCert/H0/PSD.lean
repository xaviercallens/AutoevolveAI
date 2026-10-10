import BAOCert.P2.Data

/-!
# `χ²_DESI ≥ 0` from the block structure of the inverse covariance

`psdTop` checks that the sparse list starts with a non-negative 1 × 1 diagonal entry and continues with
2 × 2 blocks `(a,a,p₁), (a,b,p₂), (b,a,p₂), (b,b,p₄)` with `p₁, p₄ ≥ 0` and `p₂² ≤ p₁ p₄`.
-/

namespace BAOCert.H0

open BAOCert

/-- Block checker for the 2 × 2 part. -/
def psd2 : List (ℕ × ℕ × ℚ) → Bool
  | (a1, b1, p1) :: (a2, b2, p2) :: (a3, b3, p3) :: (a4, b4, p4) :: rest =>
      (decide (b1 = a1) && decide (a2 = a1) && decide (b3 = a1) && decide (a3 = b2) && decide (a4 = b2) &&
        decide (b4 = b2) && decide (p3 = p2) && decide (0 ≤ p1) && decide (0 ≤ p4) && decide (p2 ^ 2 ≤ p1 * p4)) &&
        psd2 rest
  | [] => true
  | _ => false

/-- Head 1 × 1 entry, then 2 × 2 blocks. -/
def psdTop : List (ℕ × ℕ × ℚ) → Bool
  | (a, b, p) :: rest => decide (b = a) && decide (0 ≤ p) && psd2 rest
  | [] => false

lemma block_nonneg {p1 p2 p4 ra rb : ℝ} (h1 : 0 ≤ p1) (h4 : 0 ≤ p4) (h : p2 ^ 2 ≤ p1 * p4) :
    0 ≤ p1 * ra * ra + p2 * ra * rb + p2 * rb * ra + p4 * rb * rb := by
  rcases eq_or_lt_of_le (add_nonneg h1 h4) with h0 | hpos
  · have hp1 : p1 = 0 := by linarith
    have hp4 : p4 = 0 := by linarith
    have hp2 : p2 = 0 := by
      have : p2 ^ 2 ≤ 0 := by rw [hp1] at h; simpa using h
      exact pow_eq_zero_iff (n := 2) (by norm_num) |>.1 (le_antisymm this (sq_nonneg _))
    rw [hp1, hp2, hp4]; ring_nf; exact le_refl 0
  · have key : 0 ≤ (p1 + p4) * (p1 * ra * ra + p2 * ra * rb + p2 * rb * ra + p4 * rb * rb) := by
      nlinarith [sq_nonneg (p1 * ra + p2 * rb), sq_nonneg (p2 * ra + p4 * rb), mul_nonneg (sub_nonneg.2 h) (sq_nonneg ra),
        mul_nonneg (sub_nonneg.2 h) (sq_nonneg rb)]
    by_contra hneg
    push_neg at hneg
    nlinarith [mul_neg_of_pos_of_neg hpos hneg]

theorem psd2_nonneg (d : List ℚ) (x : ℕ → ℝ) (K : ℝ) :
    ∀ L : List (ℕ × ℕ × ℚ), psd2 L = true → 0 ≤ chi2Of L d x K
  | [], _ => by simp [chi2Of]
  | [_], h => by simp [psd2] at h
  | [_, _], h => by simp [psd2] at h
  | [_, _, _], h => by simp [psd2] at h
  | (a1, b1, p1) :: (a2, b2, p2) :: (a3, b3, p3) :: (a4, b4, p4) :: rest, h => by
      simp only [psd2, Bool.and_eq_true, decide_eq_true_eq] at h
      obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨e1, e2⟩, e3⟩, e4⟩, e5⟩, e6⟩, e7⟩, hp1⟩, hp4⟩, hp⟩, hrest⟩ := h
      have ih := psd2_nonneg d x K rest hrest
      unfold chi2Of at ih ⊢
      simp only [List.map_cons, List.sum_cons]
      rw [e1, e2, e3, e4, e5, e6, e7]
      have hb := block_nonneg (p1 := (p1 : ℝ)) (p2 := (p2 : ℝ)) (p4 := (p4 : ℝ))
        (ra := ((d.getD a1 0 : ℚ) : ℝ) - K * x a1) (rb := ((d.getD b2 0 : ℚ) : ℝ) - K * x b2)
        (by exact_mod_cast hp1) (by exact_mod_cast hp4) (by exact_mod_cast hp)
      linarith [hb, ih]

theorem psdTop_nonneg (d : List ℚ) (x : ℕ → ℝ) (K : ℝ) (L : List (ℕ × ℕ × ℚ)) (h : psdTop L = true) :
    0 ≤ chi2Of L d x K := by
  cases L with
  | nil => simp [psdTop] at h
  | cons e rest =>
    obtain ⟨a, b, p⟩ := e
    simp only [psdTop, Bool.and_eq_true, decide_eq_true_eq] at h
    obtain ⟨⟨hab, hp⟩, hrest⟩ := h
    subst hab
    have ih := psd2_nonneg d x K rest hrest
    unfold chi2Of at ih ⊢
    simp only [List.map_cons, List.sum_cons]
    have : 0 ≤ (p : ℝ) * (((d.getD b 0 : ℚ) : ℝ) - K * x b) * (((d.getD b 0 : ℚ) : ℝ) - K * x b) := by
      have hp' : (0 : ℝ) ≤ p := by exact_mod_cast hp
      rw [mul_assoc]; exact mul_nonneg hp' (mul_self_nonneg _)
    linarith

theorem psdTop_DESI : psdTop BAOCert.P2.Data.Pent = true := by decide +kernel

/-- The DESI DR2 BAO `χ²` is non-negative for every `Om` and every `K`. -/
theorem chi2DESI_nonneg (Om K : ℝ) : 0 ≤ BAOCert.P2.Data.chi2DESI Om K :=
  psdTop_nonneg _ _ K _ psdTop_DESI

end BAOCert.H0
