# ANSE roadmap: v1 hardening, v2, and the Night-School coding companion

Date: 2026-09-21. Based on the first runs of Phases 1-3 against a real open-weight model
(`qwen3:8b` Q4_K_M + `qwen3-embedding:0.6b`, Ollama, Tesla T4 16 GB), not on mocks.

## 1. What the live runs actually showed

| Phase | Measurement | Result | Verdict |
|---|---|---|---|
| 1 | 20-task benchmark, generate → sandbox → energy | 16/20 converged (80 %, DoD 70 %) at ~36 tok/s | **Works** |
| 2 | JEPA energy head, random split on 120 rows | r = 0.40, skill 32 % | **Invalid**: 49/120 rows were duplicates leaking across the split |
| 2 | Same, de-duplicated (71 rows), *whole tasks* held out, 10 splits | mean r = -0.002, median MAE skill 11 % | **No evidence** the latent ranks unseen tasks by energy |
| 3 | Micro-ML architect, qwen3:8b, 3 and 5 turns | 0/6 and 0/4 reach ENERGY 0 | **Fails** |
| 3 | Same, qwen2.5-coder:7b, 5 turns | 0/4; params 27.3 M → 122,890 then plateau | **Fails**, but descends |
| 3 | Anti-simulation axiom on real generations | 4/4 clean, control stub caught | **Works** |
| 3 | Attestation minted only when physically valid | True in every run | **Works** |
| - | Unit suite | 570 tests, 100 % line + branch | **Works** |

What this means:

- **The symbolic side is solid.** The sandbox, the energy evaluator, the AST whistleblower
  and attestation never issued a false pass to a real model. This is the asset.
- **The "intuition" side is unproven.** The MAE "skill" that survives is an artefact: energy
  is 5-valued and mostly 0, so any predictor near 0 beats the *mean* on MAE. Correlation on
  unseen tasks is zero. At n = 71, with a latent from a *separate* embedding model, this was
  the expected outcome; it is a data and representation problem, not a bug.
- **Feedback alone does not produce insight.** In Phase 3 both models respond to the pain
  signal (they shrink layers every turn) but never make the one structural move required
  (pool the 3×64×64 input before the first Linear; `Linear(12288, 10)` alone is 122,890
  params). Scalar "you failed" plus a trace drives local descent, not a change of strategy.
- **Live runs find bugs the mocked suite cannot.** This session: missing `subprocess` import
  in both sandbox runner scripts, Docker fallback catching the wrong exception class, a
  hard-coded single noisy benchmark deciding hot-swaps, and a trailing single-sample batch
  turning every JEPA weight into NaN (`VICReg` variance of one sample).

## 2. v1 improvement plan (hardening what exists)

Goal: make every v1 claim either measured on real hardware or deleted. About two weeks.

### 2.1 Evaluation integrity (first, because everything else depends on it)
1. **Grouped splits everywhere.** `train_val_split` must split by `task`, never by row.
   Add a `group_key` argument; make row-level splitting opt-in.
2. **De-duplicate on ingest.** `JEPADataset` drops identical `(task, code)` rows and logs
   how many. Runners truncate their log before harvesting (done for Phase 2).
3. **Right metrics for a 5-valued, zero-inflated target.** Replace MAE-vs-mean with AUROC
   for `energy > 5` (pass/fail), Spearman ρ, and a *median* baseline. Report a bootstrap CI.
4. **Frozen held-out benchmark.** 20 tasks is a smoke test. Build 200+ tasks (HumanEval+,
   MBPP+, plus own adversarial tier), split once into train-pool / dev / **never-touched
   test**, commit the split hashes.

### 2.2 Phase 2: give the surrogate a fair chance
1. **Use the generator's own hidden state.** Ollama cannot expose it. Run
   `llama-server --embeddings --pooling mean` on the same GGUF, or load the model in
   `transformers` 4-bit and take the last-layer mean. This restores the claim the
   architecture actually makes.
2. **Scale data to 2-5 k traces** (the T4 yields ~400 traces/hour). Include task text in
   the input, since energy depends on (task, code), not code alone.
3. **Baseline ladder**: median → logistic regression on embeddings → 3-layer MLP → JEPA.
   If JEPA does not beat logistic regression on AUROC, drop the JEPA energy head and keep
   the MLP. Kill criterion: AUROC < 0.65 on unseen tasks at 5 k traces.

### 2.3 Phase 3: make active inference converge
1. **Structured pain signal.** Return the *budget arithmetic*, not just the verdict:
   per-layer parameter table, the largest offender, and the ratio to budget.
2. **Strategy escalation.** After two turns of < 2× improvement, the loop switches prompt
   from "fix this" to "your approach cannot work; list three different approaches, pick
   one" (reflection turn), then resumes.
3. **Best-of-N per turn** at T = 0.8 (N = 4) with the sandbox as selector. Cheap on a T4,
   and directly measures whether the solution is in the model's distribution at all.
4. **Task ladder** instead of one hard task: budgets 5 M → 500 k → 50 k, so convergence
   rate is a curve, not a single 0 %.
5. Compare `think: true` for qwen3 on this task only; reasoning mode is what the
   pooling insight needs, and the cost (tokens) is measurable.

### 2.4 Engineering
- Move `run_llm_*.py` into `anse/experiments/` with a shared report schema and a
  `--seed`; store every report under `reports/<date>/<git-sha>/`.
- Nightly CI job on the GPU VM: hermetic suite + a 10-minute live smoke run.
- Fix the trainer NaN at the source too: `VICRegLoss` should return 0 for batch < 2.

## 3. v2: review of the proposed concept, and what to build instead

The pasted ANSE 2.0 plan has the right skeleton (local weights, surrogate, adversary,
sleep consolidation). Four parts of it will not survive contact with the results above.

| Proposal | Problem | Replacement |
|---|---|---|
| MeZO on LoRA weights, reward = sandbox energy, "update in < 1 s" | One MeZO step = 2 full generations + 2 sandbox runs (~20 s here). Energy is 5-valued, so almost every ±ε perturbation yields *identical* energy → zero gradient estimate. MeZO needs thousands of steps on a smooth loss. | **Expert iteration / rejection-sampling fine-tuning**: sample N, keep sandbox-verified winners, SFT on them; plus **DPO** on (verified-pass, verified-fail) pairs for the same task. Both use the verifier as a selector, which is exactly what it is good at. |
| Surrogate gates Docker: reject if predicted E > 50 | Today's surrogate has r ≈ 0 on unseen tasks. Gating on it would discard good code at random. | Ship the surrogate in **shadow mode** (log predictions, never gate) until AUROC ≥ 0.80 on the frozen test set; then use it only to *order* candidates, never to skip the sandbox for accepted code. |
| Adversary rewarded when Architect's code fails | Trivially hackable: emit invalid inputs, or inputs outside the spec. | Adversary outputs must pass a **spec validator** (type/precondition check) and be confirmed against a reference oracle or property (Hypothesis-style). Reward only *valid* counter-examples. |
| Self-rewrite + `importlib.reload()` hot-swap | No rollback, no audit, and the component being swapped is the one judging the swap. | Swap via new process behind a **promotion gate**: frozen benchmark, no regression, best-of-5 timing, signed attestation, previous version kept for instant rollback. The judge (sandbox, evaluator, gate) is outside the writable set. |

Hardware: **stay on the T4 for v2.0.** QLoRA (rank 16) on a 4-bit 7-8B model fits in 16 GB
at sequence length ≤ 2048 with Unsloth, batch 1 + gradient accumulation; a 3-4B model
leaves comfortable headroom and trains ~2× faster. Rent a 24-48 GB card only when a
measured bottleneck demands it. Note the T4 has no bfloat16 and no FlashAttention-2; use
fp16 + Unsloth's Triton kernels.

### v2 phases (each has a numeric exit gate; do not start the next without it)

| # | Phase | Build | Exit gate |
|---|---|---|---|
| A | **Own the weights** | `TransformersExtractor`: HF 4-bit model + LoRA slot, same `extract()` contract as `OllamaExtractor`, returns the generator's real hidden state. vLLM or llama.cpp for fast sampling, HF for training. | Phase 1 benchmark within 3 pts of Ollama result |
| B | **Verified-data flywheel** | Harvester → SQLite (exact logs) + Chroma (retrieval). Sampler: N = 8 per task, T ∈ {0.2, 0.8}. Store pass/fail pairs. | 5 k de-duplicated traces, ≥ 1 k preference pairs |
| C | **Nightly consolidation** | QLoRA SFT on winners + DPO on pairs, 1-2 h budget, replay buffer (30 % old data) against forgetting. | **+5 pts pass@1 on never-touched test, no tier regresses > 2 pts** |
| D | **Surrogate, honest** | Baseline ladder of §2.2 on generator hidden states, shadow mode. | AUROC ≥ 0.80 unseen tasks, else stays in shadow |
| E | **Validated adversary** | Architect/Adversary self-play with spec validator + oracle. | ≥ 30 % of adversary inputs are valid *and* failing on a seeded-bug suite |
| F | **Gated autopoiesis** | Self-optimisation restricted to non-judge modules, promotion gate + rollback. | One accepted, one correctly *rejected* self-patch, both attested |

## 4. "Night School": the coding companion

A local model that watches the day's work, and retrains overnight on what was *verified*.

```
 DAY (capture)                        NIGHT (learn)                     MORNING (serve)
 Claude Code transcripts ─┐
 Claude Code hooks ───────┤  scrub → episodes →  verify  → curate → QLoRA SFT+DPO → eval gate
 Antigravity logs ────────┤  (SQLite + Chroma)  (sandbox,   (dedupe,   (T4, 1-2 h)     │
 git diffs + test runs ───┘                      Lean, sympy) balance)                 ▼
                                                                    promote adapter or keep old
                                                   companion: Ollama/llama.cpp + adapter + RAG
```

### 4.1 Capture
- **Claude Code, after the fact.** Every session is already a JSONL transcript under
  `~/.claude/projects/<project>/<session>.jsonl` (prompts, tool calls, tool results,
  replies). A nightly importer is enough to start; no live plumbing needed.
- **Claude Code, live.** Hooks in `.claude/settings.json` (`UserPromptSubmit`,
  `PostToolUse`, `Stop`) append events to a local spool; useful for exact timing and for
  tagging which test run followed which edit.
- **Antigravity.** The repo already has the StrongGravity harness hook and attestation
  receipts; extend that hook to write the same event schema. Its native log format must
  be checked on the machine where it runs; do not assume it.
- **Ground truth.** `git diff` per episode and the test/sandbox outcome that followed.
  This is what makes an episode trainable rather than just text.

### 4.2 From transcript to training example
An **episode** = (context, request) → (final accepted change) + (verification result).
Intermediate failed attempts become DPO negatives. Steps: secret and PII scrubbing
(`gitleaks` patterns, e-mail, tokens, absolute home paths) → segmentation → de-duplication
→ **verification** → domain tag.

Only verified episodes train the model:

| Domain | Verifier | Energy 0 means |
|---|---|---|
| Coding | existing sandbox + project test suite | tests pass, no stubs (Axiom 2) |
| Mathematics | Lean 4 kernel for formal statements; SymPy / numeric spot-checks otherwise | proof checks, or identity holds on random points |
| Physics | unit/dimension check (`pint`), conservation-law and limiting-case tests, small simulations | dimensions consistent, invariants hold |

Lean stays optional infrastructure (as decided for v1) until the math stream has enough
volume to justify the Mathlib build cost.

### 4.3 Night job
`systemd` timer at 01:00, only if the GPU is idle: curate → QLoRA SFT (winners) + DPO
(pairs) with 30 % replay → evaluate on the frozen test set + a personal regression set →
**promote only if better and nothing regresses**; otherwise keep yesterday's adapter and
write a report. Adapters are versioned and attested; rollback is a symlink.

Be realistic about volume: one day of work is 10-50 usable episodes. That is too little
for weight updates to matter on their own. So the companion has two memories:
**retrieval over all episodes from day one** (immediate value, no training), and
**weight consolidation weekly-ish**, once a few hundred verified episodes plus the
self-generated flywheel data (v2 phase B) are available.

### 4.4 Serving
Base model + current adapter exported to GGUF → Ollama, exposed as an OpenAI-compatible
endpoint and as an MCP server, so it can be called from Claude Code itself or an editor.

### 4.5 Two constraints to settle before building capture
1. **Terms of use.** Anthropic's terms restrict using Claude outputs to train competing
   models, and Antigravity/Gemini has similar language. A private companion is a grey
   area, not a clear yes. The defensible design trains on **your own artefacts and
   verifier outcomes** (your prompts, your repo's diffs, test results, sandbox energies,
   and the local model's own verified samples) and uses assistant transcripts for
   *retrieval and episode segmentation*, not as SFT targets. Read the current terms for
   your plan before deciding otherwise.
2. **Privacy.** Transcripts contain credentials, paths and e-mail addresses. Scrubbing is
   a hard gate before anything reaches the training set, with a test suite of its own.

## 5. Order of work

1. v1 §2.1 evaluation integrity (3 days) - everything else is measured with it.
2. v1 §2.3 Phase 3 ladder + structured pain signal (3 days) - cheapest visible win.
3. v2 A + B: own the weights, start the flywheel (1 week); Night-School importer and
   retrieval memory in parallel, since they share the episode schema.
4. v2 C: first nightly consolidation; the +5 pt gate decides whether the thesis holds.
5. v2 D-F only after C passes.
