import Mathlib.Tactic

set_option linter.unusedSimpArgs false
set_option maxHeartbeats 0
namespace SLRAudit.N05

/-- velocities of certificate n = 5 -/
def v : Fin 5 → ℕ := ![1, 2, 3, 4, 5]
/-- shifts s_i = a_i / 577 -/
def s : Fin 5 → ℚ := ![322/577, 270/577, 11/577, 235/577, 345/577]

theorem v_injective : Function.Injective v := by decide
theorem v_pos : ∀ i, 0 < v i := by decide

/-- covering: for every real t some runner is within distance < 1/6 of an integer. -/
theorem cover : ∀ t : ℝ, ∃ i : Fin 5, ∃ k : ℤ, |((s i : ℚ) : ℝ) + ((v i : ℕ) : ℝ) * t - (k : ℝ)| < 1 / 6 := by
  intro t
  have h0 : (0 : ℝ) ≤ t - ⌊t⌋ := by have := Int.floor_le t; linarith
  have h1 : t - ⌊t⌋ < (1 : ℝ) := by have := Int.lt_floor_add_one t; linarith
  rcases lt_or_ge (t - ⌊t⌋) (511 / 10386 : ℝ) with c0 | c0
  · refine ⟨2, 0 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [h0, c0]
  rcases lt_or_ge (t - ⌊t⌋) (1969 / 17310 : ℝ) with c1 | c1
  · refine ⟨4, 1 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c0, c1]
  rcases lt_or_ge (t - ⌊t⌋) (2629 / 13848 : ℝ) with c2 | c2
  · refine ⟨3, 1 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1, c2]
  rcases lt_or_ge (t - ⌊t⌋) (2419 / 6924 : ℝ) with c3 | c3
  · refine ⟨1, 1 + 2 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2, c3]
  rcases lt_or_ge (t - ⌊t⌋) (2107 / 3462 : ℝ) with c4 | c4
  · refine ⟨0, 1 + 1 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c3, c4]
  rcases lt_or_ge (t - ⌊t⌋) (7435 / 10386 : ℝ) with c5 | c5
  · refine ⟨2, 2 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c4, c5]
  rcases lt_or_ge (t - ⌊t⌋) (5881 / 6924 : ℝ) with c6 | c6
  · refine ⟨1, 2 + 2 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c5, c6]
  rcases lt_or_ge (t - ⌊t⌋) (15817 / 17310 : ℝ) with c7 | c7
  · refine ⟨4, 5 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c6, c7]
  rcases lt_or_ge (t - ⌊t⌋) (13015 / 13848 : ℝ) with c8 | c8
  · refine ⟨3, 4 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c7, c8]
  refine ⟨2, 3 + 3 * ⌊t⌋, ?_⟩
  simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
  rw [abs_lt]
  push_cast
  constructor <;> linarith only [c8, h1]

#print axioms cover
#print axioms v_injective
#print axioms v_pos
end SLRAudit.N05
