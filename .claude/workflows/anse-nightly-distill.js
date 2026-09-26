export const meta = {
  name: 'anse-nightly-distill',
  description: 'Night QLoRA consolidation on the T4 over verified episodes, with an eval that can actually reject the new adapter',
  whenToUse: 'Nightly, after a cascade day has harvested verified episodes. Requires a frozen EVAL set.',
  phases: [
    { title: 'Gate', detail: 'refuse to train unless data, VRAM and the frozen split are all real' },
    { title: 'Train', detail: 'QLoRA on the T4 at the largest base that fits, fp16 (not bf16 on sm_75)' },
    { title: 'Evaluate', detail: 'held-out frozen set, trend test — not first-vs-last point' },
    { title: 'Promote', detail: 'promote only on improvement with no regression; else keep yesterday and say why' },
  ],
}

// WHY THE EVAL STAGE IS THE POINT OF THIS WORKFLOW
// The only genuine training run this project has ever done is a 12-step QLoRA smoke
// test (training_runs/smoke/qwen_lora/, real adapter_model.safetensors, 2,175,168 B).
// Its own EVAL step reported "loss fell 15.41%, improved: true" by comparing ONLY
// step 1 to step 12 on a noisy 12-point series. Recomputed properly:
//
//   mean(steps 1-6) 2.7148 -> mean(steps 7-12) 3.0242   = +11.40%  WORSE
//   OLS slope                                            = +0.0085/step  RISING
//   stdev 0.4936 vs claimed signal 0.565                 = noise >= effect
//
// The -15.41% was an artifact of step 1 happening to be the series maximum. That EVAL
// ran in 3.2e-05 s: it performs no forward pass and uses no held-out data — it just
// subtracts two numbers FIT reported. The identical defect produced the data lake's
// flagship artifact, an 8-step run whose loss rose 3.532 -> 3.692 while labelled SUCCESS.
//
// So: a trend test on held-out data, or no promotion.

const GATE_SCHEMA = {
  type: 'object',
  properties: {
    episodes_available: { type: 'integer' },
    episodes_consumable: { type: 'integer', description: 'rows that survive the JEPA/QLoRA reader, not just rows on disk' },
    distinct_tasks: { type: 'integer' },
    eval_set_frozen: { type: 'boolean' },
    eval_train_overlap: { type: 'integer' },
    vram_free_mib: { type: 'integer' },
    gpu_exclusive: { type: 'boolean', description: 'inference models unloaded so training has the card' },
    largest_base_that_fits: { type: 'string' },
    dtype: { type: 'string' },
    proceed: { type: 'boolean' },
    refusal_reason: { type: 'string' },
  },
  required: ['episodes_available', 'episodes_consumable', 'distinct_tasks', 'eval_set_frozen', 'eval_train_overlap', 'vram_free_mib', 'proceed'],
}

const TRAIN_SCHEMA = {
  type: 'object',
  properties: {
    base_model: { type: 'string' },
    steps: { type: 'integer' },
    dtype: { type: 'string' },
    peak_vram_mib: { type: 'integer' },
    weights_written: { type: 'boolean' },
    adapter_path: { type: 'string' },
    adapter_bytes: { type: 'integer' },
    loss_series: { type: 'array', items: { type: 'number' } },
    wall_clock_s: { type: 'number' },
    evidence: { type: 'string' },
  },
  required: ['base_model', 'steps', 'dtype', 'weights_written', 'adapter_path', 'loss_series', 'evidence'],
}

const EVAL_SCHEMA = {
  type: 'object',
  properties: {
    held_out_n: { type: 'integer' },
    baseline_pass: { type: 'integer' },
    candidate_pass: { type: 'integer' },
    first_vs_last_pct: { type: 'number', description: 'the NAIVE metric — reported only to show what it would have claimed' },
    mean_first_half: { type: 'number' },
    mean_second_half: { type: 'number' },
    ols_slope_per_step: { type: 'number' },
    loss_stdev: { type: 'number' },
    trend_is_improvement: { type: 'boolean' },
    regressions: { type: 'array', items: { type: 'string' }, description: 'problems solved before that now fail' },
    verdict: { type: 'string', enum: ['PROMOTE', 'REJECT', 'INCONCLUSIVE'] },
    reasoning: { type: 'string' },
    evidence: { type: 'string' },
  },
  required: ['held_out_n', 'baseline_pass', 'candidate_pass', 'mean_first_half', 'mean_second_half', 'ols_slope_per_step', 'trend_is_improvement', 'regressions', 'verdict', 'evidence'],
}

const RULES = `
NON-NEGOTIABLE RULES:
  * Report only real measurements. Never synthesise a loss curve. This repo already
    contains scripts/generate_phd_paper_figures.py:199-202 which plots
    initial_loss*(1-0.201*(1-exp(-e/5))) + gaussian noise as if it were a measurement.
  * SKIPPED is a result. scripts/post_implement_training.py correctly refuses to train
    on unverified rows and reports why — that refusal machinery is the most trustworthy
    code in the training stack. Preserve that behaviour; do not "fix" it by training anyway.
  * Never promote on a first-vs-last loss delta. Use a trend test on held-out data.
  * Never promote if any previously-solved problem now fails.
  * T4 is sm_75 (Turing): it has fp16 tensor cores but NO bf16 tensor cores, and
    FlashAttention-2 requires sm_80+. Use fp16 and an SDPA/xformers backend. Note that
    torch.cuda.is_bf16_supported() returns True here anyway — it is not a reliable guide.
  * Use .venv/bin/python, PYTHONPATH=repo root.
`

phase('Gate')
const gate = await agent(
  `${RULES}

Decide whether tonight's training may proceed. Refusing is a valid, frequent outcome.

Check every one of these and report honestly:

1. EPISODES. Count rows in data/episodes/*.jsonl. Then count how many are actually
   CONSUMABLE by loading them through the real reader — anse/jepa/dataset.py drops any
   row lacking metadata["tests_total"] into skipped["unverified"] silently
   (:222-226), and LoopTrace.metadata defaults to {} (harvester.py:60). Report both
   numbers. If consumable << available, that is the finding and training should refuse.

2. DISTINCT TASKS. anse/jepa/dataset.py:389 silently falls back to an ITEM-level split
   when there are too few distinct tasks — which recreates exactly the 49/120
   duplicate-row leakage that produced the bogus Phase-2 r=0.40 headline. Count
   distinct tasks. If too few for a task-level split, REFUSE rather than accept a
   silent item-level split. Note data/interactions.jsonl currently holds 3 rows all
   with task="test task" and hidden_state_dim=16 — test fixtures in the production
   path. Do not train on those.

3. FROZEN SPLIT. Confirm EVAL/TRAIN overlap is exactly 0 by hash.

4. GPU EXCLUSIVITY. Training needs the card. Unload inference models
   (\`ollama stop <model>\`) and confirm free VRAM via nvidia-smi. T4 usable is
   14,912 MiB. Report free MiB and whether any llama-server still holds memory.

5. LARGEST BASE THAT FITS. For 4-bit NF4 QLoRA with gradient checkpointing and 8-bit
   paged AdamW, determine the largest base that trains with headroom in the free VRAM.
   Note scripts/post_implement_training.py:189 budgets ~11,000 MiB for "7B" while the
   only real run (0.5B) peaked at 1,495 MiB — so that budget is untested. Measure or
   reason carefully and state which. The user's goal is to train the LARGEST feasible
   model overnight, so this number matters.

Set proceed=false with a specific refusal_reason if any check fails.`,
  { label: 'train-gate', phase: 'Gate', schema: GATE_SCHEMA }
)

if (!gate.proceed) {
  log(`REFUSED: ${gate.refusal_reason}`)
  return { gate, training: null, evaluation: null, promoted: false, outcome: 'refused' }
}

phase('Train')
const training = await agent(
  `${RULES}

Run the QLoRA consolidation on the T4.

Base: ${gate.largest_base_that_fits}
dtype: ${gate.dtype || 'fp16 (sm_75 has no bf16 tensor cores)'}
Free VRAM at gate: ${gate.vram_free_mib} MiB
Consumable episodes: ${gate.episodes_consumable}

Use the existing step-by-step engine rather than writing a new trainer:
scripts/night_training_workflow.py implements ARTIFACT -> DATA -> FIT -> EVAL -> GATE
and journals each step for resumability. Note it currently lives only on the
night/remediation-2026-09-25 branch — if it is absent here, say so and use
train_checkpoint.py's live SFTTrainer path instead.

CRITICAL on train_checkpoint.py: at :210-220 it silently falls back to
_execute_dry_run_training() — a config-only receipt with no weights — if any of
torch/peft/transformers/trl/datasets is missing OR cuda is unavailable, and the caller
cannot distinguish that from a real run. Nine such DRY_RUN receipts already exist on
disk. Assert explicitly that adapter_model.safetensors was written with a plausible
size, and report adapter_bytes. If no weights were written, weights_written=false and
this night FAILED — do not report it as trained.

Record the FULL loss series, every step, not just the endpoints. Report peak VRAM.`,
  { label: 'qlora-train', phase: 'Train', schema: TRAIN_SCHEMA }
)

if (!training || !training.weights_written) {
  log('Training produced no weights — nothing to evaluate or promote.')
  return { gate, training, evaluation: null, promoted: false, outcome: 'no_weights' }
}

phase('Evaluate')
const evaluation = await agent(
  `${RULES}

Evaluate the candidate adapter honestly on the FROZEN held-out set.

Adapter: ${training.adapter_path} (${training.adapter_bytes} bytes)
Loss series from FIT (${training.loss_series.length} points): ${JSON.stringify(training.loss_series)}

Do ALL of the following and report each:

A. Compute the NAIVE first-vs-last percentage change and report it as
   first_vs_last_pct. You are reporting it to demonstrate what the old gate WOULD have
   claimed — not to make a decision from it.

B. Compute the honest trend statistics: mean of the first half vs mean of the second
   half, an OLS slope per step, and the series standard deviation. If stdev is
   comparable to the claimed effect, the result is noise and the verdict is
   INCONCLUSIVE, not PROMOTE.

C. Run a REAL held-out evaluation: load the frozen EVAL problems, attempt them with
   (i) the baseline model and (ii) the base+candidate adapter, verify both with the
   real domain verifier, and compare verified pass counts. This requires actual forward
   passes. An eval that completes in microseconds performed no inference — the previous
   gate ran in 3.2e-05 s and that is how the 15.41% claim happened.

D. Detect REGRESSIONS: list any EVAL problem the baseline solved that the candidate
   does not. Any regression forces REJECT.

Verdict rules, applied mechanically:
  PROMOTE      only if candidate_pass > baseline_pass AND regressions is empty AND
               trend_is_improvement is true
  REJECT       if regressions is non-empty OR candidate_pass < baseline_pass
  INCONCLUSIVE otherwise (including when the effect is within noise)

Paste verbatim command output as evidence.`,
  { label: 'honest-eval', phase: 'Evaluate', schema: EVAL_SCHEMA }
)

phase('Promote')
const promoted = evaluation && evaluation.verdict === 'PROMOTE'
log(`Verdict: ${evaluation ? evaluation.verdict : 'NONE'} — ${promoted ? 'promoting' : 'keeping yesterday\'s adapter'}`)

const record = await agent(
  `${RULES}

Record tonight's outcome and act on the verdict.

Verdict: ${evaluation.verdict}
Reasoning: ${evaluation.reasoning || '(none given)'}
Naive metric that the old gate would have reported: ${evaluation.first_vs_last_pct}%
Honest trend: mean ${evaluation.mean_first_half} -> ${evaluation.mean_second_half}, slope ${evaluation.ols_slope_per_step}/step
Held-out: baseline ${evaluation.baseline_pass} vs candidate ${evaluation.candidate_pass} of ${evaluation.held_out_n}
Regressions: ${JSON.stringify(evaluation.regressions)}

If PROMOTE: version the adapter, write a promotion receipt including the held-out
numbers and the episode ids it trained on, and update the active pointer. Note that
daily_trainer_daemon.py on main has NO weight verification — it takes the path at :72
and records a deployment at :85. Do not use that path unless the adapter has been
verified to contain real weights.

If REJECT or INCONCLUSIVE: keep the existing adapter, and write the report anyway. A
night that correctly declines to promote is a successful night.

Append to docs/remediation/NIGHTLY_LOG.md: date, episodes trained on, base model,
peak VRAM, honest trend stats, held-out deltas, verdict, and what would need to change
for the verdict to flip. Include the naive-vs-honest metric comparison every time — it
is the standing reminder of why this gate exists.`,
  { label: 'promotion-record', phase: 'Promote' }
)

return { gate, training, evaluation, promoted, record }
