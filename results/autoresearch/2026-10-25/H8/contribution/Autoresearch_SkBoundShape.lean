/-
Autoresearch 2026-10-25, H8 contribution (Stage 1): shape of the Bogoliubov structure factor and the
diffraction test of the weakly interacting regime.

Consolidates the round-1 file `H8/Autoresearch_SkBound.lean` (kept verbatim there; its theorems are
re-proved here under the same names in a new namespace) and adds:

  * `sBog_eq_closed`           : S_B = k / √(ks² + k²)
  * `sBog_strictMonoOn`        : S_B is strictly increasing on k > 0
  * `sBog_lt_phonon`, `phonon_lower_lt_sBog` : k/(ks+k) < S_B < k/ks  (phonon regime, two-sided)
  * `sBog_lt_one`, `one_sub_sBog_le`, `sBog_tendsto_one` : S_B < 1, 1 − S_B ≤ ks²/k², S_B → 1
  * `epsBog_eq_epsFree_div_sBog` : ε_B = ε₀ / S_B (definitional: S_B is defined as ε₀/ε_B)
  * `diffraction_test_model`   : a value S > √(k/2ks) is not the Bogoliubov S_B (unconditional)
  * `diffraction_test_dispersion` : the same peak, GIVEN Feynman's variational inequality
                                    ε² ≤ ε_F[S]², refutes the Bogoliubov dispersion (owner lemma
                                    `not_bogoliubov_of_structure_factor`)
  * in-file controls of the test: it fires on S = 1 at k = ks, it never fires on S_B itself.

Variables follow lean_src/DualLength.lean: `hc = ħc`, `ks = k* = 2mc/ħ`. Model statements only.
-/

import DualLength

namespace QuantumFluids.AutoresearchSkBoundShape

open QuantumFluids.DualLength

/-- Free-particle energy `ε₀ = ħ²k²/2m = hc·k²/ks`. -/
noncomputable def epsFree (hc ks k : ℝ) : ℝ := hc * k ^ 2 / ks

/-- Bogoliubov energy `ε_B = √((hc k)² + (hc k²/ks)²)`. -/
noncomputable def epsBog (hc ks k : ℝ) : ℝ := Real.sqrt (bogoliubovSq hc ks k)

/-- Bijl–Feynman structure factor of the Bogoliubov gas, `S_B = ε₀/ε_B`. -/
noncomputable def sBog (hc ks k : ℝ) : ℝ := epsFree hc ks k / epsBog hc ks k

/-! ## Round-1 theorems (same statements and names as `Autoresearch_SkBound.lean`) -/

theorem bogoliubovSq_pos {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) :
    0 < bogoliubovSq hc ks k := by
  unfold bogoliubovSq; positivity

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

/-- `S_B(k)² ≤ k/(2ks)` for every `k > 0`. -/
theorem sBog_sq_le {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k ^ 2 ≤ k / (2 * ks) := by
  rw [sBog_sq hhc hk hks, div_le_div_iff₀ (by positivity) (by positivity)]
  nlinarith [mul_nonneg hk.le (sq_nonneg (k - ks))]

/-- **H8.** `S_B(k) ≤ √(k/(2ks))`. -/
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

/-- Bijl–Feynman for Bogoliubov: the Feynman energy built from `S_B` is `ε_B`.
Holds by construction, since `S_B` is defined as `ε₀/ε_B`. -/
theorem feynman_sBog_exact {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    (hc * k ^ 2 / (ks * sBog hc ks k)) ^ 2 = bogoliubovSq hc ks k := by
  have hS := sBog_pos hhc hk hks
  have hsq := sBog_sq hhc hk hks
  have h3 : ks ≠ 0 := ne_of_gt hks
  have hden : (ks * sBog hc ks k) ^ 2 = ks ^ 2 * (k ^ 2 / (ks ^ 2 + k ^ 2)) := by
    rw [mul_pow, hsq]
  rw [div_pow, hden]
  unfold bogoliubovSq
  have h4 : ks ^ 2 + k ^ 2 ≠ 0 := by positivity
  have h2 : k ≠ 0 := ne_of_gt hk
  field_simp

/-- The bound through the owner's `feynman_ge_iff` and `ell_ge`. -/
theorem sBog_sq_le_via_project {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k ^ 2 ≤ k / (2 * ks) := by
  have hS := sBog_pos hhc hk hks
  refine (feynman_ge_iff hk hks hS).mp ?_
  rw [← dualLength_feynman (ne_of_gt hhc) (ne_of_gt hk) (ne_of_gt hks) (ne_of_gt hS),
    feynman_sBog_exact hhc hk hks, dualLength_bogoliubov (ne_of_gt hhc) (ne_of_gt hk) (ne_of_gt hks)]
  exact ell_ge hk hks

/-- Negative control: `S ≡ 1` violates the dual-scale bound for every `0 < k < 2ks`. -/
theorem free_S_one_violates {ks k : ℝ} (_hk : 0 < k) (hks : 0 < ks) (hlt : k < 2 * ks) :
    Real.sqrt (k / (2 * ks)) < 1 := by
  rw [Real.sqrt_lt' one_pos, one_pow, div_lt_one (by positivity)]
  exact hlt

/-! ## New: shape theorems -/

/-- Closed form `S_B = k/√(ks² + k²)`. -/
theorem sBog_eq_closed {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k = k / Real.sqrt (ks ^ 2 + k ^ 2) := by
  rw [← Real.sqrt_sq (sBog_pos hhc hk hks).le, sBog_sq hhc hk hks, Real.sqrt_div (sq_nonneg k),
    Real.sqrt_sq hk.le]

/-- Squares are strictly increasing: `0 < a < b → S_B(a)² < S_B(b)²`. -/
theorem sBog_sq_lt_sq {hc ks a b : ℝ} (hhc : 0 < hc) (hks : 0 < ks) (ha : 0 < a) (hab : a < b) :
    sBog hc ks a ^ 2 < sBog hc ks b ^ 2 := by
  have hb : 0 < b := ha.trans hab
  rw [sBog_sq hhc ha hks, sBog_sq hhc hb hks, div_lt_div_iff₀ (by positivity) (by positivity)]
  have hsq : a ^ 2 < b ^ 2 := by nlinarith
  have hks2 : 0 < ks ^ 2 := by positivity
  nlinarith [mul_lt_mul_of_pos_right hsq hks2]

/-- **Monotonicity.** `S_B` is strictly increasing in `k` on `k > 0`. -/
theorem sBog_strictMonoOn {hc ks : ℝ} (hhc : 0 < hc) (hks : 0 < ks) :
    StrictMonoOn (sBog hc ks) (Set.Ioi 0) := by
  intro a ha b hb hab
  have ha' : 0 < a := Set.mem_Ioi.mp ha
  have hb' : 0 < b := Set.mem_Ioi.mp hb
  have h2 := sBog_sq_lt_sq hhc hks ha' hab
  have pa := sBog_pos hhc ha' hks
  have pb := sBog_pos hhc hb' hks
  nlinarith [h2, pa, pb]

/-- **Phonon regime, upper bound.** `S_B < k/ks` for every `k > 0` (`S_B ≈ ħk/2mc` as `k → 0`). -/
theorem sBog_lt_phonon {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k < k / ks := by
  have pS := sBog_pos hhc hk hks
  have hq : 0 < k / ks := div_pos hk hks
  have h2 : sBog hc ks k ^ 2 < (k / ks) ^ 2 := by
    rw [sBog_sq hhc hk hks, div_pow, div_lt_div_iff₀ (by positivity) (by positivity)]
    nlinarith [pow_pos hk 4]
  nlinarith [h2, pS, hq]

/-- **Phonon regime, lower bound.** `k/(ks + k) < S_B`, so `S_B/(k/ks) ∈ (ks/(ks+k), 1)`. -/
theorem phonon_lower_lt_sBog {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    k / (ks + k) < sBog hc ks k := by
  have pS := sBog_pos hhc hk hks
  have hq : 0 < k / (ks + k) := div_pos hk (by positivity)
  have h2 : (k / (ks + k)) ^ 2 < sBog hc ks k ^ 2 := by
    rw [sBog_sq hhc hk hks, div_pow, div_lt_div_iff₀ (by positivity) (by positivity)]
    nlinarith [mul_pos (pow_pos hk 3) hks]
  nlinarith [h2, pS, hq]

/-- **Below the free particle.** `S_B < 1` for every `k > 0`. -/
theorem sBog_lt_one {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k < 1 := by
  have pS := sBog_pos hhc hk hks
  have h2 : sBog hc ks k ^ 2 < 1 := by
    rw [sBog_sq hhc hk hks, div_lt_one (by positivity)]
    nlinarith [pow_pos hks 2]
  nlinarith [h2, pS]

/-- **Approach to the free particle, quantitative.** `1 − S_B ≤ ks²/k²`. -/
theorem one_sub_sBog_le {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    1 - sBog hc ks k ≤ ks ^ 2 / k ^ 2 := by
  have pS := sBog_pos hhc hk hks
  have hS1 := sBog_lt_one hhc hk hks
  have hD : 0 < ks ^ 2 + k ^ 2 := by positivity
  have hk2 : 0 < k ^ 2 := by positivity
  have e : 1 - sBog hc ks k ^ 2 = ks ^ 2 / (ks ^ 2 + k ^ 2) := by
    rw [sBog_sq hhc hk hks, eq_div_iff hD.ne', sub_mul, div_mul_cancel₀ _ hD.ne']
    ring
  have h3 : ks ^ 2 / (ks ^ 2 + k ^ 2) ≤ ks ^ 2 / k ^ 2 := by
    rw [div_le_div_iff₀ hD hk2]
    nlinarith [sq_nonneg (ks ^ 2)]
  nlinarith [e, h3, mul_pos pS (sub_pos.mpr hS1)]

/-- **`S_B → 1` as `k → ∞`** (free-particle limit). -/
theorem sBog_tendsto_one {hc ks : ℝ} (hhc : 0 < hc) (hks : 0 < ks) :
    Filter.Tendsto (sBog hc ks) Filter.atTop (nhds 1) := by
  have h0 : Filter.Tendsto (fun k : ℝ => ks ^ 2 / k ^ 2) Filter.atTop (nhds 0) :=
    (Filter.tendsto_pow_atTop (α := ℝ) two_ne_zero).const_div_atTop (ks ^ 2)
  have hlow : Filter.Tendsto (fun k : ℝ => 1 - ks ^ 2 / k ^ 2) Filter.atTop (nhds 1) := by
    have := (tendsto_const_nhds : Filter.Tendsto (fun _ : ℝ => (1 : ℝ)) Filter.atTop (nhds 1)).sub h0
    simpa using this
  refine tendsto_of_tendsto_of_tendsto_of_le_of_le' hlow tendsto_const_nhds ?_ ?_
  · filter_upwards [Filter.eventually_gt_atTop 0] with k hk
    have := one_sub_sBog_le hhc hk hks
    linarith
  · filter_upwards [Filter.eventually_gt_atTop 0] with k hk
    exact (sBog_lt_one hhc hk hks).le

/-- **`ε_B = ε₀ / S_B`.** Definitional consequence of `S_B := ε₀/ε_B` (both positive). -/
theorem epsBog_eq_epsFree_div_sBog {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    epsBog hc ks k = epsFree hc ks k / sBog hc ks k := by
  have h0 : epsFree hc ks k ≠ 0 := by unfold epsFree; positivity
  have hB : epsBog hc ks k ≠ 0 := (Real.sqrt_pos.mpr (bogoliubovSq_pos (ks := ks) hhc hk)).ne'
  unfold sBog
  rw [div_div_eq_mul_div, mul_comm, mul_div_assoc, div_self h0, mul_one]

/-! ## New: the diffraction test -/

/-- **Diffraction test, model level (unconditional).** A structure-factor value `S` above
`√(k/(2ks))` at some `k > 0` is not the Bogoliubov value `S_B(k)` for that `ks`. -/
theorem diffraction_test_model {hc ks k S : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks)
    (hpeak : Real.sqrt (k / (2 * ks)) < S) : S ≠ sBog hc ks k := by
  intro h
  rw [h] at hpeak
  exact absurd (sBog_le_sqrt hhc hk hks) (not_le.mpr hpeak)

/-- **Diffraction test, dispersion level (conditional on Feynman's variational inequality).**
If the measured `S > √(k/(2ks))` and the true dispersion obeys `ε² ≤ ε_F[S]²` (hypothesis
`hfeyn`, physics input), then the dispersion at `k` is not Bogoliubov. This is the owner lemma
`not_bogoliubov_of_structure_factor` with the peak stated in the `√` form. -/
theorem diffraction_test_dispersion {hc ks k S epsSq : ℝ} (hhc : 0 < hc) (hk : 0 < k)
    (hks : 0 < ks) (hS : 0 < S)
    (hfeyn : epsSq ≤ (hc * k ^ 2 / (ks * S)) ^ 2)
    (hpeak : Real.sqrt (k / (2 * ks)) < S) : epsSq ≠ bogoliubovSq hc ks k :=
  not_bogoliubov_of_structure_factor (ne_of_gt hhc) hk hks hS hfeyn ((Real.sqrt_lt' hS).mp hpeak)

/-- The `√` form and the squared form of the peak hypothesis agree (for `S > 0`). -/
theorem peak_sqrt_iff_sq {ks k S : ℝ} (hS : 0 < S) :
    Real.sqrt (k / (2 * ks)) < S ↔ k / (2 * ks) < S ^ 2 :=
  Real.sqrt_lt' hS

/-- **Positive control of the test.** It fires on `S = 1` at the self-dual point `k = ks`. -/
theorem diffraction_fires_free_at_selfdual {hc ks : ℝ} (hhc : 0 < hc) (hks : 0 < ks) :
    (1 : ℝ) ≠ sBog hc ks ks :=
  diffraction_test_model hhc hks hks (free_S_one_violates hks hks (by linarith))

/-- **Negative control of the test.** It never fires on the Bogoliubov value itself. -/
theorem diffraction_silent_on_sBog {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    ¬ (Real.sqrt (k / (2 * ks)) < sBog hc ks k) :=
  not_lt.mpr (sBog_le_sqrt hhc hk hks)

/-- Negative control of the phonon bound: `S ≡ 1` violates `S ≤ k/ks` for every `0 < k < ks`. -/
theorem free_S_one_violates_phonon {ks k : ℝ} (hks : 0 < ks) (hlt : k < ks) : k / ks < 1 :=
  (div_lt_one hks).mpr hlt

/-- Non-vacuity: the hypotheses are satisfiable and the sharp case is reached (`hc = ks = k = 1`). -/
theorem nonvacuous_selfdual : sBog 1 1 1 ^ 2 = 1 / (2 * 1) :=
  (sBog_sq_eq_iff one_pos one_pos one_pos).mpr rfl

end QuantumFluids.AutoresearchSkBoundShape

#print axioms QuantumFluids.AutoresearchSkBoundShape.bogoliubovSq_pos
#print axioms QuantumFluids.AutoresearchSkBoundShape.epsBog_sq
#print axioms QuantumFluids.AutoresearchSkBoundShape.sBog_pos
#print axioms QuantumFluids.AutoresearchSkBoundShape.sBog_sq
#print axioms QuantumFluids.AutoresearchSkBoundShape.sBog_sq_le
#print axioms QuantumFluids.AutoresearchSkBoundShape.sBog_le_sqrt
#print axioms QuantumFluids.AutoresearchSkBoundShape.sBog_sq_eq_iff
#print axioms QuantumFluids.AutoresearchSkBoundShape.feynman_sBog_exact
#print axioms QuantumFluids.AutoresearchSkBoundShape.sBog_sq_le_via_project
#print axioms QuantumFluids.AutoresearchSkBoundShape.free_S_one_violates
#print axioms QuantumFluids.AutoresearchSkBoundShape.sBog_eq_closed
#print axioms QuantumFluids.AutoresearchSkBoundShape.sBog_sq_lt_sq
#print axioms QuantumFluids.AutoresearchSkBoundShape.sBog_strictMonoOn
#print axioms QuantumFluids.AutoresearchSkBoundShape.sBog_lt_phonon
#print axioms QuantumFluids.AutoresearchSkBoundShape.phonon_lower_lt_sBog
#print axioms QuantumFluids.AutoresearchSkBoundShape.sBog_lt_one
#print axioms QuantumFluids.AutoresearchSkBoundShape.one_sub_sBog_le
#print axioms QuantumFluids.AutoresearchSkBoundShape.sBog_tendsto_one
#print axioms QuantumFluids.AutoresearchSkBoundShape.epsBog_eq_epsFree_div_sBog
#print axioms QuantumFluids.AutoresearchSkBoundShape.diffraction_test_model
#print axioms QuantumFluids.AutoresearchSkBoundShape.diffraction_test_dispersion
#print axioms QuantumFluids.AutoresearchSkBoundShape.peak_sqrt_iff_sq
#print axioms QuantumFluids.AutoresearchSkBoundShape.diffraction_fires_free_at_selfdual
#print axioms QuantumFluids.AutoresearchSkBoundShape.diffraction_silent_on_sBog
#print axioms QuantumFluids.AutoresearchSkBoundShape.free_S_one_violates_phonon
#print axioms QuantumFluids.AutoresearchSkBoundShape.nonvacuous_selfdual
