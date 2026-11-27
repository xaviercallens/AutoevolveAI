# P3 WORK2: applications of the CM / Bernstein library

Date: 2026-10-25. Source: `formal_cert/Programmes/CompletelyMonotone/Applications.lean` (module
`Programmes.CompletelyMonotone.Applications`, imports `Corollaries`). Compiled under the pinned stack (rc 0, 14.1 s, no
warnings); gate (`gate.py`, now including `Applications`) reports **OVERALL PASS**: 16 theorems declared = 16
`#print axioms` printed, all within {propext, Classical.choice, Quot.sound}; planted `ctl_sorry`/`ctl_axiom` still caught.
Producer-only (no independent verification). Physical optimality corollaries are conditional on upstream
`OAI.AtomicTriangular.universal_energy_minimum` (openai/math, AI-generated, not peer reviewed).

## 1. H1, H2, H3 re-derived with the original statements (Tier A)

| result | statement | proof |
|---|---|---|
| `H2_yukawa_admissible` | `0 < κ → AdmissiblePotential (g κ)` (original statement) | `riesz_cm.mul phi_cm`, `congr`, `.admissible` |
| `H1_dipolar_admissible` | `∀ d, AdmissiblePotential (g d)` (original `dipolar_admissible` needed `0 < d`) | `rpow_neg.sub_comp_add_const.const_mul`, `.admissible` |
| `H3_keldysh_admissible` | `0 < r0 → AdmissiblePotential (keldysh r0)` (original statement) | `keldysh_cm` (weakened Laplace lemma), `.admissible` |

### Proof-length comparison (real dependency closure, not counted by eye)

Method: Lean computes the transitive closure of constants used by each root theorem (`Closure.lean.txt`, output
`closure_raw.json`); `proof_length.py` counts non-blank, non-comment source lines in each declaration's range. Mathlib
and upstream openai/math are excluded on both sides. Definitions in the statement (`g`, `keldysh`, `w`, `erfcx`) are
included on both sides.

| potential | headline lines, original -> library | closure lines (decls), original -> library |
|---|---|---|
| H2 Yukawa | 2 -> 2 | 84 (13) -> 274 (50) |
| H1 dipolar, `dipolar_admissible` (d>0) | 23 -> 3 | 58 (8) -> 95 (17) |
| H1 dipolar, `dipolar_admissible_all` (every d) | 3 -> 3 | 72 (12) -> 95 (17) |
| H3 Keldysh | 8 -> 2 | 250 (34) -> 304 (43) |
| union of H1(all d), H2, H3 | | 406 (59) -> 505 (77) |
| union of those plus screened dipolar and Yukawa spectrum | | 406 (59) -> 527 (82) |
| union of all of those plus the two quadrupolar interactions | | 406 (59) -> 548 (87) |

**Honest reading.**
- The headline proof gets shorter only against the first version of H1 (23 -> 3) and H3 (8 -> 2). H2's original was
  already two lines (it used the earlier `admissible_mul` closure), and `dipolar_admissible_all` already used the same
  shifted-difference trick.
- **End to end the library route is longer, not shorter**: 505 vs 406 lines for the three existing results. Reasons:
  (i) `Basic.exp_neg_mul` routes through `KeldyshCM.expNeg_admissible` and so pulls in the whole KeldyshCM Laplace core
  (`G_sign` etc., about 130 lines) for every exponential-based result (the closures of H2, H3, the screened dipolar,
  both Yukawa-spectrum results and the Yukawa quadrupolar interaction contain `AutoresearchKeldysh.G_sign`; those of H1 and
  the Coulomb quadrupolar interaction do not); (ii) the general subordination theorem (`comp_sign`, about 30 lines) is
  paid for by H2; (iii) the library re-uses original helpers instead of removing them.
- H3: the weakened Laplace hypothesis (only `n = 0` integrability) is not exercised in a way that shortens anything.
  `keldysh_cm` still takes `D.integrable 0`, which comes from `keldysh_integrable` (the general-`n` bound), and the
  analytic core is still `KeldyshCM.laplace_admissible`. The hard erfcx and integrability bounds are reused, not avoided.
- Where the library pays off is **marginal cost of new results** (next section): screened dipolar plus Yukawa spectrum
  cost 22 extra lines in the union (527 - 505), and adding the two quadrupolar interactions 21 more (548 - 527).
- The Mathlib-only core (`MathlibOnly.lean`) would avoid cause (i); it was not used here.

## 2. New results (Tier A)

| result | statement | headline lines | physics reading |
|---|---|---|---|
| `screenedDipolar_cm` | `κ ≥ 0`, every `d`: `2 (g_κ(t) - g_κ(t + d²))` completely monotone | 2 | Yukawa-screened bilayer exciton; reduces to H1 at `κ = 0` (up to the `g_0 = t^{-1/2}` identification) |
| `yukawaSpectrum_cm` | `m` measurable, `m ≥ 0` on `(0,∞)`, `e^{-cκ} m` integrable on `(0,∞)` for all `c > 0` => `t ↦ ∫_{κ>0} m(κ) g_κ(t) dκ` completely monotone | 14 | continuous mixture of Yukawa screenings (e.g. a distribution of screening lengths); generalises the finite `YukawaMix` |
| `yukawaExpSpectrum_cm` | instance `m(κ) = e^{-κ}` (hypotheses checked: integrability via `integrableOn_exp_mul_Ioi`) | 9 | spectrum `e^{-κ}`; by hand (Tier C) the potential is `1/(r (1 + r))` since `∫_0^∞ e^{-κ(r+1)} dκ = 1/(r+1)`; the Tier X screen checked that closed form, and the equality with the integral is **not** proved in Lean |
| `secondDiff_cm` | `f` CM, `c ≥ 0` => `f(t) - 2 f(t+c) + f(t+2c)` CM | 6 | shifts `0, c, 2c` in `t = r²`: layers at `0, √c, √(2c)`, **not** equally spaced layers |
| `quadrupolarPair_cm` | `f` CM, `c ≥ 0` => `2 (3 f(t) - 4 f(t+c) + f(t+4c))` CM (proof: `Δ_c g + Δ_{2c} g + Δ_{3c} g` with `g = f - f(·+c)`; 4 uses of `sub_comp_add_const`, 2 of `add`, `const_mul`, `congr'`+`ring_nf`) | about 10 (general, counted by eye from the source), 3 each for the two instances (measured) | **exciton-exciton interaction of two aligned `+1,-2,+1` quadrupoles** (see §3) |
| `quadrupolarCoulomb_cm`, `quadrupolarYukawa_cm` | instances `f = t^{-1/2}` (every `d`) and `f = g_κ` (`κ ≥ 0`) | 3, 3 | unscreened and Yukawa-screened quadrupolar excitons |
| `triangular_screenedDipolar_optimal`, `triangular_yukawaSpectrum_optimal`, `triangular_quadrupolarCoulomb_optimal` | triangular optimality | | conditional on upstream |

A grep for `screened.*dipol|spectral|spectrum` over `formal_cert/Autoresearch`, `results/autoresearch`, `papers/ar_*`
found no earlier screened-dipolar or continuous-spectrum Yukawa result in this repo. **No literature search has been
done; no novelty claim is made.** Both follow in a few lines from standard closure properties.

## 3. Quadrupoles: the stage-brief candidate is a charge-quadrupole field (not CM); the exciton-exciton interaction IS CM

**Which object is which (Tier C derivation, hand-checked).** Take a pair potential `f(t)` (`t = r² + Δz²`), and quadrupoles
of charges `+1, -2, +1` in layers `z = 0, d, 2d`, with `c = d²`.
- The field of ONE quadrupole on a single test charge in layer 0 is `f(t) - 2 f(t+c) + f(t+4c)`: this is the candidate in
  the stage brief (weights `1, -2, 1`, shifts `0, d², 4d²`). **It is not completely monotone** (below).
- The INTERACTION of two aligned quadrupoles is `Σ_{i,j} qᵢ qⱼ f(t + (zᵢ - zⱼ)²)`: `Δz = 0` gives `1 + 4 + 1 = 6`,
  `|Δz| = d` gives `4 × (-2) = -8`, `|Δz| = 2d` gives `2 × 1 = 2`, so `6 f(t) - 8 f(t+c) + 2 f(t+4c) =
  2 (3 f(t) - 4 f(t+c) + f(t+4c))`. (Same bookkeeping reproduces the dipolar `2 f(t) - 2 f(t+d²)`.) **This is completely
  monotone** for every CM `f`: Laplace factor `3 - 4x + x⁴ = (1 - x)(3 - x - x² - x³) ≥ 0` on `[0,1]`, and in Lean it is
  `Δ_c g + Δ_{2c} g + Δ_{3c} g` (`Theorem quadrupolarPair_cm`, Tier A). The triangular-lattice theorem therefore applies
  to the quadrupolar exciton gas (conditional on upstream), with Coulomb or Yukawa pair potential. The classical-point-charge
  modelling (rigid aligned quadrupoles) is the same Tier C assumption as for H1.

**Charge-quadrupole combination `f(t) - 2 f(t+c) + f(t+4c)` is not CM.**
- **Tier X** (`applications/cm_numeric_check.py`, mpmath, 60 digits, `n = 0..7`, 15 values of `t` in `1e-3..1e4`): minimum
  signed value `-0.0443` at `n = 0`, `t = 3.16`, `c = 1`. Controls: positive controls (Riesz, Yukawa) show no negative
  value; negative controls (`cos`, the dipolar sign-flip `h_d`, the signed Yukawa mixture) all show a negative value.
  The same screen reports no negative value for `seconddiff_0_c_2c`, `screened_dipolar` (two parameter sets),
  `yukawa_exp_spectrum` and `yukawa_box_spectrum`; that is consistent with, and never a proof of, their CM status
  (the proofs are the Lean theorems above).
- **Tier A:** `quadrupole_neg_at_three` (value at `t = 3, c = 1` is negative: `1/sqrt 3 - 1 + 1/sqrt 7 < 0`, using
  `sqrt 3 > 1.7`, `sqrt 7 > 2.6`) and `quadrupole_not_cm`; `quadrupoleC_not_cm` extends this to **every** `c > 0` by the
  scaling `t ↦ c t` (`comp_affine`).
- Reason (Tier C): the weights `1, -2, 1` have zero mean but nonzero second moment in the layer distance, so the far
  field is `-d²/r³ < 0`; admissibility needs a nonnegative potential. So the triangular-lattice theorem does not apply to
  this charge-quadrupole function (which is not the interaction between two excitons).
- **Tier X for the interaction** (same screen): `quadrupolar_pair_interaction_c1` and its Yukawa-screened version
  (`kappa = 1`) show no negative value; the control `2 f(t) - 3 f(t+c) + f(t+4c)` (wrong weights, zero total charge) shows
  a negative value (`-0.0048` at `n = 0`, `t = 10`), so the screen does distinguish.

## 4. Files

- `formal_cert/Programmes/CompletelyMonotone/Applications.lean`, `results/programmes/2026-10-25/P3/compile_logs/Applications.json`
- `results/programmes/2026-10-25/P3/gate.py` (updated), `gate.json`
- `results/programmes/2026-10-25/P3/applications/{cm_numeric_check.py,numeric_check.json,Closure.lean.txt,closure_raw.json,proof_length.py,proof_length.json,proof_length_union.json}`
- `results/programmes/2026-10-25/P3/MATHLIB_READINESS.md`
