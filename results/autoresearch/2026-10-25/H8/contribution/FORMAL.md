# H8 contribution, Stage 1 (FORMALIZE): shape of the Bogoliubov structure factor and a diffraction test

**Status: producer-checked only.** Kernel compile rc 0 with no warnings or errors. All 26 declarations depend only on
`[propext, Classical.choice, Quot.sound]`, and both planted controls are flagged. This is **not yet Tier A**: an
independent recompile and statement audit (producer ≠ verifier) is still pending for the new theorems. The round-1
file `../Autoresearch_SkBound.lean` was independently verified (ACCEPT_WITH_CORRECTIONS, `../verification.md`) and is left
unchanged.

## Files
| file | sha256 | compile |
|---|---|---|
| `Autoresearch_SkBoundShape.lean` (claimed module) | `fac6c85f9e6c0bd7b60861a9e1286a56283ef211d006630351ebb3c0e9e39454` | rc 0, 1004.9 s, `compile_main.json` |
| `Autoresearch_SkBoundShapeControls.lean` (planted controls only) | `0beb41c999802886a4ee02d29875a01a064da2ea8936fc3b577dbe707db92ed5` | rc 0, 398.9 s, `compile_controls.json` |
| `numeric_gate_shape.py` → `numeric_gate_shape.json` | — | Tier X gate, run before Lean |
| `run_lean_rc2.py` | — | compile runner (env, taskset 4-7, 1800 s timeout, records rc/stdout/stderr/sha256) |

Toolchain: QuantumFluids environment. Lean `leanprover--lean4---v4.34.0-rc2`, with `LEAN_PATH` = qf-lake `build/lib/lean`
+ `packages/*/.lake/build/lib/lean` + rc2 `lib/lean` (the H7/H8 recipe; the exact list is in `compile_main.json`). The file
imports the owner's compiled `DualLength` module, which carries `import Mathlib`. The file itself does not import Mathlib.

Attempt log (all kept):
- `attempt1_*_timeout.json`: rc 124 at 1800 s for both files. Disk I/O starvation: the process sat in `D` state
  (`folio_wait_bit_common`), with no Lean error.
- `attempt2_main_rc1.json`: after re-warming the page cache (114,925 files / 9,828 modules) the file elaborated in 44 s and
  failed with 2 errors. `tendsto_pow_atTop` needed the `Filter.` prefix, and a rewrite chain in
  `epsBog_eq_epsFree_div_sBog` was wrong. Both were fixed.
- `compile_main.json`: rc 0, no warnings.

Grep of the claimed file for `sorry|admit|native_decide|axiom` declarations: no match (grep rc 1).

## Theorem list (namespace `QuantumFluids.AutoresearchSkBoundShape`)
Definitions, taken verbatim from round 1, where `bogoliubovSq hc ks k = (hc*k)^2 + (hc*k^2/ks)^2` is the owner's:
```lean
noncomputable def epsFree (hc ks k : ℝ) : ℝ := hc * k ^ 2 / ks
noncomputable def epsBog (hc ks k : ℝ) : ℝ := Real.sqrt (bogoliubovSq hc ks k)
noncomputable def sBog (hc ks k : ℝ) : ℝ := epsFree hc ks k / epsBog hc ks k
```
**The blocks in this section are an abbreviated summary.** Binders are dropped, and the hypotheses
`(hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks)` apply unless stated otherwise. The exact statements, extracted
mechanically from the compiled file, are in "Exact Lean statements" below.

### Kept from round 1 (re-proved here under the same names and statements)
```lean
theorem bogoliubovSq_pos (hhc : 0 < hc) (hk : 0 < k) : 0 < bogoliubovSq hc ks k
theorem epsBog_sq (hhc : 0 < hc) (hk : 0 < k) : epsBog hc ks k ^ 2 = epsFree hc ks k ^ 2 + (hc * k) ^ 2
theorem sBog_pos : 0 < sBog hc ks k
theorem sBog_sq : sBog hc ks k ^ 2 = k ^ 2 / (ks ^ 2 + k ^ 2)
theorem sBog_sq_le : sBog hc ks k ^ 2 ≤ k / (2 * ks)
theorem sBog_le_sqrt : sBog hc ks k ≤ Real.sqrt (k / (2 * ks))
theorem sBog_sq_eq_iff : sBog hc ks k ^ 2 = k / (2 * ks) ↔ k = ks
theorem feynman_sBog_exact : (hc * k ^ 2 / (ks * sBog hc ks k)) ^ 2 = bogoliubovSq hc ks k
theorem sBog_sq_le_via_project : sBog hc ks k ^ 2 ≤ k / (2 * ks)   -- via owner feynman_ge_iff + ell_ge
theorem free_S_one_violates (_hk : 0 < k) (hks : 0 < ks) (hlt : k < 2 * ks) : Real.sqrt (k / (2 * ks)) < 1
```
Round 1's `free_S_one_not_le_at_selfdual` (`¬ (1 ≤ √(ks/(2ks)))`) was **not carried over** as a named theorem.
Its content, `free_S_one_violates` at `k = ks`, is used inside the proof of `diffraction_fires_free_at_selfdual`, which
states something different: `1 ≠ sBog hc ks ks`.

### New: shape theorems
```lean
theorem sBog_eq_closed : sBog hc ks k = k / Real.sqrt (ks ^ 2 + k ^ 2)
theorem sBog_sq_lt_sq (hhc : 0 < hc) (hks : 0 < ks) (ha : 0 < a) (hab : a < b) :
    sBog hc ks a ^ 2 < sBog hc ks b ^ 2
theorem sBog_strictMonoOn (hhc : 0 < hc) (hks : 0 < ks) : StrictMonoOn (sBog hc ks) (Set.Ioi 0)
theorem sBog_lt_phonon : sBog hc ks k < k / ks                       -- phonon-regime upper bound
theorem phonon_lower_lt_sBog : k / (ks + k) < sBog hc ks k           -- phonon-regime lower bound
theorem sBog_lt_one : sBog hc ks k < 1
theorem one_sub_sBog_le : 1 - sBog hc ks k ≤ ks ^ 2 / k ^ 2          -- quantitative approach to the free particle
theorem sBog_tendsto_one (hhc : 0 < hc) (hks : 0 < ks) :
    Filter.Tendsto (sBog hc ks) Filter.atTop (nhds 1)
theorem epsBog_eq_epsFree_div_sBog : epsBog hc ks k = epsFree hc ks k / sBog hc ks k
```
Together, `phonon_lower_lt_sBog` and `sBog_lt_phonon` give `ks/(ks+k) < S_B/(k/ks) < 1`. So `S_B ~ k/ks = ħk/(2mc)` as
`k → 0`, with an explicit error bound.

### New: the diffraction test
```lean
-- model level, unconditional
theorem diffraction_test_model (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks)
    (hpeak : Real.sqrt (k / (2 * ks)) < S) : S ≠ sBog hc ks k
-- dispersion level, CONDITIONAL on Feynman's variational inequality `hfeyn` (physics input)
theorem diffraction_test_dispersion (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) (hS : 0 < S)
    (hfeyn : epsSq ≤ (hc * k ^ 2 / (ks * S)) ^ 2)
    (hpeak : Real.sqrt (k / (2 * ks)) < S) : epsSq ≠ bogoliubovSq hc ks k
  -- := not_bogoliubov_of_structure_factor (owner lemma, DualLength.lean) ∘ peak_sqrt_iff_sq
theorem peak_sqrt_iff_sq (hS : 0 < S) : Real.sqrt (k / (2 * ks)) < S ↔ k / (2 * ks) < S ^ 2
```
In-file controls of the test (claimed, kernel-checked):
```lean
theorem diffraction_fires_free_at_selfdual (hhc : 0 < hc) (hks : 0 < ks) : (1 : ℝ) ≠ sBog hc ks ks   -- positive: fires on S = 1 at k = ks
theorem diffraction_silent_on_sBog : ¬ (Real.sqrt (k / (2 * ks)) < sBog hc ks k)               -- negative: never fires on S_B
theorem free_S_one_violates_phonon (hks : 0 < ks) (hlt : k < ks) : k / ks < 1                   -- S = 1 breaks S ≤ k/ks for k < ks
theorem nonvacuous_selfdual : sBog 1 1 1 ^ 2 = 1 / (2 * 1)                                      -- hypotheses satisfiable, sharp case reached
```

## `#print axioms`, verbatim (from `compile_main.json` stdout)
```
'QuantumFluids.AutoresearchSkBoundShape.bogoliubovSq_pos' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.epsBog_sq' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.sBog_pos' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.sBog_sq' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.sBog_sq_le' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.sBog_le_sqrt' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.sBog_sq_eq_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.feynman_sBog_exact' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.sBog_sq_le_via_project' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.free_S_one_violates' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.sBog_eq_closed' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.sBog_sq_lt_sq' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.sBog_strictMonoOn' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.sBog_lt_phonon' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.phonon_lower_lt_sBog' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.sBog_lt_one' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.one_sub_sBog_le' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.sBog_tendsto_one' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.epsBog_eq_epsFree_div_sBog' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.diffraction_test_model' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.diffraction_test_dispersion' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.peak_sqrt_iff_sq' depends on axioms: [propext, Classical.choice, Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.diffraction_fires_free_at_selfdual' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.diffraction_silent_on_sBog' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.free_S_one_violates_phonon' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'QuantumFluids.AutoresearchSkBoundShape.nonvacuous_selfdual' depends on axioms: [propext, Classical.choice, Quot.sound]
```

## Planted controls (`compile_controls.json`): both caught
The controls file exits **rc 0** even though it contains a `sorry` and a planted axiom. That is why the axiom audit, not
the exit code, is the gate.
```
Autoresearch_SkBoundShapeControls.lean:13:8: warning: declaration uses `sorry`
'QuantumFluids.AutoresearchSkBoundShapeControls.ctl_sorry' depends on axioms: [propext,
 sorryAx,
 Classical.choice,
 Quot.sound]
'QuantumFluids.AutoresearchSkBoundShapeControls.ctl_axiom' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 QuantumFluids.AutoresearchSkBoundShapeControls.ctl_cheat]
```
`ctl_sorry` plants the false claim `1 ≤ S_B`. `ctl_cheat` plants the false claim that `S_B` is strictly antitone.

## Numeric falsification gate (Tier X, supports no claim)
The gate is `numeric_gate_shape.json`. It uses mpmath at 50 digits on 101,595 points with x = k/ks in [1e-12, 1e4].
- Claimed bounds: 0 violations each for mono, phonon_upper, phonon_lower, lt1, free, dual and epsB.
- Negative controls, each required to fail somewhere:
  - S = 1 vs `S ≤ x` for x < 1: fails at 2,196 points.
  - The wrong bound `1 − S_B ≤ 1/(4x²)`: fails at 99,572 points.
  - The wrong lower bound `x ≤ S_B`: fails at 101,595 points.
- `gate_pass: true`.

## What is new vs round 1
- Round 1 had the bound `S_B ≤ √(k/2ks)`, its sharpness at `k = ks`, the closed form of `S_B²`, Bijl–Feynman exactness,
  and the `S ≡ 1` control.
- New here:
  - the closed form `S_B = k/√(ks²+k²)` as a named theorem (round 1 had it only in the verifier's scratch);
  - strict monotonicity;
  - two-sided phonon-regime bounds;
  - `S_B < 1`, the quantitative approach to the free particle `1 − S_B ≤ ks²/k²`, and the limit `S_B → 1`;
  - `ε_B = ε₀/S_B`;
  - the diffraction test in two forms: unconditional at model level, and conditional on Feynman at dispersion level,
    linked to the owner lemma `not_bogoliubov_of_structure_factor`;
  - kernel-checked positive and negative controls of the test.

## Honest scope
- These are statements about the model formulas (`S_B := ε₀/ε_B`, T = 0 Bogoliubov), not about any real fluid.
- `epsBog_eq_epsFree_div_sBog` and `feynman_sBog_exact` hold **by construction**, because `S_B` is defined as `ε₀/ε_B`.
  They are algebraic identities, not an independent many-body derivation of `S_B`.
- `diffraction_test_model` only says that a value above the envelope is not the Bogoliubov `S_B` *for that `ks`*.
  `diffraction_test_dispersion` additionally assumes Feynman's variational inequality `ε² ≤ ε_F[S]²` as the
  hypothesis `hfeyn`. That is physics input, not proved here.
- Applying the test to data requires `ks = 2mc/ħ`, which in turn needs the measured sound speed `c`. Any uncertainty in
  `c` enters the threshold `√(k/2ks)`.
- The ⁴He remark (`S(k_roton) > 0.565`) stays **conditional**: no measured S(k) dataset is held in this lane yet.
- Novelty: none in mathematics or physics. This is textbook, AM-GM-level algebra stated and kernel-checked in the owner's
  project vocabulary. Tier A is pending an independent recompile of the new file.

## Exact Lean statements (verbatim, extracted by `audit_formal.py` from the compiled file)
```lean
theorem bogoliubovSq_pos {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) :
    0 < bogoliubovSq hc ks k :=

theorem epsBog_sq {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) :
    epsBog hc ks k ^ 2 = epsFree hc ks k ^ 2 + (hc * k) ^ 2 :=

theorem sBog_pos {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    0 < sBog hc ks k :=

theorem sBog_sq {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k ^ 2 = k ^ 2 / (ks ^ 2 + k ^ 2) :=

theorem sBog_sq_le {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k ^ 2 ≤ k / (2 * ks) :=

theorem sBog_le_sqrt {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k ≤ Real.sqrt (k / (2 * ks)) :=

theorem sBog_sq_eq_iff {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k ^ 2 = k / (2 * ks) ↔ k = ks :=

theorem feynman_sBog_exact {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    (hc * k ^ 2 / (ks * sBog hc ks k)) ^ 2 = bogoliubovSq hc ks k :=

theorem sBog_sq_le_via_project {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k ^ 2 ≤ k / (2 * ks) :=

theorem free_S_one_violates {ks k : ℝ} (_hk : 0 < k) (hks : 0 < ks) (hlt : k < 2 * ks) :
    Real.sqrt (k / (2 * ks)) < 1 :=

theorem sBog_eq_closed {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k = k / Real.sqrt (ks ^ 2 + k ^ 2) :=

theorem sBog_sq_lt_sq {hc ks a b : ℝ} (hhc : 0 < hc) (hks : 0 < ks) (ha : 0 < a) (hab : a < b) :
    sBog hc ks a ^ 2 < sBog hc ks b ^ 2 :=

theorem sBog_strictMonoOn {hc ks : ℝ} (hhc : 0 < hc) (hks : 0 < ks) :
    StrictMonoOn (sBog hc ks) (Set.Ioi 0) :=

theorem sBog_lt_phonon {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k < k / ks :=

theorem phonon_lower_lt_sBog {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    k / (ks + k) < sBog hc ks k :=

theorem sBog_lt_one {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k < 1 :=

theorem one_sub_sBog_le {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    1 - sBog hc ks k ≤ ks ^ 2 / k ^ 2 :=

theorem sBog_tendsto_one {hc ks : ℝ} (hhc : 0 < hc) (hks : 0 < ks) :
    Filter.Tendsto (sBog hc ks) Filter.atTop (nhds 1) :=

theorem epsBog_eq_epsFree_div_sBog {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    epsBog hc ks k = epsFree hc ks k / sBog hc ks k :=

theorem diffraction_test_model {hc ks k S : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks)
    (hpeak : Real.sqrt (k / (2 * ks)) < S) : S ≠ sBog hc ks k :=

theorem diffraction_test_dispersion {hc ks k S epsSq : ℝ} (hhc : 0 < hc) (hk : 0 < k)
    (hks : 0 < ks) (hS : 0 < S)
    (hfeyn : epsSq ≤ (hc * k ^ 2 / (ks * S)) ^ 2)
    (hpeak : Real.sqrt (k / (2 * ks)) < S) : epsSq ≠ bogoliubovSq hc ks k :=

theorem peak_sqrt_iff_sq {ks k S : ℝ} (hS : 0 < S) :
    Real.sqrt (k / (2 * ks)) < S ↔ k / (2 * ks) < S ^ 2 :=

theorem diffraction_fires_free_at_selfdual {hc ks : ℝ} (hhc : 0 < hc) (hks : 0 < ks) :
    (1 : ℝ) ≠ sBog hc ks ks :=

theorem diffraction_silent_on_sBog {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    ¬ (Real.sqrt (k / (2 * ks)) < sBog hc ks k) :=

theorem free_S_one_violates_phonon {ks k : ℝ} (hks : 0 < ks) (hlt : k < ks) : k / ks < 1 :=

theorem nonvacuous_selfdual : sBog 1 1 1 ^ 2 = 1 / (2 * 1) :=
```

## Mechanical audit (`python -I audit_formal.py contribution/`, output in `audit_formal.out`)
```
main rc 0 sha256 fac6c85f9e6c0bd7b60861a9e1286a56283ef211d006630351ebb3c0e9e39454 decls 26 theorem headers 26 outside whitelist []
controls rc 0 ctl_sorry flagged True ctl_axiom flagged True
compile_main stdout verbatim in FORMAL.md: True
```
(The last line was produced before this section was appended; the axioms block above is unchanged.)

Known deviation: CLAUDE.md routes Lean verification through `anse/formal/lean_runner.py`. This lane followed the
task's QuantumFluids rc2 recipe instead: direct `lean` with LEAN_PATH, the same recipe as round 1, whose
independent verifier accepted it. The required checks (compile, `#print axioms` whitelist, `sorryAx` rejection,
planted controls) are covered above.
