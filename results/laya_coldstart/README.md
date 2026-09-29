# Laya cold-start fine-tune validation (TODO 24)

Answers one question: can Laya's decision head be fine-tuned, from the real pretrained
checkpoint, on this project's own verifier-labeled results — and does it actually learn
something, or does it just memorize? Not a production training run; a bounded, CPU-only
validation of the mechanism.

## Data — real verifier labels only, never a model's own opinion

| source | rows | pass | fail | task groups |
|---|---|---|---|---|
| `cosmo3` episodes (JEPA pipeline steps, real verifier verdicts) | 206 | 173 | 33 | 68 |
| Lean hardness ladder (`results/hardness/baseline.json`, kernel-checked) | 92 | 14 | 78 | 28 |
| Lean hardness retrieval A/B (`results/hardness/retrieval_ab.json`, partial at run time) | 143 | 26 | 117 | 28 |

Each row becomes one `noul` question ("did this pass its verifier?"), state = the real
input/command, label = the real pass/fail verdict. Split 330 train / 111 held-out, **by task
group** (a proof and its negative-control sibling, or a pipeline's own retries, never split
across train/held-out).

## Method

Load the real Convai `checkpoints/laya/model.safetensors` (a genuine, published Apache-2.0
checkpoint — not random init: this is the "cold start"). Freeze the ModernBERT encoder;
train only the decision head + type embedding + scorer (26.2M of 421.3M parameters) with
AdamW, using the model family's own strictly-proper scoring-rule loss (`rl_common.
proper_reward`), 2 epochs, CPU only. Two independent seeds. A shuffled-label control repeats
the identical procedure with training labels permuted across rows.

## Result — held out, never seen in training, 111 rows

| | AUROC | Accuracy | ECE | held-out loss |
|---|---|---|---|---|
| **Base checkpoint (no fine-tuning)** | 0.322 | 0.297 | 0.525 | 1.138 |
| **Fine-tuned, seed 0** | 0.758 | 0.712 | 0.166 | 0.275 |
| **Fine-tuned, seed 1** | 0.760 | 0.703 | 0.175 | 0.284 |
| Shuffled-label control, seed 0 | 0.383 | 0.360 | 0.152 | 0.353 |
| Shuffled-label control, seed 1 | 0.359 | 0.324 | 0.198 | 0.367 |

**Verdict: YES, real signal.** The fine-tuned run's *worst* seed (0.758 AUROC / 0.703
accuracy) clears both the untrained base (0.322 / 0.297) and the shuffled control's *best*
seed (0.383 / 0.360) by a wide margin — far larger than the 0.024 seed-to-seed spread. The
untrained base actually scores *below chance* (AUROC < 0.5) on this task framing, which is
expected: it was never trained to answer "did this pass?" in this shape. The shuffled
control correctly shows no learning, confirming the gain is not an artifact of the training
loop itself. Calibration (ECE) also improves sharply, 0.525 → ~0.17.

## Honest limitations

- **Per-source breakdown is uneven.** The aggregate result is driven mostly by the
  cosmo3 slice (53 held-out rows, the largest and best-balanced). The hardness-baseline
  slice has **zero positive examples in its held-out split** (T1–T3 pass at 0%, as
  established elsewhere in this project), so AUROC is undefined there — only accuracy
  applies, and it is not very informative on an all-negative slice. The retrieval-ab slice
  has only 2 held-out positives — any AUROC computed on it is high-variance and should not
  be read on its own.
- **Head-only, 2 epochs, CPU.** This deliberately does not fine-tune the encoder or run
  long enough to be a production candidate — it is a cold-start smoke test of the
  mechanism, not a promotion.
- **Only 2 seeds.** The spread between them is small (0.024), but 2 is not a large sample.
- **The `retrieval_ab` slice was partial** when this ran (the premise-retrieval A/B
  experiment was still in progress); re-running with the finished file would change those
  counts slightly.

## Artifacts

- `dataset.jsonl` — all 449 labeled records built from the three sources.
- `split.json` — the exact group-held-out split (seed 0, 20%).
- `report.json` — full per-source metrics, training loss curves, timings, verdict.
- `checkpoints/laya_coldstart_v1/` (gitignored, not committed) — the real_s0 fine-tune,
  self-contained and loadable exactly like `checkpoints/laya/`. **This is a validation
  artifact, not a promoted checkpoint** — nothing in this project's serving path points at
  it, and it must not replace `checkpoints/laya/model.safetensors`.

## Next step, if this is worth continuing

Retrain on the finished `retrieval_ab.json`, grow the dataset (more sources: the
`capability_matrix.json` router decisions, `heldout_baseline.json` promote/reject
outcomes), and only then consider fine-tuning the encoder itself or running longer — each
change gets the same base-vs-fine-tuned-vs-shuffled-control comparison before any claim of
improvement.
