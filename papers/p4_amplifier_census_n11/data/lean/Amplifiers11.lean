import Programmes.AmplifierCensus.DataA1
import Programmes.AmplifierCensus.DataA2
import Programmes.AmplifierCensus.DataA3

/-!
# The other three connected unweighted N = 11 death-Birth amplifiers of weak selection (C1b, proposal 4)

The exhaustive census C1b (all 1,006,700,565 connected graphs on 11 vertices, nauty `geng -c 11`,
certified integer enclosure + exact Fraction finish) finds exactly four isomorphism classes with
Allen's `N_eff > N`: Richter's quartic-minus-an-edge graph (`R11_amplifier`, C1) and the three below.
They agree with the four graphs of Richter, arXiv 2204.12861v1, Fig. 1 (N_eff printed 11.0952, 11.0128,
11.0056, 11.0008).

* `A1_amplifier` (graph6 ``J?`@`eoRAW?``, 16 edges): `N_eff = 328435957 / 29601736 ≈ 11.095159`.
* `A2_amplifier` (graph6 ``J?`CP_p[C[?``, 16 edges): `N_eff ≈ 11.012785`.
* `A3_amplifier` (graph6 ``J?`@`eoRAW_``, 17 edges): `N_eff ≈ 11.005561`.

Each theorem: every rational solution of Allen eq. (5) on the graph has the stated `N_eff`, which is
`> 11`. Scope: statements about the linear system (Allen eqs. 5, 6, 9) on these adjacencies; the step
`N_eff > N ⇒ amplifier of weak selection` is Allen et al. eq. (8) (literature), not formalised. The
census completeness (that there are no others) is NOT a Lean statement.
-/

namespace AmplifierCensus

theorem GA1_symm : ∀ i j : Fin 11, GA1 i j = GA1 j i := by decide +kernel
theorem GA1_loopless : ∀ i : Fin 11, GA1 i i = false := by decide +kernel
theorem GA1_deg : ∀ i : Fin 11, deg GA1 i = if i = 0 then 2 else 3 := by decide +kernel

theorem tauA1_eq5 : Eq5 GA1 tauA1 := by
  unfold Eq5; decide +kernel

theorem tauA1_pos : ∀ i j : Fin 11, i ≠ j → 0 < tauA1 i j := by decide +kernel

theorem neff_tauA1 : neff GA1 tauA1 = 328435957 / 29601736 := by
  unfold neff remeet; decide +kernel

/-- **`J?`@`eoRAW?` is an amplifier of weak selection (Allen's criterion `N_eff > N`).** -/
theorem A1_amplifier (τ : Fin 11 → Fin 11 → ℚ) (hτ : Eq5 GA1 τ) :
    neff GA1 τ = 328435957 / 29601736 ∧ (11 : ℚ) < neff GA1 τ := by
  rw [neff_of_cert GA1 tauA1 tauA1_eq5 tauA1_pos τ hτ, neff_tauA1]
  exact ⟨rfl, by norm_num⟩

theorem GA2_symm : ∀ i j : Fin 11, GA2 i j = GA2 j i := by decide +kernel
theorem GA2_loopless : ∀ i : Fin 11, GA2 i i = false := by decide +kernel
theorem GA2_deg : ∀ i : Fin 11, deg GA2 i = if i = 1 ∨ i = 5 then 2 else if i = 10 then 4 else 3 := by
  decide +kernel

theorem tauA2_eq5 : Eq5 GA2 tauA2 := by
  unfold Eq5; decide +kernel

theorem tauA2_pos : ∀ i j : Fin 11, i ≠ j → 0 < tauA2 i j := by decide +kernel

theorem neff_tauA2 : neff GA2 tauA2 = 2890154941667179019 / 262436329991601232 := by
  unfold neff remeet; decide +kernel

/-- **`J?`CP_p[C[?` is an amplifier of weak selection.** -/
theorem A2_amplifier (τ : Fin 11 → Fin 11 → ℚ) (hτ : Eq5 GA2 τ) :
    neff GA2 τ = 2890154941667179019 / 262436329991601232 ∧ (11 : ℚ) < neff GA2 τ := by
  rw [neff_of_cert GA2 tauA2 tauA2_eq5 tauA2_pos τ hτ, neff_tauA2]
  exact ⟨rfl, by norm_num⟩

theorem GA3_symm : ∀ i j : Fin 11, GA3 i j = GA3 j i := by decide +kernel
theorem GA3_loopless : ∀ i : Fin 11, GA3 i i = false := by decide +kernel
theorem GA3_deg : ∀ i : Fin 11, deg GA3 i = if i = 0 then 2 else if i = 9 ∨ i = 10 then 4 else 3 := by
  decide +kernel

theorem tauA3_eq5 : Eq5 GA3 tauA3 := by
  unfold Eq5; decide +kernel

theorem tauA3_pos : ∀ i j : Fin 11, i ≠ j → 0 < tauA3 i j := by decide +kernel

theorem neff_tauA3 : neff GA3 tauA3 = 88175846355074579 / 8011935789939084 := by
  unfold neff remeet; decide +kernel

/-- **`J?`@`eoRAW_` is an amplifier of weak selection.** -/
theorem A3_amplifier (τ : Fin 11 → Fin 11 → ℚ) (hτ : Eq5 GA3 τ) :
    neff GA3 τ = 88175846355074579 / 8011935789939084 ∧ (11 : ℚ) < neff GA3 τ := by
  rw [neff_of_cert GA3 tauA3 tauA3_eq5 tauA3_pos τ hτ, neff_tauA3]
  exact ⟨rfl, by norm_num⟩

end AmplifierCensus

#print axioms AmplifierCensus.A1_amplifier
#print axioms AmplifierCensus.A2_amplifier
#print axioms AmplifierCensus.A3_amplifier
