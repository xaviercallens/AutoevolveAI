# Remediation workflow — how to run it

Three documents:

| File | What it is |
|---|---|
| `AUDIT_2026-09-25.md` | What six parallel audits found, with `file:line` evidence |
| `tasks.yaml` | 49 cards, tiered for model execution |
| `README.md` | This file: sequencing, tiering rationale, and the driver contract |

**Nothing here has been implemented.** These three documents are the only files written. No source file, config, or service was modified.

---

## The one thing to read first

The request was to deploy: models on the T4, night dream training, Redis with GCS backup, the DeepSeek Lean solver. The audit found that the platform underneath is not running (no GPU driver, no Redis, no GCS code) and — the reason this is a remediation plan rather than a deployment plan — **several components report success without doing the work.**

The sharpest example: `daily_trainer_daemon` records a LoRA checkpoint as *deployed* after a DRY_RUN that trained nothing. Seven such receipts are on disk. Add a nightly timer to that and you get a system that produces a deployment record every morning, forever, having learned nothing.

So Phase 1 (stop the fabrication) blocks Phase 4 (night training). That ordering is the plan's main claim.

---

## Running a card

After `P0-1` and `P0-2` land:

```bash
.venv/bin/python tools/v2_tasks.py --file docs/remediation/tasks.yaml check       # validate the graph
.venv/bin/python tools/v2_tasks.py --file docs/remediation/tasks.yaml next --tier low
.venv/bin/python tools/v2_tasks.py --file docs/remediation/tasks.yaml card P1-2   # print one card
.venv/bin/python tools/v2_tasks.py --file docs/remediation/tasks.yaml done P1-2   # after accept passes
```

`next` prints the rules block plus the card. That rendered text is the entire prompt — a card is written so a low-tier model needs nothing else.

**The driver runs `accept`, never the model.** That is the whole integrity model of this workflow, and it is also the defect `P5-7` fixes in the driver itself: today `done` records a card without running anything.

## Tiering

49 cards across 7 phases (8 / 10 / 6 / 5 / 7 / 7 / 6), verified acyclic with no unknown dependencies.

| Tier | Count | Rule |
|---|---|---|
| `low` | 18 | A Haiku-class model finishes it from the card alone. Deterministic accept command. |
| `mid` | 18 | Sonnet-class: cross-file reasoning, or a judgement the card cannot pre-decide. |
| `human` | 13 | sudo, reboot, money, credentials, published claims, or GPU-hours. `accept: []`. |

36 of 49 are model-executable. The human share is higher than a typical feature plan because this one is dominated by system state (driver, service, IAM) and by decisions about published claims — neither of which a model should make unattended.

Two deliberate choices:

- **Passwordless sudo works on this host, which is why the driver install is `human`.** Capability is not authorisation. Kernel modules, service restarts and IAM grants stay with a person.
- **Human cards are paired with low cards that verify them.** `P0-3` (a person installs the driver) is followed by `P0-4` (a model writes a deterministic readiness probe). The person does the risky thing; the machine checks it, repeatably.

## Critical path

```
P0-1 ─ P0-2 ─────────────────────────────────────────► driver usable
P0-3 ─ P0-4 ──────────► GPU real ──► P2-1 ─ P2-2 ─ P2-3 ──► residency
P0-5 ─────────────────► Redis up ──┐
P0-6 ─────────────────► auth ──────┤
                                   ├─► P3-1 ─ P3-2 ─ P3-3 ► memory + backup
P1-1 ─► P1-2..P1-10 ──► no fabrication ──┐
                                          ├─► P4-1 ─ P4-2 ─ P4-3 ─ P4-4 ─ P4-5 ─ P4-6 ► night training
P4-7 (provenance decision) ───────────────┘
```

Four gates that genuinely block:

1. **`P0-3` blocks everything GPU.** The T4 is attached (`lspci` confirms a TU104GL) but no kernel module is loaded after the `6.8.0-1067-gcp` upgrade. Until it is fixed, Ollama serves on CPU and every trainer takes its dry-run branch.
2. **`P0-6` (gateway auth) before `P3-x` (Redis holds real data).** The gateway currently invokes arbitrary MCP tools unauthenticated on a box that is about to hold conversation data and cloud credentials.
3. **Phase 1 before `P4-6` (the timer).** Stated above.
4. **`P4-4` (one real run) before `P6-1` (figures).** The figure pipeline is being rebuilt to read real artifacts only, so a real artifact has to exist.

## What the plan deliberately does not do

- **It does not deploy all models to the T4 simultaneously** — ~27 GB of weights against 15,360 MiB of VRAM. `P2-2` produces a residency policy instead. This is arithmetic, not a preference.
- **It does not schedule the existing dream path.** `dream_lora_trainer.py` trains on `torch.randint` tensors behind a dead import; `latent_dreamer` returns `catastrophic_forgetting_prevented: True` as a literal. `P4-3` rebuilds on `train_checkpoint.py`, which already contains real QLoRA.
- **It does not reinvent Night School.** `docs/ROADMAP_V1_V2_COMPANION.md` §4 already specifies capture → scrub → verify → QLoRA+DPO → promote-on-no-regression → rollback-by-symlink. Phase 4 implements that design.
- **It does not run the 42 ported v2 cards.** They target the GCP branch and a 100% coverage gate `main` lacks; their accept commands would fail immediately. `P0-1` ports them for the driver and for reference only.
- **It does not fix the Lean stack broadly.** Only the actively false gate (`P1-9`, `mcts_lean_solver` scores stdout while Lean writes to stderr) and the prover wiring (`P2-5`). The Mathlib build is `P6-4` and is human-tier because a standing preference says not to spend that compute.

## Sequencing advice

Phase 0 and Phase 1 are independent — `P1-1` through `P1-10` need no GPU, no Redis and no network, so they can run while the driver install is scheduled. That is the cheapest parallelism available: all ten Phase 1 cards are `low` or `mid` (5 each), pure code-and-tests work, and 16 cards across the whole set have no dependencies at all and can start immediately.

`P4-7` (training-data provenance) has no dependencies and gates nothing technically, but it gates Phase 4 *legally*. Settle it early; it is a conversation, not a task.

## If a card's premise is false

Say so and stop. Every card cites `file:line` evidence from a specific commit (`e48f37f`, 2026-09-25). If the code has moved, the card is stale — report the discrepancy rather than adapting the card until it passes. A card that was made to pass against different code has verified nothing, which is the failure mode this entire workflow exists to eliminate.
