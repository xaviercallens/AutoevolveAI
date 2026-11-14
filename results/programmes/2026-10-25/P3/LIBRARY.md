# P3 WORK1: Lean library of completely monotone and Bernstein functions

Date: 2026-10-25. Lane P3 (`cm_bernstein_library`), stage WORK1 (core). Producer-only: no independent verification yet.

- **Sources:** `formal_cert/Programmes/CompletelyMonotone/{Basic,Bernstein,Laplace,Limits,Examples,Corollaries,NegativeControls,MathlibOnly,MathlibOnlyBridge,Controls}.lean`.
- **Compiler:** pinned openai/math stack (Lean 4.34.1, Mathlib `d13f23b7`) via
  `taskset -c 4-7 python3 scripts/certified_numerics/lean_pinned.py compile FILE --olean MODULE --json-out ...`.
- **Logs:** `results/programmes/2026-10-25/P3/compile_logs/*.json` (full compiler output, rc, seconds).
- **Build:** the final dependency-ordered rebuild (`/home/callensxavier_gmail_com/programmes-2026-10-25/P3/rebuild_all.sh`)
  ran Basic → {Bernstein, Laplace, Limits} → {Examples, Corollaries, Controls} → {NegativeControls, MathlibOnly}
  → MathlibOnlyBridge, then the gate. Each module took 8.1–14.8 s.
- **Gate:** `results/programmes/2026-10-25/P3/gate.py` writes `gate.json`, with **OVERALL PASS**.
  - Every library module: rc 0, no error, no `sorry` warning, no `sorry`/`admit`/`axiom` in source.
  - **Every** `theorem`/`lemma` declared in the (comment-stripped) source has a parsed `#print axioms` entry
    (114 declared = 114 printed).
  - `MathlibOnly.lean` imports only `Mathlib.*` modules (checked).
  - Each compile log is newer than its source, and each compile started after its imports' compiles finished.
  - Source sha256 values are recorded in `gate.json`.
  - Gate self-test: before the rebuild, with Basic and Bernstein edited, the gate correctly reported stale logs and
    unprinted helpers (OVERALL FAIL).
- **Axioms:** all **114** library declarations depend on exactly `[propext, Classical.choice, Quot.sound]` (the
  whitelist). No declaration is axiom-free and none is outside it. The library logs carry zero compiler warnings.
- **Planted controls** (`Controls.lean`, imported by nothing): both compile with rc 0 and are **caught** by
  `#print axioms`.
  - `ProgCM.ctl_sorry` shows `sorryAx`.
  - `ProgCM.ctl_axiom` shows `ProgCM.ctl_cheat`.
  - Both "prove" the false statement "cos is CM", which `ProgCM.cos_not_cm` refutes.

Tier: every item below is **Tier A for the Lean statement as written**. Physical corollaries (triangular-lattice
optimality) are additionally **conditional on upstream `OAI.AtomicTriangular.universal_energy_minimum`** (openai/math,
AI-generated, not peer reviewed) and on how faithfully its definitions model the physics.

## Definitions (exact)

```lean
def ProgCM.IsCompletelyMonotoneOn (f : ℝ → ℝ) : Prop :=
  ContDiffOn ℝ (⊤ : ℕ∞) f (Set.Ioi 0) ∧
  ∀ (n : ℕ) (t : ℝ), 0 < t → 0 ≤ (-1 : ℝ) ^ n * iteratedDeriv n f t

def ProgCM.IsBernsteinOn (g : ℝ → ℝ) : Prop :=
  ContDiffOn ℝ (⊤ : ℕ∞) g (Set.Ioi 0) ∧ (∀ t : ℝ, 0 < t → 0 ≤ g t) ∧ IsCompletelyMonotoneOn (deriv g)
```

The domain is fixed to the open half-line `(0, ∞)`, and only values there matter (`congr`). The smoothness order is
`(⊤ : ℕ∞)`, copied from upstream. This is `C^∞`, not `ω`/analytic.

## Relation to upstream (exact equivalence, proved)

`ProgCM.isCompletelyMonotoneOn_iff_admissible : IsCompletelyMonotoneOn f ↔ OAI.AtomicTriangular.AdmissiblePotential f`.

Upstream's three clauses are smoothness, `g ≥ 0` and the sign condition. Its second clause is the `n = 0` case of the
sign condition. The wrappers `of_admissible` and `admissible` give each direction, and
`ProgCM.triangular_optimal : IsCompletelyMonotoneOn g → latticeEnergy g ≤ energy g C` restates upstream optimality.

## Theorem list

G = general statement; S = special case / instance; C = corollary. Axioms for all of them:
`[propext, Classical.choice, Quot.sound]`.

### Basic.lean (25 printed)

| theorem | statement | kind |
|---|---|---|
| `isCompletelyMonotoneOn_iff_admissible` | CM ↔ upstream `AdmissiblePotential` | G (bridge) |
| `IsCompletelyMonotoneOn.congr` | agreement on `(0,∞)` transfers CM (also `congr'`) | G |
| `IsCompletelyMonotoneOn.const_mul` | `c ≥ 0`: `c·f` CM | G |
| `IsCompletelyMonotoneOn.add` | `f + g` CM | G |
| `IsCompletelyMonotoneOn.mul` | `f · g` CM (Leibniz; reuses `AutoresearchYukawa.mul_sign`) | G |
| `IsCompletelyMonotoneOn.comp_add_const` | `c ≥ 0`: `t ↦ f(t + c)` CM | G |
| `IsCompletelyMonotoneOn.neg_deriv` | `-f'` CM | G |
| `IsCompletelyMonotoneOn.antitoneOn_sign` | each `(-1)^n f^{(n)}` antitone on `(0,∞)` | G |
| `IsCompletelyMonotoneOn.antitoneOn` | CM ⇒ antitone | G |
| `IsCompletelyMonotoneOn.sub_comp_add_const` | `c ≥ 0`: `f(t) - f(t + c)` CM (new; mean-value argument, no Bernstein–Widder) | G |
| `const`, `zero` | `c ≥ 0` constant / `0` CM | S |
| `sum` | finite nonnegative combination `∑ wᵢ Fᵢ` CM | G |
| `exp_neg_mul` | `a ≥ 0`: `e^{-a t}` CM (via `AutoresearchKeldysh.expNeg_admissible`) | S |
| `rpow_neg` | `s ≥ 0`: `t^{-s}` CM (via `TriangularRiesz.riesz_admissible`; `s = 0` handled separately) | S |
| `triangular_optimal` | CM ⇒ triangular lattice minimises energy (conditional on upstream) | C |

Also printed: the helpers `IsCompletelyMonotoneOn.{of_admissible, admissible, sign, nonneg, contDiffAt,
differentiableAt, differentiableAt_iteratedDeriv, hasDerivAt_iteratedDeriv, congr'}`.

### Bernstein.lean (16 printed; includes helpers `IsBernsteinOn.{contDiffAt, hasDerivAt, nonneg}`)

| theorem | statement | kind |
|---|---|---|
| `IsCompletelyMonotoneOn.comp_bernstein` | **f CM, ψ Bernstein, ψ > 0 on (0,∞) ⇒ f ∘ ψ CM** | **G (general subordination)** |
| `IsBernsteinOn.comp_sign` | its sign statement: strong induction over all CM `f`, `(f∘ψ)' = -((-f')∘ψ)·ψ'` + Leibniz (no Faà di Bruno) | G |
| `IsBernsteinOn.monotoneOn` | Bernstein ⇒ nondecreasing | G |
| `IsBernsteinOn.add`, `.const_mul` | closure under sum and nonnegative multiple | G |
| `IsBernsteinOn.comp` | Bernstein ∘ positive Bernstein is Bernstein | G |
| `IsBernsteinOn.affine` | `a, b ≥ 0`: `a t + b` Bernstein | S |
| `IsBernsteinOn.rpow` | `0 ≤ α ≤ 1`: `t^α` Bernstein | S (family) |
| `IsBernsteinOn.sqrt` | `√` Bernstein | S |
| `exp_neg_comp` | `a ≥ 0`, ψ positive Bernstein: `e^{-a ψ}` CM | C |
| `IsCompletelyMonotoneOn.comp_affine` | `a > 0, b ≥ 0`: `f(a t + b)` CM | C (requested case) |
| `IsCompletelyMonotoneOn.comp_sqrt` | `f(√t)` CM | C (requested case) |
| `phi_cm` | `κ ≥ 0`: `e^{-κ√t}` CM. **Positive control**: re-derives `AutoresearchYukawa.phi_admissible` (which needed `κ > 0` and a bespoke induction) in one line | C |

### Laplace.lean (4 printed)

| theorem | statement | kind |
|---|---|---|
| `integrable_pow_mul` | `∫ e^{-ck} m < ∞ ∀c>0` ⇒ `∫ kⁿ e^{-ck} m < ∞ ∀n, c>0` | G |
| `laplace` | `k, m ≥ 0` a.e., measurable, `e^{-ck} m` integrable ∀ `c > 0` ⇒ `t ↦ ∫ e^{-t k} m dμ` CM | G |
| `laplace_iteratedDeriv` | its derivatives are the differentiated integrals | G |
| `laplace_measure` | μ on `ℝ` concentrated on `[0,∞)`, `∫ e^{-cx} dμ < ∞ ∀c>0` ⇒ Laplace transform CM | G (easy direction of Bernstein–Widder) |

**What is new here, and what is not.**
- `laplace` *generalises* `AutoresearchKeldysh.laplace_admissible` by dropping the hypothesis that all moments
  `∫ kⁿ e^{-ck} m` are finite. Only the `n = 0` exponential integrability remains; the moments are derived.
- The analytic core (differentiation under the integral sign) is still the KeldyshCM proof, reused through the bridge.
- Measurability of `k, m` is still required. It is not weakened to `AEMeasurable`.

### Limits.lean (2 printed)

| theorem | statement | kind |
|---|---|---|
| `of_tendsto_iteratedDeriv` | the limit is assumed `C^∞`, and every `f_i^{(n)}(t)` converges pointwise to `f^{(n)}(t)` (any `NeBot` filter) ⇒ `f` CM | G, hypothesis-heavy |
| `of_tendstoLocallyUniformlyOn` | `F_k` CM; for every `n`, `F_k^{(n)} → G n` locally uniformly on `(0,∞)`; `f = G 0` on `(0,∞)` ⇒ `f` CM and `f^{(n)} = G n` there. Smoothness of the limit is **derived** (Mathlib `hasDerivAt_of_tendstoLocallyUniformlyOn`), not assumed | G |

### Examples.lean (6 printed)

| theorem | statement | kind |
|---|---|---|
| `inv_cm`, `inv_affine_cm` | `t⁻¹`, `(a t + b)⁻¹` (`a > 0, b ≥ 0`) CM | S |
| `one_add_rpow_neg_cm` | `(t + 1)^{-s}`, `s ≥ 0`, CM | S |
| `IsBernsteinOn.one_sub_exp` | `a ≥ 0`: `1 - e^{-a t}` Bernstein | S |
| `IsBernsteinOn.log_one_add` | `log(1 + t)` Bernstein | S |
| `exp_neg_log_one_add_cm` | `a ≥ 0`: `e^{-a log(1+t)}` CM (subordination by `log(1+t)`) | C |

### Corollaries.lean (12 printed): H1–H3 as short corollaries

| theorem | potential, in `t = r²` | proof |
|---|---|---|
| `riesz_cm` | Riesz `t^{-s/2}`, `s ≥ 0` | `rpow_neg` |
| `yukawa_cm` | **H2**: planar Yukawa `e^{-κr}/r`, `κ ≥ 0` (was `κ > 0`) | `riesz_cm.mul phi_cm` + `congr` |
| `dipolar_cm` | **H1**: bilayer exciton `2(1/r - 1/√(r²+d²))`, every `d` | `(rpow_neg).sub_comp_add_const.const_mul` |
| `shiftDiff_cm` | screened multipole difference `r^{-s} - (r²+c)^{-s/2}` | `sub_comp_add_const` |
| `keldysh_cm` | **H3L**: Rytova–Keldysh (mixture-defined, as in KeldyshCM) | the weakened `laplace`, using only `n = 0` integrability |
| `keldyshReg_cm` | Gaussian-regularised Keldysh | `mul` |
| `yukawa_softcore_cm` | soft-core Yukawa `g_κ(t + b²)` | `comp_add_const` |
| `stretchedExp_cm` | stretched exponential `e^{-a t^α}`, `0 ≤ α ≤ 1` | `exp_neg_comp` + `IsBernsteinOn.rpow` |
| `yukawa_admissible'`, `dipolar_admissible'` | consistency with H2/H1 through the bridge | `.admissible` |
| `triangular_yukawa_softcore_optimal`, `triangular_stretchedExp_optimal` | triangular optimality (conditional on upstream) | `triangular_optimal` |

For `yukawa_softcore_cm` and `stretchedExp_cm` (and their optimality corollaries), a case-insensitive grep for
`softcore|soft-core|soft core|stretched` over `formal_cert/`, `results/autoresearch/` and `papers/` (`*.lean`, `*.md`,
`*.tex`, excluding this library) returned no match. In that sense they have no earlier counterpart in this repo. Both
are elementary consequences of the closure lemmas. No novelty claim is made: no literature check has been done.

### NegativeControls.lean (9 printed): the definitions bite and the hypotheses are needed

| theorem | shows |
|---|---|
| `cos_not_cm` | the definition is not vacuous |
| `sqrt_not_cm` | `√` is Bernstein but not CM |
| `expNeg_not_bernstein` | `e^{-t}` is CM but not Bernstein (so the two classes differ) |
| `inv_not_bernstein` + `expNegInv_not_cm` | `t⁻¹` is CM and positive but not Bernstein, and `e^{-1/t}` is not CM: subordination needs the inner function to be Bernstein |
| `junk_cm` + `zero_bernstein` + `junk_comp_zero_not_cm` | `ψ ≡ 0` is Bernstein, `junk` is CM on `(0,∞)` with a negative junk value at 0, and `junk ∘ 0` is not CM: the hypothesis `ψ > 0` cannot be dropped in this formalisation |
| `signedMix_not_cm` | `e^{-t} - 2e^{-2t}` is not CM: mixtures need nonnegative weights |

### MathlibOnly.lean (36 printed) and MathlibOnlyBridge.lean (4 printed): an additive Mathlib-only core

`MathlibOnly.lean` (namespace `ProgCMCore`) uses **only specific Mathlib imports**: 8 `Mathlib.*` modules, with no
openai/math and no repo modules. It restates the same two definitions and proves natively the ingredients that
`Basic` borrows from repo or upstream modules.

- **Leibniz sign lemma:** `mul_sign`.
- **`exp_neg_mul`:** via `iteratedDeriv_exp_neg_mul : (e^{-a t})^{(n)} = (-a)^n e^{-a t}`.
- **`rpow_neg`:** via the Pochhammer form of the derivatives of `t^{-s}`.
- **Laplace analytic core:** ported from `Autoresearch/KeldyshCM.lean` (`G`, `hasDerivAt_G`, `contDiffOn_G`,
  `iteratedDeriv_G`, `G_sign`). `laplace` takes a `LaplaceData` structure that carries only the weakened
  exponential-integrability hypothesis.
- **Closure lemmas:** `congr'`, `const_mul`, `add`, `mul`, `comp_add_const`, `neg_deriv`, `antitoneOn_sign`,
  `sub_comp_add_const`, `const`, `sum`.
- **Bernstein instances:** `affine`, `rpow`, `sqrt`.
- **General subordination theorem:** `comp_bernstein`.

`MathlibOnlyBridge.lean` proves `ProgCMCore.IsCompletelyMonotoneOn f ↔ ProgCM.IsCompletelyMonotoneOn f` and the same
for Bernstein. Both are `Iff.rfl`, so the definitions are literally identical. Through these it obtains
`ProgCMCore.isCompletelyMonotoneOn_iff_admissible` and a transfer example, `comp_bernstein_progCM`.

**Scope of the port.** The Mathlib-only file does **not** contain:
- the limit theorems;
- `Examples`;
- the Bernstein closure lemmas (`add`, `const_mul`, `comp`, `monotoneOn`);
- `laplace_measure`, `comp_affine`, `comp_sqrt`;
- the corollaries.

It **duplicates** the code of `Basic`/`Bernstein`. The cleanup, not done here, is to make `Basic` import
`MathlibOnly` and re-export. Until then the duplication is a maintenance risk, not a soundness one, since both copies
pass the gate.

## General vs special-case: summary against the WORK1 spec

| WORK1 item | status |
|---|---|
| definition `IsCompletelyMonotoneOn` | done |
| exact relation to upstream `AdmissiblePotential` | done (**equivalence**) |
| positive scalar, sum, finite sums, product | done, general |
| limits under uniform convergence of derivatives | done: locally uniform version with derived smoothness, plus a pointwise version that assumes smoothness |
| translation `f(t + c)`, `c ≥ 0` | done, general |
| `e^{-a t}`, `t^{-s}` | done (`a ≥ 0`, `s ≥ 0`) |
| Laplace mixture lemma (generalising `laplace_admissible`) | done (weaker integrability hypothesis; measure form) |
| Bernstein definition | done |
| CM ∘ Bernstein for `√` and `a t + b` | done, as corollaries of the general theorem |
| CM ∘ Bernstein in general | **done** (with the necessary hypothesis `ψ > 0` on `(0,∞)`) |
| planted controls in a separate file, `#print axioms` recorded | done (caught) |

## What failed, what was not done, caveats

**Compile attempts.** All failures were fixed within one retry each, well inside the two-budgets-per-lemma rule.
1. `Basic`, first compile: 2 errors.
   - `neg_deriv`: an `exact_mod_cast` side goal had an unassigned order metavariable. Fixed by giving `m` explicitly.
   - `sum` (empty case): `simpa using zero` had a `0` vs `fun _ => 0` mismatch. Fixed by using `const`.
2. `Examples`, first compile: 2 errors.
   - `HasDerivAt.neg` produced Pi-negation form, so `convert` left a goal. Fixed by `const_mul (-a)`.
   - `simp only ... at ht` made no progress. Fixed.
3. `NegativeControls`, first compile: `simp` left `1 ≤ 0`. Fixed by adding `linarith`.
4. `MathlibOnly`, first compile: 2 errors.
   - `iteratedDeriv_const_mul_field` is pointwise at this pin, so `funext` had to come first.
   - `Real.pow_div_factorial_le_exp` takes `x` explicitly.

   Both were fixed on the second compile.
5. `Bernstein`, `Laplace`, `Limits`, `Corollaries`, `MathlibOnlyBridge` and `Controls` compiled on the first attempt.
6. Gate bugs, all found and fixed:
   - Names containing `'` were not parsed.
   - The `sorry` warning in this Lean version uses backticks.
   - A docstring line starting with "lemma (" was taken for a declaration; the gate now strips comments first.

**Not proved / out of scope.**
- Bernstein–Widder, the hard direction (every CM function is a Laplace transform of a positive measure).
- The theorem that a merely *pointwise* limit of CM functions is CM. It needs Bernstein–Widder or Helly selection.
- Laplace mixtures of an arbitrary CM *family* `∫ f_x(t) dμ(x)`. Only exponential kernels `e^{-t k(x)}` are covered.
- Stieltjes mixtures, and the Fourier criterion (CM 2D Fourier transform in `k²` ⇒ CM in `r²`). These are not part of
  WORK1.

**Design limits.**
- The domain is fixed to `(0, ∞)`. A Mathlib PR would want a set-parametric `IsCompletelyMonotoneOn f s` and the
  standard name/API review.
- The main library (`Basic` and everything that imports it) is **not Mathlib-only**. `Basic` imports
  `Autoresearch.KeldyshCM`, and so the upstream openai/math Triangular closure.
- A Mathlib-only **core** now exists (`MathlibOnly.lean`, see above). It covers the definitions, the closure lemmas,
  `exp`, `rpow`, the general subordination theorem and the Laplace lemma, but **not** limits, examples or corollaries.
- It is a candidate starting point for a Mathlib PR. A real PR would still need:
  - Mathlib naming and API review;
  - a set-parametric definition;
  - removal of the duplication.
- No Mathlib PR has been opened, and none will be without the user.

**Infrastructure.**
- The first `Basic` compile took 872.6 s, almost all of it importing from disk 2 under I/O contention: about 8.3 GB
  of mapped files (`.olean*` plus the toolchain), a thrashing page cache, and `full` I/O pressure of about 17%.
- After warming the closure with `warm_siblings.py`, compiles took 7–57 s. In the final rebuild every module took
  8.1–14.8 s.

**Verification status.** This is producer output only. An independent re-compile and audit of the statements
(producer ≠ verifier) is still owed before any paper wording.
