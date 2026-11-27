import Mathlib.Tactic

set_option linter.unusedSimpArgs false
set_option maxHeartbeats 0
namespace SLRAudit.N63

/-- velocities of certificate n = 63 -/
def v : Fin 63 → ℕ := ![2, 6, 10, 14, 18, 20, 22, 26, 28, 30, 34, 38, 40, 42, 44, 46, 50, 52, 54, 56, 58, 60, 62, 66, 68, 70, 74, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94, 98, 100, 102, 104, 106, 110, 112, 114, 116, 118, 120, 122, 124, 126, 12, 16, 24, 36, 48, 64, 128, 1, 3, 9, 27, 81]
/-- shifts s_i = a_i / 520 -/
def s : Fin 63 → ℚ := ![0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 0/520, 264/520, 512/520, 264/520, 264/520, 256/520, 8/520, 512/520, 385/520, 390/520, 388/520, 391/520, 391/520]

set_option maxRecDepth 1000000 in
theorem v_injective : Function.Injective v := by decide
theorem v_pos : ∀ i, 0 < v i := by decide

/-- covering: for every real t some runner is within distance < 1/64 of an integer. -/
theorem cover : ∀ t : ℝ, ∃ i : Fin 63, ∃ k : ℤ, |((s i : ℚ) : ℝ) + ((v i : ℕ) : ℝ) * t - (k : ℝ)| < 1 / 64 := by
  intro t
  have h0 : (0 : ℝ) ≤ t - ⌊t⌋ := by have := Int.floor_le t; linarith
  have h1 : t - ⌊t⌋ < (1 : ℝ) := by have := Int.lt_floor_add_one t; linarith
  rcases lt_or_ge (t - ⌊t⌋) (1 / 128 : ℝ) with c0 | c0
  · refine ⟨0, 0 + 2 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [h0, c0]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 532480 : ℝ) with c1 | c1
  · refine ⟨57, 2 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c0, c1]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 7936 : ℝ) with c2 | c2
  · refine ⟨49, 1 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1, c2]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 7808 : ℝ) with c3 | c3
  · refine ⟨48, 1 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2, c3]
  rcases lt_or_ge (t - ⌊t⌋) (13 / 1536 : ℝ) with c4 | c4
  · refine ⟨47, 1 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c3, c4]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 7552 : ℝ) with c5 | c5
  · refine ⟨46, 1 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c4, c5]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 7424 : ℝ) with c6 | c6
  · refine ⟨45, 1 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c5, c6]
  rcases lt_or_ge (t - ⌊t⌋) (1097 / 112320 : ℝ) with c7 | c7
  · refine ⟨61, 1 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c6, c7]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 6528 : ℝ) with c8 | c8
  · refine ⟨39, 1 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c7, c8]
  rcases lt_or_ge (t - ⌊t⌋) (13 / 1280 : ℝ) with c9 | c9
  · refine ⟨38, 1 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c8, c9]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 6272 : ℝ) with c10 | c10
  · refine ⟨37, 1 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c9, c10]
  rcases lt_or_ge (t - ⌊t⌋) (2177 / 199680 : ℝ) with c11 | c11
  · refine ⟨55, 1 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c10, c11]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 5888 : ℝ) with c12 | c12
  · refine ⟨35, 1 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c11, c12]
  rcases lt_or_ge (t - ⌊t⌋) (13 / 1152 : ℝ) with c13 | c13
  · refine ⟨34, 1 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c12, c13]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 5632 : ℝ) with c14 | c14
  · refine ⟨33, 1 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c13, c14]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 5504 : ℝ) with c15 | c15
  · refine ⟨32, 1 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c14, c15]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 5376 : ℝ) with c16 | c16
  · refine ⟨31, 1 + 84 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c15, c16]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 5248 : ℝ) with c17 | c17
  · refine ⟨30, 1 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c16, c17]
  rcases lt_or_ge (t - ⌊t⌋) (13 / 1024 : ℝ) with c18 | c18
  · refine ⟨29, 1 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c17, c18]
  rcases lt_or_ge (t - ⌊t⌋) (5 / 384 : ℝ) with c19 | c19
  · refine ⟨28, 1 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c18, c19]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 4864 : ℝ) with c20 | c20
  · refine ⟨27, 1 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c19, c20]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 149760 : ℝ) with c21 | c21
  · refine ⟨54, 1 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c20, c21]
  rcases lt_or_ge (t - ⌊t⌋) (13 / 896 : ℝ) with c22 | c22
  · refine ⟨25, 1 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c21, c22]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 4352 : ℝ) with c23 | c23
  · refine ⟨24, 1 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c22, c23]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 4224 : ℝ) with c24 | c24
  · refine ⟨23, 1 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c23, c24]
  rcases lt_or_ge (t - ⌊t⌋) (4161 / 266240 : ℝ) with c25 | c25
  · refine ⟨56, 1 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c24, c25]
  rcases lt_or_ge (t - ⌊t⌋) (8449 / 532480 : ℝ) with c26 | c26
  · refine ⟨57, 3 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c25, c26]
  rcases lt_or_ge (t - ⌊t⌋) (43 / 2688 : ℝ) with c27 | c27
  · refine ⟨50, 2 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c26, c27]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 3968 : ℝ) with c28 | c28
  · refine ⟨22, 1 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c27, c28]
  rcases lt_or_ge (t - ⌊t⌋) (129 / 7808 : ℝ) with c29 | c29
  · refine ⟨48, 2 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c28, c29]
  rcases lt_or_ge (t - ⌊t⌋) (13 / 768 : ℝ) with c30 | c30
  · refine ⟨21, 1 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c29, c30]
  rcases lt_or_ge (t - ⌊t⌋) (129 / 7552 : ℝ) with c31 | c31
  · refine ⟨46, 2 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c30, c31]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 3712 : ℝ) with c32 | c32
  · refine ⟨20, 1 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c31, c32]
  rcases lt_or_ge (t - ⌊t⌋) (43 / 2432 : ℝ) with c33 | c33
  · refine ⟨44, 2 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c32, c33]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 3584 : ℝ) with c34 | c34
  · refine ⟨19, 1 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c33, c34]
  rcases lt_or_ge (t - ⌊t⌋) (129 / 7040 : ℝ) with c35 | c35
  · refine ⟨42, 2 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c34, c35]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 3456 : ℝ) with c36 | c36
  · refine ⟨18, 1 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c35, c36]
  rcases lt_or_ge (t - ⌊t⌋) (129 / 6784 : ℝ) with c37 | c37
  · refine ⟨41, 2 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c36, c37]
  rcases lt_or_ge (t - ⌊t⌋) (5 / 256 : ℝ) with c38 | c38
  · refine ⟨17, 1 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c37, c38]
  rcases lt_or_ge (t - ⌊t⌋) (43 / 2176 : ℝ) with c39 | c39
  · refine ⟨39, 2 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c38, c39]
  rcases lt_or_ge (t - ⌊t⌋) (13 / 640 : ℝ) with c40 | c40
  · refine ⟨16, 1 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c39, c40]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 99840 : ℝ) with c41 | c41
  · refine ⟨53, 1 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c40, c41]
  rcases lt_or_ge (t - ⌊t⌋) (129 / 6016 : ℝ) with c42 | c42
  · refine ⟨36, 2 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c41, c42]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 2944 : ℝ) with c43 | c43
  · refine ⟨15, 1 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c42, c43]
  rcases lt_or_ge (t - ⌊t⌋) (43 / 1920 : ℝ) with c44 | c44
  · refine ⟨34, 2 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c43, c44]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 2816 : ℝ) with c45 | c45
  · refine ⟨14, 1 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c44, c45]
  rcases lt_or_ge (t - ⌊t⌋) (3 / 128 : ℝ) with c46 | c46
  · refine ⟨32, 2 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c45, c46]
  rcases lt_or_ge (t - ⌊t⌋) (12609 / 532480 : ℝ) with c47 | c47
  · refine ⟨57, 4 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c46, c47]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 2688 : ℝ) with c48 | c48
  · refine ⟨13, 1 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c47, c48]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 7936 : ℝ) with c49 | c49
  · refine ⟨49, 3 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c48, c49]
  rcases lt_or_ge (t - ⌊t⌋) (129 / 5248 : ℝ) with c50 | c50
  · refine ⟨30, 2 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c49, c50]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 7808 : ℝ) with c51 | c51
  · refine ⟨48, 3 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c50, c51]
  rcases lt_or_ge (t - ⌊t⌋) (13 / 512 : ℝ) with c52 | c52
  · refine ⟨12, 1 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c51, c52]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 7552 : ℝ) with c53 | c53
  · refine ⟨46, 3 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c52, c53]
  rcases lt_or_ge (t - ⌊t⌋) (43 / 1664 : ℝ) with c54 | c54
  · refine ⟨28, 2 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c53, c54]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 7424 : ℝ) with c55 | c55
  · refine ⟨45, 3 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c54, c55]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 2432 : ℝ) with c56 | c56
  · refine ⟨11, 1 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c55, c56]
  rcases lt_or_ge (t - ⌊t⌋) (1121 / 37440 : ℝ) with c57 | c57
  · refine ⟨60, 1 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c56, c57]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 6400 : ℝ) with c58 | c58
  · refine ⟨38, 3 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c57, c58]
  rcases lt_or_ge (t - ⌊t⌋) (43 / 1408 : ℝ) with c59 | c59
  · refine ⟨23, 2 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c58, c59]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 6272 : ℝ) with c60 | c60
  · refine ⟨37, 3 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c59, c60]
  rcases lt_or_ge (t - ⌊t⌋) (8321 / 266240 : ℝ) with c61 | c61
  · refine ⟨56, 2 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c60, c61]
  rcases lt_or_ge (t - ⌊t⌋) (6337 / 199680 : ℝ) with c62 | c62
  · refine ⟨55, 2 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c61, c62]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 8064 : ℝ) with c63 | c63
  · refine ⟨50, 4 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c62, c63]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 6016 : ℝ) with c64 | c64
  · refine ⟨36, 3 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c63, c64]
  rcases lt_or_ge (t - ⌊t⌋) (129 / 3968 : ℝ) with c65 | c65
  · refine ⟨22, 2 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c64, c65]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 5888 : ℝ) with c66 | c66
  · refine ⟨35, 3 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c65, c66]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 7808 : ℝ) with c67 | c67
  · refine ⟨48, 4 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c66, c67]
  rcases lt_or_ge (t - ⌊t⌋) (13 / 384 : ℝ) with c68 | c68
  · refine ⟨9, 1 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c67, c68]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 7552 : ℝ) with c69 | c69
  · refine ⟨46, 4 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c68, c69]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 5632 : ℝ) with c70 | c70
  · refine ⟨33, 3 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c69, c70]
  rcases lt_or_ge (t - ⌊t⌋) (129 / 3712 : ℝ) with c71 | c71
  · refine ⟨20, 2 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c70, c71]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 5504 : ℝ) with c72 | c72
  · refine ⟨32, 3 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c71, c72]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 7296 : ℝ) with c73 | c73
  · refine ⟨44, 4 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c72, c73]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 1792 : ℝ) with c74 | c74
  · refine ⟨8, 1 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c73, c74]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 7040 : ℝ) with c75 | c75
  · refine ⟨42, 4 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c74, c75]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 5248 : ℝ) with c76 | c76
  · refine ⟨30, 3 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c75, c76]
  rcases lt_or_ge (t - ⌊t⌋) (43 / 1152 : ℝ) with c77 | c77
  · refine ⟨18, 2 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c76, c77]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 5120 : ℝ) with c78 | c78
  · refine ⟨29, 3 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c77, c78]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 6784 : ℝ) with c79 | c79
  · refine ⟨41, 4 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c78, c79]
  rcases lt_or_ge (t - ⌊t⌋) (5 / 128 : ℝ) with c80 | c80
  · refine ⟨7, 1 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c79, c80]
  rcases lt_or_ge (t - ⌊t⌋) (20929 / 532480 : ℝ) with c81 | c81
  · refine ⟨57, 6 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c80, c81]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 4864 : ℝ) with c82 | c82
  · refine ⟨27, 3 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c81, c82]
  rcases lt_or_ge (t - ⌊t⌋) (107 / 2688 : ℝ) with c83 | c83
  · refine ⟨50, 5 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c82, c83]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 49920 : ℝ) with c84 | c84
  · refine ⟨51, 1 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c83, c84]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 7552 : ℝ) with c85 | c85
  · refine ⟨46, 5 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c84, c85]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 6016 : ℝ) with c86 | c86
  · refine ⟨36, 4 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c85, c86]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 4480 : ℝ) with c87 | c87
  · refine ⟨25, 3 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c86, c87]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 7424 : ℝ) with c88 | c88
  · refine ⟨45, 5 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c87, c88]
  rcases lt_or_ge (t - ⌊t⌋) (129 / 2944 : ℝ) with c89 | c89
  · refine ⟨15, 2 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c88, c89]
  rcases lt_or_ge (t - ⌊t⌋) (107 / 2432 : ℝ) with c90 | c90
  · refine ⟨44, 5 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c89, c90]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 4352 : ℝ) with c91 | c91
  · refine ⟨24, 3 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c90, c91]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 5760 : ℝ) with c92 | c92
  · refine ⟨34, 4 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c91, c92]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 7168 : ℝ) with c93 | c93
  · refine ⟨43, 5 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c92, c93]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 1408 : ℝ) with c94 | c94
  · refine ⟨6, 1 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c93, c94]
  rcases lt_or_ge (t - ⌊t⌋) (5257 / 112320 : ℝ) with c95 | c95
  · refine ⟨61, 2 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c94, c95]
  rcases lt_or_ge (t - ⌊t⌋) (12481 / 266240 : ℝ) with c96 | c96
  · refine ⟨56, 3 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c95, c96]
  rcases lt_or_ge (t - ⌊t⌋) (25089 / 532480 : ℝ) with c97 | c97
  · refine ⟨57, 7 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c96, c97]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 6784 : ℝ) with c98 | c98
  · refine ⟨41, 5 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c97, c98]
  rcases lt_or_ge (t - ⌊t⌋) (43 / 896 : ℝ) with c99 | c99
  · refine ⟨13, 2 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c98, c99]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 6656 : ℝ) with c100 | c100
  · refine ⟨40, 5 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c99, c100]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 3968 : ℝ) with c101 | c101
  · refine ⟨22, 3 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c100, c101]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 5248 : ℝ) with c102 | c102
  · refine ⟨30, 4 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c101, c102]
  rcases lt_or_ge (t - ⌊t⌋) (107 / 2176 : ℝ) with c103 | c103
  · refine ⟨39, 5 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c102, c103]
  rcases lt_or_ge (t - ⌊t⌋) (385 / 7808 : ℝ) with c104 | c104
  · refine ⟨48, 6 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c103, c104]
  rcases lt_or_ge (t - ⌊t⌋) (13 / 256 : ℝ) with c105 | c105
  · refine ⟨5, 1 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c104, c105]
  rcases lt_or_ge (t - ⌊t⌋) (385 / 7552 : ℝ) with c106 | c106
  · refine ⟨46, 6 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c105, c106]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 6272 : ℝ) with c107 | c107
  · refine ⟨37, 5 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c106, c107]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 4992 : ℝ) with c108 | c108
  · refine ⟨28, 4 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c107, c108]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 3712 : ℝ) with c109 | c109
  · refine ⟨20, 3 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c108, c109]
  rcases lt_or_ge (t - ⌊t⌋) (3499 / 66560 : ℝ) with c110 | c110
  · refine ⟨55, 3 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c109, c110]
  rcases lt_or_ge (t - ⌊t⌋) (129 / 2432 : ℝ) with c111 | c111
  · refine ⟨11, 2 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c110, c111]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 6016 : ℝ) with c112 | c112
  · refine ⟨36, 5 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c111, c112]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 3584 : ℝ) with c113 | c113
  · refine ⟨19, 3 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c112, c113]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 4736 : ℝ) with c114 | c114
  · refine ⟨26, 4 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c113, c114]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 5888 : ℝ) with c115 | c115
  · refine ⟨35, 5 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c114, c115]
  rcases lt_or_ge (t - ⌊t⌋) (7 / 128 : ℝ) with c116 | c116
  · refine ⟨42, 6 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c115, c116]
  rcases lt_or_ge (t - ⌊t⌋) (29249 / 532480 : ℝ) with c117 | c117
  · refine ⟨57, 8 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c116, c117]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 1152 : ℝ) with c118 | c118
  · refine ⟨4, 1 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c117, c118]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 7936 : ℝ) with c119 | c119
  · refine ⟨49, 7 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c118, c119]
  rcases lt_or_ge (t - ⌊t⌋) (385 / 6784 : ℝ) with c120 | c120
  · refine ⟨41, 6 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c119, c120]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 5632 : ℝ) with c121 | c121
  · refine ⟨33, 5 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c120, c121]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 4480 : ℝ) with c122 | c122
  · refine ⟨25, 4 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c121, c122]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 7808 : ℝ) with c123 | c123
  · refine ⟨48, 7 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c122, c123]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 3328 : ℝ) with c124 | c124
  · refine ⟨17, 3 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c123, c124]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 5504 : ℝ) with c125 | c125
  · refine ⟨32, 5 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c124, c125]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 7680 : ℝ) with c126 | c126
  · refine ⟨47, 7 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c125, c126]
  rcases lt_or_ge (t - ⌊t⌋) (129 / 2176 : ℝ) with c127 | c127
  · refine ⟨10, 2 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c126, c127]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 7552 : ℝ) with c128 | c128
  · refine ⟨46, 7 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c127, c128]
  rcases lt_or_ge (t - ⌊t⌋) (107 / 1792 : ℝ) with c129 | c129
  · refine ⟨31, 5 + 84 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c128, c129]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 3200 : ℝ) with c130 | c130
  · refine ⟨16, 3 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c129, c130]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 7424 : ℝ) with c131 | c131
  · refine ⟨45, 7 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c130, c131]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 4224 : ℝ) with c132 | c132
  · refine ⟨23, 4 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c131, c132]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 5248 : ℝ) with c133 | c133
  · refine ⟨30, 5 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c132, c133]
  rcases lt_or_ge (t - ⌊t⌋) (55 / 896 : ℝ) with c134 | c134
  · refine ⟨37, 6 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c133, c134]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 7296 : ℝ) with c135 | c135
  · refine ⟨44, 7 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c134, c135]
  rcases lt_or_ge (t - ⌊t⌋) (2091 / 33280 : ℝ) with c136 | c136
  · refine ⟨53, 2 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c135, c136]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 66560 : ℝ) with c137 | c137
  · refine ⟨52, 2 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c136, c137]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 3968 : ℝ) with c138 | c138
  · refine ⟨22, 4 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c137, c138]
  rcases lt_or_ge (t - ⌊t⌋) (811 / 12480 : ℝ) with c139 | c139
  · refine ⟨62, 6 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c138, c139]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 2944 : ℝ) with c140 | c140
  · refine ⟨15, 3 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c139, c140]
  rcases lt_or_ge (t - ⌊t⌋) (513 / 7808 : ℝ) with c141 | c141
  · refine ⟨48, 8 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c140, c141]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 4864 : ℝ) with c142 | c142
  · refine ⟨27, 5 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c141, c142]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 6784 : ℝ) with c143 | c143
  · refine ⟨41, 7 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c142, c143]
  rcases lt_or_ge (t - ⌊t⌋) (43 / 640 : ℝ) with c144 | c144
  · refine ⟨9, 2 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c143, c144]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 6656 : ℝ) with c145 | c145
  · refine ⟨40, 7 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c144, c145]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 4736 : ℝ) with c146 | c146
  · refine ⟨26, 5 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c145, c146]
  rcases lt_or_ge (t - ⌊t⌋) (513 / 7552 : ℝ) with c147 | c147
  · refine ⟨46, 8 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c146, c147]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 2816 : ℝ) with c148 | c148
  · refine ⟨14, 3 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c147, c148]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 6528 : ℝ) with c149 | c149
  · refine ⟨39, 7 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c148, c149]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 3712 : ℝ) with c150 | c150
  · refine ⟨20, 4 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c149, c150]
  rcases lt_or_ge (t - ⌊t⌋) (10433 / 149760 : ℝ) with c151 | c151
  · refine ⟨54, 3 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c150, c151]
  rcases lt_or_ge (t - ⌊t⌋) (385 / 5504 : ℝ) with c152 | c152
  · refine ⟨32, 6 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c151, c152]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 6400 : ℝ) with c153 | c153
  · refine ⟨38, 7 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c152, c153]
  rcases lt_or_ge (t - ⌊t⌋) (9 / 128 : ℝ) with c154 | c154
  · refine ⟨44, 8 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c153, c154]
  rcases lt_or_ge (t - ⌊t⌋) (37569 / 532480 : ℝ) with c155 | c155
  · refine ⟨57, 10 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c154, c155]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 896 : ℝ) with c156 | c156
  · refine ⟨3, 1 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c155, c156]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 7936 : ℝ) with c157 | c157
  · refine ⟨49, 9 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c156, c157]
  rcases lt_or_ge (t - ⌊t⌋) (513 / 7040 : ℝ) with c158 | c158
  · refine ⟨42, 8 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c157, c158]
  rcases lt_or_ge (t - ⌊t⌋) (14657 / 199680 : ℝ) with c159 | c159
  · refine ⟨55, 4 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c158, c159]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 4352 : ℝ) with c160 | c160
  · refine ⟨24, 5 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c159, c160]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 7808 : ℝ) with c161 | c161
  · refine ⟨48, 9 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c160, c161]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 3456 : ℝ) with c162 | c162
  · refine ⟨18, 4 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c161, c162]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 6016 : ℝ) with c163 | c163
  · refine ⟨36, 7 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c162, c163]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 2560 : ℝ) with c164 | c164
  · refine ⟨12, 3 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c163, c164]
  rcases lt_or_ge (t - ⌊t⌋) (513 / 6784 : ℝ) with c165 | c165
  · refine ⟨41, 8 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c164, c165]
  rcases lt_or_ge (t - ⌊t⌋) (107 / 1408 : ℝ) with c166 | c166
  · refine ⟨23, 5 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c165, c166]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 5888 : ℝ) with c167 | c167
  · refine ⟨35, 7 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c166, c167]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 7552 : ℝ) with c168 | c168
  · refine ⟨46, 9 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c167, c168]
  rcases lt_or_ge (t - ⌊t⌋) (129 / 1664 : ℝ) with c169 | c169
  · refine ⟨7, 2 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c168, c169]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 7424 : ℝ) with c170 | c170
  · refine ⟨45, 9 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c169, c170]
  rcases lt_or_ge (t - ⌊t⌋) (20801 / 266240 : ℝ) with c171 | c171
  · refine ⟨56, 5 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c170, c171]
  rcases lt_or_ge (t - ⌊t⌋) (17 / 192 : ℝ) with c172 | c172
  · refine ⟨59, 1 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c171, c172]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 2176 : ℝ) with c173 | c173
  · refine ⟨10, 3 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c172, c173]
  rcases lt_or_ge (t - ⌊t⌋) (705 / 7936 : ℝ) with c174 | c174
  · refine ⟨49, 11 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c173, c174]
  rcases lt_or_ge (t - ⌊t⌋) (57 / 640 : ℝ) with c175 | c175
  · refine ⟨34, 8 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c174, c175]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 3584 : ℝ) with c176 | c176
  · refine ⟨19, 5 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c175, c176]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 4992 : ℝ) with c177 | c177
  · refine ⟨28, 7 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c176, c177]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 6400 : ℝ) with c178 | c178
  · refine ⟨38, 9 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c177, c178]
  rcases lt_or_ge (t - ⌊t⌋) (705 / 7808 : ℝ) with c179 | c179
  · refine ⟨48, 11 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c178, c179]
  rcases lt_or_ge (t - ⌊t⌋) (129 / 1408 : ℝ) with c180 | c180
  · refine ⟨6, 2 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c179, c180]
  rcases lt_or_ge (t - ⌊t⌋) (47 / 512 : ℝ) with c181 | c181
  · refine ⟨47, 11 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c180, c181]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 6272 : ℝ) with c182 | c182
  · refine ⟨37, 9 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c181, c182]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 4864 : ℝ) with c183 | c183
  · refine ⟨27, 7 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c182, c183]
  rcases lt_or_ge (t - ⌊t⌋) (107 / 1152 : ℝ) with c184 | c184
  · refine ⟨18, 5 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c183, c184]
  rcases lt_or_ge (t - ⌊t⌋) (513 / 5504 : ℝ) with c185 | c185
  · refine ⟨32, 8 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c184, c185]
  rcases lt_or_ge (t - ⌊t⌋) (705 / 7552 : ℝ) with c186 | c186
  · refine ⟨46, 11 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c185, c186]
  rcases lt_or_ge (t - ⌊t⌋) (24961 / 266240 : ℝ) with c187 | c187
  · refine ⟨56, 6 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c186, c187]
  rcases lt_or_ge (t - ⌊t⌋) (18817 / 199680 : ℝ) with c188 | c188
  · refine ⟨55, 5 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c187, c188]
  rcases lt_or_ge (t - ⌊t⌋) (641 / 6784 : ℝ) with c189 | c189
  · refine ⟨41, 10 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c188, c189]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 4736 : ℝ) with c190 | c190
  · refine ⟨26, 7 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c189, c190]
  rcases lt_or_ge (t - ⌊t⌋) (705 / 7424 : ℝ) with c191 | c191
  · refine ⟨45, 11 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c190, c191]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 2688 : ℝ) with c192 | c192
  · refine ⟨13, 4 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c191, c192]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 6016 : ℝ) with c193 | c193
  · refine ⟨36, 9 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c192, c193]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 3328 : ℝ) with c194 | c194
  · refine ⟨17, 5 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c193, c194]
  rcases lt_or_ge (t - ⌊t⌋) (235 / 2432 : ℝ) with c195 | c195
  · refine ⟨44, 11 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c194, c195]
  rcases lt_or_ge (t - ⌊t⌋) (14593 / 149760 : ℝ) with c196 | c196
  · refine ⟨54, 4 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c195, c196]
  rcases lt_or_ge (t - ⌊t⌋) (513 / 5248 : ℝ) with c197 | c197
  · refine ⟨30, 8 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c196, c197]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 5888 : ℝ) with c198 | c198
  · refine ⟨35, 9 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c197, c198]
  rcases lt_or_ge (t - ⌊t⌋) (641 / 6528 : ℝ) with c199 | c199
  · refine ⟨39, 10 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c198, c199]
  rcases lt_or_ge (t - ⌊t⌋) (705 / 7168 : ℝ) with c200 | c200
  · refine ⟨43, 11 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c199, c200]
  rcases lt_or_ge (t - ⌊t⌋) (769 / 7808 : ℝ) with c201 | c201
  · refine ⟨48, 12 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c200, c201]
  rcases lt_or_ge (t - ⌊t⌋) (13 / 128 : ℝ) with c202 | c202
  · refine ⟨2, 1 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c201, c202]
  rcases lt_or_ge (t - ⌊t⌋) (54209 / 532480 : ℝ) with c203 | c203
  · refine ⟨57, 14 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c202, c203]
  rcases lt_or_ge (t - ⌊t⌋) (11459 / 112320 : ℝ) with c204 | c204
  · refine ⟨62, 9 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c203, c204]
  rcases lt_or_ge (t - ⌊t⌋) (641 / 6272 : ℝ) with c205 | c205
  · refine ⟨37, 10 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c204, c205]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 5632 : ℝ) with c206 | c206
  · refine ⟨33, 9 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c205, c206]
  rcases lt_or_ge (t - ⌊t⌋) (171 / 1664 : ℝ) with c207 | c207
  · refine ⟨28, 8 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c206, c207]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 4352 : ℝ) with c208 | c208
  · refine ⟨24, 7 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c207, c208]
  rcases lt_or_ge (t - ⌊t⌋) (119 / 1152 : ℝ) with c209 | c209
  · refine ⟨50, 13 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c208, c209]
  rcases lt_or_ge (t - ⌊t⌋) (10433 / 99840 : ℝ) with c210 | c210
  · refine ⟨53, 3 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c209, c210]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 5504 : ℝ) with c211 | c211
  · refine ⟨32, 9 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c210, c211]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 7936 : ℝ) with c212 | c212
  · refine ⟨49, 13 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c211, c212]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 2432 : ℝ) with c213 | c213
  · refine ⟨11, 4 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c212, c213]
  rcases lt_or_ge (t - ⌊t⌋) (705 / 6656 : ℝ) with c214 | c214
  · refine ⟨40, 11 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c213, c214]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 4224 : ℝ) with c215 | c215
  · refine ⟨23, 7 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c214, c215]
  rcases lt_or_ge (t - ⌊t⌋) (641 / 6016 : ℝ) with c216 | c216
  · refine ⟨36, 10 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c215, c216]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 7808 : ℝ) with c217 | c217
  · refine ⟨48, 13 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c216, c217]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 1792 : ℝ) with c218 | c218
  · refine ⟨8, 3 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c217, c218]
  rcases lt_or_ge (t - ⌊t⌋) (235 / 2176 : ℝ) with c219 | c219
  · refine ⟨39, 11 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c218, c219]
  rcases lt_or_ge (t - ⌊t⌋) (513 / 4736 : ℝ) with c220 | c220
  · refine ⟨26, 8 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c219, c220]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 7680 : ℝ) with c221 | c221
  · refine ⟨47, 13 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c220, c221]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 2944 : ℝ) with c222 | c222
  · refine ⟨15, 5 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c221, c222]
  rcases lt_or_ge (t - ⌊t⌋) (29121 / 266240 : ℝ) with c223 | c223
  · refine ⟨56, 7 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c222, c223]
  rcases lt_or_ge (t - ⌊t⌋) (58369 / 532480 : ℝ) with c224 | c224
  · refine ⟨57, 15 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c223, c224]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 5248 : ℝ) with c225 | c225
  · refine ⟨30, 9 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c224, c225]
  rcases lt_or_ge (t - ⌊t⌋) (141 / 1280 : ℝ) with c226 | c226
  · refine ⟨38, 11 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c225, c226]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 7552 : ℝ) with c227 | c227
  · refine ⟨46, 13 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c226, c227]
  rcases lt_or_ge (t - ⌊t⌋) (43 / 384 : ℝ) with c228 | c228
  · refine ⟨4, 2 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c227, c228]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 7424 : ℝ) with c229 | c229
  · refine ⟨45, 13 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c228, c229]
  rcases lt_or_ge (t - ⌊t⌋) (705 / 6272 : ℝ) with c230 | c230
  · refine ⟨37, 11 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c229, c230]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 5120 : ℝ) with c231 | c231
  · refine ⟨29, 9 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c230, c231]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 3968 : ℝ) with c232 | c232
  · refine ⟨22, 7 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c231, c232]
  rcases lt_or_ge (t - ⌊t⌋) (769 / 6784 : ℝ) with c233 | c233
  · refine ⟨41, 12 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c232, c233]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 2816 : ℝ) with c234 | c234
  · refine ⟨14, 5 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c233, c234]
  rcases lt_or_ge (t - ⌊t⌋) (38537 / 336960 : ℝ) with c235 | c235
  · refine ⟨62, 10 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c234, c235]
  rcases lt_or_ge (t - ⌊t⌋) (513 / 4480 : ℝ) with c236 | c236
  · refine ⟨25, 8 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c235, c236]
  rcases lt_or_ge (t - ⌊t⌋) (7659 / 66560 : ℝ) with c237 | c237
  · refine ⟨55, 6 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c236, c237]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 1664 : ℝ) with c238 | c238
  · refine ⟨7, 3 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c237, c238]
  rcases lt_or_ge (t - ⌊t⌋) (119 / 1024 : ℝ) with c239 | c239
  · refine ⟨43, 13 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c238, c239]
  rcases lt_or_ge (t - ⌊t⌋) (641 / 5504 : ℝ) with c240 | c240
  · refine ⟨32, 10 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c239, c240]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 3840 : ℝ) with c241 | c241
  · refine ⟨21, 7 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c240, c241]
  rcases lt_or_ge (t - ⌊t⌋) (15 / 128 : ℝ) with c242 | c242
  · refine ⟨36, 11 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c241, c242]
  rcases lt_or_ge (t - ⌊t⌋) (62529 / 532480 : ℝ) with c243 | c243
  · refine ⟨57, 16 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c242, c243]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 2176 : ℝ) with c244 | c244
  · refine ⟨10, 4 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c243, c244]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 7040 : ℝ) with c245 | c245
  · refine ⟨42, 13 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c244, c245]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 4864 : ℝ) with c246 | c246
  · refine ⟨27, 9 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c245, c246]
  rcases lt_or_ge (t - ⌊t⌋) (897 / 7552 : ℝ) with c247 | c247
  · refine ⟨46, 14 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c246, c247]
  rcases lt_or_ge (t - ⌊t⌋) (107 / 896 : ℝ) with c248 | c248
  · refine ⟨13, 5 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c247, c248]
  rcases lt_or_ge (t - ⌊t⌋) (705 / 5888 : ℝ) with c249 | c249
  · refine ⟨35, 11 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c248, c249]
  rcases lt_or_ge (t - ⌊t⌋) (13577 / 112320 : ℝ) with c250 | c250
  · refine ⟨61, 4 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c249, c250]
  rcases lt_or_ge (t - ⌊t⌋) (31 / 256 : ℝ) with c251 | c251
  · refine ⟨49, 15 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c250, c251]
  rcases lt_or_ge (t - ⌊t⌋) (171 / 1408 : ℝ) with c252 | c252
  · refine ⟨23, 8 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c251, c252]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 4736 : ℝ) with c253 | c253
  · refine ⟨26, 9 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c252, c253]
  rcases lt_or_ge (t - ⌊t⌋) (641 / 5248 : ℝ) with c254 | c254
  · refine ⟨30, 10 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c253, c254]
  rcases lt_or_ge (t - ⌊t⌋) (47 / 384 : ℝ) with c255 | c255
  · refine ⟨34, 11 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c254, c255]
  rcases lt_or_ge (t - ⌊t⌋) (769 / 6272 : ℝ) with c256 | c256
  · refine ⟨37, 12 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c255, c256]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 6784 : ℝ) with c257 | c257
  · refine ⟨41, 13 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c256, c257]
  rcases lt_or_ge (t - ⌊t⌋) (299 / 2432 : ℝ) with c258 | c258
  · refine ⟨44, 14 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c257, c258]
  rcases lt_or_ge (t - ⌊t⌋) (961 / 7808 : ℝ) with c259 | c259
  · refine ⟨48, 15 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c258, c259]
  rcases lt_or_ge (t - ⌊t⌋) (2091 / 16640 : ℝ) with c260 | c260
  · refine ⟨51, 2 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c259, c260]
  rcases lt_or_ge (t - ⌊t⌋) (8449 / 66560 : ℝ) with c261 | c261
  · refine ⟨52, 3 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c260, c261]
  rcases lt_or_ge (t - ⌊t⌋) (1025 / 8064 : ℝ) with c262 | c262
  · refine ⟨50, 16 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c261, c262]
  rcases lt_or_ge (t - ⌊t⌋) (961 / 7552 : ℝ) with c263 | c263
  · refine ⟨46, 15 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c262, c263]
  rcases lt_or_ge (t - ⌊t⌋) (897 / 7040 : ℝ) with c264 | c264
  · refine ⟨42, 14 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c263, c264]
  rcases lt_or_ge (t - ⌊t⌋) (49 / 384 : ℝ) with c265 | c265
  · refine ⟨39, 13 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c264, c265]
  rcases lt_or_ge (t - ⌊t⌋) (769 / 6016 : ℝ) with c266 | c266
  · refine ⟨36, 12 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c265, c266]
  rcases lt_or_ge (t - ⌊t⌋) (705 / 5504 : ℝ) with c267 | c267
  · refine ⟨32, 11 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c266, c267]
  rcases lt_or_ge (t - ⌊t⌋) (641 / 4992 : ℝ) with c268 | c268
  · refine ⟨28, 10 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c267, c268]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 4480 : ℝ) with c269 | c269
  · refine ⟨25, 9 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c268, c269]
  rcases lt_or_ge (t - ⌊t⌋) (513 / 3968 : ℝ) with c270 | c270
  · refine ⟨22, 8 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c269, c270]
  rcases lt_or_ge (t - ⌊t⌋) (961 / 7424 : ℝ) with c271 | c271
  · refine ⟨45, 15 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c270, c271]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 3456 : ℝ) with c272 | c272
  · refine ⟨18, 7 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c271, c272]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 6400 : ℝ) with c273 | c273
  · refine ⟨38, 13 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c272, c273]
  rcases lt_or_ge (t - ⌊t⌋) (385 / 2944 : ℝ) with c274 | c274
  · refine ⟨15, 6 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c273, c274]
  rcases lt_or_ge (t - ⌊t⌋) (235 / 1792 : ℝ) with c275 | c275
  · refine ⟨31, 11 + 84 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c274, c275]
  rcases lt_or_ge (t - ⌊t⌋) (1025 / 7808 : ℝ) with c276 | c276
  · refine ⟨48, 16 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c275, c276]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 2432 : ℝ) with c277 | c277
  · refine ⟨11, 5 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c276, c277]
  rcases lt_or_ge (t - ⌊t⌋) (897 / 6784 : ℝ) with c278 | c278
  · refine ⟨41, 14 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c277, c278]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 4352 : ℝ) with c279 | c279
  · refine ⟨24, 9 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c278, c279]
  rcases lt_or_ge (t - ⌊t⌋) (17 / 128 : ℝ) with c280 | c280
  · refine ⟨37, 13 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c279, c280]
  rcases lt_or_ge (t - ⌊t⌋) (70849 / 532480 : ℝ) with c281 | c281
  · refine ⟨57, 18 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c280, c281]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 1920 : ℝ) with c282 | c282
  · refine ⟨9, 4 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c281, c282]
  rcases lt_or_ge (t - ⌊t⌋) (961 / 7168 : ℝ) with c283 | c283
  · refine ⟨43, 15 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c282, c283]
  rcases lt_or_ge (t - ⌊t⌋) (705 / 5248 : ℝ) with c284 | c284
  · refine ⟨30, 11 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c283, c284]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 3328 : ℝ) with c285 | c285
  · refine ⟨17, 7 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c284, c285]
  rcases lt_or_ge (t - ⌊t⌋) (121 / 896 : ℝ) with c286 | c286
  · refine ⟨50, 17 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c285, c286]
  rcases lt_or_ge (t - ⌊t⌋) (641 / 4736 : ℝ) with c287 | c287
  · refine ⟨26, 10 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c286, c287]
  rcases lt_or_ge (t - ⌊t⌋) (27137 / 199680 : ℝ) with c288 | c288
  · refine ⟨55, 7 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c287, c288]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 1408 : ℝ) with c289 | c289
  · refine ⟨6, 3 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c288, c289]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 7936 : ℝ) with c290 | c290
  · refine ⟨49, 17 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c289, c290]
  rcases lt_or_ge (t - ⌊t⌋) (299 / 2176 : ℝ) with c291 | c291
  · refine ⟨39, 14 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c290, c291]
  rcases lt_or_ge (t - ⌊t⌋) (141 / 1024 : ℝ) with c292 | c292
  · refine ⟨29, 11 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c291, c292]
  rcases lt_or_ge (t - ⌊t⌋) (5281 / 37440 : ℝ) with c293 | c293
  · refine ⟨60, 2 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c292, c293]
  rcases lt_or_ge (t - ⌊t⌋) (235 / 1664 : ℝ) with c294 | c294
  · refine ⟨28, 11 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c293, c294]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 5888 : ℝ) with c295 | c295
  · refine ⟨35, 13 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c294, c295]
  rcases lt_or_ge (t - ⌊t⌋) (961 / 6784 : ℝ) with c296 | c296
  · refine ⟨41, 15 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c295, c296]
  rcases lt_or_ge (t - ⌊t⌋) (363 / 2560 : ℝ) with c297 | c297
  · refine ⟨47, 17 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c296, c297]
  rcases lt_or_ge (t - ⌊t⌋) (129 / 896 : ℝ) with c298 | c298
  · refine ⟨3, 2 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c297, c298]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 7552 : ℝ) with c299 | c299
  · refine ⟨46, 17 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c298, c299]
  rcases lt_or_ge (t - ⌊t⌋) (961 / 6656 : ℝ) with c300 | c300
  · refine ⟨40, 15 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c299, c300]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 5760 : ℝ) with c301 | c301
  · refine ⟨34, 13 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c300, c301]
  rcases lt_or_ge (t - ⌊t⌋) (705 / 4864 : ℝ) with c302 | c302
  · refine ⟨27, 11 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c301, c302]
  rcases lt_or_ge (t - ⌊t⌋) (14593 / 99840 : ℝ) with c303 | c303
  · refine ⟨53, 4 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c302, c303]
  rcases lt_or_ge (t - ⌊t⌋) (769 / 5248 : ℝ) with c304 | c304
  · refine ⟨30, 12 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c303, c304]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 7424 : ℝ) with c305 | c305
  · refine ⟨45, 17 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c304, c305]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 2176 : ℝ) with c306 | c306
  · refine ⟨10, 5 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c305, c306]
  rcases lt_or_ge (t - ⌊t⌋) (1153 / 7808 : ℝ) with c307 | c307
  · refine ⟨48, 18 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c306, c307]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 5632 : ℝ) with c308 | c308
  · refine ⟨33, 13 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c307, c308]
  rcases lt_or_ge (t - ⌊t⌋) (19 / 128 : ℝ) with c309 | c309
  · refine ⟨18, 8 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c308, c309]
  rcases lt_or_ge (t - ⌊t⌋) (79169 / 532480 : ℝ) with c310 | c310
  · refine ⟨57, 20 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c309, c310]
  rcases lt_or_ge (t - ⌊t⌋) (705 / 4736 : ℝ) with c311 | c311
  · refine ⟨26, 11 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c310, c311]
  rcases lt_or_ge (t - ⌊t⌋) (897 / 6016 : ℝ) with c312 | c312
  · refine ⟨36, 14 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c311, c312]
  rcases lt_or_ge (t - ⌊t⌋) (363 / 2432 : ℝ) with c313 | c313
  · refine ⟨44, 17 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c312, c313]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 1280 : ℝ) with c314 | c314
  · refine ⟨5, 3 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c313, c314]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 8064 : ℝ) with c315 | c315
  · refine ⟨50, 19 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c314, c315]
  rcases lt_or_ge (t - ⌊t⌋) (1025 / 6784 : ℝ) with c316 | c316
  · refine ⟨41, 16 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c315, c316]
  rcases lt_or_ge (t - ⌊t⌋) (51017 / 336960 : ℝ) with c317 | c317
  · refine ⟨62, 13 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c316, c317]
  rcases lt_or_ge (t - ⌊t⌋) (641 / 4224 : ℝ) with c318 | c318
  · refine ⟨23, 10 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c317, c318]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 7168 : ℝ) with c319 | c319
  · refine ⟨43, 17 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c318, c319]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 2944 : ℝ) with c320 | c320
  · refine ⟨15, 7 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c319, c320]
  rcases lt_or_ge (t - ⌊t⌋) (22913 / 149760 : ℝ) with c321 | c321
  · refine ⟨54, 6 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c320, c321]
  rcases lt_or_ge (t - ⌊t⌋) (961 / 6272 : ℝ) with c322 | c322
  · refine ⟨37, 15 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c321, c322]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 7936 : ℝ) with c323 | c323
  · refine ⟨49, 19 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c322, c323]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 1664 : ℝ) with c324 | c324
  · refine ⟨7, 4 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c323, c324]
  rcases lt_or_ge (t - ⌊t⌋) (99 / 640 : ℝ) with c325 | c325
  · refine ⟨42, 17 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c324, c325]
  rcases lt_or_ge (t - ⌊t⌋) (119 / 768 : ℝ) with c326 | c326
  · refine ⟨31, 13 + 84 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c325, c326]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 3712 : ℝ) with c327 | c327
  · refine ⟨20, 9 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c326, c327]
  rcases lt_or_ge (t - ⌊t⌋) (299 / 1920 : ℝ) with c328 | c328
  · refine ⟨34, 14 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c327, c328]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 7808 : ℝ) with c329 | c329
  · refine ⟨48, 19 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c328, c329]
  rcases lt_or_ge (t - ⌊t⌋) (41601 / 266240 : ℝ) with c330 | c330
  · refine ⟨56, 10 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c329, c330]
  rcases lt_or_ge (t - ⌊t⌋) (31297 / 199680 : ℝ) with c331 | c331
  · refine ⟨55, 8 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c330, c331]
  rcases lt_or_ge (t - ⌊t⌋) (1025 / 6528 : ℝ) with c332 | c332
  · refine ⟨39, 16 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c331, c332]
  rcases lt_or_ge (t - ⌊t⌋) (17737 / 112320 : ℝ) with c333 | c333
  · refine ⟨61, 5 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c332, c333]
  rcases lt_or_ge (t - ⌊t⌋) (385 / 2432 : ℝ) with c334 | c334
  · refine ⟨11, 6 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c333, c334]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 7680 : ℝ) with c335 | c335
  · refine ⟨47, 19 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c334, c335]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 5248 : ℝ) with c336 | c336
  · refine ⟨30, 13 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c335, c336]
  rcases lt_or_ge (t - ⌊t⌋) (61 / 384 : ℝ) with c337 | c337
  · refine ⟨50, 20 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c336, c337]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 2816 : ℝ) with c338 | c338
  · refine ⟨14, 7 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c337, c338]
  rcases lt_or_ge (t - ⌊t⌋) (961 / 6016 : ℝ) with c339 | c339
  · refine ⟨36, 15 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c338, c339]
  rcases lt_or_ge (t - ⌊t⌋) (513 / 3200 : ℝ) with c340 | c340
  · refine ⟨16, 8 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c339, c340]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 6784 : ℝ) with c341 | c341
  · refine ⟨41, 17 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c340, c341]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 3584 : ℝ) with c342 | c342
  · refine ⟨19, 9 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c341, c342]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 7552 : ℝ) with c343 | c343
  · refine ⟨46, 19 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c342, c343]
  rcases lt_or_ge (t - ⌊t⌋) (641 / 3968 : ℝ) with c344 | c344
  · refine ⟨22, 10 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c343, c344]
  rcases lt_or_ge (t - ⌊t⌋) (705 / 4352 : ℝ) with c345 | c345
  · refine ⟨24, 11 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c344, c345]
  rcases lt_or_ge (t - ⌊t⌋) (769 / 4736 : ℝ) with c346 | c346
  · refine ⟨26, 12 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c345, c346]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 5120 : ℝ) with c347 | c347
  · refine ⟨29, 13 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c346, c347]
  rcases lt_or_ge (t - ⌊t⌋) (897 / 5504 : ℝ) with c348 | c348
  · refine ⟨32, 14 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c347, c348]
  rcases lt_or_ge (t - ⌊t⌋) (961 / 5888 : ℝ) with c349 | c349
  · refine ⟨35, 15 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c348, c349]
  rcases lt_or_ge (t - ⌊t⌋) (1025 / 6272 : ℝ) with c350 | c350
  · refine ⟨37, 16 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c349, c350]
  rcases lt_or_ge (t - ⌊t⌋) (55177 / 336960 : ℝ) with c351 | c351
  · refine ⟨62, 14 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c350, c351]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 7424 : ℝ) with c352 | c352
  · refine ⟨45, 19 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c351, c352]
  rcases lt_or_ge (t - ⌊t⌋) (21 / 128 : ℝ) with c353 | c353
  · refine ⟨48, 20 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c352, c353]
  rcases lt_or_ge (t - ⌊t⌋) (87489 / 532480 : ℝ) with c354 | c354
  · refine ⟨57, 22 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c353, c354]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 384 : ℝ) with c355 | c355
  · refine ⟨1, 1 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c354, c355]
  rcases lt_or_ge (t - ⌊t⌋) (1345 / 7936 : ℝ) with c356 | c356
  · refine ⟨49, 21 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c355, c356]
  rcases lt_or_ge (t - ⌊t⌋) (1281 / 7552 : ℝ) with c357 | c357
  · refine ⟨46, 20 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c356, c357]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 7168 : ℝ) with c358 | c358
  · refine ⟨43, 19 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c357, c358]
  rcases lt_or_ge (t - ⌊t⌋) (1153 / 6784 : ℝ) with c359 | c359
  · refine ⟨41, 18 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c358, c359]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 6400 : ℝ) with c360 | c360
  · refine ⟨38, 17 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c359, c360]
  rcases lt_or_ge (t - ⌊t⌋) (1025 / 6016 : ℝ) with c361 | c361
  · refine ⟨36, 16 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c360, c361]
  rcases lt_or_ge (t - ⌊t⌋) (961 / 5632 : ℝ) with c362 | c362
  · refine ⟨33, 15 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c361, c362]
  rcases lt_or_ge (t - ⌊t⌋) (897 / 5248 : ℝ) with c363 | c363
  · refine ⟨30, 14 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c362, c363]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 4864 : ℝ) with c364 | c364
  · refine ⟨27, 13 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c363, c364]
  rcases lt_or_ge (t - ⌊t⌋) (769 / 4480 : ℝ) with c365 | c365
  · refine ⟨25, 12 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c364, c365]
  rcases lt_or_ge (t - ⌊t⌋) (45761 / 266240 : ℝ) with c366 | c366
  · refine ⟨56, 11 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c365, c366]
  rcases lt_or_ge (t - ⌊t⌋) (91649 / 532480 : ℝ) with c367 | c367
  · refine ⟨57, 23 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c366, c367]
  rcases lt_or_ge (t - ⌊t⌋) (1345 / 7808 : ℝ) with c368 | c368
  · refine ⟨48, 21 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c367, c368]
  rcases lt_or_ge (t - ⌊t⌋) (641 / 3712 : ℝ) with c369 | c369
  · refine ⟨20, 10 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c368, c369]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 7040 : ℝ) with c370 | c370
  · refine ⟨42, 19 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c369, c370]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 3328 : ℝ) with c371 | c371
  · refine ⟨17, 9 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c370, c371]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 6272 : ℝ) with c372 | c372
  · refine ⟨37, 17 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c371, c372]
  rcases lt_or_ge (t - ⌊t⌋) (513 / 2944 : ℝ) with c373 | c373
  · refine ⟨15, 8 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c372, c373]
  rcases lt_or_ge (t - ⌊t⌋) (961 / 5504 : ℝ) with c374 | c374
  · refine ⟨32, 15 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c373, c374]
  rcases lt_or_ge (t - ⌊t⌋) (1409 / 8064 : ℝ) with c375 | c375
  · refine ⟨50, 22 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c374, c375]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 2560 : ℝ) with c376 | c376
  · refine ⟨12, 7 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c375, c376]
  rcases lt_or_ge (t - ⌊t⌋) (427 / 2432 : ℝ) with c377 | c377
  · refine ⟨44, 20 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c376, c377]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 4736 : ℝ) with c378 | c378
  · refine ⟨26, 13 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c377, c378]
  rcases lt_or_ge (t - ⌊t⌋) (6593 / 37440 : ℝ) with c379 | c379
  · refine ⟨62, 15 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c378, c379]
  rcases lt_or_ge (t - ⌊t⌋) (385 / 2176 : ℝ) with c380 | c380
  · refine ⟨10, 6 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c379, c380]
  rcases lt_or_ge (t - ⌊t⌋) (11819 / 66560 : ℝ) with c381 | c381
  · refine ⟨55, 9 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c380, c381]
  rcases lt_or_ge (t - ⌊t⌋) (705 / 3968 : ℝ) with c382 | c382
  · refine ⟨22, 11 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c381, c382]
  rcases lt_or_ge (t - ⌊t⌋) (205 / 1152 : ℝ) with c383 | c383
  · refine ⟨34, 16 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c382, c383]
  rcases lt_or_ge (t - ⌊t⌋) (1345 / 7552 : ℝ) with c384 | c384
  · refine ⟨46, 21 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c383, c384]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 1792 : ℝ) with c385 | c385
  · refine ⟨8, 5 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c384, c385]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 6784 : ℝ) with c386 | c386
  · refine ⟨41, 19 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c385, c386]
  rcases lt_or_ge (t - ⌊t⌋) (23 / 128 : ℝ) with c387 | c387
  · refine ⟨28, 14 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c386, c387]
  rcases lt_or_ge (t - ⌊t⌋) (95809 / 532480 : ℝ) with c388 | c388
  · refine ⟨57, 24 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c387, c388]
  rcases lt_or_ge (t - ⌊t⌋) (27073 / 149760 : ℝ) with c389 | c389
  · refine ⟨54, 7 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c388, c389]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 6016 : ℝ) with c390 | c390
  · refine ⟨36, 17 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c389, c390]
  rcases lt_or_ge (t - ⌊t⌋) (1345 / 7424 : ℝ) with c391 | c391
  · refine ⟨45, 21 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c390, c391]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 1408 : ℝ) with c392 | c392
  · refine ⟨6, 4 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c391, c392]
  rcases lt_or_ge (t - ⌊t⌋) (491 / 2688 : ℝ) with c393 | c393
  · refine ⟨50, 23 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c392, c393]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 6656 : ℝ) with c394 | c394
  · refine ⟨40, 19 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c393, c394]
  rcases lt_or_ge (t - ⌊t⌋) (961 / 5248 : ℝ) with c395 | c395
  · refine ⟨30, 15 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c394, c395]
  rcases lt_or_ge (t - ⌊t⌋) (47 / 256 : ℝ) with c396 | c396
  · refine ⟨21, 11 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c395, c396]
  rcases lt_or_ge (t - ⌊t⌋) (1153 / 6272 : ℝ) with c397 | c397
  · refine ⟨37, 18 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c396, c397]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 2432 : ℝ) with c398 | c398
  · refine ⟨11, 7 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c397, c398]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 5888 : ℝ) with c399 | c399
  · refine ⟨35, 17 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c398, c399]
  rcases lt_or_ge (t - ⌊t⌋) (641 / 3456 : ℝ) with c400 | c400
  · refine ⟨18, 10 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c399, c400]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 7936 : ℝ) with c401 | c401
  · refine ⟨49, 23 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c400, c401]
  rcases lt_or_ge (t - ⌊t⌋) (119 / 640 : ℝ) with c402 | c402
  · refine ⟨25, 13 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c401, c402]
  rcases lt_or_ge (t - ⌊t⌋) (1025 / 5504 : ℝ) with c403 | c403
  · refine ⟨32, 16 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c402, c403]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 6528 : ℝ) with c404 | c404
  · refine ⟨39, 19 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c403, c404]
  rcases lt_or_ge (t - ⌊t⌋) (1409 / 7552 : ℝ) with c405 | c405
  · refine ⟨46, 22 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c404, c405]
  rcases lt_or_ge (t - ⌊t⌋) (6251 / 33280 : ℝ) with c406 | c406
  · refine ⟨53, 5 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c405, c406]
  rcases lt_or_ge (t - ⌊t⌋) (12609 / 66560 : ℝ) with c407 | c407
  · refine ⟨52, 4 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c406, c407]
  rcases lt_or_ge (t - ⌊t⌋) (705 / 3712 : ℝ) with c408 | c408
  · refine ⟨20, 11 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c407, c408]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 6400 : ℝ) with c409 | c409
  · refine ⟨38, 19 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c408, c409]
  rcases lt_or_ge (t - ⌊t⌋) (171 / 896 : ℝ) with c410 | c410
  · refine ⟨13, 8 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c409, c410]
  rcases lt_or_ge (t - ⌊t⌋) (269 / 1408 : ℝ) with c411 | c411
  · refine ⟨42, 21 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c410, c411]
  rcases lt_or_ge (t - ⌊t⌋) (49 / 256 : ℝ) with c412 | c412
  · refine ⟨24, 13 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c411, c412]
  rcases lt_or_ge (t - ⌊t⌋) (1153 / 6016 : ℝ) with c413 | c413
  · refine ⟨36, 18 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c412, c413]
  rcases lt_or_ge (t - ⌊t⌋) (491 / 2560 : ℝ) with c414 | c414
  · refine ⟨47, 23 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c413, c414]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 1664 : ℝ) with c415 | c415
  · refine ⟨7, 5 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c414, c415]
  rcases lt_or_ge (t - ⌊t⌋) (1409 / 7296 : ℝ) with c416 | c416
  · refine ⟨44, 22 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c415, c416]
  rcases lt_or_ge (t - ⌊t⌋) (99 / 512 : ℝ) with c417 | c417
  · refine ⟨33, 17 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c416, c417]
  rcases lt_or_ge (t - ⌊t⌋) (769 / 3968 : ℝ) with c418 | c418
  · refine ⟨22, 12 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c417, c418]
  rcases lt_or_ge (t - ⌊t⌋) (811 / 4160 : ℝ) with c419 | c419
  · refine ⟨61, 6 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c418, c419]
  rcases lt_or_ge (t - ⌊t⌋) (25 / 128 : ℝ) with c420 | c420
  · refine ⟨30, 16 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c419, c420]
  rcases lt_or_ge (t - ⌊t⌋) (104129 / 532480 : ℝ) with c421 | c421
  · refine ⟨57, 26 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c420, c421]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 2944 : ℝ) with c422 | c422
  · refine ⟨15, 9 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c421, c422]
  rcases lt_or_ge (t - ⌊t⌋) (427 / 2176 : ℝ) with c423 | c423
  · refine ⟨39, 20 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c422, c423]
  rcases lt_or_ge (t - ⌊t⌋) (705 / 3584 : ℝ) with c424 | c424
  · refine ⟨19, 11 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c423, c424]
  rcases lt_or_ge (t - ⌊t⌋) (1537 / 7808 : ℝ) with c425 | c425
  · refine ⟨48, 24 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c424, c425]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 4224 : ℝ) with c426 | c426
  · refine ⟨23, 13 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c425, c426]
  rcases lt_or_ge (t - ⌊t⌋) (961 / 4864 : ℝ) with c427 | c427
  · refine ⟨27, 15 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c426, c427]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 5504 : ℝ) with c428 | c428
  · refine ⟨32, 17 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c427, c428]
  rcases lt_or_ge (t - ⌊t⌋) (39617 / 199680 : ℝ) with c429 | c429
  · refine ⟨55, 10 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c428, c429]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 8064 : ℝ) with c430 | c430
  · refine ⟨50, 25 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c429, c430]
  rcases lt_or_ge (t - ⌊t⌋) (129 / 640 : ℝ) with c431 | c431
  · refine ⟨2, 2 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c430, c431]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 7936 : ℝ) with c432 | c432
  · refine ⟨49, 25 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c431, c432]
  rcases lt_or_ge (t - ⌊t⌋) (491 / 2432 : ℝ) with c433 | c433
  · refine ⟨44, 23 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c432, c433]
  rcases lt_or_ge (t - ⌊t⌋) (1345 / 6656 : ℝ) with c434 | c434
  · refine ⟨40, 21 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c433, c434]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 6016 : ℝ) with c435 | c435
  · refine ⟨36, 19 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c434, c435]
  rcases lt_or_ge (t - ⌊t⌋) (363 / 1792 : ℝ) with c436 | c436
  · refine ⟨31, 17 + 84 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c435, c436]
  rcases lt_or_ge (t - ⌊t⌋) (961 / 4736 : ℝ) with c437 | c437
  · refine ⟨26, 15 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c436, c437]
  rcases lt_or_ge (t - ⌊t⌋) (54081 / 266240 : ℝ) with c438 | c438
  · refine ⟨56, 13 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c437, c438]
  rcases lt_or_ge (t - ⌊t⌋) (108289 / 532480 : ℝ) with c439 | c439
  · refine ⟨57, 27 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c438, c439]
  rcases lt_or_ge (t - ⌊t⌋) (1537 / 7552 : ℝ) with c440 | c440
  · refine ⟨46, 24 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c439, c440]
  rcases lt_or_ge (t - ⌊t⌋) (235 / 1152 : ℝ) with c441 | c441
  · refine ⟨18, 11 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c440, c441]
  rcases lt_or_ge (t - ⌊t⌋) (183 / 896 : ℝ) with c442 | c442
  · refine ⟨37, 20 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c441, c442]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 2816 : ℝ) with c443 | c443
  · refine ⟨14, 9 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c442, c443]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 7808 : ℝ) with c444 | c444
  · refine ⟨48, 25 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c443, c444]
  rcases lt_or_ge (t - ⌊t⌋) (1025 / 4992 : ℝ) with c445 | c445
  · refine ⟨28, 16 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c444, c445]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 7168 : ℝ) with c446 | c446
  · refine ⟨43, 23 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c445, c446]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 2176 : ℝ) with c447 | c447
  · refine ⟨10, 7 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c446, c447]
  rcases lt_or_ge (t - ⌊t⌋) (185 / 896 : ℝ) with c448 | c448
  · refine ⟨50, 26 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c447, c448]
  rcases lt_or_ge (t - ⌊t⌋) (10433 / 49920 : ℝ) with c449 | c449
  · refine ⟨51, 3 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c448, c449]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 7040 : ℝ) with c450 | c450
  · refine ⟨42, 23 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c449, c450]
  rcases lt_or_ge (t - ⌊t⌋) (1153 / 5504 : ℝ) with c451 | c451
  · refine ⟨32, 18 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c450, c451]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 3968 : ℝ) with c452 | c452
  · refine ⟨22, 13 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c451, c452]
  rcases lt_or_ge (t - ⌊t⌋) (269 / 1280 : ℝ) with c453 | c453
  · refine ⟨38, 21 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c452, c453]
  rcases lt_or_ge (t - ⌊t⌋) (27 / 128 : ℝ) with c454 | c454
  · refine ⟨11, 8 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c453, c454]
  rcases lt_or_ge (t - ⌊t⌋) (112449 / 532480 : ℝ) with c455 | c455
  · refine ⟨57, 28 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c454, c455]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 5760 : ℝ) with c456 | c456
  · refine ⟨34, 19 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c455, c456]
  rcases lt_or_ge (t - ⌊t⌋) (705 / 3328 : ℝ) with c457 | c457
  · refine ⟨17, 11 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c456, c457]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 7552 : ℝ) with c458 | c458
  · refine ⟨46, 25 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c457, c458]
  rcases lt_or_ge (t - ⌊t⌋) (299 / 1408 : ℝ) with c459 | c459
  · refine ⟨23, 14 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c458, c459]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 5120 : ℝ) with c460 | c460
  · refine ⟨29, 17 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c459, c460]
  rcases lt_or_ge (t - ⌊t⌋) (1281 / 6016 : ℝ) with c461 | c461
  · refine ⟨36, 20 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c460, c461]
  rcases lt_or_ge (t - ⌊t⌋) (23939 / 112320 : ℝ) with c462 | c462
  · refine ⟨62, 18 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c461, c462]
  rcases lt_or_ge (t - ⌊t⌋) (1665 / 7808 : ℝ) with c463 | c463
  · refine ⟨48, 26 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c462, c463]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 896 : ℝ) with c464 | c464
  · refine ⟨3, 3 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c463, c464]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 7424 : ℝ) with c465 | c465
  · refine ⟨45, 25 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c464, c465]
  rcases lt_or_ge (t - ⌊t⌋) (1409 / 6528 : ℝ) with c466 | c466
  · refine ⟨39, 22 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c465, c466]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 5632 : ℝ) with c467 | c467
  · refine ⟨33, 19 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c466, c467]
  rcases lt_or_ge (t - ⌊t⌋) (1025 / 4736 : ℝ) with c468 | c468
  · refine ⟨26, 16 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c467, c468]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 3840 : ℝ) with c469 | c469
  · refine ⟨21, 13 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c468, c469]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 6784 : ℝ) with c470 | c470
  · refine ⟨41, 23 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c469, c470]
  rcases lt_or_ge (t - ⌊t⌋) (641 / 2944 : ℝ) with c471 | c471
  · refine ⟨15, 10 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c470, c471]
  rcases lt_or_ge (t - ⌊t⌋) (1729 / 7936 : ℝ) with c472 | c472
  · refine ⟨49, 27 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c471, c472]
  rcases lt_or_ge (t - ⌊t⌋) (363 / 1664 : ℝ) with c473 | c473
  · refine ⟨28, 17 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c472, c473]
  rcases lt_or_ge (t - ⌊t⌋) (1537 / 7040 : ℝ) with c474 | c474
  · refine ⟨42, 24 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c473, c474]
  rcases lt_or_ge (t - ⌊t⌋) (58241 / 266240 : ℝ) with c475 | c475
  · refine ⟨56, 14 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c474, c475]
  rcases lt_or_ge (t - ⌊t⌋) (43777 / 199680 : ℝ) with c476 | c476
  · refine ⟨55, 11 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c475, c476]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 7296 : ℝ) with c477 | c477
  · refine ⟨44, 25 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c476, c477]
  rcases lt_or_ge (t - ⌊t⌋) (1153 / 5248 : ℝ) with c478 | c478
  · refine ⟨30, 18 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c477, c478]
  rcases lt_or_ge (t - ⌊t⌋) (141 / 640 : ℝ) with c479 | c479
  · refine ⟨16, 11 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c478, c479]
  rcases lt_or_ge (t - ⌊t⌋) (1665 / 7552 : ℝ) with c480 | c480
  · refine ⟨46, 26 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c479, c480]
  rcases lt_or_ge (t - ⌊t⌋) (961 / 4352 : ℝ) with c481 | c481
  · refine ⟨24, 15 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c480, c481]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 5504 : ℝ) with c482 | c482
  · refine ⟨32, 19 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c481, c482]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 6656 : ℝ) with c483 | c483
  · refine ⟨40, 23 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c482, c483]
  rcases lt_or_ge (t - ⌊t⌋) (1729 / 7808 : ℝ) with c484 | c484
  · refine ⟨48, 27 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c483, c484]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 1152 : ℝ) with c485 | c485
  · refine ⟨4, 4 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c484, c485]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 7168 : ℝ) with c486 | c486
  · refine ⟨43, 25 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c485, c486]
  rcases lt_or_ge (t - ⌊t⌋) (1345 / 6016 : ℝ) with c487 | c487
  · refine ⟨36, 21 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c486, c487]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 4864 : ℝ) with c488 | c488
  · refine ⟨27, 17 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c487, c488]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 3712 : ℝ) with c489 | c489
  · refine ⟨20, 13 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c488, c489]
  rcases lt_or_ge (t - ⌊t⌋) (1409 / 6272 : ℝ) with c490 | c490
  · refine ⟨37, 22 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c489, c490]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 2560 : ℝ) with c491 | c491
  · refine ⟨12, 9 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c490, c491]
  rcases lt_or_ge (t - ⌊t⌋) (491 / 2176 : ℝ) with c492 | c492
  · refine ⟨39, 23 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c491, c492]
  rcases lt_or_ge (t - ⌊t⌋) (897 / 3968 : ℝ) with c493 | c493
  · refine ⟨22, 14 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c492, c493]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 5376 : ℝ) with c494 | c494
  · refine ⟨31, 19 + 84 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c493, c494]
  rcases lt_or_ge (t - ⌊t⌋) (29 / 128 : ℝ) with c495 | c495
  · refine ⟨41, 24 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c494, c495]
  rcases lt_or_ge (t - ⌊t⌋) (120769 / 532480 : ℝ) with c496 | c496
  · refine ⟨57, 30 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c495, c496]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 1408 : ℝ) with c497 | c497
  · refine ⟨6, 5 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c496, c497]
  rcases lt_or_ge (t - ⌊t⌋) (555 / 2432 : ℝ) with c498 | c498
  · refine ⟨44, 26 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c497, c498]
  rcases lt_or_ge (t - ⌊t⌋) (22913 / 99840 : ℝ) with c499 | c499
  · refine ⟨53, 6 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c498, c499]
  rcases lt_or_ge (t - ⌊t⌋) (1793 / 7808 : ℝ) with c500 | c500
  · refine ⟨48, 28 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c499, c500]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 4736 : ℝ) with c501 | c501
  · refine ⟨26, 17 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c500, c501]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 6400 : ℝ) with c502 | c502
  · refine ⟨38, 23 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c501, c502]
  rcases lt_or_ge (t - ⌊t⌋) (619 / 2688 : ℝ) with c503 | c503
  · refine ⟨50, 29 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c502, c503]
  rcases lt_or_ge (t - ⌊t⌋) (385 / 1664 : ℝ) with c504 | c504
  · refine ⟨7, 6 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c503, c504]
  rcases lt_or_ge (t - ⌊t⌋) (26057 / 112320 : ℝ) with c505 | c505
  · refine ⟨61, 7 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c504, c505]
  rcases lt_or_ge (t - ⌊t⌋) (119 / 512 : ℝ) with c506 | c506
  · refine ⟨19, 13 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c505, c506]
  rcases lt_or_ge (t - ⌊t⌋) (1281 / 5504 : ℝ) with c507 | c507
  · refine ⟨32, 20 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c506, c507]
  rcases lt_or_ge (t - ⌊t⌋) (1729 / 7424 : ℝ) with c508 | c508
  · refine ⟨45, 27 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c507, c508]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 1920 : ℝ) with c509 | c509
  · refine ⟨9, 7 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c508, c509]
  rcases lt_or_ge (t - ⌊t⌋) (1857 / 7936 : ℝ) with c510 | c510
  · refine ⟨49, 29 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c509, c510]
  rcases lt_or_ge (t - ⌊t⌋) (62401 / 266240 : ℝ) with c511 | c511
  · refine ⟨56, 15 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c510, c511]
  rcases lt_or_ge (t - ⌊t⌋) (124929 / 532480 : ℝ) with c512 | c512
  · refine ⟨57, 31 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c511, c512]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 6272 : ℝ) with c513 | c513
  · refine ⟨37, 23 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c512, c513]
  rcases lt_or_ge (t - ⌊t⌋) (513 / 2176 : ℝ) with c514 | c514
  · refine ⟨10, 8 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c513, c514]
  rcases lt_or_ge (t - ⌊t⌋) (35393 / 149760 : ℝ) with c515 | c515
  · refine ⟨54, 9 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c514, c515]
  rcases lt_or_ge (t - ⌊t⌋) (333 / 1408 : ℝ) with c516 | c516
  · refine ⟨42, 26 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c515, c516]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 2432 : ℝ) with c517 | c517
  · refine ⟨11, 9 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c516, c517]
  rcases lt_or_ge (t - ⌊t⌋) (1793 / 7552 : ℝ) with c518 | c518
  · refine ⟨46, 28 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c517, c518]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 5120 : ℝ) with c519 | c519
  · refine ⟨29, 19 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c518, c519]
  rcases lt_or_ge (t - ⌊t⌋) (1857 / 7808 : ℝ) with c520 | c520
  · refine ⟨48, 29 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c519, c520]
  rcases lt_or_ge (t - ⌊t⌋) (641 / 2688 : ℝ) with c521 | c521
  · refine ⟨13, 10 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c520, c521]
  rcases lt_or_ge (t - ⌊t⌋) (1345 / 5632 : ℝ) with c522 | c522
  · refine ⟨33, 21 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c521, c522]
  rcases lt_or_ge (t - ⌊t⌋) (705 / 2944 : ℝ) with c523 | c523
  · refine ⟨15, 11 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c522, c523]
  rcases lt_or_ge (t - ⌊t⌋) (15979 / 66560 : ℝ) with c524 | c524
  · refine ⟨55, 12 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c523, c524]
  rcases lt_or_ge (t - ⌊t⌋) (769 / 3200 : ℝ) with c525 | c525
  · refine ⟨16, 12 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c524, c525]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 6656 : ℝ) with c526 | c526
  · refine ⟨40, 25 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c525, c526]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 3456 : ℝ) with c527 | c527
  · refine ⟨18, 13 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c526, c527]
  rcases lt_or_ge (t - ⌊t⌋) (247 / 1024 : ℝ) with c528 | c528
  · refine ⟨43, 27 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c527, c528]
  rcases lt_or_ge (t - ⌊t⌋) (897 / 3712 : ℝ) with c529 | c529
  · refine ⟨20, 14 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c528, c529]
  rcases lt_or_ge (t - ⌊t⌋) (619 / 2560 : ℝ) with c530 | c530
  · refine ⟨47, 29 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c529, c530]
  rcases lt_or_ge (t - ⌊t⌋) (31 / 128 : ℝ) with c531 | c531
  · refine ⟨22, 15 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c530, c531]
  rcases lt_or_ge (t - ⌊t⌋) (129089 / 532480 : ℝ) with c532 | c532
  · refine ⟨57, 32 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c531, c532]
  rcases lt_or_ge (t - ⌊t⌋) (1025 / 4224 : ℝ) with c533 | c533
  · refine ⟨23, 16 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c532, c533]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 4480 : ℝ) with c534 | c534
  · refine ⟨25, 17 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c533, c534]
  rcases lt_or_ge (t - ⌊t⌋) (1153 / 4736 : ℝ) with c535 | c535
  · refine ⟨26, 18 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c534, c535]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 4992 : ℝ) with c536 | c536
  · refine ⟨28, 19 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c535, c536]
  rcases lt_or_ge (t - ⌊t⌋) (1281 / 5248 : ℝ) with c537 | c537
  · refine ⟨30, 20 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c536, c537]
  rcases lt_or_ge (t - ⌊t⌋) (229 / 832 : ℝ) with c538 | c538
  · refine ⟨58, 1 + 1 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c537, c538]
  rcases lt_or_ge (t - ⌊t⌋) (141 / 512 : ℝ) with c539 | c539
  · refine ⟨12, 11 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c538, c539]
  rcases lt_or_ge (t - ⌊t⌋) (247 / 896 : ℝ) with c540 | c540
  · refine ⟨37, 27 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c539, c540]
  rcases lt_or_ge (t - ⌊t⌋) (1025 / 3712 : ℝ) with c541 | c541
  · refine ⟨20, 16 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c540, c541]
  rcases lt_or_ge (t - ⌊t⌋) (1345 / 4864 : ℝ) with c542 | c542
  · refine ⟨27, 21 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c541, c542]
  rcases lt_or_ge (t - ⌊t⌋) (1665 / 6016 : ℝ) with c543 | c543
  · refine ⟨36, 26 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c542, c543]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 7168 : ℝ) with c544 | c544
  · refine ⟨43, 31 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c543, c544]
  rcases lt_or_ge (t - ⌊t⌋) (107 / 384 : ℝ) with c545 | c545
  · refine ⟨4, 5 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c544, c545]
  rcases lt_or_ge (t - ⌊t⌋) (2177 / 7808 : ℝ) with c546 | c546
  · refine ⟨48, 34 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c545, c546]
  rcases lt_or_ge (t - ⌊t⌋) (1857 / 6656 : ℝ) with c547 | c547
  · refine ⟨40, 29 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c546, c547]
  rcases lt_or_ge (t - ⌊t⌋) (1537 / 5504 : ℝ) with c548 | c548
  · refine ⟨32, 24 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c547, c548]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 4352 : ℝ) with c549 | c549
  · refine ⟨24, 19 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c548, c549]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 7552 : ℝ) with c550 | c550
  · refine ⟨46, 33 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c549, c550]
  rcases lt_or_ge (t - ⌊t⌋) (897 / 3200 : ℝ) with c551 | c551
  · refine ⟨16, 14 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c550, c551]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 5248 : ℝ) with c552 | c552
  · refine ⟨30, 23 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c551, c552]
  rcases lt_or_ge (t - ⌊t⌋) (683 / 2432 : ℝ) with c553 | c553
  · refine ⟨44, 32 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c552, c553]
  rcases lt_or_ge (t - ⌊t⌋) (74881 / 266240 : ℝ) with c554 | c554
  · refine ⟨56, 18 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c553, c554]
  rcases lt_or_ge (t - ⌊t⌋) (56257 / 199680 : ℝ) with c555 | c555
  · refine ⟨55, 14 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c554, c555]
  rcases lt_or_ge (t - ⌊t⌋) (397 / 1408 : ℝ) with c556 | c556
  · refine ⟨42, 31 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c555, c556]
  rcases lt_or_ge (t - ⌊t⌋) (1409 / 4992 : ℝ) with c557 | c557
  · refine ⟨28, 22 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c556, c557]
  rcases lt_or_ge (t - ⌊t⌋) (2241 / 7936 : ℝ) with c558 | c558
  · refine ⟨49, 35 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c557, c558]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 2944 : ℝ) with c559 | c559
  · refine ⟨15, 13 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c558, c559]
  rcases lt_or_ge (t - ⌊t⌋) (1921 / 6784 : ℝ) with c560 | c560
  · refine ⟨41, 30 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c559, c560]
  rcases lt_or_ge (t - ⌊t⌋) (363 / 1280 : ℝ) with c561 | c561
  · refine ⟨21, 17 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c560, c561]
  rcases lt_or_ge (t - ⌊t⌋) (1345 / 4736 : ℝ) with c562 | c562
  · refine ⟨26, 21 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c561, c562]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 5632 : ℝ) with c563 | c563
  · refine ⟨33, 25 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c562, c563]
  rcases lt_or_ge (t - ⌊t⌋) (619 / 2176 : ℝ) with c564 | c564
  · refine ⟨39, 29 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c563, c564]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 7424 : ℝ) with c565 | c565
  · refine ⟨45, 33 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c564, c565]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 896 : ℝ) with c566 | c566
  · refine ⟨3, 4 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c565, c566]
  rcases lt_or_ge (t - ⌊t⌋) (10753 / 37440 : ℝ) with c567 | c567
  · refine ⟨62, 24 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c566, c567]
  rcases lt_or_ge (t - ⌊t⌋) (1729 / 6016 : ℝ) with c568 | c568
  · refine ⟨36, 27 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c567, c568]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 5120 : ℝ) with c569 | c569
  · refine ⟨29, 23 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c568, c569]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 4224 : ℝ) with c570 | c570
  · refine ⟨23, 19 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c569, c570]
  rcases lt_or_ge (t - ⌊t⌋) (2177 / 7552 : ℝ) with c571 | c571
  · refine ⟨46, 34 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c570, c571]
  rcases lt_or_ge (t - ⌊t⌋) (961 / 3328 : ℝ) with c572 | c572
  · refine ⟨17, 15 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c571, c572]
  rcases lt_or_ge (t - ⌊t⌋) (37 / 128 : ℝ) with c573 | c573
  · refine ⟨34, 26 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c572, c573]
  rcases lt_or_ge (t - ⌊t⌋) (154049 / 532480 : ℝ) with c574 | c574
  · refine ⟨57, 38 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c573, c574]
  rcases lt_or_ge (t - ⌊t⌋) (705 / 2432 : ℝ) with c575 | c575
  · refine ⟨11, 11 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c574, c575]
  rcases lt_or_ge (t - ⌊t⌋) (14593 / 49920 : ℝ) with c576 | c576
  · refine ⟨51, 4 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c575, c576]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 6784 : ℝ) with c577 | c577
  · refine ⟨41, 31 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c576, c577]
  rcases lt_or_ge (t - ⌊t⌋) (1537 / 5248 : ℝ) with c578 | c578
  · refine ⟨30, 24 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c577, c578]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 3712 : ℝ) with c579 | c579
  · refine ⟨20, 17 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c578, c579]
  rcases lt_or_ge (t - ⌊t⌋) (1729 / 5888 : ℝ) with c580 | c580
  · refine ⟨35, 27 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c579, c580]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 8064 : ℝ) with c581 | c581
  · refine ⟨50, 37 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c580, c581]
  rcases lt_or_ge (t - ⌊t⌋) (641 / 2176 : ℝ) with c582 | c582
  · refine ⟨10, 10 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c581, c582]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 7168 : ℝ) with c583 | c583
  · refine ⟨43, 33 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c582, c583]
  rcases lt_or_ge (t - ⌊t⌋) (491 / 1664 : ℝ) with c584 | c584
  · refine ⟨28, 23 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c583, c584]
  rcases lt_or_ge (t - ⌊t⌋) (2305 / 7808 : ℝ) with c585 | c585
  · refine ⟨48, 36 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c584, c585]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 2816 : ℝ) with c586 | c586
  · refine ⟨14, 13 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c585, c586]
  rcases lt_or_ge (t - ⌊t⌋) (1857 / 6272 : ℝ) with c587 | c587
  · refine ⟨37, 29 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c586, c587]
  rcases lt_or_ge (t - ⌊t⌋) (1025 / 3456 : ℝ) with c588 | c588
  · refine ⟨18, 16 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c587, c588]
  rcases lt_or_ge (t - ⌊t⌋) (79041 / 266240 : ℝ) with c589 | c589
  · refine ⟨56, 19 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c588, c589]
  rcases lt_or_ge (t - ⌊t⌋) (158209 / 532480 : ℝ) with c590 | c590
  · refine ⟨57, 39 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c589, c590]
  rcases lt_or_ge (t - ⌊t⌋) (1409 / 4736 : ℝ) with c591 | c591
  · refine ⟨26, 22 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c590, c591]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 5376 : ℝ) with c592 | c592
  · refine ⟨31, 25 + 84 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c591, c592]
  rcases lt_or_ge (t - ⌊t⌋) (1793 / 6016 : ℝ) with c593 | c593
  · refine ⟨36, 28 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c592, c593]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 6656 : ℝ) with c594 | c594
  · refine ⟨40, 31 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c593, c594]
  rcases lt_or_ge (t - ⌊t⌋) (2177 / 7296 : ℝ) with c595 | c595
  · refine ⟨44, 34 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c594, c595]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 7936 : ℝ) with c596 | c596
  · refine ⟨49, 37 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c595, c596]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 640 : ℝ) with c597 | c597
  · refine ⟨2, 3 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c596, c597]
  rcases lt_or_ge (t - ⌊t⌋) (811 / 2688 : ℝ) with c598 | c598
  · refine ⟨50, 38 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c597, c598]
  rcases lt_or_ge (t - ⌊t⌋) (2241 / 7424 : ℝ) with c599 | c599
  · refine ⟨45, 35 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c598, c599]
  rcases lt_or_ge (t - ⌊t⌋) (2049 / 6784 : ℝ) with c600 | c600
  · refine ⟨41, 32 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c599, c600]
  rcases lt_or_ge (t - ⌊t⌋) (20139 / 66560 : ℝ) with c601 | c601
  · refine ⟨55, 15 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c600, c601]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 4864 : ℝ) with c602 | c602
  · refine ⟨27, 23 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c601, c602]
  rcases lt_or_ge (t - ⌊t⌋) (427 / 1408 : ℝ) with c603 | c603
  · refine ⟨23, 20 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c602, c603]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 7808 : ℝ) with c604 | c604
  · refine ⟨48, 37 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c603, c604]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 3584 : ℝ) with c605 | c605
  · refine ⟨19, 17 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c604, c605]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 6528 : ℝ) with c606 | c606
  · refine ⟨39, 31 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c605, c606]
  rcases lt_or_ge (t - ⌊t⌋) (39 / 128 : ℝ) with c607 | c607
  · refine ⟨15, 14 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c606, c607]
  rcases lt_or_ge (t - ⌊t⌋) (162369 / 532480 : ℝ) with c608 | c608
  · refine ⟨57, 40 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c607, c608]
  rcases lt_or_ge (t - ⌊t⌋) (11459 / 37440 : ℝ) with c609 | c609
  · refine ⟨61, 9 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c608, c609]
  rcases lt_or_ge (t - ⌊t⌋) (1921 / 6272 : ℝ) with c610 | c610
  · refine ⟨37, 30 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c609, c610]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 3968 : ℝ) with c611 | c611
  · refine ⟨22, 19 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c610, c611]
  rcases lt_or_ge (t - ⌊t⌋) (1729 / 5632 : ℝ) with c612 | c612
  · refine ⟨33, 27 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c611, c612]
  rcases lt_or_ge (t - ⌊t⌋) (747 / 2432 : ℝ) with c613 | c613
  · refine ⟨44, 35 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c612, c613]
  rcases lt_or_ge (t - ⌊t⌋) (513 / 1664 : ℝ) with c614 | c614
  · refine ⟨7, 8 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c613, c614]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 7680 : ℝ) with c615 | c615
  · refine ⟨47, 37 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c614, c615]
  rcases lt_or_ge (t - ⌊t⌋) (1857 / 6016 : ℝ) with c616 | c616
  · refine ⟨36, 29 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c615, c616]
  rcases lt_or_ge (t - ⌊t⌋) (1345 / 4352 : ℝ) with c617 | c617
  · refine ⟨24, 21 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c616, c617]
  rcases lt_or_ge (t - ⌊t⌋) (2177 / 7040 : ℝ) with c618 | c618
  · refine ⟨42, 34 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c617, c618]
  rcases lt_or_ge (t - ⌊t⌋) (119 / 384 : ℝ) with c619 | c619
  · refine ⟨13, 13 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c618, c619]
  rcases lt_or_ge (t - ⌊t⌋) (397 / 1280 : ℝ) with c620 | c620
  · refine ⟨38, 31 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c619, c620]
  rcases lt_or_ge (t - ⌊t⌋) (1153 / 3712 : ℝ) with c621 | c621
  · refine ⟨20, 18 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c620, c621]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 4736 : ℝ) with c622 | c622
  · refine ⟨26, 23 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c621, c622]
  rcases lt_or_ge (t - ⌊t⌋) (1793 / 5760 : ℝ) with c623 | c623
  · refine ⟨34, 28 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c622, c623]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 6784 : ℝ) with c624 | c624
  · refine ⟨41, 33 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c623, c624]
  rcases lt_or_ge (t - ⌊t⌋) (2433 / 7808 : ℝ) with c625 | c625
  · refine ⟨48, 38 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c624, c625]
  rcases lt_or_ge (t - ⌊t⌋) (10411 / 33280 : ℝ) with c626 | c626
  · refine ⟨53, 8 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c625, c626]
  rcases lt_or_ge (t - ⌊t⌋) (20929 / 66560 : ℝ) with c627 | c627
  · refine ⟨52, 6 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c626, c627]
  rcases lt_or_ge (t - ⌊t⌋) (2497 / 7936 : ℝ) with c628 | c628
  · refine ⟨49, 39 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c627, c628]
  rcases lt_or_ge (t - ⌊t⌋) (121 / 384 : ℝ) with c629 | c629
  · refine ⟨18, 17 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c628, c629]
  rcases lt_or_ge (t - ⌊t⌋) (1857 / 5888 : ℝ) with c630 | c630
  · refine ⟨35, 29 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c629, c630]
  rcases lt_or_ge (t - ⌊t⌋) (769 / 2432 : ℝ) with c631 | c631
  · refine ⟨11, 12 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c630, c631]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 6272 : ℝ) with c632 | c632
  · refine ⟨37, 31 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c631, c632]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 3840 : ℝ) with c633 | c633
  · refine ⟨21, 19 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c632, c633]
  rcases lt_or_ge (t - ⌊t⌋) (1665 / 5248 : ℝ) with c634 | c634
  · refine ⟨30, 26 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c633, c634]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 6656 : ℝ) with c635 | c635
  · refine ⟨40, 33 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c634, c635]
  rcases lt_or_ge (t - ⌊t⌋) (2561 / 8064 : ℝ) with c636 | c636
  · refine ⟨50, 40 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c635, c636]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 1408 : ℝ) with c637 | c637
  · refine ⟨6, 7 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c636, c637]
  rcases lt_or_ge (t - ⌊t⌋) (47873 / 149760 : ℝ) with c638 | c638
  · refine ⟨54, 12 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c637, c638]
  rcases lt_or_ge (t - ⌊t⌋) (2497 / 7808 : ℝ) with c639 | c639
  · refine ⟨48, 39 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c638, c639]
  rcases lt_or_ge (t - ⌊t⌋) (41 / 128 : ℝ) with c640 | c640
  · refine ⟨16, 16 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c639, c640]
  rcases lt_or_ge (t - ⌊t⌋) (170689 / 532480 : ℝ) with c641 | c641
  · refine ⟨57, 42 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c640, c641]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 4992 : ℝ) with c642 | c642
  · refine ⟨28, 25 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c641, c642]
  rcases lt_or_ge (t - ⌊t⌋) (2177 / 6784 : ℝ) with c643 | c643
  · refine ⟨41, 34 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c642, c643]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 1792 : ℝ) with c644 | c644
  · refine ⟨8, 9 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c643, c644]
  rcases lt_or_ge (t - ⌊t⌋) (2433 / 7552 : ℝ) with c645 | c645
  · refine ⟨46, 38 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c644, c645]
  rcases lt_or_ge (t - ⌊t⌋) (619 / 1920 : ℝ) with c646 | c646
  · refine ⟨34, 29 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c645, c646]
  rcases lt_or_ge (t - ⌊t⌋) (1281 / 3968 : ℝ) with c647 | c647
  · refine ⟨22, 20 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c646, c647]
  rcases lt_or_ge (t - ⌊t⌋) (64577 / 199680 : ℝ) with c648 | c648
  · refine ⟨55, 16 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c647, c648]
  rcases lt_or_ge (t - ⌊t⌋) (705 / 2176 : ℝ) with c649 | c649
  · refine ⟨10, 11 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c648, c649]
  rcases lt_or_ge (t - ⌊t⌋) (36419 / 112320 : ℝ) with c650 | c650
  · refine ⟨62, 27 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c649, c650]
  rcases lt_or_ge (t - ⌊t⌋) (1537 / 4736 : ℝ) with c651 | c651
  · refine ⟨26, 24 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c650, c651]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 7296 : ℝ) with c652 | c652
  · refine ⟨44, 37 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c651, c652]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 2560 : ℝ) with c653 | c653
  · refine ⟨12, 13 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c652, c653]
  rcases lt_or_ge (t - ⌊t⌋) (125 / 384 : ℝ) with c654 | c654
  · refine ⟨50, 41 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c653, c654]
  rcases lt_or_ge (t - ⌊t⌋) (1793 / 5504 : ℝ) with c655 | c655
  · refine ⟨32, 28 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c654, c655]
  rcases lt_or_ge (t - ⌊t⌋) (961 / 2944 : ℝ) with c656 | c656
  · refine ⟨15, 15 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c655, c656]
  rcases lt_or_ge (t - ⌊t⌋) (2049 / 6272 : ℝ) with c657 | c657
  · refine ⟨37, 32 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c656, c657]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 3328 : ℝ) with c658 | c658
  · refine ⟨17, 17 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c657, c658]
  rcases lt_or_ge (t - ⌊t⌋) (461 / 1408 : ℝ) with c659 | c659
  · refine ⟨42, 36 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c658, c659]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 3712 : ℝ) with c660 | c660
  · refine ⟨20, 19 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c659, c660]
  rcases lt_or_ge (t - ⌊t⌋) (87361 / 266240 : ℝ) with c661 | c661
  · refine ⟨56, 21 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c660, c661]
  rcases lt_or_ge (t - ⌊t⌋) (174849 / 532480 : ℝ) with c662 | c662
  · refine ⟨57, 43 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c661, c662]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 4480 : ℝ) with c663 | c663
  · refine ⟨25, 23 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c662, c663]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 4864 : ℝ) with c664 | c664
  · refine ⟨27, 25 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c663, c664]
  rcases lt_or_ge (t - ⌊t⌋) (1729 / 5248 : ℝ) with c665 | c665
  · refine ⟨30, 27 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c664, c665]
  rcases lt_or_ge (t - ⌊t⌋) (1857 / 5632 : ℝ) with c666 | c666
  · refine ⟨33, 29 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c665, c666]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 6016 : ℝ) with c667 | c667
  · refine ⟨36, 31 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c666, c667]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 6400 : ℝ) with c668 | c668
  · refine ⟨38, 33 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c667, c668]
  rcases lt_or_ge (t - ⌊t⌋) (2241 / 6784 : ℝ) with c669 | c669
  · refine ⟨41, 35 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c668, c669]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 7168 : ℝ) with c670 | c670
  · refine ⟨43, 37 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c669, c670]
  rcases lt_or_ge (t - ⌊t⌋) (2497 / 7552 : ℝ) with c671 | c671
  · refine ⟨46, 39 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c670, c671]
  rcases lt_or_ge (t - ⌊t⌋) (2625 / 7936 : ℝ) with c672 | c672
  · refine ⟨49, 41 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c671, c672]
  rcases lt_or_ge (t - ⌊t⌋) (43 / 128 : ℝ) with c673 | c673
  · refine ⟨1, 2 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c672, c673]
  rcases lt_or_ge (t - ⌊t⌋) (179009 / 532480 : ℝ) with c674 | c674
  · refine ⟨57, 44 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c673, c674]
  rcases lt_or_ge (t - ⌊t⌋) (2497 / 7424 : ℝ) with c675 | c675
  · refine ⟨45, 39 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c674, c675]
  rcases lt_or_ge (t - ⌊t⌋) (113417 / 336960 : ℝ) with c676 | c676
  · refine ⟨62, 28 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c675, c676]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 6272 : ℝ) with c677 | c677
  · refine ⟨37, 33 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c676, c677]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 5888 : ℝ) with c678 | c678
  · refine ⟨35, 31 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c677, c678]
  rcases lt_or_ge (t - ⌊t⌋) (1857 / 5504 : ℝ) with c679 | c679
  · refine ⟨32, 29 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c678, c679]
  rcases lt_or_ge (t - ⌊t⌋) (1729 / 5120 : ℝ) with c680 | c680
  · refine ⟨29, 27 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c679, c680]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 4736 : ℝ) with c681 | c681
  · refine ⟨26, 25 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c680, c681]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 4352 : ℝ) with c682 | c682
  · refine ⟨24, 23 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c681, c682]
  rcases lt_or_ge (t - ⌊t⌋) (1345 / 3968 : ℝ) with c683 | c683
  · refine ⟨22, 21 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c682, c683]
  rcases lt_or_ge (t - ⌊t⌋) (2561 / 7552 : ℝ) with c684 | c684
  · refine ⟨46, 40 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c683, c684]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 3584 : ℝ) with c685 | c685
  · refine ⟨19, 19 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c684, c685]
  rcases lt_or_ge (t - ⌊t⌋) (2305 / 6784 : ℝ) with c686 | c686
  · refine ⟨41, 36 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c685, c686]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 3200 : ℝ) with c687 | c687
  · refine ⟨16, 17 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c686, c687]
  rcases lt_or_ge (t - ⌊t⌋) (2049 / 6016 : ℝ) with c688 | c688
  · refine ⟨36, 32 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c687, c688]
  rcases lt_or_ge (t - ⌊t⌋) (961 / 2816 : ℝ) with c689 | c689
  · refine ⟨14, 15 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c688, c689]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 8064 : ℝ) with c690 | c690
  · refine ⟨50, 43 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c689, c690]
  rcases lt_or_ge (t - ⌊t⌋) (1793 / 5248 : ℝ) with c691 | c691
  · refine ⟨30, 28 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c690, c691]
  rcases lt_or_ge (t - ⌊t⌋) (175 / 512 : ℝ) with c692 | c692
  · refine ⟨47, 41 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c691, c692]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 2432 : ℝ) with c693 | c693
  · refine ⟨11, 13 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c692, c693]
  rcases lt_or_ge (t - ⌊t⌋) (38537 / 112320 : ℝ) with c694 | c694
  · refine ⟨61, 10 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c693, c694]
  rcases lt_or_ge (t - ⌊t⌋) (747 / 2176 : ℝ) with c695 | c695
  · refine ⟨39, 35 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c694, c695]
  rcases lt_or_ge (t - ⌊t⌋) (91521 / 266240 : ℝ) with c696 | c696
  · refine ⟨56, 22 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c695, c696]
  rcases lt_or_ge (t - ⌊t⌋) (68737 / 199680 : ℝ) with c697 | c697
  · refine ⟨55, 17 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c696, c697]
  rcases lt_or_ge (t - ⌊t⌋) (2689 / 7808 : ℝ) with c698 | c698
  · refine ⟨48, 42 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c697, c698]
  rcases lt_or_ge (t - ⌊t⌋) (397 / 1152 : ℝ) with c699 | c699
  · refine ⟨34, 31 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c698, c699]
  rcases lt_or_ge (t - ⌊t⌋) (1281 / 3712 : ℝ) with c700 | c700
  · refine ⟨20, 20 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c699, c700]
  rcases lt_or_ge (t - ⌊t⌋) (619 / 1792 : ℝ) with c701 | c701
  · refine ⟨31, 29 + 84 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c700, c701]
  rcases lt_or_ge (t - ⌊t⌋) (2433 / 7040 : ℝ) with c702 | c702
  · refine ⟨42, 38 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c701, c702]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 1664 : ℝ) with c703 | c703
  · refine ⟨7, 9 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c702, c703]
  rcases lt_or_ge (t - ⌊t⌋) (52033 / 149760 : ℝ) with c704 | c704
  · refine ⟨54, 13 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c703, c704]
  rcases lt_or_ge (t - ⌊t⌋) (2625 / 7552 : ℝ) with c705 | c705
  · refine ⟨46, 41 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c704, c705]
  rcases lt_or_ge (t - ⌊t⌋) (1025 / 2944 : ℝ) with c706 | c706
  · refine ⟨15, 16 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c705, c706]
  rcases lt_or_ge (t - ⌊t⌋) (2497 / 7168 : ℝ) with c707 | c707
  · refine ⟨43, 39 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c706, c707]
  rcases lt_or_ge (t - ⌊t⌋) (491 / 1408 : ℝ) with c708 | c708
  · refine ⟨23, 23 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c707, c708]
  rcases lt_or_ge (t - ⌊t⌋) (1921 / 5504 : ℝ) with c709 | c709
  · refine ⟨32, 30 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c708, c709]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 6784 : ℝ) with c710 | c710
  · refine ⟨41, 37 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c709, c710]
  rcases lt_or_ge (t - ⌊t⌋) (313 / 896 : ℝ) with c711 | c711
  · refine ⟨50, 44 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c710, c711]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 1280 : ℝ) with c712 | c712
  · refine ⟨5, 7 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c711, c712]
  rcases lt_or_ge (t - ⌊t⌋) (2561 / 7296 : ℝ) with c713 | c713
  · refine ⟨44, 40 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c712, c713]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 6016 : ℝ) with c714 | c714
  · refine ⟨36, 33 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c713, c714]
  rcases lt_or_ge (t - ⌊t⌋) (45 / 128 : ℝ) with c715 | c715
  · refine ⟨26, 26 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c714, c715]
  rcases lt_or_ge (t - ⌊t⌋) (187329 / 532480 : ℝ) with c716 | c716
  · refine ⟨57, 46 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c715, c716]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 3456 : ℝ) with c717 | c717
  · refine ⟨18, 19 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c716, c717]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 5632 : ℝ) with c718 | c718
  · refine ⟨33, 31 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c717, c718]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 7808 : ℝ) with c719 | c719
  · refine ⟨48, 43 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c718, c719]
  rcases lt_or_ge (t - ⌊t⌋) (769 / 2176 : ℝ) with c720 | c720
  · refine ⟨10, 12 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c719, c720]
  rcases lt_or_ge (t - ⌊t⌋) (35393 / 99840 : ℝ) with c721 | c721
  · refine ⟨53, 9 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c720, c721]
  rcases lt_or_ge (t - ⌊t⌋) (227 / 640 : ℝ) with c722 | c722
  · refine ⟨42, 39 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c721, c722]
  rcases lt_or_ge (t - ⌊t⌋) (1409 / 3968 : ℝ) with c723 | c723
  · refine ⟨22, 22 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c722, c723]
  rcases lt_or_ge (t - ⌊t⌋) (91 / 256 : ℝ) with c724 | c724
  · refine ⟨27, 27 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c723, c724]
  rcases lt_or_ge (t - ⌊t⌋) (683 / 1920 : ℝ) with c725 | c725
  · refine ⟨34, 32 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c724, c725]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 6656 : ℝ) with c726 | c726
  · refine ⟨40, 37 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c725, c726]
  rcases lt_or_ge (t - ⌊t⌋) (2689 / 7552 : ℝ) with c727 | c727
  · refine ⟨46, 42 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c726, c727]
  rcases lt_or_ge (t - ⌊t⌋) (321 / 896 : ℝ) with c728 | c728
  · refine ⟨3, 5 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c727, c728]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 7680 : ℝ) with c729 | c729
  · refine ⟨47, 43 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c728, c729]
  rcases lt_or_ge (t - ⌊t⌋) (2433 / 6784 : ℝ) with c730 | c730
  · refine ⟨41, 38 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c729, c730]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 5888 : ℝ) with c731 | c731
  · refine ⟨35, 33 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c730, c731]
  rcases lt_or_ge (t - ⌊t⌋) (1793 / 4992 : ℝ) with c732 | c732
  · refine ⟨28, 28 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c731, c732]
  rcases lt_or_ge (t - ⌊t⌋) (95681 / 266240 : ℝ) with c733 | c733
  · refine ⟨56, 23 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c732, c733]
  rcases lt_or_ge (t - ⌊t⌋) (191489 / 532480 : ℝ) with c734 | c734
  · refine ⟨57, 47 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c733, c734]
  rcases lt_or_ge (t - ⌊t⌋) (875 / 2432 : ℝ) with c735 | c735
  · refine ⟨44, 41 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c734, c735]
  rcases lt_or_ge (t - ⌊t⌋) (1153 / 3200 : ℝ) with c736 | c736
  · refine ⟨16, 18 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c735, c736]
  rcases lt_or_ge (t - ⌊t⌋) (13601 / 37440 : ℝ) with c737 | c737
  · refine ⟨60, 4 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c736, c737]
  rcases lt_or_ge (t - ⌊t⌋) (513 / 1408 : ℝ) with c738 | c738
  · refine ⟨6, 8 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c737, c738]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 7552 : ℝ) with c739 | c739
  · refine ⟨46, 43 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c738, c739]
  rcases lt_or_ge (t - ⌊t⌋) (24299 / 66560 : ℝ) with c740 | c740
  · refine ⟨55, 18 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c739, c740]
  rcases lt_or_ge (t - ⌊t⌋) (2945 / 8064 : ℝ) with c741 | c741
  · refine ⟨50, 46 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c740, c741]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 3328 : ℝ) with c742 | c742
  · refine ⟨17, 19 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c741, c742]
  rcases lt_or_ge (t - ⌊t⌋) (1921 / 5248 : ℝ) with c743 | c743
  · refine ⟨30, 30 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c742, c743]
  rcases lt_or_ge (t - ⌊t⌋) (375 / 1024 : ℝ) with c744 | c744
  · refine ⟨43, 41 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c743, c744]
  rcases lt_or_ge (t - ⌊t⌋) (47 / 128 : ℝ) with c745 | c745
  · refine ⟨9, 11 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c744, c745]
  rcases lt_or_ge (t - ⌊t⌋) (195649 / 532480 : ℝ) with c746 | c746
  · refine ⟨57, 48 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c745, c746]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 4352 : ℝ) with c747 | c747
  · refine ⟨24, 25 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c746, c747]
  rcases lt_or_ge (t - ⌊t⌋) (2497 / 6784 : ℝ) with c748 | c748
  · refine ⟨41, 39 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c747, c748]
  rcases lt_or_ge (t - ⌊t⌋) (897 / 2432 : ℝ) with c749 | c749
  · refine ⟨11, 14 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c748, c749]
  rcases lt_or_ge (t - ⌊t⌋) (2881 / 7808 : ℝ) with c750 | c750
  · refine ⟨48, 45 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c749, c750]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 5376 : ℝ) with c751 | c751
  · refine ⟨31, 31 + 84 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c750, c751]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 2944 : ℝ) with c752 | c752
  · refine ⟨15, 17 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c751, c752]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 6400 : ℝ) with c753 | c753
  · refine ⟨38, 37 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c752, c753]
  rcases lt_or_ge (t - ⌊t⌋) (427 / 1152 : ℝ) with c754 | c754
  · refine ⟨18, 20 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c753, c754]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 7424 : ℝ) with c755 | c755
  · refine ⟨45, 43 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c754, c755]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 3968 : ℝ) with c756 | c756
  · refine ⟨22, 23 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c755, c756]
  rcases lt_or_ge (t - ⌊t⌋) (333 / 896 : ℝ) with c757 | c757
  · refine ⟨25, 26 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c756, c757]
  rcases lt_or_ge (t - ⌊t⌋) (619 / 1664 : ℝ) with c758 | c758
  · refine ⟨28, 29 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c757, c758]
  rcases lt_or_ge (t - ⌊t⌋) (2049 / 5504 : ℝ) with c759 | c759
  · refine ⟨32, 32 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c758, c759]
  rcases lt_or_ge (t - ⌊t⌋) (2241 / 6016 : ℝ) with c760 | c760
  · refine ⟨36, 35 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c759, c760]
  rcases lt_or_ge (t - ⌊t⌋) (811 / 2176 : ℝ) with c761 | c761
  · refine ⟨39, 38 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c760, c761]
  rcases lt_or_ge (t - ⌊t⌋) (525 / 1408 : ℝ) with c762 | c762
  · refine ⟨42, 41 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c761, c762]
  rcases lt_or_ge (t - ⌊t⌋) (2817 / 7552 : ℝ) with c763 | c763
  · refine ⟨46, 44 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c762, c763]
  rcases lt_or_ge (t - ⌊t⌋) (1003 / 2688 : ℝ) with c764 | c764
  · refine ⟨50, 47 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c763, c764]
  rcases lt_or_ge (t - ⌊t⌋) (6251 / 16640 : ℝ) with c765 | c765
  · refine ⟨51, 5 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c764, c765]
  rcases lt_or_ge (t - ⌊t⌋) (25089 / 66560 : ℝ) with c766 | c766
  · refine ⟨52, 7 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c765, c766]
  rcases lt_or_ge (t - ⌊t⌋) (2945 / 7808 : ℝ) with c767 | c767
  · refine ⟨48, 46 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c766, c767]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 7296 : ℝ) with c768 | c768
  · refine ⟨44, 43 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c767, c768]
  rcases lt_or_ge (t - ⌊t⌋) (2561 / 6784 : ℝ) with c769 | c769
  · refine ⟨41, 40 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c768, c769]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 6272 : ℝ) with c770 | c770
  · refine ⟨37, 37 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c769, c770]
  rcases lt_or_ge (t - ⌊t⌋) (2177 / 5760 : ℝ) with c771 | c771
  · refine ⟨34, 34 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c770, c771]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 5248 : ℝ) with c772 | c772
  · refine ⟨30, 31 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c771, c772]
  rcases lt_or_ge (t - ⌊t⌋) (1793 / 4736 : ℝ) with c773 | c773
  · refine ⟨26, 28 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c772, c773]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 4224 : ℝ) with c774 | c774
  · refine ⟨23, 25 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c773, c774]
  rcases lt_or_ge (t - ⌊t⌋) (42697 / 112320 : ℝ) with c775 | c775
  · refine ⟨61, 11 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c774, c775]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 3200 : ℝ) with c776 | c776
  · refine ⟨16, 19 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c775, c776]
  rcases lt_or_ge (t - ⌊t⌋) (2241 / 5888 : ℝ) with c777 | c777
  · refine ⟨35, 35 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c776, c777]
  rcases lt_or_ge (t - ⌊t⌋) (1025 / 2688 : ℝ) with c778 | c778
  · refine ⟨13, 16 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c777, c778]
  rcases lt_or_ge (t - ⌊t⌋) (2881 / 7552 : ℝ) with c779 | c779
  · refine ⟨46, 45 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c778, c779]
  rcases lt_or_ge (t - ⌊t⌋) (1857 / 4864 : ℝ) with c780 | c780
  · refine ⟨27, 29 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c779, c780]
  rcases lt_or_ge (t - ⌊t⌋) (2689 / 7040 : ℝ) with c781 | c781
  · refine ⟨42, 42 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c780, c781]
  rcases lt_or_ge (t - ⌊t⌋) (49 / 128 : ℝ) with c782 | c782
  · refine ⟨10, 13 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c781, c782]
  rcases lt_or_ge (t - ⌊t⌋) (203969 / 532480 : ℝ) with c783 | c783
  · refine ⟨57, 50 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c782, c783]
  rcases lt_or_ge (t - ⌊t⌋) (2305 / 6016 : ℝ) with c784 | c784
  · refine ⟨36, 36 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c783, c784]
  rcases lt_or_ge (t - ⌊t⌋) (491 / 1280 : ℝ) with c785 | c785
  · refine ⟨21, 23 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c784, c785]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 5504 : ℝ) with c786 | c786
  · refine ⟨32, 33 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c785, c786]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 7168 : ℝ) with c787 | c787
  · refine ⟨43, 43 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c786, c787]
  rcases lt_or_ge (t - ⌊t⌋) (641 / 1664 : ℝ) with c788 | c788
  · refine ⟨7, 10 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c787, c788]
  rcases lt_or_ge (t - ⌊t⌋) (3009 / 7808 : ℝ) with c789 | c789
  · refine ⟨48, 47 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c788, c789]
  rcases lt_or_ge (t - ⌊t⌋) (77057 / 199680 : ℝ) with c790 | c790
  · refine ⟨55, 19 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c789, c790]
  rcases lt_or_ge (t - ⌊t⌋) (939 / 2432 : ℝ) with c791 | c791
  · refine ⟨44, 44 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c790, c791]
  rcases lt_or_ge (t - ⌊t⌋) (99 / 256 : ℝ) with c792 | c792
  · refine ⟨14, 17 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c791, c792]
  rcases lt_or_ge (t - ⌊t⌋) (2625 / 6784 : ℝ) with c793 | c793
  · refine ⟨41, 41 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c792, c793]
  rcases lt_or_ge (t - ⌊t⌋) (1537 / 3968 : ℝ) with c794 | c794
  · refine ⟨22, 24 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c793, c794]
  rcases lt_or_ge (t - ⌊t⌋) (397 / 1024 : ℝ) with c795 | c795
  · refine ⟨29, 31 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c794, c795]
  rcases lt_or_ge (t - ⌊t⌋) (2433 / 6272 : ℝ) with c796 | c796
  · refine ⟨37, 38 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c795, c796]
  rcases lt_or_ge (t - ⌊t⌋) (2881 / 7424 : ℝ) with c797 | c797
  · refine ⟨45, 45 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c796, c797]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 1152 : ℝ) with c798 | c798
  · refine ⟨4, 7 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c797, c798]
  rcases lt_or_ge (t - ⌊t⌋) (2945 / 7552 : ℝ) with c799 | c799
  · refine ⟨46, 46 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c798, c799]
  rcases lt_or_ge (t - ⌊t⌋) (2497 / 6400 : ℝ) with c800 | c800
  · refine ⟨38, 39 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c799, c800]
  rcases lt_or_ge (t - ⌊t⌋) (104001 / 266240 : ℝ) with c801 | c801
  · refine ⟨56, 25 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c800, c801]
  rcases lt_or_ge (t - ⌊t⌋) (208129 / 532480 : ℝ) with c802 | c802
  · refine ⟨57, 51 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c801, c802]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 7040 : ℝ) with c803 | c803
  · refine ⟨42, 43 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c802, c803]
  rcases lt_or_ge (t - ⌊t⌋) (1153 / 2944 : ℝ) with c804 | c804
  · refine ⟨15, 18 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c803, c804]
  rcases lt_or_ge (t - ⌊t⌋) (1003 / 2560 : ℝ) with c805 | c805
  · refine ⟨47, 47 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c804, c805]
  rcases lt_or_ge (t - ⌊t⌋) (1857 / 4736 : ℝ) with c806 | c806
  · refine ⟨26, 29 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c805, c806]
  rcases lt_or_ge (t - ⌊t⌋) (2561 / 6528 : ℝ) with c807 | c807
  · refine ⟨39, 40 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c806, c807]
  rcases lt_or_ge (t - ⌊t⌋) (705 / 1792 : ℝ) with c808 | c808
  · refine ⟨8, 11 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c807, c808]
  rcases lt_or_ge (t - ⌊t⌋) (3073 / 7808 : ℝ) with c809 | c809
  · refine ⟨48, 48 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c808, c809]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 6016 : ℝ) with c810 | c810
  · refine ⟨36, 37 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c809, c810]
  rcases lt_or_ge (t - ⌊t⌋) (555 / 1408 : ℝ) with c811 | c811
  · refine ⟨23, 26 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c810, c811]
  rcases lt_or_ge (t - ⌊t⌋) (2625 / 6656 : ℝ) with c812 | c812
  · refine ⟨40, 41 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c811, c812]
  rcases lt_or_ge (t - ⌊t⌋) (961 / 2432 : ℝ) with c813 | c813
  · refine ⟨11, 15 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c812, c813]
  rcases lt_or_ge (t - ⌊t⌋) (39553 / 99840 : ℝ) with c814 | c814
  · refine ⟨53, 10 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c813, c814]
  rcases lt_or_ge (t - ⌊t⌋) (2689 / 6784 : ℝ) with c815 | c815
  · refine ⟨41, 42 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c814, c815]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 3712 : ℝ) with c816 | c816
  · refine ⟨20, 23 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c815, c816]
  rcases lt_or_ge (t - ⌊t⌋) (1067 / 2688 : ℝ) with c817 | c817
  · refine ⟨50, 50 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c816, c817]
  rcases lt_or_ge (t - ⌊t⌋) (1729 / 4352 : ℝ) with c818 | c818
  · refine ⟨24, 27 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c817, c818]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 4992 : ℝ) with c819 | c819
  · refine ⟨28, 31 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c818, c819]
  rcases lt_or_ge (t - ⌊t⌋) (2241 / 5632 : ℝ) with c820 | c820
  · refine ⟨33, 35 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c819, c820]
  rcases lt_or_ge (t - ⌊t⌋) (2497 / 6272 : ℝ) with c821 | c821
  · refine ⟨37, 39 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c820, c821]
  rcases lt_or_ge (t - ⌊t⌋) (1657 / 4160 : ℝ) with c822 | c822
  · refine ⟨62, 33 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c821, c822]
  rcases lt_or_ge (t - ⌊t⌋) (51 / 128 : ℝ) with c823 | c823
  · refine ⟨46, 47 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c822, c823]
  rcases lt_or_ge (t - ⌊t⌋) (212289 / 532480 : ℝ) with c824 | c824
  · refine ⟨57, 52 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c823, c824]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 640 : ℝ) with c825 | c825
  · refine ⟨2, 4 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c824, c825]
  rcases lt_or_ge (t - ⌊t⌋) (3137 / 7808 : ℝ) with c826 | c826
  · refine ⟨48, 49 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c825, c826]
  rcases lt_or_ge (t - ⌊t⌋) (2881 / 7168 : ℝ) with c827 | c827
  · refine ⟨43, 45 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c826, c827]
  rcases lt_or_ge (t - ⌊t⌋) (875 / 2176 : ℝ) with c828 | c828
  · refine ⟨39, 41 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c827, c828]
  rcases lt_or_ge (t - ⌊t⌋) (103 / 256 : ℝ) with c829 | c829
  · refine ⟨35, 37 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c828, c829]
  rcases lt_or_ge (t - ⌊t⌋) (60353 / 149760 : ℝ) with c830 | c830
  · refine ⟨54, 15 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c829, c830]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 3968 : ℝ) with c831 | c831
  · refine ⟨22, 25 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c830, c831]
  rcases lt_or_ge (t - ⌊t⌋) (155 / 384 : ℝ) with c832 | c832
  · refine ⟨44, 46 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c831, c832]
  rcases lt_or_ge (t - ⌊t⌋) (1345 / 3328 : ℝ) with c833 | c833
  · refine ⟨17, 21 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c832, c833]
  rcases lt_or_ge (t - ⌊t⌋) (2433 / 6016 : ℝ) with c834 | c834
  · refine ⟨36, 38 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c833, c834]
  rcases lt_or_ge (t - ⌊t⌋) (363 / 896 : ℝ) with c835 | c835
  · refine ⟨13, 17 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c834, c835]
  rcases lt_or_ge (t - ⌊t⌋) (3009 / 7424 : ℝ) with c836 | c836
  · refine ⟨45, 47 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c835, c836]
  rcases lt_or_ge (t - ⌊t⌋) (1921 / 4736 : ℝ) with c837 | c837
  · refine ⟨26, 30 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c836, c837]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 6784 : ℝ) with c838 | c838
  · refine ⟨41, 43 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c837, c838]
  rcases lt_or_ge (t - ⌊t⌋) (108161 / 266240 : ℝ) with c839 | c839
  · refine ⟨56, 26 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c838, c839]
  rcases lt_or_ge (t - ⌊t⌋) (81217 / 199680 : ℝ) with c840 | c840
  · refine ⟨55, 20 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c839, c840]
  rcases lt_or_ge (t - ⌊t⌋) (3073 / 7552 : ℝ) with c841 | c841
  · refine ⟨46, 48 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c840, c841]
  rcases lt_or_ge (t - ⌊t⌋) (2241 / 5504 : ℝ) with c842 | c842
  · refine ⟨32, 35 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c841, c842]
  rcases lt_or_ge (t - ⌊t⌋) (1409 / 3456 : ℝ) with c843 | c843
  · refine ⟨18, 22 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c842, c843]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 4864 : ℝ) with c844 | c844
  · refine ⟨27, 31 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c843, c844]
  rcases lt_or_ge (t - ⌊t⌋) (2561 / 6272 : ℝ) with c845 | c845
  · refine ⟨37, 40 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c844, c845]
  rcases lt_or_ge (t - ⌊t⌋) (3137 / 7680 : ℝ) with c846 | c846
  · refine ⟨47, 49 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c845, c846]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 1408 : ℝ) with c847 | c847
  · refine ⟨6, 9 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c846, c847]
  rcases lt_or_ge (t - ⌊t⌋) (3201 / 7808 : ℝ) with c848 | c848
  · refine ⟨48, 50 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c847, c848]
  rcases lt_or_ge (t - ⌊t⌋) (105 / 256 : ℝ) with c849 | c849
  · refine ⟨38, 41 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c848, c849]
  rcases lt_or_ge (t - ⌊t⌋) (683 / 1664 : ℝ) with c850 | c850
  · refine ⟨28, 32 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c849, c850]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 3584 : ℝ) with c851 | c851
  · refine ⟨19, 23 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c850, c851]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 5760 : ℝ) with c852 | c852
  · refine ⟨34, 37 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c851, c852]
  rcases lt_or_ge (t - ⌊t⌋) (3265 / 7936 : ℝ) with c853 | c853
  · refine ⟨49, 51 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c852, c853]
  rcases lt_or_ge (t - ⌊t⌋) (897 / 2176 : ℝ) with c854 | c854
  · refine ⟨10, 14 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c853, c854]
  rcases lt_or_ge (t - ⌊t⌋) (27 / 64 : ℝ) with c855 | c855
  · refine ⟨59, 2 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c854, c855]
  rcases lt_or_ge (t - ⌊t⌋) (224769 / 532480 : ℝ) with c856 | c856
  · refine ⟨57, 55 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c855, c856]
  rcases lt_or_ge (t - ⌊t⌋) (811 / 1920 : ℝ) with c857 | c857
  · refine ⟨34, 38 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c856, c857]
  rcases lt_or_ge (t - ⌊t⌋) (3137 / 7424 : ℝ) with c858 | c858
  · refine ⟨45, 49 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c857, c858]
  rcases lt_or_ge (t - ⌊t⌋) (705 / 1664 : ℝ) with c859 | c859
  · refine ⟨7, 11 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c858, c859]
  rcases lt_or_ge (t - ⌊t⌋) (3201 / 7552 : ℝ) with c860 | c860
  · refine ⟨46, 50 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c859, c860]
  rcases lt_or_ge (t - ⌊t⌋) (2497 / 5888 : ℝ) with c861 | c861
  · refine ⟨35, 39 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c860, c861]
  rcases lt_or_ge (t - ⌊t⌋) (163 / 384 : ℝ) with c862 | c862
  · refine ⟨23, 28 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c861, c862]
  rcases lt_or_ge (t - ⌊t⌋) (2881 / 6784 : ℝ) with c863 | c863
  · refine ⟨41, 45 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c862, c863]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 2560 : ℝ) with c864 | c864
  · refine ⟨12, 17 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c863, c864]
  rcases lt_or_ge (t - ⌊t⌋) (2561 / 6016 : ℝ) with c865 | c865
  · refine ⟨36, 40 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c864, c865]
  rcases lt_or_ge (t - ⌊t⌋) (491 / 1152 : ℝ) with c866 | c866
  · refine ⟨18, 23 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c865, c866]
  rcases lt_or_ge (t - ⌊t⌋) (3329 / 7808 : ℝ) with c867 | c867
  · refine ⟨48, 52 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c866, c867]
  rcases lt_or_ge (t - ⌊t⌋) (1857 / 4352 : ℝ) with c868 | c868
  · refine ⟨24, 29 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c867, c868]
  rcases lt_or_ge (t - ⌊t⌋) (2241 / 5248 : ℝ) with c869 | c869
  · refine ⟨30, 35 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c868, c869]
  rcases lt_or_ge (t - ⌊t⌋) (28459 / 66560 : ℝ) with c870 | c870
  · refine ⟨55, 21 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c869, c870]
  rcases lt_or_ge (t - ⌊t⌋) (55 / 128 : ℝ) with c871 | c871
  · refine ⟨3, 6 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c870, c871]
  rcases lt_or_ge (t - ⌊t⌋) (228929 / 532480 : ℝ) with c872 | c872
  · refine ⟨57, 56 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c871, c872]
  rcases lt_or_ge (t - ⌊t⌋) (64513 / 149760 : ℝ) with c873 | c873
  · refine ⟨54, 16 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c872, c873]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 3712 : ℝ) with c874 | c874
  · refine ⟨20, 25 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c873, c874]
  rcases lt_or_ge (t - ⌊t⌋) (939 / 2176 : ℝ) with c875 | c875
  · refine ⟨39, 44 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c874, c875]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 2816 : ℝ) with c876 | c876
  · refine ⟨14, 19 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c875, c876]
  rcases lt_or_ge (t - ⌊t⌋) (3265 / 7552 : ℝ) with c877 | c877
  · refine ⟨46, 51 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c876, c877]
  rcases lt_or_ge (t - ⌊t⌋) (2049 / 4736 : ℝ) with c878 | c878
  · refine ⟨26, 32 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c877, c878]
  rcases lt_or_ge (t - ⌊t⌋) (2881 / 6656 : ℝ) with c879 | c879
  · refine ⟨40, 45 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c878, c879]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 1920 : ℝ) with c880 | c880
  · refine ⟨9, 13 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c879, c880]
  rcases lt_or_ge (t - ⌊t⌋) (2945 / 6784 : ℝ) with c881 | c881
  · refine ⟨41, 46 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c880, c881]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 4864 : ℝ) with c882 | c882
  · refine ⟨27, 33 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c881, c882]
  rcases lt_or_ge (t - ⌊t⌋) (3393 / 7808 : ℝ) with c883 | c883
  · refine ⟨48, 53 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c882, c883]
  rcases lt_or_ge (t - ⌊t⌋) (1281 / 2944 : ℝ) with c884 | c884
  · refine ⟨15, 20 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c883, c884]
  rcases lt_or_ge (t - ⌊t⌋) (48899 / 112320 : ℝ) with c885 | c885
  · refine ⟨62, 36 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c884, c885]
  rcases lt_or_ge (t - ⌊t⌋) (1729 / 3968 : ℝ) with c886 | c886
  · refine ⟨22, 27 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c885, c886]
  rcases lt_or_ge (t - ⌊t⌋) (2177 / 4992 : ℝ) with c887 | c887
  · refine ⟨28, 34 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c886, c887]
  rcases lt_or_ge (t - ⌊t⌋) (2625 / 6016 : ℝ) with c888 | c888
  · refine ⟨36, 41 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c887, c888]
  rcases lt_or_ge (t - ⌊t⌋) (3073 / 7040 : ℝ) with c889 | c889
  · refine ⟨42, 48 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c888, c889]
  rcases lt_or_ge (t - ⌊t⌋) (503 / 1152 : ℝ) with c890 | c890
  · refine ⟨50, 55 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c889, c890]
  rcases lt_or_ge (t - ⌊t⌋) (14571 / 33280 : ℝ) with c891 | c891
  · refine ⟨53, 11 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c890, c891]
  rcases lt_or_ge (t - ⌊t⌋) (29249 / 66560 : ℝ) with c892 | c892
  · refine ⟨52, 8 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c891, c892]
  rcases lt_or_ge (t - ⌊t⌋) (619 / 1408 : ℝ) with c893 | c893
  · refine ⟨23, 29 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c892, c893]
  rcases lt_or_ge (t - ⌊t⌋) (3265 / 7424 : ℝ) with c894 | c894
  · refine ⟨45, 51 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c893, c894]
  rcases lt_or_ge (t - ⌊t⌋) (1409 / 3200 : ℝ) with c895 | c895
  · refine ⟨16, 22 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c894, c895]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 5376 : ℝ) with c896 | c896
  · refine ⟨31, 37 + 84 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c895, c896]
  rcases lt_or_ge (t - ⌊t⌋) (3329 / 7552 : ℝ) with c897 | c897
  · refine ⟨46, 52 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c896, c897]
  rcases lt_or_ge (t - ⌊t⌋) (961 / 2176 : ℝ) with c898 | c898
  · refine ⟨10, 15 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c897, c898]
  rcases lt_or_ge (t - ⌊t⌋) (1131 / 2560 : ℝ) with c899 | c899
  · refine ⟨47, 53 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c898, c899]
  rcases lt_or_ge (t - ⌊t⌋) (2433 / 5504 : ℝ) with c900 | c900
  · refine ⟨32, 38 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c899, c900]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 3328 : ℝ) with c901 | c901
  · refine ⟨17, 23 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c900, c901]
  rcases lt_or_ge (t - ⌊t⌋) (3457 / 7808 : ℝ) with c902 | c902
  · refine ⟨48, 54 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c901, c902]
  rcases lt_or_ge (t - ⌊t⌋) (397 / 896 : ℝ) with c903 | c903
  · refine ⟨25, 31 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c902, c903]
  rcases lt_or_ge (t - ⌊t⌋) (227 / 512 : ℝ) with c904 | c904
  · refine ⟨33, 39 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c903, c904]
  rcases lt_or_ge (t - ⌊t⌋) (3009 / 6784 : ℝ) with c905 | c905
  · refine ⟨41, 47 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c904, c905]
  rcases lt_or_ge (t - ⌊t⌋) (3521 / 7936 : ℝ) with c906 | c906
  · refine ⟨49, 55 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c905, c906]
  rcases lt_or_ge (t - ⌊t⌋) (57 / 128 : ℝ) with c907 | c907
  · refine ⟨4, 8 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c906, c907]
  rcases lt_or_ge (t - ⌊t⌋) (237249 / 532480 : ℝ) with c908 | c908
  · refine ⟨57, 58 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c907, c908]
  rcases lt_or_ge (t - ⌊t⌋) (2625 / 5888 : ℝ) with c909 | c909
  · refine ⟨35, 41 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c908, c909]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 4736 : ℝ) with c910 | c910
  · refine ⟨26, 33 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c909, c910]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 3584 : ℝ) with c911 | c911
  · refine ⟨19, 25 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c910, c911]
  rcases lt_or_ge (t - ⌊t⌋) (2689 / 6016 : ℝ) with c912 | c912
  · refine ⟨36, 42 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c911, c912]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 2432 : ℝ) with c913 | c913
  · refine ⟨11, 17 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c912, c913]
  rcases lt_or_ge (t - ⌊t⌋) (89537 / 199680 : ℝ) with c914 | c914
  · refine ⟨55, 22 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c913, c914]
  rcases lt_or_ge (t - ⌊t⌋) (1665 / 3712 : ℝ) with c915 | c915
  · refine ⟨20, 26 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c914, c915]
  rcases lt_or_ge (t - ⌊t⌋) (747 / 1664 : ℝ) with c916 | c916
  · refine ⟨28, 35 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c915, c916]
  rcases lt_or_ge (t - ⌊t⌋) (2817 / 6272 : ℝ) with c917 | c917
  · refine ⟨37, 44 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c916, c917]
  rcases lt_or_ge (t - ⌊t⌋) (3393 / 7552 : ℝ) with c918 | c918
  · refine ⟨46, 53 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c917, c918]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 1280 : ℝ) with c919 | c919
  · refine ⟨5, 9 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c918, c919]
  rcases lt_or_ge (t - ⌊t⌋) (3521 / 7808 : ℝ) with c920 | c920
  · refine ⟨48, 55 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c919, c920]
  rcases lt_or_ge (t - ⌊t⌋) (2945 / 6528 : ℝ) with c921 | c921
  · refine ⟨39, 46 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c920, c921]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 5248 : ℝ) with c922 | c922
  · refine ⟨30, 37 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c921, c922]
  rcases lt_or_ge (t - ⌊t⌋) (1793 / 3968 : ℝ) with c923 | c923
  · refine ⟨22, 28 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c922, c923]
  rcases lt_or_ge (t - ⌊t⌋) (3009 / 6656 : ℝ) with c924 | c924
  · refine ⟨40, 47 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c923, c924]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 2688 : ℝ) with c925 | c925
  · refine ⟨13, 19 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c924, c925]
  rcases lt_or_ge (t - ⌊t⌋) (120641 / 266240 : ℝ) with c926 | c926
  · refine ⟨56, 29 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c925, c926]
  rcases lt_or_ge (t - ⌊t⌋) (51017 / 112320 : ℝ) with c927 | c927
  · refine ⟨61, 13 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c926, c927]
  rcases lt_or_ge (t - ⌊t⌋) (641 / 1408 : ℝ) with c928 | c928
  · refine ⟨6, 10 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c927, c928]
  rcases lt_or_ge (t - ⌊t⌋) (3265 / 7168 : ℝ) with c929 | c929
  · refine ⟨43, 51 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c928, c929]
  rcases lt_or_ge (t - ⌊t⌋) (175 / 384 : ℝ) with c930 | c930
  · refine ⟨34, 41 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c929, c930]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 4352 : ℝ) with c931 | c931
  · refine ⟨24, 31 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c930, c931]
  rcases lt_or_ge (t - ⌊t⌋) (3329 / 7296 : ℝ) with c932 | c932
  · refine ⟨44, 52 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c931, c932]
  rcases lt_or_ge (t - ⌊t⌋) (1345 / 2944 : ℝ) with c933 | c933
  · refine ⟨15, 21 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c932, c933]
  rcases lt_or_ge (t - ⌊t⌋) (22913 / 49920 : ℝ) with c934 | c934
  · refine ⟨51, 6 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c933, c934]
  rcases lt_or_ge (t - ⌊t⌋) (3585 / 7808 : ℝ) with c935 | c935
  · refine ⟨48, 56 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c934, c935]
  rcases lt_or_ge (t - ⌊t⌋) (2881 / 6272 : ℝ) with c936 | c936
  · refine ⟨37, 45 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c935, c936]
  rcases lt_or_ge (t - ⌊t⌋) (2177 / 4736 : ℝ) with c937 | c937
  · refine ⟨26, 34 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c936, c937]
  rcases lt_or_ge (t - ⌊t⌋) (155017 / 336960 : ℝ) with c938 | c938
  · refine ⟨62, 38 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c937, c938]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 3200 : ℝ) with c939 | c939
  · refine ⟨16, 23 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c938, c939]
  rcases lt_or_ge (t - ⌊t⌋) (3713 / 8064 : ℝ) with c940 | c940
  · refine ⟨50, 58 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c939, c940]
  rcases lt_or_ge (t - ⌊t⌋) (2241 / 4864 : ℝ) with c941 | c941
  · refine ⟨27, 35 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c940, c941]
  rcases lt_or_ge (t - ⌊t⌋) (59 / 128 : ℝ) with c942 | c942
  · refine ⟨39, 47 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c941, c942]
  rcases lt_or_ge (t - ⌊t⌋) (245569 / 532480 : ℝ) with c943 | c943
  · refine ⟨57, 60 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c942, c943]
  rcases lt_or_ge (t - ⌊t⌋) (769 / 1664 : ℝ) with c944 | c944
  · refine ⟨7, 12 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c943, c944]
  rcases lt_or_ge (t - ⌊t⌋) (3137 / 6784 : ℝ) with c945 | c945
  · refine ⟨41, 49 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c944, c945]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 5120 : ℝ) with c946 | c946
  · refine ⟨29, 37 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c945, c946]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 3456 : ℝ) with c947 | c947
  · refine ⟨18, 25 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c946, c947]
  rcases lt_or_ge (t - ⌊t⌋) (2433 / 5248 : ℝ) with c948 | c948
  · refine ⟨30, 38 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c947, c948]
  rcases lt_or_ge (t - ⌊t⌋) (653 / 1408 : ℝ) with c949 | c949
  · refine ⟨42, 51 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c948, c949]
  rcases lt_or_ge (t - ⌊t⌋) (119 / 256 : ℝ) with c950 | c950
  · refine ⟨8, 13 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c949, c950]
  rcases lt_or_ge (t - ⌊t⌋) (1131 / 2432 : ℝ) with c951 | c951
  · refine ⟨44, 53 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c950, c951]
  rcases lt_or_ge (t - ⌊t⌋) (2561 / 5504 : ℝ) with c952 | c952
  · refine ⟨32, 40 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c951, c952]
  rcases lt_or_ge (t - ⌊t⌋) (1729 / 3712 : ℝ) with c953 | c953
  · refine ⟨20, 27 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c952, c953]
  rcases lt_or_ge (t - ⌊t⌋) (2625 / 5632 : ℝ) with c954 | c954
  · refine ⟨33, 41 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c953, c954]
  rcases lt_or_ge (t - ⌊t⌋) (3521 / 7552 : ℝ) with c955 | c955
  · refine ⟨46, 55 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c954, c955]
  rcases lt_or_ge (t - ⌊t⌋) (299 / 640 : ℝ) with c956 | c956
  · refine ⟨9, 14 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c955, c956]
  rcases lt_or_ge (t - ⌊t⌋) (3649 / 7808 : ℝ) with c957 | c957
  · refine ⟨48, 57 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c956, c957]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 5888 : ℝ) with c958 | c958
  · refine ⟨35, 43 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c957, c958]
  rcases lt_or_ge (t - ⌊t⌋) (1857 / 3968 : ℝ) with c959 | c959
  · refine ⟨22, 29 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c958, c959]
  rcases lt_or_ge (t - ⌊t⌋) (2817 / 6016 : ℝ) with c960 | c960
  · refine ⟨36, 44 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c959, c960]
  rcases lt_or_ge (t - ⌊t⌋) (1259 / 2688 : ℝ) with c961 | c961
  · refine ⟨50, 59 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c960, c961]
  rcases lt_or_ge (t - ⌊t⌋) (124801 / 266240 : ℝ) with c962 | c962
  · refine ⟨56, 30 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c961, c962]
  rcases lt_or_ge (t - ⌊t⌋) (93697 / 199680 : ℝ) with c963 | c963
  · refine ⟨55, 23 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c962, c963]
  rcases lt_or_ge (t - ⌊t⌋) (2945 / 6272 : ℝ) with c964 | c964
  · refine ⟨37, 46 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c963, c964]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 4224 : ℝ) with c965 | c965
  · refine ⟨23, 31 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c964, c965]
  rcases lt_or_ge (t - ⌊t⌋) (3009 / 6400 : ℝ) with c966 | c966
  · refine ⟨38, 47 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c965, c966]
  rcases lt_or_ge (t - ⌊t⌋) (1025 / 2176 : ℝ) with c967 | c967
  · refine ⟨10, 16 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c966, c967]
  rcases lt_or_ge (t - ⌊t⌋) (17761 / 37440 : ℝ) with c968 | c968
  · refine ⟨60, 5 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c967, c968]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 4992 : ℝ) with c969 | c969
  · refine ⟨28, 37 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c968, c969]
  rcases lt_or_ge (t - ⌊t⌋) (3585 / 7552 : ℝ) with c970 | c970
  · refine ⟨46, 56 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c969, c970]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 2560 : ℝ) with c971 | c971
  · refine ⟨12, 19 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c970, c971]
  rcases lt_or_ge (t - ⌊t⌋) (3713 / 7808 : ℝ) with c972 | c972
  · refine ⟨48, 58 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c971, c972]
  rcases lt_or_ge (t - ⌊t⌋) (2497 / 5248 : ℝ) with c973 | c973
  · refine ⟨30, 39 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c972, c973]
  rcases lt_or_ge (t - ⌊t⌋) (3777 / 7936 : ℝ) with c974 | c974
  · refine ⟨49, 59 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c973, c974]
  rcases lt_or_ge (t - ⌊t⌋) (61 / 128 : ℝ) with c975 | c975
  · refine ⟨13, 20 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c974, c975]
  rcases lt_or_ge (t - ⌊t⌋) (253889 / 532480 : ℝ) with c976 | c976
  · refine ⟨57, 62 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c975, c976]
  rcases lt_or_ge (t - ⌊t⌋) (2625 / 5504 : ℝ) with c977 | c977
  · refine ⟨32, 41 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c976, c977]
  rcases lt_or_ge (t - ⌊t⌋) (1345 / 2816 : ℝ) with c978 | c978
  · refine ⟨14, 21 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c977, c978]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 5760 : ℝ) with c979 | c979
  · refine ⟨34, 43 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c978, c979]
  rcases lt_or_ge (t - ⌊t⌋) (1409 / 2944 : ℝ) with c980 | c980
  · refine ⟨15, 22 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c979, c980]
  rcases lt_or_ge (t - ⌊t⌋) (47873 / 99840 : ℝ) with c981 | c981
  · refine ⟨53, 12 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c980, c981]
  rcases lt_or_ge (t - ⌊t⌋) (3009 / 6272 : ℝ) with c982 | c982
  · refine ⟨37, 47 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c981, c982]
  rcases lt_or_ge (t - ⌊t⌋) (1537 / 3200 : ℝ) with c983 | c983
  · refine ⟨16, 24 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c982, c983]
  rcases lt_or_ge (t - ⌊t⌋) (3137 / 6528 : ℝ) with c984 | c984
  · refine ⟨39, 49 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c983, c984]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 3328 : ℝ) with c985 | c985
  · refine ⟨17, 25 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c984, c985]
  rcases lt_or_ge (t - ⌊t⌋) (3265 / 6784 : ℝ) with c986 | c986
  · refine ⟨41, 51 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c985, c986]
  rcases lt_or_ge (t - ⌊t⌋) (185 / 384 : ℝ) with c987 | c987
  · refine ⟨18, 26 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c986, c987]
  rcases lt_or_ge (t - ⌊t⌋) (3393 / 7040 : ℝ) with c988 | c988
  · refine ⟨42, 53 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c987, c988]
  rcases lt_or_ge (t - ⌊t⌋) (247 / 512 : ℝ) with c989 | c989
  · refine ⟨19, 27 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c988, c989]
  rcases lt_or_ge (t - ⌊t⌋) (3521 / 7296 : ℝ) with c990 | c990
  · refine ⟨44, 55 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c989, c990]
  rcases lt_or_ge (t - ⌊t⌋) (1793 / 3712 : ℝ) with c991 | c991
  · refine ⟨20, 28 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c990, c991]
  rcases lt_or_ge (t - ⌊t⌋) (3649 / 7552 : ℝ) with c992 | c992
  · refine ⟨46, 57 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c991, c992]
  rcases lt_or_ge (t - ⌊t⌋) (619 / 1280 : ℝ) with c993 | c993
  · refine ⟨21, 29 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c992, c993]
  rcases lt_or_ge (t - ⌊t⌋) (3777 / 7808 : ℝ) with c994 | c994
  · refine ⟨48, 59 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c993, c994]
  rcases lt_or_ge (t - ⌊t⌋) (1921 / 3968 : ℝ) with c995 | c995
  · refine ⟨22, 30 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c994, c995]
  rcases lt_or_ge (t - ⌊t⌋) (128961 / 266240 : ℝ) with c996 | c996
  · refine ⟨56, 31 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c995, c996]
  rcases lt_or_ge (t - ⌊t⌋) (163337 / 336960 : ℝ) with c997 | c997
  · refine ⟨62, 40 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c996, c997]
  rcases lt_or_ge (t - ⌊t⌋) (683 / 1408 : ℝ) with c998 | c998
  · refine ⟨23, 32 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c997, c998]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 4352 : ℝ) with c999 | c999
  · refine ⟨24, 33 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c998, c999]
  rcases lt_or_ge (t - ⌊t⌋) (72833 / 149760 : ℝ) with c1000 | c1000
  · refine ⟨54, 18 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c999, c1000]
  rcases lt_or_ge (t - ⌊t⌋) (2305 / 4736 : ℝ) with c1001 | c1001
  · refine ⟨26, 36 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1000, c1001]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 4864 : ℝ) with c1002 | c1002
  · refine ⟨27, 37 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1001, c1002]
  rcases lt_or_ge (t - ⌊t⌋) (811 / 1664 : ℝ) with c1003 | c1003
  · refine ⟨28, 38 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1002, c1003]
  rcases lt_or_ge (t - ⌊t⌋) (2497 / 5120 : ℝ) with c1004 | c1004
  · refine ⟨29, 39 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1003, c1004]
  rcases lt_or_ge (t - ⌊t⌋) (2561 / 5248 : ℝ) with c1005 | c1005
  · refine ⟨30, 40 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1004, c1005]
  rcases lt_or_ge (t - ⌊t⌋) (125 / 256 : ℝ) with c1006 | c1006
  · refine ⟨31, 41 + 84 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1005, c1006]
  rcases lt_or_ge (t - ⌊t⌋) (2689 / 5504 : ℝ) with c1007 | c1007
  · refine ⟨32, 42 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1006, c1007]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 5632 : ℝ) with c1008 | c1008
  · refine ⟨33, 43 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1007, c1008]
  rcases lt_or_ge (t - ⌊t⌋) (313 / 640 : ℝ) with c1009 | c1009
  · refine ⟨34, 44 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1008, c1009]
  rcases lt_or_ge (t - ⌊t⌋) (2881 / 5888 : ℝ) with c1010 | c1010
  · refine ⟨35, 45 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1009, c1010]
  rcases lt_or_ge (t - ⌊t⌋) (2945 / 6016 : ℝ) with c1011 | c1011
  · refine ⟨36, 46 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1010, c1011]
  rcases lt_or_ge (t - ⌊t⌋) (32619 / 66560 : ℝ) with c1012 | c1012
  · refine ⟨55, 24 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1011, c1012]
  rcases lt_or_ge (t - ⌊t⌋) (1067 / 2176 : ℝ) with c1013 | c1013
  · refine ⟨39, 50 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1012, c1013]
  rcases lt_or_ge (t - ⌊t⌋) (55177 / 112320 : ℝ) with c1014 | c1014
  · refine ⟨61, 14 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1013, c1014]
  rcases lt_or_ge (t - ⌊t⌋) (3649 / 7424 : ℝ) with c1015 | c1015
  · refine ⟨45, 57 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1014, c1015]
  rcases lt_or_ge (t - ⌊t⌋) (3713 / 7552 : ℝ) with c1016 | c1016
  · refine ⟨46, 58 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1015, c1016]
  rcases lt_or_ge (t - ⌊t⌋) (1259 / 2560 : ℝ) with c1017 | c1017
  · refine ⟨47, 59 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1016, c1017]
  rcases lt_or_ge (t - ⌊t⌋) (3841 / 7808 : ℝ) with c1018 | c1018
  · refine ⟨48, 60 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1017, c1018]
  rcases lt_or_ge (t - ⌊t⌋) (3905 / 7936 : ℝ) with c1019 | c1019
  · refine ⟨49, 61 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1018, c1019]
  rcases lt_or_ge (t - ⌊t⌋) (63 / 128 : ℝ) with c1020 | c1020
  · refine ⟨50, 62 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1019, c1020]
  rcases lt_or_ge (t - ⌊t⌋) (262209 / 532480 : ℝ) with c1021 | c1021
  · refine ⟨57, 64 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1020, c1021]
  rcases lt_or_ge (t - ⌊t⌋) (65 / 128 : ℝ) with c1022 | c1022
  · refine ⟨0, 1 + 2 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1021, c1022]
  rcases lt_or_ge (t - ⌊t⌋) (270529 / 532480 : ℝ) with c1023 | c1023
  · refine ⟨57, 66 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1022, c1023]
  rcases lt_or_ge (t - ⌊t⌋) (4033 / 7936 : ℝ) with c1024 | c1024
  · refine ⟨49, 63 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1023, c1024]
  rcases lt_or_ge (t - ⌊t⌋) (3969 / 7808 : ℝ) with c1025 | c1025
  · refine ⟨48, 62 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1024, c1025]
  rcases lt_or_ge (t - ⌊t⌋) (781 / 1536 : ℝ) with c1026 | c1026
  · refine ⟨47, 61 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1025, c1026]
  rcases lt_or_ge (t - ⌊t⌋) (3841 / 7552 : ℝ) with c1027 | c1027
  · refine ⟨46, 60 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1026, c1027]
  rcases lt_or_ge (t - ⌊t⌋) (3777 / 7424 : ℝ) with c1028 | c1028
  · refine ⟨45, 59 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1027, c1028]
  rcases lt_or_ge (t - ⌊t⌋) (3713 / 7296 : ℝ) with c1029 | c1029
  · refine ⟨44, 58 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1028, c1029]
  rcases lt_or_ge (t - ⌊t⌋) (3649 / 7168 : ℝ) with c1030 | c1030
  · refine ⟨43, 57 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1029, c1030]
  rcases lt_or_ge (t - ⌊t⌋) (19073 / 37440 : ℝ) with c1031 | c1031
  · refine ⟨62, 42 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1030, c1031]
  rcases lt_or_ge (t - ⌊t⌋) (3457 / 6784 : ℝ) with c1032 | c1032
  · refine ⟨41, 54 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1031, c1032]
  rcases lt_or_ge (t - ⌊t⌋) (261 / 512 : ℝ) with c1033 | c1033
  · refine ⟨40, 53 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1032, c1033]
  rcases lt_or_ge (t - ⌊t⌋) (3329 / 6528 : ℝ) with c1034 | c1034
  · refine ⟨39, 52 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1033, c1034]
  rcases lt_or_ge (t - ⌊t⌋) (653 / 1280 : ℝ) with c1035 | c1035
  · refine ⟨38, 51 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1034, c1035]
  rcases lt_or_ge (t - ⌊t⌋) (3201 / 6272 : ℝ) with c1036 | c1036
  · refine ⟨37, 50 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1035, c1036]
  rcases lt_or_ge (t - ⌊t⌋) (102017 / 199680 : ℝ) with c1037 | c1037
  · refine ⟨55, 25 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1036, c1037]
  rcases lt_or_ge (t - ⌊t⌋) (3009 / 5888 : ℝ) with c1038 | c1038
  · refine ⟨35, 47 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1037, c1038]
  rcases lt_or_ge (t - ⌊t⌋) (589 / 1152 : ℝ) with c1039 | c1039
  · refine ⟨34, 46 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1038, c1039]
  rcases lt_or_ge (t - ⌊t⌋) (2881 / 5632 : ℝ) with c1040 | c1040
  · refine ⟨33, 45 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1039, c1040]
  rcases lt_or_ge (t - ⌊t⌋) (2817 / 5504 : ℝ) with c1041 | c1041
  · refine ⟨32, 44 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1040, c1041]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 5376 : ℝ) with c1042 | c1042
  · refine ⟨31, 43 + 84 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1041, c1042]
  rcases lt_or_ge (t - ⌊t⌋) (2689 / 5248 : ℝ) with c1043 | c1043
  · refine ⟨30, 42 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1042, c1043]
  rcases lt_or_ge (t - ⌊t⌋) (525 / 1024 : ℝ) with c1044 | c1044
  · refine ⟨29, 41 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1043, c1044]
  rcases lt_or_ge (t - ⌊t⌋) (197 / 384 : ℝ) with c1045 | c1045
  · refine ⟨28, 40 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1044, c1045]
  rcases lt_or_ge (t - ⌊t⌋) (2497 / 4864 : ℝ) with c1046 | c1046
  · refine ⟨27, 39 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1045, c1046]
  rcases lt_or_ge (t - ⌊t⌋) (76993 / 149760 : ℝ) with c1047 | c1047
  · refine ⟨54, 19 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1046, c1047]
  rcases lt_or_ge (t - ⌊t⌋) (461 / 896 : ℝ) with c1048 | c1048
  · refine ⟨25, 36 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1047, c1048]
  rcases lt_or_ge (t - ⌊t⌋) (2241 / 4352 : ℝ) with c1049 | c1049
  · refine ⟨24, 35 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1048, c1049]
  rcases lt_or_ge (t - ⌊t⌋) (2177 / 4224 : ℝ) with c1050 | c1050
  · refine ⟨23, 34 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1049, c1050]
  rcases lt_or_ge (t - ⌊t⌋) (137281 / 266240 : ℝ) with c1051 | c1051
  · refine ⟨56, 33 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1050, c1051]
  rcases lt_or_ge (t - ⌊t⌋) (274689 / 532480 : ℝ) with c1052 | c1052
  · refine ⟨57, 67 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1051, c1052]
  rcases lt_or_ge (t - ⌊t⌋) (1387 / 2688 : ℝ) with c1053 | c1053
  · refine ⟨50, 65 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1052, c1053]
  rcases lt_or_ge (t - ⌊t⌋) (2049 / 3968 : ℝ) with c1054 | c1054
  · refine ⟨22, 32 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1053, c1054]
  rcases lt_or_ge (t - ⌊t⌋) (4033 / 7808 : ℝ) with c1055 | c1055
  · refine ⟨48, 63 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1054, c1055]
  rcases lt_or_ge (t - ⌊t⌋) (397 / 768 : ℝ) with c1056 | c1056
  · refine ⟨21, 31 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1055, c1056]
  rcases lt_or_ge (t - ⌊t⌋) (3905 / 7552 : ℝ) with c1057 | c1057
  · refine ⟨46, 61 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1056, c1057]
  rcases lt_or_ge (t - ⌊t⌋) (1921 / 3712 : ℝ) with c1058 | c1058
  · refine ⟨20, 30 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1057, c1058]
  rcases lt_or_ge (t - ⌊t⌋) (1259 / 2432 : ℝ) with c1059 | c1059
  · refine ⟨44, 59 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1058, c1059]
  rcases lt_or_ge (t - ⌊t⌋) (1857 / 3584 : ℝ) with c1060 | c1060
  · refine ⟨19, 29 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1059, c1060]
  rcases lt_or_ge (t - ⌊t⌋) (3649 / 7040 : ℝ) with c1061 | c1061
  · refine ⟨42, 57 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1060, c1061]
  rcases lt_or_ge (t - ⌊t⌋) (1793 / 3456 : ℝ) with c1062 | c1062
  · refine ⟨18, 28 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1061, c1062]
  rcases lt_or_ge (t - ⌊t⌋) (3521 / 6784 : ℝ) with c1063 | c1063
  · refine ⟨41, 55 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1062, c1063]
  rcases lt_or_ge (t - ⌊t⌋) (133 / 256 : ℝ) with c1064 | c1064
  · refine ⟨17, 27 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1063, c1064]
  rcases lt_or_ge (t - ⌊t⌋) (1131 / 2176 : ℝ) with c1065 | c1065
  · refine ⟨39, 53 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1064, c1065]
  rcases lt_or_ge (t - ⌊t⌋) (333 / 640 : ℝ) with c1066 | c1066
  · refine ⟨16, 26 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1065, c1066]
  rcases lt_or_ge (t - ⌊t⌋) (52033 / 99840 : ℝ) with c1067 | c1067
  · refine ⟨53, 13 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1066, c1067]
  rcases lt_or_ge (t - ⌊t⌋) (3137 / 6016 : ℝ) with c1068 | c1068
  · refine ⟨36, 49 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1067, c1068]
  rcases lt_or_ge (t - ⌊t⌋) (1537 / 2944 : ℝ) with c1069 | c1069
  · refine ⟨15, 24 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1068, c1069]
  rcases lt_or_ge (t - ⌊t⌋) (1003 / 1920 : ℝ) with c1070 | c1070
  · refine ⟨34, 47 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1069, c1070]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 2816 : ℝ) with c1071 | c1071
  · refine ⟨14, 23 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1070, c1071]
  rcases lt_or_ge (t - ⌊t⌋) (67 / 128 : ℝ) with c1072 | c1072
  · refine ⟨32, 45 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1071, c1072]
  rcases lt_or_ge (t - ⌊t⌋) (278849 / 532480 : ℝ) with c1073 | c1073
  · refine ⟨57, 68 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1072, c1073]
  rcases lt_or_ge (t - ⌊t⌋) (1409 / 2688 : ℝ) with c1074 | c1074
  · refine ⟨13, 22 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1073, c1074]
  rcases lt_or_ge (t - ⌊t⌋) (4161 / 7936 : ℝ) with c1075 | c1075
  · refine ⟨49, 65 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1074, c1075]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 5248 : ℝ) with c1076 | c1076
  · refine ⟨30, 43 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1075, c1076]
  rcases lt_or_ge (t - ⌊t⌋) (4097 / 7808 : ℝ) with c1077 | c1077
  · refine ⟨48, 64 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1076, c1077]
  rcases lt_or_ge (t - ⌊t⌋) (269 / 512 : ℝ) with c1078 | c1078
  · refine ⟨12, 21 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1077, c1078]
  rcases lt_or_ge (t - ⌊t⌋) (3969 / 7552 : ℝ) with c1079 | c1079
  · refine ⟨46, 62 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1078, c1079]
  rcases lt_or_ge (t - ⌊t⌋) (875 / 1664 : ℝ) with c1080 | c1080
  · refine ⟨28, 41 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1079, c1080]
  rcases lt_or_ge (t - ⌊t⌋) (3905 / 7424 : ℝ) with c1081 | c1081
  · refine ⟨45, 61 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1080, c1081]
  rcases lt_or_ge (t - ⌊t⌋) (1281 / 2432 : ℝ) with c1082 | c1082
  · refine ⟨11, 20 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1081, c1082]
  rcases lt_or_ge (t - ⌊t⌋) (3777 / 7168 : ℝ) with c1083 | c1083
  · refine ⟨43, 59 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1082, c1083]
  rcases lt_or_ge (t - ⌊t⌋) (2497 / 4736 : ℝ) with c1084 | c1084
  · refine ⟨26, 39 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1083, c1084]
  rcases lt_or_ge (t - ⌊t⌋) (6593 / 12480 : ℝ) with c1085 | c1085
  · refine ⟨61, 15 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1084, c1085]
  rcases lt_or_ge (t - ⌊t⌋) (3585 / 6784 : ℝ) with c1086 | c1086
  · refine ⟨41, 56 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1085, c1086]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 4480 : ℝ) with c1087 | c1087
  · refine ⟨25, 37 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1086, c1087]
  rcases lt_or_ge (t - ⌊t⌋) (3521 / 6656 : ℝ) with c1088 | c1088
  · refine ⟨40, 55 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1087, c1088]
  rcases lt_or_ge (t - ⌊t⌋) (1153 / 2176 : ℝ) with c1089 | c1089
  · refine ⟨10, 18 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1088, c1089]
  rcases lt_or_ge (t - ⌊t⌋) (3393 / 6400 : ℝ) with c1090 | c1090
  · refine ⟨38, 53 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1089, c1090]
  rcases lt_or_ge (t - ⌊t⌋) (747 / 1408 : ℝ) with c1091 | c1091
  · refine ⟨23, 35 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1090, c1091]
  rcases lt_or_ge (t - ⌊t⌋) (3329 / 6272 : ℝ) with c1092 | c1092
  · refine ⟨37, 52 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1091, c1092]
  rcases lt_or_ge (t - ⌊t⌋) (141441 / 266240 : ℝ) with c1093 | c1093
  · refine ⟨56, 34 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1092, c1093]
  rcases lt_or_ge (t - ⌊t⌋) (106177 / 199680 : ℝ) with c1094 | c1094
  · refine ⟨55, 26 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1093, c1094]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 8064 : ℝ) with c1095 | c1095
  · refine ⟨50, 67 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1094, c1095]
  rcases lt_or_ge (t - ⌊t⌋) (3201 / 6016 : ℝ) with c1096 | c1096
  · refine ⟨36, 50 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1095, c1096]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 3968 : ℝ) with c1097 | c1097
  · refine ⟨22, 33 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1096, c1097]
  rcases lt_or_ge (t - ⌊t⌋) (3137 / 5888 : ℝ) with c1098 | c1098
  · refine ⟨35, 49 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1097, c1098]
  rcases lt_or_ge (t - ⌊t⌋) (4161 / 7808 : ℝ) with c1099 | c1099
  · refine ⟨48, 65 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1098, c1099]
  rcases lt_or_ge (t - ⌊t⌋) (205 / 384 : ℝ) with c1100 | c1100
  · refine ⟨9, 16 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1099, c1100]
  rcases lt_or_ge (t - ⌊t⌋) (179977 / 336960 : ℝ) with c1101 | c1101
  · refine ⟨62, 44 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1100, c1101]
  rcases lt_or_ge (t - ⌊t⌋) (3009 / 5632 : ℝ) with c1102 | c1102
  · refine ⟨33, 47 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1101, c1102]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 3712 : ℝ) with c1103 | c1103
  · refine ⟨20, 31 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1102, c1103]
  rcases lt_or_ge (t - ⌊t⌋) (2945 / 5504 : ℝ) with c1104 | c1104
  · refine ⟨32, 46 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1103, c1104]
  rcases lt_or_ge (t - ⌊t⌋) (3905 / 7296 : ℝ) with c1105 | c1105
  · refine ⟨44, 61 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1104, c1105]
  rcases lt_or_ge (t - ⌊t⌋) (961 / 1792 : ℝ) with c1106 | c1106
  · refine ⟨8, 15 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1105, c1106]
  rcases lt_or_ge (t - ⌊t⌋) (3777 / 7040 : ℝ) with c1107 | c1107
  · refine ⟨42, 59 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1106, c1107]
  rcases lt_or_ge (t - ⌊t⌋) (2817 / 5248 : ℝ) with c1108 | c1108
  · refine ⟨30, 44 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1107, c1108]
  rcases lt_or_ge (t - ⌊t⌋) (619 / 1152 : ℝ) with c1109 | c1109
  · refine ⟨18, 29 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1108, c1109]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 5120 : ℝ) with c1110 | c1110
  · refine ⟨29, 43 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1109, c1110]
  rcases lt_or_ge (t - ⌊t⌋) (3649 / 6784 : ℝ) with c1111 | c1111
  · refine ⟨41, 57 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1110, c1111]
  rcases lt_or_ge (t - ⌊t⌋) (69 / 128 : ℝ) with c1112 | c1112
  · refine ⟨7, 14 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1111, c1112]
  rcases lt_or_ge (t - ⌊t⌋) (287169 / 532480 : ℝ) with c1113 | c1113
  · refine ⟨57, 70 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1112, c1113]
  rcases lt_or_ge (t - ⌊t⌋) (2625 / 4864 : ℝ) with c1114 | c1114
  · refine ⟨27, 41 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1113, c1114]
  rcases lt_or_ge (t - ⌊t⌋) (1451 / 2688 : ℝ) with c1115 | c1115
  · refine ⟨50, 68 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1114, c1115]
  rcases lt_or_ge (t - ⌊t⌋) (27073 / 49920 : ℝ) with c1116 | c1116
  · refine ⟨51, 7 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1115, c1116]
  rcases lt_or_ge (t - ⌊t⌋) (4097 / 7552 : ℝ) with c1117 | c1117
  · refine ⟨46, 64 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1116, c1117]
  rcases lt_or_ge (t - ⌊t⌋) (3265 / 6016 : ℝ) with c1118 | c1118
  · refine ⟨36, 51 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1117, c1118]
  rcases lt_or_ge (t - ⌊t⌋) (2433 / 4480 : ℝ) with c1119 | c1119
  · refine ⟨25, 38 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1118, c1119]
  rcases lt_or_ge (t - ⌊t⌋) (4033 / 7424 : ℝ) with c1120 | c1120
  · refine ⟨45, 63 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1119, c1120]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 2944 : ℝ) with c1121 | c1121
  · refine ⟨15, 25 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1120, c1121]
  rcases lt_or_ge (t - ⌊t⌋) (1323 / 2432 : ℝ) with c1122 | c1122
  · refine ⟨44, 62 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1121, c1122]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 4352 : ℝ) with c1123 | c1123
  · refine ⟨24, 37 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1122, c1123]
  rcases lt_or_ge (t - ⌊t⌋) (3137 / 5760 : ℝ) with c1124 | c1124
  · refine ⟨34, 49 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1123, c1124]
  rcases lt_or_ge (t - ⌊t⌋) (3905 / 7168 : ℝ) with c1125 | c1125
  · refine ⟨43, 61 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1124, c1125]
  rcases lt_or_ge (t - ⌊t⌋) (769 / 1408 : ℝ) with c1126 | c1126
  · refine ⟨6, 12 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1125, c1126]
  rcases lt_or_ge (t - ⌊t⌋) (61379 / 112320 : ℝ) with c1127 | c1127
  · refine ⟨62, 45 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1126, c1127]
  rcases lt_or_ge (t - ⌊t⌋) (145601 / 266240 : ℝ) with c1128 | c1128
  · refine ⟨56, 35 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1127, c1128]
  rcases lt_or_ge (t - ⌊t⌋) (291329 / 532480 : ℝ) with c1129 | c1129
  · refine ⟨57, 71 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1128, c1129]
  rcases lt_or_ge (t - ⌊t⌋) (3713 / 6784 : ℝ) with c1130 | c1130
  · refine ⟨41, 58 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1129, c1130]
  rcases lt_or_ge (t - ⌊t⌋) (491 / 896 : ℝ) with c1131 | c1131
  · refine ⟨13, 23 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1130, c1131]
  rcases lt_or_ge (t - ⌊t⌋) (3649 / 6656 : ℝ) with c1132 | c1132
  · refine ⟨40, 57 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1131, c1132]
  rcases lt_or_ge (t - ⌊t⌋) (2177 / 3968 : ℝ) with c1133 | c1133
  · refine ⟨22, 34 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1132, c1133]
  rcases lt_or_ge (t - ⌊t⌋) (2881 / 5248 : ℝ) with c1134 | c1134
  · refine ⟨30, 45 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1133, c1134]
  rcases lt_or_ge (t - ⌊t⌋) (1195 / 2176 : ℝ) with c1135 | c1135
  · refine ⟨39, 56 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1134, c1135]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 7808 : ℝ) with c1136 | c1136
  · refine ⟨48, 67 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1135, c1136]
  rcases lt_or_ge (t - ⌊t⌋) (141 / 256 : ℝ) with c1137 | c1137
  · refine ⟨5, 11 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1136, c1137]
  rcases lt_or_ge (t - ⌊t⌋) (4161 / 7552 : ℝ) with c1138 | c1138
  · refine ⟨46, 65 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1137, c1138]
  rcases lt_or_ge (t - ⌊t⌋) (3457 / 6272 : ℝ) with c1139 | c1139
  · refine ⟨37, 54 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1138, c1139]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 4992 : ℝ) with c1140 | c1140
  · refine ⟨28, 43 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1139, c1140]
  rcases lt_or_ge (t - ⌊t⌋) (2049 / 3712 : ℝ) with c1141 | c1141
  · refine ⟨20, 32 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1140, c1141]
  rcases lt_or_ge (t - ⌊t⌋) (36779 / 66560 : ℝ) with c1142 | c1142
  · refine ⟨55, 27 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1141, c1142]
  rcases lt_or_ge (t - ⌊t⌋) (1345 / 2432 : ℝ) with c1143 | c1143
  · refine ⟨11, 21 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1142, c1143]
  rcases lt_or_ge (t - ⌊t⌋) (3329 / 6016 : ℝ) with c1144 | c1144
  · refine ⟨36, 52 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1143, c1144]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 3584 : ℝ) with c1145 | c1145
  · refine ⟨19, 31 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1144, c1145]
  rcases lt_or_ge (t - ⌊t⌋) (2625 / 4736 : ℝ) with c1146 | c1146
  · refine ⟨26, 41 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1145, c1146]
  rcases lt_or_ge (t - ⌊t⌋) (3265 / 5888 : ℝ) with c1147 | c1147
  · refine ⟨35, 51 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1146, c1147]
  rcases lt_or_ge (t - ⌊t⌋) (71 / 128 : ℝ) with c1148 | c1148
  · refine ⟨42, 61 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1147, c1148]
  rcases lt_or_ge (t - ⌊t⌋) (295489 / 532480 : ℝ) with c1149 | c1149
  · refine ⟨57, 72 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1148, c1149]
  rcases lt_or_ge (t - ⌊t⌋) (641 / 1152 : ℝ) with c1150 | c1150
  · refine ⟨4, 10 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1149, c1150]
  rcases lt_or_ge (t - ⌊t⌋) (4417 / 7936 : ℝ) with c1151 | c1151
  · refine ⟨49, 69 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1150, c1151]
  rcases lt_or_ge (t - ⌊t⌋) (3777 / 6784 : ℝ) with c1152 | c1152
  · refine ⟨41, 59 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1151, c1152]
  rcases lt_or_ge (t - ⌊t⌋) (3137 / 5632 : ℝ) with c1153 | c1153
  · refine ⟨33, 49 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1152, c1153]
  rcases lt_or_ge (t - ⌊t⌋) (2497 / 4480 : ℝ) with c1154 | c1154
  · refine ⟨25, 39 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1153, c1154]
  rcases lt_or_ge (t - ⌊t⌋) (4353 / 7808 : ℝ) with c1155 | c1155
  · refine ⟨48, 68 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1154, c1155]
  rcases lt_or_ge (t - ⌊t⌋) (1857 / 3328 : ℝ) with c1156 | c1156
  · refine ⟨17, 29 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1155, c1156]
  rcases lt_or_ge (t - ⌊t⌋) (3073 / 5504 : ℝ) with c1157 | c1157
  · refine ⟨32, 48 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1156, c1157]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 7680 : ℝ) with c1158 | c1158
  · refine ⟨47, 67 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1157, c1158]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 2176 : ℝ) with c1159 | c1159
  · refine ⟨10, 19 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1158, c1159]
  rcases lt_or_ge (t - ⌊t⌋) (4225 / 7552 : ℝ) with c1160 | c1160
  · refine ⟨46, 66 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1159, c1160]
  rcases lt_or_ge (t - ⌊t⌋) (1003 / 1792 : ℝ) with c1161 | c1161
  · refine ⟨31, 47 + 84 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1160, c1161]
  rcases lt_or_ge (t - ⌊t⌋) (1793 / 3200 : ℝ) with c1162 | c1162
  · refine ⟨16, 28 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1161, c1162]
  rcases lt_or_ge (t - ⌊t⌋) (4161 / 7424 : ℝ) with c1163 | c1163
  · refine ⟨45, 65 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1162, c1163]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 4224 : ℝ) with c1164 | c1164
  · refine ⟨23, 37 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1163, c1164]
  rcases lt_or_ge (t - ⌊t⌋) (2945 / 5248 : ℝ) with c1165 | c1165
  · refine ⟨30, 46 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1164, c1165]
  rcases lt_or_ge (t - ⌊t⌋) (503 / 896 : ℝ) with c1166 | c1166
  · refine ⟨37, 55 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1165, c1166]
  rcases lt_or_ge (t - ⌊t⌋) (4097 / 7296 : ℝ) with c1167 | c1167
  · refine ⟨44, 64 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1166, c1167]
  rcases lt_or_ge (t - ⌊t⌋) (18731 / 33280 : ℝ) with c1168 | c1168
  · refine ⟨53, 14 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1167, c1168]
  rcases lt_or_ge (t - ⌊t⌋) (37569 / 66560 : ℝ) with c1169 | c1169
  · refine ⟨52, 10 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1168, c1169]
  rcases lt_or_ge (t - ⌊t⌋) (63497 / 112320 : ℝ) with c1170 | c1170
  · refine ⟨61, 16 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1169, c1170]
  rcases lt_or_ge (t - ⌊t⌋) (1665 / 2944 : ℝ) with c1171 | c1171
  · refine ⟨15, 26 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1170, c1171]
  rcases lt_or_ge (t - ⌊t⌋) (4417 / 7808 : ℝ) with c1172 | c1172
  · refine ⟨48, 69 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1171, c1172]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 4864 : ℝ) with c1173 | c1173
  · refine ⟨27, 43 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1172, c1173]
  rcases lt_or_ge (t - ⌊t⌋) (3841 / 6784 : ℝ) with c1174 | c1174
  · refine ⟨41, 60 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1173, c1174]
  rcases lt_or_ge (t - ⌊t⌋) (363 / 640 : ℝ) with c1175 | c1175
  · refine ⟨9, 17 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1174, c1175]
  rcases lt_or_ge (t - ⌊t⌋) (3777 / 6656 : ℝ) with c1176 | c1176
  · refine ⟨40, 59 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1175, c1176]
  rcases lt_or_ge (t - ⌊t⌋) (2689 / 4736 : ℝ) with c1177 | c1177
  · refine ⟨26, 42 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1176, c1177]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 7552 : ℝ) with c1178 | c1178
  · refine ⟨46, 67 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1177, c1178]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 2816 : ℝ) with c1179 | c1179
  · refine ⟨14, 25 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1178, c1179]
  rcases lt_or_ge (t - ⌊t⌋) (3713 / 6528 : ℝ) with c1180 | c1180
  · refine ⟨39, 58 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1179, c1180]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 3712 : ℝ) with c1181 | c1181
  · refine ⟨20, 33 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1180, c1181]
  rcases lt_or_ge (t - ⌊t⌋) (85313 / 149760 : ℝ) with c1182 | c1182
  · refine ⟨54, 21 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1181, c1182]
  rcases lt_or_ge (t - ⌊t⌋) (3137 / 5504 : ℝ) with c1183 | c1183
  · refine ⟨32, 49 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1182, c1183]
  rcases lt_or_ge (t - ⌊t⌋) (3649 / 6400 : ℝ) with c1184 | c1184
  · refine ⟨38, 57 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1183, c1184]
  rcases lt_or_ge (t - ⌊t⌋) (73 / 128 : ℝ) with c1185 | c1185
  · refine ⟨44, 65 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1184, c1185]
  rcases lt_or_ge (t - ⌊t⌋) (303809 / 532480 : ℝ) with c1186 | c1186
  · refine ⟨57, 74 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1185, c1186]
  rcases lt_or_ge (t - ⌊t⌋) (513 / 896 : ℝ) with c1187 | c1187
  · refine ⟨3, 8 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1186, c1187]
  rcases lt_or_ge (t - ⌊t⌋) (4545 / 7936 : ℝ) with c1188 | c1188
  · refine ⟨49, 71 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1187, c1188]
  rcases lt_or_ge (t - ⌊t⌋) (4033 / 7040 : ℝ) with c1189 | c1189
  · refine ⟨42, 63 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1188, c1189]
  rcases lt_or_ge (t - ⌊t⌋) (114497 / 199680 : ℝ) with c1190 | c1190
  · refine ⟨55, 28 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1189, c1190]
  rcases lt_or_ge (t - ⌊t⌋) (2497 / 4352 : ℝ) with c1191 | c1191
  · refine ⟨24, 39 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1190, c1191]
  rcases lt_or_ge (t - ⌊t⌋) (4481 / 7808 : ℝ) with c1192 | c1192
  · refine ⟨48, 70 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1191, c1192]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 3456 : ℝ) with c1193 | c1193
  · refine ⟨18, 31 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1192, c1193]
  rcases lt_or_ge (t - ⌊t⌋) (3457 / 6016 : ℝ) with c1194 | c1194
  · refine ⟨36, 54 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1193, c1194]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 2560 : ℝ) with c1195 | c1195
  · refine ⟨12, 23 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1194, c1195]
  rcases lt_or_ge (t - ⌊t⌋) (3905 / 6784 : ℝ) with c1196 | c1196
  · refine ⟨41, 61 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1195, c1196]
  rcases lt_or_ge (t - ⌊t⌋) (811 / 1408 : ℝ) with c1197 | c1197
  · refine ⟨23, 38 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1196, c1197]
  rcases lt_or_ge (t - ⌊t⌋) (3393 / 5888 : ℝ) with c1198 | c1198
  · refine ⟨35, 53 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1197, c1198]
  rcases lt_or_ge (t - ⌊t⌋) (4353 / 7552 : ℝ) with c1199 | c1199
  · refine ⟨46, 68 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1198, c1199]
  rcases lt_or_ge (t - ⌊t⌋) (961 / 1664 : ℝ) with c1200 | c1200
  · refine ⟨7, 15 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1199, c1200]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 7424 : ℝ) with c1201 | c1201
  · refine ⟨45, 67 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1200, c1201]
  rcases lt_or_ge (t - ⌊t⌋) (153921 / 266240 : ℝ) with c1202 | c1202
  · refine ⟨56, 37 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1201, c1202]
  rcases lt_or_ge (t - ⌊t⌋) (307969 / 532480 : ℝ) with c1203 | c1203
  · refine ⟨57, 75 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1202, c1203]
  rcases lt_or_ge (t - ⌊t⌋) (1259 / 2176 : ℝ) with c1204 | c1204
  · refine ⟨39, 59 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1203, c1204]
  rcases lt_or_ge (t - ⌊t⌋) (1409 / 2432 : ℝ) with c1205 | c1205
  · refine ⟨11, 22 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1204, c1205]
  rcases lt_or_ge (t - ⌊t⌋) (4673 / 8064 : ℝ) with c1206 | c1206
  · refine ⟨50, 73 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1205, c1206]
  rcases lt_or_ge (t - ⌊t⌋) (3265 / 5632 : ℝ) with c1207 | c1207
  · refine ⟨33, 51 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1206, c1207]
  rcases lt_or_ge (t - ⌊t⌋) (1857 / 3200 : ℝ) with c1208 | c1208
  · refine ⟨16, 29 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1207, c1208]
  rcases lt_or_ge (t - ⌊t⌋) (4161 / 7168 : ℝ) with c1209 | c1209
  · refine ⟨43, 65 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1208, c1209]
  rcases lt_or_ge (t - ⌊t⌋) (2305 / 3968 : ℝ) with c1210 | c1210
  · refine ⟨22, 36 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1209, c1210]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 4736 : ℝ) with c1211 | c1211
  · refine ⟨26, 43 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1210, c1211]
  rcases lt_or_ge (t - ⌊t⌋) (3201 / 5504 : ℝ) with c1212 | c1212
  · refine ⟨32, 50 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1211, c1212]
  rcases lt_or_ge (t - ⌊t⌋) (3649 / 6272 : ℝ) with c1213 | c1213
  · refine ⟨37, 57 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1212, c1213]
  rcases lt_or_ge (t - ⌊t⌋) (4097 / 7040 : ℝ) with c1214 | c1214
  · refine ⟨42, 64 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1213, c1214]
  rcases lt_or_ge (t - ⌊t⌋) (4545 / 7808 : ℝ) with c1215 | c1215
  · refine ⟨48, 71 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1214, c1215]
  rcases lt_or_ge (t - ⌊t⌋) (7307 / 12480 : ℝ) with c1216 | c1216
  · refine ⟨60, 6 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1215, c1216]
  rcases lt_or_ge (t - ⌊t⌋) (75 / 128 : ℝ) with c1217 | c1217
  · refine ⟨25, 41 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1216, c1217]
  rcases lt_or_ge (t - ⌊t⌋) (312129 / 532480 : ℝ) with c1218 | c1218
  · refine ⟨57, 76 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1217, c1218]
  rcases lt_or_ge (t - ⌊t⌋) (2177 / 3712 : ℝ) with c1219 | c1219
  · refine ⟨20, 34 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1218, c1219]
  rcases lt_or_ge (t - ⌊t⌋) (3905 / 6656 : ℝ) with c1220 | c1220
  · refine ⟨40, 61 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1219, c1220]
  rcases lt_or_ge (t - ⌊t⌋) (1729 / 2944 : ℝ) with c1221 | c1221
  · refine ⟨15, 27 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1220, c1221]
  rcases lt_or_ge (t - ⌊t⌋) (1579 / 2688 : ℝ) with c1222 | c1222
  · refine ⟨50, 74 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1221, c1222]
  rcases lt_or_ge (t - ⌊t⌋) (3009 / 5120 : ℝ) with c1223 | c1223
  · refine ⟨29, 47 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1222, c1223]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 7296 : ℝ) with c1224 | c1224
  · refine ⟨44, 67 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1223, c1224]
  rcases lt_or_ge (t - ⌊t⌋) (1281 / 2176 : ℝ) with c1225 | c1225
  · refine ⟨10, 20 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1224, c1225]
  rcases lt_or_ge (t - ⌊t⌋) (4673 / 7936 : ℝ) with c1226 | c1226
  · refine ⟨49, 73 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1225, c1226]
  rcases lt_or_ge (t - ⌊t⌋) (377 / 640 : ℝ) with c1227 | c1227
  · refine ⟨34, 53 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1226, c1227]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 3584 : ℝ) with c1228 | c1228
  · refine ⟨19, 33 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1227, c1228]
  rcases lt_or_ge (t - ⌊t⌋) (2945 / 4992 : ℝ) with c1229 | c1229
  · refine ⟨28, 46 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1228, c1229]
  rcases lt_or_ge (t - ⌊t⌋) (3777 / 6400 : ℝ) with c1230 | c1230
  · refine ⟨38, 59 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1229, c1230]
  rcases lt_or_ge (t - ⌊t⌋) (4609 / 7808 : ℝ) with c1231 | c1231
  · refine ⟨48, 72 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1230, c1231]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 1408 : ℝ) with c1232 | c1232
  · refine ⟨6, 13 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1231, c1232]
  rcases lt_or_ge (t - ⌊t⌋) (303 / 512 : ℝ) with c1233 | c1233
  · refine ⟨47, 71 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1232, c1233]
  rcases lt_or_ge (t - ⌊t⌋) (3713 / 6272 : ℝ) with c1234 | c1234
  · refine ⟨37, 58 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1233, c1234]
  rcases lt_or_ge (t - ⌊t⌋) (2881 / 4864 : ℝ) with c1235 | c1235
  · refine ⟨27, 45 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1234, c1235]
  rcases lt_or_ge (t - ⌊t⌋) (683 / 1152 : ℝ) with c1236 | c1236
  · refine ⟨18, 32 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1235, c1236]
  rcases lt_or_ge (t - ⌊t⌋) (3265 / 5504 : ℝ) with c1237 | c1237
  · refine ⟨32, 51 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1236, c1237]
  rcases lt_or_ge (t - ⌊t⌋) (4481 / 7552 : ℝ) with c1238 | c1238
  · refine ⟨46, 70 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1237, c1238]
  rcases lt_or_ge (t - ⌊t⌋) (158081 / 266240 : ℝ) with c1239 | c1239
  · refine ⟨56, 38 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1238, c1239]
  rcases lt_or_ge (t - ⌊t⌋) (118657 / 199680 : ℝ) with c1240 | c1240
  · refine ⟨55, 29 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1239, c1240]
  rcases lt_or_ge (t - ⌊t⌋) (4033 / 6784 : ℝ) with c1241 | c1241
  · refine ⟨41, 63 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1240, c1241]
  rcases lt_or_ge (t - ⌊t⌋) (2817 / 4736 : ℝ) with c1242 | c1242
  · refine ⟨26, 44 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1241, c1242]
  rcases lt_or_ge (t - ⌊t⌋) (4417 / 7424 : ℝ) with c1243 | c1243
  · refine ⟨45, 69 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1242, c1243]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 2688 : ℝ) with c1244 | c1244
  · refine ⟨13, 25 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1243, c1244]
  rcases lt_or_ge (t - ⌊t⌋) (3585 / 6016 : ℝ) with c1245 | c1245
  · refine ⟨36, 56 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1244, c1245]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 3328 : ℝ) with c1246 | c1246
  · refine ⟨17, 31 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1245, c1246]
  rcases lt_or_ge (t - ⌊t⌋) (1451 / 2432 : ℝ) with c1247 | c1247
  · refine ⟨44, 68 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1246, c1247]
  rcases lt_or_ge (t - ⌊t⌋) (89473 / 149760 : ℝ) with c1248 | c1248
  · refine ⟨54, 22 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1247, c1248]
  rcases lt_or_ge (t - ⌊t⌋) (3137 / 5248 : ℝ) with c1249 | c1249
  · refine ⟨30, 49 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1248, c1249]
  rcases lt_or_ge (t - ⌊t⌋) (3521 / 5888 : ℝ) with c1250 | c1250
  · refine ⟨35, 55 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1249, c1250]
  rcases lt_or_ge (t - ⌊t⌋) (3905 / 6528 : ℝ) with c1251 | c1251
  · refine ⟨39, 61 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1250, c1251]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 7168 : ℝ) with c1252 | c1252
  · refine ⟨43, 67 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1251, c1252]
  rcases lt_or_ge (t - ⌊t⌋) (4673 / 7808 : ℝ) with c1253 | c1253
  · refine ⟨48, 73 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1252, c1253]
  rcases lt_or_ge (t - ⌊t⌋) (77 / 128 : ℝ) with c1254 | c1254
  · refine ⟨2, 6 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1253, c1254]
  rcases lt_or_ge (t - ⌊t⌋) (67657 / 112320 : ℝ) with c1255 | c1255
  · refine ⟨61, 17 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1254, c1255]
  rcases lt_or_ge (t - ⌊t⌋) (3393 / 5632 : ℝ) with c1256 | c1256
  · refine ⟨33, 53 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1255, c1256]
  rcases lt_or_ge (t - ⌊t⌋) (1003 / 1664 : ℝ) with c1257 | c1257
  · refine ⟨28, 47 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1256, c1257]
  rcases lt_or_ge (t - ⌊t⌋) (2625 / 4352 : ℝ) with c1258 | c1258
  · refine ⟨24, 41 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1257, c1258]
  rcases lt_or_ge (t - ⌊t⌋) (695 / 1152 : ℝ) with c1259 | c1259
  · refine ⟨50, 76 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1258, c1259]
  rcases lt_or_ge (t - ⌊t⌋) (60353 / 99840 : ℝ) with c1260 | c1260
  · refine ⟨53, 15 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1259, c1260]
  rcases lt_or_ge (t - ⌊t⌋) (3329 / 5504 : ℝ) with c1261 | c1261
  · refine ⟨32, 52 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1260, c1261]
  rcases lt_or_ge (t - ⌊t⌋) (4801 / 7936 : ℝ) with c1262 | c1262
  · refine ⟨49, 75 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1261, c1262]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 2432 : ℝ) with c1263 | c1263
  · refine ⟨11, 23 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1262, c1263]
  rcases lt_or_ge (t - ⌊t⌋) (4033 / 6656 : ℝ) with c1264 | c1264
  · refine ⟨40, 63 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1263, c1264]
  rcases lt_or_ge (t - ⌊t⌋) (2561 / 4224 : ℝ) with c1265 | c1265
  · refine ⟨23, 40 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1264, c1265]
  rcases lt_or_ge (t - ⌊t⌋) (3649 / 6016 : ℝ) with c1266 | c1266
  · refine ⟨36, 57 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1265, c1266]
  rcases lt_or_ge (t - ⌊t⌋) (4737 / 7808 : ℝ) with c1267 | c1267
  · refine ⟨48, 74 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1266, c1267]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 1792 : ℝ) with c1268 | c1268
  · refine ⟨8, 17 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1267, c1268]
  rcases lt_or_ge (t - ⌊t⌋) (1323 / 2176 : ℝ) with c1269 | c1269
  · refine ⟨39, 62 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1268, c1269]
  rcases lt_or_ge (t - ⌊t⌋) (2881 / 4736 : ℝ) with c1270 | c1270
  · refine ⟨26, 45 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1269, c1270]
  rcases lt_or_ge (t - ⌊t⌋) (4673 / 7680 : ℝ) with c1271 | c1271
  · refine ⟨47, 73 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1270, c1271]
  rcases lt_or_ge (t - ⌊t⌋) (1793 / 2944 : ℝ) with c1272 | c1272
  · refine ⟨15, 28 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1271, c1272]
  rcases lt_or_ge (t - ⌊t⌋) (162241 / 266240 : ℝ) with c1273 | c1273
  · refine ⟨56, 39 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1272, c1273]
  rcases lt_or_ge (t - ⌊t⌋) (324609 / 532480 : ℝ) with c1274 | c1274
  · refine ⟨57, 79 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1273, c1274]
  rcases lt_or_ge (t - ⌊t⌋) (3201 / 5248 : ℝ) with c1275 | c1275
  · refine ⟨30, 50 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1274, c1275]
  rcases lt_or_ge (t - ⌊t⌋) (781 / 1280 : ℝ) with c1276 | c1276
  · refine ⟨38, 61 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1275, c1276]
  rcases lt_or_ge (t - ⌊t⌋) (4609 / 7552 : ℝ) with c1277 | c1277
  · refine ⟨46, 72 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1276, c1277]
  rcases lt_or_ge (t - ⌊t⌋) (235 / 384 : ℝ) with c1278 | c1278
  · refine ⟨4, 11 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1277, c1278]
  rcases lt_or_ge (t - ⌊t⌋) (4545 / 7424 : ℝ) with c1279 | c1279
  · refine ⟨45, 71 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1278, c1279]
  rcases lt_or_ge (t - ⌊t⌋) (3841 / 6272 : ℝ) with c1280 | c1280
  · refine ⟨37, 60 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1279, c1280]
  rcases lt_or_ge (t - ⌊t⌋) (3137 / 5120 : ℝ) with c1281 | c1281
  · refine ⟨29, 49 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1280, c1281]
  rcases lt_or_ge (t - ⌊t⌋) (2433 / 3968 : ℝ) with c1282 | c1282
  · refine ⟨22, 38 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1281, c1282]
  rcases lt_or_ge (t - ⌊t⌋) (4161 / 6784 : ℝ) with c1283 | c1283
  · refine ⟨41, 65 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1282, c1283]
  rcases lt_or_ge (t - ⌊t⌋) (1729 / 2816 : ℝ) with c1284 | c1284
  · refine ⟨14, 27 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1283, c1284]
  rcases lt_or_ge (t - ⌊t⌋) (4481 / 7296 : ℝ) with c1285 | c1285
  · refine ⟨44, 70 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1284, c1285]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 4480 : ℝ) with c1286 | c1286
  · refine ⟨25, 43 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1285, c1286]
  rcases lt_or_ge (t - ⌊t⌋) (40939 / 66560 : ℝ) with c1287 | c1287
  · refine ⟨55, 30 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1286, c1287]
  rcases lt_or_ge (t - ⌊t⌋) (1025 / 1664 : ℝ) with c1288 | c1288
  · refine ⟨7, 16 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1287, c1288]
  rcases lt_or_ge (t - ⌊t⌋) (631 / 1024 : ℝ) with c1289 | c1289
  · refine ⟨43, 69 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1288, c1289]
  rcases lt_or_ge (t - ⌊t⌋) (3393 / 5504 : ℝ) with c1290 | c1290
  · refine ⟨32, 53 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1289, c1290]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 3840 : ℝ) with c1291 | c1291
  · refine ⟨21, 37 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1290, c1291]
  rcases lt_or_ge (t - ⌊t⌋) (79 / 128 : ℝ) with c1292 | c1292
  · refine ⟨36, 58 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1291, c1292]
  rcases lt_or_ge (t - ⌊t⌋) (328769 / 532480 : ℝ) with c1293 | c1293
  · refine ⟨57, 80 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1292, c1293]
  rcases lt_or_ge (t - ⌊t⌋) (1345 / 2176 : ℝ) with c1294 | c1294
  · refine ⟨10, 21 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1293, c1294]
  rcases lt_or_ge (t - ⌊t⌋) (4353 / 7040 : ℝ) with c1295 | c1295
  · refine ⟨42, 68 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1294, c1295]
  rcases lt_or_ge (t - ⌊t⌋) (3009 / 4864 : ℝ) with c1296 | c1296
  · refine ⟨27, 47 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1295, c1296]
  rcases lt_or_ge (t - ⌊t⌋) (4673 / 7552 : ℝ) with c1297 | c1297
  · refine ⟨46, 73 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1296, c1297]
  rcases lt_or_ge (t - ⌊t⌋) (555 / 896 : ℝ) with c1298 | c1298
  · refine ⟨13, 26 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1297, c1298]
  rcases lt_or_ge (t - ⌊t⌋) (3649 / 5888 : ℝ) with c1299 | c1299
  · refine ⟨35, 57 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1298, c1299]
  rcases lt_or_ge (t - ⌊t⌋) (397 / 640 : ℝ) with c1300 | c1300
  · refine ⟨16, 31 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1299, c1300]
  rcases lt_or_ge (t - ⌊t⌋) (23233 / 37440 : ℝ) with c1301 | c1301
  · refine ⟨62, 51 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1300, c1301]
  rcases lt_or_ge (t - ⌊t⌋) (2305 / 3712 : ℝ) with c1302 | c1302
  · refine ⟨20, 36 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1301, c1302]
  rcases lt_or_ge (t - ⌊t⌋) (159 / 256 : ℝ) with c1303 | c1303
  · refine ⟨49, 77 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1302, c1303]
  rcases lt_or_ge (t - ⌊t⌋) (875 / 1408 : ℝ) with c1304 | c1304
  · refine ⟨23, 41 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1303, c1304]
  rcases lt_or_ge (t - ⌊t⌋) (2945 / 4736 : ℝ) with c1305 | c1305
  · refine ⟨26, 46 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1304, c1305]
  rcases lt_or_ge (t - ⌊t⌋) (3265 / 5248 : ℝ) with c1306 | c1306
  · refine ⟨30, 51 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1305, c1306]
  rcases lt_or_ge (t - ⌊t⌋) (239 / 384 : ℝ) with c1307 | c1307
  · refine ⟨34, 56 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1306, c1307]
  rcases lt_or_ge (t - ⌊t⌋) (3905 / 6272 : ℝ) with c1308 | c1308
  · refine ⟨37, 61 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1307, c1308]
  rcases lt_or_ge (t - ⌊t⌋) (4225 / 6784 : ℝ) with c1309 | c1309
  · refine ⟨41, 66 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1308, c1309]
  rcases lt_or_ge (t - ⌊t⌋) (1515 / 2432 : ℝ) with c1310 | c1310
  · refine ⟨44, 71 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1309, c1310]
  rcases lt_or_ge (t - ⌊t⌋) (4865 / 7808 : ℝ) with c1311 | c1311
  · refine ⟨48, 76 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1310, c1311]
  rcases lt_or_ge (t - ⌊t⌋) (10411 / 16640 : ℝ) with c1312 | c1312
  · refine ⟨51, 8 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1311, c1312]
  rcases lt_or_ge (t - ⌊t⌋) (41729 / 66560 : ℝ) with c1313 | c1313
  · refine ⟨52, 11 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1312, c1313]
  rcases lt_or_ge (t - ⌊t⌋) (5057 / 8064 : ℝ) with c1314 | c1314
  · refine ⟨50, 79 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1313, c1314]
  rcases lt_or_ge (t - ⌊t⌋) (4737 / 7552 : ℝ) with c1315 | c1315
  · refine ⟨46, 74 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1314, c1315]
  rcases lt_or_ge (t - ⌊t⌋) (4417 / 7040 : ℝ) with c1316 | c1316
  · refine ⟨42, 69 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1315, c1316]
  rcases lt_or_ge (t - ⌊t⌋) (241 / 384 : ℝ) with c1317 | c1317
  · refine ⟨39, 64 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1316, c1317]
  rcases lt_or_ge (t - ⌊t⌋) (3777 / 6016 : ℝ) with c1318 | c1318
  · refine ⟨36, 59 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1317, c1318]
  rcases lt_or_ge (t - ⌊t⌋) (3457 / 5504 : ℝ) with c1319 | c1319
  · refine ⟨32, 54 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1318, c1319]
  rcases lt_or_ge (t - ⌊t⌋) (3137 / 4992 : ℝ) with c1320 | c1320
  · refine ⟨28, 49 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1319, c1320]
  rcases lt_or_ge (t - ⌊t⌋) (2817 / 4480 : ℝ) with c1321 | c1321
  · refine ⟨25, 44 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1320, c1321]
  rcases lt_or_ge (t - ⌊t⌋) (2497 / 3968 : ℝ) with c1322 | c1322
  · refine ⟨22, 39 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1321, c1322]
  rcases lt_or_ge (t - ⌊t⌋) (4673 / 7424 : ℝ) with c1323 | c1323
  · refine ⟨45, 73 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1322, c1323]
  rcases lt_or_ge (t - ⌊t⌋) (2177 / 3456 : ℝ) with c1324 | c1324
  · refine ⟨18, 34 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1323, c1324]
  rcases lt_or_ge (t - ⌊t⌋) (4033 / 6400 : ℝ) with c1325 | c1325
  · refine ⟨38, 63 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1324, c1325]
  rcases lt_or_ge (t - ⌊t⌋) (1857 / 2944 : ℝ) with c1326 | c1326
  · refine ⟨15, 29 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1325, c1326]
  rcases lt_or_ge (t - ⌊t⌋) (1131 / 1792 : ℝ) with c1327 | c1327
  · refine ⟨31, 53 + 84 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1326, c1327]
  rcases lt_or_ge (t - ⌊t⌋) (4929 / 7808 : ℝ) with c1328 | c1328
  · refine ⟨48, 77 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1327, c1328]
  rcases lt_or_ge (t - ⌊t⌋) (1537 / 2432 : ℝ) with c1329 | c1329
  · refine ⟨11, 24 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1328, c1329]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 6784 : ℝ) with c1330 | c1330
  · refine ⟨41, 67 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1329, c1330]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 4352 : ℝ) with c1331 | c1331
  · refine ⟨24, 43 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1330, c1331]
  rcases lt_or_ge (t - ⌊t⌋) (213257 / 336960 : ℝ) with c1332 | c1332
  · refine ⟨62, 52 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1331, c1332]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 1920 : ℝ) with c1333 | c1333
  · refine ⟨9, 19 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1332, c1333]
  rcases lt_or_ge (t - ⌊t⌋) (4545 / 7168 : ℝ) with c1334 | c1334
  · refine ⟨43, 71 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1333, c1334]
  rcases lt_or_ge (t - ⌊t⌋) (3329 / 5248 : ℝ) with c1335 | c1335
  · refine ⟨30, 52 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1334, c1335]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 3328 : ℝ) with c1336 | c1336
  · refine ⟨17, 33 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1335, c1336]
  rcases lt_or_ge (t - ⌊t⌋) (569 / 896 : ℝ) with c1337 | c1337
  · refine ⟨50, 80 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1336, c1337]
  rcases lt_or_ge (t - ⌊t⌋) (3009 / 4736 : ℝ) with c1338 | c1338
  · refine ⟨26, 47 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1337, c1338]
  rcases lt_or_ge (t - ⌊t⌋) (126977 / 199680 : ℝ) with c1339 | c1339
  · refine ⟨55, 31 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1338, c1339]
  rcases lt_or_ge (t - ⌊t⌋) (897 / 1408 : ℝ) with c1340 | c1340
  · refine ⟨6, 14 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1339, c1340]
  rcases lt_or_ge (t - ⌊t⌋) (5057 / 7936 : ℝ) with c1341 | c1341
  · refine ⟨49, 79 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1340, c1341]
  rcases lt_or_ge (t - ⌊t⌋) (1387 / 2176 : ℝ) with c1342 | c1342
  · refine ⟨39, 65 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1341, c1342]
  rcases lt_or_ge (t - ⌊t⌋) (653 / 1024 : ℝ) with c1343 | c1343
  · refine ⟨29, 51 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1342, c1343]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 3712 : ℝ) with c1344 | c1344
  · refine ⟨20, 37 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1343, c1344]
  rcases lt_or_ge (t - ⌊t⌋) (3841 / 6016 : ℝ) with c1345 | c1345
  · refine ⟨36, 60 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1344, c1345]
  rcases lt_or_ge (t - ⌊t⌋) (23939 / 37440 : ℝ) with c1346 | c1346
  · refine ⟨61, 18 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1345, c1346]
  rcases lt_or_ge (t - ⌊t⌋) (3521 / 5504 : ℝ) with c1347 | c1347
  · refine ⟨32, 55 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1346, c1347]
  rcases lt_or_ge (t - ⌊t⌋) (2049 / 3200 : ℝ) with c1348 | c1348
  · refine ⟨16, 32 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1347, c1348]
  rcases lt_or_ge (t - ⌊t⌋) (170561 / 266240 : ℝ) with c1349 | c1349
  · refine ⟨56, 41 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1348, c1349]
  rcases lt_or_ge (t - ⌊t⌋) (341249 / 532480 : ℝ) with c1350 | c1350
  · refine ⟨57, 83 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1349, c1350]
  rcases lt_or_ge (t - ⌊t⌋) (1067 / 1664 : ℝ) with c1351 | c1351
  · refine ⟨28, 50 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1350, c1351]
  rcases lt_or_ge (t - ⌊t⌋) (3777 / 5888 : ℝ) with c1352 | c1352
  · refine ⟨35, 59 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1351, c1352]
  rcases lt_or_ge (t - ⌊t⌋) (4353 / 6784 : ℝ) with c1353 | c1353
  · refine ⟨41, 68 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1352, c1353]
  rcases lt_or_ge (t - ⌊t⌋) (1643 / 2560 : ℝ) with c1354 | c1354
  · refine ⟨47, 77 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1353, c1354]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 896 : ℝ) with c1355 | c1355
  · refine ⟨3, 9 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1354, c1355]
  rcases lt_or_ge (t - ⌊t⌋) (4865 / 7552 : ℝ) with c1356 | c1356
  · refine ⟨46, 76 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1355, c1356]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 6656 : ℝ) with c1357 | c1357
  · refine ⟨40, 67 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1356, c1357]
  rcases lt_or_ge (t - ⌊t⌋) (3713 / 5760 : ℝ) with c1358 | c1358
  · refine ⟨34, 58 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1357, c1358]
  rcases lt_or_ge (t - ⌊t⌋) (3137 / 4864 : ℝ) with c1359 | c1359
  · refine ⟨27, 49 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1358, c1359]
  rcases lt_or_ge (t - ⌊t⌋) (64513 / 99840 : ℝ) with c1360 | c1360
  · refine ⟨53, 16 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1359, c1360]
  rcases lt_or_ge (t - ⌊t⌋) (3393 / 5248 : ℝ) with c1361 | c1361
  · refine ⟨30, 53 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1360, c1361]
  rcases lt_or_ge (t - ⌊t⌋) (4801 / 7424 : ℝ) with c1362 | c1362
  · refine ⟨45, 75 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1361, c1362]
  rcases lt_or_ge (t - ⌊t⌋) (1409 / 2176 : ℝ) with c1363 | c1363
  · refine ⟨10, 22 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1362, c1363]
  rcases lt_or_ge (t - ⌊t⌋) (5057 / 7808 : ℝ) with c1364 | c1364
  · refine ⟨48, 79 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1363, c1364]
  rcases lt_or_ge (t - ⌊t⌋) (3649 / 5632 : ℝ) with c1365 | c1365
  · refine ⟨33, 57 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1364, c1365]
  rcases lt_or_ge (t - ⌊t⌋) (83 / 128 : ℝ) with c1366 | c1366
  · refine ⟨18, 35 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1365, c1366]
  rcases lt_or_ge (t - ⌊t⌋) (345409 / 532480 : ℝ) with c1367 | c1367
  · refine ⟨57, 84 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1366, c1367]
  rcases lt_or_ge (t - ⌊t⌋) (3073 / 4736 : ℝ) with c1368 | c1368
  · refine ⟨26, 48 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1367, c1368]
  rcases lt_or_ge (t - ⌊t⌋) (3905 / 6016 : ℝ) with c1369 | c1369
  · refine ⟨36, 61 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1368, c1369]
  rcases lt_or_ge (t - ⌊t⌋) (1579 / 2432 : ℝ) with c1370 | c1370
  · refine ⟨44, 74 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1369, c1370]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 1280 : ℝ) with c1371 | c1371
  · refine ⟨5, 13 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1370, c1371]
  rcases lt_or_ge (t - ⌊t⌋) (5249 / 8064 : ℝ) with c1372 | c1372
  · refine ⟨50, 82 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1371, c1372]
  rcases lt_or_ge (t - ⌊t⌋) (4417 / 6784 : ℝ) with c1373 | c1373
  · refine ⟨41, 69 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1372, c1373]
  rcases lt_or_ge (t - ⌊t⌋) (3585 / 5504 : ℝ) with c1374 | c1374
  · refine ⟨32, 56 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1373, c1374]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 4224 : ℝ) with c1375 | c1375
  · refine ⟨23, 43 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1374, c1375]
  rcases lt_or_ge (t - ⌊t⌋) (4673 / 7168 : ℝ) with c1376 | c1376
  · refine ⟨43, 73 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1375, c1376]
  rcases lt_or_ge (t - ⌊t⌋) (1921 / 2944 : ℝ) with c1377 | c1377
  · refine ⟨15, 30 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1376, c1377]
  rcases lt_or_ge (t - ⌊t⌋) (97793 / 149760 : ℝ) with c1378 | c1378
  · refine ⟨54, 24 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1377, c1378]
  rcases lt_or_ge (t - ⌊t⌋) (4097 / 6272 : ℝ) with c1379 | c1379
  · refine ⟨37, 64 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1378, c1379]
  rcases lt_or_ge (t - ⌊t⌋) (5185 / 7936 : ℝ) with c1380 | c1380
  · refine ⟨49, 81 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1379, c1380]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 1664 : ℝ) with c1381 | c1381
  · refine ⟨7, 17 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1380, c1381]
  rcases lt_or_ge (t - ⌊t⌋) (419 / 640 : ℝ) with c1382 | c1382
  · refine ⟨42, 72 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1381, c1382]
  rcases lt_or_ge (t - ⌊t⌋) (503 / 768 : ℝ) with c1383 | c1383
  · refine ⟨31, 55 + 84 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1382, c1383]
  rcases lt_or_ge (t - ⌊t⌋) (2433 / 3712 : ℝ) with c1384 | c1384
  · refine ⟨20, 38 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1383, c1384]
  rcases lt_or_ge (t - ⌊t⌋) (1259 / 1920 : ℝ) with c1385 | c1385
  · refine ⟨34, 59 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1384, c1385]
  rcases lt_or_ge (t - ⌊t⌋) (5121 / 7808 : ℝ) with c1386 | c1386
  · refine ⟨48, 80 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1385, c1386]
  rcases lt_or_ge (t - ⌊t⌋) (174721 / 266240 : ℝ) with c1387 | c1387
  · refine ⟨56, 42 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1386, c1387]
  rcases lt_or_ge (t - ⌊t⌋) (131137 / 199680 : ℝ) with c1388 | c1388
  · refine ⟨55, 32 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1387, c1388]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 6528 : ℝ) with c1389 | c1389
  · refine ⟨39, 67 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1388, c1389]
  rcases lt_or_ge (t - ⌊t⌋) (589 / 896 : ℝ) with c1390 | c1390
  · refine ⟨25, 46 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1389, c1390]
  rcases lt_or_ge (t - ⌊t⌋) (73859 / 112320 : ℝ) with c1391 | c1391
  · refine ⟨62, 54 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1390, c1391]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 2432 : ℝ) with c1392 | c1392
  · refine ⟨11, 25 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1391, c1392]
  rcases lt_or_ge (t - ⌊t⌋) (5057 / 7680 : ℝ) with c1393 | c1393
  · refine ⟨47, 79 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1392, c1393]
  rcases lt_or_ge (t - ⌊t⌋) (3457 / 5248 : ℝ) with c1394 | c1394
  · refine ⟨30, 54 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1393, c1394]
  rcases lt_or_ge (t - ⌊t⌋) (253 / 384 : ℝ) with c1395 | c1395
  · refine ⟨50, 83 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1394, c1395]
  rcases lt_or_ge (t - ⌊t⌋) (1857 / 2816 : ℝ) with c1396 | c1396
  · refine ⟨14, 29 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1395, c1396]
  rcases lt_or_ge (t - ⌊t⌋) (3969 / 6016 : ℝ) with c1397 | c1397
  · refine ⟨36, 62 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1396, c1397]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 3200 : ℝ) with c1398 | c1398
  · refine ⟨16, 33 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1397, c1398]
  rcases lt_or_ge (t - ⌊t⌋) (4481 / 6784 : ℝ) with c1399 | c1399
  · refine ⟨41, 70 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1398, c1399]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 3584 : ℝ) with c1400 | c1400
  · refine ⟨19, 37 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1399, c1400]
  rcases lt_or_ge (t - ⌊t⌋) (4993 / 7552 : ℝ) with c1401 | c1401
  · refine ⟨46, 78 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1400, c1401]
  rcases lt_or_ge (t - ⌊t⌋) (2625 / 3968 : ℝ) with c1402 | c1402
  · refine ⟨22, 41 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1401, c1402]
  rcases lt_or_ge (t - ⌊t⌋) (2881 / 4352 : ℝ) with c1403 | c1403
  · refine ⟨24, 45 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1402, c1403]
  rcases lt_or_ge (t - ⌊t⌋) (3137 / 4736 : ℝ) with c1404 | c1404
  · refine ⟨26, 49 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1403, c1404]
  rcases lt_or_ge (t - ⌊t⌋) (3393 / 5120 : ℝ) with c1405 | c1405
  · refine ⟨29, 53 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1404, c1405]
  rcases lt_or_ge (t - ⌊t⌋) (3649 / 5504 : ℝ) with c1406 | c1406
  · refine ⟨32, 57 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1405, c1406]
  rcases lt_or_ge (t - ⌊t⌋) (3905 / 5888 : ℝ) with c1407 | c1407
  · refine ⟨35, 61 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1406, c1407]
  rcases lt_or_ge (t - ⌊t⌋) (4161 / 6272 : ℝ) with c1408 | c1408
  · refine ⟨37, 65 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1407, c1408]
  rcases lt_or_ge (t - ⌊t⌋) (4417 / 6656 : ℝ) with c1409 | c1409
  · refine ⟨40, 69 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1408, c1409]
  rcases lt_or_ge (t - ⌊t⌋) (4673 / 7040 : ℝ) with c1410 | c1410
  · refine ⟨42, 73 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1409, c1410]
  rcases lt_or_ge (t - ⌊t⌋) (4929 / 7424 : ℝ) with c1411 | c1411
  · refine ⟨45, 77 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1410, c1411]
  rcases lt_or_ge (t - ⌊t⌋) (85 / 128 : ℝ) with c1412 | c1412
  · refine ⟨48, 81 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1411, c1412]
  rcases lt_or_ge (t - ⌊t⌋) (353729 / 532480 : ℝ) with c1413 | c1413
  · refine ⟨57, 86 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1412, c1413]
  rcases lt_or_ge (t - ⌊t⌋) (257 / 384 : ℝ) with c1414 | c1414
  · refine ⟨1, 4 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1413, c1414]
  rcases lt_or_ge (t - ⌊t⌋) (5313 / 7936 : ℝ) with c1415 | c1415
  · refine ⟨49, 83 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1414, c1415]
  rcases lt_or_ge (t - ⌊t⌋) (5057 / 7552 : ℝ) with c1416 | c1416
  · refine ⟨46, 79 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1415, c1416]
  rcases lt_or_ge (t - ⌊t⌋) (225737 / 336960 : ℝ) with c1417 | c1417
  · refine ⟨62, 55 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1416, c1417]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 6400 : ℝ) with c1418 | c1418
  · refine ⟨38, 67 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1417, c1418]
  rcases lt_or_ge (t - ⌊t⌋) (4033 / 6016 : ℝ) with c1419 | c1419
  · refine ⟨36, 63 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1418, c1419]
  rcases lt_or_ge (t - ⌊t⌋) (3777 / 5632 : ℝ) with c1420 | c1420
  · refine ⟨33, 59 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1419, c1420]
  rcases lt_or_ge (t - ⌊t⌋) (3521 / 5248 : ℝ) with c1421 | c1421
  · refine ⟨30, 55 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1420, c1421]
  rcases lt_or_ge (t - ⌊t⌋) (3265 / 4864 : ℝ) with c1422 | c1422
  · refine ⟨27, 51 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1421, c1422]
  rcases lt_or_ge (t - ⌊t⌋) (3009 / 4480 : ℝ) with c1423 | c1423
  · refine ⟨25, 47 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1422, c1423]
  rcases lt_or_ge (t - ⌊t⌋) (178881 / 266240 : ℝ) with c1424 | c1424
  · refine ⟨56, 43 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1423, c1424]
  rcases lt_or_ge (t - ⌊t⌋) (357889 / 532480 : ℝ) with c1425 | c1425
  · refine ⟨57, 87 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1424, c1425]
  rcases lt_or_ge (t - ⌊t⌋) (5249 / 7808 : ℝ) with c1426 | c1426
  · refine ⟨48, 82 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1425, c1426]
  rcases lt_or_ge (t - ⌊t⌋) (2497 / 3712 : ℝ) with c1427 | c1427
  · refine ⟨20, 39 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1426, c1427]
  rcases lt_or_ge (t - ⌊t⌋) (4737 / 7040 : ℝ) with c1428 | c1428
  · refine ⟨42, 74 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1427, c1428]
  rcases lt_or_ge (t - ⌊t⌋) (2241 / 3328 : ℝ) with c1429 | c1429
  · refine ⟨17, 35 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1428, c1429]
  rcases lt_or_ge (t - ⌊t⌋) (4225 / 6272 : ℝ) with c1430 | c1430
  · refine ⟨37, 66 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1429, c1430]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 2944 : ℝ) with c1431 | c1431
  · refine ⟨15, 31 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1430, c1431]
  rcases lt_or_ge (t - ⌊t⌋) (3713 / 5504 : ℝ) with c1432 | c1432
  · refine ⟨32, 58 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1431, c1432]
  rcases lt_or_ge (t - ⌊t⌋) (5441 / 8064 : ℝ) with c1433 | c1433
  · refine ⟨50, 85 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1432, c1433]
  rcases lt_or_ge (t - ⌊t⌋) (1729 / 2560 : ℝ) with c1434 | c1434
  · refine ⟨12, 27 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1433, c1434]
  rcases lt_or_ge (t - ⌊t⌋) (75977 / 112320 : ℝ) with c1435 | c1435
  · refine ⟨61, 19 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1434, c1435]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 2176 : ℝ) with c1436 | c1436
  · refine ⟨10, 23 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1435, c1436]
  rcases lt_or_ge (t - ⌊t⌋) (45099 / 66560 : ℝ) with c1437 | c1437
  · refine ⟨55, 33 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1436, c1437]
  rcases lt_or_ge (t - ⌊t⌋) (2689 / 3968 : ℝ) with c1438 | c1438
  · refine ⟨22, 42 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1437, c1438]
  rcases lt_or_ge (t - ⌊t⌋) (781 / 1152 : ℝ) with c1439 | c1439
  · refine ⟨34, 61 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1438, c1439]
  rcases lt_or_ge (t - ⌊t⌋) (5121 / 7552 : ℝ) with c1440 | c1440
  · refine ⟨46, 80 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1439, c1440]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 1792 : ℝ) with c1441 | c1441
  · refine ⟨8, 19 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1440, c1441]
  rcases lt_or_ge (t - ⌊t⌋) (4609 / 6784 : ℝ) with c1442 | c1442
  · refine ⟨41, 72 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1441, c1442]
  rcases lt_or_ge (t - ⌊t⌋) (87 / 128 : ℝ) with c1443 | c1443
  · refine ⟨28, 53 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1442, c1443]
  rcases lt_or_ge (t - ⌊t⌋) (362049 / 532480 : ℝ) with c1444 | c1444
  · refine ⟨57, 88 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1443, c1444]
  rcases lt_or_ge (t - ⌊t⌋) (101953 / 149760 : ℝ) with c1445 | c1445
  · refine ⟨54, 25 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1444, c1445]
  rcases lt_or_ge (t - ⌊t⌋) (4097 / 6016 : ℝ) with c1446 | c1446
  · refine ⟨36, 64 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1445, c1446]
  rcases lt_or_ge (t - ⌊t⌋) (5057 / 7424 : ℝ) with c1447 | c1447
  · refine ⟨45, 79 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1446, c1447]
  rcases lt_or_ge (t - ⌊t⌋) (961 / 1408 : ℝ) with c1448 | c1448
  · refine ⟨6, 15 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1447, c1448]
  rcases lt_or_ge (t - ⌊t⌋) (1835 / 2688 : ℝ) with c1449 | c1449
  · refine ⟨50, 86 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1448, c1449]
  rcases lt_or_ge (t - ⌊t⌋) (4545 / 6656 : ℝ) with c1450 | c1450
  · refine ⟨40, 71 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1449, c1450]
  rcases lt_or_ge (t - ⌊t⌋) (3585 / 5248 : ℝ) with c1451 | c1451
  · refine ⟨30, 56 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1450, c1451]
  rcases lt_or_ge (t - ⌊t⌋) (175 / 256 : ℝ) with c1452 | c1452
  · refine ⟨21, 41 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1451, c1452]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 6272 : ℝ) with c1453 | c1453
  · refine ⟨37, 67 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1452, c1453]
  rcases lt_or_ge (t - ⌊t⌋) (1665 / 2432 : ℝ) with c1454 | c1454
  · refine ⟨11, 26 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1453, c1454]
  rcases lt_or_ge (t - ⌊t⌋) (4033 / 5888 : ℝ) with c1455 | c1455
  · refine ⟨35, 63 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1454, c1455]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 3456 : ℝ) with c1456 | c1456
  · refine ⟨18, 37 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1455, c1456]
  rcases lt_or_ge (t - ⌊t⌋) (5441 / 7936 : ℝ) with c1457 | c1457
  · refine ⟨49, 85 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1456, c1457]
  rcases lt_or_ge (t - ⌊t⌋) (439 / 640 : ℝ) with c1458 | c1458
  · refine ⟨25, 48 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1457, c1458]
  rcases lt_or_ge (t - ⌊t⌋) (3777 / 5504 : ℝ) with c1459 | c1459
  · refine ⟨32, 59 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1458, c1459]
  rcases lt_or_ge (t - ⌊t⌋) (4481 / 6528 : ℝ) with c1460 | c1460
  · refine ⟨39, 70 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1459, c1460]
  rcases lt_or_ge (t - ⌊t⌋) (5185 / 7552 : ℝ) with c1461 | c1461
  · refine ⟨46, 81 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1460, c1461]
  rcases lt_or_ge (t - ⌊t⌋) (22891 / 33280 : ℝ) with c1462 | c1462
  · refine ⟨53, 17 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1461, c1462]
  rcases lt_or_ge (t - ⌊t⌋) (45889 / 66560 : ℝ) with c1463 | c1463
  · refine ⟨52, 12 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1462, c1463]
  rcases lt_or_ge (t - ⌊t⌋) (2561 / 3712 : ℝ) with c1464 | c1464
  · refine ⟨20, 40 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1463, c1464]
  rcases lt_or_ge (t - ⌊t⌋) (4417 / 6400 : ℝ) with c1465 | c1465
  · refine ⟨38, 69 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1464, c1465]
  rcases lt_or_ge (t - ⌊t⌋) (619 / 896 : ℝ) with c1466 | c1466
  · refine ⟨13, 29 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1465, c1466]
  rcases lt_or_ge (t - ⌊t⌋) (973 / 1408 : ℝ) with c1467 | c1467
  · refine ⟨42, 76 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1466, c1467]
  rcases lt_or_ge (t - ⌊t⌋) (177 / 256 : ℝ) with c1468 | c1468
  · refine ⟨24, 47 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1467, c1468]
  rcases lt_or_ge (t - ⌊t⌋) (4161 / 6016 : ℝ) with c1469 | c1469
  · refine ⟨36, 65 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1468, c1469]
  rcases lt_or_ge (t - ⌊t⌋) (1771 / 2560 : ℝ) with c1470 | c1470
  · refine ⟨47, 83 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1469, c1470]
  rcases lt_or_ge (t - ⌊t⌋) (1153 / 1664 : ℝ) with c1471 | c1471
  · refine ⟨7, 18 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1470, c1471]
  rcases lt_or_ge (t - ⌊t⌋) (5057 / 7296 : ℝ) with c1472 | c1472
  · refine ⟨44, 79 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1471, c1472]
  rcases lt_or_ge (t - ⌊t⌋) (355 / 512 : ℝ) with c1473 | c1473
  · refine ⟨33, 61 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1472, c1473]
  rcases lt_or_ge (t - ⌊t⌋) (26081 / 37440 : ℝ) with c1474 | c1474
  · refine ⟨60, 7 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1473, c1474]
  rcases lt_or_ge (t - ⌊t⌋) (5441 / 7808 : ℝ) with c1475 | c1475
  · refine ⟨48, 85 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1474, c1475]
  rcases lt_or_ge (t - ⌊t⌋) (2945 / 4224 : ℝ) with c1476 | c1476
  · refine ⟨23, 46 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1475, c1476]
  rcases lt_or_ge (t - ⌊t⌋) (3393 / 4864 : ℝ) with c1477 | c1477
  · refine ⟨27, 53 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1476, c1477]
  rcases lt_or_ge (t - ⌊t⌋) (3841 / 5504 : ℝ) with c1478 | c1478
  · refine ⟨32, 60 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1477, c1478]
  rcases lt_or_ge (t - ⌊t⌋) (139457 / 199680 : ℝ) with c1479 | c1479
  · refine ⟨55, 34 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1478, c1479]
  rcases lt_or_ge (t - ⌊t⌋) (5633 / 8064 : ℝ) with c1480 | c1480
  · refine ⟨50, 88 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1479, c1480]
  rcases lt_or_ge (t - ⌊t⌋) (449 / 640 : ℝ) with c1481 | c1481
  · refine ⟨2, 7 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1480, c1481]
  rcases lt_or_ge (t - ⌊t⌋) (5569 / 7936 : ℝ) with c1482 | c1482
  · refine ⟨49, 87 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1481, c1482]
  rcases lt_or_ge (t - ⌊t⌋) (1707 / 2432 : ℝ) with c1483 | c1483
  · refine ⟨44, 80 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1482, c1483]
  rcases lt_or_ge (t - ⌊t⌋) (4673 / 6656 : ℝ) with c1484 | c1484
  · refine ⟨40, 73 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1483, c1484]
  rcases lt_or_ge (t - ⌊t⌋) (4225 / 6016 : ℝ) with c1485 | c1485
  · refine ⟨36, 66 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1484, c1485]
  rcases lt_or_ge (t - ⌊t⌋) (1259 / 1792 : ℝ) with c1486 | c1486
  · refine ⟨31, 59 + 84 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1485, c1486]
  rcases lt_or_ge (t - ⌊t⌋) (3329 / 4736 : ℝ) with c1487 | c1487
  · refine ⟨26, 52 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1486, c1487]
  rcases lt_or_ge (t - ⌊t⌋) (187201 / 266240 : ℝ) with c1488 | c1488
  · refine ⟨56, 45 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1487, c1488]
  rcases lt_or_ge (t - ⌊t⌋) (374529 / 532480 : ℝ) with c1489 | c1489
  · refine ⟨57, 91 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1488, c1489]
  rcases lt_or_ge (t - ⌊t⌋) (5313 / 7552 : ℝ) with c1490 | c1490
  · refine ⟨46, 83 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1489, c1490]
  rcases lt_or_ge (t - ⌊t⌋) (811 / 1152 : ℝ) with c1491 | c1491
  · refine ⟨18, 38 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1490, c1491]
  rcases lt_or_ge (t - ⌊t⌋) (631 / 896 : ℝ) with c1492 | c1492
  · refine ⟨37, 69 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1491, c1492]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 2816 : ℝ) with c1493 | c1493
  · refine ⟨14, 31 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1492, c1493]
  rcases lt_or_ge (t - ⌊t⌋) (5505 / 7808 : ℝ) with c1494 | c1494
  · refine ⟨48, 86 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1493, c1494]
  rcases lt_or_ge (t - ⌊t⌋) (3521 / 4992 : ℝ) with c1495 | c1495
  · refine ⟨28, 55 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1494, c1495]
  rcases lt_or_ge (t - ⌊t⌋) (5057 / 7168 : ℝ) with c1496 | c1496
  · refine ⟨43, 79 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1495, c1496]
  rcases lt_or_ge (t - ⌊t⌋) (1537 / 2176 : ℝ) with c1497 | c1497
  · refine ⟨10, 24 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1496, c1497]
  rcases lt_or_ge (t - ⌊t⌋) (633 / 896 : ℝ) with c1498 | c1498
  · refine ⟨50, 89 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1497, c1498]
  rcases lt_or_ge (t - ⌊t⌋) (35393 / 49920 : ℝ) with c1499 | c1499
  · refine ⟨51, 9 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1498, c1499]
  rcases lt_or_ge (t - ⌊t⌋) (4993 / 7040 : ℝ) with c1500 | c1500
  · refine ⟨42, 78 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1499, c1500]
  rcases lt_or_ge (t - ⌊t⌋) (3905 / 5504 : ℝ) with c1501 | c1501
  · refine ⟨32, 61 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1500, c1501]
  rcases lt_or_ge (t - ⌊t⌋) (2817 / 3968 : ℝ) with c1502 | c1502
  · refine ⟨22, 44 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1501, c1502]
  rcases lt_or_ge (t - ⌊t⌋) (909 / 1280 : ℝ) with c1503 | c1503
  · refine ⟨38, 71 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1502, c1503]
  rcases lt_or_ge (t - ⌊t⌋) (91 / 128 : ℝ) with c1504 | c1504
  · refine ⟨11, 27 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1503, c1504]
  rcases lt_or_ge (t - ⌊t⌋) (378689 / 532480 : ℝ) with c1505 | c1505
  · refine ⟨57, 92 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1504, c1505]
  rcases lt_or_ge (t - ⌊t⌋) (4097 / 5760 : ℝ) with c1506 | c1506
  · refine ⟨34, 64 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1505, c1506]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 3328 : ℝ) with c1507 | c1507
  · refine ⟨17, 37 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1506, c1507]
  rcases lt_or_ge (t - ⌊t⌋) (5377 / 7552 : ℝ) with c1508 | c1508
  · refine ⟨46, 84 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1507, c1508]
  rcases lt_or_ge (t - ⌊t⌋) (1003 / 1408 : ℝ) with c1509 | c1509
  · refine ⟨23, 47 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1508, c1509]
  rcases lt_or_ge (t - ⌊t⌋) (80137 / 112320 : ℝ) with c1510 | c1510
  · refine ⟨61, 20 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1509, c1510]
  rcases lt_or_ge (t - ⌊t⌋) (641 / 896 : ℝ) with c1511 | c1511
  · refine ⟨3, 10 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1510, c1511]
  rcases lt_or_ge (t - ⌊t⌋) (5313 / 7424 : ℝ) with c1512 | c1512
  · refine ⟨45, 83 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1511, c1512]
  rcases lt_or_ge (t - ⌊t⌋) (4673 / 6528 : ℝ) with c1513 | c1513
  · refine ⟨39, 73 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1512, c1513]
  rcases lt_or_ge (t - ⌊t⌋) (4033 / 5632 : ℝ) with c1514 | c1514
  · refine ⟨33, 63 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1513, c1514]
  rcases lt_or_ge (t - ⌊t⌋) (3393 / 4736 : ℝ) with c1515 | c1515
  · refine ⟨26, 53 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1514, c1515]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 3840 : ℝ) with c1516 | c1516
  · refine ⟨21, 43 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1515, c1516]
  rcases lt_or_ge (t - ⌊t⌋) (4865 / 6784 : ℝ) with c1517 | c1517
  · refine ⟨41, 76 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1516, c1517]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 2944 : ℝ) with c1518 | c1518
  · refine ⟨15, 33 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1517, c1518]
  rcases lt_or_ge (t - ⌊t⌋) (5697 / 7936 : ℝ) with c1519 | c1519
  · refine ⟨49, 89 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1518, c1519]
  rcases lt_or_ge (t - ⌊t⌋) (1195 / 1664 : ℝ) with c1520 | c1520
  · refine ⟨28, 56 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1519, c1520]
  rcases lt_or_ge (t - ⌊t⌋) (5057 / 7040 : ℝ) with c1521 | c1521
  · refine ⟨42, 79 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1520, c1521]
  rcases lt_or_ge (t - ⌊t⌋) (191361 / 266240 : ℝ) with c1522 | c1522
  · refine ⟨56, 46 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1521, c1522]
  rcases lt_or_ge (t - ⌊t⌋) (143617 / 199680 : ℝ) with c1523 | c1523
  · refine ⟨55, 35 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1522, c1523]
  rcases lt_or_ge (t - ⌊t⌋) (5249 / 7296 : ℝ) with c1524 | c1524
  · refine ⟨44, 82 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1523, c1524]
  rcases lt_or_ge (t - ⌊t⌋) (3777 / 5248 : ℝ) with c1525 | c1525
  · refine ⟨30, 59 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1524, c1525]
  rcases lt_or_ge (t - ⌊t⌋) (461 / 640 : ℝ) with c1526 | c1526
  · refine ⟨16, 36 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1525, c1526]
  rcases lt_or_ge (t - ⌊t⌋) (5441 / 7552 : ℝ) with c1527 | c1527
  · refine ⟨46, 85 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1526, c1527]
  rcases lt_or_ge (t - ⌊t⌋) (3137 / 4352 : ℝ) with c1528 | c1528
  · refine ⟨24, 49 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1527, c1528]
  rcases lt_or_ge (t - ⌊t⌋) (3969 / 5504 : ℝ) with c1529 | c1529
  · refine ⟨32, 62 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1528, c1529]
  rcases lt_or_ge (t - ⌊t⌋) (4801 / 6656 : ℝ) with c1530 | c1530
  · refine ⟨40, 75 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1529, c1530]
  rcases lt_or_ge (t - ⌊t⌋) (5633 / 7808 : ℝ) with c1531 | c1531
  · refine ⟨48, 88 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1530, c1531]
  rcases lt_or_ge (t - ⌊t⌋) (833 / 1152 : ℝ) with c1532 | c1532
  · refine ⟨4, 13 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1531, c1532]
  rcases lt_or_ge (t - ⌊t⌋) (5185 / 7168 : ℝ) with c1533 | c1533
  · refine ⟨43, 81 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1532, c1533]
  rcases lt_or_ge (t - ⌊t⌋) (4353 / 6016 : ℝ) with c1534 | c1534
  · refine ⟨36, 68 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1533, c1534]
  rcases lt_or_ge (t - ⌊t⌋) (3521 / 4864 : ℝ) with c1535 | c1535
  · refine ⟨27, 55 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1534, c1535]
  rcases lt_or_ge (t - ⌊t⌋) (2689 / 3712 : ℝ) with c1536 | c1536
  · refine ⟨20, 42 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1535, c1536]
  rcases lt_or_ge (t - ⌊t⌋) (4545 / 6272 : ℝ) with c1537 | c1537
  · refine ⟨37, 71 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1536, c1537]
  rcases lt_or_ge (t - ⌊t⌋) (1857 / 2560 : ℝ) with c1538 | c1538
  · refine ⟨12, 29 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1537, c1538]
  rcases lt_or_ge (t - ⌊t⌋) (1579 / 2176 : ℝ) with c1539 | c1539
  · refine ⟨39, 74 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1538, c1539]
  rcases lt_or_ge (t - ⌊t⌋) (2881 / 3968 : ℝ) with c1540 | c1540
  · refine ⟨22, 45 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1539, c1540]
  rcases lt_or_ge (t - ⌊t⌋) (3905 / 5376 : ℝ) with c1541 | c1541
  · refine ⟨31, 61 + 84 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1540, c1541]
  rcases lt_or_ge (t - ⌊t⌋) (93 / 128 : ℝ) with c1542 | c1542
  · refine ⟨41, 77 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1541, c1542]
  rcases lt_or_ge (t - ⌊t⌋) (387009 / 532480 : ℝ) with c1543 | c1543
  · refine ⟨57, 94 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1542, c1543]
  rcases lt_or_ge (t - ⌊t⌋) (1025 / 1408 : ℝ) with c1544 | c1544
  · refine ⟨6, 16 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1543, c1544]
  rcases lt_or_ge (t - ⌊t⌋) (1771 / 2432 : ℝ) with c1545 | c1545
  · refine ⟨44, 83 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1544, c1545]
  rcases lt_or_ge (t - ⌊t⌋) (72833 / 99840 : ℝ) with c1546 | c1546
  · refine ⟨53, 18 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1545, c1546]
  rcases lt_or_ge (t - ⌊t⌋) (5697 / 7808 : ℝ) with c1547 | c1547
  · refine ⟨48, 89 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1546, c1547]
  rcases lt_or_ge (t - ⌊t⌋) (3457 / 4736 : ℝ) with c1548 | c1548
  · refine ⟨26, 54 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1547, c1548]
  rcases lt_or_ge (t - ⌊t⌋) (4673 / 6400 : ℝ) with c1549 | c1549
  · refine ⟨38, 73 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1548, c1549]
  rcases lt_or_ge (t - ⌊t⌋) (1963 / 2688 : ℝ) with c1550 | c1550
  · refine ⟨50, 92 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1549, c1550]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 1664 : ℝ) with c1551 | c1551
  · refine ⟨7, 19 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1550, c1551]
  rcases lt_or_ge (t - ⌊t⌋) (9131 / 12480 : ℝ) with c1552 | c1552
  · refine ⟨62, 60 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1551, c1552]
  rcases lt_or_ge (t - ⌊t⌋) (3841 / 5248 : ℝ) with c1553 | c1553
  · refine ⟨30, 60 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1552, c1553]
  rcases lt_or_ge (t - ⌊t⌋) (375 / 512 : ℝ) with c1554 | c1554
  · refine ⟨19, 41 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1553, c1554]
  rcases lt_or_ge (t - ⌊t⌋) (4033 / 5504 : ℝ) with c1555 | c1555
  · refine ⟨32, 63 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1554, c1555]
  rcases lt_or_ge (t - ⌊t⌋) (5441 / 7424 : ℝ) with c1556 | c1556
  · refine ⟨45, 85 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1555, c1556]
  rcases lt_or_ge (t - ⌊t⌋) (1409 / 1920 : ℝ) with c1557 | c1557
  · refine ⟨9, 22 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1556, c1557]
  rcases lt_or_ge (t - ⌊t⌋) (5825 / 7936 : ℝ) with c1558 | c1558
  · refine ⟨49, 91 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1557, c1558]
  rcases lt_or_ge (t - ⌊t⌋) (195521 / 266240 : ℝ) with c1559 | c1559
  · refine ⟨56, 47 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1558, c1559]
  rcases lt_or_ge (t - ⌊t⌋) (391169 / 532480 : ℝ) with c1560 | c1560
  · refine ⟨57, 95 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1559, c1560]
  rcases lt_or_ge (t - ⌊t⌋) (4609 / 6272 : ℝ) with c1561 | c1561
  · refine ⟨37, 72 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1560, c1561]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 2176 : ℝ) with c1562 | c1562
  · refine ⟨10, 25 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1561, c1562]
  rcases lt_or_ge (t - ⌊t⌋) (110273 / 149760 : ℝ) with c1563 | c1563
  · refine ⟨54, 27 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1562, c1563]
  rcases lt_or_ge (t - ⌊t⌋) (1037 / 1408 : ℝ) with c1564 | c1564
  · refine ⟨42, 81 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1563, c1564]
  rcases lt_or_ge (t - ⌊t⌋) (1793 / 2432 : ℝ) with c1565 | c1565
  · refine ⟨11, 28 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1564, c1565]
  rcases lt_or_ge (t - ⌊t⌋) (5569 / 7552 : ℝ) with c1566 | c1566
  · refine ⟨46, 87 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1565, c1566]
  rcases lt_or_ge (t - ⌊t⌋) (3777 / 5120 : ℝ) with c1567 | c1567
  · refine ⟨29, 59 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1566, c1567]
  rcases lt_or_ge (t - ⌊t⌋) (5761 / 7808 : ℝ) with c1568 | c1568
  · refine ⟨48, 90 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1567, c1568]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 2688 : ℝ) with c1569 | c1569
  · refine ⟨13, 31 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1568, c1569]
  rcases lt_or_ge (t - ⌊t⌋) (4161 / 5632 : ℝ) with c1570 | c1570
  · refine ⟨33, 65 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1569, c1570]
  rcases lt_or_ge (t - ⌊t⌋) (2177 / 2944 : ℝ) with c1571 | c1571
  · refine ⟨15, 34 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1570, c1571]
  rcases lt_or_ge (t - ⌊t⌋) (49259 / 66560 : ℝ) with c1572 | c1572
  · refine ⟨55, 36 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1571, c1572]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 3200 : ℝ) with c1573 | c1573
  · refine ⟨16, 37 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1572, c1573]
  rcases lt_or_ge (t - ⌊t⌋) (4929 / 6656 : ℝ) with c1574 | c1574
  · refine ⟨40, 77 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1573, c1574]
  rcases lt_or_ge (t - ⌊t⌋) (2561 / 3456 : ℝ) with c1575 | c1575
  · refine ⟨18, 40 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1574, c1575]
  rcases lt_or_ge (t - ⌊t⌋) (759 / 1024 : ℝ) with c1576 | c1576
  · refine ⟨43, 83 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1575, c1576]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 3712 : ℝ) with c1577 | c1577
  · refine ⟨20, 43 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1576, c1577]
  rcases lt_or_ge (t - ⌊t⌋) (1899 / 2560 : ℝ) with c1578 | c1578
  · refine ⟨47, 89 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1577, c1578]
  rcases lt_or_ge (t - ⌊t⌋) (95 / 128 : ℝ) with c1579 | c1579
  · refine ⟨22, 46 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1578, c1579]
  rcases lt_or_ge (t - ⌊t⌋) (395329 / 532480 : ℝ) with c1580 | c1580
  · refine ⟨57, 96 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1579, c1580]
  rcases lt_or_ge (t - ⌊t⌋) (3137 / 4224 : ℝ) with c1581 | c1581
  · refine ⟨23, 49 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1580, c1581]
  rcases lt_or_ge (t - ⌊t⌋) (3329 / 4480 : ℝ) with c1582 | c1582
  · refine ⟨25, 52 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1581, c1582]
  rcases lt_or_ge (t - ⌊t⌋) (3521 / 4736 : ℝ) with c1583 | c1583
  · refine ⟨26, 55 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1582, c1583]
  rcases lt_or_ge (t - ⌊t⌋) (3713 / 4992 : ℝ) with c1584 | c1584
  · refine ⟨28, 58 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1583, c1584]
  rcases lt_or_ge (t - ⌊t⌋) (3905 / 5248 : ℝ) with c1585 | c1585
  · refine ⟨30, 61 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1584, c1585]
  rcases lt_or_ge (t - ⌊t⌋) (4097 / 5504 : ℝ) with c1586 | c1586
  · refine ⟨32, 64 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1585, c1586]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 5760 : ℝ) with c1587 | c1587
  · refine ⟨34, 67 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1586, c1587]
  rcases lt_or_ge (t - ⌊t⌋) (4481 / 6016 : ℝ) with c1588 | c1588
  · refine ⟨36, 70 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1587, c1588]
  rcases lt_or_ge (t - ⌊t⌋) (145 / 192 : ℝ) with c1589 | c1589
  · refine ⟨59, 3 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1588, c1589]
  rcases lt_or_ge (t - ⌊t⌋) (4545 / 6016 : ℝ) with c1590 | c1590
  · refine ⟨36, 71 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1589, c1590]
  rcases lt_or_ge (t - ⌊t⌋) (1451 / 1920 : ℝ) with c1591 | c1591
  · refine ⟨34, 68 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1590, c1591]
  rcases lt_or_ge (t - ⌊t⌋) (4161 / 5504 : ℝ) with c1592 | c1592
  · refine ⟨32, 65 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1591, c1592]
  rcases lt_or_ge (t - ⌊t⌋) (254857 / 336960 : ℝ) with c1593 | c1593
  · refine ⟨62, 62 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1592, c1593]
  rcases lt_or_ge (t - ⌊t⌋) (1259 / 1664 : ℝ) with c1594 | c1594
  · refine ⟨28, 59 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1593, c1594]
  rcases lt_or_ge (t - ⌊t⌋) (3585 / 4736 : ℝ) with c1595 | c1595
  · refine ⟨26, 56 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1594, c1595]
  rcases lt_or_ge (t - ⌊t⌋) (3393 / 4480 : ℝ) with c1596 | c1596
  · refine ⟨25, 53 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1595, c1596]
  rcases lt_or_ge (t - ⌊t⌋) (97 / 128 : ℝ) with c1597 | c1597
  · refine ⟨23, 50 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1596, c1597]
  rcases lt_or_ge (t - ⌊t⌋) (403649 / 532480 : ℝ) with c1598 | c1598
  · refine ⟨57, 98 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1597, c1598]
  rcases lt_or_ge (t - ⌊t⌋) (3009 / 3968 : ℝ) with c1599 | c1599
  · refine ⟨22, 47 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1598, c1599]
  rcases lt_or_ge (t - ⌊t⌋) (1165 / 1536 : ℝ) with c1600 | c1600
  · refine ⟨47, 91 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1599, c1600]
  rcases lt_or_ge (t - ⌊t⌋) (2817 / 3712 : ℝ) with c1601 | c1601
  · refine ⟨20, 44 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1600, c1601]
  rcases lt_or_ge (t - ⌊t⌋) (5441 / 7168 : ℝ) with c1602 | c1602
  · refine ⟨43, 85 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1601, c1602]
  rcases lt_or_ge (t - ⌊t⌋) (875 / 1152 : ℝ) with c1603 | c1603
  · refine ⟨18, 41 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1602, c1603]
  rcases lt_or_ge (t - ⌊t⌋) (389 / 512 : ℝ) with c1604 | c1604
  · refine ⟨40, 79 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1603, c1604]
  rcases lt_or_ge (t - ⌊t⌋) (2433 / 3200 : ℝ) with c1605 | c1605
  · refine ⟨16, 38 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1604, c1605]
  rcases lt_or_ge (t - ⌊t⌋) (151937 / 199680 : ℝ) with c1606 | c1606
  · refine ⟨55, 37 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1605, c1606]
  rcases lt_or_ge (t - ⌊t⌋) (2241 / 2944 : ℝ) with c1607 | c1607
  · refine ⟨15, 35 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1606, c1607]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 5632 : ℝ) with c1608 | c1608
  · refine ⟨33, 67 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1607, c1608]
  rcases lt_or_ge (t - ⌊t⌋) (683 / 896 : ℝ) with c1609 | c1609
  · refine ⟨13, 32 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1608, c1609]
  rcases lt_or_ge (t - ⌊t⌋) (5953 / 7808 : ℝ) with c1610 | c1610
  · refine ⟨48, 93 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1609, c1610]
  rcases lt_or_ge (t - ⌊t⌋) (781 / 1024 : ℝ) with c1611 | c1611
  · refine ⟨29, 61 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1610, c1611]
  rcases lt_or_ge (t - ⌊t⌋) (5761 / 7552 : ℝ) with c1612 | c1612
  · refine ⟨46, 90 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1611, c1612]
  rcases lt_or_ge (t - ⌊t⌋) (1857 / 2432 : ℝ) with c1613 | c1613
  · refine ⟨11, 29 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1612, c1613]
  rcases lt_or_ge (t - ⌊t⌋) (114433 / 149760 : ℝ) with c1614 | c1614
  · refine ⟨54, 28 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1613, c1614]
  rcases lt_or_ge (t - ⌊t⌋) (5185 / 6784 : ℝ) with c1615 | c1615
  · refine ⟨41, 81 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1614, c1615]
  rcases lt_or_ge (t - ⌊t⌋) (1665 / 2176 : ℝ) with c1616 | c1616
  · refine ⟨10, 26 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1615, c1616]
  rcases lt_or_ge (t - ⌊t⌋) (203841 / 266240 : ℝ) with c1617 | c1617
  · refine ⟨56, 49 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1616, c1617]
  rcases lt_or_ge (t - ⌊t⌋) (407809 / 532480 : ℝ) with c1618 | c1618
  · refine ⟨57, 99 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1617, c1618]
  rcases lt_or_ge (t - ⌊t⌋) (4609 / 6016 : ℝ) with c1619 | c1619
  · refine ⟨36, 72 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1618, c1619]
  rcases lt_or_ge (t - ⌊t⌋) (6081 / 7936 : ℝ) with c1620 | c1620
  · refine ⟨49, 95 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1619, c1620]
  rcases lt_or_ge (t - ⌊t⌋) (491 / 640 : ℝ) with c1621 | c1621
  · refine ⟨9, 23 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1620, c1621]
  rcases lt_or_ge (t - ⌊t⌋) (5697 / 7424 : ℝ) with c1622 | c1622
  · refine ⟨45, 89 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1621, c1622]
  rcases lt_or_ge (t - ⌊t⌋) (4225 / 5504 : ℝ) with c1623 | c1623
  · refine ⟨32, 66 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1622, c1623]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 3584 : ℝ) with c1624 | c1624
  · refine ⟨19, 43 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1623, c1624]
  rcases lt_or_ge (t - ⌊t⌋) (4033 / 5248 : ℝ) with c1625 | c1625
  · refine ⟨30, 63 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1624, c1625]
  rcases lt_or_ge (t - ⌊t⌋) (86339 / 112320 : ℝ) with c1626 | c1626
  · refine ⟨62, 63 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1625, c1626]
  rcases lt_or_ge (t - ⌊t⌋) (1281 / 1664 : ℝ) with c1627 | c1627
  · refine ⟨7, 20 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1626, c1627]
  rcases lt_or_ge (t - ⌊t⌋) (887 / 1152 : ℝ) with c1628 | c1628
  · refine ⟨50, 97 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1627, c1628]
  rcases lt_or_ge (t - ⌊t⌋) (76993 / 99840 : ℝ) with c1629 | c1629
  · refine ⟨53, 19 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1628, c1629]
  rcases lt_or_ge (t - ⌊t⌋) (5825 / 7552 : ℝ) with c1630 | c1630
  · refine ⟨46, 91 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1629, c1630]
  rcases lt_or_ge (t - ⌊t⌋) (3457 / 4480 : ℝ) with c1631 | c1631
  · refine ⟨25, 54 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1630, c1631]
  rcases lt_or_ge (t - ⌊t⌋) (4545 / 5888 : ℝ) with c1632 | c1632
  · refine ⟨35, 71 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1631, c1632]
  rcases lt_or_ge (t - ⌊t⌋) (5633 / 7296 : ℝ) with c1633 | c1633
  · refine ⟨44, 88 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1632, c1633]
  rcases lt_or_ge (t - ⌊t⌋) (99 / 128 : ℝ) with c1634 | c1634
  · refine ⟨6, 17 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1633, c1634]
  rcases lt_or_ge (t - ⌊t⌋) (411969 / 532480 : ℝ) with c1635 | c1635
  · refine ⟨57, 100 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1634, c1635]
  rcases lt_or_ge (t - ⌊t⌋) (1387 / 1792 : ℝ) with c1636 | c1636
  · refine ⟨31, 65 + 84 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1635, c1636]
  rcases lt_or_ge (t - ⌊t⌋) (3073 / 3968 : ℝ) with c1637 | c1637
  · refine ⟨22, 48 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1636, c1637]
  rcases lt_or_ge (t - ⌊t⌋) (5057 / 6528 : ℝ) with c1638 | c1638
  · refine ⟨39, 79 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1637, c1638]
  rcases lt_or_ge (t - ⌊t⌋) (397 / 512 : ℝ) with c1639 | c1639
  · refine ⟨12, 31 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1638, c1639]
  rcases lt_or_ge (t - ⌊t⌋) (695 / 896 : ℝ) with c1640 | c1640
  · refine ⟨37, 76 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1639, c1640]
  rcases lt_or_ge (t - ⌊t⌋) (2881 / 3712 : ℝ) with c1641 | c1641
  · refine ⟨20, 45 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1640, c1641]
  rcases lt_or_ge (t - ⌊t⌋) (3777 / 4864 : ℝ) with c1642 | c1642
  · refine ⟨27, 59 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1641, c1642]
  rcases lt_or_ge (t - ⌊t⌋) (4673 / 6016 : ℝ) with c1643 | c1643
  · refine ⟨36, 73 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1642, c1643]
  rcases lt_or_ge (t - ⌊t⌋) (5569 / 7168 : ℝ) with c1644 | c1644
  · refine ⟨43, 87 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1643, c1644]
  rcases lt_or_ge (t - ⌊t⌋) (299 / 384 : ℝ) with c1645 | c1645
  · refine ⟨4, 14 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1644, c1645]
  rcases lt_or_ge (t - ⌊t⌋) (6081 / 7808 : ℝ) with c1646 | c1646
  · refine ⟨48, 95 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1645, c1646]
  rcases lt_or_ge (t - ⌊t⌋) (5185 / 6656 : ℝ) with c1647 | c1647
  · refine ⟨40, 81 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1646, c1647]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 5504 : ℝ) with c1648 | c1648
  · refine ⟨32, 67 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1647, c1648]
  rcases lt_or_ge (t - ⌊t⌋) (3393 / 4352 : ℝ) with c1649 | c1649
  · refine ⟨24, 53 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1648, c1649]
  rcases lt_or_ge (t - ⌊t⌋) (5889 / 7552 : ℝ) with c1650 | c1650
  · refine ⟨46, 92 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1649, c1650]
  rcases lt_or_ge (t - ⌊t⌋) (2497 / 3200 : ℝ) with c1651 | c1651
  · refine ⟨16, 39 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1650, c1651]
  rcases lt_or_ge (t - ⌊t⌋) (4097 / 5248 : ℝ) with c1652 | c1652
  · refine ⟨30, 64 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1651, c1652]
  rcases lt_or_ge (t - ⌊t⌋) (263177 / 336960 : ℝ) with c1653 | c1653
  · refine ⟨62, 64 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1652, c1653]
  rcases lt_or_ge (t - ⌊t⌋) (208001 / 266240 : ℝ) with c1654 | c1654
  · refine ⟨56, 50 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1653, c1654]
  rcases lt_or_ge (t - ⌊t⌋) (156097 / 199680 : ℝ) with c1655 | c1655
  · refine ⟨55, 38 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1654, c1655]
  rcases lt_or_ge (t - ⌊t⌋) (1101 / 1408 : ℝ) with c1656 | c1656
  · refine ⟨42, 86 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1655, c1656]
  rcases lt_or_ge (t - ⌊t⌋) (3905 / 4992 : ℝ) with c1657 | c1657
  · refine ⟨28, 61 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1656, c1657]
  rcases lt_or_ge (t - ⌊t⌋) (6209 / 7936 : ℝ) with c1658 | c1658
  · refine ⟨49, 97 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1657, c1658]
  rcases lt_or_ge (t - ⌊t⌋) (2305 / 2944 : ℝ) with c1659 | c1659
  · refine ⟨15, 36 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1658, c1659]
  rcases lt_or_ge (t - ⌊t⌋) (5313 / 6784 : ℝ) with c1660 | c1660
  · refine ⟨41, 83 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1659, c1660]
  rcases lt_or_ge (t - ⌊t⌋) (1003 / 1280 : ℝ) with c1661 | c1661
  · refine ⟨21, 47 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1660, c1661]
  rcases lt_or_ge (t - ⌊t⌋) (3713 / 4736 : ℝ) with c1662 | c1662
  · refine ⟨26, 58 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1661, c1662]
  rcases lt_or_ge (t - ⌊t⌋) (4417 / 5632 : ℝ) with c1663 | c1663
  · refine ⟨33, 69 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1662, c1663]
  rcases lt_or_ge (t - ⌊t⌋) (1707 / 2176 : ℝ) with c1664 | c1664
  · refine ⟨39, 80 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1663, c1664]
  rcases lt_or_ge (t - ⌊t⌋) (5825 / 7424 : ℝ) with c1665 | c1665
  · refine ⟨45, 91 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1664, c1665]
  rcases lt_or_ge (t - ⌊t⌋) (705 / 896 : ℝ) with c1666 | c1666
  · refine ⟨3, 11 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1665, c1666]
  rcases lt_or_ge (t - ⌊t⌋) (88457 / 112320 : ℝ) with c1667 | c1667
  · refine ⟨61, 22 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1666, c1667]
  rcases lt_or_ge (t - ⌊t⌋) (4033 / 5120 : ℝ) with c1668 | c1668
  · refine ⟨29, 63 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1667, c1668]
  rcases lt_or_ge (t - ⌊t⌋) (3329 / 4224 : ℝ) with c1669 | c1669
  · refine ⟨23, 52 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1668, c1669]
  rcases lt_or_ge (t - ⌊t⌋) (5953 / 7552 : ℝ) with c1670 | c1670
  · refine ⟨46, 93 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1669, c1670]
  rcases lt_or_ge (t - ⌊t⌋) (2625 / 3328 : ℝ) with c1671 | c1671
  · refine ⟨17, 41 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1670, c1671]
  rcases lt_or_ge (t - ⌊t⌋) (101 / 128 : ℝ) with c1672 | c1672
  · refine ⟨34, 71 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1671, c1672]
  rcases lt_or_ge (t - ⌊t⌋) (420289 / 532480 : ℝ) with c1673 | c1673
  · refine ⟨57, 102 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1672, c1673]
  rcases lt_or_ge (t - ⌊t⌋) (1921 / 2432 : ℝ) with c1674 | c1674
  · refine ⟨11, 30 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1673, c1674]
  rcases lt_or_ge (t - ⌊t⌋) (39553 / 49920 : ℝ) with c1675 | c1675
  · refine ⟨51, 10 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1674, c1675]
  rcases lt_or_ge (t - ⌊t⌋) (5377 / 6784 : ℝ) with c1676 | c1676
  · refine ⟨41, 84 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1675, c1676]
  rcases lt_or_ge (t - ⌊t⌋) (4161 / 5248 : ℝ) with c1677 | c1677
  · refine ⟨30, 65 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1676, c1677]
  rcases lt_or_ge (t - ⌊t⌋) (2945 / 3712 : ℝ) with c1678 | c1678
  · refine ⟨20, 46 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1677, c1678]
  rcases lt_or_ge (t - ⌊t⌋) (4673 / 5888 : ℝ) with c1679 | c1679
  · refine ⟨35, 73 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1678, c1679]
  rcases lt_or_ge (t - ⌊t⌋) (6401 / 8064 : ℝ) with c1680 | c1680
  · refine ⟨50, 100 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1679, c1680]
  rcases lt_or_ge (t - ⌊t⌋) (1729 / 2176 : ℝ) with c1681 | c1681
  · refine ⟨10, 27 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1680, c1681]
  rcases lt_or_ge (t - ⌊t⌋) (5697 / 7168 : ℝ) with c1682 | c1682
  · refine ⟨43, 89 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1681, c1682]
  rcases lt_or_ge (t - ⌊t⌋) (1323 / 1664 : ℝ) with c1683 | c1683
  · refine ⟨28, 62 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1682, c1683]
  rcases lt_or_ge (t - ⌊t⌋) (6209 / 7808 : ℝ) with c1684 | c1684
  · refine ⟨48, 97 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1683, c1684]
  rcases lt_or_ge (t - ⌊t⌋) (2241 / 2816 : ℝ) with c1685 | c1685
  · refine ⟨14, 35 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1684, c1685]
  rcases lt_or_ge (t - ⌊t⌋) (4993 / 6272 : ℝ) with c1686 | c1686
  · refine ⟨37, 78 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1685, c1686]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 3456 : ℝ) with c1687 | c1687
  · refine ⟨18, 43 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1686, c1687]
  rcases lt_or_ge (t - ⌊t⌋) (212161 / 266240 : ℝ) with c1688 | c1688
  · refine ⟨56, 51 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1687, c1688]
  rcases lt_or_ge (t - ⌊t⌋) (424449 / 532480 : ℝ) with c1689 | c1689
  · refine ⟨57, 103 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1688, c1689]
  rcases lt_or_ge (t - ⌊t⌋) (3777 / 4736 : ℝ) with c1690 | c1690
  · refine ⟨26, 59 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1689, c1690]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 5376 : ℝ) with c1691 | c1691
  · refine ⟨31, 67 + 84 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1690, c1691]
  rcases lt_or_ge (t - ⌊t⌋) (4801 / 6016 : ℝ) with c1692 | c1692
  · refine ⟨36, 75 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1691, c1692]
  rcases lt_or_ge (t - ⌊t⌋) (5313 / 6656 : ℝ) with c1693 | c1693
  · refine ⟨40, 83 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1692, c1693]
  rcases lt_or_ge (t - ⌊t⌋) (5825 / 7296 : ℝ) with c1694 | c1694
  · refine ⟨44, 91 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1693, c1694]
  rcases lt_or_ge (t - ⌊t⌋) (6337 / 7936 : ℝ) with c1695 | c1695
  · refine ⟨49, 99 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1694, c1695]
  rcases lt_or_ge (t - ⌊t⌋) (513 / 640 : ℝ) with c1696 | c1696
  · refine ⟨2, 8 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1695, c1696]
  rcases lt_or_ge (t - ⌊t⌋) (2155 / 2688 : ℝ) with c1697 | c1697
  · refine ⟨50, 101 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1696, c1697]
  rcases lt_or_ge (t - ⌊t⌋) (5953 / 7424 : ℝ) with c1698 | c1698
  · refine ⟨45, 93 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1697, c1698]
  rcases lt_or_ge (t - ⌊t⌋) (5441 / 6784 : ℝ) with c1699 | c1699
  · refine ⟨41, 85 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1698, c1699]
  rcases lt_or_ge (t - ⌊t⌋) (53419 / 66560 : ℝ) with c1700 | c1700
  · refine ⟨55, 39 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1699, c1700]
  rcases lt_or_ge (t - ⌊t⌋) (3905 / 4864 : ℝ) with c1701 | c1701
  · refine ⟨27, 61 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1700, c1701]
  rcases lt_or_ge (t - ⌊t⌋) (1131 / 1408 : ℝ) with c1702 | c1702
  · refine ⟨23, 53 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1701, c1702]
  rcases lt_or_ge (t - ⌊t⌋) (6273 / 7808 : ℝ) with c1703 | c1703
  · refine ⟨48, 98 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1702, c1703]
  rcases lt_or_ge (t - ⌊t⌋) (2881 / 3584 : ℝ) with c1704 | c1704
  · refine ⟨19, 45 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1703, c1704]
  rcases lt_or_ge (t - ⌊t⌋) (5249 / 6528 : ℝ) with c1705 | c1705
  · refine ⟨39, 82 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1704, c1705]
  rcases lt_or_ge (t - ⌊t⌋) (103 / 128 : ℝ) with c1706 | c1706
  · refine ⟨15, 37 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1705, c1706]
  rcases lt_or_ge (t - ⌊t⌋) (30241 / 37440 : ℝ) with c1707 | c1707
  · refine ⟨60, 8 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1706, c1707]
  rcases lt_or_ge (t - ⌊t⌋) (1345 / 1664 : ℝ) with c1708 | c1708
  · refine ⟨7, 21 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1707, c1708]
  rcases lt_or_ge (t - ⌊t⌋) (6209 / 7680 : ℝ) with c1709 | c1709
  · refine ⟨47, 97 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1708, c1709]
  rcases lt_or_ge (t - ⌊t⌋) (4865 / 6016 : ℝ) with c1710 | c1710
  · refine ⟨36, 76 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1709, c1710]
  rcases lt_or_ge (t - ⌊t⌋) (3521 / 4352 : ℝ) with c1711 | c1711
  · refine ⟨24, 55 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1710, c1711]
  rcases lt_or_ge (t - ⌊t⌋) (5697 / 7040 : ℝ) with c1712 | c1712
  · refine ⟨42, 89 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1711, c1712]
  rcases lt_or_ge (t - ⌊t⌋) (311 / 384 : ℝ) with c1713 | c1713
  · refine ⟨13, 34 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1712, c1713]
  rcases lt_or_ge (t - ⌊t⌋) (1037 / 1280 : ℝ) with c1714 | c1714
  · refine ⟨38, 81 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1713, c1714]
  rcases lt_or_ge (t - ⌊t⌋) (3009 / 3712 : ℝ) with c1715 | c1715
  · refine ⟨20, 47 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1714, c1715]
  rcases lt_or_ge (t - ⌊t⌋) (3841 / 4736 : ℝ) with c1716 | c1716
  · refine ⟨26, 60 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1715, c1716]
  rcases lt_or_ge (t - ⌊t⌋) (4673 / 5760 : ℝ) with c1717 | c1717
  · refine ⟨34, 73 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1716, c1717]
  rcases lt_or_ge (t - ⌊t⌋) (5505 / 6784 : ℝ) with c1718 | c1718
  · refine ⟨41, 86 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1717, c1718]
  rcases lt_or_ge (t - ⌊t⌋) (6337 / 7808 : ℝ) with c1719 | c1719
  · refine ⟨48, 99 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1718, c1719]
  rcases lt_or_ge (t - ⌊t⌋) (27051 / 33280 : ℝ) with c1720 | c1720
  · refine ⟨53, 20 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1719, c1720]
  rcases lt_or_ge (t - ⌊t⌋) (54209 / 66560 : ℝ) with c1721 | c1721
  · refine ⟨52, 14 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1720, c1721]
  rcases lt_or_ge (t - ⌊t⌋) (6465 / 7936 : ℝ) with c1722 | c1722
  · refine ⟨49, 101 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1721, c1722]
  rcases lt_or_ge (t - ⌊t⌋) (313 / 384 : ℝ) with c1723 | c1723
  · refine ⟨18, 44 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1722, c1723]
  rcases lt_or_ge (t - ⌊t⌋) (4801 / 5888 : ℝ) with c1724 | c1724
  · refine ⟨35, 75 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1723, c1724]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 2432 : ℝ) with c1725 | c1725
  · refine ⟨11, 31 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1724, c1725]
  rcases lt_or_ge (t - ⌊t⌋) (5121 / 6272 : ℝ) with c1726 | c1726
  · refine ⟨37, 80 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1725, c1726]
  rcases lt_or_ge (t - ⌊t⌋) (3137 / 3840 : ℝ) with c1727 | c1727
  · refine ⟨21, 49 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1726, c1727]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 5248 : ℝ) with c1728 | c1728
  · refine ⟨30, 67 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1727, c1728]
  rcases lt_or_ge (t - ⌊t⌋) (5441 / 6656 : ℝ) with c1729 | c1729
  · refine ⟨40, 85 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1728, c1729]
  rcases lt_or_ge (t - ⌊t⌋) (6593 / 8064 : ℝ) with c1730 | c1730
  · refine ⟨50, 103 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1729, c1730]
  rcases lt_or_ge (t - ⌊t⌋) (1153 / 1408 : ℝ) with c1731 | c1731
  · refine ⟨6, 18 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1730, c1731]
  rcases lt_or_ge (t - ⌊t⌋) (122753 / 149760 : ℝ) with c1732 | c1732
  · refine ⟨54, 30 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1731, c1732]
  rcases lt_or_ge (t - ⌊t⌋) (6401 / 7808 : ℝ) with c1733 | c1733
  · refine ⟨48, 100 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1732, c1733]
  rcases lt_or_ge (t - ⌊t⌋) (105 / 128 : ℝ) with c1734 | c1734
  · refine ⟨16, 41 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1733, c1734]
  rcases lt_or_ge (t - ⌊t⌋) (436929 / 532480 : ℝ) with c1735 | c1735
  · refine ⟨57, 106 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1734, c1735]
  rcases lt_or_ge (t - ⌊t⌋) (4097 / 4992 : ℝ) with c1736 | c1736
  · refine ⟨28, 64 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1735, c1736]
  rcases lt_or_ge (t - ⌊t⌋) (5569 / 6784 : ℝ) with c1737 | c1737
  · refine ⟨41, 87 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1736, c1737]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 1792 : ℝ) with c1738 | c1738
  · refine ⟨8, 23 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1737, c1738]
  rcases lt_or_ge (t - ⌊t⌋) (6209 / 7552 : ℝ) with c1739 | c1739
  · refine ⟨46, 97 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1738, c1739]
  rcases lt_or_ge (t - ⌊t⌋) (1579 / 1920 : ℝ) with c1740 | c1740
  · refine ⟨34, 74 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1739, c1740]
  rcases lt_or_ge (t - ⌊t⌋) (3265 / 3968 : ℝ) with c1741 | c1741
  · refine ⟨22, 51 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1740, c1741]
  rcases lt_or_ge (t - ⌊t⌋) (164417 / 199680 : ℝ) with c1742 | c1742
  · refine ⟨55, 40 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1741, c1742]
  rcases lt_or_ge (t - ⌊t⌋) (1793 / 2176 : ℝ) with c1743 | c1743
  · refine ⟨10, 28 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1742, c1743]
  rcases lt_or_ge (t - ⌊t⌋) (92617 / 112320 : ℝ) with c1744 | c1744
  · refine ⟨61, 23 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1743, c1744]
  rcases lt_or_ge (t - ⌊t⌋) (6017 / 7296 : ℝ) with c1745 | c1745
  · refine ⟨44, 94 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1744, c1745]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 2560 : ℝ) with c1746 | c1746
  · refine ⟨12, 33 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1745, c1746]
  rcases lt_or_ge (t - ⌊t⌋) (317 / 384 : ℝ) with c1747 | c1747
  · refine ⟨50, 104 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1746, c1747]
  rcases lt_or_ge (t - ⌊t⌋) (4545 / 5504 : ℝ) with c1748 | c1748
  · refine ⟨32, 71 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1747, c1748]
  rcases lt_or_ge (t - ⌊t⌋) (2433 / 2944 : ℝ) with c1749 | c1749
  · refine ⟨15, 38 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1748, c1749]
  rcases lt_or_ge (t - ⌊t⌋) (5185 / 6272 : ℝ) with c1750 | c1750
  · refine ⟨37, 81 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1749, c1750]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 3328 : ℝ) with c1751 | c1751
  · refine ⟨17, 43 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1750, c1751]
  rcases lt_or_ge (t - ⌊t⌋) (1165 / 1408 : ℝ) with c1752 | c1752
  · refine ⟨42, 91 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1751, c1752]
  rcases lt_or_ge (t - ⌊t⌋) (3073 / 3712 : ℝ) with c1753 | c1753
  · refine ⟨20, 48 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1752, c1753]
  rcases lt_or_ge (t - ⌊t⌋) (220481 / 266240 : ℝ) with c1754 | c1754
  · refine ⟨56, 53 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1753, c1754]
  rcases lt_or_ge (t - ⌊t⌋) (441089 / 532480 : ℝ) with c1755 | c1755
  · refine ⟨57, 107 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1754, c1755]
  rcases lt_or_ge (t - ⌊t⌋) (3713 / 4480 : ℝ) with c1756 | c1756
  · refine ⟨25, 58 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1755, c1756]
  rcases lt_or_ge (t - ⌊t⌋) (4033 / 4864 : ℝ) with c1757 | c1757
  · refine ⟨27, 63 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1756, c1757]
  rcases lt_or_ge (t - ⌊t⌋) (4353 / 5248 : ℝ) with c1758 | c1758
  · refine ⟨30, 68 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1757, c1758]
  rcases lt_or_ge (t - ⌊t⌋) (4673 / 5632 : ℝ) with c1759 | c1759
  · refine ⟨33, 73 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1758, c1759]
  rcases lt_or_ge (t - ⌊t⌋) (4993 / 6016 : ℝ) with c1760 | c1760
  · refine ⟨36, 78 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1759, c1760]
  rcases lt_or_ge (t - ⌊t⌋) (5313 / 6400 : ℝ) with c1761 | c1761
  · refine ⟨38, 83 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1760, c1761]
  rcases lt_or_ge (t - ⌊t⌋) (279817 / 336960 : ℝ) with c1762 | c1762
  · refine ⟨62, 68 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1761, c1762]
  rcases lt_or_ge (t - ⌊t⌋) (6273 / 7552 : ℝ) with c1763 | c1763
  · refine ⟨46, 98 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1762, c1763]
  rcases lt_or_ge (t - ⌊t⌋) (6593 / 7936 : ℝ) with c1764 | c1764
  · refine ⟨49, 103 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1763, c1764]
  rcases lt_or_ge (t - ⌊t⌋) (107 / 128 : ℝ) with c1765 | c1765
  · refine ⟨1, 5 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1764, c1765]
  rcases lt_or_ge (t - ⌊t⌋) (445249 / 532480 : ℝ) with c1766 | c1766
  · refine ⟨57, 108 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1765, c1766]
  rcases lt_or_ge (t - ⌊t⌋) (6209 / 7424 : ℝ) with c1767 | c1767
  · refine ⟨45, 97 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1766, c1767]
  rcases lt_or_ge (t - ⌊t⌋) (5889 / 7040 : ℝ) with c1768 | c1768
  · refine ⟨42, 92 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1767, c1768]
  rcases lt_or_ge (t - ⌊t⌋) (5569 / 6656 : ℝ) with c1769 | c1769
  · refine ⟨40, 87 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1768, c1769]
  rcases lt_or_ge (t - ⌊t⌋) (5249 / 6272 : ℝ) with c1770 | c1770
  · refine ⟨37, 82 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1769, c1770]
  rcases lt_or_ge (t - ⌊t⌋) (4929 / 5888 : ℝ) with c1771 | c1771
  · refine ⟨35, 77 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1770, c1771]
  rcases lt_or_ge (t - ⌊t⌋) (4609 / 5504 : ℝ) with c1772 | c1772
  · refine ⟨32, 72 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1771, c1772]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 5120 : ℝ) with c1773 | c1773
  · refine ⟨29, 67 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1772, c1773]
  rcases lt_or_ge (t - ⌊t⌋) (3969 / 4736 : ℝ) with c1774 | c1774
  · refine ⟨26, 62 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1773, c1774]
  rcases lt_or_ge (t - ⌊t⌋) (3649 / 4352 : ℝ) with c1775 | c1775
  · refine ⟨24, 57 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1774, c1775]
  rcases lt_or_ge (t - ⌊t⌋) (3329 / 3968 : ℝ) with c1776 | c1776
  · refine ⟨22, 52 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1775, c1776]
  rcases lt_or_ge (t - ⌊t⌋) (6337 / 7552 : ℝ) with c1777 | c1777
  · refine ⟨46, 99 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1776, c1777]
  rcases lt_or_ge (t - ⌊t⌋) (3009 / 3584 : ℝ) with c1778 | c1778
  · refine ⟨19, 47 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1777, c1778]
  rcases lt_or_ge (t - ⌊t⌋) (5697 / 6784 : ℝ) with c1779 | c1779
  · refine ⟨41, 89 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1778, c1779]
  rcases lt_or_ge (t - ⌊t⌋) (2689 / 3200 : ℝ) with c1780 | c1780
  · refine ⟨16, 42 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1779, c1780]
  rcases lt_or_ge (t - ⌊t⌋) (5057 / 6016 : ℝ) with c1781 | c1781
  · refine ⟨36, 79 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1780, c1781]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 2816 : ℝ) with c1782 | c1782
  · refine ⟨14, 37 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1781, c1782]
  rcases lt_or_ge (t - ⌊t⌋) (6785 / 8064 : ℝ) with c1783 | c1783
  · refine ⟨50, 106 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1782, c1783]
  rcases lt_or_ge (t - ⌊t⌋) (4417 / 5248 : ℝ) with c1784 | c1784
  · refine ⟨30, 69 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1783, c1784]
  rcases lt_or_ge (t - ⌊t⌋) (431 / 512 : ℝ) with c1785 | c1785
  · refine ⟨47, 101 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1784, c1785]
  rcases lt_or_ge (t - ⌊t⌋) (2049 / 2432 : ℝ) with c1786 | c1786
  · refine ⟨11, 32 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1785, c1786]
  rcases lt_or_ge (t - ⌊t⌋) (31553 / 37440 : ℝ) with c1787 | c1787
  · refine ⟨62, 69 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1786, c1787]
  rcases lt_or_ge (t - ⌊t⌋) (3777 / 4480 : ℝ) with c1788 | c1788
  · refine ⟨25, 59 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1787, c1788]
  rcases lt_or_ge (t - ⌊t⌋) (1835 / 2176 : ℝ) with c1789 | c1789
  · refine ⟨39, 86 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1788, c1789]
  rcases lt_or_ge (t - ⌊t⌋) (224641 / 266240 : ℝ) with c1790 | c1790
  · refine ⟨56, 54 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1789, c1790]
  rcases lt_or_ge (t - ⌊t⌋) (168577 / 199680 : ℝ) with c1791 | c1791
  · refine ⟨55, 41 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1790, c1791]
  rcases lt_or_ge (t - ⌊t⌋) (6593 / 7808 : ℝ) with c1792 | c1792
  · refine ⟨48, 103 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1791, c1792]
  rcases lt_or_ge (t - ⌊t⌋) (973 / 1152 : ℝ) with c1793 | c1793
  · refine ⟨34, 76 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1792, c1793]
  rcases lt_or_ge (t - ⌊t⌋) (3137 / 3712 : ℝ) with c1794 | c1794
  · refine ⟨20, 49 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1793, c1794]
  rcases lt_or_ge (t - ⌊t⌋) (1515 / 1792 : ℝ) with c1795 | c1795
  · refine ⟨31, 71 + 84 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1794, c1795]
  rcases lt_or_ge (t - ⌊t⌋) (5953 / 7040 : ℝ) with c1796 | c1796
  · refine ⟨42, 93 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1795, c1796]
  rcases lt_or_ge (t - ⌊t⌋) (1409 / 1664 : ℝ) with c1797 | c1797
  · refine ⟨7, 22 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1796, c1797]
  rcases lt_or_ge (t - ⌊t⌋) (126913 / 149760 : ℝ) with c1798 | c1798
  · refine ⟨54, 31 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1797, c1798]
  rcases lt_or_ge (t - ⌊t⌋) (6401 / 7552 : ℝ) with c1799 | c1799
  · refine ⟨46, 100 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1798, c1799]
  rcases lt_or_ge (t - ⌊t⌋) (2497 / 2944 : ℝ) with c1800 | c1800
  · refine ⟨15, 39 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1799, c1800]
  rcases lt_or_ge (t - ⌊t⌋) (6081 / 7168 : ℝ) with c1801 | c1801
  · refine ⟨43, 95 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1800, c1801]
  rcases lt_or_ge (t - ⌊t⌋) (1195 / 1408 : ℝ) with c1802 | c1802
  · refine ⟨23, 56 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1801, c1802]
  rcases lt_or_ge (t - ⌊t⌋) (4673 / 5504 : ℝ) with c1803 | c1803
  · refine ⟨32, 73 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1802, c1803]
  rcases lt_or_ge (t - ⌊t⌋) (5761 / 6784 : ℝ) with c1804 | c1804
  · refine ⟨41, 90 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1803, c1804]
  rcases lt_or_ge (t - ⌊t⌋) (761 / 896 : ℝ) with c1805 | c1805
  · refine ⟨50, 107 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1804, c1805]
  rcases lt_or_ge (t - ⌊t⌋) (1089 / 1280 : ℝ) with c1806 | c1806
  · refine ⟨5, 17 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1805, c1806]
  rcases lt_or_ge (t - ⌊t⌋) (6209 / 7296 : ℝ) with c1807 | c1807
  · refine ⟨44, 97 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1806, c1807]
  rcases lt_or_ge (t - ⌊t⌋) (5121 / 6016 : ℝ) with c1808 | c1808
  · refine ⟨36, 80 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1807, c1808]
  rcases lt_or_ge (t - ⌊t⌋) (109 / 128 : ℝ) with c1809 | c1809
  · refine ⟨26, 63 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1808, c1809]
  rcases lt_or_ge (t - ⌊t⌋) (453569 / 532480 : ℝ) with c1810 | c1810
  · refine ⟨57, 110 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1809, c1810]
  rcases lt_or_ge (t - ⌊t⌋) (2945 / 3456 : ℝ) with c1811 | c1811
  · refine ⟨18, 46 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1810, c1811]
  rcases lt_or_ge (t - ⌊t⌋) (4801 / 5632 : ℝ) with c1812 | c1812
  · refine ⟨33, 75 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1811, c1812]
  rcases lt_or_ge (t - ⌊t⌋) (6657 / 7808 : ℝ) with c1813 | c1813
  · refine ⟨48, 104 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1812, c1813]
  rcases lt_or_ge (t - ⌊t⌋) (1857 / 2176 : ℝ) with c1814 | c1814
  · refine ⟨10, 29 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1813, c1814]
  rcases lt_or_ge (t - ⌊t⌋) (85313 / 99840 : ℝ) with c1815 | c1815
  · refine ⟨53, 21 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1814, c1815]
  rcases lt_or_ge (t - ⌊t⌋) (547 / 640 : ℝ) with c1816 | c1816
  · refine ⟨42, 94 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1815, c1816]
  rcases lt_or_ge (t - ⌊t⌋) (3393 / 3968 : ℝ) with c1817 | c1817
  · refine ⟨22, 53 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1816, c1817]
  rcases lt_or_ge (t - ⌊t⌋) (219 / 256 : ℝ) with c1818 | c1818
  · refine ⟨27, 65 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1817, c1818]
  rcases lt_or_ge (t - ⌊t⌋) (1643 / 1920 : ℝ) with c1819 | c1819
  · refine ⟨34, 77 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1818, c1819]
  rcases lt_or_ge (t - ⌊t⌋) (5697 / 6656 : ℝ) with c1820 | c1820
  · refine ⟨40, 89 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1819, c1820]
  rcases lt_or_ge (t - ⌊t⌋) (6465 / 7552 : ℝ) with c1821 | c1821
  · refine ⟨46, 101 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1820, c1821]
  rcases lt_or_ge (t - ⌊t⌋) (769 / 896 : ℝ) with c1822 | c1822
  · refine ⟨3, 12 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1821, c1822]
  rcases lt_or_ge (t - ⌊t⌋) (6593 / 7680 : ℝ) with c1823 | c1823
  · refine ⟨47, 103 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1822, c1823]
  rcases lt_or_ge (t - ⌊t⌋) (5825 / 6784 : ℝ) with c1824 | c1824
  · refine ⟨41, 91 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1823, c1824]
  rcases lt_or_ge (t - ⌊t⌋) (5057 / 5888 : ℝ) with c1825 | c1825
  · refine ⟨35, 79 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1824, c1825]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 4992 : ℝ) with c1826 | c1826
  · refine ⟨28, 67 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1825, c1826]
  rcases lt_or_ge (t - ⌊t⌋) (228801 / 266240 : ℝ) with c1827 | c1827
  · refine ⟨56, 55 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1826, c1827]
  rcases lt_or_ge (t - ⌊t⌋) (457729 / 532480 : ℝ) with c1828 | c1828
  · refine ⟨57, 111 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1827, c1828]
  rcases lt_or_ge (t - ⌊t⌋) (2091 / 2432 : ℝ) with c1829 | c1829
  · refine ⟨44, 98 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1828, c1829]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 3200 : ℝ) with c1830 | c1830
  · refine ⟨16, 43 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1829, c1830]
  rcases lt_or_ge (t - ⌊t⌋) (4737 / 5504 : ℝ) with c1831 | c1831
  · refine ⟨32, 74 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1830, c1831]
  rcases lt_or_ge (t - ⌊t⌋) (10753 / 12480 : ℝ) with c1832 | c1832
  · refine ⟨61, 24 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1831, c1832]
  rcases lt_or_ge (t - ⌊t⌋) (5185 / 6016 : ℝ) with c1833 | c1833
  · refine ⟨36, 81 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1832, c1833]
  rcases lt_or_ge (t - ⌊t⌋) (3201 / 3712 : ℝ) with c1834 | c1834
  · refine ⟨20, 50 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1833, c1834]
  rcases lt_or_ge (t - ⌊t⌋) (4417 / 5120 : ℝ) with c1835 | c1835
  · refine ⟨29, 69 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1834, c1835]
  rcases lt_or_ge (t - ⌊t⌋) (5633 / 6528 : ℝ) with c1836 | c1836
  · refine ⟨39, 88 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1835, c1836]
  rcases lt_or_ge (t - ⌊t⌋) (6849 / 7936 : ℝ) with c1837 | c1837
  · refine ⟨49, 107 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1836, c1837]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 1408 : ℝ) with c1838 | c1838
  · refine ⟨6, 19 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1837, c1838]
  rcases lt_or_ge (t - ⌊t⌋) (6529 / 7552 : ℝ) with c1839 | c1839
  · refine ⟨46, 102 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1838, c1839]
  rcases lt_or_ge (t - ⌊t⌋) (57579 / 66560 : ℝ) with c1840 | c1840
  · refine ⟨55, 42 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1839, c1840]
  rcases lt_or_ge (t - ⌊t⌋) (6977 / 8064 : ℝ) with c1841 | c1841
  · refine ⟨50, 109 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1840, c1841]
  rcases lt_or_ge (t - ⌊t⌋) (2881 / 3328 : ℝ) with c1842 | c1842
  · refine ⟨17, 45 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1841, c1842]
  rcases lt_or_ge (t - ⌊t⌋) (4545 / 5248 : ℝ) with c1843 | c1843
  · refine ⟨30, 71 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1842, c1843]
  rcases lt_or_ge (t - ⌊t⌋) (887 / 1024 : ℝ) with c1844 | c1844
  · refine ⟨43, 97 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1843, c1844]
  rcases lt_or_ge (t - ⌊t⌋) (111 / 128 : ℝ) with c1845 | c1845
  · refine ⟨9, 26 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1844, c1845]
  rcases lt_or_ge (t - ⌊t⌋) (292297 / 336960 : ℝ) with c1846 | c1846
  · refine ⟨62, 71 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1845, c1846]
  rcases lt_or_ge (t - ⌊t⌋) (3777 / 4352 : ℝ) with c1847 | c1847
  · refine ⟨24, 59 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1846, c1847]
  rcases lt_or_ge (t - ⌊t⌋) (5889 / 6784 : ℝ) with c1848 | c1848
  · refine ⟨41, 92 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1847, c1848]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 2432 : ℝ) with c1849 | c1849
  · refine ⟨11, 33 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1848, c1849]
  rcases lt_or_ge (t - ⌊t⌋) (6785 / 7808 : ℝ) with c1850 | c1850
  · refine ⟨48, 106 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1849, c1850]
  rcases lt_or_ge (t - ⌊t⌋) (4673 / 5376 : ℝ) with c1851 | c1851
  · refine ⟨31, 73 + 84 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1850, c1851]
  rcases lt_or_ge (t - ⌊t⌋) (2561 / 2944 : ℝ) with c1852 | c1852
  · refine ⟨15, 40 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1851, c1852]
  rcases lt_or_ge (t - ⌊t⌋) (5569 / 6400 : ℝ) with c1853 | c1853
  · refine ⟨38, 87 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1852, c1853]
  rcases lt_or_ge (t - ⌊t⌋) (1003 / 1152 : ℝ) with c1854 | c1854
  · refine ⟨18, 47 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1853, c1854]
  rcases lt_or_ge (t - ⌊t⌋) (6465 / 7424 : ℝ) with c1855 | c1855
  · refine ⟨45, 101 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1854, c1855]
  rcases lt_or_ge (t - ⌊t⌋) (3457 / 3968 : ℝ) with c1856 | c1856
  · refine ⟨22, 54 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1855, c1856]
  rcases lt_or_ge (t - ⌊t⌋) (781 / 896 : ℝ) with c1857 | c1857
  · refine ⟨25, 61 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1856, c1857]
  rcases lt_or_ge (t - ⌊t⌋) (1451 / 1664 : ℝ) with c1858 | c1858
  · refine ⟨28, 68 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1857, c1858]
  rcases lt_or_ge (t - ⌊t⌋) (4801 / 5504 : ℝ) with c1859 | c1859
  · refine ⟨32, 75 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1858, c1859]
  rcases lt_or_ge (t - ⌊t⌋) (5249 / 6016 : ℝ) with c1860 | c1860
  · refine ⟨36, 82 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1859, c1860]
  rcases lt_or_ge (t - ⌊t⌋) (1899 / 2176 : ℝ) with c1861 | c1861
  · refine ⟨39, 89 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1860, c1861]
  rcases lt_or_ge (t - ⌊t⌋) (1229 / 1408 : ℝ) with c1862 | c1862
  · refine ⟨42, 96 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1861, c1862]
  rcases lt_or_ge (t - ⌊t⌋) (6593 / 7552 : ℝ) with c1863 | c1863
  · refine ⟨46, 103 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1862, c1863]
  rcases lt_or_ge (t - ⌊t⌋) (2347 / 2688 : ℝ) with c1864 | c1864
  · refine ⟨50, 110 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1863, c1864]
  rcases lt_or_ge (t - ⌊t⌋) (14571 / 16640 : ℝ) with c1865 | c1865
  · refine ⟨51, 11 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1864, c1865]
  rcases lt_or_ge (t - ⌊t⌋) (58369 / 66560 : ℝ) with c1866 | c1866
  · refine ⟨52, 15 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1865, c1866]
  rcases lt_or_ge (t - ⌊t⌋) (6849 / 7808 : ℝ) with c1867 | c1867
  · refine ⟨48, 107 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1866, c1867]
  rcases lt_or_ge (t - ⌊t⌋) (6401 / 7296 : ℝ) with c1868 | c1868
  · refine ⟨44, 100 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1867, c1868]
  rcases lt_or_ge (t - ⌊t⌋) (5953 / 6784 : ℝ) with c1869 | c1869
  · refine ⟨41, 93 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1868, c1869]
  rcases lt_or_ge (t - ⌊t⌋) (5505 / 6272 : ℝ) with c1870 | c1870
  · refine ⟨37, 86 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1869, c1870]
  rcases lt_or_ge (t - ⌊t⌋) (5057 / 5760 : ℝ) with c1871 | c1871
  · refine ⟨34, 79 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1870, c1871]
  rcases lt_or_ge (t - ⌊t⌋) (4609 / 5248 : ℝ) with c1872 | c1872
  · refine ⟨30, 72 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1871, c1872]
  rcases lt_or_ge (t - ⌊t⌋) (4161 / 4736 : ℝ) with c1873 | c1873
  · refine ⟨26, 65 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1872, c1873]
  rcases lt_or_ge (t - ⌊t⌋) (3713 / 4224 : ℝ) with c1874 | c1874
  · refine ⟨23, 58 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1873, c1874]
  rcases lt_or_ge (t - ⌊t⌋) (6977 / 7936 : ℝ) with c1875 | c1875
  · refine ⟨49, 109 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1874, c1875]
  rcases lt_or_ge (t - ⌊t⌋) (3265 / 3712 : ℝ) with c1876 | c1876
  · refine ⟨20, 51 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1875, c1876]
  rcases lt_or_ge (t - ⌊t⌋) (98819 / 112320 : ℝ) with c1877 | c1877
  · refine ⟨62, 72 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1876, c1877]
  rcases lt_or_ge (t - ⌊t⌋) (2817 / 3200 : ℝ) with c1878 | c1878
  · refine ⟨16, 44 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1877, c1878]
  rcases lt_or_ge (t - ⌊t⌋) (5185 / 5888 : ℝ) with c1879 | c1879
  · refine ⟨35, 81 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1878, c1879]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 2688 : ℝ) with c1880 | c1880
  · refine ⟨13, 37 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1879, c1880]
  rcases lt_or_ge (t - ⌊t⌋) (6657 / 7552 : ℝ) with c1881 | c1881
  · refine ⟨46, 104 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1880, c1881]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 4864 : ℝ) with c1882 | c1882
  · refine ⟨27, 67 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1881, c1882]
  rcases lt_or_ge (t - ⌊t⌋) (6209 / 7040 : ℝ) with c1883 | c1883
  · refine ⟨42, 97 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1882, c1883]
  rcases lt_or_ge (t - ⌊t⌋) (113 / 128 : ℝ) with c1884 | c1884
  · refine ⟨10, 30 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1883, c1884]
  rcases lt_or_ge (t - ⌊t⌋) (470209 / 532480 : ℝ) with c1885 | c1885
  · refine ⟨57, 114 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1884, c1885]
  rcases lt_or_ge (t - ⌊t⌋) (5313 / 6016 : ℝ) with c1886 | c1886
  · refine ⟨36, 83 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1885, c1886]
  rcases lt_or_ge (t - ⌊t⌋) (1131 / 1280 : ℝ) with c1887 | c1887
  · refine ⟨21, 53 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1886, c1887]
  rcases lt_or_ge (t - ⌊t⌋) (4865 / 5504 : ℝ) with c1888 | c1888
  · refine ⟨32, 76 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1887, c1888]
  rcases lt_or_ge (t - ⌊t⌋) (6337 / 7168 : ℝ) with c1889 | c1889
  · refine ⟨43, 99 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1888, c1889]
  rcases lt_or_ge (t - ⌊t⌋) (1473 / 1664 : ℝ) with c1890 | c1890
  · refine ⟨7, 23 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1889, c1890]
  rcases lt_or_ge (t - ⌊t⌋) (6913 / 7808 : ℝ) with c1891 | c1891
  · refine ⟨48, 108 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1890, c1891]
  rcases lt_or_ge (t - ⌊t⌋) (176897 / 199680 : ℝ) with c1892 | c1892
  · refine ⟨55, 43 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1891, c1892]
  rcases lt_or_ge (t - ⌊t⌋) (2155 / 2432 : ℝ) with c1893 | c1893
  · refine ⟨44, 101 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1892, c1893]
  rcases lt_or_ge (t - ⌊t⌋) (227 / 256 : ℝ) with c1894 | c1894
  · refine ⟨14, 39 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1893, c1894]
  rcases lt_or_ge (t - ⌊t⌋) (6017 / 6784 : ℝ) with c1895 | c1895
  · refine ⟨41, 94 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1894, c1895]
  rcases lt_or_ge (t - ⌊t⌋) (3521 / 3968 : ℝ) with c1896 | c1896
  · refine ⟨22, 55 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1895, c1896]
  rcases lt_or_ge (t - ⌊t⌋) (909 / 1024 : ℝ) with c1897 | c1897
  · refine ⟨29, 71 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1896, c1897]
  rcases lt_or_ge (t - ⌊t⌋) (5569 / 6272 : ℝ) with c1898 | c1898
  · refine ⟨37, 87 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1897, c1898]
  rcases lt_or_ge (t - ⌊t⌋) (6593 / 7424 : ℝ) with c1899 | c1899
  · refine ⟨45, 103 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1898, c1899]
  rcases lt_or_ge (t - ⌊t⌋) (1025 / 1152 : ℝ) with c1900 | c1900
  · refine ⟨4, 16 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1899, c1900]
  rcases lt_or_ge (t - ⌊t⌋) (6721 / 7552 : ℝ) with c1901 | c1901
  · refine ⟨46, 105 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1900, c1901]
  rcases lt_or_ge (t - ⌊t⌋) (5697 / 6400 : ℝ) with c1902 | c1902
  · refine ⟨38, 89 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1901, c1902]
  rcases lt_or_ge (t - ⌊t⌋) (237121 / 266240 : ℝ) with c1903 | c1903
  · refine ⟨56, 57 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1902, c1903]
  rcases lt_or_ge (t - ⌊t⌋) (474369 / 532480 : ℝ) with c1904 | c1904
  · refine ⟨57, 115 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1903, c1904]
  rcases lt_or_ge (t - ⌊t⌋) (6273 / 7040 : ℝ) with c1905 | c1905
  · refine ⟨42, 98 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1904, c1905]
  rcases lt_or_ge (t - ⌊t⌋) (2625 / 2944 : ℝ) with c1906 | c1906
  · refine ⟨15, 41 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1905, c1906]
  rcases lt_or_ge (t - ⌊t⌋) (2283 / 2560 : ℝ) with c1907 | c1907
  · refine ⟨47, 107 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1906, c1907]
  rcases lt_or_ge (t - ⌊t⌋) (300617 / 336960 : ℝ) with c1908 | c1908
  · refine ⟨62, 73 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1907, c1908]
  rcases lt_or_ge (t - ⌊t⌋) (5825 / 6528 : ℝ) with c1909 | c1909
  · refine ⟨39, 91 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1908, c1909]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 1792 : ℝ) with c1910 | c1910
  · refine ⟨8, 25 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1909, c1910]
  rcases lt_or_ge (t - ⌊t⌋) (6977 / 7808 : ℝ) with c1911 | c1911
  · refine ⟨48, 109 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1910, c1911]
  rcases lt_or_ge (t - ⌊t⌋) (5377 / 6016 : ℝ) with c1912 | c1912
  · refine ⟨36, 84 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1911, c1912]
  rcases lt_or_ge (t - ⌊t⌋) (1259 / 1408 : ℝ) with c1913 | c1913
  · refine ⟨23, 59 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1912, c1913]
  rcases lt_or_ge (t - ⌊t⌋) (5953 / 6656 : ℝ) with c1914 | c1914
  · refine ⟨40, 93 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1913, c1914]
  rcases lt_or_ge (t - ⌊t⌋) (2177 / 2432 : ℝ) with c1915 | c1915
  · refine ⟨11, 34 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1914, c1915]
  rcases lt_or_ge (t - ⌊t⌋) (89473 / 99840 : ℝ) with c1916 | c1916
  · refine ⟨53, 22 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1915, c1916]
  rcases lt_or_ge (t - ⌊t⌋) (6081 / 6784 : ℝ) with c1917 | c1917
  · refine ⟨41, 95 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1916, c1917]
  rcases lt_or_ge (t - ⌊t⌋) (3329 / 3712 : ℝ) with c1918 | c1918
  · refine ⟨20, 52 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1917, c1918]
  rcases lt_or_ge (t - ⌊t⌋) (2411 / 2688 : ℝ) with c1919 | c1919
  · refine ⟨50, 113 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1918, c1919]
  rcases lt_or_ge (t - ⌊t⌋) (3905 / 4352 : ℝ) with c1920 | c1920
  · refine ⟨24, 61 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1919, c1920]
  rcases lt_or_ge (t - ⌊t⌋) (4481 / 4992 : ℝ) with c1921 | c1921
  · refine ⟨28, 70 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1920, c1921]
  rcases lt_or_ge (t - ⌊t⌋) (100937 / 112320 : ℝ) with c1922 | c1922
  · refine ⟨61, 25 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1921, c1922]
  rcases lt_or_ge (t - ⌊t⌋) (577 / 640 : ℝ) with c1923 | c1923
  · refine ⟨2, 9 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1922, c1923]
  rcases lt_or_ge (t - ⌊t⌋) (7041 / 7808 : ℝ) with c1924 | c1924
  · refine ⟨48, 110 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1923, c1924]
  rcases lt_or_ge (t - ⌊t⌋) (6465 / 7168 : ℝ) with c1925 | c1925
  · refine ⟨43, 101 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1924, c1925]
  rcases lt_or_ge (t - ⌊t⌋) (1963 / 2176 : ℝ) with c1926 | c1926
  · refine ⟨39, 92 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1925, c1926]
  rcases lt_or_ge (t - ⌊t⌋) (231 / 256 : ℝ) with c1927 | c1927
  · refine ⟨35, 83 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1926, c1927]
  rcases lt_or_ge (t - ⌊t⌋) (135233 / 149760 : ℝ) with c1928 | c1928
  · refine ⟨54, 33 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1927, c1928]
  rcases lt_or_ge (t - ⌊t⌋) (3585 / 3968 : ℝ) with c1929 | c1929
  · refine ⟨22, 56 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1928, c1929]
  rcases lt_or_ge (t - ⌊t⌋) (347 / 384 : ℝ) with c1930 | c1930
  · refine ⟨44, 103 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1929, c1930]
  rcases lt_or_ge (t - ⌊t⌋) (3009 / 3328 : ℝ) with c1931 | c1931
  · refine ⟨17, 47 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1930, c1931]
  rcases lt_or_ge (t - ⌊t⌋) (304777 / 336960 : ℝ) with c1932 | c1932
  · refine ⟨62, 74 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1931, c1932]
  rcases lt_or_ge (t - ⌊t⌋) (811 / 896 : ℝ) with c1933 | c1933
  · refine ⟨13, 38 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1932, c1933]
  rcases lt_or_ge (t - ⌊t⌋) (6721 / 7424 : ℝ) with c1934 | c1934
  · refine ⟨45, 105 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1933, c1934]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 4736 : ℝ) with c1935 | c1935
  · refine ⟨26, 67 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1934, c1935]
  rcases lt_or_ge (t - ⌊t⌋) (6145 / 6784 : ℝ) with c1936 | c1936
  · refine ⟨41, 96 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1935, c1936]
  rcases lt_or_ge (t - ⌊t⌋) (241281 / 266240 : ℝ) with c1937 | c1937
  · refine ⟨56, 58 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1936, c1937]
  rcases lt_or_ge (t - ⌊t⌋) (181057 / 199680 : ℝ) with c1938 | c1938
  · refine ⟨55, 44 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1937, c1938]
  rcases lt_or_ge (t - ⌊t⌋) (6849 / 7552 : ℝ) with c1939 | c1939
  · refine ⟨46, 107 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1938, c1939]
  rcases lt_or_ge (t - ⌊t⌋) (4993 / 5504 : ℝ) with c1940 | c1940
  · refine ⟨32, 78 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1939, c1940]
  rcases lt_or_ge (t - ⌊t⌋) (3137 / 3456 : ℝ) with c1941 | c1941
  · refine ⟨18, 49 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1940, c1941]
  rcases lt_or_ge (t - ⌊t⌋) (4417 / 4864 : ℝ) with c1942 | c1942
  · refine ⟨27, 69 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1941, c1942]
  rcases lt_or_ge (t - ⌊t⌋) (5697 / 6272 : ℝ) with c1943 | c1943
  · refine ⟨37, 89 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1942, c1943]
  rcases lt_or_ge (t - ⌊t⌋) (6977 / 7680 : ℝ) with c1944 | c1944
  · refine ⟨47, 109 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1943, c1944]
  rcases lt_or_ge (t - ⌊t⌋) (1281 / 1408 : ℝ) with c1945 | c1945
  · refine ⟨6, 20 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1944, c1945]
  rcases lt_or_ge (t - ⌊t⌋) (7105 / 7808 : ℝ) with c1946 | c1946
  · refine ⟨48, 111 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1945, c1946]
  rcases lt_or_ge (t - ⌊t⌋) (233 / 256 : ℝ) with c1947 | c1947
  · refine ⟨38, 91 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1946, c1947]
  rcases lt_or_ge (t - ⌊t⌋) (1515 / 1664 : ℝ) with c1948 | c1948
  · refine ⟨28, 71 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1947, c1948]
  rcases lt_or_ge (t - ⌊t⌋) (3265 / 3584 : ℝ) with c1949 | c1949
  · refine ⟨19, 51 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1948, c1949]
  rcases lt_or_ge (t - ⌊t⌋) (5249 / 5760 : ℝ) with c1950 | c1950
  · refine ⟨34, 82 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1949, c1950]
  rcases lt_or_ge (t - ⌊t⌋) (7233 / 7936 : ℝ) with c1951 | c1951
  · refine ⟨49, 113 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1950, c1951]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 2176 : ℝ) with c1952 | c1952
  · refine ⟨10, 31 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1951, c1952]
  rcases lt_or_ge (t - ⌊t⌋) (2219 / 2432 : ℝ) with c1953 | c1953
  · refine ⟨44, 104 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1952, c1953]
  rcases lt_or_ge (t - ⌊t⌋) (4673 / 5120 : ℝ) with c1954 | c1954
  · refine ⟨29, 73 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1953, c1954]
  rcases lt_or_ge (t - ⌊t⌋) (7361 / 8064 : ℝ) with c1955 | c1955
  · refine ⟨50, 115 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1954, c1955]
  rcases lt_or_ge (t - ⌊t⌋) (2689 / 2944 : ℝ) with c1956 | c1956
  · refine ⟨15, 42 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1955, c1956]
  rcases lt_or_ge (t - ⌊t⌋) (6081 / 6656 : ℝ) with c1957 | c1957
  · refine ⟨40, 95 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1956, c1957]
  rcases lt_or_ge (t - ⌊t⌋) (117 / 128 : ℝ) with c1958 | c1958
  · refine ⟨20, 53 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1957, c1958]
  rcases lt_or_ge (t - ⌊t⌋) (486849 / 532480 : ℝ) with c1959 | c1959
  · refine ⟨57, 118 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1958, c1959]
  rcases lt_or_ge (t - ⌊t⌋) (4097 / 4480 : ℝ) with c1960 | c1960
  · refine ⟨25, 64 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1959, c1960]
  rcases lt_or_ge (t - ⌊t⌋) (4801 / 5248 : ℝ) with c1961 | c1961
  · refine ⟨30, 75 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1960, c1961]
  rcases lt_or_ge (t - ⌊t⌋) (5505 / 6016 : ℝ) with c1962 | c1962
  · refine ⟨36, 86 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1961, c1962]
  rcases lt_or_ge (t - ⌊t⌋) (6209 / 6784 : ℝ) with c1963 | c1963
  · refine ⟨41, 97 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1962, c1963]
  rcases lt_or_ge (t - ⌊t⌋) (6913 / 7552 : ℝ) with c1964 | c1964
  · refine ⟨46, 108 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1963, c1964]
  rcases lt_or_ge (t - ⌊t⌋) (11467 / 12480 : ℝ) with c1965 | c1965
  · refine ⟨60, 9 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1964, c1965]
  rcases lt_or_ge (t - ⌊t⌋) (4353 / 4736 : ℝ) with c1966 | c1966
  · refine ⟨26, 68 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1965, c1966]
  rcases lt_or_ge (t - ⌊t⌋) (3649 / 3968 : ℝ) with c1967 | c1967
  · refine ⟨22, 57 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1966, c1967]
  rcases lt_or_ge (t - ⌊t⌋) (6593 / 7168 : ℝ) with c1968 | c1968
  · refine ⟨43, 103 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1967, c1968]
  rcases lt_or_ge (t - ⌊t⌋) (589 / 640 : ℝ) with c1969 | c1969
  · refine ⟨16, 46 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1968, c1969]
  rcases lt_or_ge (t - ⌊t⌋) (5185 / 5632 : ℝ) with c1970 | c1970
  · refine ⟨33, 81 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1969, c1970]
  rcases lt_or_ge (t - ⌊t⌋) (825 / 896 : ℝ) with c1971 | c1971
  · refine ⟨50, 116 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1970, c1971]
  rcases lt_or_ge (t - ⌊t⌋) (2241 / 2432 : ℝ) with c1972 | c1972
  · refine ⟨11, 35 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1971, c1972]
  rcases lt_or_ge (t - ⌊t⌋) (245441 / 266240 : ℝ) with c1973 | c1973
  · refine ⟨56, 59 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1972, c1973]
  rcases lt_or_ge (t - ⌊t⌋) (491009 / 532480 : ℝ) with c1974 | c1974
  · refine ⟨57, 119 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1973, c1974]
  rcases lt_or_ge (t - ⌊t⌋) (1771 / 1920 : ℝ) with c1975 | c1975
  · refine ⟨34, 83 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1974, c1975]
  rcases lt_or_ge (t - ⌊t⌋) (6849 / 7424 : ℝ) with c1976 | c1976
  · refine ⟨45, 107 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1975, c1976]
  rcases lt_or_ge (t - ⌊t⌋) (1537 / 1664 : ℝ) with c1977 | c1977
  · refine ⟨7, 24 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1976, c1977]
  rcases lt_or_ge (t - ⌊t⌋) (6977 / 7552 : ℝ) with c1978 | c1978
  · refine ⟨46, 109 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1977, c1978]
  rcases lt_or_ge (t - ⌊t⌋) (5441 / 5888 : ℝ) with c1979 | c1979
  · refine ⟨35, 85 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1978, c1979]
  rcases lt_or_ge (t - ⌊t⌋) (355 / 384 : ℝ) with c1980 | c1980
  · refine ⟨23, 61 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1979, c1980]
  rcases lt_or_ge (t - ⌊t⌋) (6273 / 6784 : ℝ) with c1981 | c1981
  · refine ⟨41, 98 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1980, c1981]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 2560 : ℝ) with c1982 | c1982
  · refine ⟨12, 37 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1981, c1982]
  rcases lt_or_ge (t - ⌊t⌋) (5569 / 6016 : ℝ) with c1983 | c1983
  · refine ⟨36, 87 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1982, c1983]
  rcases lt_or_ge (t - ⌊t⌋) (1067 / 1152 : ℝ) with c1984 | c1984
  · refine ⟨18, 50 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1983, c1984]
  rcases lt_or_ge (t - ⌊t⌋) (7233 / 7808 : ℝ) with c1985 | c1985
  · refine ⟨48, 113 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1984, c1985]
  rcases lt_or_ge (t - ⌊t⌋) (4033 / 4352 : ℝ) with c1986 | c1986
  · refine ⟨24, 63 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1985, c1986]
  rcases lt_or_ge (t - ⌊t⌋) (4865 / 5248 : ℝ) with c1987 | c1987
  · refine ⟨30, 76 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1986, c1987]
  rcases lt_or_ge (t - ⌊t⌋) (61739 / 66560 : ℝ) with c1988 | c1988
  · refine ⟨55, 45 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1987, c1988]
  rcases lt_or_ge (t - ⌊t⌋) (119 / 128 : ℝ) with c1989 | c1989
  · refine ⟨3, 13 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1988, c1989]
  rcases lt_or_ge (t - ⌊t⌋) (495169 / 532480 : ℝ) with c1990 | c1990
  · refine ⟨57, 120 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1989, c1990]
  rcases lt_or_ge (t - ⌊t⌋) (139393 / 149760 : ℝ) with c1991 | c1991
  · refine ⟨54, 34 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1990, c1991]
  rcases lt_or_ge (t - ⌊t⌋) (3457 / 3712 : ℝ) with c1992 | c1992
  · refine ⟨20, 54 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1991, c1992]
  rcases lt_or_ge (t - ⌊t⌋) (2027 / 2176 : ℝ) with c1993 | c1993
  · refine ⟨39, 95 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1992, c1993]
  rcases lt_or_ge (t - ⌊t⌋) (2625 / 2816 : ℝ) with c1994 | c1994
  · refine ⟨14, 41 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1993, c1994]
  rcases lt_or_ge (t - ⌊t⌋) (7041 / 7552 : ℝ) with c1995 | c1995
  · refine ⟨46, 110 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1994, c1995]
  rcases lt_or_ge (t - ⌊t⌋) (4417 / 4736 : ℝ) with c1996 | c1996
  · refine ⟨26, 69 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1995, c1996]
  rcases lt_or_ge (t - ⌊t⌋) (6209 / 6656 : ℝ) with c1997 | c1997
  · refine ⟨40, 97 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1996, c1997]
  rcases lt_or_ge (t - ⌊t⌋) (1793 / 1920 : ℝ) with c1998 | c1998
  · refine ⟨9, 28 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1997, c1998]
  rcases lt_or_ge (t - ⌊t⌋) (6337 / 6784 : ℝ) with c1999 | c1999
  · refine ⟨41, 99 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1998, c1999]
  rcases lt_or_ge (t - ⌊t⌋) (4545 / 4864 : ℝ) with c2000 | c2000
  · refine ⟨27, 71 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1999, c2000]
  rcases lt_or_ge (t - ⌊t⌋) (7297 / 7808 : ℝ) with c2001 | c2001
  · refine ⟨48, 114 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2000, c2001]
  rcases lt_or_ge (t - ⌊t⌋) (105097 / 112320 : ℝ) with c2002 | c2002
  · refine ⟨61, 26 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2001, c2002]
  rcases lt_or_ge (t - ⌊t⌋) (3713 / 3968 : ℝ) with c2003 | c2003
  · refine ⟨22, 58 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2002, c2003]
  rcases lt_or_ge (t - ⌊t⌋) (4673 / 4992 : ℝ) with c2004 | c2004
  · refine ⟨28, 73 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2003, c2004]
  rcases lt_or_ge (t - ⌊t⌋) (5633 / 6016 : ℝ) with c2005 | c2005
  · refine ⟨36, 88 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2004, c2005]
  rcases lt_or_ge (t - ⌊t⌋) (6593 / 7040 : ℝ) with c2006 | c2006
  · refine ⟨42, 103 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2005, c2006]
  rcases lt_or_ge (t - ⌊t⌋) (1079 / 1152 : ℝ) with c2007 | c2007
  · refine ⟨50, 118 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2006, c2007]
  rcases lt_or_ge (t - ⌊t⌋) (31211 / 33280 : ℝ) with c2008 | c2008
  · refine ⟨53, 23 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2007, c2008]
  rcases lt_or_ge (t - ⌊t⌋) (62529 / 66560 : ℝ) with c2009 | c2009
  · refine ⟨52, 16 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2008, c2009]
  rcases lt_or_ge (t - ⌊t⌋) (1323 / 1408 : ℝ) with c2010 | c2010
  · refine ⟨23, 62 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2009, c2010]
  rcases lt_or_ge (t - ⌊t⌋) (6977 / 7424 : ℝ) with c2011 | c2011
  · refine ⟨45, 109 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2010, c2011]
  rcases lt_or_ge (t - ⌊t⌋) (3009 / 3200 : ℝ) with c2012 | c2012
  · refine ⟨16, 47 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2011, c2012]
  rcases lt_or_ge (t - ⌊t⌋) (5057 / 5376 : ℝ) with c2013 | c2013
  · refine ⟨31, 79 + 84 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2012, c2013]
  rcases lt_or_ge (t - ⌊t⌋) (7105 / 7552 : ℝ) with c2014 | c2014
  · refine ⟨46, 111 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2013, c2014]
  rcases lt_or_ge (t - ⌊t⌋) (2049 / 2176 : ℝ) with c2015 | c2015
  · refine ⟨10, 32 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2014, c2015]
  rcases lt_or_ge (t - ⌊t⌋) (2411 / 2560 : ℝ) with c2016 | c2016
  · refine ⟨47, 113 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2015, c2016]
  rcases lt_or_ge (t - ⌊t⌋) (5185 / 5504 : ℝ) with c2017 | c2017
  · refine ⟨32, 81 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2016, c2017]
  rcases lt_or_ge (t - ⌊t⌋) (3137 / 3328 : ℝ) with c2018 | c2018
  · refine ⟨17, 49 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2017, c2018]
  rcases lt_or_ge (t - ⌊t⌋) (7361 / 7808 : ℝ) with c2019 | c2019
  · refine ⟨48, 115 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2018, c2019]
  rcases lt_or_ge (t - ⌊t⌋) (845 / 896 : ℝ) with c2020 | c2020
  · refine ⟨25, 66 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2019, c2020]
  rcases lt_or_ge (t - ⌊t⌋) (483 / 512 : ℝ) with c2021 | c2021
  · refine ⟨33, 83 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2020, c2021]
  rcases lt_or_ge (t - ⌊t⌋) (6401 / 6784 : ℝ) with c2022 | c2022
  · refine ⟨41, 100 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2021, c2022]
  rcases lt_or_ge (t - ⌊t⌋) (7489 / 7936 : ℝ) with c2023 | c2023
  · refine ⟨49, 117 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2022, c2023]
  rcases lt_or_ge (t - ⌊t⌋) (121 / 128 : ℝ) with c2024 | c2024
  · refine ⟨4, 17 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2023, c2024]
  rcases lt_or_ge (t - ⌊t⌋) (503489 / 532480 : ℝ) with c2025 | c2025
  · refine ⟨57, 122 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2024, c2025]
  rcases lt_or_ge (t - ⌊t⌋) (5569 / 5888 : ℝ) with c2026 | c2026
  · refine ⟨35, 87 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2025, c2026]
  rcases lt_or_ge (t - ⌊t⌋) (4481 / 4736 : ℝ) with c2027 | c2027
  · refine ⟨26, 70 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2026, c2027]
  rcases lt_or_ge (t - ⌊t⌋) (3393 / 3584 : ℝ) with c2028 | c2028
  · refine ⟨19, 53 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2027, c2028]
  rcases lt_or_ge (t - ⌊t⌋) (5697 / 6016 : ℝ) with c2029 | c2029
  · refine ⟨36, 89 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2028, c2029]
  rcases lt_or_ge (t - ⌊t⌋) (2305 / 2432 : ℝ) with c2030 | c2030
  · refine ⟨11, 36 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2029, c2030]
  rcases lt_or_ge (t - ⌊t⌋) (189377 / 199680 : ℝ) with c2031 | c2031
  · refine ⟨55, 46 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2030, c2031]
  rcases lt_or_ge (t - ⌊t⌋) (3521 / 3712 : ℝ) with c2032 | c2032
  · refine ⟨20, 55 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2031, c2032]
  rcases lt_or_ge (t - ⌊t⌋) (1579 / 1664 : ℝ) with c2033 | c2033
  · refine ⟨28, 74 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2032, c2033]
  rcases lt_or_ge (t - ⌊t⌋) (5953 / 6272 : ℝ) with c2034 | c2034
  · refine ⟨37, 93 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2033, c2034]
  rcases lt_or_ge (t - ⌊t⌋) (7169 / 7552 : ℝ) with c2035 | c2035
  · refine ⟨46, 112 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2034, c2035]
  rcases lt_or_ge (t - ⌊t⌋) (1217 / 1280 : ℝ) with c2036 | c2036
  · refine ⟨5, 19 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2035, c2036]
  rcases lt_or_ge (t - ⌊t⌋) (7425 / 7808 : ℝ) with c2037 | c2037
  · refine ⟨48, 116 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2036, c2037]
  rcases lt_or_ge (t - ⌊t⌋) (6209 / 6528 : ℝ) with c2038 | c2038
  · refine ⟨39, 97 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2037, c2038]
  rcases lt_or_ge (t - ⌊t⌋) (4993 / 5248 : ℝ) with c2039 | c2039
  · refine ⟨30, 78 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2038, c2039]
  rcases lt_or_ge (t - ⌊t⌋) (3777 / 3968 : ℝ) with c2040 | c2040
  · refine ⟨22, 59 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2039, c2040]
  rcases lt_or_ge (t - ⌊t⌋) (6337 / 6656 : ℝ) with c2041 | c2041
  · refine ⟨40, 99 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2040, c2041]
  rcases lt_or_ge (t - ⌊t⌋) (2561 / 2688 : ℝ) with c2042 | c2042
  · refine ⟨13, 40 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2041, c2042]
  rcases lt_or_ge (t - ⌊t⌋) (253761 / 266240 : ℝ) with c2043 | c2043
  · refine ⟨56, 61 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2042, c2043]
  rcases lt_or_ge (t - ⌊t⌋) (507649 / 532480 : ℝ) with c2044 | c2044
  · refine ⟨57, 123 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2043, c2044]
  rcases lt_or_ge (t - ⌊t⌋) (5249 / 5504 : ℝ) with c2045 | c2045
  · refine ⟨32, 82 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2044, c2045]
  rcases lt_or_ge (t - ⌊t⌋) (35713 / 37440 : ℝ) with c2046 | c2046
  · refine ⟨62, 78 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2045, c2046]
  rcases lt_or_ge (t - ⌊t⌋) (1345 / 1408 : ℝ) with c2047 | c2047
  · refine ⟨6, 21 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2046, c2047]
  rcases lt_or_ge (t - ⌊t⌋) (6849 / 7168 : ℝ) with c2048 | c2048
  · refine ⟨43, 107 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2047, c2048]
  rcases lt_or_ge (t - ⌊t⌋) (367 / 384 : ℝ) with c2049 | c2049
  · refine ⟨34, 86 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2048, c2049]
  rcases lt_or_ge (t - ⌊t⌋) (4161 / 4352 : ℝ) with c2050 | c2050
  · refine ⟨24, 65 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2049, c2050]
  rcases lt_or_ge (t - ⌊t⌋) (6977 / 7296 : ℝ) with c2051 | c2051
  · refine ⟨44, 109 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2050, c2051]
  rcases lt_or_ge (t - ⌊t⌋) (2817 / 2944 : ℝ) with c2052 | c2052
  · refine ⟨15, 44 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2051, c2052]
  rcases lt_or_ge (t - ⌊t⌋) (47873 / 49920 : ℝ) with c2053 | c2053
  · refine ⟨51, 12 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2052, c2053]
  rcases lt_or_ge (t - ⌊t⌋) (7489 / 7808 : ℝ) with c2054 | c2054
  · refine ⟨48, 117 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2053, c2054]
  rcases lt_or_ge (t - ⌊t⌋) (6017 / 6272 : ℝ) with c2055 | c2055
  · refine ⟨37, 94 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2054, c2055]
  rcases lt_or_ge (t - ⌊t⌋) (4545 / 4736 : ℝ) with c2056 | c2056
  · refine ⟨26, 71 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2055, c2056]
  rcases lt_or_ge (t - ⌊t⌋) (7617 / 7936 : ℝ) with c2057 | c2057
  · refine ⟨49, 119 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2056, c2057]
  rcases lt_or_ge (t - ⌊t⌋) (3073 / 3200 : ℝ) with c2058 | c2058
  · refine ⟨16, 48 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2057, c2058]
  rcases lt_or_ge (t - ⌊t⌋) (7745 / 8064 : ℝ) with c2059 | c2059
  · refine ⟨50, 121 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2058, c2059]
  rcases lt_or_ge (t - ⌊t⌋) (4673 / 4864 : ℝ) with c2060 | c2060
  · refine ⟨27, 73 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2059, c2060]
  rcases lt_or_ge (t - ⌊t⌋) (123 / 128 : ℝ) with c2061 | c2061
  · refine ⟨39, 98 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2060, c2061]
  rcases lt_or_ge (t - ⌊t⌋) (511809 / 532480 : ℝ) with c2062 | c2062
  · refine ⟨57, 124 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2061, c2062]
  rcases lt_or_ge (t - ⌊t⌋) (1601 / 1664 : ℝ) with c2063 | c2063
  · refine ⟨7, 25 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2062, c2063]
  rcases lt_or_ge (t - ⌊t⌋) (6529 / 6784 : ℝ) with c2064 | c2064
  · refine ⟨41, 102 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2063, c2064]
  rcases lt_or_ge (t - ⌊t⌋) (4929 / 5120 : ℝ) with c2065 | c2065
  · refine ⟨29, 77 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2064, c2065]
  rcases lt_or_ge (t - ⌊t⌋) (3329 / 3456 : ℝ) with c2066 | c2066
  · refine ⟨18, 52 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2065, c2066]
  rcases lt_or_ge (t - ⌊t⌋) (5057 / 5248 : ℝ) with c2067 | c2067
  · refine ⟨30, 79 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2066, c2067]
  rcases lt_or_ge (t - ⌊t⌋) (1357 / 1408 : ℝ) with c2068 | c2068
  · refine ⟨42, 106 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2067, c2068]
  rcases lt_or_ge (t - ⌊t⌋) (247 / 256 : ℝ) with c2069 | c2069
  · refine ⟨8, 27 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2068, c2069]
  rcases lt_or_ge (t - ⌊t⌋) (2347 / 2432 : ℝ) with c2070 | c2070
  · refine ⟨44, 110 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2069, c2070]
  rcases lt_or_ge (t - ⌊t⌋) (5313 / 5504 : ℝ) with c2071 | c2071
  · refine ⟨32, 83 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2070, c2071]
  rcases lt_or_ge (t - ⌊t⌋) (3585 / 3712 : ℝ) with c2072 | c2072
  · refine ⟨20, 56 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2071, c2072]
  rcases lt_or_ge (t - ⌊t⌋) (5441 / 5632 : ℝ) with c2073 | c2073
  · refine ⟨33, 85 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2072, c2073]
  rcases lt_or_ge (t - ⌊t⌋) (7297 / 7552 : ℝ) with c2074 | c2074
  · refine ⟨46, 114 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2073, c2074]
  rcases lt_or_ge (t - ⌊t⌋) (619 / 640 : ℝ) with c2075 | c2075
  · refine ⟨9, 29 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2074, c2075]
  rcases lt_or_ge (t - ⌊t⌋) (7553 / 7808 : ℝ) with c2076 | c2076
  · refine ⟨48, 118 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2075, c2076]
  rcases lt_or_ge (t - ⌊t⌋) (5697 / 5888 : ℝ) with c2077 | c2077
  · refine ⟨35, 89 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2076, c2077]
  rcases lt_or_ge (t - ⌊t⌋) (3841 / 3968 : ℝ) with c2078 | c2078
  · refine ⟨22, 60 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2077, c2078]
  rcases lt_or_ge (t - ⌊t⌋) (5825 / 6016 : ℝ) with c2079 | c2079
  · refine ⟨36, 91 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2078, c2079]
  rcases lt_or_ge (t - ⌊t⌋) (2603 / 2688 : ℝ) with c2080 | c2080
  · refine ⟨50, 122 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2079, c2080]
  rcases lt_or_ge (t - ⌊t⌋) (257921 / 266240 : ℝ) with c2081 | c2081
  · refine ⟨56, 62 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2080, c2081]
  rcases lt_or_ge (t - ⌊t⌋) (193537 / 199680 : ℝ) with c2082 | c2082
  · refine ⟨55, 47 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2081, c2082]
  rcases lt_or_ge (t - ⌊t⌋) (6081 / 6272 : ℝ) with c2083 | c2083
  · refine ⟨37, 95 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2082, c2083]
  rcases lt_or_ge (t - ⌊t⌋) (4097 / 4224 : ℝ) with c2084 | c2084
  · refine ⟨23, 64 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2083, c2084]
  rcases lt_or_ge (t - ⌊t⌋) (6209 / 6400 : ℝ) with c2085 | c2085
  · refine ⟨38, 97 + 100 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2084, c2085]
  rcases lt_or_ge (t - ⌊t⌋) (2113 / 2176 : ℝ) with c2086 | c2086
  · refine ⟨10, 33 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2085, c2086]
  rcases lt_or_ge (t - ⌊t⌋) (6465 / 6656 : ℝ) with c2087 | c2087
  · refine ⟨40, 101 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2086, c2087]
  rcases lt_or_ge (t - ⌊t⌋) (4353 / 4480 : ℝ) with c2088 | c2088
  · refine ⟨25, 68 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2087, c2088]
  rcases lt_or_ge (t - ⌊t⌋) (36419 / 37440 : ℝ) with c2089 | c2089
  · refine ⟨61, 27 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2088, c2089]
  rcases lt_or_ge (t - ⌊t⌋) (6849 / 7040 : ℝ) with c2090 | c2090
  · refine ⟨42, 107 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2089, c2090]
  rcases lt_or_ge (t - ⌊t⌋) (4609 / 4736 : ℝ) with c2091 | c2091
  · refine ⟨26, 72 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2090, c2091]
  rcases lt_or_ge (t - ⌊t⌋) (6977 / 7168 : ℝ) with c2092 | c2092
  · refine ⟨43, 109 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2091, c2092]
  rcases lt_or_ge (t - ⌊t⌋) (2369 / 2432 : ℝ) with c2093 | c2093
  · refine ⟨11, 37 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2092, c2093]
  rcases lt_or_ge (t - ⌊t⌋) (7233 / 7424 : ℝ) with c2094 | c2094
  · refine ⟨45, 113 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2093, c2094]
  rcases lt_or_ge (t - ⌊t⌋) (4865 / 4992 : ℝ) with c2095 | c2095
  · refine ⟨28, 76 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2094, c2095]
  rcases lt_or_ge (t - ⌊t⌋) (7361 / 7552 : ℝ) with c2096 | c2096
  · refine ⟨46, 115 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2095, c2096]
  rcases lt_or_ge (t - ⌊t⌋) (2497 / 2560 : ℝ) with c2097 | c2097
  · refine ⟨12, 39 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2096, c2097]
  rcases lt_or_ge (t - ⌊t⌋) (7617 / 7808 : ℝ) with c2098 | c2098
  · refine ⟨48, 119 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2097, c2098]
  rcases lt_or_ge (t - ⌊t⌋) (5121 / 5248 : ℝ) with c2099 | c2099
  · refine ⟨30, 80 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2098, c2099]
  rcases lt_or_ge (t - ⌊t⌋) (7745 / 7936 : ℝ) with c2100 | c2100
  · refine ⟨49, 121 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2099, c2100]
  rcases lt_or_ge (t - ⌊t⌋) (125 / 128 : ℝ) with c2101 | c2101
  · refine ⟨13, 41 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2100, c2101]
  rcases lt_or_ge (t - ⌊t⌋) (520129 / 532480 : ℝ) with c2102 | c2102
  · refine ⟨57, 126 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2101, c2102]
  rcases lt_or_ge (t - ⌊t⌋) (5377 / 5504 : ℝ) with c2103 | c2103
  · refine ⟨32, 84 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2102, c2103]
  rcases lt_or_ge (t - ⌊t⌋) (2753 / 2816 : ℝ) with c2104 | c2104
  · refine ⟨14, 43 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2103, c2104]
  rcases lt_or_ge (t - ⌊t⌋) (5633 / 5760 : ℝ) with c2105 | c2105
  · refine ⟨34, 88 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2104, c2105]
  rcases lt_or_ge (t - ⌊t⌋) (2881 / 2944 : ℝ) with c2106 | c2106
  · refine ⟨15, 45 + 46 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2105, c2106]
  rcases lt_or_ge (t - ⌊t⌋) (97793 / 99840 : ℝ) with c2107 | c2107
  · refine ⟨53, 24 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2106, c2107]
  rcases lt_or_ge (t - ⌊t⌋) (6145 / 6272 : ℝ) with c2108 | c2108
  · refine ⟨37, 96 + 98 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2107, c2108]
  rcases lt_or_ge (t - ⌊t⌋) (3137 / 3200 : ℝ) with c2109 | c2109
  · refine ⟨16, 49 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2108, c2109]
  rcases lt_or_ge (t - ⌊t⌋) (6401 / 6528 : ℝ) with c2110 | c2110
  · refine ⟨39, 100 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2109, c2110]
  rcases lt_or_ge (t - ⌊t⌋) (3265 / 3328 : ℝ) with c2111 | c2111
  · refine ⟨17, 51 + 52 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2110, c2111]
  rcases lt_or_ge (t - ⌊t⌋) (6657 / 6784 : ℝ) with c2112 | c2112
  · refine ⟨41, 104 + 106 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2111, c2112]
  rcases lt_or_ge (t - ⌊t⌋) (377 / 384 : ℝ) with c2113 | c2113
  · refine ⟨18, 53 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2112, c2113]
  rcases lt_or_ge (t - ⌊t⌋) (6913 / 7040 : ℝ) with c2114 | c2114
  · refine ⟨42, 108 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2113, c2114]
  rcases lt_or_ge (t - ⌊t⌋) (503 / 512 : ℝ) with c2115 | c2115
  · refine ⟨19, 55 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2114, c2115]
  rcases lt_or_ge (t - ⌊t⌋) (7169 / 7296 : ℝ) with c2116 | c2116
  · refine ⟨44, 112 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2115, c2116]
  rcases lt_or_ge (t - ⌊t⌋) (3649 / 3712 : ℝ) with c2117 | c2117
  · refine ⟨20, 57 + 58 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2116, c2117]
  rcases lt_or_ge (t - ⌊t⌋) (7425 / 7552 : ℝ) with c2118 | c2118
  · refine ⟨46, 116 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2117, c2118]
  rcases lt_or_ge (t - ⌊t⌋) (1259 / 1280 : ℝ) with c2119 | c2119
  · refine ⟨21, 59 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2118, c2119]
  rcases lt_or_ge (t - ⌊t⌋) (7681 / 7808 : ℝ) with c2120 | c2120
  · refine ⟨48, 120 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2119, c2120]
  rcases lt_or_ge (t - ⌊t⌋) (3905 / 3968 : ℝ) with c2121 | c2121
  · refine ⟨22, 61 + 62 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2120, c2121]
  rcases lt_or_ge (t - ⌊t⌋) (262081 / 266240 : ℝ) with c2122 | c2122
  · refine ⟨56, 63 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2121, c2122]
  rcases lt_or_ge (t - ⌊t⌋) (524289 / 532480 : ℝ) with c2123 | c2123
  · refine ⟨57, 127 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2122, c2123]
  rcases lt_or_ge (t - ⌊t⌋) (1387 / 1408 : ℝ) with c2124 | c2124
  · refine ⟨23, 65 + 66 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2123, c2124]
  rcases lt_or_ge (t - ⌊t⌋) (4289 / 4352 : ℝ) with c2125 | c2125
  · refine ⟨24, 67 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2124, c2125]
  rcases lt_or_ge (t - ⌊t⌋) (147713 / 149760 : ℝ) with c2126 | c2126
  · refine ⟨54, 36 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2125, c2126]
  rcases lt_or_ge (t - ⌊t⌋) (4673 / 4736 : ℝ) with c2127 | c2127
  · refine ⟨26, 73 + 74 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2126, c2127]
  rcases lt_or_ge (t - ⌊t⌋) (4801 / 4864 : ℝ) with c2128 | c2128
  · refine ⟨27, 75 + 76 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2127, c2128]
  rcases lt_or_ge (t - ⌊t⌋) (1643 / 1664 : ℝ) with c2129 | c2129
  · refine ⟨28, 77 + 78 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2128, c2129]
  rcases lt_or_ge (t - ⌊t⌋) (5057 / 5120 : ℝ) with c2130 | c2130
  · refine ⟨29, 79 + 80 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2129, c2130]
  rcases lt_or_ge (t - ⌊t⌋) (5185 / 5248 : ℝ) with c2131 | c2131
  · refine ⟨30, 81 + 82 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2130, c2131]
  rcases lt_or_ge (t - ⌊t⌋) (253 / 256 : ℝ) with c2132 | c2132
  · refine ⟨31, 83 + 84 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2131, c2132]
  rcases lt_or_ge (t - ⌊t⌋) (5441 / 5504 : ℝ) with c2133 | c2133
  · refine ⟨32, 85 + 86 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2132, c2133]
  rcases lt_or_ge (t - ⌊t⌋) (5569 / 5632 : ℝ) with c2134 | c2134
  · refine ⟨33, 87 + 88 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2133, c2134]
  rcases lt_or_ge (t - ⌊t⌋) (633 / 640 : ℝ) with c2135 | c2135
  · refine ⟨34, 89 + 90 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2134, c2135]
  rcases lt_or_ge (t - ⌊t⌋) (5825 / 5888 : ℝ) with c2136 | c2136
  · refine ⟨35, 91 + 92 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2135, c2136]
  rcases lt_or_ge (t - ⌊t⌋) (5953 / 6016 : ℝ) with c2137 | c2137
  · refine ⟨36, 93 + 94 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2136, c2137]
  rcases lt_or_ge (t - ⌊t⌋) (65899 / 66560 : ℝ) with c2138 | c2138
  · refine ⟨55, 48 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2137, c2138]
  rcases lt_or_ge (t - ⌊t⌋) (2155 / 2176 : ℝ) with c2139 | c2139
  · refine ⟨39, 101 + 102 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2138, c2139]
  rcases lt_or_ge (t - ⌊t⌋) (6593 / 6656 : ℝ) with c2140 | c2140
  · refine ⟨40, 103 + 104 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2139, c2140]
  rcases lt_or_ge (t - ⌊t⌋) (111299 / 112320 : ℝ) with c2141 | c2141
  · refine ⟨62, 81 + 81 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2140, c2141]
  rcases lt_or_ge (t - ⌊t⌋) (6977 / 7040 : ℝ) with c2142 | c2142
  · refine ⟨42, 109 + 110 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2141, c2142]
  rcases lt_or_ge (t - ⌊t⌋) (1015 / 1024 : ℝ) with c2143 | c2143
  · refine ⟨43, 111 + 112 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2142, c2143]
  rcases lt_or_ge (t - ⌊t⌋) (2411 / 2432 : ℝ) with c2144 | c2144
  · refine ⟨44, 113 + 114 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2143, c2144]
  rcases lt_or_ge (t - ⌊t⌋) (7361 / 7424 : ℝ) with c2145 | c2145
  · refine ⟨45, 115 + 116 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2144, c2145]
  rcases lt_or_ge (t - ⌊t⌋) (7489 / 7552 : ℝ) with c2146 | c2146
  · refine ⟨46, 117 + 118 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2145, c2146]
  rcases lt_or_ge (t - ⌊t⌋) (2539 / 2560 : ℝ) with c2147 | c2147
  · refine ⟨47, 119 + 120 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2146, c2147]
  rcases lt_or_ge (t - ⌊t⌋) (7745 / 7808 : ℝ) with c2148 | c2148
  · refine ⟨48, 121 + 122 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2147, c2148]
  rcases lt_or_ge (t - ⌊t⌋) (7873 / 7936 : ℝ) with c2149 | c2149
  · refine ⟨49, 123 + 124 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2148, c2149]
  rcases lt_or_ge (t - ⌊t⌋) (127 / 128 : ℝ) with c2150 | c2150
  · refine ⟨50, 125 + 126 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2149, c2150]
  rcases lt_or_ge (t - ⌊t⌋) (528449 / 532480 : ℝ) with c2151 | c2151
  · refine ⟨57, 128 + 128 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2150, c2151]
  refine ⟨0, 2 + 2 * ⌊t⌋, ?_⟩
  simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
  rw [abs_lt]
  push_cast
  constructor <;> linarith only [c2151, h1]

#print axioms cover
#print axioms v_injective
#print axioms v_pos
end SLRAudit.N63
