/-
Autoresearch 2026-10-25, H8: the Bogoliubov structure factor obeys the dual-scale bound
`S_B(k) ≤ √(k/(2ks))` (docs/DUAL_SCALE_PROPOSAL.md, DS-QF′ "Structure factor" item).

Variables follow lean_src/DualLength.lean: `hc = ħc`, `ks = k* = 2mc/ħ`, free-particle energy
`ε₀(k) = ħ²k²/2m = hc·k²/ks`, Bogoliubov `ε_B(k) = √((hc k)² + (hc k²/ks)²) = √(ε₀(ε₀ + 2gn))`,
and the Bijl–Feynman structure factor `S_B = ε₀/ε_B`.

Already in the project (NOT re-proved here): `feynman_ge_iff` (ℓ_F ≥ 2/ks ↔ S² ≤ k/(2ks) for any
S > 0), `bogoliubov_envelope`, `not_bogoliubov_of_structure_factor`. What is new in this file is the
explicit statement about the Bogoliubov `S_B` itself: closed form, the bound, its sharpness
(equality exactly at k = ks), the Bijl–Feynman exactness that links it to `feynman_ge_iff`, and a
negative control (S ≡ 1, the free/ideal-gas value, violates the bound for every k < 2ks).
-/

import DualLength

namespace QuantumFluids.AutoresearchSkBound

open QuantumFluids.DualLength

/-- Free-particle energy `ε₀ = ħ²k²/2m = hc·k²/ks`. -/
noncomputable def epsFree (hc ks k : ℝ) : ℝ := hc * k ^ 2 / ks

/-- Bogoliubov energy `ε_B = √((hc k)² + (hc k²/ks)²)`. -/
noncomputable def epsBog (hc ks k : ℝ) : ℝ := Real.sqrt (bogoliubovSq hc ks k)

/-- Bijl–Feynman structure factor of the Bogoliubov gas, `S_B = ε₀/ε_B`. -/
noncomputable def sBog (hc ks k : ℝ) : ℝ := epsFree hc ks k / epsBog hc ks k

theorem bogoliubovSq_pos {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) :
    0 < bogoliubovSq hc ks k := by
  unfold bogoliubovSq; positivity

/-- `ε_B² = ε₀(ε₀ + 2gn)` form check: `ε_B² = ε₀² + (hc k)²`, i.e. `2gn·ε₀ = (hc k)²`. -/
theorem epsBog_sq {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) :
    epsBog hc ks k ^ 2 = epsFree hc ks k ^ 2 + (hc * k) ^ 2 := by
  unfold epsBog epsFree
  rw [Real.sq_sqrt (bogoliubovSq_pos hhc hk).le]
  unfold bogoliubovSq; ring

theorem sBog_pos {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    0 < sBog hc ks k := by
  unfold sBog epsFree epsBog
  have := Real.sqrt_pos.mpr (bogoliubovSq_pos (ks := ks) hhc hk)
  positivity

/-- Closed form: `S_B² = k²/(ks² + k²)` (independent of `hc`). -/
theorem sBog_sq {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k ^ 2 = k ^ 2 / (ks ^ 2 + k ^ 2) := by
  unfold sBog epsBog epsFree
  rw [div_pow, Real.sq_sqrt (bogoliubovSq_pos hhc hk).le]
  unfold bogoliubovSq
  have h1 : hc ≠ 0 := ne_of_gt hhc
  have h2 : k ≠ 0 := ne_of_gt hk
  have h3 : ks ≠ 0 := ne_of_gt hks
  have h4 : ks ^ 2 + k ^ 2 ≠ 0 := by positivity
  field_simp
  ring_nf

/-- **H8, squared form.** `S_B(k)² ≤ k/(2ks)` for every `k > 0`. -/
theorem sBog_sq_le {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k ^ 2 ≤ k / (2 * ks) := by
  rw [sBog_sq hhc hk hks, div_le_div_iff₀ (by positivity) (by positivity)]
  nlinarith [mul_nonneg hk.le (sq_nonneg (k - ks))]

/-- **H8.** `S_B(k) ≤ √(k/(2ks))`: the Bogoliubov structure factor sits under the dual-scale bound. -/
theorem sBog_le_sqrt {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k ≤ Real.sqrt (k / (2 * ks)) := by
  rw [← Real.sqrt_sq (sBog_pos hhc hk hks).le]
  exact Real.sqrt_le_sqrt (sBog_sq_le hhc hk hks)

/-- **Sharpness.** Equality holds exactly at the self-dual wavenumber `k = ks`. -/
theorem sBog_sq_eq_iff {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k ^ 2 = k / (2 * ks) ↔ k = ks := by
  rw [sBog_sq hhc hk hks, div_eq_div_iff (by positivity) (by positivity)]
  constructor
  · intro h
    have h' : k * (k - ks) ^ 2 = 0 := by linear_combination (-1 : ℝ) * h
    rcases mul_eq_zero.mp h' with h0 | h0
    · exact absurd h0 (ne_of_gt hk)
    · have := pow_eq_zero_iff (n := 2) (by norm_num) |>.mp h0
      linarith
  · intro h; subst h; ring

/-- **Bijl–Feynman is exact for Bogoliubov.** The Feynman energy built from `S_B` is `ε_B`, so the
project's `feynman_ge_iff` applies to `S_B` with equality in Feynman's variational inequality. -/
theorem feynman_sBog_exact {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    (hc * k ^ 2 / (ks * sBog hc ks k)) ^ 2 = bogoliubovSq hc ks k := by
  have hS := sBog_pos hhc hk hks
  have hsq := sBog_sq hhc hk hks
  have h3 : ks ≠ 0 := ne_of_gt hks
  rw [div_pow, mul_pow, hsq]
  unfold bogoliubovSq
  have h4 : ks ^ 2 + k ^ 2 ≠ 0 := by positivity
  have h2 : k ≠ 0 := ne_of_gt hk
  field_simp
  ring_nf

/-- Consistency with the project: `sBog_sq_le` is also obtained through `feynman_ge_iff`
and `ell_ge`, i.e. the bound on `S_B` is the dual-scale bound `ℓ ≥ 2/ks` read through Feynman. -/
theorem sBog_sq_le_via_project {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k ^ 2 ≤ k / (2 * ks) := by
  have hS := sBog_pos hhc hk hks
  refine (feynman_ge_iff hk hks hS).mp ?_
  rw [← dualLength_feynman (ne_of_gt hhc) (ne_of_gt hk) (ne_of_gt hks) (ne_of_gt hS),
    feynman_sBog_exact hhc hk hks, dualLength_bogoliubov (ne_of_gt hhc) (ne_of_gt hk) (ne_of_gt hks)]
  exact ell_ge hk hks

/-- **Negative control (free particle / ideal gas, `S ≡ 1`).** For every `0 < k < 2ks` the value
`S = 1` violates the bound, so the inequality is specific to the interacting (Bogoliubov) gas. -/
theorem free_S_one_violates {ks k : ℝ} (hk : 0 < k) (hks : 0 < ks) (hlt : k < 2 * ks) :
    Real.sqrt (k / (2 * ks)) < 1 := by
  rw [Real.sqrt_lt' one_pos, one_pow, div_lt_one (by positivity)]
  exact hlt

/-- Negative control, pointwise at the self-dual point: `S = 1` fails `S ≤ √(k/(2ks))` at `k = ks`. -/
theorem free_S_one_not_le_at_selfdual {ks : ℝ} (hks : 0 < ks) :
    ¬ ((1 : ℝ) ≤ Real.sqrt (ks / (2 * ks))) :=
  not_le.mpr (free_S_one_violates hks hks (by linarith))

end QuantumFluids.AutoresearchSkBound

#print axioms QuantumFluids.AutoresearchSkBound.bogoliubovSq_pos
#print axioms QuantumFluids.AutoresearchSkBound.epsBog_sq
#print axioms QuantumFluids.AutoresearchSkBound.sBog_pos
#print axioms QuantumFluids.AutoresearchSkBound.sBog_sq
#print axioms QuantumFluids.AutoresearchSkBound.sBog_sq_le
#print axioms QuantumFluids.AutoresearchSkBound.sBog_le_sqrt
#print axioms QuantumFluids.AutoresearchSkBound.sBog_sq_eq_iff
#print axioms QuantumFluids.AutoresearchSkBound.feynman_sBog_exact
#print axioms QuantumFluids.AutoresearchSkBound.sBog_sq_le_via_project
#print axioms QuantumFluids.AutoresearchSkBound.free_S_one_violates
#print axioms QuantumFluids.AutoresearchSkBound.free_S_one_not_le_at_selfdual
