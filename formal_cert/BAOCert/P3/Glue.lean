import BAOCert.H0.Lemmas
import BAOCert.H0.PSD

/-! Glue lemmas for the assembled H0 exclusion theorem (P3). -/

namespace BAOCert.P3

open BAOCert BAOCert.H0

lemma gt_of_box {T L pm : ℚ} {v : ℝ} (hv : ((L : ℚ) : ℝ) + ((pm : ℚ) : ℝ) ≤ v) (h : T < L + pm) : (T : ℝ) < v := by
  have := (Rat.cast_lt (K := ℝ)).2 h
  push_cast at this
  linarith

lemma gt_of_slab {T L : ℚ} {Om h wb : ℝ} (hs : ((L : ℚ) : ℝ) ≤ BAOCert.P2.Data.chi2DESI Om (Kof h Om wb)) (hT : T < L) :
    (T : ℝ) < chi2tot Om h wb := by
  have := (Rat.cast_lt (K := ℝ)).2 hT
  unfold chi2tot
  have hp : (0 : ℝ) ≤ ((wb - 0.02218) / 0.00055) ^ 2 := sq_nonneg _
  linarith

/-- Outside `ω_b ∈ [μ - 7σ, μ + 7σ]` the BBN term alone exceeds 49. -/
lemma gt_of_prior {T : ℚ} {Om h wb : ℝ} (hw : wb < 1833 / 100000 ∨ 2603 / 100000 < wb) (hT : T < 49) :
    (T : ℝ) < chi2tot Om h wb := by
  have hT' := (Rat.cast_lt (K := ℝ)).2 hT
  push_cast at hT'
  have hb := chi2DESI_nonneg Om (Kof h Om wb)
  have hp : (49 : ℝ) < ((wb - 0.02218) / 0.00055) ^ 2 := by
    rcases hw with hw | hw
    · have : (wb - 0.02218) / 0.00055 < -7 := by rw [div_lt_iff₀ (by norm_num)]; linarith
      nlinarith
    · have : 7 < (wb - 0.02218) / 0.00055 := by rw [lt_div_iff₀ (by norm_num)]; linarith
      nlinarith
  unfold chi2tot
  linarith

end BAOCert.P3
