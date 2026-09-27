# ANSE v2 implementation workflow (for low-tier models)

Strategy and evidence live in [`../ROADMAP_V1_V2_COMPANION.md`](../ROADMAP_V1_V2_COMPANION.md).
This directory turns that plan into **42 small cards** that a Haiku-class model can execute
one at a time, with a machine check after each. Model choice for the T4 is in
[`MODEL_SELECTION_T4.md`](MODEL_SELECTION_T4.md).

## Why cards, and why this shape

A small model fails on vague or wide tasks, and it fails silently: it says "done" when it is
not. Every card therefore has (a) exact file paths, (b) exact function signatures and
edge-case rules, (c) named tests, and (d) `accept` commands that a **driver runs**. The
model's own claim of success is never the evidence.

| Tier | Who | Cards |
|---|---|---|
| `low` | Haiku-class, card alone is enough | 19 |
| `mid` | Sonnet-class: reads unfamiliar code or designs fakes | 16 |
| `human` | A person: GPU gate runs, decisions, installing hooks | 7 |

Run `python tools/v2_tasks.py list` for the live table.

## The loop (one card = one session = one commit)

```
python tools/v2_tasks.py next --tier low   >  card.txt     # rules + the next ready card
<give card.txt to the model, in a fresh session, in the repo>
<model edits files, runs the accept commands, commits "v2(<id>): <title>">
<driver re-runs the accept commands itself>                # do not trust the transcript
python tools/v2_tasks.py done <id>                         # only if they exit 0
```

`next` only offers cards whose dependencies are done, so order is enforced. Status is kept in
`docs/v2/status.json`; `tasks.yaml` is a read-only spec. `python tools/v2_tasks.py check`
validates the graph (unknown dependencies, cycles, non-human cards without an accept command).

Setup once: `tools/setup_v2_env.sh` (Python 3.11 venv in `.venv-v2`; the system Python is 3.10).

## Ground rules baked into every card

1. **Hermetic logic, thin glue.** Logic lives in `anse/v2/` with I/O, GPU, network, clock and
   randomness injected, so tests need no GPU, no Ollama, no network. Code that must touch
   those goes in `v2_runners/` as glue under ~80 lines. `anse/` is under the repo's 100 %
   line+branch gate; `v2_runners/` is not.
2. **The judge is not editable.** Sandbox, evaluator, parser, attestation, metrics, the
   promotion gate and the writable-set guard are off limits unless a card names them.
   (`anse/v2/writable_set.py`, card F-1, later enforces this for the model itself.)
3. **Tests must bite.** A card's tests have to fail if the feature is removed. Never skip,
   xfail, delete or weaken a test; never lower `fail_under`.
4. **Three strikes.** After 3 honest failed attempts a model writes `BLOCKED:` with the exact
   error and stops. It does not widen scope. Escalate that card one tier up.
5. **Transcript-derived data is not training data** until a human writes `gates/N8.md`
   (card N-8). The curator enforces this in code (`Policy.no_train_origins`).

## Phase map and gates

```
Phase 0  evaluation integrity    V0-1..V0-7, T-1        (no gate: everything later is measured with it)
Phase A  own the weights         A-1 A-2 A-3  -> GA     HF backend within 3 pts of Ollama on Phase 1
Phase B  verified-data flywheel  B-1 B-2 B-3  -> GB     5k episodes, 1k preference pairs, 200+ tasks
Phase C  nightly consolidation   C-1..C-6     -> GC     +5 pts pass@1 on the never-touched test split, 2 of 3 seeds
Phase D  honest surrogate        D-1 D-2      -> GD     AUROC >= 0.80 (CI lower bound > 0.70) on unseen tasks, else shadow-only
Phase E  validated adversary     E-1 E-2 E-3  -> GE     >= 30 % of seeded-bug tasks get a valid failing input
Phase F  gated autopoiesis       F-1 F-2      -> GF     one accepted + one correctly rejected self-patch, attested
Night School (capture, verify, recall, serve)  N-1..N-8
```

**GC decides whether the v2 thesis holds.** If the nightly loop cannot buy +5 points on
unseen tasks, stop before D to F and rethink data volume, learning rate and replay rather
than building more machinery on top.

Suggested order for the first two weeks: Phase 0 (all `low`/`mid`, parallelisable except
V0-7 after V0-6), then A, B in parallel with C-1 to C-4, N-5a/N-5b/N-6 at any time (no
dependencies). Human gates go in the gaps.

## What a gate result looks like

Each `human` card ends by writing `docs/v2/gates/<ID>.md` with: the exact command, model and
adapter versions, seeds, the numbers, and a one-line verdict. A gate that fails is a result,
not an error: record it and follow the card's fallback.
