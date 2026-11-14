# H2 contribution, stage 1 (FORMALIZE): planar Yukawa crystals at every density, and screening-length mixtures

Date 2026-10-25. Producer run, not yet independently verified. Pinned stack: openai/math Lean 4.34.1 + Mathlib d13f23b7,
via `scripts/certified_numerics/lean_pinned.py`.

## Files

| File | Role | sha256 |
|---|---|---|
| `formal_cert/Autoresearch/Yukawa.lean` | prior round (verified ACCEPT); docstrings changed in this stage, nothing else | a16397de179837dd2119cf09c1b3086db7650b9b8bbaeb322f2d531936c033cf |
| `results/autoresearch/2026-10-25/H2/Yukawa.lean.prior_round` | byte copy of the file the prior ACCEPT was given on | 43e2df3ff9eca7ab6937904e8287311ebd6bae891e87324f501cff1dd0993bb4 |
| `formal_cert/Autoresearch/YukawaMix.lean` | **new**: closure lemmas, scaling identity, every-density corollaries, mixtures, negative control | 6a940a7cb1b4b25391a8fb6348873e04e4219501877c3a037760cd6f31b374c6 |
| `formal_cert/Autoresearch/YukawaMixControls.lean` | **new**: planted `ctl_sorry`/`ctl_axiom` + positive non-vacuity instances | 028a39361e23fe20ae510ed84300ad223087f3dff3df0e7edb749a30c93cbbf3 |
| `formal_cert/Autoresearch/YukawaControls.lean` | prior-round controls (unchanged), re-run against the rebuilt olean | ff7f11da15e3cfbe9dcd612397db2effbfdd99a89da876607ded9aa0d25740ff |

Physics wording, binding: `g κ t = exp(-κ √t)/√t` is the **planar Yukawa (3D-screened Coulomb) interaction** `e^{-κr}/r`
in `t = r²`, between particles confined to a plane (2D Yukawa crystals of dusty plasmas and colloids). It is **not** the
Green function of the 2D Debye–Hückel equation, `K₀(κr)`; `K₀` is not treated.

## Prior-round file: docstring-only change

`diff Yukawa.lean.prior_round Yukawa.lean` (backup of the verified file at `H2/Yukawa.lean.prior_round`): the only changed
lines are the module header (lines 4, 6–9), the `g` docstring (line 30) and the `yukawa_admissible` docstring (line 132),
replacing "Yukawa / Debye–Hückel" with "planar Yukawa (3D-screened Coulomb)" and adding the explicit not-`K₀` note. No
statement or proof changed. Rebuilt with `--olean Autoresearch.Yukawa`: **rc 0, 1074.1 s** (`compile_yukawa.json`).
The long wall time came from disk-2 IO starvation, with the process at about 1.6% CPU until the olean caches were warmed.
It is not a proof-cost figure. The prior verifier's ACCEPT (`H2/verification.md`) applies to unchanged statements.

## Theorem list (exact Lean statements)

From `Autoresearch.Yukawa` (prior round, namespace `AutoresearchYukawa`; carried over):

```lean
theorem admissible_mul {f h : ℝ → ℝ} (hf : AdmissiblePotential f) (hh : AdmissiblePotential h) :
    AdmissiblePotential (f * h)
theorem admissible_congr {f h : ℝ → ℝ} (hf : AdmissiblePotential f) (heq : Set.EqOn f h (Set.Ioi 0)) :
    AdmissiblePotential h
theorem phi_admissible {κ : ℝ} (hκ : 0 < κ) : AdmissiblePotential (phi κ)          -- phi κ t = exp(-κ √t)
theorem yukawa_admissible {κ : ℝ} (hκ : 0 < κ) : AdmissiblePotential (g κ)
theorem triangular_yukawa_optimal {κ : ℝ} (hκ : 0 < κ) (C : Set Plane) (hC : LocallyFinite C)
    (hdens : DensityOne C) : latticeEnergy (g κ) ≤ energy (g κ) C
theorem latticeEnergy_yukawa_lt_top {κ : ℝ} (hκ : 0 < κ) : latticeEnergy (g κ) < ⊤
theorem c_not_admissible (κ : ℝ) : ¬ AdmissiblePotential (c κ)                    -- c κ t = exp(-κ√t) cos t
```

New in `Autoresearch.YukawaMix` (namespace `AutoresearchYukawaMix`; `open scoped Pointwise`):

```lean
-- closure of upstream's AdmissiblePotential
theorem admissible_add {f h : ℝ → ℝ} (hf : AdmissiblePotential f) (hh : AdmissiblePotential h) :
    AdmissiblePotential (f + h)
theorem admissible_smul {f : ℝ → ℝ} (hf : AdmissiblePotential f) {c : ℝ} (hc : 0 ≤ c) :
    AdmissiblePotential (c • f)
theorem admissible_zero : AdmissiblePotential (0 : ℝ → ℝ)
theorem admissible_sum {ι : Type*} (s : Finset ι) (w : ι → ℝ) (f : ι → ℝ → ℝ) (hw : ∀ i ∈ s, 0 ≤ w i)
    (hf : ∀ i ∈ s, AdmissiblePotential (f i)) : AdmissiblePotential (∑ i ∈ s, w i • f i)

-- reusable finiteness criterion
theorem latticeEnergy_lt_top_of_le_riesz3 {f : ℝ → ℝ} {K : ℝ} (hK : 0 ≤ K)
    (hle : ∀ t : ℝ, 0 < t → f t ≤ K * riesz 3 t) : latticeEnergy f < ⊤

-- scaling identity (single length: density ρ = density one at screening κ/√ρ)
theorem g_rescale {κ ρ t : ℝ} (hρ : 0 < ρ) (ht : 0 < t) :
    g κ (ρ⁻¹ * t) = Real.sqrt ρ * g (κ / Real.sqrt ρ) t

-- single screening length, every density ρ > 0 (via D2, Triangular.AnyDensity)
theorem yukawa_any_density {κ : ℝ} (hκ : 0 < κ) {ρ : ℝ} (hρ : 0 < ρ) (C : Set Plane) (hC : LocallyFinite C)
    (hd : DensityRho ρ C) : latticeEnergy (fun t => g κ (ρ⁻¹ * t)) ≤ energy (g κ) C
theorem yukawa_optimal_any_density {κ : ℝ} (hκ : 0 < κ) {ρ : ℝ} (hρ : 0 < ρ) :
    LocallyFinite ((Real.sqrt ρ)⁻¹ • A) ∧ DensityRho ρ ((Real.sqrt ρ)⁻¹ • A) ∧
      ∀ C : Set Plane, LocallyFinite C → DensityRho ρ C →
        energy (g κ) ((Real.sqrt ρ)⁻¹ • A) ≤ energy (g κ) C
theorem latticeEnergy_yukawa_rho_lt_top {κ : ℝ} (hκ : 0 < κ) {ρ : ℝ} (hρ : 0 < ρ) :
    latticeEnergy (fun t => g κ (ρ⁻¹ * t)) < ⊤

-- finite mixtures of screening lengths: yukawaMix s w κ t = ∑ i ∈ s, w i * g (κ i) t
theorem yukawaMix_admissible {ι : Type*} (s : Finset ι) {w κ : ι → ℝ} (hw : ∀ i ∈ s, 0 ≤ w i)
    (hκ : ∀ i ∈ s, 0 < κ i) : AdmissiblePotential (yukawaMix s w κ)
theorem triangular_yukawaMix_optimal {ι : Type*} (s : Finset ι) {w κ : ι → ℝ} (hw : ∀ i ∈ s, 0 ≤ w i)
    (hκ : ∀ i ∈ s, 0 < κ i) (C : Set Plane) (hC : LocallyFinite C) (hd : DensityOne C) :
    latticeEnergy (yukawaMix s w κ) ≤ energy (yukawaMix s w κ) C
theorem latticeEnergy_yukawaMix_lt_top {ι : Type*} (s : Finset ι) {w κ : ι → ℝ} (hw : ∀ i ∈ s, 0 ≤ w i)
    (hκ : ∀ i ∈ s, 0 < κ i) : latticeEnergy (yukawaMix s w κ) < ⊤
theorem yukawaMix_optimal_any_density {ι : Type*} (s : Finset ι) {w κ : ι → ℝ} (hw : ∀ i ∈ s, 0 ≤ w i)
    (hκ : ∀ i ∈ s, 0 < κ i) {ρ : ℝ} (hρ : 0 < ρ) :
    LocallyFinite ((Real.sqrt ρ)⁻¹ • A) ∧ DensityRho ρ ((Real.sqrt ρ)⁻¹ • A) ∧
      ∀ C : Set Plane, LocallyFinite C → DensityRho ρ C →
        energy (yukawaMix s w κ) ((Real.sqrt ρ)⁻¹ • A) ≤ energy (yukawaMix s w κ) C
theorem latticeEnergy_yukawaMix_rho_lt_top {ι : Type*} (s : Finset ι) {w κ : ι → ℝ} (hw : ∀ i ∈ s, 0 ≤ w i)
    (hκ : ∀ i ∈ s, 0 < κ i) {ρ : ℝ} (hρ : 0 < ρ) :
    latticeEnergy (fun t => yukawaMix s w κ (ρ⁻¹ * t)) < ⊤
theorem two_length_admissible {w₁ w₂ κ₁ κ₂ : ℝ} (hw₁ : 0 ≤ w₁) (hw₂ : 0 ≤ w₂) (hκ₁ : 0 < κ₁) (hκ₂ : 0 < κ₂) :
    AdmissiblePotential (fun t => w₁ * g κ₁ t + w₂ * g κ₂ t)

-- negative control (proved, inside the claimed module; it is a true theorem, not a planted one)
theorem signedMix_neg : signedMix (1 / 4) < 0              -- signedMix t = g 1 t - 2 * g 2 t
theorem signedMix_not_admissible : ¬ AdmissiblePotential signedMix
```

`DensityRho`, `universal_any_density`, `triangular_optimal_any_density` come from `Triangular.AnyDensity` (D2, published
doi:10.5281/zenodo.23285631). `AdmissiblePotential`, `latticeEnergy`, `energy`, `A`, `universal_energy_minimum` are
upstream openai/math (`OAI.AtomicTriangular`). There are no name clashes: grep of upstream `OAI/Analysis/Triangular` and
`formal_cert/Triangular` for `admissible_add|admissible_smul|admissible_sum|admissible_zero|AdmissiblePotential.add`
found nothing.

## `#print axioms` (verbatim, `compile_yukawamix.json`, rc 0, 22.1 s)

```
'AutoresearchYukawaMix.admissible_add' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawaMix.admissible_smul' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawaMix.admissible_zero' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawaMix.admissible_sum' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawaMix.latticeEnergy_lt_top_of_le_riesz3' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawaMix.g_rescale' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawaMix.yukawa_any_density' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawaMix.yukawa_optimal_any_density' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawaMix.latticeEnergy_yukawa_rho_lt_top' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawaMix.yukawaMix_admissible' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawaMix.triangular_yukawaMix_optimal' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawaMix.latticeEnergy_yukawaMix_lt_top' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawaMix.yukawaMix_optimal_any_density' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawaMix.latticeEnergy_yukawaMix_rho_lt_top' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawaMix.two_length_admissible' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawaMix.signedMix_not_admissible' depends on axioms: [propext, Classical.choice, Quot.sound]
```

Rebuilt `Autoresearch.Yukawa` (verbatim, `compile_yukawa.json`, rc 0, 1074.1 s). The output is identical to the prior
round's `H2/compile_yukawa.json`:
```
'AutoresearchYukawa.mul_sign' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawa.admissible_mul' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawa.admissible_congr' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawa.phi_admissible' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawa.yukawa_admissible' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawa.triangular_yukawa_optimal' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawa.c_not_admissible' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawa.latticeEnergy_yukawa_lt_top' depends on axioms: [propext, Classical.choice, Quot.sound]
```

History:
- `compile_yukawamix_try1.json` (rc 1) failed only because `(Real.sqrt ρ)⁻¹ • A` needs `open scoped Pointwise`.
  Adding that line fixed it: rc 0, 32.3 s.
- `g_rescale` was added afterwards. The final compile is the one above, and the controls were re-run against that olean.

## Controls

`YukawaMixControls.lean` (`compile_yukawamix_controls.json`, rc 0, 18.6 s, re-run against the final `YukawaMix` olean),
verbatim:
```
/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/formal_cert/Autoresearch/YukawaMixControls.lean:11:8: warning: declaration uses `sorry`
'AutoresearchYukawaMixControls.ctl_sorry' depends on axioms: [sorryAx]
'AutoresearchYukawaMixControls.ctl_axiom' depends on axioms: [AutoresearchYukawaMixControls.ctl_cheat]
'AutoresearchYukawaMixControls.pos_two_length' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawaMixControls.pos_mix_rho3_finite' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawaMixControls.pos_yukawa_rho2' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawaMix.admissible_sum' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawaMix.yukawa_optimal_any_density' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawaMix.latticeEnergy_yukawa_rho_lt_top' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawaMix.yukawaMix_optimal_any_density' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawaMix.latticeEnergy_yukawaMix_rho_lt_top' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawaMix.signedMix_not_admissible' depends on axioms: [propext, Classical.choice, Quot.sound]
```
- Planted negatives were caught. `ctl_sorry` → `[sorryAx]`; `ctl_axiom` → the planted axiom `ctl_cheat`.
- Positive non-vacuity instances use concrete parameters:
  - `pos_two_length`: `e^{-r}/r + e^{-2r}/r` is admissible.
  - `pos_mix_rho3_finite`: the `Fin 2` mixture with `w = (1, 1)`, `κ = (1, 2)` has finite lattice energy at `ρ = 3`.
  - `pos_yukawa_rho2`: the every-density optimality holds at `κ = 1/2`, `ρ = 2`.
- Lean negative control `signedMix_not_admissible`: the weight-sign hypothesis cannot be dropped.
- Prior-round controls re-run against the rebuilt olean (`compile_yukawa_controls.json`, rc 0, 18.1 s), verbatim:
```
/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/formal_cert/Autoresearch/YukawaControls.lean:7:8: warning: declaration uses `sorry`
'AutoresearchYukawaControls.ctl_sorry' depends on axioms: [sorryAx]
'AutoresearchYukawaControls.ctl_axiom' depends on axioms: [AutoresearchYukawaControls.ctl_cheat]
'AutoresearchYukawa.mul_sign' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawa.admissible_mul' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawa.admissible_congr' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawa.phi_sign' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawa.phi_admissible' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawa.yukawa_admissible' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawa.triangular_yukawa_optimal' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawa.c_neg_at_pi' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawa.c_not_admissible' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawa.g_le' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchYukawa.latticeEnergy_yukawa_lt_top' depends on axioms: [propext, Classical.choice, Quot.sound]
```
- Forbidden-token grep (`sorry|admit|axiom|native_decide|implemented_by|extern|unsafe`, word match) on `Yukawa.lean` and
  `YukawaMix.lean` found no matches.
- Tier X numeric gate (`numeric_gate_mix.py` → `numeric_gate_mix.json`): mpmath, dps 40, `t = k/20` for k = 1..80, orders
  0..8. Results:
  - positive mixture `g₁ + 0.5 g₃`: 0 violations;
  - its `ρ = 3` rescaling: 0 violations;
  - negative `g₁ − 2g₂`: 530 violations, value at `t = 1/4` = −0.2585.
  - `gate_pass: true`. This is exploration only and supports no claim.

## What is new compared with the prior round
1. Closure of upstream's `AdmissiblePotential` under `+`, nonnegative scalar `•`, `0`, and finite nonnegative sums. With
   the prior `admissible_mul`/`admissible_congr`, the admissible class is now formally a convex cone closed under products.
2. Every-density planar Yukawa optimality, `yukawa_optimal_any_density`, with finite minimum (`latticeEnergy_yukawa_rho_lt_top`),
   by instantiating D2.
3. A new physical class: finite mixtures of screening lengths `∑ wᵢ e^{-κᵢ r}/r` (`wᵢ ≥ 0`, `κᵢ > 0`). These are admissible,
   optimal at density one and at every density, and have finite minima, so no corollary is `⊤ ≤ ⊤`.
4. A reusable finiteness criterion, `latticeEnergy_lt_top_of_le_riesz3`, and the scaling identity `g_rescale`.
5. A Lean negative control showing the sign condition on weights is needed (`signedMix_not_admissible`).

## Honest scope
- **Conditional (Tier A conditional).** Every optimality statement depends on upstream `universal_energy_minimum`, which is
  AI-generated, Comparator-accepted and not peer reviewed. It also depends on the fidelity of upstream's definitions
  (`energy` = liminf of disk-averaged energies, `DensityOne`, `AdmissiblePotential`). Classical model only: no temperature,
  no quantum effects, no 3D.
- **The every-density result adds no physics beyond the κ-family.** For `ρ > 0`,
  `g_κ(t/ρ) = √ρ · g_{κ/√ρ}(t)`, so the density-ρ statement is the density-one statement at screening `κ/√ρ` with energies
  scaled by `√ρ`. The only physical parameter is `κa` with `a = ρ^{-1/2}`. The pointwise identity is kernel-checked as
  `g_rescale` (Tier A, for `t > 0`). The energy-level consequence, with the factor `√ρ` pulled out of the lattice sum, is
  not stated in Lean. The value of `yukawa_optimal_any_density` is that it states the result directly at every density
  in kernel-checked form. The mixture class has no such reduction for a single κ: under rescaling, all ratios `κᵢ/κⱼ`
  are preserved.
- **Novelty is formal only.** Completely monotone functions form a convex cone closed under products, which is textbook
  (Bernstein–Widder). Complete monotonicity of `e^{-κr}/r` in `r²` is classical. What is new is the kernel-checked
  corollaries inside upstream's framework, not the mathematics.
- **Junk values.** `g κ 0 = 0` and `yukawaMix … 0 = 0` (from `√0 = 0`, `x/0 = 0`) are never evaluated: admissibility constrains
  only `t > 0`, and `energy`/`latticeEnergy` evaluate only at distinct points or nonzero lattice vectors (prior verifier's
  analysis, unchanged).
- **Not covered.** The 2D Debye–Hückel Green function `K₀(κr)`. Infinite mixtures (integrals over κ). Negative weights.
  Non-triangular phases.
- **Verification status.** Producer-only for `YukawaMix.lean`. Tier A for the new statements still needs an independent
  recompile and an adversarial statement audit (producer ≠ verifier).
