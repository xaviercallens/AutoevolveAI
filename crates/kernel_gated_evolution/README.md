# kernel_gated_evolution — Kernel-Gated Evolution (KGE), codename ALIX

A biomimetic search over exact-rational expression genomes whose **acceptance is
decided by a Lean 4 proof kernel, not by the search**. Fitness guides; the kernel
decides. A wrong fitness can waste search effort but cannot manufacture an
acceptance.

Paper (concept DOI, resolves to the latest edition): https://doi.org/10.5281/zenodo.23635678
Guidelines for end users: [`docs/KGE_GUIDELINES.md`](../../docs/KGE_GUIDELINES.md)
Formal identities: [`formal/ANSE/AlixKalSpec.lean`](../../formal/ANSE/AlixKalSpec.lean)

## What is in the crate

| mechanism | analogue | role |
|---|---|---|
| mutation + tournament + steady state | Darwinian variation and selection | the search operator |
| one-sided exact checkpoint | apoptosis | refutes a candidate that disagrees with the spec at any sample point; agreement grants nothing; zero kernel cost |
| exact dosage `out = A + B·v` per locus | gene dosage | how much each locus reaches the phenotype; `B = 0` everywhere = dead code |
| Lean rendering | — | survivors become Lean definitions + an equality theorem for the gate |

The gate itself lives in `anse/formal/lean_runner.py` (Lean verification in this
project goes through it only); this crate renders candidates and leaves acceptance
to it.

## Build and test (offline)

```bash
cargo build --offline --release
cargo test  --offline --release        # 8 tests, exact arithmetic on random genomes
```

## Use

```bash
# Calibration ladder (L1..L6, L6 = Verlet position update), Lean candidates out
./target/release/kge ladder --seeds 200 --budget 4000 --lean-out ../../results/kge_lean_candidates \
    --out ../../results/kge_rust_ladder.json

# Population vs the simplest control, paired on seeds/points/budget
./target/release/kge hillclimb --seeds 200 --budget 4000 --out ../../results/kge_rust_hillclimb.json

# Any target in prefix notation over h w q p (outside {+,-,*} is refused, not approximated)
./target/release/kge solve --name my_law --target '(* (* 1/2 h) (* w w))' \
    --seeds 100 --budget 4000 --points-file ../../results/python_sample_points.json \
    --lean-out ../../results/my_candidates --out ../../results/my_law.json

# The arbiter
cd ../.. && .venv/bin/python scripts/kge_gate_rust_solutions.py \
    --candidates results/my_candidates --names my_law --per-rung 8 --out results/my_law_gate.json
```

`--points-file` replays a run on exactly another implementation's sample points
(a JSON array of `["n/d","n/d","n/d","n/d"]` rows). Seeds are replayable (`rand_pcg`).

## Choose the search layer by target size

Measured: for targets of about four leaves or fewer, random search over small trees
and a restart hill-climber match or beat the population; the population earns its
place from about nine nodes. The checkpoint, dosage and gate are indifferent to
which layer found the candidate.

## Limits

One grammar `{+,-,*}`, four variables, dyadic constants. Solve rates fall steeply
above ~9-node targets; the Verlet target (17 nodes) is unsolved at 4,000
evaluations. The checkpoint is one-sided by design. See the paper's Limitations.

## Codename

ALIX: Apoptotic checkpoint, Lean-gated, Inheritance by mutation, eXact. The theorem
names in `AlixKalSpec.lean` are a tribute. No real names appear.

License: BSD-3-Clause.
