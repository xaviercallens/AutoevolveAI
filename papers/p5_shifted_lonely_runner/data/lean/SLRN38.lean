import Mathlib.Tactic

set_option linter.unusedSimpArgs false
set_option maxHeartbeats 0
namespace SLRAudit.N38

/-- velocities of certificate n = 38 -/
def v : Fin 38 → ℕ := ![31, 2, 3, 4, 5, 6, 64, 8, 54, 10, 50, 12, 42, 14, 15, 16, 17, 9, 60, 20, 21, 56, 24, 75, 40, 43, 26, 28, 48, 1, 44, 30, 22, 32, 18, 36, 34, 27]
/-- shifts s_i = a_i / 24337 -/
def s : Fin 38 → ℚ := ![1305/24337, 5833/24337, 2587/24337, 17532/24337, 7309/24337, 23902/24337, 18068/24337, 4057/24337, 4455/24337, 12781/24337, 6923/24337, 20299/24337, 7830/24337, 5527/24337, 3700/24337, 13077/24337, 17361/24337, 20084/24337, 9676/24337, 18621/24337, 2243/24337, 11852/24337, 3113/24337, 8830/24337, 16784/24337, 23279/24337, 22659/24337, 8709/24337, 4360/24337, 14151/24337, 14901/24337, 11519/24337, 3119/24337, 7737/24337, 11198/24337, 1934/24337, 1242/24337, 9091/24337]

theorem v_injective : Function.Injective v := by decide
theorem v_pos : ∀ i, 0 < v i := by decide

/-- covering: for every real t some runner is within distance < 1/39 of an integer. -/
theorem cover : ∀ t : ℝ, ∃ i : Fin 38, ∃ k : ℤ, |((s i : ℚ) : ℝ) + ((v i : ℕ) : ℝ) * t - (k : ℝ)| < 1 / 39 := by
  intro t
  have h0 : (0 : ℝ) ≤ t - ⌊t⌋ := by have := Int.floor_le t; linarith
  have h1 : t - ⌊t⌋ < (1 : ℝ) := by have := Int.lt_floor_add_one t; linarith
  rcases lt_or_ge (t - ⌊t⌋) (20651 / 2847429 : ℝ) with c0 | c0
  · refine ⟨5, 1 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [h0, c0]
  rcases lt_or_ge (t - ⌊t⌋) (39863 / 4745715 : ℝ) with c1 | c1
  · refine ⟨24, 1 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c0, c1]
  rcases lt_or_ge (t - ⌊t⌋) (392341 / 41762292 : ℝ) with c2 | c2
  · refine ⟨30, 1 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1, c2]
  rcases lt_or_ge (t - ⌊t⌋) (18259 / 1898286 : ℝ) with c3 | c3
  · refine ⟨21, 1 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2, c3]
  rcases lt_or_ge (t - ⌊t⌋) (149029 / 14237145 : ℝ) with c4 | c4
  · refine ⟨18, 1 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c3, c4]
  rcases lt_or_ge (t - ⌊t⌋) (247261 / 18982860 : ℝ) with c5 | c5
  · refine ⟨19, 1 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c4, c5]
  rcases lt_or_ge (t - ⌊t⌋) (181819 / 11389716 : ℝ) with c6 | c6
  · refine ⟨11, 1 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c5, c6]
  rcases lt_or_ge (t - ⌊t⌋) (296401 / 16135431 : ℝ) with c7 | c7
  · refine ⟨16, 1 + 17 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c6, c7]
  rcases lt_or_ge (t - ⌊t⌋) (190204 / 8542287 : ℝ) with c8 | c8
  · refine ⟨17, 1 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c7, c8]
  rcases lt_or_ge (t - ⌊t⌋) (618931 / 25626861 : ℝ) with c9 | c9
  · refine ⟨37, 1 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c8, c9]
  rcases lt_or_ge (t - ⌊t⌋) (1014742 / 40813149 : ℝ) with c10 | c10
  · refine ⟨25, 2 + 43 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c9, c10]
  rcases lt_or_ge (t - ⌊t⌋) (449027 / 17084574 : ℝ) with c11 | c11
  · refine ⟨35, 1 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c10, c11]
  rcases lt_or_ge (t - ⌊t⌋) (1545259 / 56948580 : ℝ) with c12 | c12
  · refine ⟨18, 2 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c11, c12]
  rcases lt_or_ge (t - ⌊t⌋) (1460395 / 53152008 : ℝ) with c13 | c13
  · refine ⟨21, 2 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c12, c13]
  rcases lt_or_ge (t - ⌊t⌋) (463477 / 15186288 : ℝ) with c14 | c14
  · refine ⟨15, 1 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c13, c14]
  rcases lt_or_ge (t - ⌊t⌋) (268379 / 8542287 : ℝ) with c15 | c15
  · refine ⟨34, 1 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c14, c15]
  rcases lt_or_ge (t - ⌊t⌋) (335371 / 10440573 : ℝ) with c16 | c16
  · refine ⟨30, 2 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c15, c16]
  rcases lt_or_ge (t - ⌊t⌋) (1268047 / 37965720 : ℝ) with c17 | c17
  · refine ⟨24, 2 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c16, c17]
  rcases lt_or_ge (t - ⌊t⌋) (874439 / 25626861 : ℝ) with c18 | c18
  · refine ⟨8, 2 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c17, c18]
  rcases lt_or_ge (t - ⌊t⌋) (826313 / 23728575 : ℝ) with c19 | c19
  · refine ⟨10, 2 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c18, c19]
  rcases lt_or_ge (t - ⌊t⌋) (2527396 / 71185725 : ℝ) with c20 | c20
  · refine ⟨23, 3 + 75 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c19, c20]
  rcases lt_or_ge (t - ⌊t⌋) (852073 / 22779432 : ℝ) with c21 | c21
  · refine ⟨22, 1 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c20, c21]
  rcases lt_or_ge (t - ⌊t⌋) (1752583 / 45558864 : ℝ) with c22 | c22
  · refine ⟨28, 2 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c21, c22]
  rcases lt_or_ge (t - ⌊t⌋) (851839 / 20881146 : ℝ) with c23 | c23
  · refine ⟨32, 1 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c22, c23]
  rcases lt_or_ge (t - ⌊t⌋) (519461 / 12338859 : ℝ) with c24 | c24
  · refine ⟨26, 2 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c23, c24]
  rcases lt_or_ge (t - ⌊t⌋) (886003 / 19932003 : ℝ) with c25 | c25
  · refine ⟨20, 1 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c24, c25]
  rcases lt_or_ge (t - ⌊t⌋) (1204769 / 26576004 : ℝ) with c26 | c26
  · refine ⟨21, 3 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c25, c26]
  rcases lt_or_ge (t - ⌊t⌋) (475021 / 9491430 : ℝ) with c27 | c27
  · refine ⟨9, 1 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c26, c27]
  rcases lt_or_ge (t - ⌊t⌋) (736691 / 14237145 : ℝ) with c28 | c28
  · refine ⟨31, 2 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c27, c28]
  rcases lt_or_ge (t - ⌊t⌋) (2698021 / 51253722 : ℝ) with c29 | c29
  · refine ⟨8, 3 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c28, c29]
  rcases lt_or_ge (t - ⌊t⌋) (1847197 / 34169148 : ℝ) with c30 | c30
  · refine ⟨35, 2 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c29, c30]
  rcases lt_or_ge (t - ⌊t⌋) (757927 / 13288002 : ℝ) with c31 | c31
  · refine ⟨13, 1 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c30, c31]
  rcases lt_or_ge (t - ⌊t⌋) (165836 / 2847429 : ℝ) with c32 | c32
  · refine ⟨14, 1 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c31, c32]
  rcases lt_or_ge (t - ⌊t⌋) (395743 / 6644001 : ℝ) with c33 | c33
  · refine ⟨27, 2 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c32, c33]
  rcases lt_or_ge (t - ⌊t⌋) (1568074 / 25626861 : ℝ) with c34 | c34
  · refine ⟨37, 2 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c33, c34]
  rcases lt_or_ge (t - ⌊t⌋) (299101 / 4745715 : ℝ) with c35 | c35
  · refine ⟨19, 2 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c34, c35]
  rcases lt_or_ge (t - ⌊t⌋) (1871728 / 29423433 : ℝ) with c36 | c36
  · refine ⟨0, 2 + 31 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c35, c36]
  rcases lt_or_ge (t - ⌊t⌋) (72433 / 949143 : ℝ) with c37 | c37
  · refine ⟨3, 1 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c36, c37]
  rcases lt_or_ge (t - ⌊t⌋) (1245544 / 16135431 : ℝ) with c38 | c38
  · refine ⟨16, 2 + 17 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c37, c38]
  rcases lt_or_ge (t - ⌊t⌋) (225152 / 2847429 : ℝ) with c39 | c39
  · refine ⟨22, 2 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c38, c39]
  rcases lt_or_ge (t - ⌊t⌋) (1988065 / 24677718 : ℝ) with c40 | c40
  · refine ⟨26, 3 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c39, c40]
  rcases lt_or_ge (t - ⌊t⌋) (699085 / 8542287 : ℝ) with c41 | c41
  · refine ⟨35, 3 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c40, c41]
  rcases lt_or_ge (t - ⌊t⌋) (5014543 / 60745152 : ℝ) with c42 | c42
  · refine ⟨6, 6 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c41, c42]
  rcases lt_or_ge (t - ⌊t⌋) (3166333 / 37965720 : ℝ) with c43 | c43
  · refine ⟨24, 4 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c42, c43]
  rcases lt_or_ge (t - ⌊t⌋) (484505 / 5694858 : ℝ) with c44 | c44
  · refine ⟨31, 3 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c43, c44]
  rcases lt_or_ge (t - ⌊t⌋) (1485901 / 17084574 : ℝ) with c45 | c45
  · refine ⟨34, 2 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c44, c45]
  rcases lt_or_ge (t - ⌊t⌋) (3515539 / 39864006 : ℝ) with c46 | c46
  · refine ⟨12, 4 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c45, c46]
  rcases lt_or_ge (t - ⌊t⌋) (6323968 / 71185725 : ℝ) with c47 | c47
  · refine ⟨23, 7 + 75 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c46, c47]
  rcases lt_or_ge (t - ⌊t⌋) (4596307 / 51253722 : ℝ) with c48 | c48
  · refine ⟨8, 5 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c47, c48]
  rcases lt_or_ge (t - ⌊t⌋) (1835146 / 19932003 : ℝ) with c49 | c49
  · refine ⟨20, 2 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c48, c49]
  rcases lt_or_ge (t - ⌊t⌋) (353155 / 3796572 : ℝ) with c50 | c50
  · refine ⟨15, 2 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c49, c50]
  rcases lt_or_ge (t - ⌊t⌋) (5341831 / 56948580 : ℝ) with c51 | c51
  · refine ⟨18, 6 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c50, c51]
  rcases lt_or_ge (t - ⌊t⌋) (2532115 / 26576004 : ℝ) with c52 | c52
  · refine ⟨27, 3 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c51, c52]
  rcases lt_or_ge (t - ⌊t⌋) (565481 / 5694858 : ℝ) with c53 | c53
  · refine ⟨11, 2 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c52, c53]
  rcases lt_or_ge (t - ⌊t⌋) (4188913 / 41762292 : ℝ) with c54 | c54
  · refine ⟨30, 5 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c53, c54]
  rcases lt_or_ge (t - ⌊t⌋) (1150003 / 11389716 : ℝ) with c55 | c55
  · refine ⟨28, 5 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c54, c55]
  rcases lt_or_ge (t - ⌊t⌋) (815257 / 7593144 : ℝ) with c56 | c56
  · refine ⟨7, 1 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c55, c56]
  rcases lt_or_ge (t - ⌊t⌋) (1028869 / 9491430 : ℝ) with c57 | c57
  · refine ⟨24, 5 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c56, c57]
  rcases lt_or_ge (t - ⌊t⌋) (3745483 / 34169148 : ℝ) with c58 | c58
  · refine ⟨35, 4 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c57, c58]
  rcases lt_or_ge (t - ⌊t⌋) (3145487 / 28474290 : ℝ) with c59 | c59
  · refine ⟨18, 7 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c58, c59]
  rcases lt_or_ge (t - ⌊t⌋) (2145547 / 18982860 : ℝ) with c60 | c60
  · refine ⟨19, 3 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c59, c60]
  rcases lt_or_ge (t - ⌊t⌋) (6912829 / 60745152 : ℝ) with c61 | c61
  · refine ⟨6, 8 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c60, c61]
  rcases lt_or_ge (t - ⌊t⌋) (2724599 / 23728575 : ℝ) with c62 | c62
  · refine ⟨10, 6 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c61, c62]
  rcases lt_or_ge (t - ⌊t⌋) (1759583 / 15186288 : ℝ) with c63 | c63
  · refine ⟨33, 4 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c62, c63]
  rcases lt_or_ge (t - ⌊t⌋) (3772471 / 32270862 : ℝ) with c64 | c64
  · refine ⟨36, 4 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c63, c64]
  rcases lt_or_ge (t - ⌊t⌋) (1685834 / 14237145 : ℝ) with c65 | c65
  · refine ⟨31, 4 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c64, c65]
  rcases lt_or_ge (t - ⌊t⌋) (1468604 / 12338859 : ℝ) with c66 | c66
  · refine ⟨26, 4 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c65, c66]
  rcases lt_or_ge (t - ⌊t⌋) (2750359 / 22779432 : ℝ) with c67 | c67
  · refine ⟨22, 3 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c66, c67]
  rcases lt_or_ge (t - ⌊t⌋) (5549155 / 45558864 : ℝ) with c68 | c68
  · refine ⟨28, 6 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c67, c68]
  rcases lt_or_ge (t - ⌊t⌋) (1778323 / 14237145 : ℝ) with c69 | c69
  · refine ⟨14, 2 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c68, c69]
  rcases lt_or_ge (t - ⌊t⌋) (853535 / 6644001 : ℝ) with c70 | c70
  · refine ⟨13, 2 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c69, c70]
  rcases lt_or_ge (t - ⌊t⌋) (1139347 / 8542287 : ℝ) with c71 | c71
  · refine ⟨17, 2 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c70, c71]
  rcases lt_or_ge (t - ⌊t⌋) (2194687 / 16135431 : ℝ) with c72 | c72
  · refine ⟨16, 3 + 17 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c71, c72]
  rcases lt_or_ge (t - ⌊t⌋) (688429 / 4745715 : ℝ) with c73 | c73
  · refine ⟨4, 1 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c72, c73]
  rcases lt_or_ge (t - ⌊t⌋) (712082 / 4745715 : ℝ) with c74 | c74
  · refine ⟨9, 2 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c73, c74]
  rcases lt_or_ge (t - ⌊t⌋) (4320811 / 28474290 : ℝ) with c75 | c75
  · refine ⟨31, 5 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c74, c75]
  rcases lt_or_ge (t - ⌊t⌋) (2026099 / 13288002 : ℝ) with c76 | c76
  · refine ⟨21, 9 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c75, c76]
  rcases lt_or_ge (t - ⌊t⌋) (2361763 / 15186288 : ℝ) with c77 | c77
  · refine ⟨15, 3 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c76, c77]
  rcases lt_or_ge (t - ⌊t⌋) (3886351 / 24677718 : ℝ) with c78 | c78
  · refine ⟨26, 5 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c77, c78]
  rcases lt_or_ge (t - ⌊t⌋) (3006881 / 18982860 : ℝ) with c79 | c79
  · refine ⟨24, 7 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c78, c79]
  rcases lt_or_ge (t - ⌊t⌋) (3181484 / 19932003 : ℝ) with c80 | c80
  · refine ⟨12, 7 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c79, c80]
  rcases lt_or_ge (t - ⌊t⌋) (9138403 / 56948580 : ℝ) with c81 | c81
  · refine ⟨18, 10 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c80, c81]
  rcases lt_or_ge (t - ⌊t⌋) (309469 / 1898286 : ℝ) with c82 | c82
  · refine ⟨19, 4 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c81, c82]
  rcases lt_or_ge (t - ⌊t⌋) (8392879 / 51253722 : ℝ) with c83 | c83
  · refine ⟨8, 9 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c82, c83]
  rcases lt_or_ge (t - ⌊t⌋) (5643769 / 34169148 : ℝ) with c84 | c84
  · refine ⟨35, 6 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c83, c84]
  rcases lt_or_ge (t - ⌊t⌋) (4430401 / 26576004 : ℝ) with c85 | c85
  · refine ⟨27, 5 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c84, c85]
  rcases lt_or_ge (t - ⌊t⌋) (990445 / 5694858 : ℝ) with c86 | c86
  · refine ⟨5, 2 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c85, c86]
  rcases lt_or_ge (t - ⌊t⌋) (8296627 / 47457150 : ℝ) with c87 | c87
  · refine ⟨10, 9 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c86, c87]
  rcases lt_or_ge (t - ⌊t⌋) (5670757 / 32270862 : ℝ) with c88 | c88
  · refine ⟨36, 6 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c87, c88]
  rcases lt_or_ge (t - ⌊t⌋) (1849634 / 10440573 : ℝ) with c89 | c89
  · refine ⟨32, 4 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c88, c89]
  rcases lt_or_ge (t - ⌊t⌋) (1354363 / 7593144 : ℝ) with c90 | c90
  · refine ⟨33, 6 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c89, c90]
  rcases lt_or_ge (t - ⌊t⌋) (2080105 / 11389716 : ℝ) with c91 | c91
  · refine ⟨11, 3 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c90, c91]
  rcases lt_or_ge (t - ⌊t⌋) (7312111 / 39864006 : ℝ) with c92 | c92
  · refine ⟨12, 8 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c91, c92]
  rcases lt_or_ge (t - ⌊t⌋) (2634977 / 14237145 : ℝ) with c93 | c93
  · refine ⟨31, 6 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c92, c93]
  rcases lt_or_ge (t - ⌊t⌋) (3733432 / 19932003 : ℝ) with c94 | c94
  · refine ⟨20, 4 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c93, c94]
  rcases lt_or_ge (t - ⌊t⌋) (5001341 / 26576004 : ℝ) with c95 | c95
  · refine ⟨21, 11 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c94, c95]
  rcases lt_or_ge (t - ⌊t⌋) (2727466 / 14237145 : ℝ) with c96 | c96
  · refine ⟨14, 3 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c95, c96]
  rcases lt_or_ge (t - ⌊t⌋) (1648228 / 8542287 : ℝ) with c97 | c97
  · refine ⟨35, 7 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c96, c97]
  rcases lt_or_ge (t - ⌊t⌋) (3143830 / 16135431 : ℝ) with c98 | c98
  · refine ⟨16, 4 + 17 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c97, c98]
  rcases lt_or_ge (t - ⌊t⌋) (2417747 / 12338859 : ℝ) with c99 | c99
  · refine ⟨26, 6 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c98, c99]
  rcases lt_or_ge (t - ⌊t⌋) (3384187 / 17084574 : ℝ) with c100 | c100
  · refine ⟨34, 4 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c99, c100]
  rcases lt_or_ge (t - ⌊t⌋) (379459 / 1898286 : ℝ) with c101 | c101
  · refine ⟨13, 3 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c100, c101]
  rcases lt_or_ge (t - ⌊t⌋) (10291165 / 51253722 : ℝ) with c102 | c102
  · refine ⟨8, 11 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c101, c102]
  rcases lt_or_ge (t - ⌊t⌋) (1344886 / 6644001 : ℝ) with c103 | c103
  · refine ⟨27, 6 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c102, c103]
  rcases lt_or_ge (t - ⌊t⌋) (4648645 / 22779432 : ℝ) with c104 | c104
  · refine ⟨22, 5 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c103, c104]
  rcases lt_or_ge (t - ⌊t⌋) (3309950 / 16135431 : ℝ) with c105 | c105
  · refine ⟨36, 7 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c104, c105]
  rcases lt_or_ge (t - ⌊t⌋) (10951825 / 53152008 : ℝ) with c106 | c106
  · refine ⟨21, 12 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c105, c106]
  rcases lt_or_ge (t - ⌊t⌋) (4130627 / 19932003 : ℝ) with c107 | c107
  · refine ⟨12, 9 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c106, c107]
  rcases lt_or_ge (t - ⌊t⌋) (989006 / 4745715 : ℝ) with c108 | c108
  · refine ⟨24, 9 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c107, c108]
  rcases lt_or_ge (t - ⌊t⌋) (6366595 / 30372576 : ℝ) with c109 | c109
  · refine ⟨33, 7 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c108, c109]
  rcases lt_or_ge (t - ⌊t⌋) (2996458 / 14237145 : ℝ) with c110 | c110
  · refine ⟨18, 13 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c109, c110]
  rcases lt_or_ge (t - ⌊t⌋) (4043833 / 18982860 : ℝ) with c111 | c111
  · refine ⟨19, 5 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c110, c111]
  rcases lt_or_ge (t - ⌊t⌋) (2233657 / 10440573 : ℝ) with c112 | c112
  · refine ⟨30, 10 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c111, c112]
  rcases lt_or_ge (t - ⌊t⌋) (10194913 / 47457150 : ℝ) with c113 | c113
  · refine ⟨10, 11 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c112, c113]
  rcases lt_or_ge (t - ⌊t⌋) (1655453 / 7593144 : ℝ) with c114 | c114
  · refine ⟨15, 4 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c113, c114]
  rcases lt_or_ge (t - ⌊t⌋) (6219097 / 28474290 : ℝ) with c115 | c115
  · refine ⟨31, 7 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c114, c115]
  rcases lt_or_ge (t - ⌊t⌋) (5620154 / 25626861 : ℝ) with c116 | c116
  · refine ⟨8, 12 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c115, c116]
  rcases lt_or_ge (t - ⌊t⌋) (7542055 / 34169148 : ℝ) with c117 | c117
  · refine ⟨35, 8 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c116, c117]
  rcases lt_or_ge (t - ⌊t⌋) (4648411 / 20881146 : ℝ) with c118 | c118
  · refine ⟨32, 5 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c117, c118]
  rcases lt_or_ge (t - ⌊t⌋) (6778415 / 30372576 : ℝ) with c119 | c119
  · refine ⟨6, 15 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c118, c119]
  rcases lt_or_ge (t - ⌊t⌋) (1487621 / 6644001 : ℝ) with c120 | c120
  · refine ⟨21, 13 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c119, c120]
  rcases lt_or_ge (t - ⌊t⌋) (6617443 / 29423433 : ℝ) with c121 | c121
  · refine ⟨0, 7 + 31 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c120, c121]
  rcases lt_or_ge (t - ⌊t⌋) (5147435 / 22779432 : ℝ) with c122 | c122
  · refine ⟨28, 11 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c121, c122]
  rcases lt_or_ge (t - ⌊t⌋) (220550 / 949143 : ℝ) with c123 | c123
  · refine ⟨7, 2 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c122, c123]
  rcases lt_or_ge (t - ⌊t⌋) (8861191 / 37965720 : ℝ) with c124 | c124
  · refine ⟨24, 10 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c123, c124]
  rcases lt_or_ge (t - ⌊t⌋) (4682575 / 19932003 : ℝ) with c125 | c125
  · refine ⟨20, 5 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c124, c125]
  rcases lt_or_ge (t - ⌊t⌋) (16764541 / 71185725 : ℝ) with c126 | c126
  · refine ⟨23, 18 + 75 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c125, c126]
  rcases lt_or_ge (t - ⌊t⌋) (9883771 / 41762292 : ℝ) with c127 | c127
  · refine ⟨30, 11 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c126, c127]
  rcases lt_or_ge (t - ⌊t⌋) (6328687 / 26576004 : ℝ) with c128 | c128
  · refine ⟨27, 7 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c127, c128]
  rcases lt_or_ge (t - ⌊t⌋) (14505973 / 60745152 : ℝ) with c129 | c129
  · refine ⟨6, 16 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c128, c129]
  rcases lt_or_ge (t - ⌊t⌋) (2088490 / 8542287 : ℝ) with c130 | c130
  · refine ⟨17, 3 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c129, c130]
  rcases lt_or_ge (t - ⌊t⌋) (6313789 / 25626861 : ℝ) with c131 | c131
  · refine ⟨37, 7 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c130, c131]
  rcases lt_or_ge (t - ⌊t⌋) (2373307 / 9491430 : ℝ) with c132 | c132
  · refine ⟨9, 3 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c131, c132]
  rcases lt_or_ge (t - ⌊t⌋) (716824 / 2847429 : ℝ) with c133 | c133
  · refine ⟨31, 8 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c132, c133]
  rcases lt_or_ge (t - ⌊t⌋) (4092973 / 16135431 : ℝ) with c134 | c134
  · refine ⟨16, 5 + 17 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c133, c134]
  rcases lt_or_ge (t - ⌊t⌋) (5079770 / 19932003 : ℝ) with c135 | c135
  · refine ⟨12, 11 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c134, c135]
  rcases lt_or_ge (t - ⌊t⌋) (3676609 / 14237145 : ℝ) with c136 | c136
  · refine ⟨14, 4 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c135, c136]
  rcases lt_or_ge (t - ⌊t⌋) (5416457 / 20881146 : ℝ) with c137 | c137
  · refine ⟨30, 12 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c136, c137]
  rcases lt_or_ge (t - ⌊t⌋) (985661 / 3796572 : ℝ) with c138 | c138
  · refine ⟨21, 15 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c137, c138]
  rcases lt_or_ge (t - ⌊t⌋) (14833261 / 56948580 : ℝ) with c139 | c139
  · refine ⟨18, 16 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c138, c139]
  rcases lt_or_ge (t - ⌊t⌋) (1248244 / 4745715 : ℝ) with c140 | c140
  · refine ⟨19, 6 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c139, c140]
  rcases lt_or_ge (t - ⌊t⌋) (757312 / 2847429 : ℝ) with c141 | c141
  · refine ⟨11, 4 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c140, c141]
  rcases lt_or_ge (t - ⌊t⌋) (2798777 / 10440573 : ℝ) with c142 | c142
  · refine ⟨32, 6 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c141, c142]
  rcases lt_or_ge (t - ⌊t⌋) (1802678 / 6644001 : ℝ) with c143 | c143
  · refine ⟨13, 4 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c142, c143]
  rcases lt_or_ge (t - ⌊t⌋) (3366890 / 12338859 : ℝ) with c144 | c144
  · refine ⟨26, 8 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c143, c144]
  rcases lt_or_ge (t - ⌊t⌋) (519845 / 1898286 : ℝ) with c145 | c145
  · refine ⟨27, 8 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c144, c145]
  rcases lt_or_ge (t - ⌊t⌋) (6521171 / 23728575 : ℝ) with c146 | c146
  · refine ⟨10, 14 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c145, c146]
  rcases lt_or_ge (t - ⌊t⌋) (3922394 / 14237145 : ℝ) with c147 | c147
  · refine ⟨23, 21 + 75 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c146, c147]
  rcases lt_or_ge (t - ⌊t⌋) (9440341 / 34169148 : ℝ) with c148 | c148
  · refine ⟨35, 10 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c147, c148]
  rcases lt_or_ge (t - ⌊t⌋) (3945601 / 14237145 : ℝ) with c149 | c149
  · refine ⟨18, 17 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c148, c149]
  rcases lt_or_ge (t - ⌊t⌋) (14748397 / 53152008 : ℝ) with c150 | c150
  · refine ⟨21, 16 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c149, c150]
  rcases lt_or_ge (t - ⌊t⌋) (4260049 / 15186288 : ℝ) with c151 | c151
  · refine ⟨15, 5 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c150, c151]
  rcases lt_or_ge (t - ⌊t⌋) (5631718 / 19932003 : ℝ) with c152 | c152
  · refine ⟨20, 6 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c151, c152]
  rcases lt_or_ge (t - ⌊t⌋) (7262932 / 25626861 : ℝ) with c153 | c153
  · refine ⟨37, 8 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c152, c153]
  rcases lt_or_ge (t - ⌊t⌋) (8117383 / 28474290 : ℝ) with c154 | c154
  · refine ⟨31, 9 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c153, c154]
  rcases lt_or_ge (t - ⌊t⌋) (8676701 / 30372576 : ℝ) with c155 | c155
  · refine ⟨6, 19 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c154, c155]
  rcases lt_or_ge (t - ⌊t⌋) (6546931 / 22779432 : ℝ) with c156 | c156
  · refine ⟨22, 7 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c155, c156]
  rcases lt_or_ge (t - ⌊t⌋) (13142299 / 45558864 : ℝ) with c157 | c157
  · refine ⟨28, 14 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c156, c157]
  rcases lt_or_ge (t - ⌊t⌋) (8515729 / 29423433 : ℝ) with c158 | c158
  · refine ⟨0, 9 + 31 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c157, c158]
  rcases lt_or_ge (t - ⌊t⌋) (872587 / 2847429 : ℝ) with c159 | c159
  · refine ⟨2, 1 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c158, c159]
  rcases lt_or_ge (t - ⌊t⌋) (5282473 / 17084574 : ℝ) with c160 | c160
  · refine ⟨34, 6 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c159, c160]
  rcases lt_or_ge (t - ⌊t⌋) (8226973 / 26576004 : ℝ) with c161 | c161
  · refine ⟨27, 9 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c160, c161]
  rcases lt_or_ge (t - ⌊t⌋) (5042116 / 16135431 : ℝ) with c162 | c162
  · refine ⟨16, 6 + 17 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c161, c162]
  rcases lt_or_ge (t - ⌊t⌋) (6546697 / 20881146 : ℝ) with c163 | c163
  · refine ⟨32, 7 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c162, c163]
  rcases lt_or_ge (t - ⌊t⌋) (1238875 / 3796572 : ℝ) with c164 | c164
  · refine ⟨3, 2 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c163, c164]
  rcases lt_or_ge (t - ⌊t⌋) (13353601 / 40813149 : ℝ) with c165 | c165
  · refine ⟨25, 15 + 43 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c164, c165]
  rcases lt_or_ge (t - ⌊t⌋) (3748037 / 11389716 : ℝ) with c166 | c166
  · refine ⟨22, 8 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c165, c166]
  rcases lt_or_ge (t - ⌊t⌋) (940123 / 2847429 : ℝ) with c167 | c167
  · refine ⟨20, 7 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c166, c167]
  rcases lt_or_ge (t - ⌊t⌋) (8797913 / 26576004 : ℝ) with c168 | c168
  · refine ⟨21, 19 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c167, c168]
  rcases lt_or_ge (t - ⌊t⌋) (11338627 / 34169148 : ℝ) with c169 | c169
  · refine ⟨35, 12 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c168, c169]
  rcases lt_or_ge (t - ⌊t⌋) (20200831 / 60745152 : ℝ) with c170 | c170
  · refine ⟨6, 22 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c169, c170]
  rcases lt_or_ge (t - ⌊t⌋) (969794 / 2847429 : ℝ) with c171 | c171
  · refine ⟨5, 3 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c170, c171]
  rcases lt_or_ge (t - ⌊t⌋) (1637572 / 4745715 : ℝ) with c172 | c172
  · refine ⟨4, 2 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c171, c172]
  rcases lt_or_ge (t - ⌊t⌋) (332245 / 949143 : ℝ) with c173 | c173
  · refine ⟨9, 4 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c172, c173]
  rcases lt_or_ge (t - ⌊t⌋) (3037633 / 8542287 : ℝ) with c174 | c174
  · refine ⟨17, 4 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c173, c174]
  rcases lt_or_ge (t - ⌊t⌋) (9161218 / 25626861 : ℝ) with c175 | c175
  · refine ⟨37, 10 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c174, c175]
  rcases lt_or_ge (t - ⌊t⌋) (340720 / 949143 : ℝ) with c176 | c176
  · refine ⟨32, 8 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c175, c176]
  rcases lt_or_ge (t - ⌊t⌋) (6143885 / 17084574 : ℝ) with c177 | c177
  · refine ⟨35, 13 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c176, c177]
  rcases lt_or_ge (t - ⌊t⌋) (20528119 / 56948580 : ℝ) with c178 | c178
  · refine ⟨18, 22 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c177, c178]
  rcases lt_or_ge (t - ⌊t⌋) (3445631 / 9491430 : ℝ) with c179 | c179
  · refine ⟨19, 8 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c178, c179]
  rcases lt_or_ge (t - ⌊t⌋) (3115808 / 8542287 : ℝ) with c180 | c180
  · refine ⟨34, 7 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c179, c180]
  rcases lt_or_ge (t - ⌊t⌋) (5556155 / 15186288 : ℝ) with c181 | c181
  · refine ⟨33, 12 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c180, c181]
  rcases lt_or_ge (t - ⌊t⌋) (2436764 / 6644001 : ℝ) with c182 | c182
  · refine ⟨21, 21 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c181, c182]
  rcases lt_or_ge (t - ⌊t⌋) (9416726 / 25626861 : ℝ) with c183 | c183
  · refine ⟨8, 20 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c182, c183]
  rcases lt_or_ge (t - ⌊t⌋) (745993 / 1898286 : ℝ) with c184 | c184
  · refine ⟨1, 1 + 2 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c183, c184]
  rcases lt_or_ge (t - ⌊t⌋) (421591 / 949143 : ℝ) with c185 | c185
  · refine ⟨29, 1 + 1 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c184, c185]
  rcases lt_or_ge (t - ⌊t⌋) (8876342 / 19932003 : ℝ) with c186 | c186
  · refine ⟨12, 19 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c185, c186]
  rcases lt_or_ge (t - ⌊t⌋) (4271593 / 9491430 : ℝ) with c187 | c187
  · refine ⟨9, 5 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c186, c187]
  rcases lt_or_ge (t - ⌊t⌋) (6431549 / 14237145 : ℝ) with c188 | c188
  · refine ⟨31, 14 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c187, c188]
  rcases lt_or_ge (t - ⌊t⌋) (12023545 / 26576004 : ℝ) with c189 | c189
  · refine ⟨27, 13 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c188, c189]
  rcases lt_or_ge (t - ⌊t⌋) (10343503 / 22779432 : ℝ) with c190 | c190
  · refine ⟨22, 11 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c189, c190]
  rcases lt_or_ge (t - ⌊t⌋) (20735443 / 45558864 : ℝ) with c191 | c191
  · refine ⟨28, 22 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c190, c191]
  rcases lt_or_ge (t - ⌊t⌋) (6524038 / 14237145 : ℝ) with c192 | c192
  · refine ⟨14, 7 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c191, c192]
  rcases lt_or_ge (t - ⌊t⌋) (13959739 / 30372576 : ℝ) with c193 | c193
  · refine ⟨33, 15 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c192, c193]
  rcases lt_or_ge (t - ⌊t⌋) (26222977 / 56948580 : ℝ) with c194 | c194
  · refine ⟨18, 28 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c193, c194]
  rcases lt_or_ge (t - ⌊t⌋) (2197387 / 4745715 : ℝ) with c195 | c195
  · refine ⟨19, 10 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c194, c195]
  rcases lt_or_ge (t - ⌊t⌋) (3986776 / 8542287 : ℝ) with c196 | c196
  · refine ⟨17, 5 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c195, c196]
  rcases lt_or_ge (t - ⌊t⌋) (12008647 / 25626861 : ℝ) with c197 | c197
  · refine ⟨37, 13 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c196, c197]
  rcases lt_or_ge (t - ⌊t⌋) (15162187 / 32270862 : ℝ) with c198 | c198
  · refine ⟨36, 16 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c197, c198]
  rcases lt_or_ge (t - ⌊t⌋) (8042171 / 17084574 : ℝ) with c199 | c199
  · refine ⟨35, 17 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c198, c199]
  rcases lt_or_ge (t - ⌊t⌋) (9428290 / 19932003 : ℝ) with c200 | c200
  · refine ⟨20, 10 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c199, c200]
  rcases lt_or_ge (t - ⌊t⌋) (4064951 / 8542287 : ℝ) with c201 | c201
  · refine ⟨34, 9 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c200, c201]
  rcases lt_or_ge (t - ⌊t⌋) (10842293 / 22779432 : ℝ) with c202 | c202
  · refine ⟨28, 23 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c201, c202]
  rcases lt_or_ge (t - ⌊t⌋) (1831343 / 3796572 : ℝ) with c203 | c203
  · refine ⟨7, 4 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c202, c203]
  rcases lt_or_ge (t - ⌊t⌋) (6452785 / 13288002 : ℝ) with c204 | c204
  · refine ⟨13, 7 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c203, c204]
  rcases lt_or_ge (t - ⌊t⌋) (5081086 / 10440573 : ℝ) with c205 | c205
  · refine ⟨30, 22 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c204, c205]
  rcases lt_or_ge (t - ⌊t⌋) (7889545 / 16135431 : ℝ) with c206 | c206
  · refine ⟨16, 9 + 17 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c205, c206]
  rcases lt_or_ge (t - ⌊t⌋) (19997602 / 40813149 : ℝ) with c207 | c207
  · refine ⟨25, 22 + 43 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c206, c207]
  rcases lt_or_ge (t - ⌊t⌋) (7454441 / 15186288 : ℝ) with c208 | c208
  · refine ⟨33, 16 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c207, c208]
  rcases lt_or_ge (t - ⌊t⌋) (26138113 / 53152008 : ℝ) with c209 | c209
  · refine ⟨21, 28 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c208, c209]
  rcases lt_or_ge (t - ⌊t⌋) (9825485 / 19932003 : ℝ) with c210 | c210
  · refine ⟨12, 21 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c209, c210]
  rcases lt_or_ge (t - ⌊t⌋) (28121263 / 56948580 : ℝ) with c211 | c211
  · refine ⟨18, 30 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c210, c211]
  rcases lt_or_ge (t - ⌊t⌋) (5646323 / 11389716 : ℝ) with c212 | c212
  · refine ⟨22, 12 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c211, c212]
  rcases lt_or_ge (t - ⌊t⌋) (22633729 / 45558864 : ℝ) with c213 | c213
  · refine ⟨28, 24 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c212, c213]
  rcases lt_or_ge (t - ⌊t⌋) (25477453 / 51253722 : ℝ) with c214 | c214
  · refine ⟨8, 27 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c213, c214]
  rcases lt_or_ge (t - ⌊t⌋) (17033485 / 34169148 : ℝ) with c215 | c215
  · refine ⟨35, 18 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c214, c215]
  rcases lt_or_ge (t - ⌊t⌋) (8055665 / 16135431 : ℝ) with c216 | c216
  · refine ⟨36, 17 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c215, c216]
  rcases lt_or_ge (t - ⌊t⌋) (2888731 / 5694858 : ℝ) with c217 | c217
  · refine ⟨5, 4 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c216, c217]
  rcases lt_or_ge (t - ⌊t⌋) (4825441 / 9491430 : ℝ) with c218 | c218
  · refine ⟨24, 21 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c217, c218]
  rcases lt_or_ge (t - ⌊t⌋) (21273487 / 41762292 : ℝ) with c219 | c219
  · refine ⟨30, 23 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c218, c219]
  rcases lt_or_ge (t - ⌊t⌋) (483701 / 949143 : ℝ) with c220 | c220
  · refine ⟨21, 29 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c219, c220]
  rcases lt_or_ge (t - ⌊t⌋) (14535203 / 28474290 : ℝ) with c221 | c221
  · refine ⟨18, 31 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c220, c221]
  rcases lt_or_ge (t - ⌊t⌋) (9738691 / 18982860 : ℝ) with c222 | c222
  · refine ⟨19, 11 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c221, c222]
  rcases lt_or_ge (t - ⌊t⌋) (5876677 / 11389716 : ℝ) with c223 | c223
  · refine ⟨11, 7 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c222, c223]
  rcases lt_or_ge (t - ⌊t⌋) (20600113 / 39864006 : ℝ) with c224 | c224
  · refine ⟨12, 22 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c223, c224]
  rcases lt_or_ge (t - ⌊t⌋) (7380692 / 14237145 : ℝ) with c225 | c225
  · refine ⟨31, 16 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c224, c225]
  rcases lt_or_ge (t - ⌊t⌋) (10377433 / 19932003 : ℝ) with c226 | c226
  · refine ⟨20, 11 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c225, c226]
  rcases lt_or_ge (t - ⌊t⌋) (15858025 / 30372576 : ℝ) with c227 | c227
  · refine ⟨33, 17 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c226, c227]
  rcases lt_or_ge (t - ⌊t⌋) (7473181 / 14237145 : ℝ) with c228 | c228
  · refine ⟨14, 8 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c227, c228]
  rcases lt_or_ge (t - ⌊t⌋) (4495657 / 8542287 : ℝ) with c229 | c229
  · refine ⟨35, 19 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c228, c229]
  rcases lt_or_ge (t - ⌊t⌋) (30019549 / 56948580 : ℝ) with c230 | c230
  · refine ⟨18, 32 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c229, c230]
  rcases lt_or_ge (t - ⌊t⌋) (28036399 / 53152008 : ℝ) with c231 | c231
  · refine ⟨21, 30 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c230, c231]
  rcases lt_or_ge (t - ⌊t⌋) (8056621 / 15186288 : ℝ) with c232 | c232
  · refine ⟨15, 9 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c231, c232]
  rcases lt_or_ge (t - ⌊t⌋) (9079045 / 17084574 : ℝ) with c233 | c233
  · refine ⟨34, 10 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c232, c233]
  rcases lt_or_ge (t - ⌊t⌋) (11111315 / 20881146 : ℝ) with c234 | c234
  · refine ⟨30, 24 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c233, c234]
  rcases lt_or_ge (t - ⌊t⌋) (20250907 / 37965720 : ℝ) with c235 | c235
  · refine ⟨24, 22 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c234, c235]
  rcases lt_or_ge (t - ⌊t⌋) (27375739 / 51253722 : ℝ) with c236 | c236
  · refine ⟨8, 29 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c235, c236]
  rcases lt_or_ge (t - ⌊t⌋) (25381201 / 47457150 : ℝ) with c237 | c237
  · refine ⟨10, 27 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c236, c237]
  rcases lt_or_ge (t - ⌊t⌋) (517343 / 949143 : ℝ) with c238 | c238
  · refine ⟨4, 3 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c237, c238]
  rcases lt_or_ge (t - ⌊t⌋) (2610368 / 4745715 : ℝ) with c239 | c239
  · refine ⟨9, 6 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c238, c239]
  rcases lt_or_ge (t - ⌊t⌋) (15710527 / 28474290 : ℝ) with c240 | c240
  · refine ⟨31, 17 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c239, c240]
  rcases lt_or_ge (t - ⌊t⌋) (14162441 / 25626861 : ℝ) with c241 | c241
  · refine ⟨8, 30 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c240, c241]
  rcases lt_or_ge (t - ⌊t⌋) (18931771 / 34169148 : ℝ) with c242 | c242
  · refine ⟨35, 20 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c241, c242]
  rcases lt_or_ge (t - ⌊t⌋) (3700964 / 6644001 : ℝ) with c243 | c243
  · refine ⟨13, 8 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c242, c243]
  rcases lt_or_ge (t - ⌊t⌋) (9004808 / 16135431 : ℝ) with c244 | c244
  · refine ⟨36, 19 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c243, c244]
  rcases lt_or_ge (t - ⌊t⌋) (7435487 / 13288002 : ℝ) with c245 | c245
  · refine ⟨27, 16 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c244, c245]
  rcases lt_or_ge (t - ⌊t⌋) (22845031 / 40813149 : ℝ) with c246 | c246
  · refine ⟨25, 25 + 43 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c245, c246]
  rcases lt_or_ge (t - ⌊t⌋) (6383567 / 11389716 : ℝ) with c247 | c247
  · refine ⟨18, 34 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c246, c247]
  rcases lt_or_ge (t - ⌊t⌋) (5343917 / 9491430 : ℝ) with c248 | c248
  · refine ⟨19, 12 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c247, c248]
  rcases lt_or_ge (t - ⌊t⌋) (29934685 / 53152008 : ℝ) with c249 | c249
  · refine ⟨21, 32 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c248, c249]
  rcases lt_or_ge (t - ⌊t⌋) (3214057 / 5694858 : ℝ) with c250 | c250
  · refine ⟨12, 24 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c249, c250]
  rcases lt_or_ge (t - ⌊t⌋) (1094009 / 1898286 : ℝ) with c251 | c251
  · refine ⟨3, 3 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c250, c251]
  rcases lt_or_ge (t - ⌊t⌋) (4935919 / 8542287 : ℝ) with c252 | c252
  · refine ⟨17, 6 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c251, c252]
  rcases lt_or_ge (t - ⌊t⌋) (14856076 / 25626861 : ℝ) with c253 | c253
  · refine ⟨37, 16 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c252, c253]
  rcases lt_or_ge (t - ⌊t⌋) (7163462 / 12338859 : ℝ) with c254 | c254
  · refine ⟨26, 16 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c253, c254]
  rcases lt_or_ge (t - ⌊t⌋) (9940457 / 17084574 : ℝ) with c255 | c255
  · refine ⟨35, 21 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c254, c255]
  rcases lt_or_ge (t - ⌊t⌋) (23794174 / 40813149 : ℝ) with c256 | c256
  · refine ⟨25, 26 + 43 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c255, c256]
  rcases lt_or_ge (t - ⌊t⌋) (22149193 / 37965720 : ℝ) with c257 | c257
  · refine ⟨24, 24 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c256, c257]
  rcases lt_or_ge (t - ⌊t⌋) (1665967 / 2847429 : ℝ) with c258 | c258
  · refine ⟨31, 18 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c257, c258]
  rcases lt_or_ge (t - ⌊t⌋) (5014094 / 8542287 : ℝ) with c259 | c259
  · refine ⟨34, 11 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c258, c259]
  rcases lt_or_ge (t - ⌊t⌋) (11723771 / 19932003 : ℝ) with c260 | c260
  · refine ⟨12, 25 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c259, c260]
  rcases lt_or_ge (t - ⌊t⌋) (8422324 / 14237145 : ℝ) with c261 | c261
  · refine ⟨14, 9 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c260, c261]
  rcases lt_or_ge (t - ⌊t⌋) (2251441 / 3796572 : ℝ) with c262 | c262
  · refine ⟨15, 10 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c261, c262]
  rcases lt_or_ge (t - ⌊t⌋) (33816121 / 56948580 : ℝ) with c263 | c263
  · refine ⟨18, 36 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c262, c263]
  rcases lt_or_ge (t - ⌊t⌋) (15820117 / 26576004 : ℝ) with c264 | c264
  · refine ⟨27, 17 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c263, c264]
  rcases lt_or_ge (t - ⌊t⌋) (1706455 / 2847429 : ℝ) with c265 | c265
  · refine ⟨11, 8 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c264, c265]
  rcases lt_or_ge (t - ⌊t⌋) (25070059 / 41762292 : ℝ) with c266 | c266
  · refine ⟨30, 27 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c265, c266]
  rcases lt_or_ge (t - ⌊t⌋) (6844861 / 11389716 : ℝ) with c267 | c267
  · refine ⟨28, 29 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c266, c267]
  rcases lt_or_ge (t - ⌊t⌋) (4611829 / 7593144 : ℝ) with c268 | c268
  · refine ⟨7, 5 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c267, c268]
  rcases lt_or_ge (t - ⌊t⌋) (2887292 / 4745715 : ℝ) with c269 | c269
  · refine ⟨24, 25 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c268, c269]
  rcases lt_or_ge (t - ⌊t⌋) (20830057 / 34169148 : ℝ) with c270 | c270
  · refine ⟨35, 22 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c269, c270]
  rcases lt_or_ge (t - ⌊t⌋) (8691316 / 14237145 : ℝ) with c271 | c271
  · refine ⟨18, 37 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c270, c271]
  rcases lt_or_ge (t - ⌊t⌋) (11636977 / 18982860 : ℝ) with c272 | c272
  · refine ⟨19, 13 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c271, c272]
  rcases lt_or_ge (t - ⌊t⌋) (37285405 / 60745152 : ℝ) with c273 | c273
  · refine ⟨6, 40 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c272, c273]
  rcases lt_or_ge (t - ⌊t⌋) (12275719 / 19932003 : ℝ) with c274 | c274
  · refine ⟨20, 13 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c273, c274]
  rcases lt_or_ge (t - ⌊t⌋) (9953951 / 16135431 : ℝ) with c275 | c275
  · refine ⟨36, 21 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c274, c275]
  rcases lt_or_ge (t - ⌊t⌋) (17608813 / 28474290 : ℝ) with c276 | c276
  · refine ⟨31, 19 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c275, c276]
  rcases lt_or_ge (t - ⌊t⌋) (15276067 / 24677718 : ℝ) with c277 | c277
  · refine ⟨26, 17 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c276, c277]
  rcases lt_or_ge (t - ⌊t⌋) (14140075 / 22779432 : ℝ) with c278 | c278
  · refine ⟨22, 15 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c277, c278]
  rcases lt_or_ge (t - ⌊t⌋) (28328587 / 45558864 : ℝ) with c279 | c279
  · refine ⟨28, 30 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c278, c279]
  rcases lt_or_ge (t - ⌊t⌋) (44289688 / 71185725 : ℝ) with c280 | c280
  · refine ⟨23, 47 + 75 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c279, c280]
  rcases lt_or_ge (t - ⌊t⌋) (1182691 / 1898286 : ℝ) with c281 | c281
  · refine ⟨30, 28 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c280, c281]
  rcases lt_or_ge (t - ⌊t⌋) (1821730 / 2847429 : ℝ) with c282 | c282
  · refine ⟨2, 2 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c281, c282]
  rcases lt_or_ge (t - ⌊t⌋) (10977331 / 17084574 : ℝ) with c283 | c283
  · refine ⟨34, 12 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c282, c283]
  rcases lt_or_ge (t - ⌊t⌋) (14638865 / 22779432 : ℝ) with c284 | c284
  · refine ⟨28, 31 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c283, c284]
  rcases lt_or_ge (t - ⌊t⌋) (18956302 / 29423433 : ℝ) with c285 | c285
  · refine ⟨0, 20 + 31 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c284, c285]
  rcases lt_or_ge (t - ⌊t⌋) (39183691 / 60745152 : ℝ) with c286 | c286
  · refine ⟨6, 42 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c285, c286]
  rcases lt_or_ge (t - ⌊t⌋) (6169879 / 9491430 : ℝ) with c287 | c287
  · refine ⟨9, 7 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c286, c287]
  rcases lt_or_ge (t - ⌊t⌋) (9278978 / 14237145 : ℝ) with c288 | c288
  · refine ⟨31, 20 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c287, c288]
  rcases lt_or_ge (t - ⌊t⌋) (26641603 / 40813149 : ℝ) with c289 | c289
  · refine ⟨25, 29 + 43 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c288, c289]
  rcases lt_or_ge (t - ⌊t⌋) (9954907 / 15186288 : ℝ) with c290 | c290
  · refine ⟨15, 11 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c289, c290]
  rcases lt_or_ge (t - ⌊t⌋) (9371467 / 14237145 : ℝ) with c291 | c291
  · refine ⟨14, 10 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c290, c291]
  rcases lt_or_ge (t - ⌊t⌋) (12498311 / 18982860 : ℝ) with c292 | c292
  · refine ⟨24, 27 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c291, c292]
  rcases lt_or_ge (t - ⌊t⌋) (26294971 / 39864006 : ℝ) with c293 | c293
  · refine ⟨12, 28 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c292, c293]
  rcases lt_or_ge (t - ⌊t⌋) (37612693 / 56948580 : ℝ) with c294 | c294
  · refine ⟨18, 40 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c293, c294]
  rcases lt_or_ge (t - ⌊t⌋) (629306 / 949143 : ℝ) with c295 | c295
  · refine ⟨19, 14 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c294, c295]
  rcases lt_or_ge (t - ⌊t⌋) (10736974 / 16135431 : ℝ) with c296 | c296
  · refine ⟨16, 12 + 17 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c295, c296]
  rcases lt_or_ge (t - ⌊t⌋) (1918937 / 2847429 : ℝ) with c297 | c297
  · refine ⟨5, 5 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c296, c297]
  rcases lt_or_ge (t - ⌊t⌋) (16012601 / 23728575 : ℝ) with c298 | c298
  · refine ⟨10, 34 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c297, c298]
  rcases lt_or_ge (t - ⌊t⌋) (10903094 / 16135431 : ℝ) with c299 | c299
  · refine ⟨36, 23 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c298, c299]
  rcases lt_or_ge (t - ⌊t⌋) (14139841 / 20881146 : ℝ) with c300 | c300
  · refine ⟨32, 15 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c299, c300]
  rcases lt_or_ge (t - ⌊t⌋) (5150935 / 7593144 : ℝ) with c301 | c301
  · refine ⟨33, 22 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c300, c301]
  rcases lt_or_ge (t - ⌊t⌋) (7774963 / 11389716 : ℝ) with c302 | c302
  · refine ⟨11, 9 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c301, c302]
  rcases lt_or_ge (t - ⌊t⌋) (13622057 / 19932003 : ℝ) with c303 | c303
  · refine ⟨12, 29 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c302, c303]
  rcases lt_or_ge (t - ⌊t⌋) (5885062 / 8542287 : ℝ) with c304 | c304
  · refine ⟨17, 7 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c303, c304]
  rcases lt_or_ge (t - ⌊t⌋) (17703505 / 25626861 : ℝ) with c305 | c305
  · refine ⟨37, 19 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c304, c305]
  rcases lt_or_ge (t - ⌊t⌋) (28866631 / 41762292 : ℝ) with c306 | c306
  · refine ⟨30, 31 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c305, c306]
  rcases lt_or_ge (t - ⌊t⌋) (2626945 / 3796572 : ℝ) with c307 | c307
  · refine ⟨6, 45 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c306, c307]
  rcases lt_or_ge (t - ⌊t⌋) (11838743 / 17084574 : ℝ) with c308 | c308
  · refine ⟨35, 25 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c307, c308]
  rcases lt_or_ge (t - ⌊t⌋) (39510979 / 56948580 : ℝ) with c309 | c309
  · refine ⟨18, 42 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c308, c309]
  rcases lt_or_ge (t - ⌊t⌋) (6594869 / 9491430 : ℝ) with c310 | c310
  · refine ⟨10, 35 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c309, c310]
  rcases lt_or_ge (t - ⌊t⌋) (17174353 / 24677718 : ℝ) with c311 | c311
  · refine ⟨26, 19 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c310, c311]
  rcases lt_or_ge (t - ⌊t⌋) (5963237 / 8542287 : ℝ) with c312 | c312
  · refine ⟨34, 13 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c311, c312]
  rcases lt_or_ge (t - ⌊t⌋) (664301 / 949143 : ℝ) with c313 | c313
  · refine ⟨13, 10 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c312, c313]
  rcases lt_or_ge (t - ⌊t⌋) (17959013 / 25626861 : ℝ) with c314 | c314
  · refine ⟨8, 38 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c313, c314]
  rcases lt_or_ge (t - ⌊t⌋) (9333773 / 13288002 : ℝ) with c315 | c315
  · refine ⟨27, 20 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c314, c315]
  rcases lt_or_ge (t - ⌊t⌋) (16038361 / 22779432 : ℝ) with c316 | c316
  · refine ⟨22, 17 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c315, c316]
  rcases lt_or_ge (t - ⌊t⌋) (22755331 / 32270862 : ℝ) with c317 | c317
  · refine ⟨36, 24 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c316, c317]
  rcases lt_or_ge (t - ⌊t⌋) (37527829 / 53152008 : ℝ) with c318 | c318
  · refine ⟨21, 40 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c317, c318]
  rcases lt_or_ge (t - ⌊t⌋) (28193257 / 39864006 : ℝ) with c319 | c319
  · refine ⟨12, 30 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c318, c319]
  rcases lt_or_ge (t - ⌊t⌋) (20854588 / 29423433 : ℝ) with c320 | c320
  · refine ⟨0, 22 + 31 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c319, c320]
  rcases lt_or_ge (t - ⌊t⌋) (14174005 / 19932003 : ℝ) with c321 | c321
  · refine ⟨20, 15 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c320, c321]
  rcases lt_or_ge (t - ⌊t⌋) (13535263 / 18982860 : ℝ) with c322 | c322
  · refine ⟨19, 15 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c321, c322]
  rcases lt_or_ge (t - ⌊t⌋) (14907887 / 20881146 : ℝ) with c323 | c323
  · refine ⟨30, 32 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c322, c323]
  rcases lt_or_ge (t - ⌊t⌋) (16961744 / 23728575 : ℝ) with c324 | c324
  · refine ⟨10, 36 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c323, c324]
  rcases lt_or_ge (t - ⌊t⌋) (5452025 / 7593144 : ℝ) with c325 | c325
  · refine ⟨15, 12 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c324, c325]
  rcases lt_or_ge (t - ⌊t⌋) (10228121 / 14237145 : ℝ) with c326 | c326
  · refine ⟨31, 22 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c325, c326]
  rcases lt_or_ge (t - ⌊t⌋) (36867169 / 51253722 : ℝ) with c327 | c327
  · refine ⟨8, 39 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c326, c327]
  rcases lt_or_ge (t - ⌊t⌋) (24626629 / 34169148 : ℝ) with c328 | c328
  · refine ⟨35, 26 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c327, c328]
  rcases lt_or_ge (t - ⌊t⌋) (7544492 / 10440573 : ℝ) with c329 | c329
  · refine ⟨32, 16 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c328, c329]
  rcases lt_or_ge (t - ⌊t⌋) (2064122 / 2847429 : ℝ) with c330 | c330
  · refine ⟨14, 11 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c329, c330]
  rcases lt_or_ge (t - ⌊t⌋) (16537151 / 22779432 : ℝ) with c331 | c331
  · refine ⟨28, 35 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c330, c331]
  rcases lt_or_ge (t - ⌊t⌋) (1390243 / 1898286 : ℝ) with c332 | c332
  · refine ⟨7, 6 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c331, c332]
  rcases lt_or_ge (t - ⌊t⌋) (27844051 / 37965720 : ℝ) with c333 | c333
  · refine ⟨24, 30 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c332, c333]
  rcases lt_or_ge (t - ⌊t⌋) (11852237 / 16135431 : ℝ) with c334 | c334
  · refine ⟨36, 25 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c333, c334]
  rcases lt_or_ge (t - ⌊t⌋) (34872631 / 47457150 : ℝ) with c335 | c335
  · refine ⟨10, 37 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c334, c335]
  rcases lt_or_ge (t - ⌊t⌋) (3535858 / 4745715 : ℝ) with c336 | c336
  · refine ⟨4, 4 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c335, c336]
  rcases lt_or_ge (t - ⌊t⌋) (3559511 / 4745715 : ℝ) with c337 | c337
  · refine ⟨9, 8 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c336, c337]
  rcases lt_or_ge (t - ⌊t⌋) (4281077 / 5694858 : ℝ) with c338 | c338
  · refine ⟨31, 23 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c337, c338]
  rcases lt_or_ge (t - ⌊t⌋) (12875617 / 17084574 : ℝ) with c339 | c339
  · refine ⟨34, 14 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c338, c339]
  rcases lt_or_ge (t - ⌊t⌋) (30091543 / 39864006 : ℝ) with c340 | c340
  · refine ⟨12, 32 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c339, c340]
  rcases lt_or_ge (t - ⌊t⌋) (53781118 / 71185725 : ℝ) with c341 | c341
  · refine ⟨23, 57 + 75 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c340, c341]
  rcases lt_or_ge (t - ⌊t⌋) (38765455 / 51253722 : ℝ) with c342 | c342
  · refine ⟨8, 41 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c341, c342]
  rcases lt_or_ge (t - ⌊t⌋) (15123148 / 19932003 : ℝ) with c343 | c343
  · refine ⟨20, 16 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c342, c343]
  rcases lt_or_ge (t - ⌊t⌋) (2883947 / 3796572 : ℝ) with c344 | c344
  · refine ⟨21, 43 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c343, c344]
  rcases lt_or_ge (t - ⌊t⌋) (43307551 / 56948580 : ℝ) with c345 | c345
  · refine ⟨18, 46 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c344, c345]
  rcases lt_or_ge (t - ⌊t⌋) (7242203 / 9491430 : ℝ) with c346 | c346
  · refine ⟨19, 16 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c345, c346]
  rcases lt_or_ge (t - ⌊t⌋) (4362053 / 5694858 : ℝ) with c347 | c347
  · refine ⟨11, 10 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c346, c347]
  rcases lt_or_ge (t - ⌊t⌋) (16038127 / 20881146 : ℝ) with c348 | c348
  · refine ⟨32, 17 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c347, c348]
  rcases lt_or_ge (t - ⌊t⌋) (10249357 / 13288002 : ℝ) with c349 | c349
  · refine ⟨13, 11 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c348, c349]
  rcases lt_or_ge (t - ⌊t⌋) (19072639 / 24677718 : ℝ) with c350 | c350
  · refine ⟨26, 21 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c349, c350]
  rcases lt_or_ge (t - ⌊t⌋) (734494 / 949143 : ℝ) with c351 | c351
  · refine ⟨27, 22 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c350, c351]
  rcases lt_or_ge (t - ⌊t⌋) (36770917 / 47457150 : ℝ) with c352 | c352
  · refine ⟨10, 39 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c351, c352]
  rcases lt_or_ge (t - ⌊t⌋) (19857299 / 25626861 : ℝ) with c353 | c353
  · refine ⟨8, 42 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c352, c353]
  rcases lt_or_ge (t - ⌊t⌋) (26524915 / 34169148 : ℝ) with c354 | c354
  · refine ⟨35, 28 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c353, c354]
  rcases lt_or_ge (t - ⌊t⌋) (22128347 / 28474290 : ℝ) with c355 | c355
  · refine ⟨18, 47 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c354, c355]
  rcases lt_or_ge (t - ⌊t⌋) (41324401 / 53152008 : ℝ) with c356 | c356
  · refine ⟨21, 44 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c355, c356]
  rcases lt_or_ge (t - ⌊t⌋) (11853193 / 15186288 : ℝ) with c357 | c357
  · refine ⟨15, 13 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c356, c357]
  rcases lt_or_ge (t - ⌊t⌋) (12635260 / 16135431 : ℝ) with c358 | c358
  · refine ⟨16, 14 + 17 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c357, c358]
  rcases lt_or_ge (t - ⌊t⌋) (29742337 / 37965720 : ℝ) with c359 | c359
  · refine ⟨24, 32 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c358, c359]
  rcases lt_or_ge (t - ⌊t⌋) (11177264 / 14237145 : ℝ) with c360 | c360
  · refine ⟨31, 24 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c359, c360]
  rcases lt_or_ge (t - ⌊t⌋) (23862989 / 30372576 : ℝ) with c361 | c361
  · refine ⟨6, 51 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c360, c361]
  rcases lt_or_ge (t - ⌊t⌋) (17936647 / 22779432 : ℝ) with c362 | c362
  · refine ⟨22, 19 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c361, c362]
  rcases lt_or_ge (t - ⌊t⌋) (35921731 / 45558864 : ℝ) with c363 | c363
  · refine ⟨28, 38 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c362, c363]
  rcases lt_or_ge (t - ⌊t⌋) (11269753 / 14237145 : ℝ) with c364 | c364
  · refine ⟨14, 12 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c363, c364]
  rcases lt_or_ge (t - ⌊t⌋) (32336461 / 40813149 : ℝ) with c365 | c365
  · refine ⟨25, 35 + 43 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c364, c365]
  rcases lt_or_ge (t - ⌊t⌋) (12801380 / 16135431 : ℝ) with c366 | c366
  · refine ⟨36, 27 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c365, c366]
  rcases lt_or_ge (t - ⌊t⌋) (45205837 / 56948580 : ℝ) with c367 | c367
  · refine ⟨18, 48 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c366, c367]
  rcases lt_or_ge (t - ⌊t⌋) (3772006 / 4745715 : ℝ) with c368 | c368
  · refine ⟨10, 40 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c367, c368]
  rcases lt_or_ge (t - ⌊t⌋) (6834205 / 8542287 : ℝ) with c369 | c369
  · refine ⟨17, 8 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c368, c369]
  rcases lt_or_ge (t - ⌊t⌋) (20550934 / 25626861 : ℝ) with c370 | c370
  · refine ⟨37, 22 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c369, c370]
  rcases lt_or_ge (t - ⌊t⌋) (3050039 / 3796572 : ℝ) with c371 | c371
  · refine ⟨33, 26 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c370, c371]
  rcases lt_or_ge (t - ⌊t⌋) (13737029 / 17084574 : ℝ) with c372 | c372
  · refine ⟨35, 29 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c371, c372]
  rcases lt_or_ge (t - ⌊t⌋) (16072291 / 19932003 : ℝ) with c373 | c373
  · refine ⟨20, 17 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c372, c373]
  rcases lt_or_ge (t - ⌊t⌋) (6912380 / 8542287 : ℝ) with c374 | c374
  · refine ⟨34, 15 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c373, c374]
  rcases lt_or_ge (t - ⌊t⌋) (21514975 / 26576004 : ℝ) with c375 | c375
  · refine ⟨27, 23 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c374, c375]
  rcases lt_or_ge (t - ⌊t⌋) (10010891 / 12338859 : ℝ) with c376 | c376
  · refine ⟨26, 22 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c375, c376]
  rcases lt_or_ge (t - ⌊t⌋) (8493635 / 10440573 : ℝ) with c377 | c377
  · refine ⟨32, 18 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c376, c377]
  rcases lt_or_ge (t - ⌊t⌋) (3137161 / 3796572 : ℝ) with c378 | c378
  · refine ⟨3, 4 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c377, c378]
  rcases lt_or_ge (t - ⌊t⌋) (47104123 / 56948580 : ℝ) with c379 | c379
  · refine ⟨18, 50 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c378, c379]
  rcases lt_or_ge (t - ⌊t⌋) (9442895 / 11389716 : ℝ) with c380 | c380
  · refine ⟨22, 20 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c379, c380]
  rcases lt_or_ge (t - ⌊t⌋) (37820017 / 45558864 : ℝ) with c381 | c381
  · refine ⟨28, 40 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c380, c381]
  rcases lt_or_ge (t - ⌊t⌋) (22085915 / 26576004 : ℝ) with c382 | c382
  · refine ⟨21, 47 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c381, c382]
  rcases lt_or_ge (t - ⌊t⌋) (28423201 / 34169148 : ℝ) with c383 | c383
  · refine ⟨35, 30 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c382, c383]
  rcases lt_or_ge (t - ⌊t⌋) (50573407 / 60745152 : ℝ) with c384 | c384
  · refine ⟨6, 54 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c383, c384]
  rcases lt_or_ge (t - ⌊t⌋) (4787017 / 5694858 : ℝ) with c385 | c385
  · refine ⟨5, 6 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c384, c385]
  rcases lt_or_ge (t - ⌊t⌋) (800146 / 949143 : ℝ) with c386 | c386
  · refine ⟨15, 14 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c385, c386]
  rcases lt_or_ge (t - ⌊t⌋) (24026633 / 28474290 : ℝ) with c387 | c387
  · refine ⟨18, 51 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c386, c387]
  rcases lt_or_ge (t - ⌊t⌋) (11232059 / 13288002 : ℝ) with c388 | c388
  · refine ⟨27, 24 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c387, c388]
  rcases lt_or_ge (t - ⌊t⌋) (1613633 / 1898286 : ℝ) with c389 | c389
  · refine ⟨9, 9 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c388, c389]
  rcases lt_or_ge (t - ⌊t⌋) (12126407 / 14237145 : ℝ) with c390 | c390
  · refine ⟨31, 26 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c389, c390]
  rcases lt_or_ge (t - ⌊t⌋) (6510115 / 7593144 : ℝ) with c391 | c391
  · refine ⟨7, 7 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c390, c391]
  rcases lt_or_ge (t - ⌊t⌋) (1630583 / 1898286 : ℝ) with c392 | c392
  · refine ⟨32, 19 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c391, c392]
  rcases lt_or_ge (t - ⌊t⌋) (7343086 / 8542287 : ℝ) with c393 | c393
  · refine ⟨35, 31 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c392, c393]
  rcases lt_or_ge (t - ⌊t⌋) (49002409 / 56948580 : ℝ) with c394 | c394
  · refine ⟨18, 52 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c393, c394]
  rcases lt_or_ge (t - ⌊t⌋) (4095673 / 4745715 : ℝ) with c395 | c395
  · refine ⟨19, 18 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c394, c395]
  rcases lt_or_ge (t - ⌊t⌋) (14773903 / 17084574 : ℝ) with c396 | c396
  · refine ⟨34, 16 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c395, c396]
  rcases lt_or_ge (t - ⌊t⌋) (13149299 / 15186288 : ℝ) with c397 | c397
  · refine ⟨33, 28 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c396, c397]
  rcases lt_or_ge (t - ⌊t⌋) (11517529 / 13288002 : ℝ) with c398 | c398
  · refine ⟨21, 49 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c397, c398]
  rcases lt_or_ge (t - ⌊t⌋) (44460313 / 51253722 : ℝ) with c399 | c399
  · refine ⟨8, 47 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c398, c399]
  rcases lt_or_ge (t - ⌊t⌋) (847568 / 949143 : ℝ) with c400 | c400
  · refine ⟨1, 2 + 2 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c399, c400]
  rcases lt_or_ge (t - ⌊t⌋) (10180139 / 11389716 : ℝ) with c401 | c401
  · refine ⟨18, 54 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c400, c401]
  rcases lt_or_ge (t - ⌊t⌋) (1698631 / 1898286 : ℝ) with c402 | c402
  · refine ⟨10, 45 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c401, c402]
  rcases lt_or_ge (t - ⌊t⌋) (18704459 / 20881146 : ℝ) with c403 | c403
  · refine ⟨30, 40 + 44 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c402, c403]
  rcases lt_or_ge (t - ⌊t⌋) (27247741 / 30372576 : ℝ) with c404 | c404
  · refine ⟨33, 29 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c403, c404]
  rcases lt_or_ge (t - ⌊t⌋) (5112343 / 5694858 : ℝ) with c405 | c405
  · refine ⟨12, 38 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c404, c405]
  rcases lt_or_ge (t - ⌊t⌋) (14533546 / 16135431 : ℝ) with c406 | c406
  · refine ⟨16, 16 + 17 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c405, c406]
  rcases lt_or_ge (t - ⌊t⌋) (26549446 / 29423433 : ℝ) with c407 | c407
  · refine ⟨0, 28 + 31 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c406, c407]
  rcases lt_or_ge (t - ⌊t⌋) (13751479 / 15186288 : ℝ) with c408 | c408
  · refine ⟨15, 15 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c407, c408]
  rcases lt_or_ge (t - ⌊t⌋) (7783348 / 8542287 : ℝ) with c409 | c409
  · refine ⟨17, 9 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c408, c409]
  rcases lt_or_ge (t - ⌊t⌋) (12147643 / 13288002 : ℝ) with c410 | c410
  · refine ⟨13, 13 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c409, c410]
  rcases lt_or_ge (t - ⌊t⌋) (15635315 / 17084574 : ℝ) with c411 | c411
  · refine ⟨35, 33 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c410, c411]
  rcases lt_or_ge (t - ⌊t⌋) (6090601 / 6644001 : ℝ) with c412 | c412
  · refine ⟨27, 26 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c411, c412]
  rcases lt_or_ge (t - ⌊t⌋) (2615110 / 2847429 : ℝ) with c413 | c413
  · refine ⟨31, 28 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c412, c413]
  rcases lt_or_ge (t - ⌊t⌋) (7861523 / 8542287 : ℝ) with c414 | c414
  · refine ⟨34, 17 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c413, c414]
  rcases lt_or_ge (t - ⌊t⌋) (18367772 / 19932003 : ℝ) with c415 | c415
  · refine ⟨12, 39 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c414, c415]
  rcases lt_or_ge (t - ⌊t⌋) (13168039 / 14237145 : ℝ) with c416 | c416
  · refine ⟨14, 14 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c415, c416]
  rcases lt_or_ge (t - ⌊t⌋) (22869211 / 24677718 : ℝ) with c417 | c417
  · refine ⟨26, 25 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c416, c417]
  rcases lt_or_ge (t - ⌊t⌋) (52798981 / 56948580 : ℝ) with c418 | c418
  · refine ⟨18, 56 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c417, c418]
  rcases lt_or_ge (t - ⌊t⌋) (7049221 / 7593144 : ℝ) with c419 | c419
  · refine ⟨33, 30 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c418, c419]
  rcases lt_or_ge (t - ⌊t⌋) (2655598 / 2847429 : ℝ) with c420 | c420
  · refine ⟨11, 12 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c419, c420]
  rcases lt_or_ge (t - ⌊t⌋) (7087439 / 7593144 : ℝ) with c421 | c421
  · refine ⟨24, 38 + 40 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c420, c421]
  rcases lt_or_ge (t - ⌊t⌋) (27498589 / 29423433 : ℝ) with c422 | c422
  · refine ⟨0, 29 + 31 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c421, c422]
  rcases lt_or_ge (t - ⌊t⌋) (44364061 / 47457150 : ℝ) with c423 | c423
  · refine ⟨10, 47 + 50 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c422, c423]
  rcases lt_or_ge (t - ⌊t⌋) (4485001 / 4745715 : ℝ) with c424 | c424
  · refine ⟨4, 5 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c423, c424]
  rcases lt_or_ge (t - ⌊t⌋) (4508654 / 4745715 : ℝ) with c425 | c425
  · refine ⟨9, 10 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c424, c425]
  rcases lt_or_ge (t - ⌊t⌋) (27100243 / 28474290 : ℝ) with c426 | c426
  · refine ⟨31, 29 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c425, c426]
  rcases lt_or_ge (t - ⌊t⌋) (25311547 / 26576004 : ℝ) with c427 | c427
  · refine ⟨27, 27 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c426, c427]
  rcases lt_or_ge (t - ⌊t⌋) (21733219 / 22779432 : ℝ) with c428 | c428
  · refine ⟨22, 23 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c427, c428]
  rcases lt_or_ge (t - ⌊t⌋) (43514875 / 45558864 : ℝ) with c429 | c429
  · refine ⟨28, 46 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c428, c429]
  rcases lt_or_ge (t - ⌊t⌋) (50815831 / 53152008 : ℝ) with c430 | c430
  · refine ⟨21, 54 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c429, c430]
  rcases lt_or_ge (t - ⌊t⌋) (2770873 / 2847429 : ℝ) with c431 | c431
  · refine ⟨2, 3 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c430, c431]
  rcases lt_or_ge (t - ⌊t⌋) (16672189 / 17084574 : ℝ) with c432 | c432
  · refine ⟨34, 18 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c431, c432]
  rcases lt_or_ge (t - ⌊t⌋) (22232009 / 22779432 : ℝ) with c433 | c433
  · refine ⟨28, 47 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c432, c433]
  rcases lt_or_ge (t - ⌊t⌋) (3729629 / 3796572 : ℝ) with c434 | c434
  · refine ⟨7, 8 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c433, c434]
  rcases lt_or_ge (t - ⌊t⌋) (6548393 / 6644001 : ℝ) with c435 | c435
  · refine ⟨13, 14 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c434, c435]
  rcases lt_or_ge (t - ⌊t⌋) (25296649 / 25626861 : ℝ) with c436 | c436
  · refine ⟨37, 27 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c435, c436]
  rcases lt_or_ge (t - ⌊t⌋) (13130345 / 13288002 : ℝ) with c437 | c437
  · refine ⟨27, 28 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c436, c437]
  rcases lt_or_ge (t - ⌊t⌋) (60064837 / 60745152 : ℝ) with c438 | c438
  · refine ⟨6, 64 + 64 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c437, c438]
  rcases lt_or_ge (t - ⌊t⌋) (14117182 / 14237145 : ℝ) with c439 | c439
  · refine ⟨14, 15 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c438, c439]
  rcases lt_or_ge (t - ⌊t⌋) (52714117 / 53152008 : ℝ) with c440 | c440
  · refine ⟨21, 56 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c439, c440]
  rcases lt_or_ge (t - ⌊t⌋) (39582973 / 39864006 : ℝ) with c441 | c441
  · refine ⟨12, 42 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c440, c441]
  rcases lt_or_ge (t - ⌊t⌋) (56595553 / 56948580 : ℝ) with c442 | c442
  · refine ⟨18, 60 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c441, c442]
  rcases lt_or_ge (t - ⌊t⌋) (11341181 / 11389716 : ℝ) with c443 | c443
  · refine ⟨22, 24 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c442, c443]
  rcases lt_or_ge (t - ⌊t⌋) (2838409 / 2847429 : ℝ) with c444 | c444
  · refine ⟨20, 21 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c443, c444]
  rcases lt_or_ge (t - ⌊t⌋) (25552157 / 25626861 : ℝ) with c445 | c445
  · refine ⟨8, 54 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c444, c445]
  rcases lt_or_ge (t - ⌊t⌋) (34118059 / 34169148 : ℝ) with c446 | c446
  · refine ⟨35, 36 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c445, c446]
  rcases lt_or_ge (t - ⌊t⌋) (32246761 / 32270862 : ℝ) with c447 | c447
  · refine ⟨36, 34 + 34 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c446, c447]
  refine ⟨5, 7 + 6 * ⌊t⌋, ?_⟩
  simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
  rw [abs_lt]
  push_cast
  constructor <;> linarith only [c447, h1]

#print axioms cover
#print axioms v_injective
#print axioms v_pos
end SLRAudit.N38
