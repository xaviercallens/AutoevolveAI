# Five mathematical hypotheses from the openai/math corpus (Riemann and Hilbert)

Run 2026-10-07, branch `worktree-openai-math-discovery`. Lab: `scripts/openai_math/hypotheses/`
(autoresearch-style `program.md`, preregistration committed before every confirmatory run:
commits `27d1d93`, `542d6f5`). Results: `results/openai_math/hypotheses/`.

**Read this first.** The anchors are claims by another model (openai/math @ `adc7f124`). Two
of them have faithful Lean statements and clean static source scans, but **neither was compiled
or Comparator-checked on this machine**. Nothing below is a proof. Each hypothesis is labelled:

- **(a) corollary**: a classical implication of an upstream theorem. It would be new only because
  upstream makes it unconditional; the contribution is the derivation, here locked as a Lean target.
- **(b) conjecture**: goes beyond anything upstream claims, tested numerically with controls.

## Tools actually used

| Asked for | What ran |
|---|---|
| LeanMaster | Lean targets compiled in LeanMaster's environment (v4.34.0-rc2, its fuller Mathlib build); `leanstack search` for related theorems |
| SocrateAI Agora | Elenchus `tools/ledger.py` to tier every claim (numeric evidence caps at X, exact arithmetic at B) |
| LeanBert | **does not exist on this machine** (no file, model or Ollama tag). Nearest: the `lean_premises` Chroma index (qwen3-embedding) and `leanstack search`; only the latter was used |
| Karpathy autoresearch | its loop shape (fixed program, one runner per experiment, fixed budget, single metric, keep/discard into `results.tsv`). Candidate strategies were written by Claude in-session; no local LLM generated candidates. `anse/core/autoresearch_swarm.py` was not used (it is simulated) |
| other tools | PARI/GP 2.13.3 via cypari2, numpy/scipy, exact rational arithmetic (Python `Fraction`) |

## The anchors

| Family | Claim | Lean statement | Static scan of the proof's import closure |
|---|---|---|---|
| 003 | ζ and every Dirichlet L-function are zero-free in Re s > 7/8 ("quasi-Riemann hypothesis"); Siegel gap (1−β) log q ≥ c | faithful: uses Mathlib's own `riemannZeta`, `DirichletCharacter.LFunction` | 2,924 files, ~486k lines: no `sorry`/`admit`/`axiom` |
| 143 (part) | classical Liénard, degree ≤ 5: at most 2 limit cycles, 2 attained | faithful: definitions are plain ODE notions | 146 files: clean |
| dyadic THF | Σ_k Σ_I \|L_I\| ≤ 40 Π‖F_v‖₃ | **not formalized** | — |

The 003 claim would be historic: no fixed zero-free half-plane Re s > θ < 1 was known. The method
(Kubota–Patterson cubic theta series over Q(√−3), a sextic large sieve, reflection vs Poisson)
reaches 11/12 in Part I and 7/8 in Part II. The decisive check is a Comparator run of
`QuasiRiemannHypothesis.json` (needs the user's approval to build the OAI project, TODO 26).
Literature check (2026-10-07): the Lins–de Melo–Pugh conjecture is open at degree 5, so the
upstream quintic result would settle it; it is false from degree 6 on.

## H1 (Riemann, a): a power-saving prime number theorem

**If** ζ(s) ≠ 0 for Re s > 7/8, **then** ψ(x) = x + O(x^{7/8} log² x) and M(x) = O_ε(x^{7/8+ε}).
Classical (von Koch–Ingham for ψ; Littlewood's equivalence for the Mertens function M). With
family 003 it becomes the first unconditional power saving in the prime number theorem (the
best unconditional error today is of Vinogradov–Korobov type, exp(−c (log x)^{3/5}(log log x)^{−1/5})).
- Evidence: none numerical by design (no computable x can fail it).
- Lean: `H1_psi`, `H1_mertens` in `scripts/openai_math/hypotheses/lean/OpenAIMathHypotheses.lean`,
  stated with Mathlib's `vonMangoldt` / `moebius` and the 003 hypothesis; elaborate, `sorry`.

## H2 (Riemann, a + b): class numbers at GRH strength, with an explicit constant

(a) Under 003: L(1, χ) ≫ 1/log log q for primitive real χ, so h(D) ≫ √|D| / log log|D| — the GRH
bound of Littlewood, unconditional, and effective if 003's argument is (today's unconditional
effective bound, from Goldfeld–Gross–Zagier, is of order (log|D|)^{1−ε}).
LeanMaster overlap (`leanstack search`): `DualScaleDyons.moore_vs_hurwitz` kernel-checks Hurwitz
class numbers against reduced-form counts for D ≤ 400, a cross-check for small |D| only.
(b) Conjecture: for every fundamental D < −4, **L(1, χ_D) · log log|D| ≥ 2/5**.
- Test (preregistered): PARI class numbers for all 3,039,632 fundamental D with |D| ≤ 10⁷.
  Training minimum (|D| ≤ 10⁶) 0.40060 at D = −163; holdout minimum (10⁶ < |D| ≤ 10⁷) 0.53577
  at D = −2,383,747 → **PASS** (weak test, as preregistered: the minimum is set by small |D|).
- Informative trend: the minimum over each dyadic window stays between 0.52 and 0.64 from
  |D| ≈ 10³ to 10⁷ with no downward drift, consistent with the 1/log log order.
- Controls: all 9 Heegner discriminants found (h = 1); the wrong-order statistic min L(1, χ_D)
  does drift down (0.2197 → 0.2047); h recomputed with `quadclassunit` agrees for both minimisers.
- Night 2026-10-07: the same check over all 27,356,753 fundamental D with 10⁷ < |D| ≤ 10⁸ gives
  minimum 0.567741 → **PASS** again (finite check; see the night section below).
- Lean: `H2_order`, `H2_explicit` (targets).

## H3 (Riemann, a): uniform primes in progressions with power saving

**If** every Dirichlet L-function is zero-free in Re s > 7/8, **then**
ψ(x; q, a) = x/φ(q) + O(x^{7/8} log² x) uniformly in q and (a, q) = 1 — non-trivial for
q ≤ x^{1/8−ε}, versus (log x)^A in Siegel–Walfisz. Classical implication; unconditional only via 003.
- Evidence: none numerical by design. Lean: `H3_ap` (target).

## H4 (Hilbert's 16th, b): degree-6 Liénard systems have at most 4 limit cycles

De Maesschalck–Dumortier (2011) built degree-6 classical Liénard systems with 4 limit cycles;
no upper bound for degree 6 was found in the literature search. Conjecture: 4 is the maximum
(the degree-6 analogue of upstream's formalized quintic theorem).
- Test: Poincaré-displacement sign changes, confirmed by bisection; random and
  averaging-structured polynomials, 8 seeds × 1200 s. **Result: at most 2 confirmed cycles at degree 5 and at degree 6** over 96 + 93
  samples from the 6 seeds that finished; 2 seeds were stopped after ~90 min stuck inside stiff samples
  (the budget was only checked between samples) and produced no result. **Not refuted, low power.**
- Controls: van der Pol → 1 cycle; an averaging-built quintic → 2; random degree 3/4 never > 1.
- **Low power, stated plainly**: the search cannot reach the canard regime where the known 4
  cycles live and never reproduced 4 at degree 6. "Not refuted" here means little.
- Lean: `Lienard.H4_degree_six`, using upstream's definitions verbatim (target).

## H5 (Hilbert transform, b): the sharp dyadic triangular Hilbert constant is 5/2

Upstream proves the bound with constant 40 (not formalized). Inputs constant on dyadic squares
make every term a finite matrix trace, so the ratio can be computed exactly and maximised.
- Preregistered H5 (**C* = 2**) was **refuted** by its own run: ratio 5/2 at N = 4.
- **Rigorous lower bound C* ≥ 5/2**: a ±1 input at N = 4 evaluated in exact rational arithmetic
  gives 1 + 1/2 + 1/2 + 1/4 (scales) + 1/4 (top term) = 5/2 (`h5_exact.py verify`).
- Amended H5′ (**C* = 5/2**), preregistered before fresh-seed runs: best ratio 2.5 at N = 6
  (40 restarts) and N = 7 (12 restarts) → not refuted by that run. No source with a sharp constant was found.
- **Night 2026-10-07: H5′ is REFUTED** under its preregistered rule. The ±1 input kron(w4, w4) at
  N = 8 has exact ratio 23/8, so **C* ≥ 23/8** (exact). Exploratory, not preregistered: a product rule
  proved on paper (not Lean-checked) gives C* ≥ 3. See the night section below.
- Controls: constant input gives exactly 1; the vectorised terms equal a direct loop; the
  Haar-free form grows as N + 1.
- Lean: not stated (the dyadic form is not in Mathlib); the exact certificate is the artifact.

## Ledger (Elenchus)

`results/openai_math/hypotheses/ledger/ledger.json`, checked by Elenchus `ledger.py` with
evidence blobs verified: 15 claims (6 from 2026-10-07, 9 from the night run), no findings
(bookkeeping only; the gate licenses nothing). Gate output: `ledger/gate_check.txt`.

| Claim | Tier | Kind |
|---|---|---|
| Static scan of upstream proofs is clean | X | numeric |
| H1/H3 follow from a zero-free half-plane (classical) | L | citation |
| H2(b) holds for all fundamental \|D\| ≤ 10⁷ | X | numeric |
| **C* ≥ 5/2 (exact witness)** | **B** | exact_harness |
| Hoelder ascent found no ratio above 5/2, N ≤ 7 (a search limit: the night's tensor input gives 11/4 at N = 6) | X | numeric |
| H4: at most 2 cycles found at degrees 5 and 6 | X | numeric |
| Night: kron(w4, w4) at N = 8 has ratio exactly 23/8; H5′ refuted | **B** | exact_harness |
| Night: ±1 maximum is 1 at N = 1 and 2 at N = 2 (exhaustive) | B | exact_harness |
| Night: product rule and C* ≥ 3 (paper proof, not Lean-checked, novelty unchecked) | C | argument |
| Night: C_1 = 1, C_2 = 2, 2 ≤ C_3 ≤ 5/2 (Hoelder-marginal bound) | C | argument |
| Night: Hoelder ascent N = 5..8 never above 5/2 | X | numeric |
| Night: H2(b) holds for all fundamental 10⁷ < \|D\| ≤ 10⁸ | X | numeric |
| Night: H4 instrument passes C1–C3, N1; P4 not reproduced (PARTIAL) | X | numeric |
| Night: D1 mechanical verdicts 37/6/2 of 45 holes | X | numeric |
| Night: D1 43 of 45 holes reproduce the challenge by token or by reading | X | numeric |

No claim is Tier A: nothing here is kernel-checked, and the Lean files are `sorry` targets.

## What would turn these into contributions

1. Compile and Comparator-check `QuasiRiemannHypothesis` and `DirichletSevenEighths` (D2). If they
   pass, H1–H3 become formalization projects on top of PrimeNumberTheoremAnd, which upstream
   already depends on.
2. H5: H5′ is refuted (23/8). Next: test H5″ (C* = 3), i.e. find a ±1 g with H(g)/(1 − |T(g)|) > 3
   or an upper-bound proof of 3; check the product rule's novelty; Lean-check or review the NOTE.md proof.
3. H4: the night's slow–fast search did not reproduce 4 cycles at degree 6 (eps 0.003 only). Next:
   higher-precision integration near the A(Y) plateau, or eps 0.006–0.01 with a matched N2.
4. H2(b): checked to 10⁸. Open: certify h with an unconditional method beyond the 0.04% recheck.

## Night run 2026-10-07

Runs on 2026-10-08 between 04:29 and 05:43 UTC, after the lane preregistrations were committed in
`c1d7cd5` (04:28:43 UTC). Each lane was checked by a separate adversarial verifier
(`verification.md` in each lane directory); the wording below includes their corrections. Results:
`results/openai_math/hypotheses/night_2026-10-07/`, rows 8–20 of `results.tsv`. Lane `result.json`
files were left as the lanes wrote them, so a few figures there are less precise than here.
Where a lane says its deviations were written before the affected run, the file times cannot
confirm it (each `deviations.md` has a single modification time).

### H2(b): extension to 10⁸ — PASS

- **What ran:** PARI `qfbclassno` for every fundamental D with 10⁷ < |D| ≤ 10⁸ (27,356,753 values;
  3/π² · 9·10⁷ ≈ 27,356,720), 180 chunks, 11,984 chunk CPU-s. 11,700 D were rechecked with
  `quadclassunit`, and all agree.
- **Decision rule:** min S ≥ 2/5. The minimum is S = 0.567741 at D = −10,560,643 (h = 211), so **PASS**.
  The minimum of L(1, χ_D) is 0.20251 at D = −60,408,307. No h = 1 occurs.
- **Controls:**
  - Positive: known h(−23), h(−47), h(−71), h(−163); exactly the 9 Heegner discriminants up to 200;
    an exact regression of the earlier holdout minimum 0.5357676931072192.
  - Negative: the last-window min L (0.20325) is below the first (0.20398). That is a margin of
    only 7·10⁻⁴, and the window minima are not monotone, so this control discriminates weakly.
- **Verifier:** CONFIRMED. It re-aggregated all 180 chunks and recomputed one chunk with its own
  PARI loop, with an exact match.
- **Shows:** a finite check of H2(b) over one more decade. The new minimum (0.5677) is above the
  holdout minimum on (10⁶, 10⁷] (0.53577). That is consistent with the global minimum at D = −163
  being a small-|D| effect, but this was not tested.
- **Does not show:** H2(b) for all D. It depends on PARI's documented correctness claim for
  `qfbclassno`, which was not verified here. The recheck is GRH-conditional and covers about 0.04%
  of the range.

### H4: degree-6 canard family — PARTIAL, instrument cannot reach the known regime

- **What ran:** a new instrument, `h4_v2` (Radau two-sided displacement plus DOP853, per-step
  deadline), on a degree-6 slow–fast family. The family is a reconstruction of De Maesschalck–Dumortier;
  the paper's full text could not be obtained. Primary F0: seed 104, 3 SDI zeros.
- **Instrument controls pass:**
  - C1, van der Pol: 1 cycle.
  - C2, averaged quintic: 2 cycles.
  - C3, 20 random degree-3/4 samples: never more than 1. Sample 14 had no evaluable grid point, so
    its 0 is vacuous, and samples 5 and 13 lost 22 and 27 of 60 points. About 19 samples are
    informative.
  - N1, degree-4 SDI: 0 sign changes in the 344 of 800 trials that were scored.
- **Decision rule:** the lane positive control P4 needs at least 4 confirmed cycles at degree 6. It
  was **not reproduced** at eps = 0.003, the only one of the 6 preregistered eps values that was
  run: 1 confirmed cycle at each of the 3 preregistered levels. The 2nd and 3rd SDI zeros map to
  Y ≈ 6.79 and 16.62. Both lie in a plateau of A(Y) that is flat to about 10⁻¹⁶; A is negative
  throughout, and max |A| is at Y = 2.4655. In each count, 14–16 sign changes on the plateau were
  rejected because the two solvers disagreed in sign. N2, the degree-4 canard negative control, ran
  out of budget with 42 of 48 curve points and no counts.
- **Status:** PARTIAL. No claim about H4: it is neither refuted nor supported.
- **Theory level:** a degree-5 SDI design scored 2157 of 3000 trials and gave at most 1 sign change.
  So there is no red flag against upstream's degree-≤5 bound, but no degree-5 ODE count was run.
- **Instrument flaw found:** the level selection picked levels inside the plateau jitter band, and
  the global resolution check passed anyway. It needs a local resolution check.
- **Next:** higher-precision integration near the plateau, or eps 0.006–0.01 with a matched N2.

### H5′: refuted; C* ≥ 23/8 exactly, C* ≥ 3 on paper

- **Decision rule (preregistered):** any certified ratio above 5/2 + 10⁻⁹ refutes H5′. The ±1 input
  kron(w4, w4) at N = 8 (w4 = sign of the committed N = 4 witness) has integer-certified
  ratio³ = 12167/512, so **ratio = 23/8** and **H5′ is REFUTED**. Three checks agree on 23/8:
  `h5_exact`, a lane-written independent implementation and the verifier's own implementation.
- **Controls:**
  - Every chunk passed its controls.
  - Power control P01: the Haar-free form at N = 4 is certified at ratio 5.
  - Exhaustive ±1 search gives an exact maximum of 1 at N = 1 and 2 at N = 2 (all 32 chunks
    complete, every argmax rechecked).
- **Search that did not find it:**
  - 18 Hoelder-ascent chunks at N = 5..8 reached per-chunk bests between 2.4999186 and
    2.4999999999.
  - Walsh lifts reached at most 5/2.
  - Multi-scale sign samples reached 3/4 at N = 5 and 1/2 at N = 6.
  - So local ascent misses the tensor extremisers.
  - 7 walsh_top chunks are BLOCKED by a key-name bug in the hashed runner. They cannot reverse the
    verdict.
- **Exploratory, not preregistered:**
  - Product rule R(f ⊗ g) = H(g) + |T(g)| R(f) for ±1 f, g. It is proved on paper in the lane
    `NOTE.md`; it is not Lean-checked, and only the lane verifier has read the proof. It also held
    exactly on random pairs.
  - The tensor powers of the N = 2 maximiser (R = 2, H = 3/2, T = 1/2) give R = 3 − 2^(1−r):
    5/2, 11/4, 23/8 at N = 4, 6, 8 by `h5_exact`, and 95/32 at N = 12 by the lane's
    `verify_tensor.py` only. Hence **C* ≥ 3**, novelty unchecked.
  - Hoelder-marginal upper bounds over all real inputs give C_1 = 1 and C_2 = 2. B_1 and B_2 were
    recomputed independently. C_3 ≤ 5/2 rests on `holder_bound.py` alone.
- **Shows:** the conjectured sharp constant 5/2 is false. Upstream's constant 40 is not contradicted.
- **Does not show:** any upper bound beyond N = 3. **H5″ (C* = 3)** is a conjecture on weak
  evidence, novelty unchecked. A ±1 g with H(g)/(1 − |T(g)|) > 3 would refute it.

### D1: definition-hole bodies (Comparator anchors) — 43 of 45 reproduce the challenge, unelaborated

- **What ran:** a frozen token comparison of all 45 definition-hole bodies in the nine Comparator
  configs, challenge against the solution's import closure, at upstream `adc7f124`. This was
  followed by a review by eye. No Lean was elaborated.
- **Controls:** 98 of 98 pass.
- **Mechanical result:** 37 MATCHES, 6 DIFFERS, 2 SORRIED_IN_CHALLENGE, and nothing NOT_FOUND or
  AMBIGUOUS. The verifier's re-run was byte-identical.
- **By reading:** the 6 DIFFERS are equivalent. Their causes are a lexer artefact (`ᶜ`), redundant
  parentheses, a binder reuse the single renaming map cannot handle (2 cases), an absorbed
  `run_cmd` line, and proof-only fields. So 43 holes reproduce the challenge's definition at the
  token level or by reading.
- **Context differences:** 8 of the 37 MATCHES have a different context and are pinned by reading
  only: KServer.MainStatement, four Rokhlin holes and three SpinAngle holes.
  - Rokhlin's extra solution opens are `open scoped InnerProductSpace CStarAlgebra` and
    `open ContinuousLinearMap`.
  - KServer has an active `attribute [local instance] Classical.propDecidable Classical.decEq`,
    but MainStatement has no decidability-dependent subterm.
- **Flagged, unpinned:** DefocusingNLS.sobolevProduct (sorry only in a membership proof) and
  ElementaryPositivity.elementaryPositivityWitness (sorry-only, empty theorem list, so any inhabitant
  is accepted).
  - sobolevOddPower's pin is conditional on sobolevProduct.
  - The challenge-only DefocusingNLS opens were not scanned. A crude grep by the verifier found no
    capture.
- **Instrument:** the lane found 4 defects in the frozen script. They were handled in advisory aids
  and not fixed. `eye_review.json` was generated by `make_eye_review.py`, although the
  preregistration says it was written by hand.
- **Does not show:** Expr-level equality. That is D2 (TODO 26).


## Preprint: the sharp constant of the absolute dyadic triangular Hilbert sum is at least 3 (2026-10-08)

Published on Zenodo: **doi:10.5281/zenodo.23232389** (https://zenodo.org/records/23232389), CC-BY-4.0, with a
sha256-manifested bundle of code, exact results and witnesses. Source: `papers/dyadic_triangular_hilbert/`.

- **Proved (on paper, exact arithmetic, not machine-checked):** a product rule for Kronecker products of step
  inputs; tensor powers of one 4x4 sign seed have ratio exactly 3 - 2^(1-r), so **C\* >= 3** for the absolute sum;
  the resolution-1 constant is 1; each dyadic level contributes at most the product of the L3 norms.
- **Conjectured:** C\* = 3, in the tensor-closed form H + 3|T| <= 3 prod ||F_v||_3. Open gap: 3 <= C\* <= 40
  (the upper bound is upstream's, not verified here).
- **Scope:** the absolute sum only. On the tensor witnesses the signed per-scale form has supremum 1, 1/2, 1/4,
  1/8, so the bound does not transfer to upstream's signed form.
- **Corrected before publication** after an independent review: Lemma 3.2 had claimed monotone convergence from
  below, false unless T = 0 or R >= 1 (now stated exactly, with a test for the counterexample class); the title
  and abstract were scoped to the absolute sum; a citation was fixed against upstream's reference list.
- Next steps: TODO 31 (formalise the product rule in Lean, attack the conjecture, exhaustive Psi at N = 2).


## Night run 2026-10-08

Matrix-valued Lieb–Thirring lab (the sharp 1D constant claim, family 262, not in Lean upstream; hypotheses H-LT1 to H-LT5
as defined in each lane's `preregistration.json` and `docs/OPENAI_MATH_LT_MATRIX.md`). Four lanes ran; each was checked
by an adversarial verifier (`verification.md` per lane), and the wording below applies every correction. Results:
`results/openai_math/hypotheses/night_2026-10-08/`, rows 21–75 of `results.tsv` (renumbered from the lane files).
All lanes reported DONE with controls passing; no lane was rejected. Nothing here proves or refutes the matrix
Lieb–Thirring claim. All lane files were uncommitted when written, so preregistration ordering rests on local
commit clocks. The H1–H5 verdicts above are unchanged by this night.

### LT_A, H-LT1 at m = 2: NO_VIOLATION_FOUND in all 22 cells
- **What ran:** gamma 0.75, 1.0, 1.25, 1.4 with four starting families (random, embed, rotpair, twist), K = 2, P = 8
  (16 cells), plus 4 random K = 3, P = 10 cells and 2 twist K = 3, P = 10 cells. 336 restarts, 0 flagged above 1e-7,
  so no refinement was needed. Restart counts per cell are unequal (12 to 36).
- **Controls:** C1 to C7 re-run in the lane before any cell counted; all pass (negative controls at gamma = 3 exceed
  L1 by +15.9%; the gamma = 1.5 control stays within 2.6e-7).
- **Best excess R/L1 − 1 (always below zero):** −2.84e-7 (gamma 1.25 twist) and −3.41e-7 (gamma 1.4 twist) are the
  closest to L1; the other cells sit at −6e-7 down to −2.2e-5.
- **Autoresearch:** extra seed blocks on the K = 2 twist cells at gamma 1.25 and 1.4 (two each) and one each at
  gamma 1.0 and 0.75 raised no best. The twist K = 3, P = 10 rows were new-cell baselines and are worse than their
  K = 2 parents; they were labelled `keep` in the lane file and are `discard` in `results.tsv`. Saturation is
  established only for gamma 1.25 and 1.4 twist (two consecutive extra chunks); for gamma 1.0 and 0.75 only one ran.
- **Deviations:** a first g0.75 chunk was killed by the driver's 520 s timeout (no JSON; seeds 1040–1079 burned and
  excluded); the rest ran from a lane-owned background queue `scripts/openai_math/lt_matrix/lt_a_bg.py` that runs
  the same frozen commands. That script is untracked at preregistration time and not hash-pinned.
- **Shows:** no violation of the matrix bound at m = 2 over this finite search.
- **Does not show:** a proof. The search cannot see violations below about 1e-6: the best cells stop 2.8e-7 to 1e-6
  below L1, scalar controls stop 2e-6 to 4e-5 below it, and a third-grid recheck of the best restart moves its excess
  from −2.84e-7 to −1.97e-7 (a shift of about 1e-7, comparable to the flag).

### LT_B, H-LT1 at m = 3 and H-LT3 (second variation): no positive Hessian direction beyond tolerance
- **What ran:** Part 1: m = 3, K = 2, P = 8, 8 restarts in each of 6 cells (gamma 1.0 and 1.25; random, embed,
  twist) plus the gamma = 1.5 control. Part 2: the Hessian of log R at the embedded scalar one-soliton for gamma 0.75,
  1.0, 1.25, 1.4 and m = 1, 2, 3 (12 cells), plus gamma = 3 negative controls at m = 1, 2.
- **Part 1 outcome:** NO_VIOLATION_FOUND in all 6 cells, 0 flagged. Control max excess −2.0e-7 (not exceeded).
  Best per cell: random −1.38e-5 and −9.3e-6, embed −2.75e-6 and −1.1e-6, twist −8.2e-7 and −9.0e-7 (gamma 1.0 and
  1.25). The detection-side `controls.json` was reused, not re-run, and Part 1 has a non-exceedance control only.
- **Part 2 outcome:** NONPOSITIVE_SECOND_VARIATION in all 12 cells. Restricted lambda_max 2.9e-9, 3.5e-9, 3.1e-10,
  1.8e-10 at gamma 0.75, 1.0, 1.25, 1.4, identical for m = 1, 2, 3. Thresholds are relative (1e-6 times the spectral
  norm; 6.8e-7 to 2.7e-6), so curvature below them is declared noise by that rule. At m = 3: 122 zero modes, 40
  negative modes of 162.
- **Shows:** H-LT3 is not killed: the scalar soliton embedding has no positive Hessian direction beyond tolerance
  in the complement of translation and dilation.
- **Does not show:** that the embedding is a saddle or a local maximum. Most matrix directions are second-order flat,
  so the Hessian cannot decide local maximality there. The identical lambda_max across m is a structural property of
  the row-0 block, not independent confirmation at m = 2, 3. The gamma = 3 negative control is a weak detection check:
  theta0 is not critical there (gradient 0.43) and the control flag bypasses the VOID path. The search cannot see
  violations below about 1e-6 (the control sits 2e-7 below the sharp value).
- **Provenance:** `driver.py` and `aggregate.py` in the lane directory are unfrozen and were run uncommitted; the
  `deviations.md` note "written ~11:40" disagrees with its file time (11:33).

### LT_C, H-LT5 (dual kinetic bound) and H-LT2 (commutator structure)
- **H-LT5 ran:** an independent sine-basis search of J = Σ‖ψ_j'‖² / ∫tr ρ³ against π²/4 at gamma = 1, m = 1..3,
  N = 1..4, 12 restarts per cell (144). Controls C1, C2, C4, C5, C6 passed (C2 under an over-strict rule that was
  amended and disclosed; 10 unit tests pass).
- **H-LT5 outcome:** NO_VIOLATION_FOUND. Nothing fell below π²/4; the smallest excess is +1.49e-8 (m = 1, N = 1).
  Cells (1,3), (1,4) and (2,4) never came within 1e-5 of π²/4, so resolution there is about 1e-4. Re-evaluations on a
  2^24 grid, a doubled basis and Gauss–Legendre agree.
- **H-LT2 ran:** commutator statistic C on stored near-maximisers (snapshot at 15:00 UTC, not re-run): 345 rows, 125
  analysed (220 had no stored parameters), 59 KILLED (52 outside the gamma = 1.5 control), 47 INTERMEDIATE, 19
  PREDICTION_HOLDS; C from 0.0012 to 0.4955.
- **H-LT2 outcome:** the preregistered prediction (near-maximisers share one constant unitary) is KILLED under its
  rule: strong near-maximisers (R ≥ (1−1e-4) L1) with C > 0.05 exist.
- **Exploratory, not preregistered:** the kills are of mixed type. Most embed, twist and rotpair kills look like tail
  noise (C about 1e-3 on the core region), but one rotpair gamma = 1.4 row is a non-commuting single-channel case
  (C 0.13 to 0.17 with second-channel weight at most 0.012). Random-family kills are multi-channel (second-channel
  weight 0.027 to 0.426), but at tr W > 0.5 C is below 0.05 in 10 of 23 non-control random kills. "One constant
  unitary is too strong" and the explanation by spatially separated pieces remain hypotheses; the 220 rows without
  parameters make selection bias possible.
- **Does not show:** a counterexample to the Lieb–Thirring claim; no Tier X candidate counterexample was found.

### LT_D, Lean closure of the upstream Lieb–Thirring solution: PARTIAL at the time, since superseded
- **What ran:** the 38-file import closure of `OAI.Analysis.LiebThirring.Main` under LeanMaster's Lean v4.34.0-rc2
  toolchain; the challenge statement elaboration; Elenchus and a statement lock on the four challenge files; and the
  request document `docs/OPENAI_MATH_D2_REQUEST.md`.
- **Outcome:** 14 files compiled, 1 failed (`FiniteParity.lean:505`, unknown constant `Set.equivOfEq`), 23 blocked
  (exactly the transitive importers of the failure). The failure is consistent with version drift; the lane did not
  check upstream's Mathlib pin for that constant. The challenge file elaborates (a parse check only; it ends in
  `sorry` by design). Elenchus returned NO_FOOTPRINT on all four sorry-ended challenge files, which is expected since
  they carry no `#print axioms`. Statement lock: 101 declarations in 4 files, `--check` OK. The axiom check (part 1c)
  was not run. No Tier A claim.
- **Lane-record gaps:** only one `controls.json` exists, written after the closure, so the preregistered
  before-closure control run is not evidenced; no Elenchus control pair was run; `deviations.md` is missing (the
  closure ran as one background process, not resumable slices, and a shell variable was used); the preregistration
  was committed under the LT_A message `bdd0dcb`.
- **Later commits (after this lane, recorded for context; they are not covered by the lane verifier):** `076e04d`
  (LT_D2b) compiled 38 of 38 files under LeanMaster's toolchain after one declared rename; `a02a5f4` (LT_D3) built the
  closure under upstream's pinned Lean 4.34.1 and Mathlib `d13f23b7` with zero edits and clean axioms; `6e47561`
  (TRI_D4) did the same for the triangular closure. Per those commit messages, no Comparator run has been done yet.
- **Next:** run Comparator on the Lieb–Thirring challenge (D2 request above).

### Lanes that produced nothing
None. LT_A's first g0.75 chunk produced no result (timeout, excluded and disclosed above).

### What to do next
1. Run Comparator on the Lieb–Thirring and triangular closures (the only route to a Tier A statement).
2. For H-LT1, attack the resolution limit: nothing below about 1e-6 is visible, so a sharper instrument is needed
   before any more restarts are worth their cost.
3. For H-LT2, re-run the commutator statistic on all 345 near-maximisers with parameters stored, then test the
   spatially-separated explanation.
4. For H-LT5, raise the budget for cells (1,3), (1,4) and (2,4), which never converged to π²/4.
