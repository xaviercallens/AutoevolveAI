# P3: Mathlib readiness of the completely monotone / Bernstein library

Date: 2026-10-25. Lane P3, stage WORK2. **No PR has been opened, no Zulip post made, nothing pushed.** This document is
for the user to decide. Everything about the library is producer-only (AI-written, compiled and axiom-checked here, no
independent audit, no human Lean expert has read it).

## 1. Duplicate check against the pinned Mathlib (`d13f23b7`, commit date 2026-09-24)

Greps over `Mathlib/` of the pinned checkout (`openai_math_pinned/lean/.lake/packages/mathlib`):

| search | result |
|---|---|
| `completelyMonotone`, `completely monotone`, `IsBernstein`, `bernstein function` | **no hits** |
| `Widder`, `totally/absolutely monoton` | one file: `Mathlib/Analysis/Calculus/AbsolutelyMonotone.lean` |
| `bernstein` (case-insensitive) | `RingTheory/Polynomial/Bernstein.lean`, `Analysis/SpecialFunctions/Bernstein.lean` (Weierstrass via Bernstein polynomials) and some unrelated mentions |
| `Laplace` | hits only by file name in `Analysis/Distribution/DerivNotation.lean` and matrix determinant files; **not inspected** beyond the file names, so I cannot say they are unrelated to the Laplace transform |

**The important finding: `Mathlib/Analysis/Calculus/AbsolutelyMonotone.lean` already exists** (Michael R. Douglas, 2025,
cites Widder's *The Laplace Transform*). It defines `AbsolutelyMonotoneOn (f : ℝ → ℝ) (s : Set ℝ)` through the existence
of a Taylor series with nonnegative terms (`HasFTaylorSeriesUpToOn ∞ f p s`), and proves only: `contDiffOn`,
`of_contDiff`, `iteratedDerivWithin_nonneg`, `iff_iteratedDerivWithin_nonneg` (under `UniqueDiffOn`), `add`, `smul`.
It has no product, composition, translation, examples, Bernstein functions, or Laplace transforms.

Consequences:
- Our `IsCompletelyMonotoneOn f` (on `(0, ∞)`) is not in Mathlib, but a PR must be built *on* `AbsolutelyMonotoneOn`
  (e.g. `CompletelyMonotoneOn f s := AbsolutelyMonotoneOn (fun x => f (-x)) (-s)`, with the sign convention checked), not
  beside it. A reviewer will ask for exactly that.
- Our `add` and `const_mul` would then be corollaries of the existing `AbsolutelyMonotoneOn.add` and `.smul`.
- Our `mul` (Leibniz sign lemma) has **no counterpart** in the existing file, so a product lemma for
  `AbsolutelyMonotoneOn` is a natural first contribution.
- `bernsteinPolynomial` and the namespace `bernstein` already exist. Our `IsBernsteinOn` (Bernstein *function*: `C^∞`,
  `g ≥ 0`, `g'` completely monotone) is a different notion with a confusable name; a better name is needed (for example
  `BernsteinFunctionOn`).
- Mathlib files now use the module system (`module` header, `public import`, `public section`). All our files use plain
  `import`.

## 2. Lemma by lemma

"Generic" = statement and proof use Mathlib only (the `MathlibOnly.lean` core, namespace `ProgCMCore`, 8 `Mathlib.*`
imports, compiled and in the gate). "Repo" = currently depends on openai/math or other repo modules.

| lemma(s) | generic? | changes needed |
|---|---|---|
| definition `IsCompletelyMonotoneOn` | generic, but wrong shape | rebase on `AbsolutelyMonotoneOn`, make set-parametric (`s`, with `UniqueDiffOn` or open `s` hypotheses), drop `Is`, drop `ProgCM` namespace |
| definition `IsBernsteinOn` | generic | rename (see above); set-parametric |
| `mul_sign` / `mul` (Leibniz) | generic (`MathlibOnly`) | state for `AbsolutelyMonotoneOn`; likely needs `iteratedDerivWithin_mul`-style lemmas on `s` (not checked whether they exist at this pin) |
| `add`, `const_mul`, `sum`, `const`, `zero` | generic | `add`/`smul` already in Mathlib for `AbsolutelyMonotoneOn`; keep only `sum` and `const` |
| `congr`, `congr'` | generic | merge into one `congr` with `EqOn` |
| `comp_add_const`, `sub_comp_add_const` | generic | the mean-value argument for `sub_comp_add_const` is short; keep |
| `neg_deriv`, `antitoneOn_sign`, `antitoneOn`, `nonneg`, `contDiffAt`, ... | generic | API lemmas; rename per Mathlib conventions (`deriv`-related names) |
| `exp_neg_mul`, `rpow_neg` | generic (`MathlibOnly` versions, no repo import) | the `Basic.lean` versions import repo modules, so only the `MathlibOnly` versions are candidates |
| `comp_bernstein` + `IsBernsteinOn.comp_sign` | generic (`MathlibOnly`) | main new theorem; about 30 lines of strong induction; deserves its own PR |
| `IsBernsteinOn.{affine, rpow, sqrt}` | generic (`MathlibOnly`) | ok |
| `IsBernsteinOn.{add, const_mul, comp}`, `monotoneOn` | **repo** (only in `Bernstein.lean`, not in the Mathlib-only file) | port to the core |
| `Limits` (`of_tendstoLocallyUniformlyOn`) | **repo** (imports `Basic`) | port; derived smoothness uses Mathlib `hasDerivAt_of_tendstoLocallyUniformlyOn` |
| `laplace` (weakened integrability) | generic core in `MathlibOnly` (`LaplaceData`), the stated `laplace` in `Laplace.lean` is **repo** (routes through `AutoresearchKeldysh.laplace_admissible`) | use `AEMeasurable` instead of `Measurable`; about 150 lines, separate PR |
| `laplace_measure` | **repo** | port |
| `Examples`, `Corollaries`, `Applications`, `NegativeControls` | repo / physics-specific | do **not** belong in Mathlib (physical potentials, upstream optimality). Negative controls could become tests (`MathlibTest/`) |

Statistics (from `LIBRARY.md` and this stage): the main library has 130 theorems checked by the gate (114 from WORK1 +
16 in `Applications`); the Mathlib-only core has 36 `theorem`/`lemma` declarations, all 36 with an axiom printout
at gate time (gate: declared = printed = 36).

## 3. Style and convention changes (not yet done)

1. Module header, `public import`, copyright/authors header, `/-! # Title ## Main definitions ## Main results ## References -/`.
2. Line length: 22 lines over 100 characters in `MathlibOnly.lean` (maximum 117), 24 in `Basic.lean`.
3. `Corollaries.lean` contains a `try simp only []` (flexible, would be flagged); not in the Mathlib-only core.
4. `(⊤ : ℕ∞)` should become `∞` with `open scoped ContDiff`, matching `AbsolutelyMonotone.lean`.
5. Every declaration needs a docstring; `lemma` vs `theorem` use to be aligned; `Measurable` to `AEMeasurable` in Laplace.
6. Remove the duplication between `Basic`/`Bernstein` and `MathlibOnly` (make the former import the latter).
7. **Linters not run.** Mathlib's style and environment linters (`lake exe lint-style`, `#lint`) have not been run on
   these files. The only checks done are compilation under the pinned Lean 4.34.1 and the `#print axioms` gate.
8. Suggested PR split (smaller PRs are easier to review): (a) definition on `AbsolutelyMonotoneOn` plus
   `mul`/`comp_add_const`/`sub_comp_add_const`; (b) `exp`, `rpow` instances; (c) Bernstein functions and
   `comp_bernstein`; (d) Laplace transform of a nonnegative measure. This is my suggestion, not a Mathlib requirement.

## 4. Dependencies

- `MathlibOnly.lean` imports exactly: `Analysis.Calculus.IteratedDeriv.Lemmas`, `Analysis.Calculus.Deriv.MeanValue`,
  `Analysis.Calculus.ParametricIntegral`, `Analysis.SpecialFunctions.Pow.Deriv`, `Analysis.SpecialFunctions.Sqrt`,
  `Analysis.SpecialFunctions.ExpDeriv`, `Analysis.Complex.Exponential`, `RingTheory.Polynomial.Pochhammer`
  (all under `Mathlib.`). No openai/math, no repo module.
- A PR rebased on `AbsolutelyMonotone.lean` would additionally import `Mathlib.Analysis.Calculus.AbsolutelyMonotone`.
- The pin is Mathlib `d13f23b7`; a PR targets current `master`, so lemma names used by the proofs (for example
  `iteratedDeriv_const_mul_field`, `Real.pow_div_factorial_le_exp`, whose signatures already needed adjustment once)
  may have moved. Not checked against current `master`.

## 5. Mathlib's policy on AI-generated contributions

Source: the leanprover-community contribution page, section "Use of AI":
<https://leanprover-community.github.io/contribute/index.html>, fetched 2026-10-25.

**Limit of this quotation.** The page was read through a fetch tool that summarises and returns quotations of at most
125 characters. I therefore could not obtain the whole section word for word. The fragments below are the verbatim
quotations the tool returned (same fragments in two independent fetches); the paraphrases are marked as such. **Read the
section yourself before deciding.** A search for an official Mathlib AI policy elsewhere (web search) found nothing
authoritative; a direct fetch of `mathlib4/CONTRIBUTING.md` on GitHub returned 404.

Verbatim fragments:
- "Using artificial intelligence tools to generate code is becoming more and more common."
- "Using an LLM when writing comments on GitHub or Zulip is not allowed: use your own words."
- "Members of the review team will summarily close without comment any low quality PR produced using LLMs"
- "code written by an AI without the supervision of a Lean subject expert fails to meet that bar by a large margin."
- "It is essential that you understand all the content written by an AI."
- "you must explain this in the PR description. Explain which tool(s) you used and how you used it."
- "If your PR contains a substantial amount of LLM-generated code, add the `LLM-generated` label"

Paraphrase (fetch tool's summary, not verbatim): repeat low-quality submitters may be suspended or banned from PRs and
Zulip; contributors must be able to justify design decisions without AI assistance; AI use must be disclosed in the PR
description.

**What this means for this library (my reading, for you to judge).**
- The whole library, the proofs and the docstrings were written by an AI (Claude) and have not been read by a Lean
  subject expert. Under the quoted text it would fall in the category the page warns about unless a human who understands
  every line takes ownership.
- Any PR would need: a human author who understands and can defend all of it; disclosure of the tool in the PR
  description; the `LLM-generated` label; and the PR description and all GitHub/Zulip comments written by the human in
  their own words (so I should not draft those comments).
- The existing `AbsolutelyMonotone.lean` has an active author; the natural first step is a human conversation with the
  Mathlib community (for example whether the product lemma and `CompletelyMonotoneOn` are wanted), not a large PR.
- Alternatives that need no policy decision: keep the library downstream (it already imports cleanly, and
  `MathlibOnly.lean` shows it needs only Mathlib), or publish it as a standalone Lean package with the AI provenance stated.

## 6. Decision options

1. **No Mathlib PR**: keep as the downstream repo library (cost: none).
2. **Human-led small PR**: you (or a Lean-fluent collaborator) review `MathlibOnly.lean`, rebase on
   `AbsolutelyMonotoneOn`, run the Mathlib linters, and open PR (a) of section 3.8 with the disclosure and label. Cost:
   a real review and rewrite, plus the linter and name checks listed above; the review of statements is the part I cannot do.
3. **Ask first**: a human posts a short question on Zulip about whether `CompletelyMonotoneOn`/Bernstein functions are wanted.
