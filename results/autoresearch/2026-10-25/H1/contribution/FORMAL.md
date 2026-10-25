# H1 contribution, stage 1 (FORMALIZE): bilayer exciton potential, every density, and the shifted-difference family

Status: **producer-checked only**. The new theorems have not been independently verified yet; that happens in a later
stage, so nothing here is called "verified". The four prior-round theorems are imported unchanged and keep their
prior status (ACCEPT_WITH_CORRECTIONS, `../verification.md`).

## Files

| file | role | sha256 |
|---|---|---|
| `formal_cert/Autoresearch/DipolarExciton.lean` | prior round, **unchanged**, imported | `b85389a50373adaf877e866c79f0696ba0a284d9626bc9a56040821c3e11f27d` |
| `formal_cert/Autoresearch/DipolarExcitonMultipolar.lean` | **new** contribution module | `7f52ea64903c43cbfe95b76eea74a2ea01040c45d778ae05bbb848aa9554f98a` |
| `formal_cert/Autoresearch/DipolarExcitonMultipolarControls.lean` | **new** planted controls (only place with `sorry`/`axiom`) | `1754e1a9ba6ed844a1d0356872cf2a5662c89d13e85d1fd39747f3fe1215106d` |
| `formal_cert/Triangular/AnyDensity.lean` | D2 (Oct 10), unchanged, imported | `0a6d86eef3ee24b2b6828ff602707868e160969bfbebc41db375c05b383c5168` |


Toolchain: pinned openai/math, Lean 4.34.1 + Mathlib d13f23b7, via
`taskset -c 4-7 python3 scripts/certified_numerics/lean_pinned.py compile FILE [--olean MOD] --json-out OUT`.
- `compile_attempt1.json`: `DipolarExcitonMultipolar.lean --olean Autoresearch.DipolarExcitonMultipolar`, rc 0, 1073.9 s
  (almost all of it waiting on disk 2 I/O: the process sat at 0–6 % CPU with a thread in `folio_wait_bit_common`; the
  page cache was re-warmed twice by re-reading the mapped `.olean`/`.ir` files). No warnings, no errors. First attempt.
- `compile_controls.json`: `DipolarExcitonMultipolarControls.lean`, rc 0, 29.7 s.
- The Oct 10 `Triangular/AnyDensity.olean` imported without problems next to today's rebuilt `Riesz`/`RieszFinite`
  oleans (sources unchanged), so it was **not** rebuilt.
- `grep -c sorry` on both claimed modules: 0.

Prior-round names live in namespace `AutoresearchDipolar`; new names in `AutoresearchDipolarMultipolar`.
`g d t = 2 * (t ^ (-(1 / 2 : ℝ)) - (t + d ^ 2) ^ (-(1 / 2 : ℝ)))` (`t = r²`).

## Theorem list (exact Lean statements)

### Kept (prior round, imported unchanged)
```lean
theorem dipolar_admissible {d : ℝ} (_hd : 0 < d) : AdmissiblePotential (g d)
theorem triangular_dipolar_optimal {d : ℝ} (hd : 0 < d) (C : Set Plane) (hC : LocallyFinite C)
    (hdens : DensityOne C) : latticeEnergy (g d) ≤ energy (g d) C
theorem latticeEnergy_dipolar_lt_top (d : ℝ) : latticeEnergy (g d) < ⊤
theorem h_not_admissible {d : ℝ} (hd : 0 < d) : ¬ AdmissiblePotential (h d)   -- negative control, h d t = t^(-1/2) - 2 (t+d²)^(-1/2)
```

### New: shifted-difference (multipolar-form) family
```lean
noncomputable def shiftDiff (s c : ℝ) : ℝ → ℝ := fun t => t ^ (-(s / 2)) - (t + c) ^ (-(s / 2))

theorem shiftDiff_admissible {s c : ℝ} (hs : 0 < s) (hc : 0 ≤ c) : AdmissiblePotential (shiftDiff s c)

lemma admissible_const_mul {f : ℝ → ℝ} (hf : AdmissiblePotential f) {k : ℝ} (hk : 0 ≤ k) :
    AdmissiblePotential (fun t => k * f t)

lemma g_eq_shiftDiff (d : ℝ) : AutoresearchDipolar.g d = fun t => 2 * shiftDiff 1 (d ^ 2) t

theorem dipolar_admissible_all (d : ℝ) : AdmissiblePotential (AutoresearchDipolar.g d)

theorem triangular_shiftDiff_optimal {s c : ℝ} (hs : 0 < s) (hc : 0 ≤ c) (C : Set Plane) (hC : LocallyFinite C)
    (hdens : DensityOne C) : latticeEnergy (shiftDiff s c) ≤ energy (shiftDiff s c) C
```
Negative control for the generalisation (the sign of `c` matters):
```lean
theorem shiftDiff_neg_of_neg {s c : ℝ} (hs : 0 < s) (hc : c < 0) : shiftDiff s c (-2 * c) < 0
theorem shiftDiff_not_admissible_of_neg {s c : ℝ} (hs : 0 < s) (hc : c < 0) :
    ¬ AdmissiblePotential (shiftDiff s c)
```
The task asked for `c > 0`; the lemma is stated for `c ≥ 0`, which contains it (`c = 0` gives the zero potential).

### New: every density (instantiation of D2 `TriangularDensity.triangular_optimal_any_density`)
```lean
theorem triangular_dipolar_optimal_any_density {d : ℝ} (hd : 0 < d) {ρ : ℝ} (hρ : 0 < ρ) :
    LocallyFinite ((Real.sqrt ρ)⁻¹ • A) ∧ TriangularDensity.DensityRho ρ ((Real.sqrt ρ)⁻¹ • A) ∧
      ∀ C : Set Plane, LocallyFinite C → TriangularDensity.DensityRho ρ C →
        energy (AutoresearchDipolar.g d) ((Real.sqrt ρ)⁻¹ • A) ≤ energy (AutoresearchDipolar.g d) C

theorem triangular_shiftDiff_optimal_any_density {s c : ℝ} (hs : 0 < s) (hc : 0 ≤ c) {ρ : ℝ} (hρ : 0 < ρ) :
    LocallyFinite ((Real.sqrt ρ)⁻¹ • A) ∧ TriangularDensity.DensityRho ρ ((Real.sqrt ρ)⁻¹ • A) ∧
      ∀ C : Set Plane, LocallyFinite C → TriangularDensity.DensityRho ρ C →
        energy (shiftDiff s c) ((Real.sqrt ρ)⁻¹ • A) ≤ energy (shiftDiff s c) C
```

### New: non-vacuity at every density (the every-density statement is not `⊤ ≤ ⊤`)
```lean
lemma g_scaled_le (d : ℝ) {ρ : ℝ} (hρ : 0 < ρ) {t : ℝ} (ht : 0 < t) :
    AutoresearchDipolar.g d (ρ⁻¹ * t) ≤ (d ^ 2 * (ρ⁻¹) ^ (-((3 : ℝ) / 2))) * riesz 3 t

theorem latticeEnergy_dipolar_scaled_lt_top (d : ℝ) {ρ : ℝ} (hρ : 0 < ρ) :
    latticeEnergy (fun t => AutoresearchDipolar.g d (ρ⁻¹ * t)) < ⊤

theorem energy_dipolar_any_density_lt_top {d : ℝ} (hd : 0 < d) {ρ : ℝ} (hρ : 0 < ρ) :
    energy (AutoresearchDipolar.g d) ((Real.sqrt ρ)⁻¹ • A) < ⊤
```

## `#print axioms` and planted controls (verbatim, `compile_controls.json`, rc 0, 29.7 s)
```
/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/formal_cert/Autoresearch/DipolarExcitonMultipolarControls.lean:8:8: warning: declaration uses `sorry`
'AutoresearchDipolarMultipolarControls.ctl_sorry' depends on axioms: [sorryAx]
'AutoresearchDipolarMultipolarControls.ctl_axiom' depends on axioms: [AutoresearchDipolarMultipolarControls.ctl_cheat]
'AutoresearchDipolar.dipolar_admissible' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchDipolar.triangular_dipolar_optimal' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchDipolar.latticeEnergy_dipolar_lt_top' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchDipolar.h_not_admissible' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchDipolarMultipolar.shiftDiff_admissible' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchDipolarMultipolar.admissible_const_mul' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchDipolarMultipolar.g_eq_shiftDiff' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchDipolarMultipolar.dipolar_admissible_all' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchDipolarMultipolar.shiftDiff_neg_of_neg' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchDipolarMultipolar.shiftDiff_not_admissible_of_neg' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'AutoresearchDipolarMultipolar.triangular_dipolar_optimal_any_density' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'AutoresearchDipolarMultipolar.triangular_shiftDiff_optimal_any_density' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'AutoresearchDipolarMultipolar.triangular_shiftDiff_optimal' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchDipolarMultipolar.g_scaled_le' depends on axioms: [propext, Classical.choice, Quot.sound]
'AutoresearchDipolarMultipolar.latticeEnergy_dipolar_scaled_lt_top' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'AutoresearchDipolarMultipolar.energy_dipolar_any_density_lt_top' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'TriangularDensity.triangular_optimal_any_density' depends on axioms: [propext, Classical.choice, Quot.sound]
'OAI.AtomicTriangular.universal_energy_minimum' depends on axioms: [propext, Classical.choice, Quot.sound]
```
Gate reading: rc is 0 even with the planted `sorry` and planted axiom, so rc is not the gate; the axiom list is. Both
planted controls are caught (`sorryAx`, `ctl_cheat`); every claimed theorem is within the whitelist
`{propext, Classical.choice, Quot.sound}`. The same lines (for the ten theorems printed there) appear in
`compile_attempt1.json`.

## Human proof sketch (Tier C summary of what the kernel checked)
- `shiftDiff_admissible`: `d^r/dt^r (t+c)^a = descPoch_r(a) (t+c)^{a-r}`; with `a = -s/2`,
  `(-1)^r descPoch_r(-s/2) = ascPoch_r(s/2) > 0` for `s > 0`, and `t^{a-r} - (t+c)^{a-r} ≥ 0` because `x ↦ x^e` is
  antitone on `(0,∞)` for `e ≤ 0` and `c ≥ 0`. Smoothness: rpow is smooth away from 0. (Equivalently, by Bernstein,
  `t^{-s/2} - (t+c)^{-s/2} = Γ(s/2)^{-1} ∫ e^{-ut}(1 - e^{-uc}) u^{s/2-1} du`.)
- Negative control: for `c < 0` and `t = -2c > 0`, `t + c = -c ∈ (0, t)`, so `(t+c)^{-s/2} > t^{-s/2}`.
- Every density: D2 rescales a density-`ρ` configuration by `√ρ` to density one and uses that `t ↦ g(t/ρ)` is admissible.
- Non-vacuity: `g_d(t) ≤ d² t^{-3/2}` (prior-round `g_le`), so `g_d(t/ρ) ≤ d² ρ^{3/2} t^{-3/2}`, and the Riesz-3
  lattice sum is finite (D1b); `attained` identifies `energy (g d) (ρ^{-1/2} A)` with that lattice sum.

## What is new versus the prior round
- New: `shiftDiff_admissible` (all `s > 0`, `c ≥ 0`), the reduction `g_eq_shiftDiff` and `dipolar_admissible_all`
  (drops the unused `0 < d`, addressing verification correction 2 in Lean), `admissible_const_mul`,
  `triangular_shiftDiff_optimal`, the negative control `shiftDiff_not_admissible_of_neg`, the every-density corollary
  for `g d` and `shiftDiff s c` as module theorems (the prior verifier had only instantiated it in a deleted scratch
  file), and the every-density finiteness `energy_dipolar_any_density_lt_top`.
- Kept by import, unchanged: the four prior theorems listed above . `formal_cert/Autoresearch/DipolarExciton.lean` is tracked and clean in git
  (`git status --porcelain` lists no change; last commit touching it: `ede25aec8726384dc80c465d7fa047d91723af1f`); its
  mtime (07:17) precedes `../verification.md` (07:29) and its imported olean was built at 07:18. `verification.md` did
  not record a hash, so the sha256 above is a record for future checks, not proof of identity with the verified text.

## Honest scope
- All optimality statements are **conditional** on upstream `OAI.AtomicTriangular.universal_energy_minimum`
  (openai/math, AI-generated, not peer reviewed; the 2D Cohn–Kumar conjecture is open in the human literature) and on the
  fidelity of its definitions (`energy` = liminf of disk averages, `LocallyFinite`, `DensityOne`; D2's `DensityRho`).
- Physics: classical point particles, zero temperature, no kinetic/zero-point energy; rigid bound e–h pairs aligned
  perpendicular to the layers at fixed separation `d`. For `s ≠ 1`, `shiftDiff s c` is a **mathematical**
  generalisation only; no physical multipole model is claimed for it.
- The complete-monotonicity step is elementary (Bernstein / folklore). The contribution is the explicit kernel-checked
  corollaries, not a new physics result.
- Not done (open): finiteness of `latticeEnergy (shiftDiff s c)` for general `s > 0` (true by the mean value theorem,
  `shiftDiff s c t ≤ (s/2) c t^{-s/2-1}`, so it is ≤ a Riesz-(s+2) sum, but not formalised here; for `s > 2` it follows
  trivially from `shiftDiff ≤ riesz s`, also not stated); and the kernel-checked scaling identity
  `g_d(t/ρ) = √ρ · g_{d√ρ}(t)` asserted in `../NOTE.md` (the every-density result above does not need it).
