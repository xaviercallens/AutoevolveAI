import BAOCert.Core
import Mathlib.Analysis.SpecialFunctions.Pow.Real

/-!
# Generic layer for certified BAO likelihoods (pilot P2)

* monotonicity of `invE`, `chi` and the `D_V` base `wV` in `Om`;
* cube-root bounds;
* a rational interval evaluator for expression trees with a soundness theorem;
* the centred profile bound: `A > 0 → ∀ t, c - t B + t² A ≥ c - B²/(4A)`;
* `checkFrom_take`, so prefixes of a checked table need no re-check.
-/

namespace BAOCert

open MeasureTheory Set

/-! ## Monotonicity in `Om` -/

lemma invE_pos {Om x : ℝ} (h0 : 0 ≤ Om) (h1 : Om ≤ 1) (hx : 0 ≤ x) : 0 < invE Om x := by
  unfold invE E
  exact one_div_pos.2 (Real.sqrt_pos.2 (arg_pos h0 h1 hx))

lemma invE_anti_Om {a b x : ℝ} (ha : 0 ≤ a) (hab : a ≤ b) (hb : b ≤ 1) (hx : 0 ≤ x) :
    invE b x ≤ invE a x := by
  unfold invE E
  have hA := arg_pos ha (hab.trans hb) hx
  have h3 : 1 ≤ (1 + x) ^ 3 := one_le_pow₀ (by linarith)
  have hmono : a * (1 + x) ^ 3 + (1 - a) ≤ b * (1 + x) ^ 3 + (1 - b) := by nlinarith
  exact one_div_le_one_div_of_le (Real.sqrt_pos.2 hA) (Real.sqrt_le_sqrt hmono)

lemma invE_intervalIntegrable {Om z : ℝ} (h0 : 0 ≤ Om) (h1 : Om ≤ 1) (hz : 0 ≤ z) :
    IntervalIntegrable (invE Om) volume 0 z := by
  have hsub : uIcc (0 : ℝ) z ⊆ Ici 0 := by
    intro x hx
    rw [uIcc_of_le hz] at hx
    exact hx.1
  exact ((invE_antitoneOn h0 h1).mono hsub).intervalIntegrable

lemma chi_nonneg {Om z : ℝ} (h0 : 0 ≤ Om) (h1 : Om ≤ 1) (hz : 0 ≤ z) : 0 ≤ chi Om z := by
  unfold chi
  exact intervalIntegral.integral_nonneg hz (fun x hx => (invE_pos h0 h1 hx.1).le)

lemma chi_anti_Om {a b z : ℝ} (ha : 0 ≤ a) (hab : a ≤ b) (hb : b ≤ 1) (hz : 0 ≤ z) :
    chi b z ≤ chi a z := by
  unfold chi
  exact intervalIntegral.integral_mono_on hz (invE_intervalIntegrable (ha.trans hab) hb hz)
    (invE_intervalIntegrable ha (hab.trans hb) hz) (fun x hx => invE_anti_Om ha hab hb hx.1)

/-! ## Cube roots and the `D_V` base -/

/-- Real cube root on `[0, ∞)`. -/
noncomputable def cbrt (x : ℝ) : ℝ := x ^ ((3 : ℝ)⁻¹)

lemma cbrt_mono {x y : ℝ} (hx : 0 ≤ x) (hxy : x ≤ y) : cbrt x ≤ cbrt y :=
  Real.rpow_le_rpow hx hxy (by norm_num)

lemma cbrt_cube {v : ℝ} (hv : 0 ≤ v) : cbrt (v ^ 3) = v := by
  unfold cbrt
  have h := Real.pow_rpow_inv_natCast hv (n := 3) (by norm_num)
  simpa using h

lemma le_cbrt {v X : ℝ} (hv : 0 ≤ v) (h : v ^ 3 ≤ X) : v ≤ cbrt X := by
  calc v = cbrt (v ^ 3) := (cbrt_cube hv).symm
    _ ≤ cbrt X := cbrt_mono (by positivity) h

lemma cbrt_le {v X : ℝ} (hv : 0 ≤ v) (hX : 0 ≤ X) (h : X ≤ v ^ 3) : cbrt X ≤ v :=
  (cbrt_mono hX h).trans_eq (cbrt_cube hv)

/-- The `D_V` base: `D_V / r_d = K · wV`, `wV = (z χ² / E)^{1/3}`. -/
noncomputable def wV (Om z : ℝ) : ℝ := cbrt (z * chi Om z ^ 2 * invE Om z)

lemma wV_bounds {Om z cl ch il ih wl wh : ℝ} (h0 : 0 ≤ Om) (h1 : Om ≤ 1) (hz : 0 ≤ z)
    (hcl : 0 ≤ cl) (hil : 0 ≤ il) (hwl : 0 ≤ wl) (hwh : 0 ≤ wh)
    (hc : cl ≤ chi Om z ∧ chi Om z ≤ ch) (hi : il ≤ invE Om z ∧ invE Om z ≤ ih)
    (hlo : wl ^ 3 ≤ z * cl ^ 2 * il) (hhi : z * ch ^ 2 * ih ≤ wh ^ 3) :
    wl ≤ wV Om z ∧ wV Om z ≤ wh := by
  have hchi0 := chi_nonneg h0 h1 hz
  have hinv0 := (invE_pos h0 h1 hz).le
  have hX0 : 0 ≤ z * chi Om z ^ 2 * invE Om z := by positivity
  have hXlo : z * cl ^ 2 * il ≤ z * chi Om z ^ 2 * invE Om z := by
    have := pow_le_pow_left₀ hcl hc.1 2
    have h2 : z * cl ^ 2 ≤ z * chi Om z ^ 2 := mul_le_mul_of_nonneg_left this hz
    exact mul_le_mul h2 hi.1 hil (by positivity)
  have hXhi : z * chi Om z ^ 2 * invE Om z ≤ z * ch ^ 2 * ih := by
    have := pow_le_pow_left₀ hchi0 hc.2 2
    have h2 : z * chi Om z ^ 2 ≤ z * ch ^ 2 := mul_le_mul_of_nonneg_left this hz
    exact mul_le_mul h2 hi.2 hinv0 (by nlinarith [sq_nonneg ch])
  exact ⟨le_cbrt hwl (hlo.trans hXlo), cbrt_le hwh hX0 (hXhi.trans hhi)⟩

lemma wV_anti_Om {a b z : ℝ} (ha : 0 ≤ a) (hab : a ≤ b) (hb : b ≤ 1) (hz : 0 ≤ z) :
    wV b z ≤ wV a z := by
  unfold wV
  have hcb := chi_nonneg (ha.trans hab) hb hz
  have hib := (invE_pos (ha.trans hab) hb hz).le
  have hX0 : 0 ≤ z * chi b z ^ 2 * invE b z := by positivity
  apply cbrt_mono hX0
  have h2 : z * chi b z ^ 2 ≤ z * chi a z ^ 2 :=
    mul_le_mul_of_nonneg_left (pow_le_pow_left₀ hcb (chi_anti_Om ha hab hb hz) 2) hz
  exact mul_le_mul h2 (invE_anti_Om ha hab hb hz) hib (by positivity)

/-! ## Rational interval evaluation -/

/-- A closed rational interval `[lo, hi]`. -/
structure Iv where
  lo : ℚ
  hi : ℚ
deriving DecidableEq

/-- `x ∈ [lo, hi]`. -/
def Iv.mem (I : Iv) (x : ℝ) : Prop := (I.lo : ℝ) ≤ x ∧ x ≤ (I.hi : ℝ)

def Iv.add (I J : Iv) : Iv := ⟨I.lo + J.lo, I.hi + J.hi⟩

def Iv.mul (I J : Iv) : Iv :=
  ⟨min (min (I.lo * J.lo) (I.lo * J.hi)) (min (I.hi * J.lo) (I.hi * J.hi)),
   max (max (I.lo * J.lo) (I.lo * J.hi)) (max (I.hi * J.lo) (I.hi * J.hi))⟩

/-- Expression trees over rational constants and variables. -/
inductive Ex where
  | c (q : ℚ)
  | v (j : ℕ)
  | add (a b : Ex)
  | mul (a b : Ex)

/-- Real value of an expression for the variable assignment `x`. -/
noncomputable def Ex.eval (x : ℕ → ℝ) : Ex → ℝ
  | .c q => (q : ℝ)
  | .v j => x j
  | .add a b => a.eval x + b.eval x
  | .mul a b => a.eval x * b.eval x

/-- Interval value of an expression for the interval assignment `env`. -/
def Ex.ieval (env : ℕ → Iv) : Ex → Iv
  | .c q => ⟨q, q⟩
  | .v j => env j
  | .add a b => (a.ieval env).add (b.ieval env)
  | .mul a b => (a.ieval env).mul (b.ieval env)

lemma lin_lo {a b x c : ℝ} (h1 : a ≤ x) (h2 : x ≤ b) : min (c * a) (c * b) ≤ c * x := by
  rcases le_total 0 c with hc | hc
  · exact (min_le_left _ _).trans (mul_le_mul_of_nonneg_left h1 hc)
  · exact (min_le_right _ _).trans (mul_le_mul_of_nonpos_left h2 hc)

lemma lin_hi {a b x c : ℝ} (h1 : a ≤ x) (h2 : x ≤ b) : c * x ≤ max (c * a) (c * b) := by
  rcases le_total 0 c with hc | hc
  · exact (mul_le_mul_of_nonneg_left h2 hc).trans (le_max_right _ _)
  · exact (mul_le_mul_of_nonpos_left h1 hc).trans (le_max_left _ _)

lemma Iv.mem_add {I J : Iv} {x y : ℝ} (hx : I.mem x) (hy : J.mem y) : (I.add J).mem (x + y) := by
  unfold Iv.mem Iv.add at *
  push_cast
  exact ⟨add_le_add hx.1 hy.1, add_le_add hx.2 hy.2⟩

lemma Iv.mem_mul {I J : Iv} {x y : ℝ} (hx : I.mem x) (hy : J.mem y) : (I.mul J).mem (x * y) := by
  unfold Iv.mem Iv.mul at *
  obtain ⟨hx1, hx2⟩ := hx
  obtain ⟨hy1, hy2⟩ := hy
  push_cast
  set a : ℝ := (I.lo : ℝ)
  set b : ℝ := (I.hi : ℝ)
  set c : ℝ := (J.lo : ℝ)
  set d : ℝ := (J.hi : ℝ)
  constructor
  · -- x y ≥ min (y a) (y b), and y a ≥ min (a c) (a d), y b ≥ min (b c) (b d)
    have h0 : min (y * a) (y * b) ≤ y * x := lin_lo hx1 hx2
    have ha : min (a * c) (a * d) ≤ a * y := lin_lo hy1 hy2
    have hb : min (b * c) (b * d) ≤ b * y := lin_lo hy1 hy2
    have e1 : y * a = a * y := mul_comm _ _
    have e2 : y * b = b * y := mul_comm _ _
    have e3 : y * x = x * y := mul_comm _ _
    rw [e1, e2, e3] at h0
    calc min (min (a * c) (a * d)) (min (b * c) (b * d)) ≤ min (a * y) (b * y) := min_le_min ha hb
      _ ≤ x * y := h0
  · have h0 : y * x ≤ max (y * a) (y * b) := lin_hi hx1 hx2
    have ha : a * y ≤ max (a * c) (a * d) := lin_hi hy1 hy2
    have hb : b * y ≤ max (b * c) (b * d) := lin_hi hy1 hy2
    have e1 : y * a = a * y := mul_comm _ _
    have e2 : y * b = b * y := mul_comm _ _
    have e3 : y * x = x * y := mul_comm _ _
    rw [e1, e2, e3] at h0
    calc x * y ≤ max (a * y) (b * y) := h0
      _ ≤ max (max (a * c) (a * d)) (max (b * c) (b * d)) := max_le_max ha hb

/-- Soundness of interval evaluation. -/
theorem Ex.ieval_sound (x : ℕ → ℝ) (env : ℕ → Iv) (h : ∀ j, (env j).mem (x j)) :
    ∀ e : Ex, (e.ieval env).mem (e.eval x) := by
  intro e
  induction e with
  | c q => exact ⟨le_refl _, le_refl _⟩
  | v j => exact h j
  | add a b iha ihb => exact Iv.mem_add iha ihb
  | mul a b iha ihb => exact Iv.mem_mul iha ihb

/-- Interval assignments read from a list (default `[0, 0]`, which contains the default value `0`). -/
def envOf (L : List Iv) (j : ℕ) : Iv := L.getD j ⟨0, 0⟩

/-- Variable assignments read from a list (default `0`). -/
noncomputable def valOf (L : List ℝ) (j : ℕ) : ℝ := L.getD j 0

lemma env_ok : ∀ (E : List Iv) (X : List ℝ), List.Forall₂ (fun I x => I.mem x) E X →
    ∀ j, (envOf E j).mem (valOf X j) := by
  intro E X h
  induction h with
  | nil => intro j; simp [envOf, valOf, Iv.mem]
  | cons hx _ ih =>
    intro j
    cases j with
    | zero => simpa [envOf, valOf] using hx
    | succ j => simpa [envOf, valOf] using ih j

/-! ## Quadratic forms over sparse entries and the centred profile -/

/-- Sum of a list of expressions. -/
def sumEx : List Ex → Ex
  | [] => .c 0
  | e :: t => .add e (sumEx t)

lemma eval_sumEx (x : ℕ → ℝ) : ∀ L : List Ex, (sumEx L).eval x = (L.map (Ex.eval x)).sum := by
  intro L
  induction L with
  | nil => simp [sumEx, Ex.eval]
  | cons e t ih => simp [sumEx, Ex.eval, ih]

/-- Residual expression `d_j - K₀ x_j`. -/
def rEx (d : List ℚ) (K0 : ℚ) (j : ℕ) : Ex := .add (.c (d.getD j 0)) (.mul (.c (-K0)) (.v j))

/-- `c' = Σ P_jk r_j r_k` at `K₀`. -/
def cEx (P : List (ℕ × ℕ × ℚ)) (d : List ℚ) (K0 : ℚ) : Ex :=
  sumEx (P.map fun e => .mul (.c e.2.2) (.mul (rEx d K0 e.1) (rEx d K0 e.2.1)))

/-- `B' = Σ P_jk (r_j x_k + x_j r_k)`. -/
def bEx (P : List (ℕ × ℕ × ℚ)) (d : List ℚ) (K0 : ℚ) : Ex :=
  sumEx (P.map fun e => .mul (.c e.2.2) (.add (.mul (rEx d K0 e.1) (.v e.2.1)) (.mul (.v e.1) (rEx d K0 e.2.1))))

/-- `A = Σ P_jk x_j x_k`. -/
def aEx (P : List (ℕ × ℕ × ℚ)) : Ex :=
  sumEx (P.map fun e => .mul (.c e.2.2) (.mul (.v e.1) (.v e.2.1)))

/-- The Gaussian `χ²` over the sparse entries `P` of the inverse covariance, for prediction `K x_j`. -/
noncomputable def chi2Of (P : List (ℕ × ℕ × ℚ)) (d : List ℚ) (x : ℕ → ℝ) (K : ℝ) : ℝ :=
  (P.map fun e => (e.2.2 : ℝ) * (((d.getD e.1 0 : ℚ) : ℝ) - K * x e.1) * (((d.getD e.2.1 0 : ℚ) : ℝ) - K * x e.2.1)).sum

theorem chi2_expand (P : List (ℕ × ℕ × ℚ)) (d : List ℚ) (K0 : ℚ) (x : ℕ → ℝ) (K : ℝ) :
    chi2Of P d x K = (cEx P d K0).eval x - (K - K0) * (bEx P d K0).eval x + (K - K0) ^ 2 * (aEx P).eval x := by
  unfold chi2Of cEx bEx aEx
  rw [eval_sumEx, eval_sumEx, eval_sumEx]
  induction P with
  | nil => simp
  | cons e t ih =>
    simp only [List.map_cons, List.sum_cons] at ih ⊢
    rw [ih]
    simp only [Ex.eval, rEx]
    push_cast
    ring

/-- For `A ≥ A_lo > 0`, `c ≥ c_lo`, `|B| ≤ B_m`: `c - t B + t² A ≥ c_lo - B_m²/(4 A_lo)` for every `t`. -/
theorem profile_lower {c B A cl Bm Al : ℝ} (hc : cl ≤ c) (hB : |B| ≤ Bm) (hAl : 0 < Al) (hA : Al ≤ A) (t : ℝ) :
    cl - Bm ^ 2 / (4 * Al) ≤ c - t * B + t ^ 2 * A := by
  have hA0 : 0 < A := lt_of_lt_of_le hAl hA
  have hsq : 0 ≤ A * (t - B / (2 * A)) ^ 2 := by positivity
  have key : c - B ^ 2 / (4 * A) ≤ c - t * B + t ^ 2 * A := by
    have : c - t * B + t ^ 2 * A - (c - B ^ 2 / (4 * A)) = A * (t - B / (2 * A)) ^ 2 := by
      field_simp
      ring
    linarith
  have hB2 : B ^ 2 ≤ Bm ^ 2 := by
    have := sq_abs B
    nlinarith [abs_nonneg B, hB]
  have hfrac : B ^ 2 / (4 * A) ≤ Bm ^ 2 / (4 * Al) := by
    apply div_le_div₀ (by positivity) hB2 (by positivity)
    linarith
  linarith

lemma abs_le_of_mem {I : Iv} {x : ℝ} (h : I.mem x) : |x| ≤ ((max |I.lo| |I.hi| : ℚ) : ℝ) := by
  obtain ⟨h1, h2⟩ := h
  push_cast
  rw [abs_le]
  constructor
  · have : -(max |(I.lo : ℝ)| |(I.hi : ℝ)|) ≤ (I.lo : ℝ) := by
      have := neg_abs_le (I.lo : ℝ)
      have := le_max_left |(I.lo : ℝ)| |(I.hi : ℝ)|
      linarith
    linarith
  · have : (I.hi : ℝ) ≤ max |(I.lo : ℝ)| |(I.hi : ℝ)| := (le_abs_self _).trans (le_max_right _ _)
    linarith

/-! ## Case lemmas used by the generated files -/

/-- If every variable lies in its interval, then `χ²(K) ≥ L` for **every** real `K`
(profile over `K = c/(100 h r_d)`), as soon as two rational inequalities hold. -/
theorem chi2_lower_of_env (P : List (ℕ × ℕ × ℚ)) (d : List ℚ) (K0 : ℚ) (x : ℕ → ℝ) (env : ℕ → Iv)
    (henv : ∀ j, (env j).mem (x j)) (L : ℚ)
    (hA : 0 < ((aEx P).ieval env).lo)
    (hL : L ≤ ((cEx P d K0).ieval env).lo -
      (max |((bEx P d K0).ieval env).lo| |((bEx P d K0).ieval env).hi|) ^ 2 / (4 * ((aEx P).ieval env).lo)) :
    ∀ K : ℝ, (L : ℝ) ≤ chi2Of P d x K := by
  intro K
  have hc := Ex.ieval_sound x env henv (cEx P d K0)
  have hb := Ex.ieval_sound x env henv (bEx P d K0)
  have ha := Ex.ieval_sound x env henv (aEx P)
  rw [chi2_expand P d K0 x K]
  have hAr : (0 : ℝ) < (((aEx P).ieval env).lo : ℝ) := by exact_mod_cast hA
  have hLr : (L : ℝ) ≤ (((cEx P d K0).ieval env).lo : ℝ) -
      (((max |((bEx P d K0).ieval env).lo| |((bEx P d K0).ieval env).hi| : ℚ)) : ℝ) ^ 2 /
        (4 * (((aEx P).ieval env).lo : ℝ)) := by
    have := (Rat.cast_le (K := ℝ)).2 hL
    push_cast at this ⊢
    exact this
  exact hLr.trans (profile_lower hc.1 (abs_le_of_mem hb) hAr ha.1 (K - K0))

/-- At `K = K₀` the value of `χ²` lies in the interval of the centred constant term. -/
theorem chi2_mem_at_K0 (P : List (ℕ × ℕ × ℚ)) (d : List ℚ) (K0 : ℚ) (x : ℕ → ℝ) (env : ℕ → Iv)
    (henv : ∀ j, (env j).mem (x j)) : ((cEx P d K0).ieval env).mem (chi2Of P d x (K0 : ℝ)) := by
  rw [chi2_expand P d K0 x (K0 : ℝ)]
  simpa using Ex.ieval_sound x env henv (cEx P d K0)

/-! ## Tables: prefixes of a checked table are checked -/

lemma checkFrom_take (p q S D : ℕ) : ∀ (L : List (ℕ × ℕ)) (i k : ℕ),
    checkFrom p q S D i L = true → checkFrom p q S D i (L.take k) = true := by
  intro L
  induction L with
  | nil => intro i k _; simp [checkFrom]
  | cons x t ih =>
    intro i k h
    cases k with
    | zero => simp [checkFrom]
    | succ k =>
      simp only [List.take_succ_cons, checkFrom, Bool.and_eq_true] at h ⊢
      exact ⟨h.1, ih (i + 1) k h.2⟩

/-! ## Smoke test: kernel evaluation of the interval evaluator on rationals -/

example : (Ex.ieval (envOf [⟨123456789012345 / 1000000000000, 123456789012346 / 1000000000000⟩,
    ⟨-98765432109 / 100000000000, -98765432108 / 100000000000⟩])
    (.add (.mul (.c (35321 / 1000)) (.mul (.v 0) (.v 1))) (.mul (.v 1) (.v 1)))).hi ≤ -42 := by
  decide +kernel

end BAOCert
