import ANSE.DyadicNavierStokesRegulatorSpec
import Mathlib.Data.Real.Basic
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Data.Finset.Basic
import Mathlib.Tactic

/-!
# Cutoff-Uniform Enstrophy Bounds, Fractional Riccati Integrability Thresholds, and Resonant-Triad Depletion in Dyadic and Toroidal Fluid Hierarchies

Formal Lean 4 proof module for the 10-Hypothesis Frontier Investigation (six hypotheses proved
at Tier A/B, four refuted or obstructed by machine-checked counterexample and obstruction theorems).
Every theorem in this module is checked against its read-only canonical specification in
`ANSE.DyadicNavierStokesRegulatorSpec` via environment-level definitional equality (`example : Spec.<Target> := <Candidate>`).
-/

open ANSE.DyadicNavierStokesRegulatorSpec

namespace ANSE.DyadicNavierStokesRegulator

/-- Pointwise bridge: `(k n)^2 * a n * NL k a n = prodIn k a n - prodOut k a n`. -/
lemma enstrophyTerm_eq (k a : ℕ → ℝ) (n : ℕ) :
    (k n) ^ 2 * a n * NL k a n = prodIn k a n - prodOut k a n := by
  cases n with
  | zero => unfold NL prodIn prodOut; ring
  | succ m => unfold NL prodIn prodOut; ring

/-- Under general ratio scaling `k (n + 1) = r * k n`, `prodIn (n + 1) = r^2 * prodOut n`. -/
lemma prodIn_succ_eq_ratio_sq_mul_prodOut (k a : ℕ → ℝ) (r : ℝ) (n : ℕ)
    (hratio : k (n + 1) = r * k n) :
    prodIn k a (n + 1) = r ^ 2 * prodOut k a n := by
  show (k (n + 1)) ^ 2 * a (n + 1) * (k n) * (a n) ^ 2 = r ^ 2 * prodOut k a n
  unfold prodOut
  rw [hratio]
  ring

/-- Summed ratio scaling lemma: `∑_{n≤N} prodIn n = r^2 ∑_{n<N} prodOut n`. -/
lemma sum_prodIn_eq_ratio_sq_mul_sum_prodOut (k a : ℕ → ℝ) (r : ℝ) (N : ℕ)
    (hratio : ∀ n, n < N → k (n + 1) = r * k n) :
    (Finset.range (N + 1)).sum (fun n => prodIn k a n) =
      r ^ 2 * (Finset.range N).sum (fun n => prodOut k a n) := by
  rw [Finset.sum_range_succ' (fun n => prodIn k a n) N]
  have h0 : prodIn k a 0 = 0 := rfl
  rw [h0, add_zero, Finset.mul_sum]
  refine Finset.sum_congr rfl ?_
  intro i hi
  exact prodIn_succ_eq_ratio_sq_mul_prodOut k a r i (hratio i (Finset.mem_range.mp hi))

/-- Theorem 1 (`H1` — Proved): General ratio-`r` enstrophy production identity with coefficient `r^2 - 1`. -/
theorem thm_general_ratio_enstrophy_production : Spec_thm_general_ratio_enstrophy_production := by
  intro k a r N hratio hbc
  have hL : (Finset.range (N + 1)).sum (fun n => (k n) ^ 2 * a n * NL k a n) =
      (Finset.range (N + 1)).sum (fun n => prodIn k a n - prodOut k a n) :=
    Finset.sum_congr rfl (fun n _ => enstrophyTerm_eq k a n)
  have hR : (Finset.range N).sum (fun n => (k n) ^ 3 * (a n) ^ 2 * a (n + 1)) =
      (Finset.range N).sum (fun n => prodOut k a n) :=
    Finset.sum_congr rfl (fun _ _ => rfl)
  rw [hL, hR]
  have hN : prodOut k a N = 0 := by
    unfold prodOut; rw [hbc]; ring
  rw [Finset.sum_sub_distrib, sum_prodIn_eq_ratio_sq_mul_sum_prodOut k a r N hratio,
      Finset.sum_range_succ (fun n => prodOut k a n) N, hN, add_zero]
  ring

/-- Theorem 2 (`H2a` — Proved): Exact dyadic shifted-flux identity and sharp bound `≤ Ω_N / 2`. -/
theorem thm_dyadic_step1_flux_bound_half : Spec_thm_dyadic_step1_flux_bound_half := by
  intro k a N hdouble
  have key : (Finset.range N).sum (fun n => (k n) ^ 2 * (a (n + 1)) ^ 2) =
      (1 / 4 : ℝ) * (Finset.range N).sum (fun n => (k (n + 1)) ^ 2 * (a (n + 1)) ^ 2) := by
    rw [Finset.mul_sum]
    refine Finset.sum_congr rfl ?_
    intro i hi
    rw [hdouble i (Finset.mem_range.mp hi)]
    ring
  have hsplit : (Finset.range (N + 1)).sum (fun n => (k n) ^ 2 * (a n) ^ 2) =
      (Finset.range N).sum (fun n => (k (n + 1)) ^ 2 * (a (n + 1)) ^ 2) + (k 0) ^ 2 * (a 0) ^ 2 :=
    Finset.sum_range_succ' (fun n => (k n) ^ 2 * (a n) ^ 2) N
  have h0 : (0 : ℝ) ≤ (k 0) ^ 2 * (a 0) ^ 2 := mul_nonneg (sq_nonneg _) (sq_nonneg _)
  unfold Omega
  rw [key, hsplit]
  constructor
  · ring
  · linarith

/-- Helper lemma: quartic sum bound `∑_{n<N} k_n^4 a_n^4 ≤ 4 Ω_N^2`. -/
lemma step2_quartic_bound (k a : ℕ → ℝ) (N : ℕ) :
    (Finset.range N).sum (fun n => (k n) ^ 4 * (a n) ^ 4) ≤ 4 * (Omega k a N) ^ 2 := by
  have hnn : ∀ i, (0 : ℝ) ≤ (k i) ^ 4 * (a i) ^ 4 := by
    intro i
    have h : (k i) ^ 4 * (a i) ^ 4 = ((k i) ^ 2 * (a i) ^ 2) ^ 2 := by ring
    rw [h]; exact sq_nonneg _
  have hsubset : Finset.range N ⊆ Finset.range (N + 1) := by
    intro x hx
    rw [Finset.mem_range] at hx ⊢
    exact Nat.lt_succ_of_lt hx
  have hsub : (Finset.range N).sum (fun n => (k n) ^ 4 * (a n) ^ 4) ≤
      (Finset.range (N + 1)).sum (fun n => (k n) ^ 4 * (a n) ^ 4) :=
    Finset.sum_le_sum_of_subset_of_nonneg hsubset (fun i _ _ => hnn i)
  have hx : ∀ i ∈ Finset.range (N + 1), (0 : ℝ) ≤ (k i) ^ 2 * (a i) ^ 2 :=
    fun i _ => mul_nonneg (sq_nonneg _) (sq_nonneg _)
  have hCS := Finset.sum_sq_le_sq_sum_of_nonneg
      (s := Finset.range (N + 1)) (f := fun n => (k n) ^ 2 * (a n) ^ 2) hx
  have hEq : (Finset.range (N + 1)).sum (fun n => (k n) ^ 4 * (a n) ^ 4) =
      (Finset.range (N + 1)).sum (fun n => ((k n) ^ 2 * (a n) ^ 2) ^ 2) :=
    Finset.sum_congr rfl (fun i _ => by ring)
  have hRHS : ((Finset.range (N + 1)).sum (fun n => (k n) ^ 2 * (a n) ^ 2)) ^ 2 =
      4 * (Omega k a N) ^ 2 := by
    unfold Omega; ring
  rw [hEq] at hsub
  have htrans := le_trans hsub hCS
  rw [hRHS] at htrans
  exact htrans

/-- Helper lemma: Cauchy–Schwarz on `f_n = k_n^2 a_n^2` and `g_n = k_n a_{n+1}`. -/
lemma step3_cauchy_schwarz (k a : ℕ → ℝ) (N : ℕ) :
    ((Finset.range N).sum (fun n => (k n) ^ 3 * (a n) ^ 2 * a (n + 1))) ^ 2 ≤
      ((Finset.range N).sum (fun n => (k n) ^ 4 * (a n) ^ 4)) *
        ((Finset.range N).sum (fun n => (k n) ^ 2 * (a (n + 1)) ^ 2)) := by
  have h := Finset.sum_mul_sq_le_sq_mul_sq (Finset.range N)
      (fun n => (k n) ^ 2 * (a n) ^ 2) (fun n => (k n) * a (n + 1))
  have e1 : (Finset.range N).sum (fun n => (k n) ^ 3 * (a n) ^ 2 * a (n + 1)) =
      (Finset.range N).sum (fun n => ((k n) ^ 2 * (a n) ^ 2) * ((k n) * a (n + 1))) :=
    Finset.sum_congr rfl (fun i _ => by ring)
  rw [e1]
  refine le_trans h (le_of_eq ?_)
  congr 1
  · exact Finset.sum_congr rfl (fun i _ => by ring)
  · exact Finset.sum_congr rfl (fun i _ => by ring)

/-- Theorem 3 (`H3` — Proved): Unconditional local cubic enstrophy production bound `S_N^2 ≤ 2 Ω_N^3`. -/
theorem thm_dyadic_local_enstrophy_production_bound : Spec_thm_dyadic_local_enstrophy_production_bound := by
  intro k a N hdouble
  have h3 := step3_cauchy_schwarz k a N
  have h2 := step2_quartic_bound k a N
  have h1 := (thm_dyadic_step1_flux_bound_half k a N hdouble).2
  have hg : (0 : ℝ) ≤ (Finset.range N).sum (fun n => (k n) ^ 2 * (a (n + 1)) ^ 2) :=
    Finset.sum_nonneg (fun i _ => mul_nonneg (sq_nonneg _) (sq_nonneg _))
  have hb : (0 : ℝ) ≤ 4 * (Omega k a N) ^ 2 := by
    have := sq_nonneg (Omega k a N); linarith
  have hmul := mul_le_mul h2 h1 hg hb
  have hring : (4 * (Omega k a N) ^ 2) * (Omega k a N / 2) = 2 * (Omega k a N) ^ 3 := by ring
  rw [hring] at hmul
  exact le_trans h3 hmul

/-- Theorem 4 (`H4` — Proved): Fractional dissipation Riccati exponent collapse and `α ≥ 1/2` threshold. -/
theorem thm_riccati_exponent_chain_and_threshold : Spec_thm_riccati_exponent_chain_and_threshold := by
  intro a ha h3
  have ha_ne : a ≠ 0 := ne_of_gt ha
  have h_rho_div : rhoExp a = (3 * a - 1) / a := by
    unfold rhoExp; field_simp
  have h_rho_ne : rhoExp a ≠ 0 := by
    rw [h_rho_div]; exact div_ne_zero h3 ha_ne
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
  · unfold pExp qExp; ring
  · unfold pExp rhoExp; ring
  · unfold rExp qExp pExp
    have h_denom : 2 - (1 / a - 1) = (3 * a - 1) / a := by field_simp; ring
    rw [h_denom]
    field_simp
    ring
  · have h_two : 2 - pExp a = rhoExp a := by unfold pExp rhoExp; ring
    have h_q : qExp a = rhoExp a + 1 := by unfold qExp rhoExp; ring
    unfold sExp rExp
    rw [h_two, h_q]
    field_simp
    ring
  · unfold pExp
    rw [sub_lt_iff_lt_add, div_lt_iff₀ ha, div_lt_iff₀ (by norm_num : (0 : ℝ) < 3)]
    constructor <;> intro h <;> linarith
  · unfold rhoExp
    constructor
    · intro h
      have h1 : 1 / a ≤ 2 := by linarith
      rw [div_le_iff₀ ha] at h1
      linarith
    · intro h
      have h1 : 1 / a ≤ 2 := by
        rw [div_le_iff₀ ha]
        linarith
      linarith

/-- Graded weight cancellation lemma: `gWeight n * kDyadic n = 1`. -/
lemma gWeight_mul_kDyadic (n : ℕ) : gWeight n * kDyadic n = 1 := by
  unfold gWeight kDyadic
  rw [← mul_pow]
  norm_num

/-- At `σ = 3`, `gWeight n * (D * kDyadic n ^ 3) = D * kDyadic n ^ 2`. -/
lemma sigma_three_weight_eq (D : ℝ) (n : ℕ) :
    gWeight n * (D * kDyadic n ^ 3) = D * kDyadic n ^ 2 := by
  have h1 := gWeight_mul_kDyadic n
  calc gWeight n * (D * kDyadic n ^ 3)
      = D * ((gWeight n * kDyadic n) * kDyadic n ^ 2) := by ring
    _ = D * (1 * kDyadic n ^ 2) := by rw [h1]
    _ = D * kDyadic n ^ 2 := by ring

/-- Theorem 5 (`H7` — Proved): Cutoff-uniform enstrophy bound for the `σ = 3` dispersive regulator. -/
theorem thm_sigma_three_cutoff_uniform_enstrophy_bound :
    Spec_thm_sigma_three_cutoff_uniform_enstrophy_bound := by
  intro D M_inf Hval sqNorm cubTerm N hsq hcub hM hH
  have h_quad : (Finset.range (N + 2)).sum (fun n => (gWeight n * (D * kDyadic n ^ 3)) * sqNorm n) =
      (Finset.range (N + 2)).sum (fun n => (D * kDyadic n ^ 2) * sqNorm n) := by
    refine Finset.sum_congr rfl (fun n _ => ?_)
    rw [sigma_three_weight_eq D n]
  have h_cub_abs :
      |(Finset.range (N + 1)).sum (fun n => (gWeight n * kDyadic n) * cubTerm n)| ≤
        M_inf * (Finset.range (N + 2)).sum (fun n => sqNorm n) := by
    have h_step1 :
        |(Finset.range (N + 1)).sum (fun n => (gWeight n * kDyadic n) * cubTerm n)| ≤
          (Finset.range (N + 1)).sum (fun n => |(gWeight n * kDyadic n) * cubTerm n|) :=
      Finset.abs_sum_le_sum_abs _ _
    have h_step2 :
        (Finset.range (N + 1)).sum (fun n => |(gWeight n * kDyadic n) * cubTerm n|) ≤
          (Finset.range (N + 1)).sum (fun n => M_inf * sqNorm n) := by
      refine Finset.sum_le_sum (fun n _ => ?_)
      rw [gWeight_mul_kDyadic n, one_mul]
      exact hcub n
    have h_step3 :
        (Finset.range (N + 1)).sum (fun n => M_inf * sqNorm n) =
          M_inf * (Finset.range (N + 1)).sum (fun n => sqNorm n) := by
      rw [Finset.mul_sum]
    have h_step4 :
        M_inf * (Finset.range (N + 1)).sum (fun n => sqNorm n) ≤
          M_inf * (Finset.range (N + 2)).sum (fun n => sqNorm n) := by
      refine mul_le_mul_of_nonneg_left ?_ hM
      rw [Finset.sum_range_succ _ (N + 1)]
      linarith [hsq (N + 1)]
    linarith
  have h_neg := neg_abs_le ((Finset.range (N + 1)).sum (fun n => (gWeight n * kDyadic n) * cubTerm n))
  linarith

/-- Theorem 6 (`H9a` — Proved): Discrete `Sym^2` Clausen recurrence and spectral elementary symmetric functions. -/
theorem thm_sym2_clausen_recurrence_and_spectral_lock :
    Spec_thm_sym2_clausen_recurrence_and_spectral_lock := by
  constructor
  · intro a b u hu n
    have h1 : u (n + 2) = a * u (n + 1) + b * u n := hu n
    have h2 : u (n + 3) = a * u (n + 2) + b * u (n + 1) := hu (n + 1)
    rw [h2, h1]
    ring
  · intro a b lam mu hsum hprod
    subst hsum
    refine ⟨by nlinarith [hprod], ?_⟩
    rw [show lam ^ 2 * (lam * mu) * mu ^ 2 = (lam * mu) ^ 3 by ring, hprod]
    ring

/-- Theorem 7 (`H9b` — Proved): T-dual effective radius invariance and self-dual lower barrier. -/
theorem thm_tdual_effective_radius_self_dual_barrier :
    Spec_thm_tdual_effective_radius_self_dual_barrier := by
  intro α R hα hR
  have hdiv : 0 < α / R := div_pos hα hR
  have hmax : 0 < Reff α R := lt_of_lt_of_le hR (le_max_left _ _)
  refine ⟨?_, ?_, ?_⟩
  · have h_inv : α / (α / R) = R := by field_simp
    unfold Reff
    rw [h_inv, max_comm]
  · have h1 : R * (α / R) ≤ Reff α R * Reff α R :=
      mul_le_mul (le_max_left _ _) (le_max_right _ _) hdiv.le hmax.le
    have h2 : R * (α / R) = α := by field_simp
    calc α = R * (α / R) := h2.symm
      _ ≤ Reff α R * Reff α R := h1
      _ = (Reff α R) ^ 2 := by ring
  · intro hne
    rcases lt_or_gt_of_ne hne with hlt | hgt
    · have h_lt_div : R < α / R := by
        rw [lt_div_iff₀ hR]
        nlinarith
      have h_eq : Reff α R = α / R := max_eq_right h_lt_div.le
      rw [h_eq]
      have h_sq : α * R ^ 2 < α ^ 2 := by nlinarith
      have h_R2 : 0 < R ^ 2 := sq_pos_of_pos hR
      rw [div_pow, lt_div_iff₀ h_R2]
      exact h_sq
    · have h_le_div : α / R ≤ R := by
        rw [div_le_iff₀ hR]
        nlinarith
      have h_eq : Reff α R = R := max_eq_left h_le_div
      rw [h_eq]
      exact hgt

/-- Theorem 8 (`H10a` — Proved): Toroidal 2-section degree identity and odd-sector normalized Laplacian eigenvalue. -/
theorem thm_torus_two_section_spectral_degree_identity :
    Spec_thm_torus_two_section_spectral_degree_identity := by
  intro n hn
  have hdeg_eq : 6 * (n - 2) + 4 = 6 * n - 8 := by ring
  have hdeg_pos : 0 < 6 * (n - 2) + 4 := by linarith
  have hdeg_ne : 6 * n - 8 ≠ 0 := by linarith
  refine ⟨hdeg_eq, hdeg_pos, ?_, ?_⟩
  · show 1 - (-4 : ℝ) / (6 * (n - 2) + 4) = (6 * n - 4) / (6 * n - 8)
    rw [hdeg_eq]
    field_simp
    ring
  · show 1 < 1 - (-4 : ℝ) / (6 * (n - 2) + 4)
    rw [hdeg_eq]
    have h_pos2 : 0 < 6 * n - 8 := by linarith
    have h_div : 0 < 4 / (6 * n - 8) := div_pos (by norm_num) h_pos2
    have h_sign : 1 - (-4 : ℝ) / (6 * n - 8) = 1 + 4 / (6 * n - 8) := by ring
    linarith

/-- Theorem 9 (`H2b` — Formally Refuted Conjecture): Refutation of the `Ω_N / 4` shifted-flux bound
and refutation of the dyadic coefficient `3` on arithmetic wavenumbers `k_n = n + 1`. -/
theorem thm_dyadic_flux_bound_quarter_refuted : Spec_thm_dyadic_flux_bound_quarter_refuted := by
  have h_flux : (Finset.range 2).sum (fun n => (kDyadic n) ^ 2 * (aWit (n + 1)) ^ 2) = 40 := by
    rw [Finset.sum_range_succ, Finset.sum_range_succ, Finset.sum_range_zero]
    unfold kDyadic aWit
    norm_num
  have h_om : Omega kDyadic aWit 2 = 161 / 2 := by
    unfold Omega
    rw [Finset.sum_range_succ, Finset.sum_range_succ, Finset.sum_range_succ, Finset.sum_range_zero]
    unfold kDyadic aWit
    norm_num
  have h_refute : ¬ ((Finset.range 2).sum (fun n => (kDyadic n) ^ 2 * (aWit (n + 1)) ^ 2) ≤ Omega kDyadic aWit 2 / 4) := by
    rw [h_flux, h_om]
    norm_num
  have h_arith_lhs : (Finset.range 3).sum (fun n => prodIn kArith aUnit n - prodOut kArith aUnit n) = 13 := by
    rw [Finset.sum_range_succ, Finset.sum_range_succ, Finset.sum_range_succ, Finset.sum_range_zero]
    unfold prodIn prodOut kArith aUnit
    norm_num
  have h_arith_rhs : 3 * (Finset.range 2).sum (fun n => prodOut kArith aUnit n) = 27 := by
    rw [Finset.sum_range_succ, Finset.sum_range_succ, Finset.sum_range_zero]
    unfold prodOut kArith aUnit
    norm_num
  exact ⟨h_flux, h_om, h_refute, h_arith_lhs, h_arith_rhs⟩

/-- Theorem 10 (`H5` — Formally Obstructed Conjecture): Open-band `α ∈ (1/3, 1/2)` Riccati obstruction
and exact `Δθ = 2` integrability deficit at the 3D-NSE-equivalent exponent `α = 2/5`. -/
theorem thm_cheskidov_ns3d_equivalent_obstruction : Spec_thm_cheskidov_ns3d_equivalent_obstruction := by
  refine ⟨?_, ?_, ?_, ?_, ?_⟩
  · intro a h13 h12
    have ha : 0 < a := by linarith
    have h_rho_pos : 0 < rhoExp a := by
      unfold rhoExp
      rw [sub_pos, div_lt_iff₀ ha]
      linarith
    have h_rho_lt_one : rhoExp a < 1 := by
      unfold rhoExp
      have h_gt_two : 2 < 1 / a := by
        rw [lt_div_iff₀ ha]
        linarith
      linarith
    have h_theta_gt_two : 2 < thetaStar a := by
      unfold thetaStar
      rw [lt_div_iff₀ h_rho_pos]
      linarith
    exact ⟨h_rho_pos, h_rho_lt_one, h_theta_gt_two⟩
  · unfold rhoExp; norm_num
  · unfold rExp qExp pExp; norm_num
  · unfold thetaStar rhoExp; norm_num
  · unfold thetaStar rhoExp; norm_num

/-- Theorem 11 (`H6` — Unit-Energy Sphere Coercive Threshold & Supercritical Reynolds Obstruction):
On the normalized unit-energy sphere `2 E_1 = a_0^2 + a_1^2 = 1` with Pythagorean positive-cone witness
`a_0 = 15/17, a_1 = 8/17`, `3 S_1 - ν D_{1/2, 1} < 0` at `ν = 1`, whereas at `ν = 1/3` (`Re = 3`),
`3 S_1 - ν D_{1/2, 1} = 3671 / 14739 > 0` on the unit energy sphere. -/
theorem thm_single_step_coercive_damping_counterexample :
    Spec_thm_single_step_coercive_damping_counterexample := by
  unfold Spec_thm_single_step_coercive_damping_counterexample
  have h_nonneg : ∀ n : ℕ, (0 : ℝ) ≤ (if n = 0 then (15 : ℝ) / 17 else if n = 1 then 8 / 17 else 0) := by
    intro n
    split_ifs <;> norm_num
  have h_E1 : (Finset.range 2).sum (fun n =>
      (if n = 0 then (15 : ℝ) / 17 else if n = 1 then 8 / 17 else 0) ^ 2) = 1 := by
    rw [Finset.sum_range_succ, Finset.sum_range_succ, Finset.sum_range_zero]
    norm_num
  have h_S1 : 3 * (Finset.range 1).sum (fun n => (kDyadic n) ^ 3 *
      (if n = 0 then (15 : ℝ) / 17 else if n = 1 then 8 / 17 else 0) ^ 2 *
      (if n + 1 = 0 then 15 / 17 else if n + 1 = 1 then 8 / 17 else 0)) = 5400 / 4913 := by
    rw [Finset.sum_range_succ, Finset.sum_range_zero]
    unfold kDyadic
    norm_num
  have h_D1 : (Finset.range 2).sum (fun n => (kDyadic n) ^ 3 *
      (if n = 0 then (15 : ℝ) / 17 else if n = 1 then 8 / 17 else 0) ^ 2) = 12529 / 4913 := by
    rw [Finset.sum_range_succ, Finset.sum_range_succ, Finset.sum_range_zero]
    unfold kDyadic
    norm_num
  refine ⟨h_nonneg, h_E1, h_S1, h_D1, by linarith, by linarith⟩

/-- Theorem 12 (`H8` & `H10b` — Formally Obstructed/Refuted Conjectures):
(a) Unbounded `2^N` enstrophy-to-Hamiltonian weight gap at `σ = 2` (Gross–Pitaevskii quantum pressure);
(b) Exact parity amputation (`|k_1 + k_2|^2 % 2 = 0`) of resonant triads in the odd-norm-square shell on `ℤ^3`. -/
theorem thm_sigma_two_and_odd_parity_obstructions :
    Spec_thm_sigma_two_and_odd_parity_obstructions := by
  constructor
  · intro D N hD
    unfold gWeight kDyadic
    have hk : (2 : ℝ) ^ N ≠ 0 := pow_ne_zero N (by norm_num)
    have hhalf : (1 / 2 : ℝ) ^ N ≠ 0 := pow_ne_zero N (by norm_num)
    have hX : D * ((2 : ℝ) ^ N) ^ 2 ≠ 0 := mul_ne_zero hD (pow_ne_zero 2 hk)
    have h_denom : (1 / 2 : ℝ) ^ N * (D * ((2 : ℝ) ^ N) ^ 2) ≠ 0 := mul_ne_zero hhalf hX
    have h_prod : (1 / 2 : ℝ) ^ N * (2 : ℝ) ^ N = 1 := by
      rw [← mul_pow]; norm_num
    rw [div_eq_iff h_denom]
    linear_combination -(D * ((2 : ℝ) ^ N) ^ 2) * h_prod
  · intro x1 y1 z1 x2 y2 z2
    have h_alg : normSqZ3 (x1 + x2) (y1 + y2) (z1 + z2) =
        normSqZ3 x1 y1 z1 + normSqZ3 x2 y2 z2 + 2 * (x1 * x2 + y1 * y2 + z1 * z2) := by
      unfold normSqZ3
      ring
    refine ⟨h_alg, ?_⟩
    intro h1 h2
    rw [h_alg]
    omega

-- Environment-level Definitional Equality Checks against Read-Only Spec (`Spec.lean`)
example : Spec_thm_general_ratio_enstrophy_production := thm_general_ratio_enstrophy_production
example : Spec_thm_dyadic_step1_flux_bound_half := thm_dyadic_step1_flux_bound_half
example : Spec_thm_dyadic_local_enstrophy_production_bound := thm_dyadic_local_enstrophy_production_bound
example : Spec_thm_riccati_exponent_chain_and_threshold := thm_riccati_exponent_chain_and_threshold
example : Spec_thm_sigma_three_cutoff_uniform_enstrophy_bound := thm_sigma_three_cutoff_uniform_enstrophy_bound
example : Spec_thm_sym2_clausen_recurrence_and_spectral_lock := thm_sym2_clausen_recurrence_and_spectral_lock
example : Spec_thm_tdual_effective_radius_self_dual_barrier := thm_tdual_effective_radius_self_dual_barrier
example : Spec_thm_torus_two_section_spectral_degree_identity := thm_torus_two_section_spectral_degree_identity
example : Spec_thm_dyadic_flux_bound_quarter_refuted := thm_dyadic_flux_bound_quarter_refuted
example : Spec_thm_cheskidov_ns3d_equivalent_obstruction := thm_cheskidov_ns3d_equivalent_obstruction
example : Spec_thm_single_step_coercive_damping_counterexample := thm_single_step_coercive_damping_counterexample
example : Spec_thm_sigma_two_and_odd_parity_obstructions := thm_sigma_two_and_odd_parity_obstructions

#print axioms enstrophyTerm_eq
#print axioms prodIn_succ_eq_ratio_sq_mul_prodOut
#print axioms sum_prodIn_eq_ratio_sq_mul_sum_prodOut
#print axioms step2_quartic_bound
#print axioms step3_cauchy_schwarz
#print axioms gWeight_mul_kDyadic
#print axioms sigma_three_weight_eq
#print axioms thm_general_ratio_enstrophy_production
#print axioms thm_dyadic_step1_flux_bound_half
#print axioms thm_dyadic_local_enstrophy_production_bound
#print axioms thm_riccati_exponent_chain_and_threshold
#print axioms thm_sigma_three_cutoff_uniform_enstrophy_bound
#print axioms thm_sym2_clausen_recurrence_and_spectral_lock
#print axioms thm_tdual_effective_radius_self_dual_barrier
#print axioms thm_torus_two_section_spectral_degree_identity
#print axioms thm_dyadic_flux_bound_quarter_refuted
#print axioms thm_cheskidov_ns3d_equivalent_obstruction
#print axioms thm_single_step_coercive_damping_counterexample
#print axioms thm_sigma_two_and_odd_parity_obstructions

end ANSE.DyadicNavierStokesRegulator
