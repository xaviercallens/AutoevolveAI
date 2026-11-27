import Mathlib.Tactic

set_option linter.unusedSimpArgs false
set_option maxHeartbeats 0
namespace SLRAudit.N33

/-- velocities of certificate n = 33 -/
def v : Fin 33 → ℕ := ![60, 24, 32, 1, 10, 6, 25, 50, 44, 13, 22, 12, 9, 15, 8, 36, 20, 30, 26, 48, 7, 18, 4, 40, 45, 2, 28, 29, 14, 27, 16, 3, 5]
/-- shifts s_i = a_i / 18497 -/
def s : Fin 33 → ℚ := ![13731/18497, 2669/18497, 10811/18497, 13220/18497, 13385/18497, 13570/18497, 109/18497, 1843/18497, 23/18497, 5545/18497, 16098/18497, 521/18497, 15909/18497, 16628/18497, 3380/18497, 16393/18497, 5840/18497, 6052/18497, 6802/18497, 8261/18497, 8373/18497, 15404/18497, 4466/18497, 5892/18497, 16972/18497, 4101/18497, 17692/18497, 17922/18497, 2641/18497, 8815/18497, 4236/18497, 10504/18497, 2993/18497]

theorem v_injective : Function.Injective v := by decide
theorem v_pos : ∀ i, 0 < v i := by decide

/-- covering: for every real t some runner is within distance < 1/34 of an integer. -/
theorem cover : ∀ t : ℝ, ∃ i : Fin 33, ∃ k : ℤ, |((s i : ℚ) : ℝ) + ((v i : ℕ) : ℝ) * t - (k : ℝ)| < 1 / 34 := by
  intro t
  have h0 : (0 : ℝ) ≤ t - ⌊t⌋ := by have := Int.floor_le t; linarith
  have h1 : t - ⌊t⌋ < (1 : ℝ) := by have := Int.lt_floor_add_one t; linarith
  rcases lt_or_ge (t - ⌊t⌋) (14791 / 15722450 : ℝ) with c0 | c0
  · refine ⟨6, 0 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [h0, c0]
  rcases lt_or_ge (t - ⌊t⌋) (45867 / 17609144 : ℝ) with c1 | c1
  · refine ⟨26, 1 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c0, c1]
  rcases lt_or_ge (t - ⌊t⌋) (30011 / 7546776 : ℝ) with c2 | c2
  · refine ⟨15, 1 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1, c2]
  rcases lt_or_ge (t - ⌊t⌋) (180541 / 37733880 : ℝ) with c3 | c3
  · refine ⟨0, 1 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2, c3]
  rcases lt_or_ge (t - ⌊t⌋) (82043 / 9433470 : ℝ) with c4 | c4
  · refine ⟨13, 1 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c3, c4]
  rcases lt_or_ge (t - ⌊t⌋) (123659 / 11320164 : ℝ) with c5 | c5
  · refine ⟨21, 1 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c4, c5]
  rcases lt_or_ge (t - ⌊t⌋) (366521 / 30187104 : ℝ) with c6 | c6
  · refine ⟨19, 1 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c5, c6]
  rcases lt_or_ge (t - ⌊t⌋) (279821 / 20124736 : ℝ) with c7 | c7
  · refine ⟨2, 1 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c6, c7]
  rcases lt_or_ge (t - ⌊t⌋) (106489 / 5660082 : ℝ) with c8 | c8
  · refine ⟨12, 1 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c7, c8]
  rcases lt_or_ge (t - ⌊t⌋) (115895 / 5660082 : ℝ) with c9 | c9
  · refine ⟨29, 1 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c8, c9]
  rcases lt_or_ge (t - ⌊t⌋) (269813 / 12577960 : ℝ) with c10 | c10
  · refine ⟨0, 2 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c9, c10]
  rcases lt_or_ge (t - ⌊t⌋) (147209 / 6288980 : ℝ) with c11 | c11
  · refine ⟨17, 1 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c10, c11]
  rcases lt_or_ge (t - ⌊t⌋) (416127 / 16351348 : ℝ) with c12 | c12
  · refine ⟨18, 1 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c11, c12]
  rcases lt_or_ge (t - ⌊t⌋) (38461 / 1257796 : ℝ) with c13 | c13
  · refine ⟨4, 1 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c12, c13]
  rcases lt_or_ge (t - ⌊t⌋) (718931 / 22640328 : ℝ) with c14 | c14
  · refine ⟨15, 2 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c13, c14]
  rcases lt_or_ge (t - ⌊t⌋) (995419 / 30187104 : ℝ) with c15 | c15
  · refine ⟨19, 2 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c14, c15]
  rcases lt_or_ge (t - ⌊t⌋) (89767 / 2515592 : ℝ) with c16 | c16
  · refine ⟨16, 1 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c15, c16]
  rcases lt_or_ge (t - ⌊t⌋) (556649 / 15093552 : ℝ) with c17 | c17
  · refine ⟨1, 1 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c16, c17]
  rcases lt_or_ge (t - ⌊t⌋) (96395 / 2515592 : ℝ) with c18 | c18
  · refine ⟨26, 2 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c17, c18]
  rcases lt_or_ge (t - ⌊t⌋) (1213631 / 31444900 : ℝ) with c19 | c19
  · refine ⟨7, 2 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c18, c19]
  rcases lt_or_ge (t - ⌊t⌋) (643689 / 15722450 : ℝ) with c20 | c20
  · refine ⟨6, 1 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c19, c20]
  rcases lt_or_ge (t - ⌊t⌋) (62005 / 1257796 : ℝ) with c21 | c21
  · refine ⟨5, 1 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c20, c21]
  rcases lt_or_ge (t - ⌊t⌋) (503371 / 10062368 : ℝ) with c22 | c22
  · refine ⟨30, 1 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c21, c22]
  rcases lt_or_ge (t - ⌊t⌋) (728961 / 13835756 : ℝ) with c23 | c23
  · refine ⟨10, 2 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c22, c23]
  rcases lt_or_ge (t - ⌊t⌋) (458865 / 8175674 : ℝ) with c24 | c24
  · refine ⟨9, 1 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c23, c24]
  rcases lt_or_ge (t - ⌊t⌋) (976583 / 16980246 : ℝ) with c25 | c25
  · refine ⟨29, 2 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c24, c25]
  rcases lt_or_ge (t - ⌊t⌋) (1842529 / 31444900 : ℝ) with c26 | c26
  · refine ⟨7, 3 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c25, c26]
  rcases lt_or_ge (t - ⌊t⌋) (1347829 / 22640328 : ℝ) with c27 | c27
  · refine ⟨15, 3 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c26, c27]
  rcases lt_or_ge (t - ⌊t⌋) (557601 / 8804572 : ℝ) with c28 | c28
  · refine ⟨28, 1 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c27, c28]
  rcases lt_or_ge (t - ⌊t⌋) (752557 / 11320164 : ℝ) with c29 | c29
  · refine ⟨21, 2 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c28, c29]
  rcases lt_or_ge (t - ⌊t⌋) (1704863 / 25155920 : ℝ) with c30 | c30
  · refine ⟨23, 3 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c29, c30]
  rcases lt_or_ge (t - ⌊t⌋) (1904409 / 27671512 : ℝ) with c31 | c31
  · refine ⟨8, 3 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c30, c31]
  rcases lt_or_ge (t - ⌊t⌋) (217449 / 3144490 : ℝ) with c32 | c32
  · refine ⟨24, 4 + 45 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c31, c32]
  rcases lt_or_ge (t - ⌊t⌋) (1295843 / 18238042 : ℝ) with c33 | c33
  · refine ⟨27, 3 + 29 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c32, c33]
  rcases lt_or_ge (t - ⌊t⌋) (898711 / 12577960 : ℝ) with c34 | c34
  · refine ⟨0, 5 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c33, c34]
  rcases lt_or_ge (t - ⌊t⌋) (710941 / 9433470 : ℝ) with c35 | c35
  · refine ⟨13, 2 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c34, c35]
  rcases lt_or_ge (t - ⌊t⌋) (362713 / 4402286 : ℝ) with c36 | c36
  · refine ⟨20, 1 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c35, c36]
  rcases lt_or_ge (t - ⌊t⌋) (629681 / 7546776 : ℝ) with c37 | c37
  · refine ⟨11, 1 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c36, c37]
  rcases lt_or_ge (t - ⌊t⌋) (1077733 / 12577960 : ℝ) with c38 | c38
  · refine ⟨16, 2 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c37, c38]
  rcases lt_or_ge (t - ⌊t⌋) (658909 / 7546776 : ℝ) with c39 | c39
  · refine ⟨15, 4 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c38, c39]
  rcases lt_or_ge (t - ⌊t⌋) (3325031 / 37733880 : ℝ) with c40 | c40
  · refine ⟨0, 6 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c39, c40]
  rcases lt_or_ge (t - ⌊t⌋) (1699423 / 18866940 : ℝ) with c41 | c41
  · refine ⟨17, 3 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c40, c41]
  rcases lt_or_ge (t - ⌊t⌋) (2585939 / 28300410 : ℝ) with c42 | c42
  · refine ⟨24, 5 + 45 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c41, c42]
  rcases lt_or_ge (t - ⌊t⌋) (2333761 / 25155920 : ℝ) with c43 | c43
  · refine ⟨23, 4 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c42, c43]
  rcases lt_or_ge (t - ⌊t⌋) (1605481 / 16980246 : ℝ) with c44 | c44
  · refine ⟨29, 3 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c43, c44]
  rcases lt_or_ge (t - ⌊t⌋) (2882113 / 30187104 : ℝ) with c45 | c45
  · refine ⟨19, 5 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c44, c45]
  rcases lt_or_ge (t - ⌊t⌋) (1357859 / 13835756 : ℝ) with c46 | c46
  · refine ⟨10, 3 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c45, c46]
  rcases lt_or_ge (t - ⌊t⌋) (124013 / 1257796 : ℝ) with c47 | c47
  · refine ⟨7, 5 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c46, c47]
  rcases lt_or_ge (t - ⌊t⌋) (532475 / 5031184 : ℝ) with c48 | c48
  · refine ⟨14, 1 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c47, c48]
  rcases lt_or_ge (t - ⌊t⌋) (2166515 / 20124736 : ℝ) with c49 | c49
  · refine ⟨2, 4 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c48, c49]
  rcases lt_or_ge (t - ⌊t⌋) (1932561 / 17609144 : ℝ) with c50 | c50
  · refine ⟨26, 4 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c49, c50]
  rcases lt_or_ge (t - ⌊t⌋) (1132269 / 10062368 : ℝ) with c51 | c51
  · refine ⟨30, 2 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c50, c51]
  rcases lt_or_ge (t - ⌊t⌋) (3214837 / 28300410 : ℝ) with c52 | c52
  · refine ⟨24, 6 + 45 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c51, c52]
  rcases lt_or_ge (t - ⌊t⌋) (2605625 / 22640328 : ℝ) with c53 | c53
  · refine ⟨15, 5 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c52, c53]
  rcases lt_or_ge (t - ⌊t⌋) (1170337 / 10062368 : ℝ) with c54 | c54
  · refine ⟨19, 6 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c53, c54]
  rcases lt_or_ge (t - ⌊t⌋) (2962659 / 25155920 : ℝ) with c55 | c55
  · refine ⟨23, 5 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c54, c55]
  rcases lt_or_ge (t - ⌊t⌋) (604815 / 5031184 : ℝ) with c56 | c56
  · refine ⟨1, 3 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c55, c56]
  rcases lt_or_ge (t - ⌊t⌋) (153495 / 1257796 : ℝ) with c57 | c57
  · refine ⟨21, 3 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c56, c57]
  rcases lt_or_ge (t - ⌊t⌋) (776107 / 6288980 : ℝ) with c58 | c58
  · refine ⟨17, 4 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c57, c58]
  rcases lt_or_ge (t - ⌊t⌋) (245129 / 1886694 : ℝ) with c59 | c59
  · refine ⟨12, 2 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c58, c59]
  rcases lt_or_ge (t - ⌊t⌋) (1087763 / 8175674 : ℝ) with c60 | c60
  · refine ⟨9, 2 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c59, c60]
  rcases lt_or_ge (t - ⌊t⌋) (1706631 / 12577960 : ℝ) with c61 | c61
  · refine ⟨16, 3 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c60, c61]
  rcases lt_or_ge (t - ⌊t⌋) (96753 / 628898 : ℝ) with c62 | c62
  · refine ⟨31, 1 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c61, c62]
  rcases lt_or_ge (t - ⌊t⌋) (5840623 / 37733880 : ℝ) with c63 | c63
  · refine ⟨0, 10 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c62, c63]
  rcases lt_or_ge (t - ⌊t⌋) (2957219 / 18866940 : ℝ) with c64 | c64
  · refine ⟨17, 5 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c63, c64]
  rcases lt_or_ge (t - ⌊t⌋) (4472633 / 28300410 : ℝ) with c65 | c65
  · refine ⟨24, 8 + 45 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c64, c65]
  rcases lt_or_ge (t - ⌊t⌋) (4987019 / 31444900 : ℝ) with c66 | c66
  · refine ⟨7, 8 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c65, c66]
  rcases lt_or_ge (t - ⌊t⌋) (2530383 / 15722450 : ℝ) with c67 | c67
  · refine ⟨6, 4 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c66, c67]
  rcases lt_or_ge (t - ⌊t⌋) (2443343 / 15093552 : ℝ) with c68 | c68
  · refine ⟨1, 4 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c67, c68]
  rcases lt_or_ge (t - ⌊t⌋) (545633 / 3144490 : ℝ) with c69 | c69
  · refine ⟨32, 1 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c68, c69]
  rcases lt_or_ge (t - ⌊t⌋) (1761167 / 10062368 : ℝ) with c70 | c70
  · refine ⟨30, 3 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c69, c70]
  rcases lt_or_ge (t - ⌊t⌋) (2010353 / 11320164 : ℝ) with c71 | c71
  · refine ⟨21, 4 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c70, c71]
  rcases lt_or_ge (t - ⌊t⌋) (2931719 / 16351348 : ℝ) with c72 | c72
  · refine ⟨18, 5 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c71, c72]
  rcases lt_or_ge (t - ⌊t⌋) (3190357 / 17609144 : ℝ) with c73 | c73
  · refine ⟨26, 6 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c72, c73]
  rcases lt_or_ge (t - ⌊t⌋) (5048899 / 27671512 : ℝ) with c74 | c74
  · refine ⟨8, 8 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c73, c74]
  rcases lt_or_ge (t - ⌊t⌋) (495551 / 2515592 : ℝ) with c75 | c75
  · refine ⟨22, 1 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c74, c75]
  rcases lt_or_ge (t - ⌊t⌋) (4492319 / 22640328 : ℝ) with c76 | c76
  · refine ⟨15, 8 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c75, c76]
  rcases lt_or_ge (t - ⌊t⌋) (6026603 / 30187104 : ℝ) with c77 | c77
  · refine ⟨19, 10 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c76, c77]
  rcases lt_or_ge (t - ⌊t⌋) (4053209 / 20124736 : ℝ) with c78 | c78
  · refine ⟨2, 7 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c77, c78]
  rcases lt_or_ge (t - ⌊t⌋) (3072241 / 15093552 : ℝ) with c79 | c79
  · refine ⟨1, 5 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c78, c79]
  rcases lt_or_ge (t - ⌊t⌋) (1815397 / 8804572 : ℝ) with c80 | c80
  · refine ⟨28, 3 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c79, c80]
  rcases lt_or_ge (t - ⌊t⌋) (814913 / 3773388 : ℝ) with c81 | c81
  · refine ⟨5, 2 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c80, c81]
  rcases lt_or_ge (t - ⌊t⌋) (3560617 / 16351348 : ℝ) with c82 | c82
  · refine ⟨18, 6 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c81, c82]
  rcases lt_or_ge (t - ⌊t⌋) (991611 / 4402286 : ℝ) with c83 | c83
  · refine ⟨20, 2 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c82, c83]
  rcases lt_or_ge (t - ⌊t⌋) (1161373 / 5031184 : ℝ) with c84 | c84
  · refine ⟨14, 2 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c83, c84]
  rcases lt_or_ge (t - ⌊t⌋) (2639251 / 11320164 : ℝ) with c85 | c85
  · refine ⟨21, 5 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c84, c85]
  rcases lt_or_ge (t - ⌊t⌋) (2964427 / 12577960 : ℝ) with c86 | c86
  · refine ⟨16, 5 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c85, c86]
  rcases lt_or_ge (t - ⌊t⌋) (1364285 / 5660082 : ℝ) with c87 | c87
  · refine ⟨12, 3 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c86, c87]
  rcases lt_or_ge (t - ⌊t⌋) (457897 / 1886694 : ℝ) with c88 | c88
  · refine ⟨29, 7 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c87, c88]
  rcases lt_or_ge (t - ⌊t⌋) (4440333 / 18238042 : ℝ) with c89 | c89
  · refine ⟨27, 8 + 29 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c88, c89]
  rcases lt_or_ge (t - ⌊t⌋) (1233713 / 5031184 : ℝ) with c90 | c90
  · refine ⟨1, 6 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c89, c90]
  rcases lt_or_ge (t - ⌊t⌋) (629159 / 2515592 : ℝ) with c91 | c91
  · refine ⟨11, 3 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c90, c91]
  rcases lt_or_ge (t - ⌊t⌋) (6935593 / 27671512 : ℝ) with c92 | c92
  · refine ⟨8, 11 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c91, c92]
  rcases lt_or_ge (t - ⌊t⌋) (4448153 / 17609144 : ℝ) with c93 | c93
  · refine ⟨26, 8 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c92, c93]
  rcases lt_or_ge (t - ⌊t⌋) (1916705 / 7546776 : ℝ) with c94 | c94
  · refine ⟨15, 10 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c93, c94]
  rcases lt_or_ge (t - ⌊t⌋) (4189515 / 16351348 : ℝ) with c95 | c95
  · refine ⟨18, 7 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c94, c95]
  rcases lt_or_ge (t - ⌊t⌋) (197915 / 628898 : ℝ) with c96 | c96
  · refine ⟨3, 1 + 1 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c95, c96]
  rcases lt_or_ge (t - ⌊t⌋) (5378869 / 16980246 : ℝ) with c97 | c97
  · refine ⟨29, 9 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c96, c97]
  rcases lt_or_ge (t - ⌊t⌋) (7993843 / 25155920 : ℝ) with c98 | c98
  · refine ⟨23, 13 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c97, c98]
  rcases lt_or_ge (t - ⌊t⌋) (8822287 / 27671512 : ℝ) with c99 | c99
  · refine ⟨8, 14 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c98, c99]
  rcases lt_or_ge (t - ⌊t⌋) (201839 / 628898 : ℝ) with c100 | c100
  · refine ⟨6, 8 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c99, c100]
  rcases lt_or_ge (t - ⌊t⌋) (4043201 / 12577960 : ℝ) with c101 | c101
  · refine ⟨0, 20 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c100, c101]
  rcases lt_or_ge (t - ⌊t⌋) (2033903 / 6288980 : ℝ) with c102 | c102
  · refine ⟨17, 10 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c101, c102]
  rcases lt_or_ge (t - ⌊t⌋) (4502349 / 13835756 : ℝ) with c103 | c103
  · refine ⟨10, 8 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c102, c103]
  rcases lt_or_ge (t - ⌊t⌋) (2078999 / 6288980 : ℝ) with c104 | c104
  · refine ⟨4, 4 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c103, c104]
  rcases lt_or_ge (t - ⌊t⌋) (2516375 / 7546776 : ℝ) with c105 | c105
  · refine ⟨11, 4 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c104, c105]
  rcases lt_or_ge (t - ⌊t⌋) (4222223 / 12577960 : ℝ) with c106 | c106
  · refine ⟨16, 7 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c105, c106]
  rcases lt_or_ge (t - ⌊t⌋) (2545603 / 7546776 : ℝ) with c107 | c107
  · refine ⟨15, 13 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c106, c107]
  rcases lt_or_ge (t - ⌊t⌋) (12758501 / 37733880 : ℝ) with c108 | c108
  · refine ⟨0, 21 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c107, c108]
  rcases lt_or_ge (t - ⌊t⌋) (1075511 / 3144490 : ℝ) with c109 | c109
  · refine ⟨13, 6 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c108, c109]
  rcases lt_or_ge (t - ⌊t⌋) (3897047 / 11320164 : ℝ) with c110 | c110
  · refine ⟨21, 7 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c109, c110]
  rcases lt_or_ge (t - ⌊t⌋) (10428889 / 30187104 : ℝ) with c111 | c111
  · refine ⟨19, 17 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c110, c111]
  rcases lt_or_ge (t - ⌊t⌋) (3073193 / 8804572 : ℝ) with c112 | c112
  · refine ⟨28, 5 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c111, c112]
  rcases lt_or_ge (t - ⌊t⌋) (1790271 / 5031184 : ℝ) with c113 | c113
  · refine ⟨14, 3 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c112, c113]
  rcases lt_or_ge (t - ⌊t⌋) (7197699 / 20124736 : ℝ) with c114 | c114
  · refine ⟨2, 12 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c113, c114]
  rcases lt_or_ge (t - ⌊t⌋) (6334847 / 17609144 : ℝ) with c115 | c115
  · refine ⟨26, 11 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c114, c115]
  rcases lt_or_ge (t - ⌊t⌋) (1620509 / 4402286 : ℝ) with c116 | c116
  · refine ⟨20, 3 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c115, c116]
  rcases lt_or_ge (t - ⌊t⌋) (1174531 / 3144490 : ℝ) with c117 | c117
  · refine ⟨32, 2 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c116, c117]
  rcases lt_or_ge (t - ⌊t⌋) (1443811 / 3773388 : ℝ) with c118 | c118
  · refine ⟨5, 3 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c117, c118]
  rcases lt_or_ge (t - ⌊t⌋) (507961 / 1257796 : ℝ) with c119 | c119
  · refine ⟨25, 1 + 2 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c118, c119]
  rcases lt_or_ge (t - ⌊t⌋) (15274093 / 37733880 : ℝ) with c120 | c120
  · refine ⟨0, 25 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c119, c120]
  rcases lt_or_ge (t - ⌊t⌋) (3855431 / 9433470 : ℝ) with c121 | c121
  · refine ⟨13, 7 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c120, c121]
  rcases lt_or_ge (t - ⌊t⌋) (6705107 / 16351348 : ℝ) with c122 | c122
  · refine ⟨18, 11 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c121, c122]
  rcases lt_or_ge (t - ⌊t⌋) (6216731 / 15093552 : ℝ) with c123 | c123
  · refine ⟨1, 10 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c122, c123]
  rcases lt_or_ge (t - ⌊t⌋) (3145273 / 7546776 : ℝ) with c124 | c124
  · refine ⟨11, 5 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c123, c124]
  rcases lt_or_ge (t - ⌊t⌋) (3702091 / 8804572 : ℝ) with c125 | c125
  · refine ⟨28, 6 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c124, c125]
  rcases lt_or_ge (t - ⌊t⌋) (5300997 / 12577960 : ℝ) with c126 | c126
  · refine ⟨0, 26 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c125, c126]
  rcases lt_or_ge (t - ⌊t⌋) (4276759 / 10062368 : ℝ) with c127 | c127
  · refine ⟨30, 7 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c126, c127]
  rcases lt_or_ge (t - ⌊t⌋) (2707897 / 6288980 : ℝ) with c128 | c128
  · refine ⟨4, 5 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c127, c128]
  rcases lt_or_ge (t - ⌊t⌋) (7592643 / 17609144 : ℝ) with c129 | c129
  · refine ⟨26, 13 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c128, c129]
  rcases lt_or_ge (t - ⌊t⌋) (11966777 / 27671512 : ℝ) with c130 | c130
  · refine ⟨8, 19 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c129, c130]
  rcases lt_or_ge (t - ⌊t⌋) (1124449 / 2515592 : ℝ) with c131 | c131
  · refine ⟨22, 2 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c130, c131]
  rcases lt_or_ge (t - ⌊t⌋) (7334005 / 16351348 : ℝ) with c132 | c132
  · refine ⟨18, 12 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c131, c132]
  rcases lt_or_ge (t - ⌊t⌋) (8213721 / 18238042 : ℝ) with c133 | c133
  · refine ⟨27, 14 + 29 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c132, c133]
  rcases lt_or_ge (t - ⌊t⌋) (9084393 / 20124736 : ℝ) with c134 | c134
  · refine ⟨2, 15 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c133, c134]
  rcases lt_or_ge (t - ⌊t⌋) (6845629 / 15093552 : ℝ) with c135 | c135
  · refine ⟨1, 11 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c134, c135]
  rcases lt_or_ge (t - ⌊t⌋) (1718281 / 3773388 : ℝ) with c136 | c136
  · refine ⟨21, 9 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c135, c136]
  rcases lt_or_ge (t - ⌊t⌋) (8617301 / 18866940 : ℝ) with c137 | c137
  · refine ⟨17, 14 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c136, c137]
  rcases lt_or_ge (t - ⌊t⌋) (874027 / 1886694 : ℝ) with c138 | c138
  · refine ⟨12, 5 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c137, c138]
  rcases lt_or_ge (t - ⌊t⌋) (2631487 / 5660082 : ℝ) with c139 | c139
  · refine ⟨29, 13 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c138, c139]
  rcases lt_or_ge (t - ⌊t⌋) (8221541 / 17609144 : ℝ) with c140 | c140
  · refine ⟨26, 14 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c139, c140]
  rcases lt_or_ge (t - ⌊t⌋) (11767231 / 25155920 : ℝ) with c141 | c141
  · refine ⟨23, 19 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c140, c141]
  rcases lt_or_ge (t - ⌊t⌋) (919157 / 1886694 : ℝ) with c142 | c142
  · refine ⟨31, 2 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c141, c142]
  rcases lt_or_ge (t - ⌊t⌋) (18418583 / 37733880 : ℝ) with c143 | c143
  · refine ⟨0, 30 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c142, c143]
  rcases lt_or_ge (t - ⌊t⌋) (4330989 / 8804572 : ℝ) with c144 | c144
  · refine ⟨28, 7 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c143, c144]
  rcases lt_or_ge (t - ⌊t⌋) (12396129 / 25155920 : ℝ) with c145 | c145
  · refine ⟨23, 20 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c144, c145]
  rcases lt_or_ge (t - ⌊t⌋) (2491509 / 5031184 : ℝ) with c146 | c146
  · refine ⟨1, 12 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c145, c146]
  rcases lt_or_ge (t - ⌊t⌋) (1258057 / 2515592 : ℝ) with c147 | c147
  · refine ⟨11, 6 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c146, c147]
  rcases lt_or_ge (t - ⌊t⌋) (8523359 / 16980246 : ℝ) with c148 | c148
  · refine ⟨29, 14 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c147, c148]
  rcases lt_or_ge (t - ⌊t⌋) (8850439 / 17609144 : ℝ) with c149 | c149
  · refine ⟨26, 15 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c148, c149]
  rcases lt_or_ge (t - ⌊t⌋) (2249407 / 4402286 : ℝ) with c150 | c150
  · refine ⟨20, 4 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c149, c150]
  rcases lt_or_ge (t - ⌊t⌋) (15460073 / 30187104 : ℝ) with c151 | c151
  · refine ⟨19, 25 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c150, c151]
  rcases lt_or_ge (t - ⌊t⌋) (10342189 / 20124736 : ℝ) with c152 | c152
  · refine ⟨2, 17 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c151, c152]
  rcases lt_or_ge (t - ⌊t⌋) (4232253 / 8175674 : ℝ) with c153 | c153
  · refine ⟨9, 7 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c152, c153]
  rcases lt_or_ge (t - ⌊t⌋) (9471517 / 18238042 : ℝ) with c154 | c154
  · refine ⟨27, 16 + 29 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c153, c154]
  rcases lt_or_ge (t - ⌊t⌋) (1638093 / 3144490 : ℝ) with c155 | c155
  · refine ⟨6, 13 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c154, c155]
  rcases lt_or_ge (t - ⌊t⌋) (6558793 / 12577960 : ℝ) with c156 | c156
  · refine ⟨0, 32 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c155, c156]
  rcases lt_or_ge (t - ⌊t⌋) (3291699 / 6288980 : ℝ) with c157 | c157
  · refine ⟨17, 16 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c156, c157]
  rcases lt_or_ge (t - ⌊t⌋) (8591801 / 16351348 : ℝ) with c158 | c158
  · refine ⟨18, 14 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c157, c158]
  rcases lt_or_ge (t - ⌊t⌋) (667359 / 1257796 : ℝ) with c159 | c159
  · refine ⟨4, 6 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c158, c159]
  rcases lt_or_ge (t - ⌊t⌋) (12039095 / 22640328 : ℝ) with c160 | c160
  · refine ⟨15, 20 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c159, c160]
  rcases lt_or_ge (t - ⌊t⌋) (16088971 / 30187104 : ℝ) with c161 | c161
  · refine ⟨19, 26 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c160, c161]
  rcases lt_or_ge (t - ⌊t⌋) (1347563 / 2515592 : ℝ) with c162 | c162
  · refine ⟨16, 11 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c161, c162]
  rcases lt_or_ge (t - ⌊t⌋) (8103425 / 15093552 : ℝ) with c163 | c163
  · refine ⟨1, 13 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c162, c163]
  rcases lt_or_ge (t - ⌊t⌋) (9152257 / 16980246 : ℝ) with c164 | c164
  · refine ⟨29, 15 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c163, c164]
  rcases lt_or_ge (t - ⌊t⌋) (1704409 / 3144490 : ℝ) with c165 | c165
  · refine ⟨13, 9 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c164, c165]
  rcases lt_or_ge (t - ⌊t⌋) (690903 / 1257796 : ℝ) with c166 | c166
  · refine ⟨5, 4 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c165, c166]
  rcases lt_or_ge (t - ⌊t⌋) (5534555 / 10062368 : ℝ) with c167 | c167
  · refine ⟨30, 9 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c166, c167]
  rcases lt_or_ge (t - ⌊t⌋) (7646839 / 13835756 : ℝ) with c168 | c168
  · refine ⟨10, 13 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c167, c168]
  rcases lt_or_ge (t - ⌊t⌋) (10100415 / 18238042 : ℝ) with c169 | c169
  · refine ⟨27, 17 + 29 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c168, c169]
  rcases lt_or_ge (t - ⌊t⌋) (4186835 / 7546776 : ℝ) with c170 | c170
  · refine ⟨0, 34 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c169, c170]
  rcases lt_or_ge (t - ⌊t⌋) (2100799 / 3773388 : ℝ) with c171 | c171
  · refine ⟨17, 17 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c170, c171]
  rcases lt_or_ge (t - ⌊t⌋) (15792797 / 28300410 : ℝ) with c172 | c172
  · refine ⟨24, 26 + 45 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c171, c172]
  rcases lt_or_ge (t - ⌊t⌋) (12667993 / 22640328 : ℝ) with c173 | c173
  · refine ⟨15, 21 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c172, c173]
  rcases lt_or_ge (t - ⌊t⌋) (4959887 / 8804572 : ℝ) with c174 | c174
  · refine ⟨28, 8 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c173, c174]
  rcases lt_or_ge (t - ⌊t⌋) (1803429 / 3144490 : ℝ) with c175 | c175
  · refine ⟨32, 3 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c174, c175]
  rcases lt_or_ge (t - ⌊t⌋) (17346767 / 30187104 : ℝ) with c176 | c176
  · refine ⟨19, 28 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c175, c176]
  rcases lt_or_ge (t - ⌊t⌋) (11599985 / 20124736 : ℝ) with c177 | c177
  · refine ⟨2, 19 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c176, c177]
  rcases lt_or_ge (t - ⌊t⌋) (8732323 / 15093552 : ℝ) with c178 | c178
  · refine ⟨1, 14 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c177, c178]
  rcases lt_or_ge (t - ⌊t⌋) (4403069 / 7546776 : ℝ) with c179 | c179
  · refine ⟨11, 7 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c178, c179]
  rcases lt_or_ge (t - ⌊t⌋) (7366713 / 12577960 : ℝ) with c180 | c180
  · refine ⟨16, 12 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c179, c180]
  rcases lt_or_ge (t - ⌊t⌋) (4432297 / 7546776 : ℝ) with c181 | c181
  · refine ⟨15, 22 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c180, c181]
  rcases lt_or_ge (t - ⌊t⌋) (10729313 / 18238042 : ℝ) with c182 | c182
  · refine ⟨27, 18 + 29 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c181, c182]
  rcases lt_or_ge (t - ⌊t⌋) (11132893 / 18866940 : ℝ) with c183 | c183
  · refine ⟨17, 18 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c182, c183]
  rcases lt_or_ge (t - ⌊t⌋) (4861151 / 8175674 : ℝ) with c184 | c184
  · refine ⟨9, 8 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c183, c184]
  rcases lt_or_ge (t - ⌊t⌋) (17975665 / 30187104 : ℝ) with c185 | c185
  · refine ⟨19, 29 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c184, c185]
  rcases lt_or_ge (t - ⌊t⌋) (8275737 / 13835756 : ℝ) with c186 | c186
  · refine ⟨10, 14 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c185, c186]
  rcases lt_or_ge (t - ⌊t⌋) (752911 / 1257796 : ℝ) with c187 | c187
  · refine ⟨7, 30 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c186, c187]
  rcases lt_or_ge (t - ⌊t⌋) (3048067 / 5031184 : ℝ) with c188 | c188
  · refine ⟨14, 5 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c187, c188]
  rcases lt_or_ge (t - ⌊t⌋) (1148425 / 1886694 : ℝ) with c189 | c189
  · refine ⟨13, 10 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c188, c189]
  rcases lt_or_ge (t - ⌊t⌋) (10737133 / 17609144 : ℝ) with c190 | c190
  · refine ⟨26, 18 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c189, c190]
  rcases lt_or_ge (t - ⌊t⌋) (6163453 / 10062368 : ℝ) with c191 | c191
  · refine ⟨30, 10 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c190, c191]
  rcases lt_or_ge (t - ⌊t⌋) (10410053 / 16980246 : ℝ) with c192 | c192
  · refine ⟨29, 17 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c191, c192]
  rcases lt_or_ge (t - ⌊t⌋) (16997961 / 27671512 : ℝ) with c193 | c193
  · refine ⟨8, 27 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c192, c193]
  rcases lt_or_ge (t - ⌊t⌋) (13925789 / 22640328 : ℝ) with c194 | c194
  · refine ⟨15, 23 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c193, c194]
  rcases lt_or_ge (t - ⌊t⌋) (6201521 / 10062368 : ℝ) with c195 | c195
  · refine ⟨19, 30 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c194, c195]
  rcases lt_or_ge (t - ⌊t⌋) (15540619 / 25155920 : ℝ) with c196 | c196
  · refine ⟨23, 25 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c195, c196]
  rcases lt_or_ge (t - ⌊t⌋) (3120407 / 5031184 : ℝ) with c197 | c197
  · refine ⟨1, 15 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c196, c197]
  rcases lt_or_ge (t - ⌊t⌋) (782393 / 1257796 : ℝ) with c198 | c198
  · refine ⟨21, 12 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c197, c198]
  rcases lt_or_ge (t - ⌊t⌋) (3920597 / 6288980 : ℝ) with c199 | c199
  · refine ⟨17, 19 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c198, c199]
  rcases lt_or_ge (t - ⌊t⌋) (17679491 / 28300410 : ℝ) with c200 | c200
  · refine ⟨24, 29 + 45 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c199, c200]
  rcases lt_or_ge (t - ⌊t⌋) (3965693 / 6288980 : ℝ) with c201 | c201
  · refine ⟨4, 7 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c200, c201]
  rcases lt_or_ge (t - ⌊t⌋) (5588785 / 8804572 : ℝ) with c202 | c202
  · refine ⟨28, 9 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c201, c202]
  rcases lt_or_ge (t - ⌊t⌋) (7995611 / 12577960 : ℝ) with c203 | c203
  · refine ⟨16, 13 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c202, c203]
  rcases lt_or_ge (t - ⌊t⌋) (17626859 / 27671512 : ℝ) with c204 | c204
  · refine ⟨8, 28 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c203, c204]
  rcases lt_or_ge (t - ⌊t⌋) (19233461 / 30187104 : ℝ) with c205 | c205
  · refine ⟨19, 31 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c204, c205]
  rcases lt_or_ge (t - ⌊t⌋) (12857781 / 20124736 : ℝ) with c206 | c206
  · refine ⟨2, 21 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c205, c206]
  rcases lt_or_ge (t - ⌊t⌋) (10077159 / 15722450 : ℝ) with c207 | c207
  · refine ⟨6, 16 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c206, c207]
  rcases lt_or_ge (t - ⌊t⌋) (8904635 / 13835756 : ℝ) with c208 | c208
  · refine ⟨10, 15 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c207, c208]
  rcases lt_or_ge (t - ⌊t⌋) (11366031 / 17609144 : ℝ) with c209 | c209
  · refine ⟨26, 19 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c208, c209]
  rcases lt_or_ge (t - ⌊t⌋) (2878305 / 4402286 : ℝ) with c210 | c210
  · refine ⟨20, 5 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c209, c210]
  rcases lt_or_ge (t - ⌊t⌋) (24707563 / 37733880 : ℝ) with c211 | c211
  · refine ⟨0, 40 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c210, c211]
  rcases lt_or_ge (t - ⌊t⌋) (12390689 / 18866940 : ℝ) with c212 | c212
  · refine ⟨17, 20 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c211, c212]
  rcases lt_or_ge (t - ⌊t⌋) (11987109 / 18238042 : ℝ) with c213 | c213
  · refine ⟨27, 20 + 29 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c212, c213]
  rcases lt_or_ge (t - ⌊t⌋) (19862359 / 30187104 : ℝ) with c214 | c214
  · refine ⟨19, 32 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c213, c214]
  rcases lt_or_ge (t - ⌊t⌋) (20709469 / 31444900 : ℝ) with c215 | c215
  · refine ⟨7, 33 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c214, c215]
  rcases lt_or_ge (t - ⌊t⌋) (18255757 / 27671512 : ℝ) with c216 | c216
  · refine ⟨8, 29 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c215, c216]
  rcases lt_or_ge (t - ⌊t⌋) (9990119 / 15093552 : ℝ) with c217 | c217
  · refine ⟨1, 16 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c216, c217]
  rcases lt_or_ge (t - ⌊t⌋) (5031967 / 7546776 : ℝ) with c218 | c218
  · refine ⟨11, 8 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c217, c218]
  rcases lt_or_ge (t - ⌊t⌋) (3359683 / 5031184 : ℝ) with c219 | c219
  · refine ⟨23, 27 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c218, c219]
  rcases lt_or_ge (t - ⌊t⌋) (5490049 / 8175674 : ℝ) with c220 | c220
  · refine ⟨9, 9 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c219, c220]
  rcases lt_or_ge (t - ⌊t⌋) (6371023 / 9433470 : ℝ) with c221 | c221
  · refine ⟨13, 11 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c220, c221]
  rcases lt_or_ge (t - ⌊t⌋) (7670435 / 11320164 : ℝ) with c222 | c222
  · refine ⟨21, 13 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c221, c222]
  rcases lt_or_ge (t - ⌊t⌋) (11107393 / 16351348 : ℝ) with c223 | c223
  · refine ⟨18, 18 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c222, c223]
  rcases lt_or_ge (t - ⌊t⌋) (3879877 / 5660082 : ℝ) with c224 | c224
  · refine ⟨12, 7 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c223, c224]
  rcases lt_or_ge (t - ⌊t⌋) (1753347 / 2515592 : ℝ) with c225 | c225
  · refine ⟨22, 3 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c224, c225]
  rcases lt_or_ge (t - ⌊t⌋) (15812483 / 22640328 : ℝ) with c226 | c226
  · refine ⟨15, 26 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c225, c226]
  rcases lt_or_ge (t - ⌊t⌋) (21120155 / 30187104 : ℝ) with c227 | c227
  · refine ⟨19, 34 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c226, c227]
  rcases lt_or_ge (t - ⌊t⌋) (14115577 / 20124736 : ℝ) with c228 | c228
  · refine ⟨2, 23 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c227, c228]
  rcases lt_or_ge (t - ⌊t⌋) (10619017 / 15093552 : ℝ) with c229 | c229
  · refine ⟨1, 17 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c228, c229]
  rcases lt_or_ge (t - ⌊t⌋) (6217683 / 8804572 : ℝ) with c230 | c230
  · refine ⟨28, 10 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c229, c230]
  rcases lt_or_ge (t - ⌊t⌋) (2701607 / 3773388 : ℝ) with c231 | c231
  · refine ⟨5, 5 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c230, c231]
  rcases lt_or_ge (t - ⌊t⌋) (11736291 / 16351348 : ℝ) with c232 | c232
  · refine ⟨18, 19 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c231, c232]
  rcases lt_or_ge (t - ⌊t⌋) (22596163 / 31444900 : ℝ) with c233 | c233
  · refine ⟨7, 36 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c232, c233]
  rcases lt_or_ge (t - ⌊t⌋) (2266991 / 3144490 : ℝ) with c234 | c234
  · refine ⟨6, 18 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c233, c234]
  rcases lt_or_ge (t - ⌊t⌋) (1814877 / 2515592 : ℝ) with c235 | c235
  · refine ⟨0, 44 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c234, c235]
  rcases lt_or_ge (t - ⌊t⌋) (909899 / 1257796 : ℝ) with c236 | c236
  · refine ⟨17, 22 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c235, c236]
  rcases lt_or_ge (t - ⌊t⌋) (12296747 / 16980246 : ℝ) with c237 | c237
  · refine ⟨29, 20 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c236, c237]
  rcases lt_or_ge (t - ⌊t⌋) (3676965 / 5031184 : ℝ) with c238 | c238
  · refine ⟨14, 6 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c237, c238]
  rcases lt_or_ge (t - ⌊t⌋) (8299333 / 11320164 : ℝ) with c239 | c239
  · refine ⟨21, 14 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c238, c239]
  rcases lt_or_ge (t - ⌊t⌋) (9253407 / 12577960 : ℝ) with c240 | c240
  · refine ⟨16, 15 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c239, c240]
  rcases lt_or_ge (t - ⌊t⌋) (7421249 / 10062368 : ℝ) with c241 | c241
  · refine ⟨30, 12 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c240, c241]
  rcases lt_or_ge (t - ⌊t⌋) (23225061 / 31444900 : ℝ) with c242 | c242
  · refine ⟨7, 37 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c241, c242]
  rcases lt_or_ge (t - ⌊t⌋) (2333307 / 3144490 : ℝ) with c243 | c243
  · refine ⟨13, 12 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c242, c243]
  rcases lt_or_ge (t - ⌊t⌋) (18685109 / 25155920 : ℝ) with c244 | c244
  · refine ⟨23, 30 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c243, c244]
  rcases lt_or_ge (t - ⌊t⌋) (3749305 / 5031184 : ℝ) with c245 | c245
  · refine ⟨1, 18 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c244, c245]
  rcases lt_or_ge (t - ⌊t⌋) (1886955 / 2515592 : ℝ) with c246 | c246
  · refine ⟨11, 9 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c245, c246]
  rcases lt_or_ge (t - ⌊t⌋) (20771349 / 27671512 : ℝ) with c247 | c247
  · refine ⟨8, 33 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c246, c247]
  rcases lt_or_ge (t - ⌊t⌋) (13252725 / 17609144 : ℝ) with c248 | c248
  · refine ⟨26, 22 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c247, c248]
  rcases lt_or_ge (t - ⌊t⌋) (5690093 / 7546776 : ℝ) with c249 | c249
  · refine ⟨15, 28 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c248, c249]
  rcases lt_or_ge (t - ⌊t⌋) (12365189 / 16351348 : ℝ) with c250 | c250
  · refine ⟨18, 20 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c249, c250]
  rcases lt_or_ge (t - ⌊t⌋) (14277383 / 18866940 : ℝ) with c251 | c251
  · refine ⟨17, 23 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c250, c251]
  rcases lt_or_ge (t - ⌊t⌋) (21452879 / 28300410 : ℝ) with c252 | c252
  · refine ⟨24, 35 + 45 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c251, c252]
  rcases lt_or_ge (t - ⌊t⌋) (23853959 / 31444900 : ℝ) with c253 | c253
  · refine ⟨7, 38 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c252, c253]
  rcases lt_or_ge (t - ⌊t⌋) (11963853 / 15722450 : ℝ) with c254 | c254
  · refine ⟨6, 19 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c253, c254]
  rcases lt_or_ge (t - ⌊t⌋) (23006849 / 30187104 : ℝ) with c255 | c255
  · refine ⟨19, 37 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c254, c255]
  rcases lt_or_ge (t - ⌊t⌋) (2432327 / 3144490 : ℝ) with c256 | c256
  · refine ⟨32, 4 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c255, c256]
  rcases lt_or_ge (t - ⌊t⌋) (978083 / 1257796 : ℝ) with c257 | c257
  · refine ⟨28, 11 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c256, c257]
  rcases lt_or_ge (t - ⌊t⌋) (10791329 / 13835756 : ℝ) with c258 | c258
  · refine ⟨10, 18 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c257, c258]
  rcases lt_or_ge (t - ⌊t⌋) (22081777 / 28300410 : ℝ) with c259 | c259
  · refine ⟨24, 36 + 45 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c258, c259]
  rcases lt_or_ge (t - ⌊t⌋) (17699177 / 22640328 : ℝ) with c260 | c260
  · refine ⟨15, 29 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c259, c260]
  rcases lt_or_ge (t - ⌊t⌋) (23635747 / 30187104 : ℝ) with c261 | c261
  · refine ⟨19, 38 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c260, c261]
  rcases lt_or_ge (t - ⌊t⌋) (1976461 / 2515592 : ℝ) with c262 | c262
  · refine ⟨16, 16 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c261, c262]
  rcases lt_or_ge (t - ⌊t⌋) (2976077 / 3773388 : ℝ) with c263 | c263
  · refine ⟨21, 15 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c262, c263]
  rcases lt_or_ge (t - ⌊t⌋) (501029 / 628898 : ℝ) with c264 | c264
  · refine ⟨20, 6 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c263, c264]
  rcases lt_or_ge (t - ⌊t⌋) (8050147 / 10062368 : ℝ) with c265 | c265
  · refine ⟨30, 13 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c264, c265]
  rcases lt_or_ge (t - ⌊t⌋) (12592751 / 15722450 : ℝ) with c266 | c266
  · refine ⟨6, 20 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c265, c266]
  rcases lt_or_ge (t - ⌊t⌋) (1548055 / 1886694 : ℝ) with c267 | c267
  · refine ⟨31, 3 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c266, c267]
  rcases lt_or_ge (t - ⌊t⌋) (10332181 / 12577960 : ℝ) with c268 | c268
  · refine ⟨0, 50 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c267, c268]
  rcases lt_or_ge (t - ⌊t⌋) (519065 / 628898 : ℝ) with c269 | c269
  · refine ⟨9, 11 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c268, c269]
  rcases lt_or_ge (t - ⌊t⌋) (5223489 / 6288980 : ℝ) with c270 | c270
  · refine ⟨4, 9 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c269, c270]
  rcases lt_or_ge (t - ⌊t⌋) (6289763 / 7546776 : ℝ) with c271 | c271
  · refine ⟨11, 10 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c270, c271]
  rcases lt_or_ge (t - ⌊t⌋) (10511203 / 12577960 : ℝ) with c272 | c272
  · refine ⟨16, 17 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c271, c272]
  rcases lt_or_ge (t - ⌊t⌋) (6318991 / 7546776 : ℝ) with c273 | c273
  · refine ⟨15, 31 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c272, c273]
  rcases lt_or_ge (t - ⌊t⌋) (31625441 / 37733880 : ℝ) with c274 | c274
  · refine ⟨0, 51 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c273, c274]
  rcases lt_or_ge (t - ⌊t⌋) (26369551 / 31444900 : ℝ) with c275 | c275
  · refine ⟨7, 42 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c274, c275]
  rcases lt_or_ge (t - ⌊t⌋) (13221649 / 15722450 : ℝ) with c276 | c276
  · refine ⟨6, 21 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c275, c276]
  rcases lt_or_ge (t - ⌊t⌋) (23286941 / 27671512 : ℝ) with c277 | c277
  · refine ⟨8, 37 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c276, c277]
  rcases lt_or_ge (t - ⌊t⌋) (9557129 / 11320164 : ℝ) with c278 | c278
  · refine ⟨21, 16 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c277, c278]
  rcases lt_or_ge (t - ⌊t⌋) (25522441 / 30187104 : ℝ) with c279 | c279
  · refine ⟨19, 41 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c278, c279]
  rcases lt_or_ge (t - ⌊t⌋) (7475479 / 8804572 : ℝ) with c280 | c280
  · refine ⟨28, 12 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c279, c280]
  rcases lt_or_ge (t - ⌊t⌋) (4305863 / 5031184 : ℝ) with c281 | c281
  · refine ⟨14, 7 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c280, c281]
  rcases lt_or_ge (t - ⌊t⌋) (17260067 / 20124736 : ℝ) with c282 | c282
  · refine ⟨2, 28 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c281, c282]
  rcases lt_or_ge (t - ⌊t⌋) (15139419 / 17609144 : ℝ) with c283 | c283
  · refine ⟨26, 25 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c282, c283]
  rcases lt_or_ge (t - ⌊t⌋) (8679045 / 10062368 : ℝ) with c284 | c284
  · refine ⟨30, 14 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c283, c284]
  rcases lt_or_ge (t - ⌊t⌋) (15760497 / 18238042 : ℝ) with c285 | c285
  · refine ⟨27, 26 + 29 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c284, c285]
  rcases lt_or_ge (t - ⌊t⌋) (19585871 / 22640328 : ℝ) with c286 | c286
  · refine ⟨15, 32 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c285, c286]
  rcases lt_or_ge (t - ⌊t⌋) (8717113 / 10062368 : ℝ) with c287 | c287
  · refine ⟨19, 42 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c286, c287]
  rcases lt_or_ge (t - ⌊t⌋) (21829599 / 25155920 : ℝ) with c288 | c288
  · refine ⟨23, 35 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c287, c288]
  rcases lt_or_ge (t - ⌊t⌋) (4378203 / 5031184 : ℝ) with c289 | c289
  · refine ⟨1, 21 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c288, c289]
  rcases lt_or_ge (t - ⌊t⌋) (14812339 / 16980246 : ℝ) with c290 | c290
  · refine ⟨29, 24 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c289, c290]
  rcases lt_or_ge (t - ⌊t⌋) (8257717 / 9433470 : ℝ) with c291 | c291
  · refine ⟨13, 14 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c290, c291]
  rcases lt_or_ge (t - ⌊t⌋) (1136859 / 1257796 : ℝ) with c292 | c292
  · refine ⟨25, 2 + 2 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c291, c292]
  rcases lt_or_ge (t - ⌊t⌋) (5137673 / 5660082 : ℝ) with c293 | c293
  · refine ⟨12, 9 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c292, c293]
  rcases lt_or_ge (t - ⌊t⌋) (1715693 / 1886694 : ℝ) with c294 | c294
  · refine ⟨29, 25 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c293, c294]
  rcases lt_or_ge (t - ⌊t⌋) (14880781 / 16351348 : ℝ) with c295 | c295
  · refine ⟨18, 24 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c294, c295]
  rcases lt_or_ge (t - ⌊t⌋) (13763507 / 15093552 : ℝ) with c296 | c296
  · refine ⟨1, 22 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c295, c296]
  rcases lt_or_ge (t - ⌊t⌋) (6918661 / 7546776 : ℝ) with c297 | c297
  · refine ⟨11, 11 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c296, c297]
  rcases lt_or_ge (t - ⌊t⌋) (8104377 / 8804572 : ℝ) with c298 | c298
  · refine ⟨28, 13 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c297, c298]
  rcases lt_or_ge (t - ⌊t⌋) (11589977 / 12577960 : ℝ) with c299 | c299
  · refine ⟨0, 56 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c298, c299]
  rcases lt_or_ge (t - ⌊t⌋) (9307943 / 10062368 : ℝ) with c300 | c300
  · refine ⟨30, 15 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c299, c300]
  rcases lt_or_ge (t - ⌊t⌋) (5852387 / 6288980 : ℝ) with c301 | c301
  · refine ⟨4, 10 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c300, c301]
  rcases lt_or_ge (t - ⌊t⌋) (16397215 / 17609144 : ℝ) with c302 | c302
  · refine ⟨26, 27 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c301, c302]
  rcases lt_or_ge (t - ⌊t⌋) (4136101 / 4402286 : ℝ) with c303 | c303
  · refine ⟨20, 7 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c302, c303]
  rcases lt_or_ge (t - ⌊t⌋) (2382245 / 2515592 : ℝ) with c304 | c304
  · refine ⟨22, 4 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c303, c304]
  rcases lt_or_ge (t - ⌊t⌋) (15509679 / 16351348 : ℝ) with c305 | c305
  · refine ⟨18, 25 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c304, c305]
  rcases lt_or_ge (t - ⌊t⌋) (28666931 / 30187104 : ℝ) with c306 | c306
  · refine ⟨19, 46 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c305, c306]
  rcases lt_or_ge (t - ⌊t⌋) (19146761 / 20124736 : ℝ) with c307 | c307
  · refine ⟨2, 31 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c306, c307]
  rcases lt_or_ge (t - ⌊t⌋) (14392405 / 15093552 : ℝ) with c308 | c308
  · refine ⟨1, 23 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c307, c308]
  rcases lt_or_ge (t - ⌊t⌋) (3604975 / 3773388 : ℝ) with c309 | c309
  · refine ⟨21, 18 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c308, c309]
  rcases lt_or_ge (t - ⌊t⌋) (18050771 / 18866940 : ℝ) with c310 | c310
  · refine ⟨17, 29 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c309, c310]
  rcases lt_or_ge (t - ⌊t⌋) (27112961 / 28300410 : ℝ) with c311 | c311
  · refine ⟨24, 44 + 45 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c310, c311]
  rcases lt_or_ge (t - ⌊t⌋) (30142939 / 31444900 : ℝ) with c312 | c312
  · refine ⟨7, 48 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c311, c312]
  rcases lt_or_ge (t - ⌊t⌋) (15108343 / 15722450 : ℝ) with c313 | c313
  · refine ⟨6, 24 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c312, c313]
  rcases lt_or_ge (t - ⌊t⌋) (13306921 / 13835756 : ℝ) with c314 | c314
  · refine ⟨10, 22 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c313, c314]
  rcases lt_or_ge (t - ⌊t⌋) (612245 / 628898 : ℝ) with c315 | c315
  · refine ⟨32, 5 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c314, c315]
  rcases lt_or_ge (t - ⌊t⌋) (4934761 / 5031184 : ℝ) with c316 | c316
  · refine ⟨14, 8 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c315, c316]
  rcases lt_or_ge (t - ⌊t⌋) (19775659 / 20124736 : ℝ) with c317 | c317
  · refine ⟨2, 32 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c316, c317]
  rcases lt_or_ge (t - ⌊t⌋) (16699033 / 16980246 : ℝ) with c318 | c318
  · refine ⟨29, 27 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c317, c318]
  rcases lt_or_ge (t - ⌊t⌋) (12397897 / 12577960 : ℝ) with c319 | c319
  · refine ⟨16, 20 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c318, c319]
  rcases lt_or_ge (t - ⌊t⌋) (9936841 / 10062368 : ℝ) with c320 | c320
  · refine ⟨30, 16 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c319, c320]
  rcases lt_or_ge (t - ⌊t⌋) (37285523 / 37733880 : ℝ) with c321 | c321
  · refine ⟨0, 60 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c320, c321]
  rcases lt_or_ge (t - ⌊t⌋) (8733275 / 8804572 : ℝ) with c322 | c322
  · refine ⟨28, 14 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c321, c322]
  rcases lt_or_ge (t - ⌊t⌋) (24974089 / 25155920 : ℝ) with c323 | c323
  · refine ⟨23, 40 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c322, c323]
  rcases lt_or_ge (t - ⌊t⌋) (5007101 / 5031184 : ℝ) with c324 | c324
  · refine ⟨1, 24 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c323, c324]
  refine ⟨11, 12 + 12 * ⌊t⌋, ?_⟩
  simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
  rw [abs_lt]
  push_cast
  constructor <;> linarith only [c324, h1]

#print axioms cover
#print axioms v_injective
#print axioms v_pos
end SLRAudit.N33
