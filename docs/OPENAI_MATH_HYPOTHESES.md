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
  (40 restarts) and N = 7 (12 restarts) → **not refuted**. No source with a sharp constant was found.
- Controls: constant input gives exactly 1; the vectorised terms equal a direct loop; the
  Haar-free form grows as N + 1.
- Lean: not stated (the dyadic form is not in Mathlib); the exact certificate is the artifact.

## Ledger (Elenchus)

`results/openai_math/hypotheses/ledger/ledger.json`, checked by Elenchus `ledger.py` with
evidence blobs verified: 6 claims, no findings (bookkeeping only; the gate licenses nothing).

| Claim | Tier | Kind |
|---|---|---|
| Static scan of upstream proofs is clean | X | numeric |
| H1/H3 follow from a zero-free half-plane (classical) | L | citation |
| H2(b) holds for all fundamental \|D\| ≤ 10⁷ | X | numeric |
| **C* ≥ 5/2 (exact witness)** | **B** | exact_harness |
| No ratio above 5/2 found, N ≤ 7 | X | numeric |
| H4: at most 2 cycles found at degrees 5 and 6 | X | numeric |

No claim is Tier A: nothing here is kernel-checked, and the Lean files are `sorry` targets.

## What would turn these into contributions

1. Compile and Comparator-check `QuasiRiemannHypothesis` and `DirichletSevenEighths` (D2). If they
   pass, H1–H3 become formalization projects on top of PrimeNumberTheoremAnd, which upstream
   already depends on.
2. H5′: an upper-bound proof of 5/2, or a search method that beats it (multi-scale
   initialisation, larger N).
3. H4: a slow–fast (canard) search near De Maesschalck–Dumortier's construction, so that the
   instrument first reproduces 4 cycles at degree 6.
4. H2(b): extend the computation past 10⁷ (the bound is tightest at D = −163).
