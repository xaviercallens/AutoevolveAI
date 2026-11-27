# D2 independent verification

Verifier: separate agent (producer != verifier), 2026-10-10, worktree commit 8912d76 (`AnyDensity.lean` last changed in 6845de3).
Toolchain: `scripts/certified_numerics/lean_pinned.py` (upstream-pinned Lean 4.34.1 + Mathlib + openai/math OAI). Scratch Lean file
`formal_cert/Triangular/VerifyScratchD2.lean` was compiled without `--olean` and then deleted (a copy is kept as `verify_d2/VerifyScratchD2.lean` in the job scratch directory). Numerics scripts are in the job
scratch directory (`verify_d2/numerics.py`, `verify_d2/gauss_mp.py`), not in the repo.

## VERDICT: CONFIRMED_WITH_CORRECTIONS

`universal_any_density` and `riesz_any_density` compile and use only the three whitelisted axioms. The statement says what it
claims. The verifier proved in the kernel that the hypothesis can be satisfied and that the bound is attained, and also refuted the
unscaled variant. The corrections are about wording and missing companion lemmas, not about the proof.

## 1. Statement adequacy

* **Lattice side.** Upstream defines `latticeEnergy g = Σ'_{a ∈ A, a ≠ 0} ofReal(g ‖a‖²)`, where `A = range triangularPoint`
  and `triangularPoint(j,k) = √(2/√3)·(j + k/2, k√3/2)` has covolume 1 (numerically det = 1.0). With `g t = h(ρ⁻¹ t)` the sum is
  `Σ_{a} h(‖a‖²/ρ) = Σ_{y ∈ ρ^{-1/2}A \ 0} h(‖y‖²)`, the per-point energy of the lattice ρ^{-1/2}A. That lattice has covolume
  1/ρ, so its density is ρ. The statement is therefore correct as written.
* **Density notion.** `DensityRho ρ C := Tendsto (diskCount C R / (π R²)) atTop (𝓝 ρ)`. This is upstream's `DensityOne`
  with 1 replaced by ρ: the same origin-centred closed disks and the same counting. It inherits upstream's choices (origin-centred
  disks, `liminf` "lower energy" in [0,∞], ordered pairs), and the D1 verification already discussed these.
* **ρ = 1 control (kernel).** `example : DensityRho 1 C ↔ DensityOne C := Iff.rfl` compiles. `rho_one`, the D2 instance at ρ = 1
  after `simpa`, has exactly the type of `(universal_energy_minimum h C hh hC hd).1`. The two proofs are equal by `rfl`
  (proof irrelevance), so D2 at ρ = 1 is upstream's statement.
* **Non-vacuity (kernel).** `scaled_density : 0 < ρ → DensityRho ρ ((√ρ)⁻¹ • A)` is proved from upstream's
  `triangular_densityOne`, `A_eq_support` and the producer's `diskCount_smul`. So `DensityRho ρ` can be satisfied for every ρ > 0.
* **Sharpness, not a trivial bound (kernel).** `attained : energy h ((√ρ)⁻¹ • A) = latticeEnergy (fun t => h (ρ⁻¹ * t))` for
  every admissible h, via `energy_smul` and the second conjunct of upstream's theorem. Together with D2 this shows that ρ^{-1/2}A
  attains the minimum among density-ρ configurations, i.e. it is *optimal*, not only a lower bound. The producer's file proves
  only the lower bound.
* **Possible vacuity of the value.** As with D1, the bound can be `⊤ ≤ ⊤`. For the Riesz potential, `latticeEnergy(riesz s ∘ (ρ⁻¹·))
  = ρ^{s/2}·latticeEnergy(riesz s)`, which is finite iff s > 2 (D1b). So `riesz_any_density` is informative only for s > 2,
  and its docstring does not say so.
* **Admissibility under scaling.** `admissible_comp_mul` uses `iteratedDeriv r (g(c·)) = c^r g^{(r)}(c·)`, which the producer
  proves by induction (`iterate_deriv_comp_mul`), with c^r ≥ 0. This is correct, and every condition is on (0,∞) only.

## 2. Recompile and axiom audit (own run)

* `lean_pinned.py compile formal_cert/Triangular/AnyDensity.lean --olean Triangular.AnyDensity`: rc 0, 14.1 s. The only
  messages were 2 deprecation warnings (`dif_pos`, line 76).
* `grep -n "sorry|native_decide|axiom|admit|implemented_by|extern|unsafe|opaque"` on `AnyDensity.lean` and `Riesz.lean`: no hits.
* Scratch `#print axioms`: `universal_any_density`, `riesz_any_density`, `admissible_comp_mul`, `energy_smul`, `density_smul`,
  and the verifier's `scaled_density`, `attained`, `unscaled_false` all print `[propext, Classical.choice, Quot.sound]`.
  Scratch compile: rc 0, 13.6 s, no warnings. The kernel prints the statement as
  `∀ h, AdmissiblePotential h → ∀ {ρ}, 0 < ρ → ∀ C, LocallyFinite C → DensityRho ρ C → latticeEnergy (fun t => h (ρ⁻¹ * t)) ≤ energy h C`.
* Planted-control file `Axioms.lean` (`ctl_sorry`, `ctl_axiom`): not re-run here. The D1 verification ran it and it flagged both.

## 3. Negative control

* **ρ = 4 is not a valid negative control.** The task suggested the unscaled claim `latticeEnergy h ≤ energy h C` at ρ = 4. That
  claim is weaker than D2 and is true: admissible h is antitone (r = 1 sign condition), so h(t) ≤ h(t/4) termwise and
  `latticeEnergy h ≤ latticeEnergy (h(·/4)) ≤ energy h C`. Numerically, the unscaled sum is at most the ρ-scaled sum for every
  ρ ≥ 1 in the table below. The verifier did not kernel-check this direction.
* **ρ = 1/4 refutes it (kernel).** `unscaled_false : ¬ ∀ C, LocallyFinite C → DensityRho (1/4) C →
  latticeEnergy (riesz 4) ≤ energy (riesz 4) C` is proved with whitelisted axioms only. The witness is C = 2A, whose energy is
  `Σ (4‖a‖²)^{-2}`, strictly below `Σ ‖a‖^{-4} < ∞`. The proof uses `ENNReal.tsum_lt_tsum` and D1b's finiteness. So the unscaled
  claim has no proof, and the factor ρ⁻¹ in the D2 statement is necessary. Numerically (exp(−t)): the unscaled value is 2.1418, and the
  energy of 2A is 0.0592.

## 4. Numerics: ρ-scaled triangular vs square lattice at the same density

The per-point energy `Σ_{y ∈ ρ^{-1/2}L \ 0} h(‖y‖²)` was computed with L covolume 1. Positive control: the square-lattice Riesz-4 sum at ρ = 1,
truncated at N = 400, gives 6.026796, against the closed form 4ζ(2)β(2) = 6.026812 (difference = truncation tail).
exp(−t) values are mpmath 60-digit direct sums (N = 40), cross-checked against the Poisson/theta form. Both give the same differences.

| h | ρ | triangular | square | square − tri |
|---|---|---|---|---|
| exp(−t) | 0.5 | 0.60238788592 | 0.61630926604 | 1.392e-2 |
| exp(−t) | 2 | 5.2831853119385 | 5.2831853744169 | 6.248e-8 |
| exp(−t) | 4 | 11.566370614359172955 | 11.566370614359173314 | 3.586e-16 |
| t^{-2} (s = 4) | 0.5 | 1.445835 | 1.506699 | ratio tri/sq 0.959605 |
| t^{-2} (s = 4) | 2 | 23.13337 | 24.10718 | ratio 0.959605 |
| t^{-2} (s = 4) | 4 | 92.53347 | 96.42874 | ratio 0.959605 |

The triangular lattice is smaller in every case. For the Riesz potential the ratio does not depend on ρ, as homogeneity predicts.
The Gaussian gap shrinks like exp(−π²ρ·min dual norm²). At ρ = 4 the gap is below double precision: a float64 run printed
`tri<square=False` there, and the mpmath run resolves the gap. A second negative control, a covolume-1 rectangular lattice with
aspect ratio 2, is never below the triangular lattice (ρ = 0.5, 2, 4).

## 5. Overclaim scan (`docs/DISCOVERY_PROPOSAL_2026-10-10.md`, D2 parts) and corrections

1. §4 says "D2 is not yet independently verified". Update it to point to this file (CONFIRMED_WITH_CORRECTIONS).
2. D2 is a scaling corollary of upstream's theorem and inherits all of its conditionality (statement fidelity not human-audited,
   AI-generated proof). §3 says this for D1 only. Add the same caveat for D2, and add that the step from D2 to upstream is
   mathematically immediate (dilation invariance of the problem).
3. "the scaled triangular lattice is optimal" (§2 table, `AnyDensity.lean` docstring): the file proves only the lower bound.
   Add the verifier's `scaled_density` and `attained` (both short, see §1) to `AnyDensity.lean`, or say "is a lower bound".
4. `riesz_any_density` docstring: add "informative only for s > 2 (lattice energy ρ^{s/2}·ζ_A(s) < ∞); for s ≤ 2 both sides are ⊤".
5. Minor: the preregistration says P ≈ 65–70% and the proposal table says ~70%. Name the scaled lattice explicitly as
   ρ^{-1/2}A in the table.
6. No claim of novelty was found for D2. Keep it that way: rescaling to arbitrary density is standard in Cohn–Kumar.
