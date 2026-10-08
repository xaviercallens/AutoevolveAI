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
