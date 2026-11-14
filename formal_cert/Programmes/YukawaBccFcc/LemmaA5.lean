import Programmes.YukawaBccFcc.Chains

namespace YukawaBccFcc

open Finset

/-! ## (A.6) -/

/-- `allFrom f a n` checks `f a, …, f (a + n - 1)`. -/
def allFrom (f : ℕ → Bool) (a : ℕ) : ℕ → Bool
  | 0 => true
  | n + 1 => f (a + n) && allFrom f a n

theorem allFrom_sound (f : ℕ → Bool) (a : ℕ) :
    ∀ n, allFrom f a n = true → ∀ j, a ≤ j → j < a + n → f j = true := by
  intro n
  induction n with
  | zero => intro _ j h1 h2; omega
  | succ n ih =>
    intro h j h1 h2
    simp only [allFrom, Bool.and_eq_true] at h
    by_cases hj : j = a + n
    · rw [hj]; exact h.1
    · exact ih h.2 j h1 (by omega)

theorem blocks_sound (f : ℕ → Bool) (N : ℕ) (h : ∀ k < N, allFrom f (100 * k) 100 = true) :
    ∀ j < 100 * N, f j = true := by
  intro j hj
  exact allFrom_sound f (100 * (j / 100)) 100 (h (j / 100) (by omega)) j (by omega) (by omega)

def cellA6 (j : ℕ) : Bool :=
  decide (0 ≤ C1.getD (j + 1) 0) &&
  decide ((3 / 1000 : ℚ) < paLo * polQ (fun n => n) Ntab 12 (C1.getD (j + 1) 0)
    - pbHi * polQ (fun n => n) Mtab 48 (C2.getD j 0) - 1 / 10 ^ 18)

theorem cellsA6_b0 : allFrom cellA6 (100 * 0) 100 = true := by decide +kernel

theorem cellsA6_b1 : allFrom cellA6 (100 * 1) 100 = true := by decide +kernel

theorem cellsA6_b2 : allFrom cellA6 (100 * 2) 100 = true := by decide +kernel

theorem cellsA6_b3 : allFrom cellA6 (100 * 3) 100 = true := by decide +kernel

theorem cellsA6_b4 : allFrom cellA6 (100 * 4) 100 = true := by decide +kernel

theorem cellsA6_b5 : allFrom cellA6 (100 * 5) 100 = true := by decide +kernel

theorem cellsA6_b6 : allFrom cellA6 (100 * 6) 100 = true := by decide +kernel

theorem cellsA6_b7 : allFrom cellA6 (100 * 7) 100 = true := by decide +kernel

theorem cellsA6_b8 : allFrom cellA6 (100 * 8) 100 = true := by decide +kernel

theorem cellsA6_b9 : allFrom cellA6 (100 * 9) 100 = true := by decide +kernel


theorem cellsA6 : ∀ j < 100 * 10, cellA6 j = true := by
  apply blocks_sound
  intro k hk
  interval_cases k
  · exact cellsA6_b0
  · exact cellsA6_b1
  · exact cellsA6_b2
  · exact cellsA6_b3
  · exact cellsA6_b4
  · exact cellsA6_b5
  · exact cellsA6_b6
  · exact cellsA6_b7
  · exact cellsA6_b8
  · exact cellsA6_b9

/-- **Lemma A.5, inequality (A.6)** of Luo–Wei, for every integer `0 ≤ j < 1000`. -/
theorem lemmaA5_A6 (j : ℕ) (hj : j < 1000) :
    Real.pi * a2 * ∑ n ∈ Icc (1 : ℕ) 12, (n : ℝ) * (Nc n : ℝ) *
        Real.exp (-(Real.pi * a2) * n * (1 + ((j : ℝ) + 1) / 10000))
      - Real.pi * b2 * ∑ l ∈ Icc (1 : ℕ) 48, (l : ℝ) * (Mc l : ℝ) *
        Real.exp (-(Real.pi * b2) * l * (1 + (j : ℝ) / 10000))
      - 1 / 10 ^ 18 > 3 / 1000 := by
  have hc := cellsA6 j (by omega)
  simp only [cellA6, Bool.and_eq_true, decide_eq_true_eq] at hc
  obtain ⟨h0, hc⟩ := hc
  have hcR : ((3 / 1000 : ℚ) : ℝ) < ((paLo * polQ (fun n => n) Ntab 12 (C1.getD (j + 1) 0)
      - pbHi * polQ (fun n => n) Mtab 48 (C2.getD j 0) - 1 / 10 ^ 18 : ℚ) : ℝ) := by exact_mod_cast hc
  simp only [Rat.cast_sub, Rat.cast_mul, polQ_cast] at hcR
  have e1 : ∑ n ∈ Icc (1 : ℕ) 12, (n : ℝ) * (Nc n : ℝ) * Real.exp (-(Real.pi * a2) * n * (1 + ((j : ℝ) + 1) / 10000))
      = polR (fun n => n) Nc 12 (Real.exp (-(Real.pi * a2) * (1 + ((j : ℝ) + 1) / 10000))) :=
    shell_sum_eq (fun n => n) Nc 12 _ _
  have e2 : ∑ l ∈ Icc (1 : ℕ) 48, (l : ℝ) * (Mc l : ℝ) * Real.exp (-(Real.pi * b2) * l * (1 + (j : ℝ) / 10000))
      = polR (fun n => n) Mc 48 (Real.exp (-(Real.pi * b2) * (1 + (j : ℝ) / 10000))) :=
    shell_sum_eq (fun n => n) Mc 48 _ _
  rw [e1, e2, polR_congr _ Nc Ntab 12 Nc_tab, polR_congr _ Mc Mtab 48 Mc_tab]
  have hX := chain_lo_bound (p := Real.pi * a2) pa_mem.2 (by decide +kernel) (by decide +kernel) C1_ok eOK_all.1
    eOK_all.2.1 heads_ok.1.1 heads_ok.1.2 heads_ok.2.1.2 (j + 1) (by rw [C_len.1]; omega)
  have hY := chain_hi_bound (p := Real.pi * b2) pb_mem.1 (by decide +kernel) (by decide +kernel) C2_ok
    eOK_all.2.2.1 eOK_all.2.2.2.1 heads_ok.2.2.1 heads_ok.2.2.2.1 j (by rw [C_len.2.1]; omega)
  have tX : ((1 : ℚ) : ℝ) + ((j + 1 : ℕ) : ℝ) * ((1 / 10000 : ℚ) : ℝ) = 1 + ((j : ℝ) + 1) / 10000 := by
    push_cast; ring
  have tY : ((1 : ℚ) : ℝ) + ((j : ℕ) : ℝ) * ((1 / 10000 : ℚ) : ℝ) = 1 + (j : ℝ) / 10000 := by
    push_cast; ring
  rw [tX] at hX
  rw [tY] at hY
  have h0' : (0 : ℝ) ≤ ((C1.getD (j + 1) 0 : ℚ) : ℝ) := by exact_mod_cast h0
  have hF := polR_mono (fun n => n) Ntab 12 h0' hX
  have hB := polR_mono (fun n => n) Mtab 48 (Real.exp_pos _).le hY
  have hpa : ((paLo : ℚ) : ℝ) ≤ Real.pi * a2 := pa_mem.1
  have hpb : Real.pi * b2 ≤ ((pbHi : ℚ) : ℝ) := pb_mem.2
  have hpaLo0 : (0 : ℝ) ≤ ((paLo : ℚ) : ℝ) := by exact_mod_cast (show (0 : ℚ) ≤ paLo by decide +kernel)
  have hF0 := polR_nonneg (fun n => n) Ntab 12 h0'
  have hB0 := polR_nonneg (fun n => n) Mtab 48 (Real.exp_pos (-(Real.pi * b2) * (1 + (j : ℝ) / 10000))).le
  have m1 : ((paLo : ℚ) : ℝ) * polR (fun n => n) Ntab 12 ((C1.getD (j + 1) 0 : ℚ) : ℝ) ≤
      Real.pi * a2 * polR (fun n => n) Ntab 12 (Real.exp (-(Real.pi * a2) * (1 + ((j : ℝ) + 1) / 10000))) :=
    mul_le_mul hpa hF hF0 pa_pos.le
  have m2 : Real.pi * b2 * polR (fun n => n) Mtab 48 (Real.exp (-(Real.pi * b2) * (1 + (j : ℝ) / 10000))) ≤
      ((pbHi : ℚ) : ℝ) * polR (fun n => n) Mtab 48 ((C2.getD j 0 : ℚ) : ℝ) :=
    mul_le_mul hpb hB hB0 (pb_pos.le.trans hpb)
  push_cast at hcR
  linarith

/-! ## (A.7) -/

def cellA7 (j : ℕ) : Bool :=
  decide (0 ≤ C3.getD (j + 1) 0) &&
  decide ((1 / 10000 : ℚ) < polQ (fun _ => 1) Mtab 48 (C3.getD (j + 1) 0) - polQ (fun _ => 1) Ntab 12 (C4.getD j 0)
    - 1 / 10 ^ 18)

theorem cellsA7_b0 : allFrom cellA7 (100 * 0) 100 = true := by decide +kernel

theorem cellsA7_b1 : allFrom cellA7 (100 * 1) 100 = true := by decide +kernel

theorem cellsA7_b2 : allFrom cellA7 (100 * 2) 100 = true := by decide +kernel

theorem cellsA7_b3 : allFrom cellA7 (100 * 3) 100 = true := by decide +kernel

theorem cellsA7_b4 : allFrom cellA7 (100 * 4) 100 = true := by decide +kernel

theorem cellsA7_b5 : allFrom cellA7 (100 * 5) 100 = true := by decide +kernel

theorem cellsA7_b6 : allFrom cellA7 (100 * 6) 100 = true := by decide +kernel

theorem cellsA7_b7 : allFrom cellA7 (100 * 7) 100 = true := by decide +kernel

theorem cellsA7_b8 : allFrom cellA7 (100 * 8) 100 = true := by decide +kernel

theorem cellsA7_b9 : allFrom cellA7 (100 * 9) 100 = true := by decide +kernel

theorem cellsA7_b10 : allFrom cellA7 (100 * 10) 100 = true := by decide +kernel

theorem cellsA7_b11 : allFrom cellA7 (100 * 11) 100 = true := by decide +kernel

theorem cellsA7_b12 : allFrom cellA7 (100 * 12) 100 = true := by decide +kernel

theorem cellsA7_b13 : allFrom cellA7 (100 * 13) 100 = true := by decide +kernel

theorem cellsA7_b14 : allFrom cellA7 (100 * 14) 100 = true := by decide +kernel

theorem cellsA7_b15 : allFrom cellA7 (100 * 15) 100 = true := by decide +kernel

theorem cellsA7_b16 : allFrom cellA7 (100 * 16) 100 = true := by decide +kernel

theorem cellsA7_b17 : allFrom cellA7 (100 * 17) 100 = true := by decide +kernel

theorem cellsA7_b18 : allFrom cellA7 (100 * 18) 100 = true := by decide +kernel

theorem cellsA7_b19 : allFrom cellA7 (100 * 19) 100 = true := by decide +kernel


theorem cellsA7 : ∀ j < 100 * 20, cellA7 j = true := by
  apply blocks_sound
  intro k hk
  interval_cases k
  · exact cellsA7_b0
  · exact cellsA7_b1
  · exact cellsA7_b2
  · exact cellsA7_b3
  · exact cellsA7_b4
  · exact cellsA7_b5
  · exact cellsA7_b6
  · exact cellsA7_b7
  · exact cellsA7_b8
  · exact cellsA7_b9
  · exact cellsA7_b10
  · exact cellsA7_b11
  · exact cellsA7_b12
  · exact cellsA7_b13
  · exact cellsA7_b14
  · exact cellsA7_b15
  · exact cellsA7_b16
  · exact cellsA7_b17
  · exact cellsA7_b18
  · exact cellsA7_b19

/-- **Lemma A.5, inequality (A.7)** of Luo–Wei, for every integer `0 ≤ j < 2000`. -/
theorem lemmaA5_A7 (j : ℕ) (hj : j < 2000) :
    ∑ l ∈ Icc (1 : ℕ) 48, (Mc l : ℝ) * Real.exp (-(Real.pi * b2) * l * (11 / 10 + ((j : ℝ) + 1) / 2000))
      - ∑ n ∈ Icc (1 : ℕ) 12, (Nc n : ℝ) * Real.exp (-(Real.pi * a2) * n * (11 / 10 + (j : ℝ) / 2000))
      - 1 / 10 ^ 18 > 1 / 10000 := by
  have hc := cellsA7 j (by omega)
  simp only [cellA7, Bool.and_eq_true, decide_eq_true_eq] at hc
  obtain ⟨h0, hc⟩ := hc
  have hcR : ((1 / 10000 : ℚ) : ℝ) < ((polQ (fun _ => 1) Mtab 48 (C3.getD (j + 1) 0)
      - polQ (fun _ => 1) Ntab 12 (C4.getD j 0) - 1 / 10 ^ 18 : ℚ) : ℝ) := by exact_mod_cast hc
  simp only [Rat.cast_sub, polQ_cast] at hcR
  have e1 : ∑ l ∈ Icc (1 : ℕ) 48, (Mc l : ℝ) * Real.exp (-(Real.pi * b2) * l * (11 / 10 + ((j : ℝ) + 1) / 2000))
      = polR (fun _ => 1) Mc 48 (Real.exp (-(Real.pi * b2) * (11 / 10 + ((j : ℝ) + 1) / 2000))) := by
    rw [← shell_sum_eq]; simp
  have e2 : ∑ n ∈ Icc (1 : ℕ) 12, (Nc n : ℝ) * Real.exp (-(Real.pi * a2) * n * (11 / 10 + (j : ℝ) / 2000))
      = polR (fun _ => 1) Nc 12 (Real.exp (-(Real.pi * a2) * (11 / 10 + (j : ℝ) / 2000))) := by
    rw [← shell_sum_eq]; simp
  rw [e1, e2, polR_congr _ Nc Ntab 12 Nc_tab, polR_congr _ Mc Mtab 48 Mc_tab]
  have hX := chain_lo_bound (p := Real.pi * b2) pb_mem.2 (by decide +kernel) (by decide +kernel) C3_ok
    eOK_all.2.2.2.2.1 eOK_all.2.2.2.2.2.1 heads_ok.2.2.2.2.1.1 heads_ok.2.2.2.2.1.2 heads_ok.2.2.2.2.2.1.2
    (j + 1) (by rw [C_len.2.2.1]; omega)
  have hY := chain_hi_bound (p := Real.pi * a2) pa_mem.1 (by decide +kernel) (by decide +kernel) C4_ok
    eOK_all.2.2.2.2.2.2.1 eOK_all.2.2.2.2.2.2.2 heads_ok.2.2.2.2.2.2.1 heads_ok.2.2.2.2.2.2.2 j
    (by rw [C_len.2.2.2]; omega)
  have tX : ((11 / 10 : ℚ) : ℝ) + ((j + 1 : ℕ) : ℝ) * ((1 / 2000 : ℚ) : ℝ) = 11 / 10 + ((j : ℝ) + 1) / 2000 := by
    push_cast; ring
  have tY : ((11 / 10 : ℚ) : ℝ) + ((j : ℕ) : ℝ) * ((1 / 2000 : ℚ) : ℝ) = 11 / 10 + (j : ℝ) / 2000 := by
    push_cast; ring
  rw [tX] at hX
  rw [tY] at hY
  have h0' : (0 : ℝ) ≤ ((C3.getD (j + 1) 0 : ℚ) : ℝ) := by exact_mod_cast h0
  have hF := polR_mono (fun _ => 1) Mtab 48 h0' hX
  have hB := polR_mono (fun _ => 1) Ntab 12 (Real.exp_pos _).le hY
  push_cast at hcR
  linarith

end YukawaBccFcc
