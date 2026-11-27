/-
Autoresearch 2026-10-25, H7: the σ = 3 dispersive regulator gives a cutoff-uniform enstrophy bound
`2DΩ ≤ H₃ + (2E)^{3/2}` (docs/DUAL_SCALE_PROPOSAL.md §7 step 2; PLAN.md "σ = 3 regulator" line).

Model: complexified truncated dyadic shell model (lean_src/QuantumFluidsShell.lean, `shellBc`) on shells
`0..N+1`, `k_n = 2ⁿ`, dispersion `ω_n = D k_n³`. Definitions (index ranges as in `dispersive_norm_le`):
  `S = Σ_{n<N+2} |v_n|²`, `E = S/2`, `Ω = ½ Σ_{n<N+2} k_n² |v_n|²`,
  `H₃ = Σ_{n<N+2} 2⁻ⁿ D k_n³ |v_n|² + Σ_{n<N+1} 2⁻ⁿ k_n Im(conj(v_n)² v_{n+1})`.

WHAT IS PROVED: the pointwise inequality, for every `N`, `v`, real `D`, and the `D > 0` bound on `Ω`.
It is a specialization of the owner's `QuantumFluids.ShellComplex.dispersive_norm_le` (whose docstring names
this case); new here are the faithful σ = 3 definitions, the rpow form and the corollary.

WHAT IS NOT PROVED: that `H₃` is conserved by the σ = 3 flow (the dispersion/cubic cross-term cancellation is
checked exact-symbolically in numeric_gate.py, not in Lean) and the chain rule along solutions. Uniformity in
time of the bound is therefore conditional on those two facts.
-/

import ShellHamiltonian

namespace QuantumFluids.AutoresearchEnstrophy

open QuantumFluids.ShellComplex

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

/-- **σ = 3 cutoff-uniform enstrophy bound (pointwise form).** For every cutoff `N`, every state `v` and every
real `D`: `2DΩ ≤ H₃ + (2E)^{3/2}`. -/
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

/-- **Enstrophy bound with the regulator strength made explicit (`D > 0`).** -/
theorem enstrophy_le (D : ℝ) (hD : 0 < D) (N : ℕ) (v : ℕ → ℂ) :
    enstrophy N v ≤ (ham3 D N v + (2 * energy N v) ^ (3 / 2 : ℝ)) / (2 * D) := by
  rw [le_div_iff₀ (by positivity)]
  have := enstrophy_bound D N v
  linarith

/-- **Negative control: the `(2E)^{3/2}` term cannot be dropped.** With `N = 0`, `v = (1, -i, 0, …)`, `D = 1`:
`2DΩ = 5` but `H₃ = 4`. -/
theorem drop_cubic_term_fails :
    ¬ (2 * 1 * enstrophy 0 (fun n => if n = 0 then (1 : ℂ) else if n = 1 then -Complex.I else 0)
        ≤ ham3 1 0 (fun n => if n = 0 then (1 : ℂ) else if n = 1 then -Complex.I else 0)) := by
  simp [enstrophy, ham3, kk, Finset.sum_range_succ, Complex.normSq_apply]
  norm_num

end QuantumFluids.AutoresearchEnstrophy

#print axioms QuantumFluids.AutoresearchEnstrophy.weight_eq_one
#print axioms QuantumFluids.AutoresearchEnstrophy.disp_weight
#print axioms QuantumFluids.AutoresearchEnstrophy.sqrt_mul_self_eq_rpow
#print axioms QuantumFluids.AutoresearchEnstrophy.enstrophy_bound
#print axioms QuantumFluids.AutoresearchEnstrophy.enstrophy_le
#print axioms QuantumFluids.AutoresearchEnstrophy.drop_cubic_term_fails
