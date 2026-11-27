import Mathlib.Tactic
import Mathlib.Analysis.SpecialFunctions.Pow.Real

/-!
# Proposal 4, E3 (2026-10-31): engine-level universal bound (Eq. (1) of Ma, Xu, Dong, Sun, arXiv:1802.09806)

A phenomenological low-dissipation Carnot engine model, NOT a real engine.  Data: `a = √Mh > 0`, `b = √Mc > 0`
(so `Mh = a²`, `Mc = b²`, `M = (a+b)²`), reversible heat scale `q = η_C Q_h^{(r)} > 0`, `c = η_C ∈ (0,1)`, times `th, tc > 0`.
Paper's Eqs. (3), (4):
`P = (q - a²/th - b²/tc)/(th+tc)`, `η = (q - a²/th - b²/tc)/(q/c - a²/th)` (denominator `> 0`: positive heat from the hot bath).
`P̃ = P/Pmax`, `Pmax = q²/(4M)`, i.e. `P̃ q² = 4 (a+b)² P`; `s = √(1-P̃)`.

`engine_bound`: for every such engine with `P > 0`: `η/η_C + (1-c) P̃ / (2 (1+s) - c P̃) ≤ 1`  (Eq. (1)), no `ζ` and no
use of Eq. (13) is needed (the worst case `ζ = 1` is absorbed by `w ≤ 1`).
-/

namespace LowDissE3

theorem cs2 {A B x y : ℝ} (hx : 0 < x) (hy : 0 < y) : (A + B) ^ 2 / (x + y) ≤ A ^ 2 / x + B ^ 2 / y := by
  rw [div_add_div _ _ hx.ne' hy.ne', div_le_div_iff₀ (by positivity) (by positivity)]
  nlinarith [sq_nonneg (A * y - B * x)]

set_option maxHeartbeats 3000000 in
theorem engine_bound {a b q c th tc P Pt e : ℝ} (ha : 0 < a) (hb : 0 < b) (hq : 0 < q) (hc0 : 0 < c) (hc1 : c < 1)
    (hth : 0 < th) (htc : 0 < tc)
    (hP : P = (q - a ^ 2 / th - b ^ 2 / tc) / (th + tc)) (hPpos : 0 < P)
    (hQ : 0 < q / c - a ^ 2 / th)
    (he : e = (q - a ^ 2 / th - b ^ 2 / tc) / (q / c - a ^ 2 / th))
    (hPt : Pt * q ^ 2 = 4 * (a + b) ^ 2 * P) :
    e / c + (1 - c) * Pt / (2 * (1 + Real.sqrt (1 - Pt)) - c * Pt) ≤ 1 := by
  set τ := th + tc with hτ
  have hτpos : 0 < τ := by positivity
  set W := q - a ^ 2 / th - b ^ 2 / tc with hW
  have hWP : W = P * τ := by
    rw [hP]; field_simp
  have hWpos : 0 < W := by rw [hWP]; positivity
  have hM : 0 < (a + b) ^ 2 := by positivity
  -- Eq. (8)/(5): a²/th + b²/tc ≥ M/τ, hence P τ² - q τ + M ≤ 0
  have h8 := cs2 (A := a) (B := b) hth htc
  have hquad : P * τ ^ 2 - q * τ + (a + b) ^ 2 ≤ 0 := by
    have h1 : (a + b) ^ 2 / τ ≤ q - P * τ := by
      have : a ^ 2 / th + b ^ 2 / tc = q - W := by rw [hW]; ring
      rw [← hWP] at *
      linarith
    rw [div_le_iff₀ hτpos] at h1
    nlinarith
  -- τ ≤ τ₊
  have hD : 0 ≤ q ^ 2 - 4 * P * (a + b) ^ 2 := by
    nlinarith [sq_nonneg (2 * P * τ - q)]
  have hPt_def : q ^ 2 * (1 - Pt) = q ^ 2 - 4 * P * (a + b) ^ 2 := by nlinarith [hPt]
  have h1Pt : 0 ≤ 1 - Pt := by
    by_contra hneg
    push Not at hneg
    have : q ^ 2 * (1 - Pt) < 0 := mul_neg_of_pos_of_neg (by positivity) hneg
    linarith
  set s := Real.sqrt (1 - Pt) with hs
  have hs0 : 0 ≤ s := Real.sqrt_nonneg _
  have hs2 : s ^ 2 = 1 - Pt := Real.sq_sqrt h1Pt
  have hPtpos : 0 < Pt := by
    have : 0 < Pt * q ^ 2 := by rw [hPt]; positivity
    by_contra hneg
    push Not at hneg
    have := mul_nonpos_of_nonpos_of_nonneg hneg (by positivity : (0 : ℝ) ≤ q ^ 2)
    linarith
  have hs1 : s < 1 := by nlinarith
  have hτle : 2 * P * τ ≤ q * (1 + s) := by
    have hsq : (2 * P * τ - q) ^ 2 ≤ (q * s) ^ 2 := by
      have : (q * s) ^ 2 = q ^ 2 * (1 - Pt) := by rw [mul_pow, hs2]
      rw [this, hPt_def]
      nlinarith
    have hqs : 0 ≤ q * s := by positivity
    have := abs_le_of_sq_le_sq' hsq hqs
    linarith [this.2]
  -- efficiency bookkeeping
  have hden : 0 < q / c - a ^ 2 / th := hQ
  have hWe : W = e * (q / c - a ^ 2 / th) := by
    rw [he]; exact (div_mul_cancel₀ _ hden.ne').symm
  have hqu : q * (1 - e / c) = (1 - e) * (a ^ 2 / th) + b ^ 2 / tc := by
    have h2 : q * (1 - e / c) = q - e * (q / c) := by ring
    have h3 : e * (q / c) = W + e * (a ^ 2 / th) := by rw [hWe]; ring
    rw [h2, h3]
    linarith [hW]
  have hpos1 : 0 < 1 - e := by
    have hqc : 0 < q / c - q := by
      rw [sub_pos, lt_div_iff₀ hc0]; nlinarith [mul_pos hq (sub_pos.2 hc1)]
    have hbt : 0 < b ^ 2 / tc := by positivity
    have h3 : W < q / c - a ^ 2 / th := by linarith [hW]
    by_contra hneg
    push Not at hneg
    have h4 := mul_le_mul_of_nonneg_right (show (1 : ℝ) ≤ e by linarith) hden.le
    linarith [hWe]
  have hepos : 0 < e := by rw [he]; positivity
  obtain ⟨w, hw0, hw2⟩ : ∃ w : ℝ, 0 < w ∧ w ^ 2 = 1 - e :=
    ⟨Real.sqrt (1 - e), Real.sqrt_pos.mpr hpos1, Real.sq_sqrt hpos1.le⟩
  have hw1 : w ≤ 1 := by
    by_contra hneg
    push Not at hneg
    nlinarith [mul_pos hw0 hw0]
  have hXpos : 0 < 1 - e / c := by
    have : 0 < q * (1 - e / c) := by
      rw [hqu]; have : 0 < (1 - e) * (a ^ 2 / th) := by positivity
      have : 0 < b ^ 2 / tc := by positivity
      linarith
    by_contra hneg
    push Not at hneg
    have := mul_nonpos_of_nonneg_of_nonpos hq.le hneg
    linarith
  -- weighted Cauchy–Schwarz with A = w a, B = b
  have hcs := cs2 (A := w * a) (B := b) hth htc
  have hcs' : (w * a + b) ^ 2 / τ ≤ w ^ 2 * a ^ 2 / th + b ^ 2 / tc := by
    have : (w * a) ^ 2 / th = w ^ 2 * a ^ 2 / th := by ring
    rw [this] at hcs; exact hcs
  have hwab : w * (a + b) ≤ w * a + b := by nlinarith
  have hlow : (w * (a + b)) ^ 2 ≤ (w * a + b) ^ 2 := by
    apply pow_le_pow_left₀ (by positivity) hwab
  have hkey : q * (1 - e / c) * τ ≥ w ^ 2 * (a + b) ^ 2 := by
    have h1 : w ^ 2 * a ^ 2 / th + b ^ 2 / tc = q * (1 - e / c) := by
      rw [hqu, ← hw2]; ring
    rw [← h1]
    have h2 : (w * (a + b)) ^ 2 / τ ≤ w ^ 2 * a ^ 2 / th + b ^ 2 / tc :=
      le_trans (div_le_div_of_nonneg_right hlow hτpos.le) hcs'
    rw [div_le_iff₀ hτpos] at h2
    nlinarith
  -- with u = e/c :  2 (1-u) >= (1-s)(1-c u)
  set u := e / c with hu
  have hcu : 1 - c * u = w ^ 2 := by
    have : c * u = e := by rw [hu]; field_simp
    rw [this]; linarith
  have hmain : q ^ 2 * (1 - u) * (1 + s) ≥ q * (1 - u) * (2 * P * τ) := by
    have h0 : 0 < q * (1 - u) := mul_pos hq hXpos
    have := mul_le_mul_of_nonneg_left hτle h0.le
    nlinarith
  have hmain2 : q ^ 2 * (1 - u) * (1 + s) ≥ 2 * P * (a + b) ^ 2 * w ^ 2 := by
    have h6 : 2 * P * (w ^ 2 * (a + b) ^ 2) ≤ 2 * P * (q * (1 - u) * τ) :=
      mul_le_mul_of_nonneg_left hkey (by positivity)
    nlinarith [h6, hmain]
  have hPt2 : 2 * P * (a + b) ^ 2 = Pt * q ^ 2 / 2 := by nlinarith [hPt]
  have hineq : 2 * (1 - u) ≥ (1 - s) * (1 - c * u) := by
    have h3 : q ^ 2 * (1 - u) * (1 + s) ≥ Pt * q ^ 2 / 2 * w ^ 2 := by
      rw [hPt2] at hmain2; exact hmain2
    have hq2 : 0 < q ^ 2 := by positivity
    have h4 : (1 - u) * (1 + s) ≥ Pt / 2 * w ^ 2 := by
      have : q ^ 2 * ((1 - u) * (1 + s)) ≥ q ^ 2 * (Pt / 2 * w ^ 2) := by nlinarith
      exact le_of_mul_le_mul_left this hq2
    have hPt3 : Pt = (1 - s) * (1 + s) := by nlinarith
    rw [hPt3, ← hcu] at h4
    have h5 : (1 + s) * (2 * (1 - u)) ≥ (1 + s) * ((1 - s) * (1 - c * u)) := by nlinarith
    exact le_of_mul_le_mul_left h5 (by linarith)
  -- final algebra
  have hden2 : 0 < 2 - c * (1 - s) := by nlinarith
  have hPt3 : Pt = (1 - s) * (1 + s) := by nlinarith
  have hdd : 2 * (1 + s) - c * Pt = (1 + s) * (2 - c * (1 - s)) := by rw [hPt3]; ring
  have hfrac : (1 - c) * Pt / (2 * (1 + s) - c * Pt) = (1 - c) * (1 - s) / (2 - c * (1 - s)) := by
    rw [hdd, hPt3]
    field_simp
  have hule : u ≤ (1 + s) / (2 - c * (1 - s)) := by
    rw [le_div_iff₀ hden2]; nlinarith
  have hrw : 1 - (1 - c) * (1 - s) / (2 - c * (1 - s)) = (1 + s) / (2 - c * (1 - s)) := by
    field_simp; ring
  rw [hfrac]
  linarith

end LowDissE3
