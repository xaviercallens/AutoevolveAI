import Mathlib.Tactic

set_option linter.unusedSimpArgs false
set_option maxHeartbeats 0
namespace SLRAudit.N11

/-- velocities of certificate n = 11 -/
def v : Fin 11 → ℕ := ![1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
/-- shifts s_i = a_i / 2305 -/
def s : Fin 11 → ℚ := ![1104/2305, 911/2305, 2109/2305, 1161/2305, 257/2305, 1343/2305, 984/2305, 1347/2305, 172/2305, 1084/2305, 1801/2305]

theorem v_injective : Function.Injective v := by decide
theorem v_pos : ∀ i, 0 < v i := by decide

/-- covering: for every real t some runner is within distance < 1/12 of an integer. -/
theorem cover : ∀ t : ℝ, ∃ i : Fin 11, ∃ k : ℤ, |((s i : ℚ) : ℝ) + ((v i : ℕ) : ℝ) * t - (k : ℝ)| < 1 / 12 := by
  intro t
  have h0 : (0 : ℝ) ≤ t - ⌊t⌋ := by have := Int.floor_le t; linarith
  have h1 : t - ⌊t⌋ < (1 : ℝ) := by have := Int.lt_floor_add_one t; linarith
  rcases lt_or_ge (t - ⌊t⌋) (241 / 248940 : ℝ) with c0 | c0
  · refine ⟨8, 0 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [h0, c0]
  rcases lt_or_ge (t - ⌊t⌋) (4657 / 82980 : ℝ) with c1 | c1
  · refine ⟨2, 1 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c0, c1]
  rcases lt_or_ge (t - ⌊t⌋) (13849 / 165960 : ℝ) with c2 | c2
  · refine ⟨5, 1 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1, c2]
  rcases lt_or_ge (t - ⌊t⌋) (18157 / 193620 : ℝ) with c3 | c3
  · refine ⟨6, 1 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2, c3]
  rcases lt_or_ge (t - ⌊t⌋) (27901 / 248940 : ℝ) with c4 | c4
  · refine ⟨8, 1 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c3, c4]
  rcases lt_or_ge (t - ⌊t⌋) (16033 / 110640 : ℝ) with c5 | c5
  · refine ⟨3, 1 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c4, c5]
  rcases lt_or_ge (t - ⌊t⌋) (44617 / 276600 : ℝ) with c6 | c6
  · refine ⟨9, 2 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c5, c6]
  rcases lt_or_ge (t - ⌊t⌋) (26881 / 138300 : ℝ) with c7 | c7
  · refine ⟨4, 1 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c6, c7]
  rcases lt_or_ge (t - ⌊t⌋) (63673 / 304260 : ℝ) with c8 | c8
  · refine ⟨10, 3 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c7, c8]
  rcases lt_or_ge (t - ⌊t⌋) (55561 / 248940 : ℝ) with c9 | c9
  · refine ⟨8, 2 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c8, c9]
  rcases lt_or_ge (t - ⌊t⌋) (41509 / 165960 : ℝ) with c10 | c10
  · refine ⟨5, 2 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c9, c10]
  rcases lt_or_ge (t - ⌊t⌋) (72277 / 276600 : ℝ) with c11 | c11
  · refine ⟨9, 3 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c10, c11]
  rcases lt_or_ge (t - ⌊t⌋) (19033 / 55320 : ℝ) with c12 | c12
  · refine ⟨1, 1 + 2 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c11, c12]
  rcases lt_or_ge (t - ⌊t⌋) (32317 / 82980 : ℝ) with c13 | c13
  · refine ⟨2, 2 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c12, c13]
  rcases lt_or_ge (t - ⌊t⌋) (69169 / 165960 : ℝ) with c14 | c14
  · refine ⟨5, 3 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c13, c14]
  rcases lt_or_ge (t - ⌊t⌋) (96781 / 221280 : ℝ) with c15 | c15
  · refine ⟨7, 4 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c14, c15]
  rcases lt_or_ge (t - ⌊t⌋) (110881 / 248940 : ℝ) with c16 | c16
  · refine ⟨8, 4 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c15, c16]
  rcases lt_or_ge (t - ⌊t⌋) (16717 / 27660 : ℝ) with c17 | c17
  · refine ⟨0, 1 + 1 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c16, c17]
  rcases lt_or_ge (t - ⌊t⌋) (71353 / 110640 : ℝ) with c18 | c18
  · refine ⟨3, 3 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c17, c18]
  rcases lt_or_ge (t - ⌊t⌋) (128797 / 193620 : ℝ) with c19 | c19
  · refine ⟨6, 5 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c18, c19]
  rcases lt_or_ge (t - ⌊t⌋) (166201 / 248940 : ℝ) with c20 | c20
  · refine ⟨8, 6 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c19, c20]
  rcases lt_or_ge (t - ⌊t⌋) (59977 / 82980 : ℝ) with c21 | c21
  · refine ⟨2, 3 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c20, c21]
  rcases lt_or_ge (t - ⌊t⌋) (124489 / 165960 : ℝ) with c22 | c22
  · refine ⟨5, 5 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c21, c22]
  rcases lt_or_ge (t - ⌊t⌋) (210577 / 276600 : ℝ) with c23 | c23
  · refine ⟨9, 8 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c22, c23]
  rcases lt_or_ge (t - ⌊t⌋) (46693 / 55320 : ℝ) with c24 | c24
  · refine ⟨1, 2 + 2 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c23, c24]
  rcases lt_or_ge (t - ⌊t⌋) (257293 / 304260 : ℝ) with c25 | c25
  · refine ⟨10, 10 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c24, c25]
  rcases lt_or_ge (t - ⌊t⌋) (238237 / 276600 : ℝ) with c26 | c26
  · refine ⟨9, 9 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c25, c26]
  rcases lt_or_ge (t - ⌊t⌋) (99013 / 110640 : ℝ) with c27 | c27
  · refine ⟨3, 4 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c26, c27]
  rcases lt_or_ge (t - ⌊t⌋) (152149 / 165960 : ℝ) with c28 | c28
  · refine ⟨5, 6 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c27, c28]
  rcases lt_or_ge (t - ⌊t⌋) (207421 / 221280 : ℝ) with c29 | c29
  · refine ⟨7, 8 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c28, c29]
  rcases lt_or_ge (t - ⌊t⌋) (184117 / 193620 : ℝ) with c30 | c30
  · refine ⟨6, 7 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c29, c30]
  rcases lt_or_ge (t - ⌊t⌋) (265897 / 276600 : ℝ) with c31 | c31
  · refine ⟨9, 10 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c30, c31]
  rcases lt_or_ge (t - ⌊t⌋) (137521 / 138300 : ℝ) with c32 | c32
  · refine ⟨4, 5 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c31, c32]
  refine ⟨8, 9 + 9 * ⌊t⌋, ?_⟩
  simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
  rw [abs_lt]
  push_cast
  constructor <;> linarith only [c32, h1]

#print axioms cover
#print axioms v_injective
#print axioms v_pos
end SLRAudit.N11
