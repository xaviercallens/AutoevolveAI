import Programmes.YukawaBccFcc.LemmaA5

namespace YukawaBccFcc

open Finset

/-! ## (A.8) and the constants of Lemma 6.1 -/

/-- **Lemma A.5, inequality (A.8)**: `8 e^{(π a² - 3 π 2^{-4/3}) 21/10} > 25/2`. -/
theorem lemmaA5_A8 : 8 * Real.exp ((Real.pi * a2 - 3 * (Real.pi * b2)) * (21 / 10)) > 25 / 2 := by
  have hz : (((paLo - 3 * pbHi) * (21 / 10) : ℚ) : ℝ) ≤ (Real.pi * a2 - 3 * (Real.pi * b2)) * (21 / 10) := by
    push_cast; nlinarith [pa_mem.1, pb_mem.2]
  have hE := (eLo_le ((paLo - 3 * pbHi) * (21 / 10)) 30 (by decide +kernel)).trans (Real.exp_le_exp.2 hz)
  have hq : (25 / 2 : ℚ) < 8 * eLo ((paLo - 3 * pbHi) * (21 / 10)) 30 := by decide +kernel
  have hq' : ((25 / 2 : ℚ) : ℝ) < ((8 * eLo ((paLo - 3 * pbHi) * (21 / 10)) 30 : ℚ) : ℝ) := by exact_mod_cast hq
  push_cast at hq'
  linarith

/-- Proof of Lemma 6.1: `e^{-π a²} < 1/49`. -/
theorem lemma61_exp_fcc : Real.exp (-(Real.pi * a2)) < 1 / 49 := by
  have e0 : eOK (-paLo * 1) 30 = true := by decide +kernel
  have h := exp_neg_hi (p := Real.pi * a2) (pl := paLo) (t := 1) 30 pa_mem.1 (by decide +kernel) e0
  have hq : eHi (-paLo * 1) 30 < 1 / 49 := by decide +kernel
  have hq' : ((eHi (-paLo * 1) 30 : ℚ) : ℝ) < ((1 / 49 : ℚ) : ℝ) := by exact_mod_cast hq
  push_cast at h hq'
  simpa using lt_of_le_of_lt h hq'

/-- Proof of Lemma 6.1: `e^{-π 2^{-4/3}} < 3/10`. -/
theorem lemma61_exp_bcc : Real.exp (-(Real.pi * b2)) < 3 / 10 := by
  have h := exp_neg_hi (p := Real.pi * b2) (pl := pbLo) (t := 1) 30 pb_mem.1 (by decide +kernel) eOK_all.2.2.1
  have hq : eHi (-pbLo * 1) 30 < 3 / 10 := by decide +kernel
  have hq' : ((eHi (-pbLo * 1) 30 : ℚ) : ℝ) < ((3 / 10 : ℚ) : ℝ) := by exact_mod_cast hq
  push_cast at h hq'
  simpa using lt_of_le_of_lt h hq'

/-- Proof of Lemma 6.1: `π 2^{-4/3} < 5/4`. -/
theorem lemma61_pb_lt : Real.pi * b2 < 5 / 4 := by
  have hq : pbHi < 5 / 4 := by decide +kernel
  have hq' : ((pbHi : ℚ) : ℝ) < ((5 / 4 : ℚ) : ℝ) := by exact_mod_cast hq
  push_cast at hq'
  linarith [pb_mem.2]

/-- Proof of Lemma 6.1: `a² > 3 · 2^{-4/3}`. -/
theorem lemma61_a2_gt : a2 > 3 * b2 := by
  have hq : 3 * sHi < rLo := by decide +kernel
  have hq' : ((3 * sHi : ℚ) : ℝ) < ((rLo : ℚ) : ℝ) := by exact_mod_cast hq
  push_cast at hq'
  linarith [a2_br.1, b2_br.2]

/-- Proof of Lemma 6.1: `e^{-π a² · 21/10} < 1/128`. -/
theorem lemma61_exp_fcc_21 : Real.exp (-(Real.pi * a2) * (21 / 10)) < 1 / 128 := by
  have h1 : Real.exp (-(Real.pi * a2) * (21 / 10)) ≤ Real.exp (-(Real.pi * a2)) ^ 2 := by
    rw [← Real.exp_nat_mul]
    apply Real.exp_le_exp.2
    push_cast
    nlinarith [pa_pos]
  have h2 := lemma61_exp_fcc
  have h3 : Real.exp (-(Real.pi * a2)) ^ 2 < (1 / 49) ^ 2 :=
    pow_lt_pow_left₀ h2 (Real.exp_pos _).le (by norm_num)
  have h4 : ((1 : ℝ) / 49) ^ 2 < 1 / 128 := by norm_num
  linarith

/-- Proof of Lemma 6.1 (via Prop. 4.1): for `0 ≤ x ≤ 1/128`, `12 + 30((1-x)^{-2} - 1) < 25/2`. -/
theorem lemma61_prop41_bracket (x : ℝ) (_h0 : 0 ≤ x) (h1 : x ≤ 1 / 128) :
    12 + 30 * (1 / (1 - x) ^ 2 - 1) < 25 / 2 := by
  have hpos : (127 / 128 : ℝ) ^ 2 ≤ (1 - x) ^ 2 := by
    apply pow_le_pow_left₀ (by norm_num); linarith
  have hinv : 1 / (1 - x) ^ 2 ≤ 1 / (127 / 128 : ℝ) ^ 2 := one_div_le_one_div_of_le (by positivity) hpos
  have : (12 : ℝ) + 30 * (1 / (127 / 128 : ℝ) ^ 2 - 1) < 25 / 2 := by norm_num
  linarith

/-- Proof of Lemma 6.1, first omitted tail: every partial sum of `30 Σ_{n ≥ 13} n 49^{-n}` is `< 10^{-18}`. -/
theorem lemma61_tail_fcc (K : ℕ) :
    30 * ∑ k ∈ range K, ((13 + k : ℕ) : ℝ) * (1 / 49 : ℝ) ^ (13 + k) < 1 / 10 ^ 18 := by
  have h := tail_le (fun n => (n : ℝ) * (1 / 49 : ℝ) ^ n) 13 (14 / 637) (fun n => by positivity) (by norm_num)
    (by norm_num) (fun n hn => by
      have hn' : (13 : ℝ) ≤ n := by exact_mod_cast hn
      have hp : (0 : ℝ) ≤ (1 / 49 : ℝ) ^ n := by positivity
      simp only [Nat.cast_add, Nat.cast_one, pow_succ]
      nlinarith) K
  have : (30 : ℝ) * (((13 : ℕ) : ℝ) * (1 / 49 : ℝ) ^ 13 / (1 - 14 / 637)) < 1 / 10 ^ 18 := by norm_num
  linarith

/-- Proof of Lemma 6.1, second omitted tail: every partial sum of `(75/2) Σ_{l ≥ 49} l² (3/10)^l` is `< 10^{-18}`. -/
theorem lemma61_tail_bcc (K : ℕ) :
    75 / 2 * ∑ k ∈ range K, ((49 + k : ℕ) : ℝ) ^ 2 * (3 / 10 : ℝ) ^ (49 + k) < 1 / 10 ^ 18 := by
  have h := tail_le (fun n => (n : ℝ) ^ 2 * (3 / 10 : ℝ) ^ n) 49 ((50 / 49) ^ 2 * (3 / 10)) (fun n => by positivity)
    (by norm_num) (by norm_num) (fun n hn => by
      have hn' : (49 : ℝ) ≤ n := by exact_mod_cast hn
      have hp : (0 : ℝ) ≤ (3 / 10 : ℝ) ^ n := by positivity
      have hsq : ((n : ℝ) + 1) ^ 2 ≤ (50 / 49) ^ 2 * (n : ℝ) ^ 2 := by nlinarith
      simp only [Nat.cast_add, Nat.cast_one, pow_succ (3 / 10 : ℝ)]
      nlinarith) K
  have : (75 / 2 : ℝ) * (((49 : ℕ) : ℝ) ^ 2 * (3 / 10 : ℝ) ^ 49 / (1 - (50 / 49) ^ 2 * (3 / 10))) < 1 / 10 ^ 18 := by
    norm_num
  linarith

/-- The rational omitted-tail bound printed in the proof of Lemma A.6. -/
theorem lemmaA6_tail :
    60 * (1 / 49 : ℚ) ^ 13 / (1 - 1 / 49) + 60 * (3 / 10 : ℚ) ^ 49 / (1 - 3 / 10) < 7 / 10 ^ 21 := by decide +kernel

/-- The rational step of Lemma A.1: `55995/10⁶ < 7/125`. -/
theorem lemmaA1_rational : (55995 / 10 ^ 6 : ℚ) < 7 / 125 := by decide +kernel

end YukawaBccFcc
