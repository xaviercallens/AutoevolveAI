import Mathlib.Analysis.Complex.ExponentialBounds
import Mathlib.Analysis.Real.Pi.Bounds
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Order.Interval.Finset.Defs
import Mathlib.Data.Int.Interval
import Mathlib.Data.Set.Card
import Mathlib.Algebra.Order.Field.GeomSum
import Mathlib.Tactic

/-!
# M3: independent kernel check of the finite lemmas of Luo–Wei (arXiv 2610.31456), generic part

Objects of the paper, with the paper's notation:
* `a2 = a² = 2^{1/3}` (FCC minimal squared length, unit covolume), `b2 = 2^{-4/3}` (BCC squared-length unit).
* `Nc n` = number of integer triples of squared norm `2n` (Lemma A.5), `Mc l` = number of integer triples of
  squared norm `l` whose coordinates all have the same parity. Both are *computed* by the kernel over a box and
  proved equal to the `Set.ncard` of the full (infinite-domain) set (`Nc_eq_ncard`, `Mc_eq_ncard`).
* Certified `exp` enclosures for rational arguments (`Real.exp_bound`, range reduction `exp z = exp(z/8)^8`),
  `π` from `Real.pi_gt_d20`/`Real.pi_lt_d20`, cube-root bounds from cubes.
* Chain lemmas: an untrusted rational table checked step by step (`chainLo`, `chainHi`) encloses the geometric
  sequence `x e^k`; `polR` monotonicity lifts it to the finite shell sums.
Tier A covers only these Lean statements. The passage from them to Lemma 6.1 (theta functions as lattice sums,
Poisson summation, the derivative argument) is NOT formalised here.
-/

namespace YukawaBccFcc

open Finset

/-! ## Shell multiplicities -/

def normSq (m : ℤ × ℤ × ℤ) : ℤ := m.1 ^ 2 + m.2.1 ^ 2 + m.2.2 ^ 2

def box (R : ℤ) : Finset (ℤ × ℤ × ℤ) := Icc (-R) R ×ˢ Icc (-R) R ×ˢ Icc (-R) R

/-- All coordinates have the same parity. -/
def sameParity (m : ℤ × ℤ × ℤ) : Prop := m.1 % 2 = m.2.1 % 2 ∧ m.2.1 % 2 = m.2.2 % 2

instance : DecidablePred sameParity := fun m => by unfold sameParity; infer_instance

/-- FCC multiplicity `N_n`: integer triples of squared norm `2n`, counted in the box `[-5,5]³`. -/
def Nc (n : ℕ) : ℕ := ((box 5).filter (fun m => normSq m = 2 * (n : ℤ))).card

/-- BCC multiplicity `M_l`: same-parity integer triples of squared norm `l`, counted in the box `[-6,6]³`. -/
def Mc (l : ℕ) : ℕ := ((box 6).filter (fun m => normSq m = (l : ℤ) ∧ sameParity m)).card

lemma coord_le {x : ℤ} {R : ℤ} (hR : 0 ≤ R) (h : x ^ 2 < (R + 1) ^ 2) : -R ≤ x ∧ x ≤ R := by
  have := abs_lt_of_sq_lt_sq' h (by linarith)
  constructor <;> omega

lemma mem_box_of_normSq_lt {R : ℤ} (hR : 0 ≤ R) (m : ℤ × ℤ × ℤ) (h : normSq m < (R + 1) ^ 2) : m ∈ box R := by
  obtain ⟨x, y, z⟩ := m
  simp only [normSq] at h
  have hx := coord_le hR (show x ^ 2 < (R + 1) ^ 2 by nlinarith [sq_nonneg y, sq_nonneg z])
  have hy := coord_le hR (show y ^ 2 < (R + 1) ^ 2 by nlinarith [sq_nonneg x, sq_nonneg z])
  have hz := coord_le hR (show z ^ 2 < (R + 1) ^ 2 by nlinarith [sq_nonneg x, sq_nonneg y])
  simp only [box, mem_product, mem_Icc]
  exact ⟨hx, hy, hz⟩

/-- The box count is the count over all of `ℤ³` (for `2n < 36`). -/
theorem Nc_eq_ncard (n : ℕ) (hn : 2 * n < 36) :
    Nc n = Set.ncard {m : ℤ × ℤ × ℤ | normSq m = 2 * (n : ℤ)} := by
  rw [Nc, ← Set.ncard_coe_finset]
  congr 1
  ext m
  simp only [coe_filter, Set.mem_ofPred_eq, and_iff_right_iff_imp]
  intro h
  exact mem_box_of_normSq_lt (by norm_num) m (by rw [h]; norm_num; omega)

/-- The box count is the count over all of `ℤ³` (for `l < 49`). -/
theorem Mc_eq_ncard (l : ℕ) (hl : l < 49) :
    Mc l = Set.ncard {m : ℤ × ℤ × ℤ | normSq m = (l : ℤ) ∧ sameParity m} := by
  rw [Mc, ← Set.ncard_coe_finset]
  congr 1
  ext m
  simp only [coe_filter, Set.mem_ofPred_eq, and_iff_right_iff_imp]
  intro h
  exact mem_box_of_normSq_lt (by norm_num) m (by rw [h.1]; norm_num; omega)

/-! ## Constants -/

/-- `a² = 2^{1/3}`. -/
noncomputable def a2 : ℝ := (2 : ℝ) ^ ((1 : ℝ) / 3)

/-- `2^{-4/3}`. -/
noncomputable def b2 : ℝ := (2 : ℝ) ^ (-(4 : ℝ) / 3)

lemma a2_pos : 0 < a2 := Real.rpow_pos_of_pos (by norm_num) _

lemma b2_pos : 0 < b2 := Real.rpow_pos_of_pos (by norm_num) _

lemma a2_cube : a2 ^ 3 = 2 := by
  unfold a2
  rw [← Real.rpow_natCast, ← Real.rpow_mul (by norm_num)]
  norm_num

lemma b2_cube : b2 ^ 3 = 1 / 16 := by
  unfold b2
  rw [← Real.rpow_natCast, ← Real.rpow_mul (by norm_num)]
  rw [show (-(4 : ℝ) / 3 * ((3 : ℕ) : ℝ)) = -((4 : ℕ) : ℝ) by push_cast; ring, Real.rpow_neg (by norm_num),
    Real.rpow_natCast]
  norm_num

lemma lt_of_cube_lt_cube {x y : ℝ} (hy : 0 ≤ y) (h : x ^ 3 < y ^ 3) : x < y := lt_of_pow_lt_pow_left₀ 3 hy h

/-- Rational bracket of `a2` from rational cubes. -/
lemma a2_mem (lo hi : ℚ) (_h1 : 0 ≤ lo) (h2 : lo ^ 3 < 2) (h3 : 2 < hi ^ 3) (h4 : 0 ≤ hi) :
    (lo : ℝ) < a2 ∧ a2 < (hi : ℝ) := by
  constructor
  · apply lt_of_cube_lt_cube a2_pos.le
    rw [a2_cube]; exact_mod_cast h2
  · apply lt_of_cube_lt_cube (by exact_mod_cast h4)
    rw [a2_cube]; exact_mod_cast h3

lemma b2_mem (lo hi : ℚ) (_h1 : 0 ≤ lo) (h2 : lo ^ 3 < 1 / 16) (h3 : 1 / 16 < hi ^ 3) (h4 : 0 ≤ hi) :
    (lo : ℝ) < b2 ∧ b2 < (hi : ℝ) := by
  constructor
  · apply lt_of_cube_lt_cube b2_pos.le
    rw [b2_cube]
    have := (Rat.cast_lt (K := ℝ)).2 h2
    push_cast at this
    exact this
  · apply lt_of_cube_lt_cube (by exact_mod_cast h4)
    rw [b2_cube]
    have := (Rat.cast_lt (K := ℝ)).2 h3
    push_cast at this
    exact this

def piLo : ℚ := 314159265358979323846 / 10 ^ 20
def piHi : ℚ := 314159265358979323847 / 10 ^ 20

lemma pi_mem : (piLo : ℝ) < Real.pi ∧ Real.pi < (piHi : ℝ) := by
  have h1 := Real.pi_gt_d20
  have h2 := Real.pi_lt_d20
  unfold piLo piHi
  constructor
  · push_cast; norm_num at h1 ⊢; linarith
  · push_cast; norm_num at h2 ⊢; linarith

/-- Product bracket for positive factors. -/
lemma mul_mem {x y : ℝ} {xl xh yl yh : ℚ} (hxl : 0 ≤ xl) (hyl : 0 ≤ yl) (hx : (xl : ℝ) < x ∧ x < xh)
    (hy : (yl : ℝ) < y ∧ y < yh) : ((xl * yl : ℚ) : ℝ) ≤ x * y ∧ x * y ≤ ((xh * yh : ℚ) : ℝ) := by
  have hxl' : (0 : ℝ) ≤ xl := by exact_mod_cast hxl
  have hyl' : (0 : ℝ) ≤ yl := by exact_mod_cast hyl
  push_cast
  constructor
  · exact mul_le_mul hx.1.le hy.1.le hyl' (by linarith [hx.1])
  · exact mul_le_mul hx.2.le hy.2.le (by linarith [hy.1]) (by linarith [hx.1, hx.2])

/-! ## Certified `exp` of a rational -/

/-- `Σ_{m<n} t^m/m!`. -/
def expSum (t : ℚ) (n : ℕ) : ℚ := ∑ m ∈ range n, t ^ m / (m.factorial : ℚ)

/-- `|t|^n (n+1)/(n! n)`. -/
def expRem (t : ℚ) (n : ℕ) : ℚ := |t| ^ n * ((n + 1 : ℚ) / ((n.factorial : ℚ) * n))

theorem exp_mem (t : ℚ) (n : ℕ) (hn : 0 < n) (ht : |t| ≤ 1) :
    ((expSum t n - expRem t n : ℚ) : ℝ) ≤ Real.exp t ∧ Real.exp t ≤ ((expSum t n + expRem t n : ℚ) : ℝ) := by
  have ht' : |(t : ℝ)| ≤ 1 := by exact_mod_cast ht
  have h := Real.exp_bound ht' hn
  rw [abs_le] at h
  unfold expSum expRem
  push_cast
  have e : ((n.succ : ℝ) / ((n.factorial : ℝ) * n)) = ((n : ℝ) + 1) / ((n.factorial : ℝ) * n) := by push_cast; ring
  rw [e] at h
  constructor <;> linarith [h.1, h.2]

/-- Lower enclosure of `exp z` through `exp z = exp(z/8)^8`. -/
def eLo (z : ℚ) (n : ℕ) : ℚ := (expSum (z / 8) n - expRem (z / 8) n) ^ 8

/-- Upper enclosure of `exp z` through `exp z = exp(z/8)^8`. -/
def eHi (z : ℚ) (n : ℕ) : ℚ := (expSum (z / 8) n + expRem (z / 8) n) ^ 8

def eOK (z : ℚ) (n : ℕ) : Bool :=
  decide (0 < n) && decide (|z / 8| ≤ 1) && decide (0 ≤ expSum (z / 8) n - expRem (z / 8) n)

lemma exp_eq_pow8 (z : ℝ) : Real.exp z = Real.exp (z / 8) ^ 8 := by
  rw [← Real.exp_nat_mul]; congr 1; push_cast; ring

theorem eLo_le (z : ℚ) (n : ℕ) (h : eOK z n = true) : ((eLo z n : ℚ) : ℝ) ≤ Real.exp z := by
  simp only [eOK, Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨hn, hz⟩, hp⟩ := h
  have E := (exp_mem (z / 8) n hn hz).1
  have hp' : (0 : ℝ) ≤ ((expSum (z / 8) n - expRem (z / 8) n : ℚ) : ℝ) := by exact_mod_cast hp
  rw [exp_eq_pow8]
  unfold eLo
  push_cast at E hp' ⊢
  exact pow_le_pow_left₀ hp' E 8

theorem le_eHi (z : ℚ) (n : ℕ) (h : eOK z n = true) : Real.exp z ≤ ((eHi z n : ℚ) : ℝ) := by
  simp only [eOK, Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨hn, hz⟩, _⟩ := h
  have E := (exp_mem (z / 8) n hn hz).2
  rw [exp_eq_pow8]
  unfold eHi
  push_cast at E ⊢
  exact pow_le_pow_left₀ (Real.exp_pos _).le E 8

/-- `exp(-p t) ≥ eLo(-ph t)` when `p ≤ ph`, `t ≥ 0`. -/
lemma exp_neg_lo {p : ℝ} {ph t : ℚ} (n : ℕ) (hp : p ≤ ph) (ht : 0 ≤ t) (h : eOK (-ph * t) n = true) :
    ((eLo (-ph * t) n : ℚ) : ℝ) ≤ Real.exp (-p * t) := by
  refine (eLo_le _ n h).trans (Real.exp_le_exp.2 ?_)
  have ht' : (0 : ℝ) ≤ t := by exact_mod_cast ht
  push_cast
  nlinarith

/-- `exp(-p t) ≤ eHi(-pl t)` when `pl ≤ p`, `t ≥ 0`. -/
lemma exp_neg_hi {p : ℝ} {pl t : ℚ} (n : ℕ) (hp : (pl : ℝ) ≤ p) (ht : 0 ≤ t) (h : eOK (-pl * t) n = true) :
    Real.exp (-p * t) ≤ ((eHi (-pl * t) n : ℚ) : ℝ) := by
  refine (Real.exp_le_exp.2 ?_).trans (le_eHi _ n h)
  have ht' : (0 : ℝ) ≤ t := by exact_mod_cast ht
  push_cast
  nlinarith

/-! ## Checked chains -/

/-- Lower chain: `0 ≤ b ≤ a s` for consecutive entries. -/
def chainLo (s : ℚ) : List ℚ → Bool
  | a :: b :: t => decide (0 ≤ b) && decide (b ≤ a * s) && chainLo s (b :: t)
  | _ => true

/-- Upper chain: `b ≥ a S` for consecutive entries. -/
def chainHi (S : ℚ) : List ℚ → Bool
  | a :: b :: t => decide (a * S ≤ b) && chainHi S (b :: t)
  | _ => true

theorem chainLo_sound (s : ℚ) (e : ℝ) (he : 0 ≤ e) (hs : (s : ℝ) ≤ e) :
    ∀ (l : List ℚ) (x : ℝ), chainLo s l = true → (0 : ℚ) ≤ l.headD 0 → ((l.headD 0 : ℚ) : ℝ) ≤ x →
      ∀ k, k < l.length → ((l.getD k 0 : ℚ) : ℝ) ≤ x * e ^ k := by
  intro l
  induction l with
  | nil => intro x _ _ _ k hk; simp at hk
  | cons a t ih =>
    intro x hc ha hax k hk
    cases k with
    | zero => simpa using hax
    | succ k =>
      cases t with
      | nil => simp at hk
      | cons b t' =>
        simp only [chainLo, Bool.and_eq_true, decide_eq_true_eq] at hc
        obtain ⟨⟨hb0, hbs⟩, hrest⟩ := hc
        simp only [List.headD_cons] at ha hax
        have ha' : (0 : ℝ) ≤ a := by exact_mod_cast ha
        have hbx : ((b : ℚ) : ℝ) ≤ x * e := by
          have h1 : ((b : ℚ) : ℝ) ≤ (a : ℝ) * s := by exact_mod_cast hbs
          have h2 : (a : ℝ) * s ≤ a * e := mul_le_mul_of_nonneg_left hs ha'
          have h3 : (a : ℝ) * e ≤ x * e := mul_le_mul_of_nonneg_right hax he
          linarith
        have := ih (x * e) hrest (by simpa using hb0) (by simpa using hbx) k (by simpa using hk)
        rw [List.getD_cons_succ, pow_succ]
        calc _ ≤ x * e * e ^ k := this
          _ = x * (e ^ k * e) := by ring

theorem chainHi_sound (S : ℚ) (e : ℝ) (he : 0 ≤ e) (hs : e ≤ (S : ℝ)) :
    ∀ (l : List ℚ) (x : ℝ), chainHi S l = true → 0 ≤ x → x ≤ ((l.headD 0 : ℚ) : ℝ) →
      ∀ k, k < l.length → x * e ^ k ≤ ((l.getD k 0 : ℚ) : ℝ) := by
  intro l
  induction l with
  | nil => intro x _ _ _ k hk; simp at hk
  | cons a t ih =>
    intro x hc hx0 hax k hk
    cases k with
    | zero => simpa using hax
    | succ k =>
      cases t with
      | nil => simp at hk
      | cons b t' =>
        simp only [chainHi, Bool.and_eq_true, decide_eq_true_eq] at hc
        obtain ⟨hbs, hrest⟩ := hc
        simp only [List.headD_cons] at hax
        have hbx : x * e ≤ ((b : ℚ) : ℝ) := by
          have h1 : (a : ℝ) * S ≤ ((b : ℚ) : ℝ) := by exact_mod_cast hbs
          have ha0 : (0 : ℝ) ≤ a := hx0.trans hax
          have h2 : (a : ℝ) * e ≤ a * S := mul_le_mul_of_nonneg_left hs ha0
          have h3 : x * e ≤ a * e := mul_le_mul_of_nonneg_right hax he
          linarith
        have := ih (x * e) hrest (mul_nonneg hx0 he) (by simpa using hbx) k (by simpa using hk)
        rw [List.getD_cons_succ, pow_succ]
        calc x * (e ^ k * e) = x * e * e ^ k := by ring
          _ ≤ _ := this

/-! ## Shell polynomials -/

/-- `Σ_{n=1}^{K} w(n) c(n) q^n` over `ℚ`. -/
def polQ (w c : ℕ → ℕ) (K : ℕ) (q : ℚ) : ℚ := ∑ n ∈ Icc 1 K, (w n : ℚ) * (c n : ℚ) * q ^ n

/-- `Σ_{n=1}^{K} w(n) c(n) x^n` over `ℝ`. -/
noncomputable def polR (w c : ℕ → ℕ) (K : ℕ) (x : ℝ) : ℝ := ∑ n ∈ Icc 1 K, (w n : ℝ) * (c n : ℝ) * x ^ n

lemma polQ_cast (w c : ℕ → ℕ) (K : ℕ) (q : ℚ) : ((polQ w c K q : ℚ) : ℝ) = polR w c K q := by
  simp [polQ, polR]

lemma polR_mono (w c : ℕ → ℕ) (K : ℕ) {x y : ℝ} (hx : 0 ≤ x) (hxy : x ≤ y) : polR w c K x ≤ polR w c K y := by
  unfold polR
  apply sum_le_sum
  intro n _
  exact mul_le_mul_of_nonneg_left (pow_le_pow_left₀ hx hxy n) (by positivity)

lemma polR_nonneg (w c : ℕ → ℕ) (K : ℕ) {x : ℝ} (hx : 0 ≤ x) : 0 ≤ polR w c K x := by
  unfold polR
  exact sum_nonneg fun n _ => by positivity

lemma polR_congr (w c c' : ℕ → ℕ) (K : ℕ) (h : ∀ n ∈ Icc 1 K, c n = c' n) (x : ℝ) :
    polR w c K x = polR w c' K x := by
  unfold polR
  exact sum_congr rfl fun n hn => by rw [h n hn]

/-- The paper's shell sum `Σ w(n) c(n) e^{-p n t}` is `polR` at `x = e^{-p t}`. -/
lemma shell_sum_eq (w c : ℕ → ℕ) (K : ℕ) (p t : ℝ) :
    ∑ n ∈ Icc 1 K, (w n : ℝ) * (c n : ℝ) * Real.exp (-p * n * t) = polR w c K (Real.exp (-p * t)) := by
  unfold polR
  refine sum_congr rfl fun n _ => ?_
  rw [← Real.exp_nat_mul]
  congr 2
  ring

/-- `x e^k` for `x = e^{-p t₀}`, `e = e^{-p h}` is `e^{-p (t₀ + k h)}`. -/
lemma geom_exp (p t0 h : ℝ) (k : ℕ) :
    Real.exp (-p * t0) * Real.exp (-p * h) ^ k = Real.exp (-p * (t0 + k * h)) := by
  rw [← Real.exp_nat_mul, ← Real.exp_add]
  congr 1
  ring

/-! ## Geometric tail domination (for the omitted-shell bounds of Lemma 6.1) -/

theorem tail_le (a : ℕ → ℝ) (N : ℕ) (ρ : ℝ) (h0 : ∀ n, 0 ≤ a n) (hρ0 : 0 ≤ ρ) (hρ : ρ < 1)
    (hstep : ∀ n, N ≤ n → a (n + 1) ≤ ρ * a n) (K : ℕ) :
    ∑ k ∈ range K, a (N + k) ≤ a N / (1 - ρ) := by
  have hdom : ∀ k, a (N + k) ≤ a N * ρ ^ k := by
    intro k
    induction k with
    | zero => simp
    | succ k ih =>
      calc a (N + (k + 1)) = a ((N + k) + 1) := by rw [Nat.add_succ]
        _ ≤ ρ * a (N + k) := hstep _ (Nat.le_add_right _ _)
        _ ≤ ρ * (a N * ρ ^ k) := mul_le_mul_of_nonneg_left ih hρ0
        _ = a N * ρ ^ (k + 1) := by ring
  have hgeom : ∑ k ∈ range K, ρ ^ k ≤ 1 / (1 - ρ) := by
    have := geom_sum_Ico_le_of_lt_one (m := 0) (n := K) hρ0 hρ
    rw [pow_zero] at this
    rwa [Finset.range_eq_Ico]
  calc ∑ k ∈ range K, a (N + k) ≤ ∑ k ∈ range K, a N * ρ ^ k := sum_le_sum fun k _ => hdom k
    _ = a N * ∑ k ∈ range K, ρ ^ k := by rw [mul_sum]
    _ ≤ a N * (1 / (1 - ρ)) := mul_le_mul_of_nonneg_left hgeom (h0 N)
    _ = a N / (1 - ρ) := by ring

end YukawaBccFcc
