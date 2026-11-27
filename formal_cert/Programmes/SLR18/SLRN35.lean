import Mathlib.Tactic

set_option linter.unusedSimpArgs false
set_option maxHeartbeats 0
namespace SLRAudit.N35

/-- velocities of certificate n = 35 -/
def v : Fin 35 → ℕ := ![68, 2, 60, 4, 5, 6, 1, 8, 9, 33, 19, 12, 35, 14, 15, 16, 3, 18, 42, 54, 21, 7, 32, 24, 48, 28, 27, 10, 11, 30, 56, 45, 36, 70, 72]
/-- shifts s_i = a_i / 20737 -/
def s : Fin 35 → ℚ := ![8462/20737, 16639/20737, 14000/20737, 18294/20737, 5370/20737, 1173/20737, 12529/20737, 11696/20737, 19350/20737, 4641/20737, 2078/20737, 8170/20737, 10409/20737, 892/20737, 6426/20737, 19585/20737, 8366/20737, 13477/20737, 19534/20737, 3065/20737, 7508/20737, 13405/20737, 11112/20737, 12054/20737, 20313/20737, 15015/20737, 4695/20737, 7676/20737, 18182/20737, 18415/20737, 11015/20737, 16983/20737, 11629/20737, 1803/20737, 799/20737]

theorem v_injective : Function.Injective v := by decide
theorem v_pos : ∀ i, 0 < v i := by decide

/-- covering: for every real t some runner is within distance < 1/36 of an integer. -/
theorem cover : ∀ t : ℝ, ∃ i : Fin 35, ∃ k : ℤ, |((s i : ℚ) : ℝ) + ((v i : ℕ) : ℝ) * t - (k : ℝ)| < 1 / 36 := by
  intro t
  have h0 : (0 : ℝ) ≤ t - ⌊t⌋ := by have := Int.floor_le t; linarith
  have h1 : t - ⌊t⌋ < (1 : ℝ) := by have := Int.lt_floor_add_one t; linarith
  rcases lt_or_ge (t - ⌊t⌋) (36001 / 35833536 : ℝ) with c0 | c0
  · refine ⟨24, 1 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [h0, c0]
  rcases lt_or_ge (t - ⌊t⌋) (64045 / 31354344 : ℝ) with c1 | c1
  · refine ⟨18, 1 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c0, c1]
  rcases lt_or_ge (t - ⌊t⌋) (62209 / 11944512 : ℝ) with c2 | c2
  · refine ⟨15, 1 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c1, c2]
  rcases lt_or_ge (t - ⌊t⌋) (70669 / 6718788 : ℝ) with c3 | c3
  · refine ⟨8, 1 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c2, c3]
  rcases lt_or_ge (t - ⌊t⌋) (10247 / 746532 : ℝ) with c4 | c4
  · refine ⟨28, 1 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c3, c4]
  rcases lt_or_ge (t - ⌊t⌋) (367237 / 23889024 : ℝ) with c5 | c5
  · refine ⟨22, 1 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c4, c5]
  rcases lt_or_ge (t - ⌊t⌋) (656929 / 40312728 : ℝ) with c6 | c6
  · refine ⟨19, 1 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c5, c6]
  rcases lt_or_ge (t - ⌊t⌋) (333325 / 17916768 : ℝ) with c7 | c7
  · refine ⟨23, 1 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c6, c7]
  rcases lt_or_ge (t - ⌊t⌋) (282097 / 13437576 : ℝ) with c8 | c8
  · refine ⟨17, 1 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c7, c8]
  rcases lt_or_ge (t - ⌊t⌋) (782533 / 35833536 : ℝ) with c9 | c9
  · refine ⟨24, 2 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c8, c9]
  rcases lt_or_ge (t - ⌊t⌋) (1009801 / 44791920 : ℝ) with c10 | c10
  · refine ⟨2, 2 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c9, c10]
  rcases lt_or_ge (t - ⌊t⌋) (108685 / 2986128 : ℝ) with c11 | c11
  · refine ⟨3, 1 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c10, c11]
  rcases lt_or_ge (t - ⌊t⌋) (850861 / 22395960 : ℝ) with c12 | c12
  · refine ⟨29, 2 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c11, c12]
  rcases lt_or_ge (t - ⌊t⌋) (1955701 / 50764176 : ℝ) with c13 | c13
  · refine ⟨0, 3 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c12, c13]
  rcases lt_or_ge (t - ⌊t⌋) (1756333 / 44791920 : ℝ) with c14 | c14
  · refine ⟨2, 3 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c13, c14]
  rcases lt_or_ge (t - ⌊t⌋) (1095157 / 26875152 : ℝ) with c15 | c15
  · refine ⟨32, 2 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c14, c15]
  rcases lt_or_ge (t - ⌊t⌋) (2231569 / 53750304 : ℝ) with c16 | c16
  · refine ⟨34, 3 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c15, c16]
  rcases lt_or_ge (t - ⌊t⌋) (1529065 / 35833536 : ℝ) with c17 | c17
  · refine ⟨24, 3 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c16, c17]
  rcases lt_or_ge (t - ⌊t⌋) (1139077 / 26128620 : ℝ) with c18 | c18
  · refine ⟨12, 2 + 35 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c17, c18]
  rcases lt_or_ge (t - ⌊t⌋) (1863793 / 41805792 : ℝ) with c19 | c19
  · refine ⟨30, 3 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c18, c19]
  rcases lt_or_ge (t - ⌊t⌋) (535933 / 11197980 : ℝ) with c20 | c20
  · refine ⟨14, 1 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c19, c20]
  rcases lt_or_ge (t - ⌊t⌋) (284689 / 5225724 : ℝ) with c21 | c21
  · refine ⟨21, 1 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c20, c21]
  rcases lt_or_ge (t - ⌊t⌋) (346213 / 5972256 : ℝ) with c22 | c22
  · refine ⟨7, 1 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c21, c22]
  rcases lt_or_ge (t - ⌊t⌋) (1079857 / 17916768 : ℝ) with c23 | c23
  · refine ⟨23, 2 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c22, c23]
  rcases lt_or_ge (t - ⌊t⌋) (490933 / 7465320 : ℝ) with c24 | c24
  · refine ⟨27, 1 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c23, c24]
  rcases lt_or_ge (t - ⌊t⌋) (808741 / 11944512 : ℝ) with c25 | c25
  · refine ⟨15, 2 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c24, c25]
  rcases lt_or_ge (t - ⌊t⌋) (735157 / 10451448 : ℝ) with c26 | c26
  · refine ⟨13, 1 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c25, c26]
  rcases lt_or_ge (t - ⌊t⌋) (1597393 / 22395960 : ℝ) with c27 | c27
  · refine ⟨29, 3 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c26, c27]
  rcases lt_or_ge (t - ⌊t⌋) (1885609 / 26128620 : ℝ) with c28 | c28
  · refine ⟨12, 3 + 35 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c27, c28]
  rcases lt_or_ge (t - ⌊t⌋) (2303641 / 31354344 : ℝ) with c29 | c29
  · refine ⟨18, 4 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c28, c29]
  rcases lt_or_ge (t - ⌊t⌋) (1028629 / 13437576 : ℝ) with c30 | c30
  · refine ⟨17, 2 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c29, c30]
  rcases lt_or_ge (t - ⌊t⌋) (1860301 / 23889024 : ℝ) with c31 | c31
  · refine ⟨22, 3 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c30, c31]
  rcases lt_or_ge (t - ⌊t⌋) (1243513 / 15677172 : ℝ) with c32 | c32
  · refine ⟨20, 2 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c31, c32]
  rcases lt_or_ge (t - ⌊t⌋) (479551 / 5972256 : ℝ) with c33 | c33
  · refine ⟨30, 5 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c32, c33]
  rcases lt_or_ge (t - ⌊t⌋) (1719793 / 20902896 : ℝ) with c34 | c34
  · refine ⟨25, 3 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c33, c34]
  rcases lt_or_ge (t - ⌊t⌋) (4195297 / 50764176 : ℝ) with c35 | c35
  · refine ⟨0, 6 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c34, c35]
  rcases lt_or_ge (t - ⌊t⌋) (4471165 / 53750304 : ℝ) with c36 | c36
  · refine ⟨34, 6 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c35, c36]
  rcases lt_or_ge (t - ⌊t⌋) (3022129 / 35833536 : ℝ) with c37 | c37
  · refine ⟨24, 5 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c36, c37]
  rcases lt_or_ge (t - ⌊t⌋) (2093257 / 24635556 : ℝ) with c38 | c38
  · refine ⟨9, 3 + 33 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c37, c38]
  rcases lt_or_ge (t - ⌊t⌋) (168265 / 1493064 : ℝ) with c39 | c39
  · refine ⟨1, 1 + 2 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c38, c39]
  rcases lt_or_ge (t - ⌊t⌋) (256493 / 2239596 : ℝ) with c40 | c40
  · refine ⟨14, 2 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c39, c40]
  rcases lt_or_ge (t - ⌊t⌋) (3888541 / 33593940 : ℝ) with c41 | c41
  · refine ⟨31, 6 + 45 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c40, c41]
  rcases lt_or_ge (t - ⌊t⌋) (817201 / 6718788 : ℝ) with c42 | c42
  · refine ⟨8, 2 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c41, c42]
  rcases lt_or_ge (t - ⌊t⌋) (5488993 / 44791920 : ℝ) with c43 | c43
  · refine ⟨2, 8 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c42, c43]
  rcases lt_or_ge (t - ⌊t⌋) (3334753 / 26875152 : ℝ) with c44 | c44
  · refine ⟨32, 5 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c43, c44]
  rcases lt_or_ge (t - ⌊t⌋) (6710761 / 53750304 : ℝ) with c45 | c45
  · refine ⟨34, 9 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c44, c45]
  rcases lt_or_ge (t - ⌊t⌋) (1990045 / 15677172 : ℝ) with c46 | c46
  · refine ⟨20, 3 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c45, c46]
  rcases lt_or_ge (t - ⌊t⌋) (1555273 / 11944512 : ℝ) with c47 | c47
  · refine ⟨15, 3 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c46, c47]
  rcases lt_or_ge (t - ⌊t⌋) (1775161 / 13437576 : ℝ) with c48 | c48
  · refine ⟨17, 3 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c47, c48]
  rcases lt_or_ge (t - ⌊t⌋) (1219681 / 8958384 : ℝ) with c49 | c49
  · refine ⟨11, 2 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c48, c49]
  rcases lt_or_ge (t - ⌊t⌋) (3090457 / 22395960 : ℝ) with c50 | c50
  · refine ⟨29, 5 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c49, c50]
  rcases lt_or_ge (t - ⌊t⌋) (1481689 / 10451448 : ℝ) with c51 | c51
  · refine ⟨13, 2 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c50, c51]
  rcases lt_or_ge (t - ⌊t⌋) (2572921 / 17916768 : ℝ) with c52 | c52
  · refine ⟨23, 4 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c51, c52]
  rcases lt_or_ge (t - ⌊t⌋) (573949 / 3732660 : ℝ) with c53 | c53
  · refine ⟨4, 1 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c52, c53]
  rcases lt_or_ge (t - ⌊t⌋) (725041 / 4479192 : ℝ) with c54 | c54
  · refine ⟨5, 1 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c53, c54]
  rcases lt_or_ge (t - ⌊t⌋) (247493 / 1493064 : ℝ) with c55 | c55
  · refine ⟨27, 2 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c54, c55]
  rcases lt_or_ge (t - ⌊t⌋) (8950357 / 53750304 : ℝ) with c56 | c56
  · refine ⟨34, 12 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c55, c56]
  rcases lt_or_ge (t - ⌊t⌋) (6008257 / 35833536 : ℝ) with c57 | c57
  · refine ⟨24, 9 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c56, c57]
  rcases lt_or_ge (t - ⌊t⌋) (5289769 / 31354344 : ℝ) with c58 | c58
  · refine ⟨18, 8 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c57, c58]
  rcases lt_or_ge (t - ⌊t⌋) (7089517 / 41805792 : ℝ) with c59 | c59
  · refine ⟨30, 10 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c58, c59]
  rcases lt_or_ge (t - ⌊t⌋) (3836989 / 22395960 : ℝ) with c60 | c60
  · refine ⟨29, 6 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c59, c60]
  rcases lt_or_ge (t - ⌊t⌋) (4099897 / 23889024 : ℝ) with c61 | c61
  · refine ⟨22, 6 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c60, c61]
  rcases lt_or_ge (t - ⌊t⌋) (7728589 / 44791920 : ℝ) with c62 | c62
  · refine ⟨2, 11 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c61, c62]
  rcases lt_or_ge (t - ⌊t⌋) (2736577 / 15677172 : ℝ) with c63 | c63
  · refine ⟨20, 4 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c62, c63]
  rcases lt_or_ge (t - ⌊t⌋) (4332853 / 24635556 : ℝ) with c64 | c64
  · refine ⟨9, 6 + 33 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c63, c64]
  rcases lt_or_ge (t - ⌊t⌋) (3584377 / 20156364 : ℝ) with c65 | c65
  · refine ⟨26, 5 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c64, c65]
  rcases lt_or_ge (t - ⌊t⌋) (1092745 / 5972256 : ℝ) with c66 | c66
  · refine ⟨7, 2 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c65, c66]
  rcases lt_or_ge (t - ⌊t⌋) (3319453 / 17916768 : ℝ) with c67 | c67
  · refine ⟨23, 5 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c66, c67]
  rcases lt_or_ge (t - ⌊t⌋) (2521693 / 13437576 : ℝ) with c68 | c68
  · refine ⟨17, 4 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c67, c68]
  rcases lt_or_ge (t - ⌊t⌋) (565627 / 2986128 : ℝ) with c69 | c69
  · refine ⟨25, 6 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c68, c69]
  rcases lt_or_ge (t - ⌊t⌋) (1031221 / 5225724 : ℝ) with c70 | c70
  · refine ⟨21, 2 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c69, c70]
  rcases lt_or_ge (t - ⌊t⌋) (5237 / 25164 : ℝ) with c71 | c71
  · refine ⟨16, 1 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c70, c71]
  rcases lt_or_ge (t - ⌊t⌋) (11189953 / 53750304 : ℝ) with c72 | c72
  · refine ⟨34, 15 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c71, c72]
  rcases lt_or_ge (t - ⌊t⌋) (7501321 / 35833536 : ℝ) with c73 | c73
  · refine ⟨24, 11 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c72, c73]
  rcases lt_or_ge (t - ⌊t⌋) (2228221 / 10451448 : ℝ) with c74 | c74
  · refine ⟨13, 3 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c73, c74]
  rcases lt_or_ge (t - ⌊t⌋) (4330909 / 20156364 : ℝ) with c75 | c75
  · refine ⟨26, 6 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c74, c75]
  rcases lt_or_ge (t - ⌊t⌋) (1966213 / 8958384 : ℝ) with c76 | c76
  · refine ⟨11, 3 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c75, c76]
  rcases lt_or_ge (t - ⌊t⌋) (8868781 / 40312728 : ℝ) with c77 | c77
  · refine ⟨19, 12 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c76, c77]
  rcases lt_or_ge (t - ⌊t⌋) (497587 / 2239596 : ℝ) with c78 | c78
  · refine ⟨20, 5 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c77, c78]
  rcases lt_or_ge (t - ⌊t⌋) (9329113 / 41805792 : ℝ) with c79 | c79
  · refine ⟨30, 13 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c78, c79]
  rcases lt_or_ge (t - ⌊t⌋) (4705921 / 20902896 : ℝ) with c80 | c80
  · refine ⟨25, 7 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c79, c80]
  rcases lt_or_ge (t - ⌊t⌋) (4065985 / 17916768 : ℝ) with c81 | c81
  · refine ⟨23, 6 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c80, c81]
  rcases lt_or_ge (t - ⌊t⌋) (1563733 / 6718788 : ℝ) with c82 | c82
  · refine ⟨8, 3 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c81, c82]
  rcases lt_or_ge (t - ⌊t⌋) (5592961 / 23889024 : ℝ) with c83 | c83
  · refine ⟨22, 8 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c82, c83]
  rcases lt_or_ge (t - ⌊t⌋) (6320881 / 26875152 : ℝ) with c84 | c84
  · refine ⟨32, 9 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c83, c84]
  rcases lt_or_ge (t - ⌊t⌋) (5825917 / 24635556 : ℝ) with c85 | c85
  · refine ⟨9, 8 + 33 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c84, c85]
  rcases lt_or_ge (t - ⌊t⌋) (5330053 / 22395960 : ℝ) with c86 | c86
  · refine ⟨29, 8 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c85, c86]
  rcases lt_or_ge (t - ⌊t⌋) (9615313 / 40312728 : ℝ) with c87 | c87
  · refine ⟨19, 13 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c86, c87]
  rcases lt_or_ge (t - ⌊t⌋) (10714717 / 44791920 : ℝ) with c88 | c88
  · refine ⟨2, 15 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c87, c88]
  rcases lt_or_ge (t - ⌊t⌋) (7529365 / 31354344 : ℝ) with c89 | c89
  · refine ⟨18, 11 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c88, c89]
  rcases lt_or_ge (t - ⌊t⌋) (3268225 / 13437576 : ℝ) with c90 | c90
  · refine ⟨17, 5 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c89, c90]
  rcases lt_or_ge (t - ⌊t⌋) (6364801 / 26128620 : ℝ) with c91 | c91
  · refine ⟨12, 9 + 35 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c90, c91]
  rcases lt_or_ge (t - ⌊t⌋) (12407149 / 50764176 : ℝ) with c92 | c92
  · refine ⟨0, 17 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c91, c92]
  rcases lt_or_ge (t - ⌊t⌋) (2775529 / 11197980 : ℝ) with c93 | c93
  · refine ⟨14, 4 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c92, c93]
  rcases lt_or_ge (t - ⌊t⌋) (8367733 / 33593940 : ℝ) with c94 | c94
  · refine ⟨31, 12 + 45 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c93, c94]
  rcases lt_or_ge (t - ⌊t⌋) (13429549 / 53750304 : ℝ) with c95 | c95
  · refine ⟨34, 18 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c94, c95]
  rcases lt_or_ge (t - ⌊t⌋) (5077441 / 20156364 : ℝ) with c96 | c96
  · refine ⟨26, 7 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c95, c96]
  rcases lt_or_ge (t - ⌊t⌋) (3048337 / 11944512 : ℝ) with c97 | c97
  · refine ⟨15, 5 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c96, c97]
  rcases lt_or_ge (t - ⌊t⌋) (11461249 / 44791920 : ℝ) with c98 | c98
  · refine ⟨2, 16 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c97, c98]
  rcases lt_or_ge (t - ⌊t⌋) (2678681 / 10451448 : ℝ) with c99 | c99
  · refine ⟨33, 18 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c98, c99]
  rcases lt_or_ge (t - ⌊t⌋) (10361845 / 40312728 : ℝ) with c100 | c100
  · refine ⟨19, 14 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c99, c100]
  rcases lt_or_ge (t - ⌊t⌋) (3678589 / 14184108 : ℝ) with c101 | c101
  · refine ⟨10, 5 + 19 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c100, c101]
  rcases lt_or_ge (t - ⌊t⌋) (5452453 / 20902896 : ℝ) with c102 | c102
  · refine ⟨25, 8 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c101, c102]
  rcases lt_or_ge (t - ⌊t⌋) (1983997 / 7465320 : ℝ) with c103 | c103
  · refine ⟨27, 3 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c102, c103]
  rcases lt_or_ge (t - ⌊t⌋) (6572449 / 24635556 : ℝ) with c104 | c104
  · refine ⟨9, 9 + 33 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c103, c104]
  rcases lt_or_ge (t - ⌊t⌋) (4812517 / 17916768 : ℝ) with c105 | c105
  · refine ⟨23, 7 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c104, c105]
  rcases lt_or_ge (t - ⌊t⌋) (4229641 / 15677172 : ℝ) with c106 | c106
  · refine ⟨20, 6 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c105, c106]
  rcases lt_or_ge (t - ⌊t⌋) (1215317 / 4479192 : ℝ) with c107 | c107
  · refine ⟨29, 9 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c106, c107]
  rcases lt_or_ge (t - ⌊t⌋) (7111333 / 26128620 : ℝ) with c108 | c108
  · refine ⟨12, 10 + 35 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c107, c108]
  rcases lt_or_ge (t - ⌊t⌋) (12207781 / 44791920 : ℝ) with c109 | c109
  · refine ⟨2, 17 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c108, c109]
  rcases lt_or_ge (t - ⌊t⌋) (855217 / 2986128 : ℝ) with c110 | c110
  · refine ⟨3, 2 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c109, c110]
  rcases lt_or_ge (t - ⌊t⌋) (2352313 / 8211852 : ℝ) with c111 | c111
  · refine ⟨28, 4 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c110, c111]
  rcases lt_or_ge (t - ⌊t⌋) (9022429 / 31354344 : ℝ) with c112 | c112
  · refine ⟨18, 13 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c111, c112]
  rcases lt_or_ge (t - ⌊t⌋) (5823973 / 20156364 : ℝ) with c113 | c113
  · refine ⟨26, 8 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c112, c113]
  rcases lt_or_ge (t - ⌊t⌋) (12954313 / 44791920 : ℝ) with c114 | c114
  · refine ⟨2, 18 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c113, c114]
  rcases lt_or_ge (t - ⌊t⌋) (7813945 / 26875152 : ℝ) with c115 | c115
  · refine ⟨32, 11 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c114, c115]
  rcases lt_or_ge (t - ⌊t⌋) (15669145 / 53750304 : ℝ) with c116 | c116
  · refine ⟨34, 21 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c115, c116]
  rcases lt_or_ge (t - ⌊t⌋) (10487449 / 35833536 : ℝ) with c117 | c117
  · refine ⟨24, 15 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c116, c117]
  rcases lt_or_ge (t - ⌊t⌋) (9860797 / 33593940 : ℝ) with c118 | c118
  · refine ⟨31, 14 + 45 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c117, c118]
  rcases lt_or_ge (t - ⌊t⌋) (11854909 / 40312728 : ℝ) with c119 | c119
  · refine ⟨19, 16 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c118, c119]
  rcases lt_or_ge (t - ⌊t⌋) (12315241 / 41805792 : ℝ) with c120 | c120
  · refine ⟨30, 17 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c119, c120]
  rcases lt_or_ge (t - ⌊t⌋) (6198985 / 20902896 : ℝ) with c121 | c121
  · refine ⟨25, 9 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c120, c121]
  rcases lt_or_ge (t - ⌊t⌋) (4014757 / 13437576 : ℝ) with c122 | c122
  · refine ⟨17, 6 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c121, c122]
  rcases lt_or_ge (t - ⌊t⌋) (2712745 / 8958384 : ℝ) with c123 | c123
  · refine ⟨11, 4 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c122, c123]
  rcases lt_or_ge (t - ⌊t⌋) (1839277 / 5972256 : ℝ) with c124 | c124
  · refine ⟨7, 3 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c123, c124]
  rcases lt_or_ge (t - ⌊t⌋) (5559049 / 17916768 : ℝ) with c125 | c125
  · refine ⟨23, 8 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c124, c125]
  rcases lt_or_ge (t - ⌊t⌋) (4425121 / 14184108 : ℝ) with c126 | c126
  · refine ⟨10, 6 + 19 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c125, c126]
  rcases lt_or_ge (t - ⌊t⌋) (3522061 / 11197980 : ℝ) with c127 | c127
  · refine ⟨14, 5 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c126, c127]
  rcases lt_or_ge (t - ⌊t⌋) (3794869 / 11944512 : ℝ) with c128 | c128
  · refine ⟨15, 6 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c127, c128]
  rcases lt_or_ge (t - ⌊t⌋) (8560477 / 26875152 : ℝ) with c129 | c129
  · refine ⟨32, 12 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c128, c129]
  rcases lt_or_ge (t - ⌊t⌋) (17162209 / 53750304 : ℝ) with c130 | c130
  · refine ⟨34, 23 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c129, c130]
  rcases lt_or_ge (t - ⌊t⌋) (1471573 / 4479192 : ℝ) with c131 | c131
  · refine ⟨5, 2 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c130, c131]
  rcases lt_or_ge (t - ⌊t⌋) (8604397 / 26128620 : ℝ) with c132 | c132
  · refine ⟨12, 12 + 35 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c131, c132]
  rcases lt_or_ge (t - ⌊t⌋) (1972615 / 5972256 : ℝ) with c133 | c133
  · refine ⟨30, 19 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c132, c133]
  rcases lt_or_ge (t - ⌊t⌋) (6945517 / 20902896 : ℝ) with c134 | c134
  · refine ⟨25, 10 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c133, c134]
  rcases lt_or_ge (t - ⌊t⌋) (1777753 / 5225724 : ℝ) with c135 | c135
  · refine ⟨21, 3 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c134, c135]
  rcases lt_or_ge (t - ⌊t⌋) (2310265 / 6718788 : ℝ) with c136 | c136
  · refine ⟨8, 4 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c135, c136]
  rcases lt_or_ge (t - ⌊t⌋) (1320481 / 3732660 : ℝ) with c137 | c137
  · refine ⟨4, 2 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c136, c137]
  rcases lt_or_ge (t - ⌊t⌋) (3721285 / 10451448 : ℝ) with c138 | c138
  · refine ⟨13, 5 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c137, c138]
  rcases lt_or_ge (t - ⌊t⌋) (801095 / 2239596 : ℝ) with c139 | c139
  · refine ⟨9, 12 + 33 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c138, c139]
  rcases lt_or_ge (t - ⌊t⌋) (8579089 / 23889024 : ℝ) with c140 | c140
  · refine ⟨22, 12 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c139, c140]
  rcases lt_or_ge (t - ⌊t⌋) (12100393 / 33593940 : ℝ) with c141 | c141
  · refine ⟨31, 17 + 45 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c140, c141]
  rcases lt_or_ge (t - ⌊t⌋) (19401805 / 53750304 : ℝ) with c142 | c142
  · refine ⟨34, 26 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c141, c142]
  rcases lt_or_ge (t - ⌊t⌋) (2730529 / 7465320 : ℝ) with c143 | c143
  · refine ⟨27, 4 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c142, c143]
  rcases lt_or_ge (t - ⌊t⌋) (15301369 / 41805792 : ℝ) with c144 | c144
  · refine ⟨30, 21 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c143, c144]
  rcases lt_or_ge (t - ⌊t⌋) (7692049 / 20902896 : ℝ) with c145 | c145
  · refine ⟨25, 11 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c144, c145]
  rcases lt_or_ge (t - ⌊t⌋) (14841037 / 40312728 : ℝ) with c146 | c146
  · refine ⟨19, 20 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c145, c146]
  rcases lt_or_ge (t - ⌊t⌋) (316225 / 746532 : ℝ) with c147 | c147
  · refine ⟨6, 1 + 1 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c146, c147]
  rcases lt_or_ge (t - ⌊t⌋) (4467817 / 10451448 : ℝ) with c148 | c148
  · refine ⟨13, 6 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c147, c148]
  rcases lt_or_ge (t - ⌊t⌋) (2585809 / 5972256 : ℝ) with c149 | c149
  · refine ⟨7, 4 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c148, c149]
  rcases lt_or_ge (t - ⌊t⌋) (7798645 / 17916768 : ℝ) with c150 | c150
  · refine ⟨23, 11 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c149, c150]
  rcases lt_or_ge (t - ⌊t⌋) (8810101 / 20156364 : ℝ) with c151 | c151
  · refine ⟨26, 12 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c150, c151]
  rcases lt_or_ge (t - ⌊t⌋) (1961849 / 4479192 : ℝ) with c152 | c152
  · refine ⟨29, 14 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c151, c152]
  rcases lt_or_ge (t - ⌊t⌋) (1312159 / 2986128 : ℝ) with c153 | c153
  · refine ⟨25, 13 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c152, c153]
  rcases lt_or_ge (t - ⌊t⌋) (5287933 / 11944512 : ℝ) with c154 | c154
  · refine ⟨15, 8 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c153, c154]
  rcases lt_or_ge (t - ⌊t⌋) (2318105 / 5225724 : ℝ) with c155 | c155
  · refine ⟨12, 16 + 35 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c154, c155]
  rcases lt_or_ge (t - ⌊t⌋) (23880997 / 53750304 : ℝ) with c156 | c156
  · refine ⟨34, 32 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c155, c156]
  rcases lt_or_ge (t - ⌊t⌋) (1003025 / 2239596 : ℝ) with c157 | c157
  · refine ⟨14, 7 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c156, c157]
  rcases lt_or_ge (t - ⌊t⌋) (15086521 / 33593940 : ℝ) with c158 | c158
  · refine ⟨31, 21 + 45 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c157, c158]
  rcases lt_or_ge (t - ⌊t⌋) (3056797 / 6718788 : ℝ) with c159 | c159
  · refine ⟨8, 5 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c158, c159]
  rcases lt_or_ge (t - ⌊t⌋) (20419633 / 44791920 : ℝ) with c160 | c160
  · refine ⟨2, 28 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c159, c160]
  rcases lt_or_ge (t - ⌊t⌋) (12293137 / 26875152 : ℝ) with c161 | c161
  · refine ⟨32, 17 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c160, c161]
  rcases lt_or_ge (t - ⌊t⌋) (24627529 / 53750304 : ℝ) with c162 | c162
  · refine ⟨34, 33 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c161, c162]
  rcases lt_or_ge (t - ⌊t⌋) (7215769 / 15677172 : ℝ) with c163 | c163
  · refine ⟨20, 10 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c162, c163]
  rcases lt_or_ge (t - ⌊t⌋) (3477061 / 7465320 : ℝ) with c164 | c164
  · refine ⟨27, 5 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c163, c164]
  rcases lt_or_ge (t - ⌊t⌋) (4205809 / 8958384 : ℝ) with c165 | c165
  · refine ⟨11, 6 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c164, c165]
  rcases lt_or_ge (t - ⌊t⌋) (10555777 / 22395960 : ℝ) with c166 | c166
  · refine ⟨29, 15 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c165, c166]
  rcases lt_or_ge (t - ⌊t⌋) (12337057 / 26128620 : ℝ) with c167 | c167
  · refine ⟨12, 17 + 35 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c166, c167]
  rcases lt_or_ge (t - ⌊t⌋) (9556633 / 20156364 : ℝ) with c168 | c168
  · refine ⟨26, 13 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c167, c168]
  rcases lt_or_ge (t - ⌊t⌋) (9931645 / 20902896 : ℝ) with c169 | c169
  · refine ⟨25, 14 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c168, c169]
  rcases lt_or_ge (t - ⌊t⌋) (2524285 / 5225724 : ℝ) with c170 | c170
  · refine ⟨21, 4 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c169, c170]
  rcases lt_or_ge (t - ⌊t⌋) (11565217 / 23889024 : ℝ) with c171 | c171
  · refine ⟨22, 16 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c170, c171]
  rcases lt_or_ge (t - ⌊t⌋) (13039669 / 26875152 : ℝ) with c172 | c172
  · refine ⟨32, 18 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c171, c172]
  rcases lt_or_ge (t - ⌊t⌋) (26120593 / 53750304 : ℝ) with c173 | c173
  · refine ⟨34, 35 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c172, c173]
  rcases lt_or_ge (t - ⌊t⌋) (2218105 / 4479192 : ℝ) with c174 | c174
  · refine ⟨5, 3 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c173, c174]
  rcases lt_or_ge (t - ⌊t⌋) (744907 / 1493064 : ℝ) with c175 | c175
  · refine ⟨13, 7 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c174, c175]
  rcases lt_or_ge (t - ⌊t⌋) (26084449 / 52257240 : ℝ) with c176 | c176
  · refine ⟨33, 35 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c175, c176]
  rcases lt_or_ge (t - ⌊t⌋) (13083589 / 26128620 : ℝ) with c177 | c177
  · refine ⟨12, 18 + 35 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c176, c177]
  rcases lt_or_ge (t - ⌊t⌋) (15741217 / 31354344 : ℝ) with c178 | c178
  · refine ⟨18, 22 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c177, c178]
  rcases lt_or_ge (t - ⌊t⌋) (6034465 / 11944512 : ℝ) with c179 | c179
  · refine ⟨15, 9 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c178, c179]
  rcases lt_or_ge (t - ⌊t⌋) (22659229 / 44791920 : ℝ) with c180 | c180
  · refine ⟨2, 31 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c179, c180]
  rcases lt_or_ge (t - ⌊t⌋) (7962301 / 15677172 : ℝ) with c181 | c181
  · refine ⟨20, 11 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c180, c181]
  rcases lt_or_ge (t - ⌊t⌋) (12544705 / 24635556 : ℝ) with c182 | c182
  · refine ⟨9, 17 + 33 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c181, c182]
  rcases lt_or_ge (t - ⌊t⌋) (10303165 / 20156364 : ℝ) with c183 | c183
  · refine ⟨26, 14 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c182, c183]
  rcases lt_or_ge (t - ⌊t⌋) (5761657 / 11197980 : ℝ) with c184 | c184
  · refine ⟨14, 8 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c183, c184]
  rcases lt_or_ge (t - ⌊t⌋) (17326117 / 33593940 : ℝ) with c185 | c185
  · refine ⟨31, 24 + 45 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c184, c185]
  rcases lt_or_ge (t - ⌊t⌋) (20813293 / 40312728 : ℝ) with c186 | c186
  · refine ⟨19, 28 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c185, c186]
  rcases lt_or_ge (t - ⌊t⌋) (9291709 / 17916768 : ℝ) with c187 | c187
  · refine ⟨23, 13 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c186, c187]
  rcases lt_or_ge (t - ⌊t⌋) (7000885 / 13437576 : ℝ) with c188 | c188
  · refine ⟨17, 10 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c187, c188]
  rcases lt_or_ge (t - ⌊t⌋) (7411249 / 14184108 : ℝ) with c189 | c189
  · refine ⟨10, 10 + 19 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c188, c189]
  rcases lt_or_ge (t - ⌊t⌋) (23405761 / 44791920 : ℝ) with c190 | c190
  · refine ⟨2, 32 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c189, c190]
  rcases lt_or_ge (t - ⌊t⌋) (1601749 / 2986128 : ℝ) with c191 | c191
  · refine ⟨3, 3 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c190, c191]
  rcases lt_or_ge (t - ⌊t⌋) (13625 / 25164 : ℝ) with c192 | c192
  · refine ⟨16, 2 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c191, c192]
  rcases lt_or_ge (t - ⌊t⌋) (5664809 / 10451448 : ℝ) with c193 | c193
  · refine ⟨33, 38 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c192, c193]
  rcases lt_or_ge (t - ⌊t⌋) (19445833 / 35833536 : ℝ) with c194 | c194
  · refine ⟨24, 27 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c193, c194]
  rcases lt_or_ge (t - ⌊t⌋) (2067013 / 3732660 : ℝ) with c195 | c195
  · refine ⟨4, 3 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c194, c195]
  rcases lt_or_ge (t - ⌊t⌋) (3332341 / 5972256 : ℝ) with c196 | c196
  · refine ⟨7, 5 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c195, c196]
  rcases lt_or_ge (t - ⌊t⌋) (10038241 / 17916768 : ℝ) with c197 | c197
  · refine ⟨23, 14 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c196, c197]
  rcases lt_or_ge (t - ⌊t⌋) (3803329 / 6718788 : ℝ) with c198 | c198
  · refine ⟨8, 6 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c197, c198]
  rcases lt_or_ge (t - ⌊t⌋) (6780997 / 11944512 : ℝ) with c199 | c199
  · refine ⟨15, 10 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c198, c199]
  rcases lt_or_ge (t - ⌊t⌋) (5960881 / 10451448 : ℝ) with c200 | c200
  · refine ⟨13, 8 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c199, c200]
  rcases lt_or_ge (t - ⌊t⌋) (12795373 / 22395960 : ℝ) with c201 | c201
  · refine ⟨29, 18 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c200, c201]
  rcases lt_or_ge (t - ⌊t⌋) (23052889 / 40312728 : ℝ) with c202 | c202
  · refine ⟨19, 31 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c201, c202]
  rcases lt_or_ge (t - ⌊t⌋) (25645357 / 44791920 : ℝ) with c203 | c203
  · refine ⟨2, 35 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c202, c203]
  rcases lt_or_ge (t - ⌊t⌋) (8157781 / 14184108 : ℝ) with c204 | c204
  · refine ⟨10, 11 + 19 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c203, c204]
  rcases lt_or_ge (t - ⌊t⌋) (7747417 / 13437576 : ℝ) with c205 | c205
  · refine ⟨17, 11 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c204, c205]
  rcases lt_or_ge (t - ⌊t⌋) (13804813 / 23889024 : ℝ) with c206 | c206
  · refine ⟨22, 19 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c205, c206]
  rcases lt_or_ge (t - ⌊t⌋) (6508189 / 11197980 : ℝ) with c207 | c207
  · refine ⟨14, 9 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c206, c207]
  rcases lt_or_ge (t - ⌊t⌋) (19565713 / 33593940 : ℝ) with c208 | c208
  · refine ⟨31, 27 + 45 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c207, c208]
  rcases lt_or_ge (t - ⌊t⌋) (31346317 / 53750304 : ℝ) with c209 | c209
  · refine ⟨34, 42 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c208, c209]
  rcases lt_or_ge (t - ⌊t⌋) (11796229 / 20156364 : ℝ) with c210 | c210
  · refine ⟨26, 16 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c209, c210]
  rcases lt_or_ge (t - ⌊t⌋) (914797 / 1493064 : ℝ) with c211 | c211
  · refine ⟨1, 2 + 2 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c210, c211]
  rcases lt_or_ge (t - ⌊t⌋) (6411341 / 10451448 : ℝ) with c212 | c212
  · refine ⟨33, 43 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c211, c212]
  rcases lt_or_ge (t - ⌊t⌋) (16069717 / 26128620 : ℝ) with c213 | c213
  · refine ⟨12, 22 + 35 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c212, c213]
  rcases lt_or_ge (t - ⌊t⌋) (25752817 / 41805792 : ℝ) with c214 | c214
  · refine ⟨30, 35 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c213, c214]
  rcases lt_or_ge (t - ⌊t⌋) (12917773 / 20902896 : ℝ) with c215 | c215
  · refine ⟨25, 18 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c214, c215]
  rcases lt_or_ge (t - ⌊t⌋) (3270817 / 5225724 : ℝ) with c216 | c216
  · refine ⟨21, 5 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c215, c216]
  rcases lt_or_ge (t - ⌊t⌋) (8904313 / 14184108 : ℝ) with c217 | c217
  · refine ⟨10, 12 + 19 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c216, c217]
  rcases lt_or_ge (t - ⌊t⌋) (7527529 / 11944512 : ℝ) with c218 | c218
  · refine ⟨15, 11 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c217, c218]
  rcases lt_or_ge (t - ⌊t⌋) (8493949 / 13437576 : ℝ) with c219 | c219
  · refine ⟨17, 12 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c218, c219]
  rcases lt_or_ge (t - ⌊t⌋) (5698873 / 8958384 : ℝ) with c220 | c220
  · refine ⟨11, 8 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c219, c220]
  rcases lt_or_ge (t - ⌊t⌋) (14288437 / 22395960 : ℝ) with c221 | c221
  · refine ⟨29, 20 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c220, c221]
  rcases lt_or_ge (t - ⌊t⌋) (6707413 / 10451448 : ℝ) with c222 | c222
  · refine ⟨13, 9 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c221, c222]
  rcases lt_or_ge (t - ⌊t⌋) (11531305 / 17916768 : ℝ) with c223 | c223
  · refine ⟨23, 16 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c222, c223]
  rcases lt_or_ge (t - ⌊t⌋) (20220409 / 31354344 : ℝ) with c224 | c224
  · refine ⟨18, 28 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c223, c224]
  rcases lt_or_ge (t - ⌊t⌋) (7254721 / 11197980 : ℝ) with c225 | c225
  · refine ⟨14, 10 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c224, c225]
  rcases lt_or_ge (t - ⌊t⌋) (5338441 / 8211852 : ℝ) with c226 | c226
  · refine ⟨28, 8 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c225, c226]
  rcases lt_or_ge (t - ⌊t⌋) (10201897 / 15677172 : ℝ) with c227 | c227
  · refine ⟨20, 14 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c226, c227]
  rcases lt_or_ge (t - ⌊t⌋) (17518861 / 26875152 : ℝ) with c228 | c228
  · refine ⟨32, 24 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c227, c228]
  rcases lt_or_ge (t - ⌊t⌋) (13664305 / 20902896 : ℝ) with c229 | c229
  · refine ⟨25, 19 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c228, c229]
  rcases lt_or_ge (t - ⌊t⌋) (2964637 / 4479192 : ℝ) with c230 | c230
  · refine ⟨5, 4 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c229, c230]
  rcases lt_or_ge (t - ⌊t⌋) (994025 / 1493064 : ℝ) with c231 | c231
  · refine ⟨27, 7 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c230, c231]
  rcases lt_or_ge (t - ⌊t⌋) (35825509 / 53750304 : ℝ) with c232 | c232
  · refine ⟨34, 48 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c231, c232]
  rcases lt_or_ge (t - ⌊t⌋) (23925025 / 35833536 : ℝ) with c233 | c233
  · refine ⟨24, 33 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c232, c233]
  rcases lt_or_ge (t - ⌊t⌋) (20966941 / 31354344 : ℝ) with c234 | c234
  · refine ⟨18, 29 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c233, c234]
  rcases lt_or_ge (t - ⌊t⌋) (27992413 / 41805792 : ℝ) with c235 | c235
  · refine ⟨30, 38 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c234, c235]
  rcases lt_or_ge (t - ⌊t⌋) (15034969 / 22395960 : ℝ) with c236 | c236
  · refine ⟨29, 21 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c235, c236]
  rcases lt_or_ge (t - ⌊t⌋) (4549861 / 6718788 : ℝ) with c237 | c237
  · refine ⟨8, 7 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c236, c237]
  rcases lt_or_ge (t - ⌊t⌋) (4078873 / 5972256 : ℝ) with c238 | c238
  · refine ⟨7, 6 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c237, c238]
  rcases lt_or_ge (t - ⌊t⌋) (12277837 / 17916768 : ℝ) with c239 | c239
  · refine ⟨23, 17 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c238, c239]
  rcases lt_or_ge (t - ⌊t⌋) (9240481 / 13437576 : ℝ) with c240 | c240
  · refine ⟨17, 13 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c239, c240]
  rcases lt_or_ge (t - ⌊t⌋) (2058691 / 2986128 : ℝ) with c241 | c241
  · refine ⟨25, 20 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c240, c241]
  rcases lt_or_ge (t - ⌊t⌋) (8274061 / 11944512 : ℝ) with c242 | c242
  · refine ⟨15, 12 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c241, c242]
  rcases lt_or_ge (t - ⌊t⌋) (23298373 / 33593940 : ℝ) with c243 | c243
  · refine ⟨31, 32 + 45 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c242, c243]
  rcases lt_or_ge (t - ⌊t⌋) (37318573 / 53750304 : ℝ) with c244 | c244
  · refine ⟨34, 50 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c243, c244]
  rcases lt_or_ge (t - ⌊t⌋) (14035825 / 20156364 : ℝ) with c245 | c245
  · refine ⟨26, 19 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c244, c245]
  rcases lt_or_ge (t - ⌊t⌋) (10948429 / 15677172 : ℝ) with c246 | c246
  · refine ⟨20, 15 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c245, c246]
  rcases lt_or_ge (t - ⌊t⌋) (36535897 / 52257240 : ℝ) with c247 | c247
  · refine ⟨33, 49 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c246, c247]
  rcases lt_or_ge (t - ⌊t⌋) (18309313 / 26128620 : ℝ) with c248 | c248
  · refine ⟨12, 25 + 35 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c247, c248]
  rcases lt_or_ge (t - ⌊t⌋) (28278613 / 40312728 : ℝ) with c249 | c249
  · refine ⟨19, 38 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c248, c249]
  rcases lt_or_ge (t - ⌊t⌋) (16790941 / 23889024 : ℝ) with c250 | c250
  · refine ⟨22, 23 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c249, c250]
  rcases lt_or_ge (t - ⌊t⌋) (15781501 / 22395960 : ℝ) with c251 | c251
  · refine ⟨29, 22 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c250, c251]
  rcases lt_or_ge (t - ⌊t⌋) (4212211 / 5972256 : ℝ) with c252 | c252
  · refine ⟨30, 40 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c251, c252]
  rcases lt_or_ge (t - ⌊t⌋) (31617613 / 44791920 : ℝ) with c253 | c253
  · refine ⟨2, 43 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c252, c253]
  rcases lt_or_ge (t - ⌊t⌋) (19011925 / 26875152 : ℝ) with c254 | c254
  · refine ⟨32, 26 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c253, c254]
  rcases lt_or_ge (t - ⌊t⌋) (38065105 / 53750304 : ℝ) with c255 | c255
  · refine ⟨34, 51 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c254, c255]
  rcases lt_or_ge (t - ⌊t⌋) (25418089 / 35833536 : ℝ) with c256 | c256
  · refine ⟨24, 35 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c255, c256]
  rcases lt_or_ge (t - ⌊t⌋) (7453945 / 10451448 : ℝ) with c257 | c257
  · refine ⟨13, 10 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c256, c257]
  rcases lt_or_ge (t - ⌊t⌋) (8001253 / 11197980 : ℝ) with c258 | c258
  · refine ⟨14, 11 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c257, c258]
  rcases lt_or_ge (t - ⌊t⌋) (4808981 / 6718788 : ℝ) with c259 | c259
  · refine ⟨31, 33 + 45 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c258, c259]
  rcases lt_or_ge (t - ⌊t⌋) (6445405 / 8958384 : ℝ) with c260 | c260
  · refine ⟨11, 9 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c259, c260]
  rcases lt_or_ge (t - ⌊t⌋) (29025145 / 40312728 : ℝ) with c261 | c261
  · refine ⟨19, 39 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c260, c261]
  rcases lt_or_ge (t - ⌊t⌋) (17770429 / 24635556 : ℝ) with c262 | c262
  · refine ⟨9, 24 + 33 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c261, c262]
  rcases lt_or_ge (t - ⌊t⌋) (38811637 / 53750304 : ℝ) with c263 | c263
  · refine ⟨34, 52 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c262, c263]
  rcases lt_or_ge (t - ⌊t⌋) (6472829 / 8958384 : ℝ) with c264 | c264
  · refine ⟨2, 44 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c263, c264]
  rcases lt_or_ge (t - ⌊t⌋) (30232009 / 41805792 : ℝ) with c265 | c265
  · refine ⟨30, 41 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c264, c265]
  rcases lt_or_ge (t - ⌊t⌋) (15157369 / 20902896 : ℝ) with c266 | c266
  · refine ⟨25, 21 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c265, c266]
  rcases lt_or_ge (t - ⌊t⌋) (13024369 / 17916768 : ℝ) with c267 | c267
  · refine ⟨23, 18 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c266, c267]
  rcases lt_or_ge (t - ⌊t⌋) (38028961 / 52257240 : ℝ) with c268 | c268
  · refine ⟨33, 51 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c267, c268]
  rcases lt_or_ge (t - ⌊t⌋) (3811169 / 5225724 : ℝ) with c269 | c269
  · refine ⟨12, 26 + 35 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c268, c269]
  rcases lt_or_ge (t - ⌊t⌋) (26164621 / 35833536 : ℝ) with c270 | c270
  · refine ⟨24, 36 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c269, c270]
  rcases lt_or_ge (t - ⌊t⌋) (10397377 / 14184108 : ℝ) with c271 | c271
  · refine ⟨10, 14 + 19 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c270, c271]
  rcases lt_or_ge (t - ⌊t⌋) (17537473 / 23889024 : ℝ) with c272 | c272
  · refine ⟨22, 24 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c271, c272]
  rcases lt_or_ge (t - ⌊t⌋) (19758457 / 26875152 : ℝ) with c273 | c273
  · refine ⟨32, 27 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c272, c273]
  rcases lt_or_ge (t - ⌊t⌋) (39558169 / 53750304 : ℝ) with c274 | c274
  · refine ⟨34, 53 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c273, c274]
  rcases lt_or_ge (t - ⌊t⌋) (6084973 / 8211852 : ℝ) with c275 | c275
  · refine ⟨28, 9 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c274, c275]
  rcases lt_or_ge (t - ⌊t⌋) (9987013 / 13437576 : ℝ) with c276 | c276
  · refine ⟨17, 14 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c275, c276]
  rcases lt_or_ge (t - ⌊t⌋) (562709 / 746532 : ℝ) with c277 | c277
  · refine ⟨4, 4 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c276, c277]
  rcases lt_or_ge (t - ⌊t⌋) (9020593 / 11944512 : ℝ) with c278 | c278
  · refine ⟨15, 13 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c277, c278]
  rcases lt_or_ge (t - ⌊t⌋) (33857209 / 44791920 : ℝ) with c279 | c279
  · refine ⟨2, 46 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c278, c279]
  rcases lt_or_ge (t - ⌊t⌋) (7904405 / 10451448 : ℝ) with c280 | c280
  · refine ⟨33, 53 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c279, c280]
  rcases lt_or_ge (t - ⌊t⌋) (2828911 / 3732660 : ℝ) with c281 | c281
  · refine ⟨12, 27 + 35 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c280, c281]
  rcases lt_or_ge (t - ⌊t⌋) (31725073 / 41805792 : ℝ) with c282 | c282
  · refine ⟨30, 43 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c281, c282]
  rcases lt_or_ge (t - ⌊t⌋) (15903901 / 20902896 : ℝ) with c283 | c283
  · refine ⟨25, 22 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c282, c283]
  rcases lt_or_ge (t - ⌊t⌋) (573907 / 746532 : ℝ) with c284 | c284
  · refine ⟨21, 6 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c283, c284]
  rcases lt_or_ge (t - ⌊t⌋) (15528889 / 20156364 : ℝ) with c285 | c285
  · refine ⟨26, 21 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c284, c285]
  rcases lt_or_ge (t - ⌊t⌋) (3454913 / 4479192 : ℝ) with c286 | c286
  · refine ⟨29, 24 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c285, c286]
  rcases lt_or_ge (t - ⌊t⌋) (27657685 / 35833536 : ℝ) with c287 | c287
  · refine ⟨24, 38 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c286, c287]
  rcases lt_or_ge (t - ⌊t⌋) (34603741 / 44791920 : ℝ) with c288 | c288
  · refine ⟨2, 47 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c287, c288]
  rcases lt_or_ge (t - ⌊t⌋) (2348281 / 2986128 : ℝ) with c289 | c289
  · refine ⟨3, 4 + 4 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c288, c289]
  rcases lt_or_ge (t - ⌊t⌋) (5296393 / 6718788 : ℝ) with c290 | c290
  · refine ⟨8, 8 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c289, c290]
  rcases lt_or_ge (t - ⌊t⌋) (35350273 / 44791920 : ℝ) with c291 | c291
  · refine ⟨2, 48 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c290, c291]
  rcases lt_or_ge (t - ⌊t⌋) (21251521 / 26875152 : ℝ) with c292 | c292
  · refine ⟨32, 29 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c291, c292]
  rcases lt_or_ge (t - ⌊t⌋) (42544297 / 53750304 : ℝ) with c293 | c293
  · refine ⟨34, 57 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c292, c293]
  rcases lt_or_ge (t - ⌊t⌋) (12441493 / 15677172 : ℝ) with c294 | c294
  · refine ⟨20, 17 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c293, c294]
  rcases lt_or_ge (t - ⌊t⌋) (33218137 / 41805792 : ℝ) with c295 | c295
  · refine ⟨30, 45 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c294, c295]
  rcases lt_or_ge (t - ⌊t⌋) (16650433 / 20902896 : ℝ) with c296 | c296
  · refine ⟨25, 23 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c295, c296]
  rcases lt_or_ge (t - ⌊t⌋) (10733545 / 13437576 : ℝ) with c297 | c297
  · refine ⟨17, 15 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c296, c297]
  rcases lt_or_ge (t - ⌊t⌋) (7191937 / 8958384 : ℝ) with c298 | c298
  · refine ⟨11, 10 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c297, c298]
  rcases lt_or_ge (t - ⌊t⌋) (4825405 / 5972256 : ℝ) with c299 | c299
  · refine ⟨7, 7 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c298, c299]
  rcases lt_or_ge (t - ⌊t⌋) (14517433 / 17916768 : ℝ) with c300 | c300
  · refine ⟨23, 20 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c299, c300]
  rcases lt_or_ge (t - ⌊t⌋) (25446133 / 31354344 : ℝ) with c301 | c301
  · refine ⟨18, 35 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c300, c301]
  rcases lt_or_ge (t - ⌊t⌋) (32757805 / 40312728 : ℝ) with c302 | c302
  · refine ⟨19, 44 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c301, c302]
  rcases lt_or_ge (t - ⌊t⌋) (29150749 / 35833536 : ℝ) with c303 | c303
  · refine ⟨24, 40 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c302, c303]
  rcases lt_or_ge (t - ⌊t⌋) (21295441 / 26128620 : ℝ) with c304 | c304
  · refine ⟨12, 29 + 35 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c303, c304]
  rcases lt_or_ge (t - ⌊t⌋) (9767125 / 11944512 : ℝ) with c305 | c305
  · refine ⟨15, 14 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c304, c305]
  rcases lt_or_ge (t - ⌊t⌋) (21998053 / 26875152 : ℝ) with c306 | c306
  · refine ⟨32, 30 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c305, c306]
  rcases lt_or_ge (t - ⌊t⌋) (44037361 / 53750304 : ℝ) with c307 | c307
  · refine ⟨34, 59 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c306, c307]
  rcases lt_or_ge (t - ⌊t⌋) (3711169 / 4479192 : ℝ) with c308 | c308
  · refine ⟨5, 5 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c307, c308]
  rcases lt_or_ge (t - ⌊t⌋) (6831505 / 8211852 : ℝ) with c309 | c309
  · refine ⟨28, 10 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c308, c309]
  rcases lt_or_ge (t - ⌊t⌋) (42268429 / 50764176 : ℝ) with c310 | c310
  · refine ⟨0, 57 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c309, c310]
  rcases lt_or_ge (t - ⌊t⌋) (44783893 / 53750304 : ℝ) with c311 | c311
  · refine ⟨34, 60 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c310, c311]
  rcases lt_or_ge (t - ⌊t⌋) (29897281 / 35833536 : ℝ) with c312 | c312
  · refine ⟨24, 41 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c311, c312]
  rcases lt_or_ge (t - ⌊t⌋) (26192665 / 31354344 : ℝ) with c313 | c313
  · refine ⟨18, 36 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c312, c313]
  rcases lt_or_ge (t - ⌊t⌋) (11890441 / 14184108 : ℝ) with c314 | c314
  · refine ⟨10, 16 + 19 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c313, c314]
  rcases lt_or_ge (t - ⌊t⌋) (37589869 / 44791920 : ℝ) with c315 | c315
  · refine ⟨2, 51 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c314, c315]
  rcases lt_or_ge (t - ⌊t⌋) (13188025 / 15677172 : ℝ) with c316 | c316
  · refine ⟨20, 18 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c315, c316]
  rcases lt_or_ge (t - ⌊t⌋) (20756557 / 24635556 : ℝ) with c317 | c317
  · refine ⟨9, 28 + 33 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c316, c317]
  rcases lt_or_ge (t - ⌊t⌋) (17021953 / 20156364 : ℝ) with c318 | c318
  · refine ⟨26, 23 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c317, c318]
  rcases lt_or_ge (t - ⌊t⌋) (9494317 / 11197980 : ℝ) with c319 | c319
  · refine ⟨14, 13 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c318, c319]
  rcases lt_or_ge (t - ⌊t⌋) (28524097 / 33593940 : ℝ) with c320 | c320
  · refine ⟨31, 39 + 45 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c319, c320]
  rcases lt_or_ge (t - ⌊t⌋) (34250869 / 40312728 : ℝ) with c321 | c321
  · refine ⟨19, 46 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c320, c321]
  rcases lt_or_ge (t - ⌊t⌋) (15263965 / 17916768 : ℝ) with c322 | c322
  · refine ⟨23, 21 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c321, c322]
  rcases lt_or_ge (t - ⌊t⌋) (11480077 / 13437576 : ℝ) with c323 | c323
  · refine ⟨17, 16 + 18 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c322, c323]
  rcases lt_or_ge (t - ⌊t⌋) (8947009 / 10451448 : ℝ) with c324 | c324
  · refine ⟨13, 12 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c323, c324]
  rcases lt_or_ge (t - ⌊t⌋) (44747749 / 52257240 : ℝ) with c325 | c325
  · refine ⟨33, 60 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c324, c325]
  rcases lt_or_ge (t - ⌊t⌋) (22013 / 25164 : ℝ) with c326 | c326
  · refine ⟨16, 3 + 3 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c325, c326]
  rcases lt_or_ge (t - ⌊t⌋) (47023489 / 53750304 : ℝ) with c327 | c327
  · refine ⟨34, 63 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c326, c327]
  rcases lt_or_ge (t - ⌊t⌋) (31390345 / 35833536 : ℝ) with c328 | c328
  · refine ⟨24, 43 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c327, c328]
  rcases lt_or_ge (t - ⌊t⌋) (44508025 / 50764176 : ℝ) with c329 | c329
  · refine ⟨0, 60 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c328, c329]
  rcases lt_or_ge (t - ⌊t⌋) (10513657 / 11944512 : ℝ) with c330 | c330
  · refine ⟨15, 15 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c329, c330]
  rcases lt_or_ge (t - ⌊t⌋) (17768485 / 20156364 : ℝ) with c331 | c331
  · refine ⟨26, 24 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c330, c331]
  rcases lt_or_ge (t - ⌊t⌋) (7938469 / 8958384 : ℝ) with c332 | c332
  · refine ⟨11, 11 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c331, c332]
  rcases lt_or_ge (t - ⌊t⌋) (35743933 / 40312728 : ℝ) with c333 | c333
  · refine ⟨19, 48 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c332, c333]
  rcases lt_or_ge (t - ⌊t⌋) (1990651 / 2239596 : ℝ) with c334 | c334
  · refine ⟨20, 19 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c333, c334]
  rcases lt_or_ge (t - ⌊t⌋) (12636973 / 14184108 : ℝ) with c335 | c335
  · refine ⟨10, 17 + 19 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c334, c335]
  rcases lt_or_ge (t - ⌊t⌋) (45254557 / 50764176 : ℝ) with c336 | c336
  · refine ⟨0, 61 + 68 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c335, c336]
  rcases lt_or_ge (t - ⌊t⌋) (16010497 / 17916768 : ℝ) with c337 | c337
  · refine ⟨23, 22 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c336, c337]
  rcases lt_or_ge (t - ⌊t⌋) (6042925 / 6718788 : ℝ) with c338 | c338
  · refine ⟨8, 9 + 9 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c337, c338]
  rcases lt_or_ge (t - ⌊t⌋) (23535037 / 26128620 : ℝ) with c339 | c339
  · refine ⟨12, 32 + 35 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c338, c339]
  rcases lt_or_ge (t - ⌊t⌋) (24237649 / 26875152 : ℝ) with c340 | c340
  · refine ⟨32, 33 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c339, c340]
  rcases lt_or_ge (t - ⌊t⌋) (18890029 / 20902896 : ℝ) with c341 | c341
  · refine ⟨25, 26 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c340, c341]
  rcases lt_or_ge (t - ⌊t⌋) (4763881 / 5225724 : ℝ) with c342 | c342
  · refine ⟨21, 7 + 7 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c341, c342]
  rcases lt_or_ge (t - ⌊t⌋) (10240849 / 11197980 : ℝ) with c343 | c343
  · refine ⟨14, 14 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c342, c343]
  rcases lt_or_ge (t - ⌊t⌋) (30763693 / 33593940 : ℝ) with c344 | c344
  · refine ⟨31, 42 + 45 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c343, c344]
  rcases lt_or_ge (t - ⌊t⌋) (49263085 / 53750304 : ℝ) with c345 | c345
  · refine ⟨34, 66 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c344, c345]
  rcases lt_or_ge (t - ⌊t⌋) (18515017 / 20156364 : ℝ) with c346 | c346
  · refine ⟨26, 25 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c345, c346]
  rcases lt_or_ge (t - ⌊t⌋) (7578037 / 8211852 : ℝ) with c347 | c347
  · refine ⟨28, 11 + 11 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c346, c347]
  rcases lt_or_ge (t - ⌊t⌋) (37236997 / 40312728 : ℝ) with c348 | c348
  · refine ⟨19, 50 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c347, c348]
  rcases lt_or_ge (t - ⌊t⌋) (9693541 / 10451448 : ℝ) with c349 | c349
  · refine ⟨13, 13 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c348, c349]
  rcases lt_or_ge (t - ⌊t⌋) (5571937 / 5972256 : ℝ) with c350 | c350
  · refine ⟨7, 8 + 8 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c349, c350]
  rcases lt_or_ge (t - ⌊t⌋) (16757029 / 17916768 : ℝ) with c351 | c351
  · refine ⟨23, 23 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c350, c351]
  rcases lt_or_ge (t - ⌊t⌋) (14681089 / 15677172 : ℝ) with c352 | c352
  · refine ⟨20, 20 + 21 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c351, c352]
  rcases lt_or_ge (t - ⌊t⌋) (4201445 / 4479192 : ℝ) with c353 | c353
  · refine ⟨29, 29 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c352, c353]
  rcases lt_or_ge (t - ⌊t⌋) (2805223 / 2986128 : ℝ) with c354 | c354
  · refine ⟨25, 27 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c353, c354]
  rcases lt_or_ge (t - ⌊t⌋) (11260189 / 11944512 : ℝ) with c355 | c355
  · refine ⟨15, 16 + 16 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c354, c355]
  rcases lt_or_ge (t - ⌊t⌋) (3560077 / 3732660 : ℝ) with c356 | c356
  · refine ⟨4, 5 + 5 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c355, c356]
  rcases lt_or_ge (t - ⌊t⌋) (19261549 / 20156364 : ℝ) with c357 | c357
  · refine ⟨26, 26 + 27 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c356, c357]
  rcases lt_or_ge (t - ⌊t⌋) (49973473 / 52257240 : ℝ) with c358 | c358
  · refine ⟨33, 67 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c357, c358]
  rcases lt_or_ge (t - ⌊t⌋) (3575443 / 3732660 : ℝ) with c359 | c359
  · refine ⟨12, 34 + 35 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c358, c359]
  rcases lt_or_ge (t - ⌊t⌋) (51502681 / 53750304 : ℝ) with c360 | c360
  · refine ⟨34, 69 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c359, c360]
  rcases lt_or_ge (t - ⌊t⌋) (34376473 / 35833536 : ℝ) with c361 | c361
  · refine ⟨24, 47 + 48 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c360, c361]
  rcases lt_or_ge (t - ⌊t⌋) (32256757 / 33593940 : ℝ) with c362 | c362
  · refine ⟨31, 44 + 45 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c361, c362]
  rcases lt_or_ge (t - ⌊t⌋) (38730061 / 40312728 : ℝ) with c363 | c363
  · refine ⟨19, 52 + 54 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c362, c363]
  rcases lt_or_ge (t - ⌊t⌋) (7209721 / 7465320 : ℝ) with c364 | c364
  · refine ⟨27, 10 + 10 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c363, c364]
  rcases lt_or_ge (t - ⌊t⌋) (8685001 / 8958384 : ℝ) with c365 | c365
  · refine ⟨11, 12 + 12 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c364, c365]
  rcases lt_or_ge (t - ⌊t⌋) (21753757 / 22395960 : ℝ) with c366 | c366
  · refine ⟨29, 30 + 30 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c365, c366]
  rcases lt_or_ge (t - ⌊t⌋) (52249213 / 53750304 : ℝ) with c367 | c367
  · refine ⟨34, 70 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c366, c367]
  rcases lt_or_ge (t - ⌊t⌋) (8712425 / 8958384 : ℝ) with c368 | c368
  · refine ⟨2, 59 + 60 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c367, c368]
  rcases lt_or_ge (t - ⌊t⌋) (40683457 / 41805792 : ℝ) with c369 | c369
  · refine ⟨30, 55 + 56 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c368, c369]
  rcases lt_or_ge (t - ⌊t⌋) (20383093 / 20902896 : ℝ) with c370 | c370
  · refine ⟨25, 28 + 28 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c369, c370]
  rcases lt_or_ge (t - ⌊t⌋) (17503561 / 17916768 : ℝ) with c371 | c371
  · refine ⟨23, 24 + 24 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c370, c371]
  rcases lt_or_ge (t - ⌊t⌋) (30671857 / 31354344 : ℝ) with c372 | c372
  · refine ⟨18, 42 + 42 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c371, c372]
  rcases lt_or_ge (t - ⌊t⌋) (10987381 / 11197980 : ℝ) with c373 | c373
  · refine ⟨14, 15 + 15 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c372, c373]
  rcases lt_or_ge (t - ⌊t⌋) (33003289 / 33593940 : ℝ) with c374 | c374
  · refine ⟨31, 45 + 45 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c373, c374]
  rcases lt_or_ge (t - ⌊t⌋) (23509729 / 23889024 : ℝ) with c375 | c375
  · refine ⟨22, 32 + 32 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c374, c375]
  rcases lt_or_ge (t - ⌊t⌋) (26477245 / 26875152 : ℝ) with c376 | c376
  · refine ⟨32, 36 + 36 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c375, c376]
  rcases lt_or_ge (t - ⌊t⌋) (25774633 / 26128620 : ℝ) with c377 | c377
  · refine ⟨12, 35 + 35 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c376, c377]
  rcases lt_or_ge (t - ⌊t⌋) (4457701 / 4479192 : ℝ) with c378 | c378
  · refine ⟨5, 6 + 6 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c377, c378]
  rcases lt_or_ge (t - ⌊t⌋) (1491439 / 1493064 : ℝ) with c379 | c379
  · refine ⟨13, 14 + 14 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c378, c379]
  rcases lt_or_ge (t - ⌊t⌋) (52213069 / 52257240 : ℝ) with c380 | c380
  · refine ⟨33, 70 + 70 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c379, c380]
  rcases lt_or_ge (t - ⌊t⌋) (53742277 / 53750304 : ℝ) with c381 | c381
  · refine ⟨34, 72 + 72 * ⌊t⌋, ?_⟩
    simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
    rw [abs_lt]
    push_cast
    constructor <;> linarith only [c380, c381]
  refine ⟨24, 49 + 48 * ⌊t⌋, ?_⟩
  simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *
  rw [abs_lt]
  push_cast
  constructor <;> linarith only [c381, h1]

#print axioms cover
#print axioms v_injective
#print axioms v_pos
end SLRAudit.N35
