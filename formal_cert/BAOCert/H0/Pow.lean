import BAOCert.H0.BBNBase
import BAOCert.Likelihood
import Mathlib.Analysis.SpecialFunctions.Log.Deriv
import Mathlib.Analysis.Complex.ExponentialBounds

/-!
# Certified enclosures of `log`, `exp` and the Aubourg sound horizon (pilot P3)

* `log x` for rational `0 < x`: write `x · 2^k = 1 - u` with `0 ≤ u < 1`; Mathlib's
  `Real.abs_log_sub_add_sum_range_le` bounds `log (1 - u)`, and `Real.log_two_near_10` bounds `log 2`.
* `exp t` for rational `|t| ≤ 1`: Mathlib's `Real.exp_bound`.
* `rdAubourg ω_cb ω_b = 55.154 · exp(c₀ - a log ω_cb - b log ω_b)` with `c₀ = -72.3 (ω_ν + 0.0006)²`,
  `a = 0.25351`, `b = 0.12807`, enclosed through `exp T = (exp (T/2))²`.
All rational side conditions are closed by `decide +kernel` in the instances.
-/

namespace BAOCert.H0

open BAOCert ANSE.BAOBBNH0 Finset

/-- `Σ_{i<n} u^{i+1}/(i+1)`. -/
def logSum (u : ℚ) (n : ℕ) : ℚ := ∑ i ∈ range n, u ^ (i + 1) / (i + 1)

/-- `u^{n+1}/(1-u)`. -/
def logRem (u : ℚ) (n : ℕ) : ℚ := u ^ (n + 1) / (1 - u)

/-- Rational bracket of `log 2` from `|log 2 - 287209/414355| ≤ 10⁻¹⁰`. -/
def log2lo : ℚ := 287209 / 414355 - 1 / 10 ^ 10
def log2hi : ℚ := 287209 / 414355 + 1 / 10 ^ 10

/-- Enclosure of `log x` for `x · 2^k = 1 - u`. -/
def logIv (x : ℚ) (k n : ℕ) : Iv :=
  let u := 1 - x * 2 ^ k
  ⟨-logSum u n - logRem u n - k * log2hi, -logSum u n + logRem u n - k * log2lo⟩

/-- Side condition for `logIv`: `0 ≤ u < 1`. -/
def logOK (x : ℚ) (k : ℕ) : Bool := decide (0 < x * 2 ^ k) && decide (x * 2 ^ k ≤ 1)

lemma log_two_mem : (log2lo : ℝ) ≤ Real.log 2 ∧ Real.log 2 ≤ (log2hi : ℝ) := by
  have h := Real.log_two_near_10
  rw [abs_le] at h
  unfold log2lo log2hi
  push_cast
  constructor <;> linarith [h.1, h.2]

theorem logIv_mem (x : ℚ) (k n : ℕ) (h : logOK x k = true) : (logIv x k n).mem (Real.log x) := by
  simp only [logOK, Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨hpos, hle⟩ := h
  set u : ℚ := 1 - x * 2 ^ k with hu
  have hu0 : (0 : ℝ) ≤ u := by
    have : (0 : ℚ) ≤ u := by rw [hu]; linarith
    exact_mod_cast this
  have hu1 : (u : ℝ) < 1 := by
    have : u < 1 := by rw [hu]; linarith
    exact_mod_cast this
  have habs : |(u : ℝ)| < 1 := by rw [abs_of_nonneg hu0]; exact hu1
  have hser := Real.abs_log_sub_add_sum_range_le habs n
  rw [abs_of_nonneg hu0] at hser
  have hx0 : (0 : ℝ) < (x : ℝ) := by
    have : (0 : ℚ) < x := by
      by_contra hc
      push_neg at hc
      have : x * 2 ^ k ≤ 0 := mul_nonpos_of_nonpos_of_nonneg hc (by positivity)
      linarith
    exact_mod_cast this
  have hsplit : Real.log (x : ℝ) = Real.log (1 - (u : ℝ)) - k * Real.log 2 := by
    have h1 : (1 : ℝ) - u = (x : ℝ) * 2 ^ k := by rw [hu]; push_cast; ring
    rw [h1, Real.log_mul hx0.ne' (by positivity), Real.log_pow]
    ring
  have hl2 := log_two_mem
  have hk : (0 : ℝ) ≤ k := by positivity
  rw [abs_le] at hser
  unfold logIv Iv.mem
  simp only
  push_cast [logSum, logRem]
  rw [hsplit]
  have hu' : (u : ℝ) = 1 - (x : ℝ) * 2 ^ k := by rw [hu]; push_cast; ring
  rw [hu'] at hser ⊢
  constructor
  · nlinarith [hser.1, hser.2, mul_le_mul_of_nonneg_left hl2.2 hk]
  · nlinarith [hser.1, hser.2, mul_le_mul_of_nonneg_left hl2.1 hk]

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

/-! ## The sound horizon -/

/-- `a`, `b`, `c₀` of eq. 16 as rationals. -/
def aQ : ℚ := 25351 / 100000
def bQ : ℚ := 12807 / 100000
def c0Q : ℚ := -(723 / 10) * (107 / 10000 * (6 / 100) + 6 / 10000) ^ 2

/-- Enclosure of the exponent `T = c₀ - a log ω_cb - b log ω_b`. -/
def tIv (wcb wb : ℚ) (k1 k2 n : ℕ) : Iv :=
  ⟨c0Q - aQ * (logIv wcb k1 n).hi - bQ * (logIv wb k2 n).hi, c0Q - aQ * (logIv wcb k1 n).lo - bQ * (logIv wb k2 n).lo⟩

/-- Enclosure of `rdAubourg` via `exp T = (exp (T/2))²`. -/
def rdIv (wcb wb : ℚ) (k1 k2 n m : ℕ) : Iv :=
  let T := tIv wcb wb k1 k2 n
  ⟨(55154 / 1000) * (expSum (T.lo / 2) m - expRem (T.lo / 2) m) ^ 2,
   (55154 / 1000) * (expSum (T.hi / 2) m + expRem (T.hi / 2) m) ^ 2⟩

/-- All side conditions of `rdIv`. -/
def rdOK (wcb wb : ℚ) (k1 k2 n m : ℕ) : Bool :=
  let T := tIv wcb wb k1 k2 n
  logOK wcb k1 && logOK wb k2 && decide (0 < m) && decide (|T.lo / 2| ≤ 1) && decide (|T.hi / 2| ≤ 1) &&
    decide (0 ≤ expSum (T.lo / 2) m - expRem (T.lo / 2) m)

lemma rd_eq_exp {wcb wb : ℝ} (h1 : 0 < wcb) (h2 : 0 < wb) :
    rdAubourg wcb wb = 55.154 * Real.exp (-72.3 * (omegaNu + 0.0006) ^ 2 - 0.25351 * Real.log wcb - 0.12807 * Real.log wb) := by
  unfold rdAubourg
  rw [Real.rpow_def_of_pos h1, Real.rpow_def_of_pos h2, ← Real.exp_add, mul_div_assoc, ← Real.exp_sub]
  congr 2
  ring

theorem rdIv_mem (wcb wb : ℚ) (k1 k2 n m : ℕ) (h : rdOK wcb wb k1 k2 n m = true) :
    (rdIv wcb wb k1 k2 n m).mem (rdAubourg wcb wb) := by
  simp only [rdOK, Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨⟨⟨⟨h1, h2⟩, hm⟩, hlo⟩, hhi⟩, hpos⟩ := h
  have L1 := logIv_mem wcb k1 n h1
  have L2 := logIv_mem wb k2 n h2
  have pos_of_logOK : ∀ {x : ℚ} {k : ℕ}, logOK x k = true → (0 : ℝ) < x := by
    intro x k hk
    simp only [logOK, Bool.and_eq_true, decide_eq_true_eq] at hk
    have : (0 : ℚ) < x := by
      by_contra hc
      push_neg at hc
      have : x * 2 ^ k ≤ 0 := mul_nonpos_of_nonpos_of_nonneg hc (by positivity)
      linarith [hk.1]
    exact_mod_cast this
  rw [rd_eq_exp (pos_of_logOK h1) (pos_of_logOK h2)]
  set T : ℝ := -72.3 * (omegaNu + 0.0006) ^ 2 - 0.25351 * Real.log wcb - 0.12807 * Real.log wb with hT
  have hc0 : (-72.3 : ℝ) * (omegaNu + 0.0006) ^ 2 = (c0Q : ℝ) := by unfold c0Q omegaNu; push_cast; norm_num
  have ha : (0.25351 : ℝ) = (aQ : ℝ) := by unfold aQ; push_cast; norm_num
  have hb : (0.12807 : ℝ) = (bQ : ℝ) := by unfold bQ; push_cast; norm_num
  have hTmem : (((tIv wcb wb k1 k2 n).lo : ℚ) : ℝ) ≤ T ∧ T ≤ (((tIv wcb wb k1 k2 n).hi : ℚ) : ℝ) := by
    rw [hT, hc0, ha, hb]
    unfold tIv
    unfold Iv.mem at L1 L2
    have ha0 : (0 : ℝ) ≤ aQ := by unfold aQ; norm_num
    have hb0 : (0 : ℝ) ≤ bQ := by unfold bQ; norm_num
    push_cast
    constructor
    · nlinarith [mul_le_mul_of_nonneg_left L1.2 ha0, mul_le_mul_of_nonneg_left L2.2 hb0]
    · nlinarith [mul_le_mul_of_nonneg_left L1.1 ha0, mul_le_mul_of_nonneg_left L2.1 hb0]
  set Tq := tIv wcb wb k1 k2 n
  have Elo := (exp_mem (Tq.lo / 2) m hm hlo).1
  have Ehi := (exp_mem (Tq.hi / 2) m hm hhi).2
  have hsq : Real.exp T = Real.exp (T / 2) ^ 2 := by rw [← Real.exp_nat_mul]; congr 1; push_cast; ring
  have hmono1 : Real.exp ((Tq.lo / 2 : ℚ) : ℝ) ≤ Real.exp (T / 2) := by
    apply Real.exp_le_exp.2; push_cast; linarith [hTmem.1]
  have hmono2 : Real.exp (T / 2) ≤ Real.exp ((Tq.hi / 2 : ℚ) : ℝ) := by
    apply Real.exp_le_exp.2; push_cast; linarith [hTmem.2]
  have hpos' : (0 : ℝ) ≤ ((expSum (Tq.lo / 2) m - expRem (Tq.lo / 2) m : ℚ) : ℝ) := by exact_mod_cast hpos
  unfold rdIv Iv.mem
  simp only
  rw [hsq]
  push_cast at Elo Ehi hpos' hmono1 hmono2 ⊢
  have e1 : (0 : ℝ) ≤ Real.exp (T / 2) := (Real.exp_pos _).le
  constructor
  · have := pow_le_pow_left₀ hpos' (Elo.trans hmono1) 2
    nlinarith [this]
  · have := pow_le_pow_left₀ e1 (hmono2.trans Ehi) 2
    nlinarith [this]

/-! ## Smoke test at Om = 0.3, h = 0.73, ω_b = 0.02218 -/

example : rdOK (3 / 10 * (73 / 100) ^ 2 - 107 / 10000 * (6 / 100)) (2218 / 100000) 2 5 60 25 = true := by
  decide +kernel

end BAOCert.H0
