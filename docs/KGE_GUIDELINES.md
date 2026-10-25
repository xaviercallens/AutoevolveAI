# Kernel-Gated Evolution (KGE) — where and how to use it

Foundation paper: Paper J, concept DOI [10.5281/zenodo.23635678](https://doi.org/10.5281/zenodo.23635678)
(resolves to the latest edition). Reference implementation:
`crates/kernel_gated_evolution` (`kge ladder`, `kge hillclimb`, `kge solve`).
Formal identities: `formal/ANSE/AlixKalSpec.lean`. The gate: `anse/formal/lean_runner.py`.

KGE is a biomimetic search whose **acceptance is decided by a proof kernel, not by
the search**. Three mechanisms, each kept because measurement supported it:

| mechanism | life analogue | what it does here | status |
|---|---|---|---|
| mutation + tournament selection, steady state | Darwinian variation and selection | the operator that solves targets | load-bearing |
| one-sided exact checkpoint | apoptosis / developmental checkpoint | refutes a candidate that disagrees with the spec at any sample point; agreement grants nothing; zero kernel cost | load-bearing, proved one-sided (`alix_checkpoint_refutes`) |
| exact dosage `out = A + B·v` per locus | gene dosage / expression level | tells you exactly how much each locus reaches the phenotype; `B = 0` everywhere = dead code | instrumentation (did not improve search as an operator guide) |
| Lean 4 kernel, `#print axioms`, no `sorryAx` | the environment's final judgement | decides acceptance; one invocation per batch at any failure rate | the arbiter |

**Fitness guides; the kernel decides.** A wrong fitness can waste search effort but
cannot manufacture an acceptance.

---

## 1. When to use it

Use KGE when **all three** hold:

1. A candidate's acceptance must be **formal** (equality to a specification), not
   empirical (tests pass).
2. An **exact evaluator** exists for the candidate representation (here: exact
   rationals over an expression grammar).
3. The specification can be **rendered as a Lean definition** the kernel can
   compare against (`ring` closes polynomial identities over `Rat`).

If one is missing, keep the kernel gate and swap the search layer. The gate is the
part with the guarantee; the search is the part that is allowed to be creative.

**Choose the search layer by target size.** Measured on the ladder and on five
SRSD-Feynman laws: for targets of about four leaves or fewer, random search over
small trees and a restart hill-climber match or beat the population (on three of
the five Hub laws the population lost to both); the population earns its place
from about nine nodes (L3: 49 vs 9 discordant pairs, p = 9e‑8). The checkpoint,
the dosage analysis and the kernel gate are indifferent to which layer produced
the candidate — swap the layer, keep the gate.

### Where it applies today (the reference grammar `{+,−,*}`, dyadic constants, ≤4 variables)

- **Lean-gated numerical kernels**: integrator steps, stencils, update rules,
  finite-difference coefficient sets that must be *proved* equal to a spec before
  entering a simulation. Worked example: the Verlet position update.
- **Any synthesis with a formal acceptance criterion**: compiler rewrite rules,
  computer-algebra simplifications, conjectured closed forms.
- **Inert-locus (dead-code) analysis** of evolved programs — exact, from dosage.
- **Batching expensive verification**: any Lean-verifying pipeline (LLM prover
  loops, conjecture miners) can read the per-declaration report and verify a batch
  at the price of one invocation.
- **Rediscovery of polynomial laws from exact data**: on SRSD-Feynman, 8 of 120
  laws lie inside the grammar; KGE recovers them from 12 exact samples where dense
  regression is underdetermined, and *proves* the recovered form.

### Where it does not apply yet (the grammar's roadmap, with counts from SRSD-Feynman)

| refusal | laws | what would be needed |
|---|---|---|
| functions / constants outside `{+,−,*}` (sqrt, exp, trig, π) | 79 | new operators **with their dosage rule proved** |
| division by a variable | 10 | rational-function dosage (not affine); checkpoint unchanged |
| more than 4 variables | 6 | runtime variable arity (mechanical) |
| physical constants given as floats | ~15 | exact constants as symbols, or interval arithmetic with a different soundness story |

---

### Turn on lifetime learning for mid-sized targets

`--tuning baldwin` solves each constant locus exactly when its required value
`v* = v + (want − out)/B` agrees at every sample point (proved:
`xav_required_value`). Measured over 1,200 paired seeds it never lost a solve the
plain population found, and at **matched total work** it stays ahead on L3
(0.450 vs 0.395) and L5 (0.060 vs 0.040) and is level on L4. `--tuning lamarck`
gives identical results — exact tuning is all-or-nothing. It costs 2.3–2.8× the
tree-point work per run from L3 up, so compare at matched work, as above.

### Keep fitness variance alive

Proved (H12, `AlixPopulationGenetics.lean`): in the one-locus haploid model a round of selection raises mean
fitness by exactly `Var(w)/w̄`, so selection stalls when the population's fitness variance is gone; and (H11)
neutral drift moves a lineage to fixation only with probability `1/N`. Registered, not yet tested: stalled KGE
runs should be those whose fitness variance has collapsed. Fresh random immigrants or redrawn sample points are
the levers to try.

## 2. How to use it — the discipline

Each rule below is there because skipping it produced a wrong conclusion in this
programme at least once (see `LL.md` §29).

1. **eXact first.** Keep everything the search sees exact. The checkpoint's
   soundness and the dosage identities rest on it; a float fitness turns refutations
   into guesses.
2. **Arbiter before operator.** Build and test the kernel gate with a **planted wrong
   candidate in every batch** before tuning any operator. Nothing an operator does
   means anything until the gate is shown to refuse. (`scripts/kge_gate_rust_solutions.py`
   plants `spec + 1` in every batch.)
3. **The simplest control first.** Run a single-individual restart hill-climber on
   the same seeds, points and budget (restarts paid from the budget) and report
   McNemar on the discordant pairs. On easy targets it *beats* the population
   (L1: 66 vs 31, p = 4.9e‑4); the population earns its place from L3 (49 vs 9,
   p = 9e‑8). Design the population in because the hard rungs need it, not because
   the method is called genetic.
4. **Calibrate difficulty on a pooled band fixed in advance** — never on the rung
   that flatters a method.
5. **Report both costs**: fitness evaluations *and* total tree-point evaluations.
   An operator that probes the genome spends compute the budget does not see.
6. **Replay, don't inspect.** When two implementations disagree, replay one on the
   other's exact sample points (`kge … --points-file`). A solve rate that moves with
   the points is a property of the landscape instance, not a bug.
7. **Grow the grammar deliberately.** Each new operator ships with its dosage rule
   proved in `AlixKalSpec.lean`, as `+`, `−`, `*` are, or not at all.
8. **Never let the generator grade itself.** The search is heuristic and may be
   wrong; acceptance is the kernel's. This is the whole design, and it applies to the
   people running it as much as to the machine.

### Minimal recipe

```bash
# build
cd crates/kernel_gated_evolution && cargo build --offline --release && cargo test --offline --release

# one target, prefix notation over h w q p, vs baselines, Lean candidates out
./target/release/kge solve --name my_law --target '(* (* 1/2 h) (* w w))' \
  --seeds 100 --budget 4000 --points-file ../../results/python_sample_points.json \
  --lean-out ../../results/my_candidates --out ../../results/my_law.json

# the arbiter (Lean verification goes through lean_runner.py only)
cd ../.. && .venv/bin/python scripts/kge_gate_rust_solutions.py \
  --candidates results/my_candidates --names my_law --per-rung 8 --out results/my_law_gate.json
```

---

## 3. What it brings, and to whom

- **Science**: a mechanical bridge from a candidate formula to a *certified* one.
  What comes out of the search is not a formula that fits but a formula with a
  kernel-checked proof that it equals the specification everywhere. For laws inside
  the grammar: rediscovery with a proof attached, from a dozen exact samples.
- **Verified software**: numerical kernels are routinely hand-derived and
  empirically tested; a pipeline that evolves them and refuses to accept without a
  proof moves the guarantee from the test suite to the kernel — at one invocation
  per batch.
- **Human–AI collaboration**: let the generator be creative and the arbiter be
  formal, and never let the generator grade itself. Every control in this programme
  exists because that principle was applied to our own work as well as to the
  machine's.

## 4. Limits, plainly

- Reference grammar only; measurements are not general.
- Solve rates fall steeply above ~9-node targets; the Verlet target (17 nodes) is
  unsolved at 4,000 evaluations. The cliff is not explained by basin geometry
  (measured) and not relieved by recombination (eight operators, pre-registered
  bars; Paper I). The bottleneck is finding the basin in a growing space.
- The checkpoint is one-sided by design: an evader that agrees on all sample
  points survives it and costs one kernel invocation before rejection.
- ~97% of a Lean invocation is fixed overhead; batching amortises it, a persistent
  kernel would remove it (not built).

## Codename

The engine's codename is **ALIX** — Apoptotic checkpoint, Lean-gated, Inheritance by
mutation, eXact. The theorem names in `AlixKalSpec.lean` are a tribute to the people
whose support carried this long effort. No real names appear anywhere in the code
or the papers.
