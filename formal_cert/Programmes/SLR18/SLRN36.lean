import Mathlib.Tactic

set_option linter.unusedSimpArgs false
set_option maxHeartbeats 0
namespace SLRAudit.N36

/-- velocities of certificate n = 36 -/
def v : Fin 36 → ℕ := ![1, 2, 3, 60, 5, 6, 7, 8, 9, 21, 11, 12, 13, 14, 15, 16, 40, 18, 10, 25, 65, 22, 20, 24, 48, 4, 27, 28, 38, 30, 32, 34, 72, 31, 54, 36]
/-- shifts s_i = a_i / 21904 -/
def s : Fin 36 → ℚ := ![949/21904, 3661/21904, 12315/21904, 20952/21904, 15123/21904, 16343/21904, 19432/21904, 21108/21904, 20419/21904, 8775/21904, 18423/21904, 18041/21904, 19083/21904, 18669/21904, 8421/21904, 1010/21904, 4281/21904, 207/21904, 1808/21904, 639/21904, 17359/21904, 5433/21904, 5411/21904, 4779/21904, 11328/21904, 19408/21904, 12489/21904, 214/21904, 11757/21904, 20543/21904, 10412/21904, 3556/21904, 8915/21904, 16454/21904, 9026/21904, 5343/21904]

theorem v_injective : Function.Injective v := by decide
theorem v_pos : ∀ i, 0 < v i := by decide

/-- covering: for every real t some runner is within distance < 1/37 of an integer. -/
theorem cover : ∀ t : ℝ, ∃ i : Fin 36, ∃ k : ℤ, |((s i : ℚ) : ℝ) + ((v i : ℕ) : ℝ) * t - (k : ℝ)| < 1 / 37 := by
  intro t
  have h0 : (0 : ℝ) ≤ t - ⌊t⌋ := by have := Int.floor_le t; linarith
  have h1 : t - ⌊t⌋ < (1 : ℝ) := by have := Int.lt_floor_add_one t; linarith
  rcases lt_or_ge (t - ⌊t⌋) (385 / 394272 : ℝ) with c0 | c0
  · refine ⟨17, 0 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [h0, c0]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 164280 : ℝ) with c1 | c1
  · refine ⟨3, 1 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c0, c1]
  rcases lt_or_ge (t - ⌊t⌋) (347 / 43808 : ℝ) with c2 | c2
  · refine ⟨7, 1 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1, c2]
  rcases lt_or_ge (t - ⌊t⌋) (3413 / 284752 : ℝ) with c3 | c3
  · refine ⟨12, 1 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2, c3]
  rcases lt_or_ge (t - ⌊t⌋) (10739 / 832352 : ℝ) with c4 | c4
  · refine ⟨28, 1 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c3, c4]
  rcases lt_or_ge (t - ⌊t⌋) (383 / 19166 : ℝ) with c5 | c5
  · refine ⟨6, 1 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c4, c5]
  rcases lt_or_ge (t - ⌊t⌋) (3643 / 175232 : ℝ) with c6 | c6
  · refine ⟨16, 1 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c5, c6]
  rcases lt_or_ge (t - ⌊t⌋) (17153 / 788544 : ℝ) with c7 | c7
  · refine ⟨35, 1 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c6, c7]
  rcases lt_or_ge (t - ⌊t⌋) (193 / 5476 : ℝ) with c8 | c8
  · refine ⟨25, 1 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c7, c8]
  rcases lt_or_ge (t - ⌊t⌋) (11141 / 306656 : ℝ) with c9 | c9
  · refine ⟨27, 1 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c8, c9]
  rcases lt_or_ge (t - ⌊t⌋) (3417 / 87616 : ℝ) with c10 | c10
  · refine ⟨22, 1 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c9, c10]
  rcases lt_or_ge (t - ⌊t⌋) (2051 / 43808 : ℝ) with c11 | c11
  · refine ⟨5, 1 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c10, c11]
  rcases lt_or_ge (t - ⌊t⌋) (8497 / 175232 : ℝ) with c12 | c12
  · refine ⟨30, 2 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c11, c12]
  rcases lt_or_ge (t - ⌊t⌋) (13019 / 262848 : ℝ) with c13 | c13
  · refine ⟨35, 2 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c12, c13]
  rcases lt_or_ge (t - ⌊t⌋) (26431 / 525696 : ℝ) with c14 | c14
  · refine ⟨32, 4 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c13, c14]
  rcases lt_or_ge (t - ⌊t⌋) (8407 / 164280 : ℝ) with c15 | c15
  · refine ⟨3, 4 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c14, c15]
  rcases lt_or_ge (t - ⌊t⌋) (859 / 16428 : ℝ) with c16 | c16
  · refine ⟨24, 3 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c15, c16]
  rcases lt_or_ge (t - ⌊t⌋) (10637 / 197136 : ℝ) with c17 | c17
  · refine ⟨26, 2 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c16, c17]
  rcases lt_or_ge (t - ⌊t⌋) (22289 / 394272 : ℝ) with c18 | c18
  · refine ⟨17, 1 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c17, c18]
  rcases lt_or_ge (t - ⌊t⌋) (7373 / 109520 : ℝ) with c19 | c19
  · refine ⟨4, 1 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c18, c19]
  rcases lt_or_ge (t - ⌊t⌋) (743 / 10952 : ℝ) with c20 | c20
  · refine ⟨3, 5 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c19, c20]
  rcases lt_or_ge (t - ⌊t⌋) (45761 / 657120 : ℝ) with c21 | c21
  · refine ⟨29, 3 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c20, c21]
  rcases lt_or_ge (t - ⌊t⌋) (62023 / 876160 : ℝ) with c22 | c22
  · refine ⟨16, 3 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c21, c22]
  rcases lt_or_ge (t - ⌊t⌋) (22093 / 306656 : ℝ) with c23 | c23
  · refine ⟨27, 2 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c22, c23]
  rcases lt_or_ge (t - ⌊t⌋) (24925 / 339512 : ℝ) with c24 | c24
  · refine ⟨33, 3 + 31 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c23, c24]
  rcases lt_or_ge (t - ⌊t⌋) (13207 / 175232 : ℝ) with c25 | c25
  · refine ⟨23, 2 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c24, c25]
  rcases lt_or_ge (t - ⌊t⌋) (11875 / 153328 : ℝ) with c26 | c26
  · refine ⟨9, 2 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c25, c26]
  rcases lt_or_ge (t - ⌊t⌋) (123101 / 1577088 : ℝ) with c27 | c27
  · refine ⟨32, 6 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c26, c27]
  rcases lt_or_ge (t - ⌊t⌋) (43761 / 547600 : ℝ) with c28 | c28
  · refine ⟨19, 2 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c27, c28]
  rcases lt_or_ge (t - ⌊t⌋) (38967 / 481888 : ℝ) with c29 | c29
  · refine ⟨21, 2 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c28, c29]
  rcases lt_or_ge (t - ⌊t⌋) (25731 / 306656 : ℝ) with c30 | c30
  · refine ⟨13, 2 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c29, c30]
  rcases lt_or_ge (t - ⌊t⌋) (13883 / 164280 : ℝ) with c31 | c31
  · refine ⟨3, 6 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c30, c31]
  rcases lt_or_ge (t - ⌊t⌋) (50543 / 591408 : ℝ) with c32 | c32
  · refine ⟨34, 5 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c31, c32]
  rcases lt_or_ge (t - ⌊t⌋) (25317 / 284752 : ℝ) with c33 | c33
  · refine ⟨12, 2 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c32, c33]
  rcases lt_or_ge (t - ⌊t⌋) (38989 / 438080 : ℝ) with c34 | c34
  · refine ⟨22, 2 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c33, c34]
  rcases lt_or_ge (t - ⌊t⌋) (53815 / 591408 : ℝ) with c35 | c35
  · refine ⟨26, 3 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c34, c35]
  rcases lt_or_ge (t - ⌊t⌋) (1293 / 13690 : ℝ) with c36 | c36
  · refine ⟨18, 1 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c35, c36]
  rcases lt_or_ge (t - ⌊t⌋) (83927 / 876160 : ℝ) with c37 | c37
  · refine ⟨16, 4 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c36, c37]
  rcases lt_or_ge (t - ⌊t⌋) (26359 / 262848 : ℝ) with c38 | c38
  · refine ⟨11, 2 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c37, c38]
  rcases lt_or_ge (t - ⌊t⌋) (16621 / 164280 : ℝ) with c39 | c39
  · refine ⟨3, 7 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c38, c39]
  rcases lt_or_ge (t - ⌊t⌋) (4511 / 43808 : ℝ) with c40 | c40
  · refine ⟨29, 4 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c39, c40]
  rcases lt_or_ge (t - ⌊t⌋) (25977 / 240944 : ℝ) with c41 | c41
  · refine ⟨10, 2 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c40, c41]
  rcases lt_or_ge (t - ⌊t⌋) (11993 / 109520 : ℝ) with c42 | c42
  · refine ⟨14, 2 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c41, c42]
  rcases lt_or_ge (t - ⌊t⌋) (14731 / 131424 : ℝ) with c43 | c43
  · refine ⟨17, 2 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c42, c43]
  rcases lt_or_ge (t - ⌊t⌋) (21163 / 186184 : ℝ) with c44 | c44
  · refine ⟨31, 4 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c43, c44]
  rcases lt_or_ge (t - ⌊t⌋) (7543 / 65712 : ℝ) with c45 | c45
  · refine ⟨24, 6 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c44, c45]
  rcases lt_or_ge (t - ⌊t⌋) (61525 / 525696 : ℝ) with c46 | c46
  · refine ⟨23, 3 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c45, c46]
  rcases lt_or_ge (t - ⌊t⌋) (23981 / 197136 : ℝ) with c47 | c47
  · refine ⟨8, 2 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c46, c47]
  rcases lt_or_ge (t - ⌊t⌋) (21695 / 175232 : ℝ) with c48 | c48
  · refine ⟨15, 2 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c47, c48]
  rcases lt_or_ge (t - ⌊t⌋) (57529 / 459984 : ℝ) with c49 | c49
  · refine ⟨9, 3 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c48, c49]
  rcases lt_or_ge (t - ⌊t⌋) (60871 / 481888 : ℝ) with c50 | c50
  · refine ⟨21, 3 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c49, c50]
  rcases lt_or_ge (t - ⌊t⌋) (5823 / 43808 : ℝ) with c51 | c51
  · refine ⟨7, 2 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c50, c51]
  rcases lt_or_ge (t - ⌊t⌋) (23413 / 175232 : ℝ) with c52 | c52
  · refine ⟨32, 10 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c51, c52]
  rcases lt_or_ge (t - ⌊t⌋) (22097 / 164280 : ℝ) with c53 | c53
  · refine ⟨3, 9 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c52, c53]
  rcases lt_or_ge (t - ⌊t⌋) (89569 / 657120 : ℝ) with c54 | c54
  · refine ⟨29, 5 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c53, c54]
  rcases lt_or_ge (t - ⌊t⌋) (60893 / 438080 : ℝ) with c55 | c55
  · refine ⟨22, 3 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c54, c55]
  rcases lt_or_ge (t - ⌊t⌋) (10181 / 65712 : ℝ) with c56 | c56
  · refine ⟨2, 1 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c55, c56]
  rcases lt_or_ge (t - ⌊t⌋) (6805 / 43808 : ℝ) with c57 | c57
  · refine ⟨13, 3 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c56, c57]
  rcases lt_or_ge (t - ⌊t⌋) (3121 / 19166 : ℝ) with c58 | c58
  · refine ⟨6, 2 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c57, c58]
  rcases lt_or_ge (t - ⌊t⌋) (47221 / 284752 : ℝ) with c59 | c59
  · refine ⟨12, 3 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c58, c59]
  rcases lt_or_ge (t - ⌊t⌋) (66097 / 394272 : ℝ) with c60 | c60
  · refine ⟨17, 3 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c59, c60]
  rcases lt_or_ge (t - ⌊t⌋) (9191 / 54760 : ℝ) with c61 | c61
  · refine ⟨3, 11 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c60, c61]
  rcases lt_or_ge (t - ⌊t⌋) (111473 / 657120 : ℝ) with c62 | c62
  · refine ⟨29, 6 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c61, c62]
  rcases lt_or_ge (t - ⌊t⌋) (7525 / 43808 : ℝ) with c63 | c63
  · refine ⟨21, 4 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c62, c63]
  rcases lt_or_ge (t - ⌊t⌋) (79433 / 459984 : ℝ) with c64 | c64
  · refine ⟨9, 4 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c63, c64]
  rcases lt_or_ge (t - ⌊t⌋) (57883 / 328560 : ℝ) with c65 | c65
  · refine ⟨14, 3 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c64, c65]
  rcases lt_or_ge (t - ⌊t⌋) (5825 / 32856 : ℝ) with c66 | c66
  · refine ⟨24, 9 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c65, c66]
  rcases lt_or_ge (t - ⌊t⌋) (54949 / 306656 : ℝ) with c67 | c67
  · refine ⟨27, 5 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c66, c67]
  rcases lt_or_ge (t - ⌊t⌋) (48263 / 262848 : ℝ) with c68 | c68
  · refine ⟨11, 3 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c67, c68]
  rcases lt_or_ge (t - ⌊t⌋) (32647 / 175232 : ℝ) with c69 | c69
  · refine ⟨15, 3 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c68, c69]
  rcases lt_or_ge (t - ⌊t⌋) (82797 / 438080 : ℝ) with c70 | c70
  · refine ⟨22, 4 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c69, c70]
  rcases lt_or_ge (t - ⌊t⌋) (298333 / 1577088 : ℝ) with c71 | c71
  · refine ⟨32, 14 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c70, c71]
  rcases lt_or_ge (t - ⌊t⌋) (1331 / 6845 : ℝ) with c72 | c72
  · refine ⟨18, 2 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c71, c72]
  rcases lt_or_ge (t - ⌊t⌋) (47881 / 240944 : ℝ) with c73 | c73
  · refine ⟨10, 3 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c72, c73]
  rcases lt_or_ge (t - ⌊t⌋) (35111 / 175232 : ℝ) with c74 | c74
  · refine ⟨23, 5 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c73, c74]
  rcases lt_or_ge (t - ⌊t⌋) (119527 / 591408 : ℝ) with c75 | c75
  · refine ⟨26, 6 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c74, c75]
  rcases lt_or_ge (t - ⌊t⌋) (44459 / 219040 : ℝ) with c76 | c76
  · refine ⟨29, 7 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c75, c76]
  rcases lt_or_ge (t - ⌊t⌋) (289889 / 1423760 : ℝ) with c77 | c77
  · refine ⟨20, 14 + 65 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c76, c77]
  rcases lt_or_ge (t - ⌊t⌋) (35877 / 175232 : ℝ) with c78 | c78
  · refine ⟨30, 7 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c77, c78]
  rcases lt_or_ge (t - ⌊t⌋) (28057 / 131424 : ℝ) with c79 | c79
  · refine ⟨5, 2 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c78, c79]
  rcases lt_or_ge (t - ⌊t⌋) (65901 / 306656 : ℝ) with c80 | c80
  · refine ⟨27, 6 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c79, c80]
  rcases lt_or_ge (t - ⌊t⌋) (104679 / 481888 : ℝ) with c81 | c81
  · refine ⟨21, 5 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c80, c81]
  rcases lt_or_ge (t - ⌊t⌋) (11929 / 54760 : ℝ) with c82 | c82
  · refine ⟨3, 14 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c81, c82]
  rcases lt_or_ge (t - ⌊t⌋) (33779 / 153328 : ℝ) with c83 | c83
  · refine ⟨9, 5 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c82, c83]
  rcases lt_or_ge (t - ⌊t⌋) (88001 / 394272 : ℝ) with c84 | c84
  · refine ⟨17, 4 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c83, c84]
  rcases lt_or_ge (t - ⌊t⌋) (69539 / 306656 : ℝ) with c85 | c85
  · refine ⟨13, 4 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c84, c85]
  rcases lt_or_ge (t - ⌊t⌋) (15295 / 65712 : ℝ) with c86 | c86
  · refine ⟨8, 3 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c85, c86]
  rcases lt_or_ge (t - ⌊t⌋) (5117 / 21904 : ℝ) with c87 | c87
  · refine ⟨34, 13 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c86, c87]
  rcases lt_or_ge (t - ⌊t⌋) (79685 / 339512 : ℝ) with c88 | c88
  · refine ⟨33, 8 + 31 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c87, c88]
  rcases lt_or_ge (t - ⌊t⌋) (155281 / 657120 : ℝ) with c89 | c89
  · refine ⟨29, 8 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c88, c89]
  rcases lt_or_ge (t - ⌊t⌋) (104701 / 438080 : ℝ) with c90 | c90
  · refine ⟨22, 5 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c89, c90]
  rcases lt_or_ge (t - ⌊t⌋) (69125 / 284752 : ℝ) with c91 | c91
  · refine ⟨12, 4 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c90, c91]
  rcases lt_or_ge (t - ⌊t⌋) (192385 / 788544 : ℝ) with c92 | c92
  · refine ⟨35, 9 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c91, c92]
  rcases lt_or_ge (t - ⌊t⌋) (385949 / 1577088 : ℝ) with c93 | c93
  · refine ⟨32, 18 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c92, c93]
  rcases lt_or_ge (t - ⌊t⌋) (215351 / 876160 : ℝ) with c94 | c94
  · refine ⟨16, 10 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c93, c94]
  rcases lt_or_ge (t - ⌊t⌋) (43599 / 175232 : ℝ) with c95 | c95
  · refine ⟨15, 4 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c94, c95]
  rcases lt_or_ge (t - ⌊t⌋) (10979 / 43808 : ℝ) with c96 | c96
  · refine ⟨27, 7 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c95, c96]
  rcases lt_or_ge (t - ⌊t⌋) (41263 / 164280 : ℝ) with c97 | c97
  · refine ⟨3, 16 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c96, c97]
  rcases lt_or_ge (t - ⌊t⌋) (11299 / 43808 : ℝ) with c98 | c98
  · refine ⟨7, 3 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c97, c98]
  rcases lt_or_ge (t - ⌊t⌋) (29277 / 109520 : ℝ) with c99 | c99
  · refine ⟨4, 2 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c98, c99]
  rcases lt_or_ge (t - ⌊t⌋) (123241 / 459984 : ℝ) with c100 | c100
  · refine ⟨9, 6 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c99, c100]
  rcases lt_or_ge (t - ⌊t⌋) (35437 / 131424 : ℝ) with c101 | c101
  · refine ⟨29, 9 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c100, c101]
  rcases lt_or_ge (t - ⌊t⌋) (47451 / 175232 : ℝ) with c102 | c102
  · refine ⟨16, 11 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c101, c102]
  rcases lt_or_ge (t - ⌊t⌋) (214289 / 788544 : ℝ) with c103 | c103
  · refine ⟨35, 10 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c102, c103]
  rcases lt_or_ge (t - ⌊t⌋) (781 / 2738 : ℝ) with c104 | c104
  · refine ⟨25, 2 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c103, c104]
  rcases lt_or_ge (t - ⌊t⌋) (69785 / 240944 : ℝ) with c105 | c105
  · refine ⟨10, 4 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c104, c105]
  rcases lt_or_ge (t - ⌊t⌋) (4031 / 13690 : ℝ) with c106 | c106
  · refine ⟨18, 3 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c105, c106]
  rcases lt_or_ge (t - ⌊t⌋) (91443 / 306656 : ℝ) with c107 | c107
  · refine ⟨13, 5 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c106, c107]
  rcases lt_or_ge (t - ⌊t⌋) (837 / 2738 : ℝ) with c108 | c108
  · refine ⟨6, 3 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c107, c108]
  rcases lt_or_ge (t - ⌊t⌋) (148487 / 481888 : ℝ) with c109 | c109
  · refine ⟨21, 7 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c108, c109]
  rcases lt_or_ge (t - ⌊t⌋) (54551 / 175232 : ℝ) with c110 | c110
  · refine ⟨15, 5 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c109, c110]
  rcases lt_or_ge (t - ⌊t⌋) (185239 / 591408 : ℝ) with c111 | c111
  · refine ⟨26, 9 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c110, c111]
  rcases lt_or_ge (t - ⌊t⌋) (20735 / 65712 : ℝ) with c112 | c112
  · refine ⟨9, 7 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c111, c112]
  rcases lt_or_ge (t - ⌊t⌋) (91029 / 284752 : ℝ) with c113 | c113
  · refine ⟨12, 5 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c112, c113]
  rcases lt_or_ge (t - ⌊t⌋) (281063 / 876160 : ℝ) with c114 | c114
  · refine ⟨16, 13 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c113, c114]
  rcases lt_or_ge (t - ⌊t⌋) (98757 / 306656 : ℝ) with c115 | c115
  · refine ⟨27, 9 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c114, c115]
  rcases lt_or_ge (t - ⌊t⌋) (21233 / 65712 : ℝ) with c116 | c116
  · refine ⟨24, 16 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c115, c116]
  rcases lt_or_ge (t - ⌊t⌋) (57015 / 175232 : ℝ) with c117 | c117
  · refine ⟨23, 8 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c116, c117]
  rcases lt_or_ge (t - ⌊t⌋) (192919 / 591408 : ℝ) with c118 | c118
  · refine ⟨34, 18 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c117, c118]
  rcases lt_or_ge (t - ⌊t⌋) (258097 / 788544 : ℝ) with c119 | c119
  · refine ⟨35, 12 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c118, c119]
  rcases lt_or_ge (t - ⌊t⌋) (273587 / 832352 : ℝ) with c120 | c120
  · refine ⟨28, 13 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c119, c120]
  rcases lt_or_ge (t - ⌊t⌋) (57781 / 175232 : ℝ) with c121 | c121
  · refine ⟨30, 11 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c120, c121]
  rcases lt_or_ge (t - ⌊t⌋) (112541 / 339512 : ℝ) with c122 | c122
  · refine ⟨33, 11 + 31 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c121, c122]
  rcases lt_or_ge (t - ⌊t⌋) (131809 / 394272 : ℝ) with c123 | c123
  · refine ⟨17, 6 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c122, c123]
  rcases lt_or_ge (t - ⌊t⌋) (54953 / 164280 : ℝ) with c124 | c124
  · refine ⟨3, 21 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c123, c124]
  rcases lt_or_ge (t - ⌊t⌋) (220993 / 657120 : ℝ) with c125 | c125
  · refine ⟨29, 11 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c124, c125]
  rcases lt_or_ge (t - ⌊t⌋) (148509 / 438080 : ℝ) with c126 | c126
  · refine ⟨22, 7 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c125, c126]
  rcases lt_or_ge (t - ⌊t⌋) (67789 / 197136 : ℝ) with c127 | c127
  · refine ⟨8, 4 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c126, c127]
  rcases lt_or_ge (t - ⌊t⌋) (67957 / 197136 : ℝ) with c128 | c128
  · refine ⟨34, 19 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c127, c128]
  rcases lt_or_ge (t - ⌊t⌋) (302967 / 876160 : ℝ) with c129 | c129
  · refine ⟨16, 14 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c128, c129]
  rcases lt_or_ge (t - ⌊t⌋) (92071 / 262848 : ℝ) with c130 | c130
  · refine ⟨11, 5 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c129, c130]
  rcases lt_or_ge (t - ⌊t⌋) (57691 / 164280 : ℝ) with c131 | c131
  · refine ⟨3, 22 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c130, c131]
  rcases lt_or_ge (t - ⌊t⌋) (170391 / 481888 : ℝ) with c132 | c132
  · refine ⟨21, 8 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c131, c132]
  rcases lt_or_ge (t - ⌊t⌋) (280001 / 788544 : ℝ) with c133 | c133
  · refine ⟨35, 13 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c132, c133]
  rcases lt_or_ge (t - ⌊t⌋) (561181 / 1577088 : ℝ) with c134 | c134
  · refine ⟨32, 26 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c133, c134]
  rcases lt_or_ge (t - ⌊t⌋) (109709 / 306656 : ℝ) with c135 | c135
  · refine ⟨27, 10 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c134, c135]
  rcases lt_or_ge (t - ⌊t⌋) (197089 / 547600 : ℝ) with c136 | c136
  · refine ⟨19, 9 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c135, c136]
  rcases lt_or_ge (t - ⌊t⌋) (63257 / 175232 : ℝ) with c137 | c137
  · refine ⟨30, 12 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c136, c137]
  rcases lt_or_ge (t - ⌊t⌋) (55683 / 153328 : ℝ) with c138 | c138
  · refine ⟨9, 8 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c137, c138]
  rcases lt_or_ge (t - ⌊t⌋) (123493 / 339512 : ℝ) with c139 | c139
  · refine ⟨33, 12 + 31 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c138, c139]
  rcases lt_or_ge (t - ⌊t⌋) (23971 / 65712 : ℝ) with c140 | c140
  · refine ⟨24, 18 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c139, c140]
  rcases lt_or_ge (t - ⌊t⌋) (192949 / 525696 : ℝ) with c141 | c141
  · refine ⟨23, 9 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c140, c141]
  rcases lt_or_ge (t - ⌊t⌋) (113347 / 306656 : ℝ) with c142 | c142
  · refine ⟨13, 6 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c141, c142]
  rcases lt_or_ge (t - ⌊t⌋) (324871 / 876160 : ℝ) with c143 | c143
  · refine ⟨16, 15 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c142, c143]
  rcases lt_or_ge (t - ⌊t⌋) (65503 / 175232 : ℝ) with c144 | c144
  · refine ⟨15, 6 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c143, c144]
  rcases lt_or_ge (t - ⌊t⌋) (49961 / 131424 : ℝ) with c145 | c145
  · refine ⟨5, 3 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c144, c145]
  rcases lt_or_ge (t - ⌊t⌋) (16775 / 43808 : ℝ) with c146 | c146
  · refine ⟨7, 4 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c145, c146]
  rcases lt_or_ge (t - ⌊t⌋) (67221 / 175232 : ℝ) with c147 | c147
  · refine ⟨32, 28 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c146, c147]
  rcases lt_or_ge (t - ⌊t⌋) (63167 / 164280 : ℝ) with c148 | c148
  · refine ⟨3, 24 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c147, c148]
  rcases lt_or_ge (t - ⌊t⌋) (6335 / 16428 : ℝ) with c149 | c149
  · refine ⟨24, 19 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c148, c149]
  rcases lt_or_ge (t - ⌊t⌋) (76349 / 197136 : ℝ) with c150 | c150
  · refine ⟨26, 11 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c149, c150]
  rcases lt_or_ge (t - ⌊t⌋) (153713 / 394272 : ℝ) with c151 | c151
  · refine ⟨17, 7 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c150, c151]
  rcases lt_or_ge (t - ⌊t⌋) (540 / 1369 : ℝ) with c152 | c152
  · refine ⟨18, 4 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c151, c152]
  rcases lt_or_ge (t - ⌊t⌋) (112933 / 284752 : ℝ) with c153 | c153
  · refine ⟨12, 6 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c152, c153]
  rcases lt_or_ge (t - ⌊t⌋) (192295 / 481888 : ℝ) with c154 | c154
  · refine ⟨21, 9 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c153, c154]
  rcases lt_or_ge (t - ⌊t⌋) (218993 / 547600 : ℝ) with c155 | c155
  · refine ⟨19, 10 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c154, c155]
  rcases lt_or_ge (t - ⌊t⌋) (26303 / 65712 : ℝ) with c156 | c156
  · refine ⟨34, 22 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c155, c156]
  rcases lt_or_ge (t - ⌊t⌋) (13181 / 32856 : ℝ) with c157 | c157
  · refine ⟨3, 25 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c156, c157]
  rcases lt_or_ge (t - ⌊t⌋) (88267 / 219040 : ℝ) with c158 | c158
  · refine ⟨29, 13 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c157, c158]
  rcases lt_or_ge (t - ⌊t⌋) (18835 / 43808 : ℝ) with c159 | c159
  · refine ⟨1, 1 + 2 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c158, c159]
  rcases lt_or_ge (t - ⌊t⌋) (113975 / 262848 : ℝ) with c160 | c160
  · refine ⟨11, 6 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c159, c160]
  rcases lt_or_ge (t - ⌊t⌋) (76455 / 175232 : ℝ) with c161 | c161
  · refine ⟨15, 7 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c160, c161]
  rcases lt_or_ge (t - ⌊t⌋) (192317 / 438080 : ℝ) with c162 | c162
  · refine ⟨22, 9 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c161, c162]
  rcases lt_or_ge (t - ⌊t⌋) (135251 / 306656 : ℝ) with c163 | c163
  · refine ⟨13, 7 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c162, c163]
  rcases lt_or_ge (t - ⌊t⌋) (8597 / 19166 : ℝ) with c164 | c164
  · refine ⟨6, 4 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c163, c164]
  rcases lt_or_ge (t - ⌊t⌋) (78919 / 175232 : ℝ) with c165 | c165
  · refine ⟨23, 11 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c164, c165]
  rcases lt_or_ge (t - ⌊t⌋) (89693 / 197136 : ℝ) with c166 | c166
  · refine ⟨8, 5 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c165, c166]
  rcases lt_or_ge (t - ⌊t⌋) (89861 / 197136 : ℝ) with c167 | c167
  · refine ⟨34, 25 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c166, c167]
  rcases lt_or_ge (t - ⌊t⌋) (210857 / 459984 : ℝ) with c168 | c168
  · refine ⟨9, 10 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c167, c168]
  rcases lt_or_ge (t - ⌊t⌋) (51181 / 109520 : ℝ) with c169 | c169
  · refine ⟨4, 3 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c168, c169]
  rcases lt_or_ge (t - ⌊t⌋) (113593 / 240944 : ℝ) with c170 | c170
  · refine ⟨10, 6 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c169, c170]
  rcases lt_or_ge (t - ⌊t⌋) (10695 / 21904 : ℝ) with c171 | c171
  · refine ⟨2, 2 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c170, c171]
  rcases lt_or_ge (t - ⌊t⌋) (236103 / 481888 : ℝ) with c172 | c172
  · refine ⟨21, 11 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c171, c172]
  rcases lt_or_ge (t - ⌊t⌋) (6769 / 13690 : ℝ) with c173 | c173
  · refine ⟨18, 5 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c172, c173]
  rcases lt_or_ge (t - ⌊t⌋) (92351 / 186184 : ℝ) with c174 | c174
  · refine ⟨31, 17 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c173, c174]
  rcases lt_or_ge (t - ⌊t⌋) (87407 / 175232 : ℝ) with c175 | c175
  · refine ⟨15, 8 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c174, c175]
  rcases lt_or_ge (t - ⌊t⌋) (197521 / 394272 : ℝ) with c176 | c176
  · refine ⟨17, 9 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c175, c176]
  rcases lt_or_ge (t - ⌊t⌋) (82333 / 164280 : ℝ) with c177 | c177
  · refine ⟨3, 31 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c176, c177]
  rcases lt_or_ge (t - ⌊t⌋) (22251 / 43808 : ℝ) with c178 | c178
  · refine ⟨7, 5 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c177, c178]
  rcases lt_or_ge (t - ⌊t⌋) (55801 / 109520 : ℝ) with c179 | c179
  · refine ⟨14, 8 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c178, c179]
  rcases lt_or_ge (t - ⌊t⌋) (157155 / 306656 : ℝ) with c180 | c180
  · refine ⟨13, 8 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c179, c180]
  rcases lt_or_ge (t - ⌊t⌋) (45293 / 87616 : ℝ) with c181 | c181
  · refine ⟨11, 7 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c180, c181]
  rcases lt_or_ge (t - ⌊t⌋) (28357 / 54760 : ℝ) with c182 | c182
  · refine ⟨3, 32 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c181, c182]
  rcases lt_or_ge (t - ⌊t⌋) (56941 / 109520 : ℝ) with c183 | c183
  · refine ⟨19, 13 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c182, c183]
  rcases lt_or_ge (t - ⌊t⌋) (91259 / 175232 : ℝ) with c184 | c184
  · refine ⟨16, 21 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c183, c184]
  rcases lt_or_ge (t - ⌊t⌋) (411425 / 788544 : ℝ) with c185 | c185
  · refine ⟨35, 19 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c184, c185]
  rcases lt_or_ge (t - ⌊t⌋) (2931 / 5476 : ℝ) with c186 | c186
  · refine ⟨25, 3 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c185, c186]
  rcases lt_or_ge (t - ⌊t⌋) (164469 / 306656 : ℝ) with c187 | c187
  · refine ⟨27, 15 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c186, c187]
  rcases lt_or_ge (t - ⌊t⌋) (47225 / 87616 : ℝ) with c188 | c188
  · refine ⟨22, 11 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c187, c188]
  rcases lt_or_ge (t - ⌊t⌋) (23955 / 43808 : ℝ) with c189 | c189
  · refine ⟨5, 4 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c188, c189]
  rcases lt_or_ge (t - ⌊t⌋) (12057 / 21904 : ℝ) with c190 | c190
  · refine ⟨12, 8 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c189, c190]
  rcases lt_or_ge (t - ⌊t⌋) (90547 / 164280 : ℝ) with c191 | c191
  · refine ⟨3, 34 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c190, c191]
  rcases lt_or_ge (t - ⌊t⌋) (254665 / 459984 : ℝ) with c192 | c192
  · refine ⟨9, 12 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c191, c192]
  rcases lt_or_ge (t - ⌊t⌋) (219425 / 394272 : ℝ) with c193 | c193
  · refine ⟨17, 10 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c192, c193]
  rcases lt_or_ge (t - ⌊t⌋) (189205 / 339512 : ℝ) with c194 | c194
  · refine ⟨33, 18 + 31 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c193, c194]
  rcases lt_or_ge (t - ⌊t⌋) (793681 / 1423760 : ℝ) with c195 | c195
  · refine ⟨20, 37 + 65 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c194, c195]
  rcases lt_or_ge (t - ⌊t⌋) (135497 / 240944 : ℝ) with c196 | c196
  · refine ⟨10, 7 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c195, c196]
  rcases lt_or_ge (t - ⌊t⌋) (37199 / 65712 : ℝ) with c197 | c197
  · refine ⟨8, 6 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c196, c197]
  rcases lt_or_ge (t - ⌊t⌋) (37255 / 65712 : ℝ) with c198 | c198
  · refine ⟨34, 31 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c197, c198]
  rcases lt_or_ge (t - ⌊t⌋) (6219 / 10952 : ℝ) with c199 | c199
  · refine ⟨3, 35 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c198, c199]
  rcases lt_or_ge (t - ⌊t⌋) (374321 / 657120 : ℝ) with c200 | c200
  · refine ⟨29, 18 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c199, c200]
  rcases lt_or_ge (t - ⌊t⌋) (500103 / 876160 : ℝ) with c201 | c201
  · refine ⟨16, 23 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c200, c201]
  rcases lt_or_ge (t - ⌊t⌋) (338567 / 591408 : ℝ) with c202 | c202
  · refine ⟨26, 16 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c201, c202]
  rcases lt_or_ge (t - ⌊t⌋) (37661 / 65712 : ℝ) with c203 | c203
  · refine ⟨24, 28 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c202, c203]
  rcases lt_or_ge (t - ⌊t⌋) (189307 / 328560 : ℝ) with c204 | c204
  · refine ⟨14, 9 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c203, c204]
  rcases lt_or_ge (t - ⌊t⌋) (455233 / 788544 : ℝ) with c205 | c205
  · refine ⟨35, 21 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c204, c205]
  rcases lt_or_ge (t - ⌊t⌋) (911645 / 1577088 : ℝ) with c206 | c206
  · refine ⟨32, 42 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c205, c206]
  rcases lt_or_ge (t - ⌊t⌋) (101589 / 175232 : ℝ) with c207 | c207
  · refine ⟨30, 19 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c206, c207]
  rcases lt_or_ge (t - ⌊t⌋) (279911 / 481888 : ℝ) with c208 | c208
  · refine ⟨21, 13 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c207, c208]
  rcases lt_or_ge (t - ⌊t⌋) (179059 / 306656 : ℝ) with c209 | c209
  · refine ⟨13, 9 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c208, c209]
  rcases lt_or_ge (t - ⌊t⌋) (11335 / 19166 : ℝ) with c210 | c210
  · refine ⟨6, 5 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c209, c210]
  rcases lt_or_ge (t - ⌊t⌋) (4069 / 6845 : ℝ) with c211 | c211
  · refine ⟨18, 6 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c210, c211]
  rcases lt_or_ge (t - ⌊t⌋) (522007 / 876160 : ℝ) with c212 | c212
  · refine ⟨16, 24 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c211, c212]
  rcases lt_or_ge (t - ⌊t⌋) (157783 / 262848 : ℝ) with c213 | c213
  · refine ⟨11, 8 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c212, c213]
  rcases lt_or_ge (t - ⌊t⌋) (276569 / 459984 : ℝ) with c214 | c214
  · refine ⟨9, 13 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c213, c214]
  rcases lt_or_ge (t - ⌊t⌋) (26415 / 43808 : ℝ) with c215 | c215
  · refine ⟨29, 19 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c214, c215]
  rcases lt_or_ge (t - ⌊t⌋) (859393 / 1423760 : ℝ) with c216 | c216
  · refine ⟨20, 40 + 65 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c215, c216]
  rcases lt_or_ge (t - ⌊t⌋) (477137 / 788544 : ℝ) with c217 | c217
  · refine ⟨35, 22 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c216, c217]
  rcases lt_or_ge (t - ⌊t⌋) (955453 / 1577088 : ℝ) with c218 | c218
  · refine ⟨32, 44 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c217, c218]
  rcases lt_or_ge (t - ⌊t⌋) (186373 / 306656 : ℝ) with c219 | c219
  · refine ⟨27, 17 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c218, c219]
  rcases lt_or_ge (t - ⌊t⌋) (120157 / 197136 : ℝ) with c220 | c220
  · refine ⟨26, 17 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c219, c220]
  rcases lt_or_ge (t - ⌊t⌋) (80443 / 131424 : ℝ) with c221 | c221
  · refine ⟨17, 11 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c220, c221]
  rcases lt_or_ge (t - ⌊t⌋) (114255 / 186184 : ℝ) with c222 | c222
  · refine ⟨31, 21 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c221, c222]
  rcases lt_or_ge (t - ⌊t⌋) (40399 / 65712 : ℝ) with c223 | c223
  · refine ⟨24, 30 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c222, c223]
  rcases lt_or_ge (t - ⌊t⌋) (324373 / 525696 : ℝ) with c224 | c224
  · refine ⟨23, 15 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c223, c224]
  rcases lt_or_ge (t - ⌊t⌋) (514531 / 832352 : ℝ) with c225 | c225
  · refine ⟨28, 24 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c224, c225]
  rcases lt_or_ge (t - ⌊t⌋) (881297 / 1423760 : ℝ) with c226 | c226
  · refine ⟨20, 41 + 65 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c225, c226]
  rcases lt_or_ge (t - ⌊t⌋) (977357 / 1577088 : ℝ) with c227 | c227
  · refine ⟨32, 45 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c226, c227]
  rcases lt_or_ge (t - ⌊t⌋) (543911 / 876160 : ℝ) with c228 | c228
  · refine ⟨16, 25 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c227, c228]
  rcases lt_or_ge (t - ⌊t⌋) (109311 / 175232 : ℝ) with c229 | c229
  · refine ⟨15, 10 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c228, c229]
  rcases lt_or_ge (t - ⌊t⌋) (178645 / 284752 : ℝ) with c230 | c230
  · refine ⟨12, 9 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c229, c230]
  rcases lt_or_ge (t - ⌊t⌋) (27727 / 43808 : ℝ) with c231 | c231
  · refine ⟨7, 6 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c230, c231]
  rcases lt_or_ge (t - ⌊t⌋) (111029 / 175232 : ℝ) with c232 | c232
  · refine ⟨32, 46 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c231, c232]
  rcases lt_or_ge (t - ⌊t⌋) (104237 / 164280 : ℝ) with c233 | c233
  · refine ⟨3, 39 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c232, c233]
  rcases lt_or_ge (t - ⌊t⌋) (418129 / 657120 : ℝ) with c234 | c234
  · refine ⟨29, 20 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c233, c234]
  rcases lt_or_ge (t - ⌊t⌋) (279933 / 438080 : ℝ) with c235 | c235
  · refine ⟨22, 13 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c234, c235]
  rcases lt_or_ge (t - ⌊t⌋) (350417 / 547600 : ℝ) with c236 | c236
  · refine ⟨19, 16 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c235, c236]
  rcases lt_or_ge (t - ⌊t⌋) (211211 / 328560 : ℝ) with c237 | c237
  · refine ⟨14, 10 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c236, c237]
  rcases lt_or_ge (t - ⌊t⌋) (197325 / 306656 : ℝ) with c238 | c238
  · refine ⟨27, 18 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c237, c238]
  rcases lt_or_ge (t - ⌊t⌋) (536435 / 832352 : ℝ) with c239 | c239
  · refine ⟨28, 25 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c238, c239]
  rcases lt_or_ge (t - ⌊t⌋) (113163 / 175232 : ℝ) with c240 | c240
  · refine ⟨16, 26 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c239, c240]
  rcases lt_or_ge (t - ⌊t⌋) (382375 / 591408 : ℝ) with c241 | c241
  · refine ⟨26, 18 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c240, c241]
  rcases lt_or_ge (t - ⌊t⌋) (14213 / 21904 : ℝ) with c242 | c242
  · refine ⟨9, 14 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c241, c242]
  rcases lt_or_ge (t - ⌊t⌋) (157401 / 240944 : ℝ) with c243 | c243
  · refine ⟨10, 8 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c242, c243]
  rcases lt_or_ge (t - ⌊t⌋) (28709 / 43808 : ℝ) with c244 | c244
  · refine ⟨13, 10 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c243, c244]
  rcases lt_or_ge (t - ⌊t⌋) (14379 / 21904 : ℝ) with c245 | c245
  · refine ⟨24, 32 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c244, c245]
  rcases lt_or_ge (t - ⌊t⌋) (346277 / 525696 : ℝ) with c246 | c246
  · refine ⟨23, 16 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c245, c246]
  rcases lt_or_ge (t - ⌊t⌋) (14617 / 21904 : ℝ) with c247 | c247
  · refine ⟨4, 4 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c246, c247]
  rcases lt_or_ge (t - ⌊t⌋) (36571 / 54760 : ℝ) with c248 | c248
  · refine ⟨3, 41 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c247, c248]
  rcases lt_or_ge (t - ⌊t⌋) (440033 / 657120 : ℝ) with c249 | c249
  · refine ⟨29, 21 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c248, c249]
  rcases lt_or_ge (t - ⌊t⌋) (29429 / 43808 : ℝ) with c250 | c250
  · refine ⟨21, 15 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c249, c250]
  rcases lt_or_ge (t - ⌊t⌋) (133501 / 197136 : ℝ) with c251 | c251
  · refine ⟨8, 7 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c250, c251]
  rcases lt_or_ge (t - ⌊t⌋) (133669 / 197136 : ℝ) with c252 | c252
  · refine ⟨34, 37 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c251, c252]
  rcases lt_or_ge (t - ⌊t⌋) (372321 / 547600 : ℝ) with c253 | c253
  · refine ⟨19, 17 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c252, c253]
  rcases lt_or_ge (t - ⌊t⌋) (179687 / 262848 : ℝ) with c254 | c254
  · refine ⟨11, 9 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c253, c254]
  rcases lt_or_ge (t - ⌊t⌋) (120263 / 175232 : ℝ) with c255 | c255
  · refine ⟨15, 11 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c254, c255]
  rcases lt_or_ge (t - ⌊t⌋) (301837 / 438080 : ℝ) with c256 | c256
  · refine ⟨22, 14 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c255, c256]
  rcases lt_or_ge (t - ⌊t⌋) (1086877 / 1577088 : ℝ) with c257 | c257
  · refine ⟨32, 50 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c256, c257]
  rcases lt_or_ge (t - ⌊t⌋) (9507 / 13690 : ℝ) with c258 | c258
  · refine ⟨18, 7 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c257, c258]
  rcases lt_or_ge (t - ⌊t⌋) (320377 / 459984 : ℝ) with c259 | c259
  · refine ⟨9, 15 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c258, c259]
  rcases lt_or_ge (t - ⌊t⌋) (580243 / 832352 : ℝ) with c260 | c260
  · refine ⟨28, 27 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c259, c260]
  rcases lt_or_ge (t - ⌊t⌋) (45875 / 65712 : ℝ) with c261 | c261
  · refine ⟨24, 34 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c260, c261]
  rcases lt_or_ge (t - ⌊t⌋) (122727 / 175232 : ℝ) with c262 | c262
  · refine ⟨23, 17 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c261, c262]
  rcases lt_or_ge (t - ⌊t⌋) (200549 / 284752 : ℝ) with c263 | c263
  · refine ⟨12, 10 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c262, c263]
  rcases lt_or_ge (t - ⌊t⌋) (123493 / 175232 : ℝ) with c264 | c264
  · refine ⟨30, 23 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c263, c264]
  rcases lt_or_ge (t - ⌊t⌋) (93769 / 131424 : ℝ) with c265 | c265
  · refine ⟨5, 5 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c264, c265]
  rcases lt_or_ge (t - ⌊t⌋) (219229 / 306656 : ℝ) with c266 | c266
  · refine ⟨27, 20 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c265, c266]
  rcases lt_or_ge (t - ⌊t⌋) (345623 / 481888 : ℝ) with c267 | c267
  · refine ⟨21, 16 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c266, c267]
  rcases lt_or_ge (t - ⌊t⌋) (243965 / 339512 : ℝ) with c268 | c268
  · refine ⟨33, 23 + 31 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c267, c268]
  rcases lt_or_ge (t - ⌊t⌋) (15769 / 21904 : ℝ) with c269 | c269
  · refine ⟨19, 18 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c268, c269]
  rcases lt_or_ge (t - ⌊t⌋) (631527 / 876160 : ℝ) with c270 | c270
  · refine ⟨16, 29 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c269, c270]
  rcases lt_or_ge (t - ⌊t⌋) (285137 / 394272 : ℝ) with c271 | c271
  · refine ⟨17, 13 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c270, c271]
  rcases lt_or_ge (t - ⌊t⌋) (222867 / 306656 : ℝ) with c272 | c272
  · refine ⟨13, 11 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c271, c272]
  rcases lt_or_ge (t - ⌊t⌋) (14073 / 19166 : ℝ) with c273 | c273
  · refine ⟨6, 6 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c272, c273]
  rcases lt_or_ge (t - ⌊t⌋) (24133 / 32856 : ℝ) with c274 | c274
  · refine ⟨3, 45 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c273, c274]
  rcases lt_or_ge (t - ⌊t⌋) (483841 / 657120 : ℝ) with c275 | c275
  · refine ⟨29, 23 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c274, c275]
  rcases lt_or_ge (t - ⌊t⌋) (323741 / 438080 : ℝ) with c276 | c276
  · refine ⟨22, 15 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c275, c276]
  rcases lt_or_ge (t - ⌊t⌋) (48613 / 65712 : ℝ) with c277 | c277
  · refine ⟨24, 36 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c276, c277]
  rcases lt_or_ge (t - ⌊t⌋) (179305 / 240944 : ℝ) with c278 | c278
  · refine ⟨10, 9 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c277, c278]
  rcases lt_or_ge (t - ⌊t⌋) (1174493 / 1577088 : ℝ) with c279 | c279
  · refine ⟨32, 54 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c278, c279]
  rcases lt_or_ge (t - ⌊t⌋) (653431 / 876160 : ℝ) with c280 | c280
  · refine ⟨16, 30 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c279, c280]
  rcases lt_or_ge (t - ⌊t⌋) (131215 / 175232 : ℝ) with c281 | c281
  · refine ⟨15, 12 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c280, c281]
  rcases lt_or_ge (t - ⌊t⌋) (32883 / 43808 : ℝ) with c282 | c282
  · refine ⟨27, 21 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c281, c282]
  rcases lt_or_ge (t - ⌊t⌋) (123403 / 164280 : ℝ) with c283 | c283
  · refine ⟨3, 46 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c282, c283]
  rcases lt_or_ge (t - ⌊t⌋) (33203 / 43808 : ℝ) with c284 | c284
  · refine ⟨7, 7 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c283, c284]
  rcases lt_or_ge (t - ⌊t⌋) (416129 / 547600 : ℝ) with c285 | c285
  · refine ⟨19, 19 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c284, c285]
  rcases lt_or_ge (t - ⌊t⌋) (141635 / 186184 : ℝ) with c286 | c286
  · refine ⟨31, 26 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c285, c286]
  rcases lt_or_ge (t - ⌊t⌋) (367527 / 481888 : ℝ) with c287 | c287
  · refine ⟨21, 17 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c286, c287]
  rcases lt_or_ge (t - ⌊t⌋) (67197 / 87616 : ℝ) with c288 | c288
  · refine ⟨11, 10 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c287, c288]
  rcases lt_or_ge (t - ⌊t⌋) (42047 / 54760 : ℝ) with c289 | c289
  · refine ⟨3, 47 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c288, c289]
  rcases lt_or_ge (t - ⌊t⌋) (101149 / 131424 : ℝ) with c290 | c290
  · refine ⟨29, 24 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c289, c290]
  rcases lt_or_ge (t - ⌊t⌋) (135067 / 175232 : ℝ) with c291 | c291
  · refine ⟨16, 31 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c290, c291]
  rcases lt_or_ge (t - ⌊t⌋) (608561 / 788544 : ℝ) with c292 | c292
  · refine ⟨35, 28 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c291, c292]
  rcases lt_or_ge (t - ⌊t⌋) (1075 / 1369 : ℝ) with c293 | c293
  · refine ⟨25, 4 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c292, c293]
  rcases lt_or_ge (t - ⌊t⌋) (155405 / 197136 : ℝ) with c294 | c294
  · refine ⟨8, 8 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c293, c294]
  rcases lt_or_ge (t - ⌊t⌋) (155573 / 197136 : ℝ) with c295 | c295
  · refine ⟨34, 43 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c294, c295]
  rcases lt_or_ge (t - ⌊t⌋) (5438 / 6845 : ℝ) with c296 | c296
  · refine ⟨18, 8 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c295, c296]
  rcases lt_or_ge (t - ⌊t⌋) (244771 / 306656 : ℝ) with c297 | c297
  · refine ⟨13, 12 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c296, c297]
  rcases lt_or_ge (t - ⌊t⌋) (438033 / 547600 : ℝ) with c298 | c298
  · refine ⟨19, 20 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c297, c298]
  rcases lt_or_ge (t - ⌊t⌋) (420703 / 525696 : ℝ) with c299 | c299
  · refine ⟨32, 58 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c298, c299]
  rcases lt_or_ge (t - ⌊t⌋) (131617 / 164280 : ℝ) with c300 | c300
  · refine ⟨3, 49 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c299, c300]
  rcases lt_or_ge (t - ⌊t⌋) (175883 / 219040 : ℝ) with c301 | c301
  · refine ⟨29, 25 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c300, c301]
  rcases lt_or_ge (t - ⌊t⌋) (228829 / 284752 : ℝ) with c302 | c302
  · refine ⟨20, 53 + 65 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c301, c302]
  rcases lt_or_ge (t - ⌊t⌋) (53989 / 65712 : ℝ) with c303 | c303
  · refine ⟨2, 3 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c302, c303]
  rcases lt_or_ge (t - ⌊t⌋) (252085 / 306656 : ℝ) with c304 | c304
  · refine ⟨27, 23 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c303, c304]
  rcases lt_or_ge (t - ⌊t⌋) (54089 / 65712 : ℝ) with c305 | c305
  · refine ⟨24, 40 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c304, c305]
  rcases lt_or_ge (t - ⌊t⌋) (144631 / 175232 : ℝ) with c306 | c306
  · refine ⟨23, 20 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c305, c306]
  rcases lt_or_ge (t - ⌊t⌋) (488623 / 591408 : ℝ) with c307 | c307
  · refine ⟨34, 45 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c306, c307]
  rcases lt_or_ge (t - ⌊t⌋) (652369 / 788544 : ℝ) with c308 | c308
  · refine ⟨35, 30 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c307, c308]
  rcases lt_or_ge (t - ⌊t⌋) (689763 / 832352 : ℝ) with c309 | c309
  · refine ⟨28, 32 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c308, c309]
  rcases lt_or_ge (t - ⌊t⌋) (145397 / 175232 : ℝ) with c310 | c310
  · refine ⟨30, 27 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c309, c310]
  rcases lt_or_ge (t - ⌊t⌋) (54655 / 65712 : ℝ) with c311 | c311
  · refine ⟨26, 23 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c310, c311]
  rcases lt_or_ge (t - ⌊t⌋) (201209 / 240944 : ℝ) with c312 | c312
  · refine ⟨10, 10 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c311, c312]
  rcases lt_or_ge (t - ⌊t⌋) (549553 / 657120 : ℝ) with c313 | c313
  · refine ⟨29, 26 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c312, c313]
  rcases lt_or_ge (t - ⌊t⌋) (367549 / 438080 : ℝ) with c314 | c314
  · refine ⟨22, 17 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c313, c314]
  rcases lt_or_ge (t - ⌊t⌋) (459937 / 547600 : ℝ) with c315 | c315
  · refine ⟨19, 21 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c314, c315]
  rcases lt_or_ge (t - ⌊t⌋) (276923 / 328560 : ℝ) with c316 | c316
  · refine ⟨14, 13 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c315, c316]
  rcases lt_or_ge (t - ⌊t⌋) (9243 / 10952 : ℝ) with c317 | c317
  · refine ⟨24, 41 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c316, c317]
  rcases lt_or_ge (t - ⌊t⌋) (166525 / 197136 : ℝ) with c318 | c318
  · refine ⟨34, 46 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c317, c318]
  rcases lt_or_ge (t - ⌊t⌋) (741047 / 876160 : ℝ) with c319 | c319
  · refine ⟨16, 34 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c318, c319]
  rcases lt_or_ge (t - ⌊t⌋) (223495 / 262848 : ℝ) with c320 | c320
  · refine ⟨11, 11 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c319, c320]
  rcases lt_or_ge (t - ⌊t⌋) (139831 / 164280 : ℝ) with c321 | c321
  · refine ⟨3, 52 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c320, c321]
  rcases lt_or_ge (t - ⌊t⌋) (411335 / 481888 : ℝ) with c322 | c322
  · refine ⟨21, 19 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c321, c322]
  rcases lt_or_ge (t - ⌊t⌋) (674273 / 788544 : ℝ) with c323 | c323
  · refine ⟨35, 31 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c322, c323]
  rcases lt_or_ge (t - ⌊t⌋) (244357 / 284752 : ℝ) with c324 | c324
  · refine ⟨12, 12 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c323, c324]
  rcases lt_or_ge (t - ⌊t⌋) (94989 / 109520 : ℝ) with c325 | c325
  · refine ⟨4, 5 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c324, c325]
  rcases lt_or_ge (t - ⌊t⌋) (266675 / 306656 : ℝ) with c326 | c326
  · refine ⟨13, 13 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c325, c326]
  rcases lt_or_ge (t - ⌊t⌋) (16811 / 19166 : ℝ) with c327 | c327
  · refine ⟨6, 7 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c326, c327]
  rcases lt_or_ge (t - ⌊t⌋) (38679 / 43808 : ℝ) with c328 | c328
  · refine ⟨7, 8 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c327, c328]
  rcases lt_or_ge (t - ⌊t⌋) (154837 / 175232 : ℝ) with c329 | c329
  · refine ⟨32, 64 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c328, c329]
  rcases lt_or_ge (t - ⌊t⌋) (145307 / 164280 : ℝ) with c330 | c330
  · refine ⟨3, 54 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c329, c330]
  rcases lt_or_ge (t - ⌊t⌋) (407993 / 459984 : ℝ) with c331 | c331
  · refine ⟨9, 19 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c330, c331]
  rcases lt_or_ge (t - ⌊t⌋) (350849 / 394272 : ℝ) with c332 | c332
  · refine ⟨17, 16 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c331, c332]
  rcases lt_or_ge (t - ⌊t⌋) (2449 / 2738 : ℝ) with c333 | c333
  · refine ⟨18, 9 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c332, c333]
  rcases lt_or_ge (t - ⌊t⌋) (19701 / 21904 : ℝ) with c334 | c334
  · refine ⟨8, 9 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c333, c334]
  rcases lt_or_ge (t - ⌊t⌋) (59159 / 65712 : ℝ) with c335 | c335
  · refine ⟨34, 49 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c334, c335]
  rcases lt_or_ge (t - ⌊t⌋) (29609 / 32856 : ℝ) with c336 | c336
  · refine ⟨3, 55 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c335, c336]
  rcases lt_or_ge (t - ⌊t⌋) (197787 / 219040 : ℝ) with c337 | c337
  · refine ⟨29, 28 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c336, c337]
  rcases lt_or_ge (t - ⌊t⌋) (40739 / 43808 : ℝ) with c338 | c338
  · refine ⟨1, 2 + 2 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c337, c338]
  rcases lt_or_ge (t - ⌊t⌋) (21547 / 21904 : ℝ) with c339 | c339
  · refine ⟨0, 1 + 1 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c338, c339]
  rcases lt_or_ge (t - ⌊t⌋) (32347 / 32856 : ℝ) with c340 | c340
  · refine ⟨3, 60 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c339, c340]
  rcases lt_or_ge (t - ⌊t⌋) (172777 / 175232 : ℝ) with c341 | c341
  · refine ⟨30, 32 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c340, c341]
  rcases lt_or_ge (t - ⌊t⌋) (821187 / 832352 : ℝ) with c342 | c342
  · refine ⟨28, 38 + 38 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c341, c342]
  rcases lt_or_ge (t - ⌊t⌋) (433261 / 438080 : ℝ) with c343 | c343
  · refine ⟨22, 20 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c342, c343]
  rcases lt_or_ge (t - ⌊t⌋) (477047 / 481888 : ℝ) with c344 | c344
  · refine ⟨21, 22 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c343, c344]
  rcases lt_or_ge (t - ⌊t⌋) (6807 / 6845 : ℝ) with c345 | c345
  · refine ⟨18, 10 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c344, c345]
  rcases lt_or_ge (t - ⌊t⌋) (185443 / 186184 : ℝ) with c346 | c346
  · refine ⟨31, 34 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c345, c346]
  rcases lt_or_ge (t - ⌊t⌋) (175023 / 175232 : ℝ) with c347 | c347
  · refine ⟨15, 16 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c346, c347]
  refine ⟨17, 18 + 18 * ⌊t⌋, ?_⟩
  simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
  rw [abs_lt]
  push_cast
  constructor <;> linarith only [c347, h1]

#print axioms cover
#print axioms v_injective
#print axioms v_pos
end SLRAudit.N36
