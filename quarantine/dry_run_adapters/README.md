# Quarantined DRY_RUN adapter receipts

These 9 `checkpoint_v*/final_adapter/adapter_config.json` directories (the
audit at `docs/remediation/AUDIT_2026-09-25.md` counted 7; a full scan on
2026-09-26 found 2 more, untracked because `.gitignore` covers `adapters/`)
were produced by `daily_trainer_daemon.py` accepting `train_checkpoint.py`'s
config-only DRY_RUN path and recording it as a deployed checkpoint. Card
**P1-5** closes that defect going forward; this card only quarantines the
receipts DRY_RUN already produced.

**What these are not:** trained models. Every `adapter_config.json` here has
`"mode": "DRY_RUN"`, no directory contains an `adapter_model.safetensors`, and
each references a `dataset` under `training_runs\datasets\delta_...` (Windows
separators) whose corresponding delta file is a 1-line fixture — the daemon's
own default `min_samples=50` cannot have produced a real run from it.

**Redis may still name one of these.** `antigravity:active_lora_version` could
point at a quarantined checkpoint from before P1-5 landed. This card does not
rewrite that history; it only stops new DRY_RUN receipts from being recorded
as deployments and moves the pre-existing ones out of the active `adapters/`
tree. If a serving path reads `active_lora_version` and expects the checkpoint
to be at its old location, that read will now fail loudly instead of silently
serving an untrained model — which is the correct failure mode.

## Code that still expects `adapters/checkpoint_v*`

Found by `grep -rln "adapters/checkpoint_v"`:

- `daily_trainer_daemon.py` — the producer. Unaffected by this move; it writes
  new checkpoints under `adapters/`, and P1-5 is what stops a DRY_RUN one from
  being recorded as active.
- `tests/remediation/test_no_dry_run_deployment.py` — P1-5's own test. It
  builds its fixtures in a temp directory and does not read these quarantined
  ones, so the move does not affect it.

Not fixed here, per the card's scope — quarantine only.
