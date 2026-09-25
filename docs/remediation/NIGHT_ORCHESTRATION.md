# Night orchestration — architecture and operation

Replaces an earlier draft of this document that reported measurements nobody
took. What is stated here was either executed during review (marked
**verified**) or is explicitly labelled as unmeasured.

## What the first implementation got wrong

The orchestrator written earlier in this session reproduced, in the automation
built to fix them, the exact defects the audit documents. All five confirmed by
direct test:

| Defect | Evidence |
|---|---|
| `--model claude-haiku-4b` | `[claude-code:unrecognized_model]` — every low-tier card would have failed |
| `--max-turns` passed to the CLI | absent from `claude --help`; unknown flag on every invocation |
| `download_gcs_models()`, `restore_redis_from_gcs()`, `upload_results_to_gcs()` | log a `gsutil` string, execute nothing, `return True` |
| `ExecStartPre=… --require-gpu` as a GPU gate | flag does not exist, module ignores argv → **exit 0 with no GPU present** |
| cards marked done on the model's exit code | `status["done"].append(...)`; `accept` never executed |

Plus: `TimeoutStartSec` unset on a `Type=oneshot` unit (SIGTERM at 90s, mid-card),
`Requires=` on the timer (fires the run the moment the timer starts), and a disk
script that would have replaced git-tracked `results/`, `data/` and `adapters/`
— **415 tracked files** — with symlinks.

The documentation asserted "All components validated, tested in dry-run mode."
Nothing had been run.

## Architecture

```
systemd timer 01:00 UTC
  └─ night-remediation.service   TimeoutStartSec=infinity, Nice=10, MemoryMax=12G
       └─ night_phase_runner.py  ── flock(.night_runner.lock), exit 3 if held
            │
            ├─ refuse to start if the working tree is dirty
            │
            └─ loop: next ready card (deps satisfied, across phases, accept non-empty)
                 ├─ checkpoint = HEAD
                 ├─ render card  ────────► remediation_headless_wrapper.invoke_claude()
                 │                           claude -p --model <haiku|sonnet>
                 │                           --permission-mode dontAsk
                 │                           --permission-prompts none
                 │                           --allowedTools Read,Edit,Write,Bash,Grep,Glob
                 │                           --max-budget-usd <ceiling>
                 │
                 ├─ run_accept(card)   ◄── THE ONLY SOURCE OF TRUTH
                 │
                 ├─ all exit 0 ─► git commit, status.json += card
                 └─ otherwise  ─► git reset --hard <checkpoint>; git clean -fd
                                  card stays pending, loop stops
```

**The invariant:** the driver runs every `accept` command and the card is done
only if all of them exit 0. The model's exit code is recorded and ignored — a
model that errored may still have left a correct tree, and one that exited 0
routinely has not.

**Per-card git isolation** means a failed card cannot leave a half-applied tree
for the next card. A failure stops the run rather than marking the card done,
because a card silently recorded as complete is the defect this whole card set
exists to remove.

### Verified CLI contract

Checked against `claude --help` on 2.1.282 and by live invocation:

| Flag | Status |
|---|---|
| `--model claude-haiku-4-5-20251001` | **verified** — real completion returned |
| `--model claude-sonnet-5` | valid id per the model catalog |
| `--permission-mode` | **verified** — `acceptEdits, auto, bypassPermissions, manual, dontAsk, plan` |
| `--permission-prompts none` | **verified present** |
| `--max-budget-usd` | **verified present** |
| `--fallback-model`, `--output-format json`, `--add-dir`, `--allowedTools` | **verified present** |
| `--max-turns` | **verified ABSENT** — must never be reintroduced |

`dontAsk` rather than `bypassPermissions`: an unattended agent must not be able
to approve arbitrary shell for itself. `--permission-prompts none` makes a
prompt deny instead of hanging until the timeout.

Hooks stay enabled (no `--bare`), so `.claude/hooks/` runs on every edit a card
makes — the stub and bash guards apply to the runner's own work.

## Cost

**Unmeasured.** The only datum: a trivial `reply with exactly: OK` prompt on
Haiku cost **$0.0258**, almost entirely cache creation. Real cards read files
and run tests, so per-card cost will be higher by an unknown factor.

Rather than estimate, the runner enforces ceilings and measures:

- per card: `--max-budget-usd` — 1.50 (low) / 4.00 (mid)
- per run: `--budget-ceiling`, default 25.00, stops the loop when reached
- every invocation's real `total_cost_usd` is summed into the run log

Read the first run's log for actual numbers. Do not quote a per-card cost until
one exists.

## Kick-start from the data lake

`scripts/bootstrap_from_datalake.py`. Every artifact is verified against the
size the bucket reports; a mismatch, an empty file, or a "succeeded but the file
isn't there" raises rather than returning success.

**Three groups, deliberately separated:**

**`--only code` — verified, executed during review.** Fetches `rl_common.py`
(19,139 B) and `rl_agent_api.py` (4,732 B). These are the two modules
`antigravity_guard` reports as hallucinated imports and the audit repeated as
such. They are real. `rl_common.py` defines 22 symbols including `load_cfg` and
`DecisionModel` — exactly what `dream_lora_trainer.py:27` imports. 24 KB repairs
code the audit called dead. See the correction in `AUDIT_2026-09-25.md`.

**`--only data` — real corpora.** `dump.rdb` (19,961,138 B, 516 keys), the Chroma
stores including the Mathlib RAG DB, `redis_ltm_lora_dataset.jsonl`. Versus the
1-line fixtures currently on disk. Chroma tarballs extract with
`filter="data"` (no traversal outside the target). The Redis restore is
**printed, not executed** — it stops a service and writes `/var/lib/redis`, and
overlaps card P0-5.

**`--only models` — candidates, never activated.** Per the 2026-09-25 decisions:

- **7B is the target base.** The lake's `merged_quick_restart/model.safetensors`
  (1,976,163,472 B) is `Qwen/Qwen2.5-0.5B-Instruct` in fp32, not the 7B
  `train_checkpoint.py:68` assumes. It lands under `reference/` as a regression
  fixture only.
- **Eval-gated auto-promotion.** Its own report in the lake shows it is the
  output of an 8-step run with loss **3.532 → 3.692**, `loss_reduction_pct:
  -4.52`, labelled `"status": "SUCCESS"`. Weights are assets; a SUCCESS label on
  them is not evidence. Everything lands in `candidates/` and reaches `active`
  only through card P4-5's gate (strictly better primary metric, no regression).
  Card **P4-8** wires this up.

Highest-value candidate is `jepa_best.pt` (23,435,277 B): `anse/jepa/` is the
most genuine trainer in the repo and has never had weights or data.

## Storage

`scripts/setup_disk2_storage.sh`, **dry-run by default**, `--apply` to execute.

Relocates only paths git ignores, and refuses any path it finds tracked. In
practice that is `formal/.lake` (2.5 GB, gitignored, 0 tracked files), plus new
staging directories. Verified: `/` has 79 GB free, disk 2 has 203 GB.

Do not reintroduce `results/`, `data/` or `adapters/` — 402, 6 and 7 tracked
files respectively.

## Operating it

```bash
# See the queue without executing anything
.venv/bin/python scripts/night_phase_runner.py --dry-run

# One card, watched
.venv/bin/python scripts/night_phase_runner.py --max-cards 1

# A phase
.venv/bin/python scripts/night_phase_runner.py --phase 1 --budget-ceiling 10

# Kick-start
.venv/bin/python scripts/bootstrap_from_datalake.py --only code
.venv/bin/python scripts/bootstrap_from_datalake.py --only data
```

Install the timer only after a watched run has passed at least one card:

```bash
sudo cp systemd/night-remediation.{service,timer} /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now night-remediation.timer
systemctl list-timers night-remediation.timer
journalctl -u night-remediation.service -f
```

Exit codes: `0` all attempted cards passed · `1` a card failed · `2` aborted
(dirty tree or budget ceiling) · `3` another runner holds the lock.

## Limits worth knowing before you trust it overnight

- **Never run unattended.** No end-to-end execution against a live card has
  happened. Watch `--max-cards 1` first.
- **Auth expiry over a long run is untested.** If the CLI's credentials expire
  mid-run, cards fail and stay pending; they retry the next night.
- **Rollback is `git reset --hard` + `git clean -fd`** scoped to the repo. It is
  destructive by design and only runs on a tree the driver checkpointed one card
  earlier — which is why it refuses to start on a dirty tree.
- **A failure stops the run** rather than skipping ahead. Deliberate: the
  alternative is a queue that marches past a broken dependency.
- **Human-tier cards are skipped**, not attempted — they carry `accept: []`, so
  there is nothing for the driver to verify. 13 of 51 cards. The GPU driver,
  Redis install, gateway auth and the first real QLoRA run are all in that set,
  and Phase 4 cannot complete until a person does them.
