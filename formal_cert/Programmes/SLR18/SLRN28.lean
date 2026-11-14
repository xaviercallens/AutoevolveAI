import Mathlib.Tactic

set_option linter.unusedSimpArgs false
set_option maxHeartbeats 0
namespace SLRAudit.N28

/-- velocities of certificate n = 28 -/
def v : Fin 28 → ℕ := ![1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]
/-- shifts s_i = a_i / 13457 -/
def s : Fin 28 → ℚ := ![10965/13457, 1943/13457, 11559/13457, 8887/13457, 8807/13457, 1397/13457, 2346/13457, 13061/13457, 12120/13457, 545/13457, 12896/13457, 10668/13457, 4/13457, 7123/13457, 8701/13457, 10791/13457, 11360/13457, 8118/13457, 2588/13457, 11164/13457, 13290/13457, 10949/13457, 6430/13457, 3853/13457, 6435/13457, 1626/13457, 11294/13457, 3254/13457]

theorem v_injective : Function.Injective v := by decide
theorem v_pos : ∀ i, 0 < v i := by decide

/-- covering: for every real t some runner is within distance < 1/29 of an integer. -/
theorem cover : ∀ t : ℝ, ∃ i : Fin 28, ∃ k : ℤ, |((s i : ℚ) : ℝ) + ((v i : ℕ) : ℝ) * t - (k : ℝ)| < 1 / 29 := by
  intro t
  have h0 : (0 : ℝ) ≤ t - ⌊t⌋ := by have := Int.floor_le t; linarith
  have h1 : t - ⌊t⌋ < (1 : ℝ) := by have := Int.lt_floor_add_one t; linarith
  rcases lt_or_ge (t - ⌊t⌋) (24941 / 3122024 : ℝ) with c0 | c0
  · refine ⟨7, 1 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [h0, c0]
  rcases lt_or_ge (t - ⌊t⌋) (17410 / 1170759 : ℝ) with c1 | c1
  · refine ⟨8, 1 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c0, c1]
  rcases lt_or_ge (t - ⌊t⌋) (15723 / 780506 : ℝ) with c2 | c2
  · refine ⟨11, 1 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1, c2]
  rcases lt_or_ge (t - ⌊t⌋) (28048 / 1170759 : ℝ) with c3 | c3
  · refine ⟨17, 1 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2, c3]
  rcases lt_or_ge (t - ⌊t⌋) (151381 / 5853795 : ℝ) with c4 | c4
  · refine ⟨14, 1 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c3, c4]
  rcases lt_or_ge (t - ⌊t⌋) (11048 / 390253 : ℝ) with c5 | c5
  · refine ⟨27, 1 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c4, c5]
  rcases lt_or_ge (t - ⌊t⌋) (291973 / 9366072 : ℝ) with c6 | c6
  · refine ⟨23, 1 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c5, c6]
  rcases lt_or_ge (t - ⌊t⌋) (197143 / 5463542 : ℝ) with c7 | c7
  · refine ⟨13, 1 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c6, c7]
  rcases lt_or_ge (t - ⌊t⌋) (22833 / 390253 : ℝ) with c8 | c8
  · refine ⟨2, 1 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c7, c8]
  rcases lt_or_ge (t - ⌊t⌋) (470207 / 7805060 : ℝ) with c9 | c9
  · refine ⟨19, 2 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c8, c9]
  rcases lt_or_ge (t - ⌊t⌋) (607348 / 9756325 : ℝ) with c10 | c10
  · refine ⟨24, 2 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c9, c10]
  rcases lt_or_ge (t - ⌊t⌋) (148307 / 1951265 : ℝ) with c11 | c11
  · refine ⟨4, 1 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c10, c11]
  rcases lt_or_ge (t - ⌊t⌋) (403594 / 5073289 : ℝ) with c12 | c12
  · refine ⟨12, 1 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c11, c12]
  rcases lt_or_ge (t - ⌊t⌋) (145987 / 1561012 : ℝ) with c13 | c13
  · refine ⟨3, 1 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c12, c13]
  rcases lt_or_ge (t - ⌊t⌋) (77581 / 780506 : ℝ) with c14 | c14
  · refine ⟨9, 1 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c13, c14]
  rcases lt_or_ge (t - ⌊t⌋) (484591 / 4683036 : ℝ) with c15 | c15
  · refine ⟨11, 2 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c14, c15]
  rcases lt_or_ge (t - ⌊t⌋) (293698 / 2731771 : ℝ) with c16 | c16
  · refine ⟨13, 2 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c15, c16]
  rcases lt_or_ge (t - ⌊t⌋) (43023 / 390253 : ℝ) with c17 | c17
  · refine ⟨19, 3 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c16, c17]
  rcases lt_or_ge (t - ⌊t⌋) (568531 / 5073289 : ℝ) with c18 | c18
  · refine ⟨25, 3 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c17, c18]
  rcases lt_or_ge (t - ⌊t⌋) (357493 / 3122024 : ℝ) with c19 | c19
  · refine ⟨23, 3 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c18, c19]
  rcases lt_or_ge (t - ⌊t⌋) (335676 / 2731771 : ℝ) with c20 | c20
  · refine ⟨6, 1 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c19, c20]
  rcases lt_or_ge (t - ⌊t⌋) (442483 / 3512277 : ℝ) with c21 | c21
  · refine ⟨8, 2 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c20, c21]
  rcases lt_or_ge (t - ⌊t⌋) (207597 / 1561012 : ℝ) with c22 | c22
  · refine ⟨7, 2 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c21, c22]
  rcases lt_or_ge (t - ⌊t⌋) (474397 / 3512277 : ℝ) with c23 | c23
  · refine ⟨17, 3 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c22, c23]
  rcases lt_or_ge (t - ⌊t⌋) (1480103 / 10927084 : ℝ) with c24 | c24
  · refine ⟨27, 4 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c23, c24]
  rcases lt_or_ge (t - ⌊t⌋) (871277 / 6244048 : ℝ) with c25 | c25
  · refine ⟨15, 3 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c24, c25]
  rcases lt_or_ge (t - ⌊t⌋) (1387854 / 9756325 : ℝ) with c26 | c26
  · refine ⟨24, 4 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c25, c26]
  rcases lt_or_ge (t - ⌊t⌋) (396353 / 2731771 : ℝ) with c27 | c27
  · refine ⟨20, 4 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c26, c27]
  rcases lt_or_ge (t - ⌊t⌋) (363197 / 2341518 : ℝ) with c28 | c28
  · refine ⟨5, 1 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c27, c28]
  rcases lt_or_ge (t - ⌊t⌋) (85725 / 390253 : ℝ) with c29 | c29
  · refine ⟨0, 1 + 1 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c28, c29]
  rcases lt_or_ge (t - ⌊t⌋) (433672 / 1951265 : ℝ) with c30 | c30
  · refine ⟨24, 6 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c29, c30]
  rcases lt_or_ge (t - ⌊t⌋) (264428 / 1170759 : ℝ) with c31 | c31
  · refine ⟨14, 4 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c30, c31]
  rcases lt_or_ge (t - ⌊t⌋) (2307821 / 10146578 : ℝ) with c32 | c32
  · refine ⟨25, 6 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c31, c32]
  rcases lt_or_ge (t - ⌊t⌋) (2417702 / 10536831 : ℝ) with c33 | c33
  · refine ⟨26, 7 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c32, c33]
  rcases lt_or_ge (t - ⌊t⌋) (832736 / 3512277 : ℝ) with c34 | c34
  · refine ⟨8, 3 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c33, c34]
  rcases lt_or_ge (t - ⌊t⌋) (1969565 / 8195313 : ℝ) with c35 | c35
  · refine ⟨20, 6 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c34, c35]
  rcases lt_or_ge (t - ⌊t⌋) (1325431 / 5463542 : ℝ) with c36 | c36
  · refine ⟨27, 7 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c35, c36]
  rcases lt_or_ge (t - ⌊t⌋) (1635282 / 6634301 : ℝ) with c37 | c37
  · refine ⟨16, 5 + 17 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c36, c37]
  rcases lt_or_ge (t - ⌊t⌋) (683951 / 2731771 : ℝ) with c38 | c38
  · refine ⟨13, 4 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c37, c38]
  rcases lt_or_ge (t - ⌊t⌋) (805447 / 3122024 : ℝ) with c39 | c39
  · refine ⟨7, 3 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c38, c39]
  rcases lt_or_ge (t - ⌊t⌋) (725929 / 2731771 : ℝ) with c40 | c40
  · refine ⟨6, 2 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c39, c40]
  rcases lt_or_ge (t - ⌊t⌋) (107712 / 390253 : ℝ) with c41 | c41
  · refine ⟨4, 2 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c40, c41]
  rcases lt_or_ge (t - ⌊t⌋) (109135 / 390253 : ℝ) with c42 | c42
  · refine ⟨10, 4 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c41, c42]
  rcases lt_or_ge (t - ⌊t⌋) (2427707 / 8585566 : ℝ) with c43 | c43
  · refine ⟨21, 7 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c42, c43]
  rcases lt_or_ge (t - ⌊t⌋) (2558758 / 8975819 : ℝ) with c44 | c44
  · refine ⟨22, 7 + 23 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c43, c44]
  rcases lt_or_ge (t - ⌊t⌋) (786606 / 2731771 : ℝ) with c45 | c45
  · refine ⟨20, 7 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c44, c45]
  rcases lt_or_ge (t - ⌊t⌋) (1712393 / 5853795 : ℝ) with c46 | c46
  · refine ⟨14, 5 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c45, c46]
  rcases lt_or_ge (t - ⌊t⌋) (1168411 / 3902530 : ℝ) with c47 | c47
  · refine ⟨9, 3 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c46, c47]
  rcases lt_or_ge (t - ⌊t⌋) (2119553 / 7024554 : ℝ) with c48 | c48
  · refine ⟨17, 6 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c47, c48]
  rcases lt_or_ge (t - ⌊t⌋) (2025535 / 6634301 : ℝ) with c49 | c49
  · refine ⟨16, 6 + 17 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c48, c49]
  rcases lt_or_ge (t - ⌊t⌋) (1574353 / 5073289 : ℝ) with c50 | c50
  · refine ⟨12, 4 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c49, c50]
  rcases lt_or_ge (t - ⌊t⌋) (125575 / 390253 : ℝ) with c51 | c51
  · refine ⟨5, 2 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c50, c51]
  rcases lt_or_ge (t - ⌊t⌋) (377968 / 1170759 : ℝ) with c52 | c52
  · refine ⟨23, 8 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c51, c52]
  rcases lt_or_ge (t - ⌊t⌋) (510509 / 1561012 : ℝ) with c53 | c53
  · refine ⟨15, 6 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c52, c53]
  rcases lt_or_ge (t - ⌊t⌋) (134060 / 390253 : ℝ) with c54 | c54
  · refine ⟨3, 2 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c53, c54]
  rcases lt_or_ge (t - ⌊t⌋) (407663 / 1170759 : ℝ) with c55 | c55
  · refine ⟨8, 4 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c54, c55]
  rcases lt_or_ge (t - ⌊t⌋) (827675 / 2341518 : ℝ) with c56 | c56
  · refine ⟨11, 5 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c55, c56]
  rcases lt_or_ge (t - ⌊t⌋) (418301 / 1170759 : ℝ) with c57 | c57
  · refine ⟨17, 7 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c56, c57]
  rcases lt_or_ge (t - ⌊t⌋) (562345 / 1561012 : ℝ) with c58 | c58
  · refine ⟨19, 8 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c57, c58]
  rcases lt_or_ge (t - ⌊t⌋) (2415788 / 6634301 : ℝ) with c59 | c59
  · refine ⟨16, 7 + 17 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c58, c59]
  rcases lt_or_ge (t - ⌊t⌋) (1137999 / 3122024 : ℝ) with c60 | c60
  · refine ⟨23, 9 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c59, c60]
  rcases lt_or_ge (t - ⌊t⌋) (1590738 / 4292783 : ℝ) with c61 | c61
  · refine ⟨10, 5 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c60, c61]
  rcases lt_or_ge (t - ⌊t⌋) (458752 / 1170759 : ℝ) with c62 | c62
  · refine ⟨2, 2 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c61, c62]
  rcases lt_or_ge (t - ⌊t⌋) (1074204 / 2731771 : ℝ) with c63 | c63
  · refine ⟨13, 6 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c62, c63]
  rcases lt_or_ge (t - ⌊t⌋) (779332 / 1951265 : ℝ) with c64 | c64
  · refine ⟨9, 4 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c63, c64]
  rcases lt_or_ge (t - ⌊t⌋) (1116182 / 2731771 : ℝ) with c65 | c65
  · refine ⟨6, 3 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c64, c65]
  rcases lt_or_ge (t - ⌊t⌋) (1600989 / 3902530 : ℝ) with c66 | c66
  · refine ⟨19, 9 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c65, c66]
  rcases lt_or_ge (t - ⌊t⌋) (2900059 / 7024554 : ℝ) with c67 | c67
  · refine ⟨17, 8 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c66, c67]
  rcases lt_or_ge (t - ⌊t⌋) (347363 / 780506 : ℝ) with c68 | c68
  · refine ⟨1, 1 + 2 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c67, c68]
  rcases lt_or_ge (t - ⌊t⌋) (4194503 / 9366072 : ℝ) with c69 | c69
  · refine ⟨23, 11 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c68, c69]
  rcases lt_or_ge (t - ⌊t⌋) (1411271 / 3122024 : ℝ) with c70 | c70
  · refine ⟨15, 8 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c69, c70]
  rcases lt_or_ge (t - ⌊t⌋) (1613242 / 3512277 : ℝ) with c71 | c71
  · refine ⟨8, 5 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c70, c71]
  rcases lt_or_ge (t - ⌊t⌋) (181143 / 390253 : ℝ) with c72 | c72
  · refine ⟨12, 6 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c71, c72]
  rcases lt_or_ge (t - ⌊t⌋) (928813 / 1951265 : ℝ) with c73 | c73
  · refine ⟨4, 3 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c72, c73]
  rcases lt_or_ge (t - ⌊t⌋) (3920830 / 8195313 : ℝ) with c74 | c74
  · refine ⟨20, 11 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c73, c74]
  rcases lt_or_ge (t - ⌊t⌋) (1143703 / 2341518 : ℝ) with c75 | c75
  · refine ⟨5, 3 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c74, c75]
  rcases lt_or_ge (t - ⌊t⌋) (2883152 / 5853795 : ℝ) with c76 | c76
  · refine ⟨14, 8 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c75, c76]
  rcases lt_or_ge (t - ⌊t⌋) (1948917 / 3902530 : ℝ) with c77 | c77
  · refine ⟨9, 5 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c76, c77]
  rcases lt_or_ge (t - ⌊t⌋) (1585953 / 3122024 : ℝ) with c78 | c78
  · refine ⟨7, 5 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c77, c78]
  rcases lt_or_ge (t - ⌊t⌋) (995621 / 1951265 : ℝ) with c79 | c79
  · refine ⟨19, 11 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c78, c79]
  rcases lt_or_ge (t - ⌊t⌋) (3212795 / 6244048 : ℝ) with c80 | c80
  · refine ⟨15, 9 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c79, c80]
  rcases lt_or_ge (t - ⌊t⌋) (202988 / 390253 : ℝ) with c81 | c81
  · refine ⟨11, 7 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c80, c81]
  rcases lt_or_ge (t - ⌊t⌋) (1226855 / 2341518 : ℝ) with c82 | c82
  · refine ⟨17, 10 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c81, c82]
  rcases lt_or_ge (t - ⌊t⌋) (615869 / 1170759 : ℝ) with c83 | c83
  · refine ⟨20, 12 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c82, c83]
  rcases lt_or_ge (t - ⌊t⌋) (412349 / 780506 : ℝ) with c84 | c84
  · refine ⟨27, 15 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c83, c84]
  rcases lt_or_ge (t - ⌊t⌋) (4975009 / 9366072 : ℝ) with c85 | c85
  · refine ⟨23, 13 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c84, c85]
  rcases lt_or_ge (t - ⌊t⌋) (1464457 / 2731771 : ℝ) with c86 | c86
  · refine ⟨13, 8 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c85, c86]
  rcases lt_or_ge (t - ⌊t⌋) (2745112 / 5073289 : ℝ) with c87 | c87
  · refine ⟨12, 7 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c86, c87]
  rcases lt_or_ge (t - ⌊t⌋) (5290384 / 9756325 : ℝ) with c88 | c88
  · refine ⟨24, 14 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c87, c88]
  rcases lt_or_ge (t - ⌊t⌋) (215205 / 390253 : ℝ) with c89 | c89
  · refine ⟨6, 4 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c88, c89]
  rcases lt_or_ge (t - ⌊t⌋) (2371244 / 4292783 : ℝ) with c90 | c90
  · refine ⟨10, 7 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c89, c90]
  rcases lt_or_ge (t - ⌊t⌋) (4769225 / 8585566 : ℝ) with c91 | c91
  · refine ⟨21, 13 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c90, c91]
  rcases lt_or_ge (t - ⌊t⌋) (218227 / 390253 : ℝ) with c92 | c92
  · refine ⟨14, 9 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c91, c92]
  rcases lt_or_ge (t - ⌊t⌋) (4372737 / 7805060 : ℝ) with c93 | c93
  · refine ⟨19, 12 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c92, c93]
  rcases lt_or_ge (t - ⌊t⌋) (5929979 / 10536831 : ℝ) with c94 | c94
  · refine ⟨26, 16 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c93, c94]
  rcases lt_or_ge (t - ⌊t⌋) (2003495 / 3512277 : ℝ) with c95 | c95
  · refine ⟨8, 6 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c94, c95]
  rcases lt_or_ge (t - ⌊t⌋) (1567112 / 2731771 : ℝ) with c96 | c96
  · refine ⟨20, 13 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c95, c96]
  rcases lt_or_ge (t - ⌊t⌋) (450381 / 780506 : ℝ) with c97 | c97
  · refine ⟨15, 10 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c96, c97]
  rcases lt_or_ge (t - ⌊t⌋) (926493 / 1561012 : ℝ) with c98 | c98
  · refine ⟨3, 3 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c97, c98]
  rcases lt_or_ge (t - ⌊t⌋) (233917 / 390253 : ℝ) with c99 | c99
  · refine ⟨9, 6 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c98, c99]
  rcases lt_or_ge (t - ⌊t⌋) (2826109 / 4683036 : ℝ) with c100 | c100
  · refine ⟨11, 8 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c99, c100]
  rcases lt_or_ge (t - ⌊t⌋) (3319167 / 5463542 : ℝ) with c101 | c101
  · refine ⟨13, 9 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c100, c101]
  rcases lt_or_ge (t - ⌊t⌋) (476299 / 780506 : ℝ) with c102 | c102
  · refine ⟨19, 13 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c101, c102]
  rcases lt_or_ge (t - ⌊t⌋) (6210351 / 10146578 : ℝ) with c103 | c103
  · refine ⟨25, 16 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c102, c103]
  rcases lt_or_ge (t - ⌊t⌋) (1918505 / 3122024 : ℝ) with c104 | c104
  · refine ⟨23, 15 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c103, c104]
  rcases lt_or_ge (t - ⌊t⌋) (3135365 / 5073289 : ℝ) with c105 | c105
  · refine ⟨12, 8 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c104, c105]
  rcases lt_or_ge (t - ⌊t⌋) (5091589 / 8195313 : ℝ) with c106 | c106
  · refine ⟨20, 14 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c105, c106]
  rcases lt_or_ge (t - ⌊t⌋) (3663658 / 5853795 : ℝ) with c107 | c107
  · refine ⟨14, 10 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c106, c107]
  rcases lt_or_ge (t - ⌊t⌋) (988103 / 1561012 : ℝ) with c108 | c108
  · refine ⟨7, 6 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c107, c108]
  rcases lt_or_ge (t - ⌊t⌋) (4461071 / 7024554 : ℝ) with c109 | c109
  · refine ⟨17, 12 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c108, c109]
  rcases lt_or_ge (t - ⌊t⌋) (6710485 / 10536831 : ℝ) with c110 | c110
  · refine ⟨26, 18 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c109, c110]
  rcases lt_or_ge (t - ⌊t⌋) (3993301 / 6244048 : ℝ) with c111 | c111
  · refine ⟨15, 11 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c110, c111]
  rcases lt_or_ge (t - ⌊t⌋) (2761497 / 4292783 : ℝ) with c112 | c112
  · refine ⟨10, 8 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c111, c112]
  rcases lt_or_ge (t - ⌊t⌋) (504521 / 780506 : ℝ) with c113 | c113
  · refine ⟨21, 15 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c112, c113]
  rcases lt_or_ge (t - ⌊t⌋) (766978 / 1170759 : ℝ) with c114 | c114
  · refine ⟨5, 4 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c113, c114]
  rcases lt_or_ge (t - ⌊t⌋) (4367053 / 6634301 : ℝ) with c115 | c115
  · refine ⟨16, 12 + 17 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c114, c115]
  rcases lt_or_ge (t - ⌊t⌋) (5153243 / 7805060 : ℝ) with c116 | c116
  · refine ⟨19, 14 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c115, c116]
  rcases lt_or_ge (t - ⌊t⌋) (6461143 / 9756325 : ℝ) with c117 | c117
  · refine ⟨24, 17 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c116, c117]
  rcases lt_or_ge (t - ⌊t⌋) (1319066 / 1951265 : ℝ) with c118 | c118
  · refine ⟨4, 4 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c117, c118]
  rcases lt_or_ge (t - ⌊t⌋) (265972 / 390253 : ℝ) with c119 | c119
  · refine ⟨8, 7 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c118, c119]
  rcases lt_or_ge (t - ⌊t⌋) (1608181 / 2341518 : ℝ) with c120 | c120
  · refine ⟨11, 9 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c119, c120]
  rcases lt_or_ge (t - ⌊t⌋) (1896688 / 2731771 : ℝ) with c121 | c121
  · refine ⟨6, 5 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c120, c121]
  rcases lt_or_ge (t - ⌊t⌋) (2729423 / 3902530 : ℝ) with c122 | c122
  · refine ⟨9, 7 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c121, c122]
  rcases lt_or_ge (t - ⌊t⌋) (2191777 / 3122024 : ℝ) with c123 | c123
  · refine ⟨15, 12 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c122, c123]
  rcases lt_or_ge (t - ⌊t⌋) (6851396 / 9756325 : ℝ) with c124 | c124
  · refine ⟨24, 18 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c123, c124]
  rcases lt_or_ge (t - ⌊t⌋) (849005 / 1170759 : ℝ) with c125 | c125
  · refine ⟨2, 3 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c124, c125]
  rcases lt_or_ge (t - ⌊t⌋) (284313 / 390253 : ℝ) with c126 | c126
  · refine ⟨18, 14 + 19 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c125, c126]
  rcases lt_or_ge (t - ⌊t⌋) (3151750 / 4292783 : ℝ) with c127 | c127
  · refine ⟨10, 9 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c126, c127]
  rcases lt_or_ge (t - ⌊t⌋) (6330237 / 8585566 : ℝ) with c128 | c128
  · refine ⟨21, 17 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c127, c128]
  rcases lt_or_ge (t - ⌊t⌋) (1154379 / 1561012 : ℝ) with c129 | c129
  · refine ⟨23, 18 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c128, c129]
  rcases lt_or_ge (t - ⌊t⌋) (7241649 / 9756325 : ℝ) with c130 | c130
  · refine ⟨24, 19 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c129, c130]
  rcases lt_or_ge (t - ⌊t⌋) (2028601 / 2731771 : ℝ) with c131 | c131
  · refine ⟨27, 21 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c130, c131]
  rcases lt_or_ge (t - ⌊t⌋) (5241577 / 7024554 : ℝ) with c132 | c132
  · refine ⟨17, 14 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c131, c132]
  rcases lt_or_ge (t - ⌊t⌋) (4099673 / 5463542 : ℝ) with c133 | c133
  · refine ⟨13, 11 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c132, c133]
  rcases lt_or_ge (t - ⌊t⌋) (2366459 / 3122024 : ℝ) with c134 | c134
  · refine ⟨7, 7 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c133, c134]
  rcases lt_or_ge (t - ⌊t⌋) (5933749 / 7805060 : ℝ) with c135 | c135
  · refine ⟨19, 16 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c134, c135]
  rcases lt_or_ge (t - ⌊t⌋) (4773807 / 6244048 : ℝ) with c136 | c136
  · refine ⟨15, 13 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c135, c136]
  rcases lt_or_ge (t - ⌊t⌋) (1202205 / 1561012 : ℝ) with c137 | c137
  · refine ⟨11, 10 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c136, c137]
  rcases lt_or_ge (t - ⌊t⌋) (3915871 / 5073289 : ℝ) with c138 | c138
  · refine ⟨12, 10 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c137, c138]
  rcases lt_or_ge (t - ⌊t⌋) (5147559 / 6634301 : ℝ) with c139 | c139
  · refine ⟨16, 14 + 17 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c138, c139]
  rcases lt_or_ge (t - ⌊t⌋) (1214951 / 1561012 : ℝ) with c140 | c140
  · refine ⟨27, 22 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c139, c140]
  rcases lt_or_ge (t - ⌊t⌋) (7316527 / 9366072 : ℝ) with c141 | c141
  · refine ⟨23, 19 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c140, c141]
  rcases lt_or_ge (t - ⌊t⌋) (3360245 / 4292783 : ℝ) with c142 | c142
  · refine ⟨21, 18 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c141, c142]
  rcases lt_or_ge (t - ⌊t⌋) (8271497 / 10536831 : ℝ) with c143 | c143
  · refine ⟨26, 22 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c142, c143]
  rcases lt_or_ge (t - ⌊t⌋) (2784001 / 3512277 : ℝ) with c144 | c144
  · refine ⟨8, 8 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c143, c144]
  rcases lt_or_ge (t - ⌊t⌋) (1559838 / 1951265 : ℝ) with c145 | c145
  · refine ⟨9, 8 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c144, c145]
  rcases lt_or_ge (t - ⌊t⌋) (2815915 / 3512277 : ℝ) with c146 | c146
  · refine ⟨17, 15 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c145, c146]
  rcases lt_or_ge (t - ⌊t⌋) (4080808 / 5073289 : ℝ) with c147 | c147
  · refine ⟨25, 21 + 26 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c146, c147]
  rcases lt_or_ge (t - ⌊t⌋) (7241794 / 8975819 : ℝ) with c148 | c148
  · refine ⟨22, 19 + 23 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c147, c148]
  rcases lt_or_ge (t - ⌊t⌋) (3162001 / 3902530 : ℝ) with c149 | c149
  · refine ⟨19, 17 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c148, c149]
  rcases lt_or_ge (t - ⌊t⌋) (6652601 / 8195313 : ℝ) with c150 | c150
  · refine ⟨20, 18 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c149, c150]
  rcases lt_or_ge (t - ⌊t⌋) (641403 / 780506 : ℝ) with c151 | c151
  · refine ⟨5, 5 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c150, c151]
  rcases lt_or_ge (t - ⌊t⌋) (4834417 / 5853795 : ℝ) with c152 | c152
  · refine ⟨14, 13 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c151, c152]
  rcases lt_or_ge (t - ⌊t⌋) (7110743 / 8585566 : ℝ) with c153 | c153
  · refine ⟨21, 19 + 22 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c152, c153]
  rcases lt_or_ge (t - ⌊t⌋) (658373 / 780506 : ℝ) with c154 | c154
  · refine ⟨3, 4 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c153, c154]
  rcases lt_or_ge (t - ⌊t⌋) (4306124 / 5073289 : ℝ) with c155 | c155
  · refine ⟨12, 11 + 13 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c154, c155]
  rcases lt_or_ge (t - ⌊t⌋) (999217 / 1170759 : ℝ) with c156 | c156
  · refine ⟨11, 11 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c155, c156]
  rcases lt_or_ge (t - ⌊t⌋) (2007361 / 2341518 : ℝ) with c157 | c157
  · refine ⟨17, 16 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c156, c157]
  rcases lt_or_ge (t - ⌊t⌋) (1342851 / 1561012 : ℝ) with c158 | c158
  · refine ⟨19, 18 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c157, c158]
  rcases lt_or_ge (t - ⌊t⌋) (8412408 / 9756325 : ℝ) with c159 | c159
  · refine ⟨24, 22 + 25 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c158, c159]
  rcases lt_or_ge (t - ⌊t⌋) (1709319 / 1951265 : ℝ) with c160 | c160
  · refine ⟨4, 5 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c159, c160]
  rcases lt_or_ge (t - ⌊t⌋) (344589 / 390253 : ℝ) with c161 | c161
  · refine ⟨7, 8 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c160, c161]
  rcases lt_or_ge (t - ⌊t⌋) (6572706 / 7414807 : ℝ) with c162 | c162
  · refine ⟨18, 17 + 19 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c161, c162]
  rcases lt_or_ge (t - ⌊t⌋) (5554313 / 6244048 : ℝ) with c163 | c163
  · refine ⟨15, 15 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c162, c163]
  rcases lt_or_ge (t - ⌊t⌋) (5928065 / 6634301 : ℝ) with c164 | c164
  · refine ⟨16, 16 + 17 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c163, c164]
  rcases lt_or_ge (t - ⌊t⌋) (3509929 / 3902530 : ℝ) with c165 | c165
  · refine ⟨9, 9 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c164, c165]
  rcases lt_or_ge (t - ⌊t⌋) (3174254 / 3512277 : ℝ) with c166 | c166
  · refine ⟨8, 9 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c165, c166]
  rcases lt_or_ge (t - ⌊t⌋) (7433107 / 8195313 : ℝ) with c167 | c167
  · refine ⟨20, 20 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c166, c167]
  rcases lt_or_ge (t - ⌊t⌋) (1776127 / 1951265 : ℝ) with c168 | c168
  · refine ⟨19, 19 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c167, c168]
  rcases lt_or_ge (t - ⌊t⌋) (3932256 / 4292783 : ℝ) with c169 | c169
  · refine ⟨10, 11 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c168, c169]
  rcases lt_or_ge (t - ⌊t⌋) (368808 / 390253 : ℝ) with c170 | c170
  · refine ⟨1, 2 + 2 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c169, c170]
  rcases lt_or_ge (t - ⌊t⌋) (8877539 / 9366072 : ℝ) with c171 | c171
  · refine ⟨23, 23 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c170, c171]
  rcases lt_or_ge (t - ⌊t⌋) (2972283 / 3122024 : ℝ) with c172 | c172
  · refine ⟨15, 16 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c171, c172]
  rcases lt_or_ge (t - ⌊t⌋) (7823360 / 8195313 : ℝ) with c173 | c173
  · refine ⟨20, 21 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c172, c173]
  rcases lt_or_ge (t - ⌊t⌋) (1871641 / 1951265 : ℝ) with c174 | c174
  · refine ⟨14, 15 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c173, c174]
  rcases lt_or_ge (t - ⌊t⌋) (7494761 / 7805060 : ℝ) with c175 | c175
  · refine ⟨19, 20 + 20 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c174, c175]
  rcases lt_or_ge (t - ⌊t⌋) (2635216 / 2731771 : ℝ) with c176 | c176
  · refine ⟨13, 14 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c175, c176]
  rcases lt_or_ge (t - ⌊t⌋) (6802589 / 7024554 : ℝ) with c177 | c177
  · refine ⟨17, 18 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c176, c177]
  rcases lt_or_ge (t - ⌊t⌋) (10222762 / 10536831 : ℝ) with c178 | c178
  · refine ⟨26, 27 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c177, c178]
  rcases lt_or_ge (t - ⌊t⌋) (2677194 / 2731771 : ℝ) with c179 | c179
  · refine ⟨6, 7 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c178, c179]
  rcases lt_or_ge (t - ⌊t⌋) (1157231 / 1170759 : ℝ) with c180 | c180
  · refine ⟨5, 6 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c179, c180]
  rcases lt_or_ge (t - ⌊t⌋) (7353212 / 7414807 : ℝ) with c181 | c181
  · refine ⟨18, 19 + 19 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c180, c181]
  rcases lt_or_ge (t - ⌊t⌋) (10846175 / 10927084 : ℝ) with c182 | c182
  · refine ⟨27, 28 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c181, c182]
  rcases lt_or_ge (t - ⌊t⌋) (1950091 / 1951265 : ℝ) with c183 | c183
  · refine ⟨9, 10 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c182, c183]
  refine ⟨7, 9 + 8 * ⌊t⌋, ?_⟩
  simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
  rw [abs_lt]
  push_cast
  constructor <;> linarith only [c183, h1]

#print axioms cover
#print axioms v_injective
#print axioms v_pos
end SLRAudit.N28
