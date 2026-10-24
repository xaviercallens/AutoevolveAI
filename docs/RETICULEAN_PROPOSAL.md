# ReticuLean: proof-carrying evolution with *measured* recombination

A proposal for the next generation of this repository's AlphaEvolve line
(`anse/autopoiesis/alphaevolve_biomimetic.py`,
`.agents/skills/alphaevolve-biomimetic-workflow`), grounded in what the
Reticulata sub-project actually established and in the ten failure modes of
[`LL.md` §29](../LL.md).

Working name **ReticuLean** — reticulate evolution, Lean-checked fitness.

---

## 1. The gap this closes

The existing system already has MAP-Elites islands, NSGA-II Pareto fronts,
ε-lexicase selection, diploid dominance masking, AST homologous crossover, an
artificial immune system, and the ARGOS hardness auditors that block the obvious
specification-gaming routes. It is a capable engine. Two things are missing, and
both are things the Reticulata work supplies.

**(a) Nothing in the fitness vector is kernel-checked.** The objective is
`(latency, memory, metabolic_energy, invariant_error)` — four empirical numbers.
`ARGOS-HARD-008` blocks the crudest gaming (a function ignoring its inputs and
returning a constant), but an empirical objective is in principle always gameable,
and §29 is a two-day record of *every* un-kernel-checked gate turning out to be
forced, degenerate, or measuring the apparatus. The repository already owns the
one gate that cannot be talked around: `anse/formal/lean_runner.py`, which
compiles and then reads `#print axioms` for every declaration, rejects `sorryAx`,
and whitelists `{propext, Classical.choice, Quot.sound}`. `sorry` and a smuggled
axiom both exit zero, which is exactly why the axiom read exists.

**(b) Nobody measures whether the recombination operator does anything.**
`homologous_crossover` exists. Whether the resulting population is genuinely
recombinant, or merely a mutation-driven lineage with a crossover call in the
loop, has never been measured — and §29.2 is the rule that a mechanism which
cannot be shown to act is not evidence that it acts. This is not a hypothetical
worry: in GP generally, crossover is frequently decorative.

The second gap is the interesting one, because this repository has built,
verified and published the instrument that closes it.

## 2. The central idea: a behavioural profile *is* an aligned sequence

Reticulata detects recombination by refuting the four-point condition on a
distance derived from aligned sequences, with complete deletion *within the
subset* so every quadruple carries its own denominator, and emits a certificate
the Lean kernel rechecks.

Run each candidate program against a battery of `T` probes and record, per probe,
one symbol:

| symbol | meaning |
| :-- | :-- |
| `A` | correct output |
| `C` | incorrect output |
| `G` | raised / crashed |
| `T` | timed out |
| `-` | not applicable (probe inadmissible for this candidate) |

That is a four-state alphabet plus a gap character: **precisely the model
`subset::Alignment` already assumes**, with `-` handled by the same complete
deletion that exists for missing bases. So a `programs × probes` matrix is an
alignment, and the following apply **unchanged**:

- `subset::quadruple_counts` and `find_quartet_certificates` — exact integer
  certificates over a per-quadruple denominator;
- `splits::split_system_with` — the split-level system and its incompatible pairs;
- `emit_lean` — certificate emission for kernel recheck;
- the matched-null floor machinery, including v1.17.0's rejection sampling on the
  realised nuisance and v1.20.0's floor-convergence check.

**The null is natural and it is the right one.** A population evolved with
crossover disabled is *clonal by construction*: variation is mutation from a
single parent, so its lineage is a tree. A population evolved with crossover
enabled, at matched budget, should violate the four-point condition if crossover
is contributing. That converts "we added recombination" into a measurement with a
kernel-checkable exhibit.

> **Primary diagnostic.** Does the crossover-enabled population's quartet margin
> exceed the floor of a mutation-only population matched on realised budget and
> realised diversity? If not, the crossover operator is decorative — and that is
> worth more than another operator.

§29.7 applies immediately: the split-level form requires `C(n/2,2)^2` conjuncts,
so for population sizes beyond ~8 use the **quartet** certificate, which is the
programme's only validated instrument, and treat the split form as exploratory.

### 2.1 Phase 0 has been run, on synthetic profiles

The claim above is testable without building anything else, so it was tested
before the rest of this document was written. `reticulation profiles` was added
to expose the complete-deletion quartet path for an arbitrary matrix (the
pre-existing `fasta` subcommand routes through *pairwise* deletion, whose four
numbers are not commensurable), and
[`scripts/reticulean_phase0_demo.py`](../sub_projects/socrateai_scientific_genetic/SocrateAI-Scientific-Genetic/scripts/reticulean_phase0_demo.py)
builds two arms at matched budget: a mutation-only lineage, which is a tree by
construction and therefore the null, and the same lineage plus crossovers at
interior breakpoints. Eight candidates, 1200 probes, three seeds, mutation rate
swept:

| rate | clonal violating | recombinant violating | max clonal margin | min recomb. margin | margin separates | count separates | null varies |
| --: | :-- | :-- | --: | --: | :-: | :-: | :-: |
| 0.0005 | `[0, 0, 0]` | `[0, 0, 0]` | 0 | 0 | no | no | **no** |
| 0.0020 | `[0, 0, 0]` | `[21, 25, 27]` | 0 | 0.00342 | yes | yes | **no** |
| 0.0080 | `[13, 19, 21]` | `[37, 53, 45]` | 0.00342 | 0.00514 | **yes** | **yes** | **yes** |
| 0.0200 | `[60, 61, 56]` | `[59, 59, 65]` | 0.00685 | 0.01370 | **yes** | no | **yes** |

Three things fall out, and all three are the programme's own lessons reappearing
in a new domain.

**The mapping works.** Certificates are found on program profiles and every one
revalidates. A representative exhibit names four candidates, their six pairwise
counts and the 1168 probes at which all four were admissible — an exact integer
comparison, not a score.

**The margin is the statistic, not the count.** At rate 0.02 the violating count
fails completely (clonal 56–61 against recombinant 59–65, overlapping) while the
margin still separates by a factor of two. That is the saturation regime that
killed this programme's topology line, and the margin survives it.

**Both ends of the rate are unusable, for opposite reasons.** Below 0.002 the
clonal null produces *no violating quadruple at all*, so the comparison is
against an empty null and any positive observation is trivially "significant" —
G2 says report that as degenerate, not as a result, and the table does. Above
0.02 saturation takes the count. The usable window here is around 0.008, where
the null can vary **and** the margin separates.

**Scope.** These are synthetic profiles whose ground truth holds by construction;
the mutation-and-crossover model is hand-written and is not how a real program
population varies. This validates the instrument and locates the window. It says
nothing yet about `alphaevolve_biomimetic` output, which is Phase 0's real
target and the next step.

## 3. Fitness as a ladder whose top rungs are proofs

Replace the flat objective with a graded one, decided lexicographically from the
top so that no amount of empirical gain buys a rung:

| rung | obligation | checked by |
| :-- | :-- | :-- |
| 0 | parses, and passes the ARGOS auditors | existing |
| 1 | typechecks | compiler |
| 2 | **spec discharged in Lean 4, axioms ⊆ whitelist, no `sorryAx`** | `lean_runner.py` |
| 3 | discharged without `Classical.choice` (constructive) | `#print axioms` |
| 4 | empirical: latency, memory, energy — the current NSGA-II vector | existing |

Rung 2 is the load-bearing change. A candidate cannot climb it by passing tests,
because what is read is the axiom set of the compiled declaration. Rungs 0–1 and
4 remain gameable in principle and are therefore never allowed to outrank 2–3.

For targets without a full specification, rung 2 degrades to *partial* obligations
— a loop invariant, a monotonicity lemma, a refinement against a reference
implementation — and the ladder records which obligation was discharged, so
"verified" is never an unqualified word in a report.

## 4. Variation operators from real genetics, each with a stated purpose

Beyond the existing homologous crossover and methylation masking. Every entry
names the computational job it is hired for; an operator without one is
decoration.

| mechanism | computational analogue | why |
| :-- | :-- | :-- |
| **Gene duplication + divergence** (Ohno) | duplicate a function, let copies specialise under different probes | the dominant source of novelty in real genomes and absent from most GP; escapes a local optimum *without losing the working copy* |
| **Gene conversion** (non-reciprocal) | overwrite a region of lineage A with B's homologue, leaving B intact | propagates a rung-2-verified subroutine across the population without the reciprocal cost |
| **Horizontal gene transfer** | import a module from a *different problem's* archive | cross-task transfer at module granularity, which islands approximate only coarsely |
| **Transposable elements** | relocate a block, with a copy-number ceiling | structural reorganisation; the ceiling is the brake real genomes also need |
| **Operon formation** | co-locate functions that are always co-called | locality and cache behaviour — directly relevant to the numeric-kernel targets |
| **Synonymous rewriting** | semantics-preserving rewrites (strength reduction generalised) | *neutral* drift, which is how real populations cross fitness valleys |
| **Recombination hotspots** | learn where crossover has historically succeeded and bias breakpoints there | breakpoints are not uniform in real genomes; Reticulata's published-breakpoint work is the model |

Each operator ships with the §29.2 obligation: a demonstration that the
population measurably differs with it enabled, against a matched null. An
operator that cannot be shown to act is removed, not retained on plausibility.

## 5. Guards, each traceable to a specific failure

| # | guard | from |
| :-- | :-- | :-- |
| G1 | fitness passes a positive **and** a negative control before any run counts; a deliberately broken candidate must score strictly worse | §29.2 |
| G2 | the null reports its own spread; zero spread ⇒ BLOCKED, not a p-value | §29.2 |
| G3 | improvement must exceed a floor from a null matched on **realised** nuisance, with acceptance rate reported | §29.4 |
| G4 | the floor must be shown converged — draw more null runs until the running maximum stops rising | §29.3 |
| G5 | no uncertainty estimator that can return identically zero, or that is bounded by the statistic it bounds | §29.3 |
| G6 | exact integer comparison before any ratio; equal counts ⇒ UNRESOLVED | §29.6 |
| G7 | every reported number machine-traced to a stored artifact before publication | §29.10 |
| G8 | any check must distinguish the hypothesis from its nearest alternative | §29.1 |
| G9 | for all-must-hold criteria, state the scaling axis and validate at the real problem size; emit near-miss distributions | §29.7 |
| G10 | assert every programmatic edit applied; gate runs on build success; assert a field only new code could produce | §29.10 |
| G11 | separate RNG streams for structure and noise, or average over fixed seeds before optimising | §29.5 |
| G12 | for every gate that refuses work, report which clause binds and whether it measures the data or the apparatus | §29.9 |

## 6. What to build first

**Phase 0 — the instrument, before any new operator.** Half done: §2.1 validates
the instrument on synthetic profiles and locates the usable rate window. What
remains is the real target — emit behavioural profiles from existing
`alphaevolve_biomimetic` runs and measure whether crossover-enabled populations
are non-tree-like against a mutation-only null at matched budget. The glue is
written; the inputs are not. It is decisive either way:

- certificates appear ⇒ recombination is real, and the exhibit names which
  candidates recombined, with a Lean file the kernel rechecks;
- no certificates ⇒ crossover is decorative, which redirects the whole programme
  and is the more valuable result.

Pre-register both readings before running, per G1/G8.

**Phase 1 — rung 2.** Wire `lean_runner.py` into the fitness ladder for one
target that already has a Lean specification, and verify the ladder is
*ordinal*: a candidate that improves latency while dropping a rung must lose.

**Phase 2 — one operator, measured.** Gene duplication + divergence first: it is
the strongest candidate from biology and the easiest to measure, since a
duplicated-then-diverged pair leaves a signature the quartet certificate can see.

**Phase 3 — hotspots.** Only once Phase 0 says recombination contributes at all.

## 7. What this proposal does not claim

- **The split-level instrument is unvalidated.** It is proved (four theorems,
  module 27/27, no `sorry`) and it has zero power at 16 taxa on real data
  (§29.7). Phase 0 therefore uses the quartet certificate. The split form is
  exploratory and labelled as such.
- **The genetic analogy is a source of operators, not of authority.** Each
  operator earns its place by a measured effect, not by having a biological name.
- **Proof-carrying fitness does not make a result true.** It makes one rung
  ungameable. Rungs 0–1 and 4 remain empirical, and the ARGOS auditors remain
  necessary.
- **No benchmark numbers are claimed here.** This document proposes; it reports
  nothing. Any figure it later carries must satisfy G7.

---

### Provenance of the ideas

The reticulation machinery, its certificates and its failure modes:
[`docs/GENETICA_RETICULATA.md`](GENETICA_RETICULATA.md) §§10–20, Paper F
(10.5281/zenodo.23610116) and Paper G (10.5281/zenodo.23604793). The existing
evolution engine: `.agents/skills/alphaevolve-biomimetic-workflow`. The ten
binding rules: [`LL.md`](../LL.md) §29.
