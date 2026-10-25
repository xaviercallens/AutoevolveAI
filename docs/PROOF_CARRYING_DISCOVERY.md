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

## 4. Next experiments, with the controls that make them count

| experiment | success criterion | controls |
|---|---|---|
| Lean proof of zero-stability for BDF1–6 and instability for BDF7 | 7 theorems gated | perturbed coefficient that breaks stability must fail |
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
