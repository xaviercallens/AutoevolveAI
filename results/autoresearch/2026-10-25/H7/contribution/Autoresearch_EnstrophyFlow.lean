/-
Autoresearch 2026-10-25, H7 stage 1 (formalize): exact conservation of the second invariant `H₃` along the
dispersive shell flow, and the resulting time- and cutoff-uniform enstrophy bound along solutions.

Model (QuantumFluids `lean_src/QuantumFluidsShell.lean`, `shellBc`): shells `0..N+1`, truncation `v_{N+2} = 0`,
  `dv_n/dt = F_n(v) := B_n(v) - i ω_n v_n`,  `B_n = shellBc k n v`  (`B_0 = -k_0 conj(v_0) v_1`,
  `B_{m+1} = k_m v_m² - k_{m+1} conj(v_{m+1}) v_{m+2}`).
σ = 3 is `k_n = 2ⁿ`, `ω_n = D k_n³`.

Section 1 repeats the definitions (`kk`, `energy`, `enstrophy`, `ham3`) and the helper lemmas and pointwise bound
`enstrophy_bound` of the prior round (`H7/Autoresearch_Enstrophy.lean`) with identical statements and proof bodies
(docstrings shortened; `enstrophy_le`, `drop_cubic_term_fails` not repeated), so that this file is self-contained.

Section 2 (new): for a general quadratic-plus-cubic functional
  `H(v) = Σ_{n<N+2} q_n |v_n|² + Σ_{n<N+1} g_n Im(conj(v_n)² v_{n+1})`
its first variation `dHam` in a direction `w`, and the algebraic identity `dHam(v)[F(v)] = 0` under the weight
conditions `g_{n+1}·2k_n = g_n k_{n+1}` and `2 q_{n+1} k_n + g_n (2ω_n - ω_{n+1}) = 2 q_n k_n`. Both hold for
`q_n = 2⁻ⁿ ω_n`, `g_n = 2⁻ⁿ k_n`, for EVERY real sequences `k`, `ω`. The cubic/nonlinear part reuses the owner's
`sum_dT`; the quadratic/nonlinear part and the dispersion/cubic cross terms are new.

Section 3 (new): the chain rule. If `t ↦ u t` solves the ODE on `[0, T]` (every shell `n ≤ N+1` has derivative
`F_n(u t)` at every `t ∈ [0,T]`, and `u t (N+2) = 0`), then `H(u t)` and `S(u t) = Σ|u_n|²` are constant on `[0,T]`.

Section 4 (new): along such a solution of the σ = 3 flow, for every `t ∈ [0,T]`,
  `2 D Ω(u t) ≤ H₃(u 0) + (2 E(u 0))^{3/2}`.

WHAT IS NOT PROVED: existence of solutions (local or global) of the ODE; the solution is a hypothesis. Nothing
about the infinite-shell limit `N → ∞`, blow-up, or the O5 trap.
-/

import ShellHamiltonian

namespace QuantumFluids.AutoresearchEnstrophy

open QuantumFluids.ShellComplex

/-! ## Section 1: prior-round definitions and pointwise bound (verbatim) -/

/-- Dyadic wavenumbers `k_n = 2ⁿ`. -/
noncomputable def kk (n : ℕ) : ℝ := (2 : ℝ) ^ n

/-- Energy `E = ½ Σ_{n ≤ N+1} |v_n|²`. -/
noncomputable def energy (N : ℕ) (v : ℕ → ℂ) : ℝ :=
  (1 / 2) * ∑ n ∈ Finset.range (N + 2), Complex.normSq (v n)

/-- Enstrophy `Ω = ½ Σ_{n ≤ N+1} k_n² |v_n|²`. -/
noncomputable def enstrophy (N : ℕ) (v : ℕ → ℂ) : ℝ :=
  (1 / 2) * ∑ n ∈ Finset.range (N + 2), kk n ^ 2 * Complex.normSq (v n)

/-- Second invariant with σ = 3 dispersion `ω_n = D k_n³`:
`H₃ = Σ 2⁻ⁿ ω_n |v_n|² + Σ 2⁻ⁿ k_n Im(conj(v_n)² v_{n+1})`. -/
noncomputable def ham3 (D : ℝ) (N : ℕ) (v : ℕ → ℂ) : ℝ :=
  ∑ n ∈ Finset.range (N + 2), (1 / 2 : ℝ) ^ n * (D * kk n ^ 3) * Complex.normSq (v n)
    + ∑ n ∈ Finset.range (N + 1),
        ((1 / 2 : ℝ) ^ n * kk n) * ((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * v (n + 1)).im

theorem weight_eq_one (n : ℕ) : (1 / 2 : ℝ) ^ n * kk n = 1 := by
  rw [kk, ← mul_pow]; norm_num

theorem disp_weight (D : ℝ) (n : ℕ) : (1 / 2 : ℝ) ^ n * (D * kk n ^ 3) = D * kk n ^ 2 := by
  have h := weight_eq_one n
  calc (1 / 2 : ℝ) ^ n * (D * kk n ^ 3) = ((1 / 2 : ℝ) ^ n * kk n) * (D * kk n ^ 2) := by ring
    _ = D * kk n ^ 2 := by rw [h, one_mul]

theorem sqrt_mul_self_eq_rpow {S : ℝ} (hS : 0 ≤ S) : Real.sqrt S * S = S ^ (3 / 2 : ℝ) := by
  rw [Real.sqrt_eq_rpow, show (3 / 2 : ℝ) = 1 / 2 + 1 by norm_num,
    Real.rpow_add' hS (by norm_num), Real.rpow_one]

/-- **σ = 3 enstrophy bound (pointwise form).** -/
theorem enstrophy_bound (D : ℝ) (N : ℕ) (v : ℕ → ℂ) :
    2 * D * enstrophy N v ≤ ham3 D N v + (2 * energy N v) ^ (3 / 2 : ℝ) := by
  have hc : ∀ n, |(1 / 2 : ℝ) ^ n * kk n| ≤ 1 := fun n => by rw [weight_eq_one]; norm_num
  have h := dispersive_norm_le (fun n => (1 / 2 : ℝ) ^ n * (D * kk n ^ 3))
    (fun n => (1 / 2 : ℝ) ^ n * kk n) v N (ham3 D N v) hc rfl
  have hq : ∑ n ∈ Finset.range (N + 2), (1 / 2 : ℝ) ^ n * (D * kk n ^ 3) * Complex.normSq (v n)
      = 2 * D * enstrophy N v := by
    rw [enstrophy, Finset.mul_sum, Finset.mul_sum]
    refine Finset.sum_congr rfl (fun n _ => ?_)
    rw [disp_weight]; ring
  have hS0 : 0 ≤ ∑ n ∈ Finset.range (N + 2), Complex.normSq (v n) :=
    Finset.sum_nonneg (fun n _ => Complex.normSq_nonneg _)
  have h2E : 2 * energy N v = ∑ n ∈ Finset.range (N + 2), Complex.normSq (v n) := by
    rw [energy]; ring
  rw [hq, sqrt_mul_self_eq_rpow hS0] at h
  rw [h2E]
  exact h

/-! ## Section 2: the vector field and the algebraic rate identity -/

/-- The right-hand side of the dispersive shell ODE: `F_n(v) = B_n(v) - i ω_n v_n`. -/
noncomputable def F (k ω : ℕ → ℝ) (v : ℕ → ℂ) (n : ℕ) : ℂ :=
  shellBc k n v - Complex.I * (ω n : ℂ) * v n

/-- `R_n = Re(conj(v_n)² v_{n+1})`, the real companion of the Hamiltonian density. -/
noncomputable def R (v : ℕ → ℂ) (n : ℕ) : ℝ :=
  ((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * v (n + 1)).re

/-- General quadratic-plus-cubic functional `Σ_{n<N+2} q_n |v_n|² + Σ_{n<N+1} g_n Im(conj(v_n)² v_{n+1})`. -/
noncomputable def hamG (q g : ℕ → ℝ) (N : ℕ) (v : ℕ → ℂ) : ℝ :=
  ∑ n ∈ Finset.range (N + 2), q n * Complex.normSq (v n)
    + ∑ n ∈ Finset.range (N + 1),
        g n * ((starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * v (n + 1)).im

/-- First variation of `hamG` at `v` in the direction `w` (product rule written out). -/
noncomputable def dHam (q g : ℕ → ℝ) (N : ℕ) (v w : ℕ → ℂ) : ℝ :=
  ∑ n ∈ Finset.range (N + 2), q n * (2 * ((starRingEnd ℂ) (v n) * w n).re)
    + ∑ n ∈ Finset.range (N + 1), g n *
        (2 * (starRingEnd ℂ) (v n) * (starRingEnd ℂ) (w n) * v (n + 1)
          + (starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * w (n + 1)).im

/-- `ham3` is the general functional with `q_n = 2⁻ⁿ D k_n³`, `g_n = 2⁻ⁿ k_n`. -/
theorem ham3_eq_hamG (D : ℝ) (N : ℕ) (v : ℕ → ℂ) :
    ham3 D N v = hamG (fun n => (1 / 2 : ℝ) ^ n * (D * kk n ^ 3)) (fun n => (1 / 2 : ℝ) ^ n * kk n) N v :=
  rfl

/-- The dispersive rotation does no work: `Re(conj(v_n) F_n) = Re(conj(v_n) B_n)`. -/
theorem re_conj_mul_F (k ω : ℕ → ℝ) (v : ℕ → ℂ) (n : ℕ) :
    ((starRingEnd ℂ) (v n) * F k ω v n).re = ((starRingEnd ℂ) (v n) * shellBc k n v).re := by
  have h0 : ((starRingEnd ℂ) (v n) * (Complex.I * (ω n : ℂ) * v n)).re = 0 := by
    simp [Complex.mul_re, Complex.mul_im] <;> ring
  rw [F, mul_sub, Complex.sub_re, h0, sub_zero]

/-- Cubic variation along `F` = owner's `dT` (along `B`) + dispersion cross term `(2ω_n - ω_{n+1}) R_n`. -/
theorem dT_F (k ω : ℕ → ℝ) (v : ℕ → ℂ) (n : ℕ) :
    (2 * (starRingEnd ℂ) (v n) * (starRingEnd ℂ) (F k ω v n) * v (n + 1)
        + (starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * F k ω v (n + 1)).im
      = dT k v n + (2 * ω n - ω (n + 1)) * R v n := by
  simp only [F, dT, R, map_sub, map_mul, Complex.conj_conj, Complex.conj_ofReal, Complex.conj_I]
  simp [Complex.mul_im, Complex.mul_re, Complex.sub_im, Complex.sub_re, Complex.add_im,
    Complex.add_re] <;> ring

theorem re_B_zero (k : ℕ → ℝ) (v : ℕ → ℂ) :
    ((starRingEnd ℂ) (v 0) * shellBc k 0 v).re = -(k 0 * R v 0) := by
  simp only [shellBc, R]
  simp [Complex.mul_re, Complex.mul_im] <;> ring

theorem re_B_succ (k : ℕ → ℝ) (v : ℕ → ℂ) (m : ℕ) :
    ((starRingEnd ℂ) (v (m + 1)) * shellBc k (m + 1) v).re = k m * R v m - k (m + 1) * R v (m + 1) := by
  simp only [shellBc, R]
  simp [Complex.mul_re, Complex.mul_im, Complex.sub_re, Complex.sub_im] <;> ring

/-- Telescoping of the quadratic part along `B` together with the dispersion cross terms. -/
theorem quad_tel (k ω q g : ℕ → ℝ) (v : ℕ → ℂ)
    (hw : ∀ n, 2 * q (n + 1) * k n + g n * (2 * ω n - ω (n + 1)) = 2 * q n * k n) :
    ∀ M : ℕ, ∑ n ∈ Finset.range (M + 1), q n * (2 * ((starRingEnd ℂ) (v n) * shellBc k n v).re)
        + ∑ n ∈ Finset.range M, g n * ((2 * ω n - ω (n + 1)) * R v n)
      = -(2 * q M * k M * R v M)
  | 0 => by
      simp only [zero_add, Finset.sum_range_one, Finset.sum_range_zero, add_zero, re_B_zero]
      ring
  | M + 1 => by
      have h := quad_tel k ω q g v hw M
      rw [Finset.sum_range_succ (fun n => q n * (2 * ((starRingEnd ℂ) (v n) * shellBc k n v).re)) (M + 1),
        Finset.sum_range_succ (fun n => g n * ((2 * ω n - ω (n + 1)) * R v n)) M, re_B_succ]
      linear_combination h + R v M * hw M

/-- **Rate identity (algebraic core).** Under the two weight conditions and the truncation `v_{N+2} = 0`,
the first variation of `hamG` along the full vector field `F` (nonlinearity plus dispersion) vanishes. -/
theorem rate_zero (k ω q g : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ)
    (hg : ∀ n, g (n + 1) * (2 * k n) = g n * k (n + 1))
    (hw : ∀ n, 2 * q (n + 1) * k n + g n * (2 * ω n - ω (n + 1)) = 2 * q n * k n)
    (hbc : v (N + 2) = 0) :
    dHam q g N v (F k ω v) = 0 := by
  unfold dHam
  have hsplit : ∑ n ∈ Finset.range (N + 1), g n *
        (2 * (starRingEnd ℂ) (v n) * (starRingEnd ℂ) (F k ω v n) * v (n + 1)
          + (starRingEnd ℂ) (v n) * (starRingEnd ℂ) (v n) * F k ω v (n + 1)).im
      = ∑ n ∈ Finset.range (N + 1), g n * dT k v n
        + ∑ n ∈ Finset.range (N + 1), g n * ((2 * ω n - ω (n + 1)) * R v n) := by
    rw [← Finset.sum_add_distrib]
    refine Finset.sum_congr rfl (fun n _ => ?_)
    rw [dT_F]; ring
  have hq : ∑ n ∈ Finset.range (N + 2), q n * (2 * ((starRingEnd ℂ) (v n) * F k ω v n).re)
      = ∑ n ∈ Finset.range (N + 2), q n * (2 * ((starRingEnd ℂ) (v n) * shellBc k n v).re) :=
    Finset.sum_congr rfl (fun n _ => by rw [re_conj_mul_F])
  rw [hsplit, hq, sum_dT k g v hg N]
  have ht : ∑ n ∈ Finset.range (N + 2), q n * (2 * ((starRingEnd ℂ) (v n) * shellBc k n v).re)
        + ∑ n ∈ Finset.range (N + 1), g n * ((2 * ω n - ω (n + 1)) * R v n)
      = -(2 * q (N + 1) * k (N + 1) * R v (N + 1)) := quad_tel k ω q g v hw (N + 1)
  have hbc' : v (N + 1 + 1) = 0 := hbc
  have hR : R v (N + 1) = 0 := by simp [R, hbc, hbc']
  have hX : flux4 v N = 0 := by simp [flux4, hbc]
  rw [hR] at ht
  rw [hX]
  linarith

/-- The dyadic weights `q_n = 2⁻ⁿ ω_n`, `g_n = 2⁻ⁿ k_n` satisfy the cross condition, for every `k`, `ω`. -/
theorem cross_weights_ok (k ω : ℕ → ℝ) (n : ℕ) :
    2 * ((1 / 2 : ℝ) ^ (n + 1) * ω (n + 1)) * k n + ((1 / 2 : ℝ) ^ n * k n) * (2 * ω n - ω (n + 1))
      = 2 * ((1 / 2 : ℝ) ^ n * ω n) * k n := by
  rw [pow_succ]; ring

/-- **`H` with dyadic weights is conserved by the truncated dispersive flow (algebraic core),
for every wavenumber sequence `k` and every dispersion law `ω`.** -/
theorem ham_rate_zero (k ω : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ) (hbc : v (N + 2) = 0) :
    dHam (fun n => (1 / 2 : ℝ) ^ n * ω n) (fun n => (1 / 2 : ℝ) ^ n * k n) N v (F k ω v) = 0 :=
  rate_zero k ω _ _ v N (weights_ok k) (cross_weights_ok k ω) hbc

/-- **Energy rate (algebraic core):** `Σ_{n<N+2} 2 Re(conj(v_n) F_n) = 0` under `v_{N+2} = 0`. -/
theorem energy_rate_zero (k ω : ℕ → ℝ) (v : ℕ → ℂ) (N : ℕ) (hbc : v (N + 2) = 0) :
    ∑ n ∈ Finset.range (N + 2), 2 * ((starRingEnd ℂ) (v n) * F k ω v n).re = 0 := by
  have h : ∑ n ∈ Finset.range (N + 2), ((starRingEnd ℂ) (v n) * shellBc k n v).re = 0 :=
    shellBc_energy_conservation k v (N + 1) hbc
  calc ∑ n ∈ Finset.range (N + 2), 2 * ((starRingEnd ℂ) (v n) * F k ω v n).re
      = 2 * ∑ n ∈ Finset.range (N + 2), ((starRingEnd ℂ) (v n) * shellBc k n v).re := by
        rw [Finset.mul_sum]
        exact Finset.sum_congr rfl (fun n _ => by rw [re_conj_mul_F])
    _ = 0 := by rw [h, mul_zero]

/-! ## Section 3: chain rule along solutions -/

theorem hasDerivAt_re {f : ℝ → ℂ} {f' : ℂ} {t : ℝ} (h : HasDerivAt f f' t) :
    HasDerivAt (fun s => (f s).re) f'.re t := by
  have C : HasFDerivAt Complex.re Complex.reCLM (f t) := Complex.reCLM.hasFDerivAt
  simpa using! C.comp_hasDerivAt t h

theorem hasDerivAt_im {f : ℝ → ℂ} {f' : ℂ} {t : ℝ} (h : HasDerivAt f f' t) :
    HasDerivAt (fun s => (f s).im) f'.im t := by
  have C : HasFDerivAt Complex.im Complex.imCLM (f t) := Complex.imCLM.hasFDerivAt
  simpa using! C.comp_hasDerivAt t h

theorem hasDerivAt_conj {f : ℝ → ℂ} {f' : ℂ} {t : ℝ} (h : HasDerivAt f f' t) :
    HasDerivAt (fun s => (starRingEnd ℂ) (f s)) ((starRingEnd ℂ) f') t :=
  h.star

theorem normSq_eq_re (z : ℂ) : Complex.normSq z = ((starRingEnd ℂ) z * z).re := by
  rw [← Complex.normSq_eq_conj_mul_self, Complex.ofReal_re]

theorem hasDerivAt_normSq {f : ℝ → ℂ} {f' : ℂ} {t : ℝ} (h : HasDerivAt f f' t) :
    HasDerivAt (fun s => Complex.normSq (f s)) (2 * ((starRingEnd ℂ) (f t) * f').re) t := by
  have h2 := hasDerivAt_re ((hasDerivAt_conj h).fun_mul h)
  have e : (fun s => Complex.normSq (f s)) = fun s => ((starRingEnd ℂ) (f s) * f s).re := by
    funext s; exact normSq_eq_re (f s)
  have e2 : 2 * ((starRingEnd ℂ) (f t) * f').re
      = ((starRingEnd ℂ) f' * f t + (starRingEnd ℂ) (f t) * f').re := by
    simp [Complex.mul_re, Complex.add_re] <;> ring
  rw [e, e2]
  exact h2

theorem hasDerivAt_cubic {f g : ℝ → ℂ} {f' g' : ℂ} {t : ℝ} (hf : HasDerivAt f f' t)
    (hg : HasDerivAt g g' t) :
    HasDerivAt (fun s => ((starRingEnd ℂ) (f s) * (starRingEnd ℂ) (f s) * g s).im)
      ((2 * (starRingEnd ℂ) (f t) * (starRingEnd ℂ) f' * g t
        + (starRingEnd ℂ) (f t) * (starRingEnd ℂ) (f t) * g').im) t := by
  have hc := hasDerivAt_conj hf
  have h2 := hasDerivAt_im ((hc.fun_mul hc).fun_mul hg)
  have e : 2 * (starRingEnd ℂ) (f t) * (starRingEnd ℂ) f' * g t
        + (starRingEnd ℂ) (f t) * (starRingEnd ℂ) (f t) * g'
      = ((starRingEnd ℂ) f' * (starRingEnd ℂ) (f t) + (starRingEnd ℂ) (f t) * (starRingEnd ℂ) f') * g t
        + (starRingEnd ℂ) (f t) * (starRingEnd ℂ) (f t) * g' := by ring
  rw [e]
  exact h2

/-- **Chain rule for `hamG`.** -/
theorem hasDerivAt_hamG (q g : ℕ → ℝ) (N : ℕ) (u : ℝ → ℕ → ℂ) (u' : ℕ → ℂ) (t : ℝ)
    (hu : ∀ n, n < N + 2 → HasDerivAt (fun s => u s n) (u' n) t) :
    HasDerivAt (fun s => hamG q g N (u s)) (dHam q g N (u t) u') t := by
  have h1 : HasDerivAt (fun s => ∑ n ∈ Finset.range (N + 2), q n * Complex.normSq (u s n))
      (∑ n ∈ Finset.range (N + 2), q n * (2 * ((starRingEnd ℂ) (u t n) * u' n).re)) t :=
    HasDerivAt.fun_sum (fun n hn => (hasDerivAt_normSq (hu n (Finset.mem_range.mp hn))).const_mul (q n))
  have h2 : HasDerivAt (fun s => ∑ n ∈ Finset.range (N + 1),
        g n * ((starRingEnd ℂ) (u s n) * (starRingEnd ℂ) (u s n) * u s (n + 1)).im)
      (∑ n ∈ Finset.range (N + 1), g n *
        (2 * (starRingEnd ℂ) (u t n) * (starRingEnd ℂ) (u' n) * u t (n + 1)
          + (starRingEnd ℂ) (u t n) * (starRingEnd ℂ) (u t n) * u' (n + 1)).im) t := by
    refine HasDerivAt.fun_sum (fun n hn => ?_)
    have hn' := Finset.mem_range.mp hn
    exact (hasDerivAt_cubic (hu n (by omega)) (hu (n + 1) (by omega))).const_mul (g n)
  exact h1.add h2

/-- A functional whose derivative vanishes along the solution on `[0, T]` is constant there. -/
theorem const_on_Icc (Φ : (ℕ → ℂ) → ℝ) (Φ' : (ℕ → ℂ) → ℝ) (u : ℝ → ℕ → ℂ) (T : ℝ)
    (hd : ∀ t ∈ Set.Icc (0 : ℝ) T, HasDerivAt (fun s => Φ (u s)) (Φ' (u t)) t)
    (hz : ∀ t ∈ Set.Icc (0 : ℝ) T, Φ' (u t) = 0) :
    ∀ t ∈ Set.Icc (0 : ℝ) T, Φ (u t) = Φ (u 0) := by
  have hcont : ContinuousOn (fun s => Φ (u s)) (Set.Icc 0 T) :=
    fun t ht => (hd t ht).continuousAt.continuousWithinAt
  have hder : ∀ x ∈ Set.Ico (0 : ℝ) T, HasDerivWithinAt (fun s => Φ (u s)) 0 (Set.Ici x) x := by
    intro x hx
    have hx' : x ∈ Set.Icc (0 : ℝ) T := Set.Ico_subset_Icc_self hx
    have := hd x hx'
    rw [hz x hx'] at this
    exact this.hasDerivWithinAt
  exact constant_of_has_deriv_right_zero hcont hder

/-- **`H` is constant along solutions of the truncated dispersive flow on `[0, T]`** (any `k`, `ω`). -/
theorem ham_conserved (k ω : ℕ → ℝ) (N : ℕ) (u : ℝ → ℕ → ℂ) (T : ℝ)
    (hsol : ∀ t ∈ Set.Icc (0 : ℝ) T, ∀ n, n < N + 2 →
      HasDerivAt (fun s => u s n) (F k ω (u t) n) t)
    (hbc : ∀ t ∈ Set.Icc (0 : ℝ) T, u t (N + 2) = 0) :
    ∀ t ∈ Set.Icc (0 : ℝ) T,
      hamG (fun n => (1 / 2 : ℝ) ^ n * ω n) (fun n => (1 / 2 : ℝ) ^ n * k n) N (u t)
        = hamG (fun n => (1 / 2 : ℝ) ^ n * ω n) (fun n => (1 / 2 : ℝ) ^ n * k n) N (u 0) :=
  const_on_Icc (hamG (fun n => (1 / 2 : ℝ) ^ n * ω n) (fun n => (1 / 2 : ℝ) ^ n * k n) N)
    (fun v => dHam (fun n => (1 / 2 : ℝ) ^ n * ω n) (fun n => (1 / 2 : ℝ) ^ n * k n) N v (F k ω v)) u T
    (fun t ht => hasDerivAt_hamG _ _ N u (F k ω (u t)) t (hsol t ht))
    (fun t ht => ham_rate_zero k ω (u t) N (hbc t ht))

/-- **Energy is constant along solutions on `[0, T]`.** -/
theorem energy_conserved (k ω : ℕ → ℝ) (N : ℕ) (u : ℝ → ℕ → ℂ) (T : ℝ)
    (hsol : ∀ t ∈ Set.Icc (0 : ℝ) T, ∀ n, n < N + 2 →
      HasDerivAt (fun s => u s n) (F k ω (u t) n) t)
    (hbc : ∀ t ∈ Set.Icc (0 : ℝ) T, u t (N + 2) = 0) :
    ∀ t ∈ Set.Icc (0 : ℝ) T, energy N (u t) = energy N (u 0) := by
  have hd : ∀ t ∈ Set.Icc (0 : ℝ) T,
      HasDerivAt (fun s => energy N (u s))
        ((fun v => (1 / 2 : ℝ) * ∑ n ∈ Finset.range (N + 2), 2 * ((starRingEnd ℂ) (v n) * F k ω v n).re)
          (u t)) t := by
    intro t ht
    exact (HasDerivAt.fun_sum (fun n hn =>
      hasDerivAt_normSq (hsol t ht n (Finset.mem_range.mp hn)))).const_mul (1 / 2 : ℝ)
  exact const_on_Icc (energy N)
    (fun v => (1 / 2 : ℝ) * ∑ n ∈ Finset.range (N + 2), 2 * ((starRingEnd ℂ) (v n) * F k ω v n).re) u T hd
    (fun t ht => by
      show (1 / 2 : ℝ) * ∑ n ∈ Finset.range (N + 2), 2 * ((starRingEnd ℂ) (u t n) * F k ω (u t) n).re = 0
      rw [energy_rate_zero k ω (u t) N (hbc t ht), mul_zero])

/-! ## Section 4: the σ = 3 enstrophy bound along solutions, uniform in time and cutoff -/

/-- **σ = 3: `2DΩ(t) ≤ H₃(0) + (2E(0))^{3/2}` for every `t ∈ [0, T]` along a solution of the truncated
σ = 3 dispersive shell flow** (`k_n = 2ⁿ`, `ω_n = D k_n³`, any real `D`, any cutoff `N`). The right-hand side
depends only on the initial state. -/
theorem enstrophy_bound_along_flow (D : ℝ) (N : ℕ) (u : ℝ → ℕ → ℂ) (T : ℝ)
    (hsol : ∀ t ∈ Set.Icc (0 : ℝ) T, ∀ n, n < N + 2 →
      HasDerivAt (fun s => u s n) (F kk (fun m => D * kk m ^ 3) (u t) n) t)
    (hbc : ∀ t ∈ Set.Icc (0 : ℝ) T, u t (N + 2) = 0) :
    ∀ t ∈ Set.Icc (0 : ℝ) T,
      2 * D * enstrophy N (u t) ≤ ham3 D N (u 0) + (2 * energy N (u 0)) ^ (3 / 2 : ℝ) := by
  intro t ht
  have hH := ham_conserved kk (fun m => D * kk m ^ 3) N u T hsol hbc t ht
  have hE := energy_conserved kk (fun m => D * kk m ^ 3) N u T hsol hbc t ht
  have hb := enstrophy_bound D N (u t)
  have hH' : ham3 D N (u t) = ham3 D N (u 0) := hH
  rw [hH', hE] at hb
  exact hb

/-- `D > 0` form: `Ω(t) ≤ (H₃(0) + (2E(0))^{3/2}) / (2D)` along the flow. -/
theorem enstrophy_le_along_flow (D : ℝ) (hD : 0 < D) (N : ℕ) (u : ℝ → ℕ → ℂ) (T : ℝ)
    (hsol : ∀ t ∈ Set.Icc (0 : ℝ) T, ∀ n, n < N + 2 →
      HasDerivAt (fun s => u s n) (F kk (fun m => D * kk m ^ 3) (u t) n) t)
    (hbc : ∀ t ∈ Set.Icc (0 : ℝ) T, u t (N + 2) = 0) :
    ∀ t ∈ Set.Icc (0 : ℝ) T,
      enstrophy N (u t) ≤ (ham3 D N (u 0) + (2 * energy N (u 0)) ^ (3 / 2 : ℝ)) / (2 * D) := by
  intro t ht
  rw [le_div_iff₀ (by positivity)]
  have := enstrophy_bound_along_flow D N u T hsol hbc t ht
  linarith

/-- Consistency witness only (not a non-triviality result): the zero trajectory satisfies the solution
hypotheses of `enstrophy_bound_along_flow` for every `D`, `N`, `T`. -/
theorem zero_trajectory_is_solution (D : ℝ) (N : ℕ) (T : ℝ) :
    (∀ t ∈ Set.Icc (0 : ℝ) T, ∀ n, n < N + 2 →
      HasDerivAt (fun s => (fun (_ : ℝ) (_ : ℕ) => (0 : ℂ)) s n)
        (F kk (fun m => D * kk m ^ 3) ((fun (_ : ℝ) (_ : ℕ) => (0 : ℂ)) t) n) t)
    ∧ (∀ t ∈ Set.Icc (0 : ℝ) T, (fun (_ : ℝ) (_ : ℕ) => (0 : ℂ)) t (N + 2) = 0) := by
  refine ⟨fun t _ n _ => ?_, fun t _ => rfl⟩
  have h0 : F kk (fun m => D * kk m ^ 3) (fun _ => (0 : ℂ)) n = 0 := by
    cases n <;> simp [F, shellBc]
  rw [h0]
  exact hasDerivAt_const t (0 : ℂ)

/-! ## Controls inside the claimed development (sensitivity, not planted holes) -/

/-- Two-shell test state `v = (1, 1, 0, 0, …)`. -/
noncomputable def v11 : ℕ → ℂ := fun n => if n < 2 then 1 else 0

/-- **Positive control (direct computation, independent of `rate_zero`).** With the correct dyadic weights,
`N = 0`, `D = 1`, the σ = 3 rate at `v11` is `0`. -/
theorem rate_v11_correct :
    dHam (fun n => (1 / 2 : ℝ) ^ n * (1 * kk n ^ 3)) (fun n => (1 / 2 : ℝ) ^ n * kk n) 0 v11
      (F kk (fun m => 1 * kk m ^ 3) v11) = 0 := by
  simp [dHam, F, shellBc, v11, kk, Finset.sum_range_succ, Complex.mul_re, Complex.mul_im]
  norm_num

/-- **Negative control: the `2⁻ⁿ` weight on the dispersive part is load-bearing.** With `q_n = ω_n`
(weight dropped), same state, `N = 0`, `D = 1`: the rate is `8 ≠ 0`, so that functional is not conserved. -/
theorem rate_v11_wrong_weight :
    dHam (fun n => 1 * kk n ^ 3) (fun n => (1 / 2 : ℝ) ^ n * kk n) 0 v11
      (F kk (fun m => 1 * kk m ^ 3) v11) = 8 := by
  simp [dHam, F, shellBc, v11, kk, Finset.sum_range_succ, Complex.mul_re, Complex.mul_im]
  norm_num

/-- **Negative control: the truncation is load-bearing.** With `v_2 ≠ 0` (state `(1,1,1,0,…)`, `N = 0`), the
correct-weight σ = 3 rate is nonzero. -/
noncomputable def v111 : ℕ → ℂ := fun n => if n < 3 then 1 else 0

theorem rate_v111_no_truncation :
    dHam (fun n => (1 / 2 : ℝ) ^ n * (1 * kk n ^ 3)) (fun n => (1 / 2 : ℝ) ^ n * kk n) 0 v111
      (F kk (fun m => 1 * kk m ^ 3) v111) ≠ 0 := by
  simp [dHam, F, shellBc, v111, kk, Finset.sum_range_succ, Complex.mul_re, Complex.mul_im]
  norm_num

end QuantumFluids.AutoresearchEnstrophy

#print axioms QuantumFluids.AutoresearchEnstrophy.enstrophy_bound
#print axioms QuantumFluids.AutoresearchEnstrophy.re_conj_mul_F
#print axioms QuantumFluids.AutoresearchEnstrophy.dT_F
#print axioms QuantumFluids.AutoresearchEnstrophy.quad_tel
#print axioms QuantumFluids.AutoresearchEnstrophy.rate_zero
#print axioms QuantumFluids.AutoresearchEnstrophy.ham_rate_zero
#print axioms QuantumFluids.AutoresearchEnstrophy.energy_rate_zero
#print axioms QuantumFluids.AutoresearchEnstrophy.hasDerivAt_hamG
#print axioms QuantumFluids.AutoresearchEnstrophy.const_on_Icc
#print axioms QuantumFluids.AutoresearchEnstrophy.ham_conserved
#print axioms QuantumFluids.AutoresearchEnstrophy.energy_conserved
#print axioms QuantumFluids.AutoresearchEnstrophy.enstrophy_bound_along_flow
#print axioms QuantumFluids.AutoresearchEnstrophy.enstrophy_le_along_flow
#print axioms QuantumFluids.AutoresearchEnstrophy.zero_trajectory_is_solution
#print axioms QuantumFluids.AutoresearchEnstrophy.rate_v11_correct
#print axioms QuantumFluids.AutoresearchEnstrophy.rate_v11_wrong_weight
#print axioms QuantumFluids.AutoresearchEnstrophy.rate_v111_no_truncation
