# Proof-Carrying Discovery — a proposal for verified computational science

**Status:** proposal with a working pilot, 2026-10-25. Builds on Kernel-Gated Evolution
(Paper J, concept DOI [10.5281/zenodo.23635678](https://doi.org/10.5281/zenodo.23635678))
and the cross-repo roadmap ([`KGE_EXTENSION_ROADMAP.md`](KGE_EXTENSION_ROADMAP.md)).

## 1. What the rusty-SUNDIALS example actually showed

The roadmap named rusty-SUNDIALS' integrators as the strongest new domain. The pilot was run
rather than described (`scripts/kge_bdf_pilot.py`, `scripts/kge_certify_sundials_bdf.py`):

| step | result |
|---|---|
| Solve BDF-k coefficients from the order conditions, exactly over ℚ, k = 1..8 | BDF2 `b = 2/3`, BDF3 `b = 6/11` **match the textbook**; no search needed |
| Prove every order condition in Lean (`formal/ANSE/AlixBDF.lean`) | **9/9 gated**, incl. a negative control: BDF2 with one coefficient off by 1/100 provably fails |
| Certify rusty-SUNDIALS' **production** `BDF_L` table (`crates/cvode/src/solver.rs`) against two independent derivations | **all 5 rows match exactly**; each row proved as a polynomial identity (`formal/ANSE/AlixSundialsBDF.lean`, **5/5 gated**) |
| Check zero-stability (numerically, labelled) | BDF1–6 stable; **BDF7 and BDF8 satisfy every order condition yet are not zero-stable** (max root modulus 1.0222, 1.1839) |

Three lessons, each of which changes the approach:

1. **When the specification is affine in the parameters, exact solving replaces search.** The
   "lifetime learning" step of KGE is not a refinement here — it is the whole computation. Search
   is only needed over *structure* (which coefficients may be nonzero): the 4-step structure search
   found 15 stencils admitting an exact method, decided by linear algebra alone.
2. **A kernel can certify existing artefacts, not only new ones.** The most immediately useful
   result was not a discovered method but a *certificate for constants already shipping* in a
   numerical library — and the same pass caught a wrong doc comment (`l[0] = 1 always`; it is l[1]).
3. **The kernel proves exactly what was specified, and the specification was incomplete.**
   BDF7 passes every order condition the kernel checks and is useless. This is not a flaw of the
   kernel; it is the frontier of trust moving from *proof* to *specification completeness*.

## 2. Improvements to KGE that follow

1. **Structure search × exact solve.** Add a mode to the crate that enumerates structures
   (stencil supports, monomial sets, operator skeletons) and solves the affine parameters exactly,
   falling back to tree evolution only where the specification is not affine. On SRSD-Feynman this
   is the hybrid the paper's future-research section motivated (dense regression needs ~35 points,
   the search 12).
2. **Multi-property specifications with tiers.** A candidate carries a ledger: properties *proved*
   (kernel), *measured* (numerical, with method stated), *assumed* (named, unchecked). BDF7 would
   read: order 7 — proved; zero-stability — measured, **fails**.
3. **Certification mode for existing code.** Parse constants from source *exactly* (fractions as
   written, never via the float), check them against independent derivations, emit Lean
   identities. Cheap, high-value, and applicable today to every numerical table in your repositories.
4. **Prove the missing property.** Zero-stability for fixed k is a root condition on an explicit
   polynomial; proving BDF1–6 stable (and BDF7 unstable, by exhibiting a root outside the unit disc)
   in Lean would make the certified BDF family complete.
5. **Variance health and the one-invocation gate** stay as they are: they made the search and the
   verification affordable and diagnosable.

## 3. The proposal: Proof-Carrying Discovery with Adversarial Specification Closure

Modern verified science has two halves that rarely meet: **generators** (LLMs, evolution,
symbolic regression) that propose results cheaply and are often wrong, and **proof kernels** that
are perfectly reliable about the statement they are given. The BDF7 result shows where the
remaining risk lives: not in the proof, but in whether the statement proved is the one that
matters. The proposal is to make that risk *searchable*.

**The loop.**

1. **Specify exactly** — the property in Lean, plus an *independent empirical oracle*
   (simulation, data, or a numerical check) that encodes what the specification is meant to capture.
2. **Generate freely** — any generator; it is never trusted.
3. **Solve exactly** — every parameter the specification makes affine is solved in closed form
   (`v* = v + (want − out)/B`; linear systems over ℚ).
4. **Gate in one invocation** — batched kernel verification reading the per-declaration report,
   a planted wrong candidate in every batch.
5. **Red-team the specification** *(the new step)* — point the **same generator at the
   specification itself**: search for candidates the kernel *accepts* but the empirical oracle
   *rejects*. Each one is a **specification gap**. BDF7 is the worked example — the structure search
   produced it automatically, the kernel proved its order, and the stability oracle rejected it.
6. **Close the gap** — add the missing property to the specification (zero-stability), prove it,
   and repeat until red-teaming finds nothing within budget. Report the **spec-gap rate** alongside
   the result.
7. **Ship a certificate ledger** — proved / measured / assumed, each claim traced to an artefact by
   a provenance gate that blocks publication on any mismatch.

**Why this is a step beyond kernel-gated search.** Kernel-gated search answers *"is this
candidate correct?"* with certainty. Adversarial specification closure answers the question a
scientist actually asks — *"is 'correct' the right word for what I specified?"* — with evidence
and a measurable stopping rule. It turns the generator, usually the untrusted part, into the
instrument that tests the trusted part's assumptions.

## 3b. Result: the loop run end to end on linear multistep methods

`scripts/kge_spec_closure_bdf.py`, `results/kge_spec_closure_bdf.json`. A structure-search generator
(every support of a k-step BDF-type stencil, k ≤ 7, coefficients solved exactly for the highest
order the support admits) produced **247 candidates, each satisfying its order conditions**. Two
specifications were red-teamed by an **independent oracle** — the definition of zero-stability
itself, simulated: run `Σ aⱼ y_{n+j} = 0` from unit-vector starts and reject unbounded growth.

| specification | accepts | red-team gaps (kernel-acceptable, oracle-rejected) |
|---|---:|---:|
| v1 — order conditions only (what Lean proves today) | 247 | **94 (38.1%)** |
| v2 — order conditions + exact root condition (Schur–Cohn / cyclotomic over ℚ) | 153 | **0** |

Over-strictness (v2 rejects a stencil the oracle accepts): **0**. The two mechanisms — exact algebra
and simulation — share no code, and agree on all 247. Highest zero-stable order by step count: k
for k ≤ 6, and **6 for k = 7**, so the BDF7 failure generalises into a barrier visible in the data.

**Three errors of mine along the way, each caught by a control rather than by inspection:**

1. *Blind starts.* A first diagnostic started from the all-ones vector and reported peak |y| = 1
   forever. For any consistent method that vector is the constant solution (Σaⱼ = 0), so it excites
   only the z = 1 mode and cannot see an unstable root. The oracle uses unit-vector starts.
2. *Too short a horizon.* A 400-step oracle accepted BDF7 (peak 1.7×10⁴, under its 10⁶ bound); the
   control "BDF7 must be rejected" failed, which is how it was found. At 1000 steps the peak is
   9.6×10⁹. The oracle now runs 2000 steps and its blind spot is stated: it catches root moduli
   above about 1.006 and would miss a root at 1.001.
3. *An over-strict exact test.* The first `zero_stable_exact` required every non-unit root strictly
   inside the disc, which rejects weakly stable methods (leapfrog, ρ = z² − 1). Its own control —
   agreement with numeric roots on BDF1–8 — could not catch this, because none of those has a weak
   root; the over-strictness check did (31 disagreements, all exactly simple on-circle roots). It now
   strips cyclotomic factors exactly (Kronecker), requires each at most once, and runs Schur–Cohn on
   the remainder. `tests/unit/test_zero_stability_exact.py` (6 tests) pins the controls that would
   have caught it: leapfrog accepted, `(z−1)²` and `(z²+1)²` rejected, BDF1–6 accepted, BDF7/8 rejected.

**What this does and does not show.** It demonstrates that specification gaps are *findable by the
generator* and that closing one removes them from this candidate set. It does not show completeness
of v2 in general. The oracle is finite-horizon, and the candidate set is one family.

### 3c. Kernel-proved instability of BDF7 and BDF8

The open item was a Lean proof of zero-stability. Half of it is now closed
(`formal/ANSE/AlixStability.lean`, **103 declarations through `lean_runner`, 0 `sorry`, whitelist axioms
only**): **BDF7 and BDF8 each have a characteristic root outside the unit disc.**

The intermediate value theorem cannot do this, because the offending roots are a complex-conjugate pair
(modulus 1.0222 and 1.1839). The certificate is instead a *power sum*: if every root of a degree-n
polynomial lies in the closed unit disc then `|s_m| ≤ n` for every `m`, where `s_m = Σ zᵢᵐ`. The `s_m`
are rational — Newton's identities with Vieta give `s_1 … s_{n-1}` from the coefficients, and the
recurrence the roots force gives the rest — so one index with `|s_m| > n` proves a root outside the disc
without locating it. BDF8 is certified at `s₈ ≈ 8.7147 > 8`, BDF7 at `s₅₉ ≈ 8.0379 > 7`
(`results/kge_stability_certificates.json`). The instance proofs are generated from exact arithmetic by
`scripts/kge_gen_stability_lean.py`, never typed.

Controls: BDF1–6 produce **no certificate** within 400 terms (their `|s_m|` stays ≤ k), the Newton-based
sums agree with power sums of the numerically computed roots, and 13 unit tests pin all of this.

**Still open, and why it is the harder half.** Zero-stability of BDF1–6 needs the *opposite* inclusion —
every root inside the disc and the unit-circle roots simple. A bounded power sum is necessary for that,
not sufficient, so this certificate cannot give it. It needs either a formalised Schur–Cohn theorem or a
different witness. It remains decided *exactly* by `kge_spec_closure_bdf.py`, and unproved by the kernel.
The Dahlquist equivalence between the root condition and bounded solutions is also not formalised.

## 4. Next experiments, with the controls that make them count

| experiment | success criterion | controls |
|---|---|---|
| ~~Lean proof of instability for BDF7/8~~ **done** (§3c). Open: Lean proof of zero-stability for BDF1–6 | Schur–Cohn soundness, or another witness for "all roots inside" | a perturbed coefficient that breaks stability must fail to certify |
| Spec red-team on BDF: generator searches stencils passing order conditions | finds a stable/unstable split; spec gap rate reported before and after adding stability | random stencil sampling as the naive baseline |
| Certification mode across all numerical tables in rusty-SUNDIALS (Adams, error constants `BDF_ERR_COEFF`, RK tableaux) | every table either certified or a discrepancy named | a planted typo in a copy of the table must be caught |
| Structure search × exact solve on SRSD-Feynman | beats tree evolution at matched total work | restart hill-climber and random search on the same budget |
| Runge–Kutta order conditions (nonlinear in coefficients) | recover RK4 and a 3-stage order-3 family | the affine-solve step must be shown insufficient here, motivating search |

## 5. Limits, stated once

Zero-stability above was checked numerically, not proved. Only constant-step BDF was certified
(variable-step coefficients depend on the step history). The proposal's red-teaming step needs an
empirical oracle that is itself trusted; where none exists, the ledger's *assumed* tier is the
honest answer.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
