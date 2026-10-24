---
name: reticulean-evolution
description: Run or extend ReticuLean — proof-carrying evolutionary program synthesis with MEASURED recombination. Treats a program's behavioural profile over a probe battery as an aligned sequence, so the Reticulata quartet certificate decides whether a crossover operator actually recombines or is decorative; adds a Lean-4 rung to the fitness ladder that cannot be gamed by passing tests; and enforces the twelve guards of LL.md §29. Use when adding a variation operator to anse/autopoiesis/alphaevolve_biomimetic.py, when asked whether crossover contributes, or when a fitness function needs a gate an optimiser cannot talk around.
---

# ReticuLean: proof-carrying evolution with measured recombination

Full rationale: [`docs/RETICULEAN_PROPOSAL.md`](file:///home/xavkal/xdev/AutoevolveAI/docs/RETICULEAN_PROPOSAL.md).
Binding rules: [`LL.md`](file:///home/xavkal/xdev/AutoevolveAI/LL.md) §29.
This skill is the operating procedure; it does not restate the argument.

## 1. The two additions to the existing engine

The AlphaEvolve engine (`alphaevolve-biomimetic-workflow`) already has MAP-Elites
islands, NSGA-II, ε-lexicase, diploid masking, AST homologous crossover, AIS
negative selection and the ARGOS auditors. ReticuLean adds exactly two things:

1. **A fitness rung that is kernel-checked**, so no empirical gain can buy it.
2. **An instrument that measures whether recombination happens**, so no operator
   is retained on plausibility.

## 2. Behavioural profiles are alignments — the mapping

Run each candidate against `T` probes; emit one symbol per probe.

| symbol | meaning |
| :-- | :-- |
| `A` | correct output |
| `C` | incorrect output |
| `G` | raised / crashed |
| `T` | timed out |
| `-` | probe inadmissible for this candidate (the gap character) |

Write the `programs × probes` matrix as FASTA, one record per candidate. It is
then a valid `subset::Alignment`: four states plus a gap, with complete deletion
within the subset giving every quadruple its own denominator.

```bash
cd sub_projects/socrateai_scientific_genetic/SocrateAI-Scientific-Genetic
# Complete-deletion quartet certificates on a profile matrix (the right path).
# NOT `fasta`: that subcommand uses PAIRWISE deletion, whose four numbers share
# no denominator and are not commensurable.
./rust/reticulation/target/release/reticulation profiles <profiles.fasta> --top 5

# Phase 0, already runnable: synthetic clonal-vs-recombinant arms, rate swept.
python scripts/reticulean_phase0_demo.py --out data/reticulean_phase0
```

Phase 0 on synthetic profiles is **done** and reported in the proposal §2.1: the
mapping works and every certificate revalidates; the **margin** separates the
arms where the violating **count** fails under saturation; and both rate extremes
are unusable — too low and the null is degenerate, too high and saturation wins.
Locate that window before reading any count as a result.

**Use the quartet certificate, not the split system.** The split-level form is
proved but has zero power at 16 taxa on real data, because its conjunct count is
`C(n/2,2)^2` — 36 at n=8 but 784 at n=16 (LL.md §29.7). Treat it as exploratory
and say so in any report.

## 3. The primary diagnostic, and how to run it honestly

> Does the crossover-enabled population's quartet margin exceed the floor of a
> **mutation-only** population matched on realised budget and realised diversity?

A mutation-only population is clonal by construction, so its lineage is a tree
and its profile matrix should satisfy the four-point condition up to noise. The
procedure:

1. **Pre-register both readings** before running (G1, G8): certificates appear ⇒
   recombination is real, with a named exhibit; none appear ⇒ crossover is
   decorative, which is the more valuable finding.
2. Run crossover-enabled and crossover-disabled arms at **matched budget**.
3. Build the matched null by **rejection sampling on the realised** nuisance, not
   on its mean (G3) — accept a null run only when its realised diversity is
   within tolerance of the test arm's, and report the acceptance rate.
4. **Show the floor converged** (G4): keep drawing null runs until the running
   maximum stops rising. Report the growth factor. A floor from five runs is an
   order statistic, not a floor.
5. Decide on the **integer count first** (G6): fewer violating quadruples than
   the floor is below, **equal is UNRESOLVED**, more is above. Only then form a
   ratio.
6. Emit the certificate and recheck it with the kernel (§4).

## 4. The fitness ladder — decided from the top

| rung | obligation | checker |
| :-- | :-- | :-- |
| 0 | parses; passes ARGOS `CYBER-001..005`, `EPIST-006`, `HARD-007..010` | existing auditors |
| 1 | typechecks | compiler |
| 2 | **Lean spec discharged, axioms ⊆ {propext, Classical.choice, Quot.sound}, no `sorryAx`** | `anse/formal/lean_runner.py` |
| 3 | discharged without `Classical.choice` | `#print axioms` |
| 4 | latency, memory, energy, invariant error | existing NSGA-II vector |

```bash
.venv/bin/python -m anse.formal.lean_runner --formal-dir formal formal/ANSE/<Target>.lean
```

Rules for the ladder:

- **Lexicographic from the top.** A candidate that improves rung 4 while dropping
  a rung must lose. Verify this ordinality with a deliberately-constructed
  candidate before trusting any run (G1).
- Never report "verified" unqualified. Record *which* obligation was discharged;
  partial obligations (a loop invariant, a monotonicity lemma, refinement against
  a reference implementation) are legitimate and must be named as partial.
- `sorry` and a smuggled axiom both exit zero. The axiom read is the gate, never
  the exit code.

## 5. Adding an operator — the obligation

Candidate operators and their purpose are tabulated in the proposal (gene
duplication + divergence, gene conversion, horizontal transfer, transposition,
operon formation, synonymous rewriting, recombination hotspots). To add one:

1. State the computational job it is hired for. An operator without one is
   decoration.
2. Run the §3 diagnostic with the operator enabled and disabled at matched
   budget.
3. If the population does not measurably differ, **remove the operator**. Do not
   retain it because the biology is suggestive.
4. State the scaling axis (G9): how does the operator's cost or its criterion
   grow with program size and population size? Validate at the real size, not a
   convenient one.

Build order: Phase 0 the instrument, Phase 1 rung 2, Phase 2 gene duplication,
Phase 3 hotspots — and Phase 3 only if Phase 0 says recombination contributes.

## 6. Pre-flight checklist (all twelve guards)

Run before reporting anything.

```
G1  positive AND negative control on the fitness; broken candidate scores worse
G2  null reports its own spread; zero spread => BLOCKED, not a p-value
G3  null matched on REALISED nuisance; acceptance rate reported
G4  floor shown converged; growth factor reported
G5  no uncertainty estimator that can return identically zero
G6  integer comparison before ratios; equal => UNRESOLVED
G7  every reported number machine-traced to a stored artifact
G8  every check distinguishes the hypothesis from its nearest alternative
G9  scaling axis stated; validated at the real problem size; near-miss emitted
G10 edits asserted applied; runs gated on build; stale-artifact field asserted
G11 separate RNG streams for structure and noise
G12 for every refusing gate, which clause binds, and does it measure the data
    or the apparatus
```

## 7. Verification before calling work done

```bash
python antigravity_guard.py
python test_rigor_guard.py
.venv/bin/python -m pytest tests/ -q -p no:cacheprovider
```

Report the actual output. A grep that matches nothing looks exactly like success
(G10).
