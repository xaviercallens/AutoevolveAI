import Mathlib.Tactic

set_option linter.unusedSimpArgs false
set_option maxHeartbeats 0
namespace SLRAudit.N25

/-- velocities of certificate n = 25 -/
def v : Fin 25 → ℕ := ![1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
/-- shifts s_i = a_i / 10816 -/
def s : Fin 25 → ℚ := ![1041/10816, 8021/10816, 9718/10816, 926/10816, 6111/10816, 10335/10816, 2909/10816, 4482/10816, 780/10816, 4144/10816, 4035/10816, 280/10816, 5554/10816, 7059/10816, 2844/10816, 5772/10816, 7971/10816, 6829/10816, 107/10816, 9530/10816, 7070/10816, 5548/10816, 5980/10816, 4285/10816, 2028/10816]

theorem v_injective : Function.Injective v := by decide
theorem v_pos : ∀ i, 0 < v i := by decide

/-- covering: for every real t some runner is within distance < 1/26 of an integer. -/
theorem cover : ∀ t : ℝ, ∃ i : Fin 25, ∃ k : ℤ, |((s i : ℚ) : ℝ) + ((v i : ℕ) : ℝ) * t - (k : ℝ)| < 1 / 26 := by
  intro t
  have h0 : (0 : ℝ) ≤ t - ⌊t⌋ := by have := Int.floor_le t; linarith
  have h1 : t - ⌊t⌋ < (1 : ℝ) := by have := Int.lt_floor_add_one t; linarith
  rcases lt_or_ge (t - ⌊t⌋) (309 / 205504 : ℝ) with c0 | c0
  · refine ⟨18, 0 + 19 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [h0, c0]
  rcases lt_or_ge (t - ⌊t⌋) (23 / 1664 : ℝ) with c1 | c1
  · refine ⟨5, 1 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c0, c1]
  rcases lt_or_ge (t - ⌊t⌋) (3261 / 183872 : ℝ) with c2 | c2
  · refine ⟨16, 1 + 17 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1, c2]
  rcases lt_or_ge (t - ⌊t⌋) (2081 / 113568 : ℝ) with c3 | c3
  · refine ⟨20, 1 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2, c3]
  rcases lt_or_ge (t - ⌊t⌋) (101 / 4784 : ℝ) with c4 | c4
  · refine ⟨22, 1 + 23 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c3, c4]
  rcases lt_or_ge (t - ⌊t⌋) (757 / 16224 : ℝ) with c5 | c5
  · refine ⟨2, 1 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c4, c5]
  rcases lt_or_ge (t - ⌊t⌋) (699 / 13520 : ℝ) with c6 | c6
  · refine ⟨14, 1 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c5, c6]
  rcases lt_or_ge (t - ⌊t⌋) (11125 / 205504 : ℝ) with c7 | c7
  · refine ⟨18, 1 + 19 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c6, c7]
  rcases lt_or_ge (t - ⌊t⌋) (7197 / 118976 : ℝ) with c8 | c8
  · refine ⟨10, 1 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c7, c8]
  rcases lt_or_ge (t - ⌊t⌋) (443 / 6760 : ℝ) with c9 | c9
  · refine ⟨9, 1 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c8, c9]
  rcases lt_or_ge (t - ⌊t⌋) (5921 / 86528 : ℝ) with c10 | c10
  · refine ⟨23, 2 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c9, c10]
  rcases lt_or_ge (t - ⌊t⌋) (3375 / 43264 : ℝ) with c11 | c11
  · refine ⟨7, 1 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c10, c11]
  rcases lt_or_ge (t - ⌊t⌋) (1369 / 16224 : ℝ) with c12 | c12
  · refine ⟨11, 1 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c11, c12]
  rcases lt_or_ge (t - ⌊t⌋) (5121 / 54080 : ℝ) with c13 | c13
  · refine ⟨4, 1 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c12, c13]
  rcases lt_or_ge (t - ⌊t⌋) (1153 / 11648 : ℝ) with c14 | c14
  · refine ⟨13, 2 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c13, c14]
  rcases lt_or_ge (t - ⌊t⌋) (1189 / 10816 : ℝ) with c15 | c15
  · refine ⟨6, 1 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c14, c15]
  rcases lt_or_ge (t - ⌊t⌋) (4299 / 37856 : ℝ) with c16 | c16
  · refine ⟨20, 3 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c15, c16]
  rcases lt_or_ge (t - ⌊t⌋) (19 / 128 : ℝ) with c17 | c17
  · refine ⟨1, 1 + 2 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c16, c17]
  rcases lt_or_ge (t - ⌊t⌋) (725 / 4784 : ℝ) with c18 | c18
  · refine ⟨22, 4 + 23 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c17, c18]
  rcases lt_or_ge (t - ⌊t⌋) (801 / 5200 : ℝ) with c19 | c19
  · refine ⟨24, 4 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c18, c19]
  rcases lt_or_ge (t - ⌊t⌋) (3415 / 21632 : ℝ) with c20 | c20
  · refine ⟨19, 4 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c19, c20]
  rcases lt_or_ge (t - ⌊t⌋) (1119 / 6760 : ℝ) with c21 | c21
  · refine ⟨9, 2 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c20, c21]
  rcases lt_or_ge (t - ⌊t⌋) (1985 / 11648 : ℝ) with c22 | c22
  · refine ⟨13, 3 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c21, c22]
  rcases lt_or_ge (t - ⌊t⌋) (901 / 4992 : ℝ) with c23 | c23
  · refine ⟨5, 2 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c22, c23]
  rcases lt_or_ge (t - ⌊t⌋) (1501 / 8112 : ℝ) with c24 | c24
  · refine ⟨14, 3 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c23, c24]
  rcases lt_or_ge (t - ⌊t⌋) (36851 / 194688 : ℝ) with c25 | c25
  · refine ⟨17, 4 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c24, c25]
  rcases lt_or_ge (t - ⌊t⌋) (13655 / 70304 : ℝ) with c26 | c26
  · refine ⟨12, 3 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c25, c26]
  rcases lt_or_ge (t - ⌊t⌋) (8783 / 43264 : ℝ) with c27 | c27
  · refine ⟨7, 2 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c26, c27]
  rcases lt_or_ge (t - ⌊t⌋) (12237 / 59488 : ℝ) with c28 | c28
  · refine ⟨21, 5 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c27, c28]
  rcases lt_or_ge (t - ⌊t⌋) (23713 / 113568 : ℝ) with c29 | c29
  · refine ⟨20, 5 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c28, c29]
  rcases lt_or_ge (t - ⌊t⌋) (43573 / 205504 : ℝ) with c30 | c30
  · refine ⟨18, 4 + 19 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c29, c30]
  rcases lt_or_ge (t - ⌊t⌋) (409 / 1872 : ℝ) with c31 | c31
  · refine ⟨8, 2 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c30, c31]
  rcases lt_or_ge (t - ⌊t⌋) (729 / 3328 : ℝ) with c32 | c32
  · refine ⟨15, 4 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c31, c32]
  rcases lt_or_ge (t - ⌊t⌋) (5153 / 21632 : ℝ) with c33 | c33
  · refine ⟨3, 1 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c32, c33]
  rcases lt_or_ge (t - ⌊t⌋) (28829 / 118976 : ℝ) with c34 | c34
  · refine ⟨10, 3 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c33, c34]
  rcases lt_or_ge (t - ⌊t⌋) (19139 / 75712 : ℝ) with c35 | c35
  · refine ⟨6, 2 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c34, c35]
  rcases lt_or_ge (t - ⌊t⌋) (9707 / 37856 : ℝ) with c36 | c36
  · refine ⟨20, 6 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c35, c36]
  rcases lt_or_ge (t - ⌊t⌋) (27891 / 108160 : ℝ) with c37 | c37
  · refine ⟨19, 6 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c36, c37]
  rcases lt_or_ge (t - ⌊t⌋) (359 / 1352 : ℝ) with c38 | c38
  · refine ⟨9, 3 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c37, c38]
  rcases lt_or_ge (t - ⌊t⌋) (19063 / 70304 : ℝ) with c39 | c39
  · refine ⟨12, 4 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c38, c39]
  rcases lt_or_ge (t - ⌊t⌋) (57 / 208 : ℝ) with c40 | c40
  · refine ⟨24, 7 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c39, c40]
  rcases lt_or_ge (t - ⌊t⌋) (71843 / 259584 : ℝ) with c41 | c41
  · refine ⟨23, 7 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c40, c41]
  rcases lt_or_ge (t - ⌊t⌋) (937 / 3328 : ℝ) with c42 | c42
  · refine ⟨15, 5 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c41, c42]
  rcases lt_or_ge (t - ⌊t⌋) (15937 / 54080 : ℝ) with c43 | c43
  · refine ⟨4, 2 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c42, c43]
  rcases lt_or_ge (t - ⌊t⌋) (17645 / 59488 : ℝ) with c44 | c44
  · refine ⟨21, 7 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c43, c44]
  rcases lt_or_ge (t - ⌊t⌋) (58483 / 194688 : ℝ) with c45 | c45
  · refine ⟨17, 6 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c44, c45]
  rcases lt_or_ge (t - ⌊t⌋) (34529 / 113568 : ℝ) with c46 | c46
  · refine ⟨20, 7 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c45, c46]
  rcases lt_or_ge (t - ⌊t⌋) (33299 / 108160 : ℝ) with c47 | c47
  · refine ⟨19, 7 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c46, c47]
  rcases lt_or_ge (t - ⌊t⌋) (3649 / 11648 : ℝ) with c48 | c48
  · refine ⟨13, 5 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c47, c48]
  rcases lt_or_ge (t - ⌊t⌋) (12913 / 40560 : ℝ) with c49 | c49
  · refine ⟨14, 5 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c48, c49]
  rcases lt_or_ge (t - ⌊t⌋) (27553 / 86528 : ℝ) with c50 | c50
  · refine ⟨23, 8 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c49, c50]
  rcases lt_or_ge (t - ⌊t⌋) (14191 / 43264 : ℝ) with c51 | c51
  · refine ⟨7, 3 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c50, c51]
  rcases lt_or_ge (t - ⌊t⌋) (5425 / 16224 : ℝ) with c52 | c52
  · refine ⟨11, 4 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c51, c52]
  rcases lt_or_ge (t - ⌊t⌋) (1733 / 4992 : ℝ) with c53 | c53
  · refine ⟨5, 3 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c52, c53]
  rcases lt_or_ge (t - ⌊t⌋) (24471 / 70304 : ℝ) with c54 | c54
  · refine ⟨12, 5 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c53, c54]
  rcases lt_or_ge (t - ⌊t⌋) (39937 / 113568 : ℝ) with c55 | c55
  · refine ⟨20, 8 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c54, c55]
  rcases lt_or_ge (t - ⌊t⌋) (1841 / 5200 : ℝ) with c56 | c56
  · refine ⟨24, 9 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c55, c56]
  rcases lt_or_ge (t - ⌊t⌋) (38707 / 108160 : ℝ) with c57 | c57
  · refine ⟨19, 8 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c56, c57]
  rcases lt_or_ge (t - ⌊t⌋) (2055 / 5408 : ℝ) with c58 | c58
  · refine ⟨2, 2 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c57, c58]
  rcases lt_or_ge (t - ⌊t⌋) (15617 / 40560 : ℝ) with c59 | c59
  · refine ⟨14, 6 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c58, c59]
  rcases lt_or_ge (t - ⌊t⌋) (29955 / 75712 : ℝ) with c60 | c60
  · refine ⟨6, 3 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c59, c60]
  rcases lt_or_ge (t - ⌊t⌋) (15115 / 37856 : ℝ) with c61 | c61
  · refine ⟨20, 9 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c60, c61]
  rcases lt_or_ge (t - ⌊t⌋) (104291 / 259584 : ℝ) with c62 | c62
  · refine ⟨23, 10 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c61, c62]
  rcases lt_or_ge (t - ⌊t⌋) (1353 / 3328 : ℝ) with c63 | c63
  · refine ⟨15, 7 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c62, c63]
  rcases lt_or_ge (t - ⌊t⌋) (8823 / 21632 : ℝ) with c64 | c64
  · refine ⟨19, 9 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c63, c64]
  rcases lt_or_ge (t - ⌊t⌋) (26705 / 64896 : ℝ) with c65 | c65
  · refine ⟨17, 8 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c64, c65]
  rcases lt_or_ge (t - ⌊t⌋) (2259 / 5408 : ℝ) with c66 | c66
  · refine ⟨11, 5 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c65, c66]
  rcases lt_or_ge (t - ⌊t⌋) (50461 / 118976 : ℝ) with c67 | c67
  · refine ⟨10, 5 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c66, c67]
  rcases lt_or_ge (t - ⌊t⌋) (29879 / 70304 : ℝ) with c68 | c68
  · refine ⟨12, 6 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c67, c68]
  rcases lt_or_ge (t - ⌊t⌋) (78973 / 183872 : ℝ) with c69 | c69
  · refine ⟨16, 8 + 17 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c68, c69]
  rcases lt_or_ge (t - ⌊t⌋) (25757 / 59488 : ℝ) with c70 | c70
  · refine ⟨21, 10 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c69, c70]
  rcases lt_or_ge (t - ⌊t⌋) (275 / 624 : ℝ) with c71 | c71
  · refine ⟨8, 4 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c70, c71]
  rcases lt_or_ge (t - ⌊t⌋) (38369 / 86528 : ℝ) with c72 | c72
  · refine ⟨23, 11 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c71, c72]
  rcases lt_or_ge (t - ⌊t⌋) (19599 / 43264 : ℝ) with c73 | c73
  · refine ⟨7, 4 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c72, c73]
  rcases lt_or_ge (t - ⌊t⌋) (759 / 1664 : ℝ) with c74 | c74
  · refine ⟨13, 7 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c73, c74]
  rcases lt_or_ge (t - ⌊t⌋) (49523 / 108160 : ℝ) with c75 | c75
  · refine ⟨19, 10 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c74, c75]
  rcases lt_or_ge (t - ⌊t⌋) (3147 / 6760 : ℝ) with c76 | c76
  · refine ⟨9, 5 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c75, c76]
  rcases lt_or_ge (t - ⌊t⌋) (1561 / 3328 : ℝ) with c77 | c77
  · refine ⟨15, 8 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c76, c77]
  rcases lt_or_ge (t - ⌊t⌋) (10561 / 21632 : ℝ) with c78 | c78
  · refine ⟨3, 2 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c77, c78]
  rcases lt_or_ge (t - ⌊t⌋) (26753 / 54080 : ℝ) with c79 | c79
  · refine ⟨4, 3 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c78, c79]
  rcases lt_or_ge (t - ⌊t⌋) (8129 / 16224 : ℝ) with c80 | c80
  · refine ⟨11, 6 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c79, c80]
  rcases lt_or_ge (t - ⌊t⌋) (855 / 1664 : ℝ) with c81 | c81
  · refine ⟨5, 4 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c80, c81]
  rcases lt_or_ge (t - ⌊t⌋) (4205 / 8112 : ℝ) with c82 | c82
  · refine ⟨14, 8 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c81, c82]
  rcases lt_or_ge (t - ⌊t⌋) (101747 / 194688 : ℝ) with c83 | c83
  · refine ⟨17, 10 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c82, c83]
  rcases lt_or_ge (t - ⌊t⌋) (6145 / 11648 : ℝ) with c84 | c84
  · refine ⟨13, 8 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c83, c84]
  rcases lt_or_ge (t - ⌊t⌋) (40771 / 75712 : ℝ) with c85 | c85
  · refine ⟨6, 4 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c84, c85]
  rcases lt_or_ge (t - ⌊t⌋) (20523 / 37856 : ℝ) with c86 | c86
  · refine ⟨20, 12 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c85, c86]
  rcases lt_or_ge (t - ⌊t⌋) (2597 / 4784 : ℝ) with c87 | c87
  · refine ⟨22, 13 + 23 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c86, c87]
  rcases lt_or_ge (t - ⌊t⌋) (100605 / 183872 : ℝ) with c88 | c88
  · refine ⟨16, 10 + 17 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c87, c88]
  rcases lt_or_ge (t - ⌊t⌋) (1033 / 1872 : ℝ) with c89 | c89
  · refine ⟨8, 5 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c88, c89]
  rcases lt_or_ge (t - ⌊t⌋) (2881 / 5200 : ℝ) with c90 | c90
  · refine ⟨24, 14 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c89, c90]
  rcases lt_or_ge (t - ⌊t⌋) (60339 / 108160 : ℝ) with c91 | c91
  · refine ⟨19, 12 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c90, c91]
  rcases lt_or_ge (t - ⌊t⌋) (3823 / 6760 : ℝ) with c92 | c92
  · refine ⟨9, 6 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c91, c92]
  rcases lt_or_ge (t - ⌊t⌋) (49185 / 86528 : ℝ) with c93 | c93
  · refine ⟨23, 14 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c92, c93]
  rcases lt_or_ge (t - ⌊t⌋) (25007 / 43264 : ℝ) with c94 | c94
  · refine ⟨7, 5 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c93, c94]
  rcases lt_or_ge (t - ⌊t⌋) (9481 / 16224 : ℝ) with c95 | c95
  · refine ⟨11, 7 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c94, c95]
  rcases lt_or_ge (t - ⌊t⌋) (2805 / 4784 : ℝ) with c96 | c96
  · refine ⟨22, 14 + 23 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c95, c96]
  rcases lt_or_ge (t - ⌊t⌋) (66977 / 113568 : ℝ) with c97 | c97
  · refine ⟨20, 13 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c96, c97]
  rcases lt_or_ge (t - ⌊t⌋) (1977 / 3328 : ℝ) with c98 | c98
  · refine ⟨15, 10 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c97, c98]
  rcases lt_or_ge (t - ⌊t⌋) (6977 / 11648 : ℝ) with c99 | c99
  · refine ⟨13, 9 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c98, c99]
  rcases lt_or_ge (t - ⌊t⌋) (72093 / 118976 : ℝ) with c100 | c100
  · refine ⟨10, 7 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c99, c100]
  rcases lt_or_ge (t - ⌊t⌋) (65747 / 108160 : ℝ) with c101 | c101
  · refine ⟨19, 13 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c100, c101]
  rcases lt_or_ge (t - ⌊t⌋) (158371 / 259584 : ℝ) with c102 | c102
  · refine ⟨23, 15 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c101, c102]
  rcases lt_or_ge (t - ⌊t⌋) (83 / 128 : ℝ) with c103 | c103
  · refine ⟨1, 2 + 2 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c102, c103]
  rcases lt_or_ge (t - ⌊t⌋) (8811 / 13520 : ℝ) with c104 | c104
  · refine ⟨14, 10 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c103, c104]
  rcases lt_or_ge (t - ⌊t⌋) (46103 / 70304 : ℝ) with c105 | c105
  · refine ⟨12, 9 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c104, c105]
  rcases lt_or_ge (t - ⌊t⌋) (1241 / 1872 : ℝ) with c106 | c106
  · refine ⟨8, 6 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c105, c106]
  rcases lt_or_ge (t - ⌊t⌋) (3611 / 5408 : ℝ) with c107 | c107
  · refine ⟨11, 8 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c106, c107]
  rcases lt_or_ge (t - ⌊t⌋) (3397 / 4992 : ℝ) with c108 | c108
  · refine ⟨5, 5 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c107, c108]
  rcases lt_or_ge (t - ⌊t⌋) (37569 / 54080 : ℝ) with c109 | c109
  · refine ⟨4, 4 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c108, c109]
  rcases lt_or_ge (t - ⌊t⌋) (11573 / 16224 : ℝ) with c110 | c110
  · refine ⟨2, 3 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c109, c110]
  rcases lt_or_ge (t - ⌊t⌋) (29137 / 40560 : ℝ) with c111 | c111
  · refine ⟨14, 11 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c110, c111]
  rcases lt_or_ge (t - ⌊t⌋) (2393 / 3328 : ℝ) with c112 | c112
  · refine ⟨15, 12 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c111, c112]
  rcases lt_or_ge (t - ⌊t⌋) (15969 / 21632 : ℝ) with c113 | c113
  · refine ⟨3, 3 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c112, c113]
  rcases lt_or_ge (t - ⌊t⌋) (8641 / 11648 : ℝ) with c114 | c114
  · refine ⟨13, 11 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c113, c114]
  rcases lt_or_ge (t - ⌊t⌋) (48337 / 64896 : ℝ) with c115 | c115
  · refine ⟨17, 14 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c114, c115]
  rcases lt_or_ge (t - ⌊t⌋) (12185 / 16224 : ℝ) with c116 | c116
  · refine ⟨11, 9 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c115, c116]
  rcases lt_or_ge (t - ⌊t⌋) (3921 / 5200 : ℝ) with c117 | c117
  · refine ⟨24, 19 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c116, c117]
  rcases lt_or_ge (t - ⌊t⌋) (81971 / 108160 : ℝ) with c118 | c118
  · refine ⟨19, 16 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c117, c118]
  rcases lt_or_ge (t - ⌊t⌋) (1035 / 1352 : ℝ) with c119 | c119
  · refine ⟨9, 8 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c118, c119]
  rcases lt_or_ge (t - ⌊t⌋) (161 / 208 : ℝ) with c120 | c120
  · refine ⟨8, 7 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c119, c120]
  rcases lt_or_ge (t - ⌊t⌋) (201635 / 259584 : ℝ) with c121 | c121
  · refine ⟨23, 19 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c120, c121]
  rcases lt_or_ge (t - ⌊t⌋) (2601 / 3328 : ℝ) with c122 | c122
  · refine ⟨15, 13 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c121, c122]
  rcases lt_or_ge (t - ⌊t⌋) (93725 / 118976 : ℝ) with c123 | c123
  · refine ⟨10, 9 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c122, c123]
  rcases lt_or_ge (t - ⌊t⌋) (162549 / 205504 : ℝ) with c124 | c124
  · refine ⟨18, 15 + 19 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c123, c124]
  rcases lt_or_ge (t - ⌊t⌋) (4129 / 5200 : ℝ) with c125 | c125
  · refine ⟨24, 20 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c124, c125]
  rcases lt_or_ge (t - ⌊t⌋) (47389 / 59488 : ℝ) with c126 | c126
  · refine ⟨21, 18 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c125, c126]
  rcases lt_or_ge (t - ⌊t⌋) (155827 / 194688 : ℝ) with c127 | c127
  · refine ⟨17, 15 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c126, c127]
  rcases lt_or_ge (t - ⌊t⌋) (3845 / 4784 : ℝ) with c128 | c128
  · refine ⟨22, 19 + 23 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c127, c128]
  rcases lt_or_ge (t - ⌊t⌋) (56919 / 70304 : ℝ) with c129 | c129
  · refine ⟨12, 11 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c128, c129]
  rcases lt_or_ge (t - ⌊t⌋) (9473 / 11648 : ℝ) with c130 | c130
  · refine ⟨13, 12 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c129, c130]
  rcases lt_or_ge (t - ⌊t⌋) (62403 / 75712 : ℝ) with c131 | c131
  · refine ⟨6, 6 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c130, c131]
  rcases lt_or_ge (t - ⌊t⌋) (35823 / 43264 : ℝ) with c132 | c132
  · refine ⟨7, 7 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c131, c132]
  rcases lt_or_ge (t - ⌊t⌋) (13537 / 16224 : ℝ) with c133 | c133
  · refine ⟨11, 10 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c132, c133]
  rcases lt_or_ge (t - ⌊t⌋) (4229 / 4992 : ℝ) with c134 | c134
  · refine ⟨5, 6 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c133, c134]
  rcases lt_or_ge (t - ⌊t⌋) (2303 / 2704 : ℝ) with c135 | c135
  · refine ⟨14, 13 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c134, c135]
  rcases lt_or_ge (t - ⌊t⌋) (166643 / 194688 : ℝ) with c136 | c136
  · refine ⟨17, 16 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c135, c136]
  rcases lt_or_ge (t - ⌊t⌋) (92787 / 108160 : ℝ) with c137 | c137
  · refine ⟨19, 18 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c136, c137]
  rcases lt_or_ge (t - ⌊t⌋) (5851 / 6760 : ℝ) with c138 | c138
  · refine ⟨9, 9 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c137, c138]
  rcases lt_or_ge (t - ⌊t⌋) (10191 / 10816 : ℝ) with c139 | c139
  · refine ⟨0, 1 + 1 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c138, c139]
  rcases lt_or_ge (t - ⌊t⌋) (81633 / 86528 : ℝ) with c140 | c140
  · refine ⟨23, 23 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c139, c140]
  rcases lt_or_ge (t - ⌊t⌋) (41231 / 43264 : ℝ) with c141 | c141
  · refine ⟨7, 8 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c140, c141]
  rcases lt_or_ge (t - ⌊t⌋) (1591 / 1664 : ℝ) with c142 | c142
  · refine ⟨13, 14 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c141, c142]
  rcases lt_or_ge (t - ⌊t⌋) (73219 / 75712 : ℝ) with c143 | c143
  · refine ⟨6, 7 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c142, c143]
  rcases lt_or_ge (t - ⌊t⌋) (36747 / 37856 : ℝ) with c144 | c144
  · refine ⟨20, 21 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c143, c144]
  rcases lt_or_ge (t - ⌊t⌋) (21377 / 21632 : ℝ) with c145 | c145
  · refine ⟨3, 4 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c144, c145]
  rcases lt_or_ge (t - ⌊t⌋) (1865 / 1872 : ℝ) with c146 | c146
  · refine ⟨8, 9 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c145, c146]
  refine ⟨11, 12 + 12 * ⌊t⌋, ?_⟩
  simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
  rw [abs_lt]
  push_cast
  constructor <;> linarith only [c146, h1]

#print axioms cover
#print axioms v_injective
#print axioms v_pos
end SLRAudit.N25
