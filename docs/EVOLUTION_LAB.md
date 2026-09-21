# Evolution Lab: goals, use cases and workflow for Phases 1 to 3

## Goal

Every claimed improvement of ANSE must be **measured on a real model, against an
independent check, with a gate that can fail**. A failing gate is a result, not
an embarrassment: it says what to work on next.

Per phase:

| Phase | Goal |
|---|---|
| 1 Reality engine | On simple tasks, the loop improves verified results (hidden tests), within a task (retries) and across tasks (memory), and never reports a false success. |
| 2 JEPA intuition | Predicted energy is useful on tasks the model has never seen: better than trivial baselines, and good enough to choose which candidate to execute. |
| 3 Autopoiesis | A component is replaced only by a child that is proven equivalent and measurably better than noise, through a swap that can be rolled back. |

## Workflow (the same five steps for every phase)

1. **Baseline.** Read the code, list concrete defects, measure current behaviour on a real model.
2. **Evolve behind a parameter.** Each improvement is opt-in (`hidden_tests=`, `lesson_memory=`, `adaptive_retry=`, `pair_mode=`, registry root), so the old path stays runnable for comparison.
3. **Run five use cases.** One runner per phase: `run_phase{1,2,3}_evolution.py`. Each use case answers one question and stores raw evidence rows.
4. **Gate.** One boolean goal per use case, computed from the measured numbers. Exit code 1 if any goal fails.
5. **Review, then promote or report.** A skeptical review re-runs the evidence looking for leaks, gates that are true by construction and unsupported numbers. Findings are fixed and the runner is re-run.

Results land in `results/phase{N}_evolution/results.json` and are shown, read-only,
in the web interface under **Evolution Lab** (`PORT=5000 python3 web/server.py`, tab
"Evolution Lab" or `/#evolution`; API: `GET /api/evolution`, `GET /api/evolution/{1|2|3}`).

Multi-agent version of steps 2 to 5 (as used for Phases 2 and 3): three builders with
disjoint file ownership, then one skeptical reviewer per build, then a fix step for
every confirmed major finding.

## Phase 1: what changed and the five use cases

Defects found: could not run without a GPU (`api_base_url` unused); energy was
self-graded (`assert True` scored 0); energy was all-or-nothing; memory was written
and never read; a reply without code crashed the loop; the retry prompt did not
contain the failing code; the sandbox runner raised `NameError` on any `OSError`;
Tier 1 had no memory or CPU limit.

Evolutions: `APIExtractor` (Ollama/vLLM, real embeddings), hidden tests with graded
energy, verified-only lesson memory, adaptive retry (diagnose before fixing, warn and
raise temperature when the model repeats itself), rlimits in Tier 1.

| UC | Question |
|---|---|
| 1 Honest energy | How often does the legacy self-graded loop claim convergence on code that fails hidden tests? |
| 2 Learning from pain | Do retries rescue verified failures? Plain retry vs adaptive retry. |
| 3 Pain prompt ablation | Does including the failing code raise the retry fix rate? |
| 4 Memory transfer | Do lessons from train tasks help on unseen sibling tasks? |
| 5 Robustness | Do hostile replies ever crash the loop, converge falsely or poison memory? |

Suite: `tasks/phase1_evolution.yaml`, 20 simple tasks in 5 families (2 train + 2 unseen
siblings each), every reference solution verified against its own hidden tests via an out-of-process trusted driver.

Measured (`qwen2.5-coder:1.5b`, 20 tasks, 2 real seeds, 266 generations) — gate **4 of 6**:

| UC | Result | Goal |
|---|---|---|
| 1 | Legacy loop claimed 11 of 20 converged; hidden tests verify 7. **4 false convergences (36%)**. | informational |
| 2 | Verified pass@1 42.5% -> pass@3 52.5%. Plain retry rescued 4 of 23 failures; adaptive retry rescued 2. Mean energy rises across retries (22.5 -> 24.0 -> 29.0). | plain PASS, adaptive **FAIL** |
| 3 | Retry fix rate with the failing code in the prompt 4/16, without 2/16. | PASS (small n) |
| 4 | Unseen sibling tasks: pass@1 35% with and without memory; pass@3 50% off vs 40% on; 1 gain, 3 regressions. | **FAIL** |
| 5 | 8 hostile scenarios: 0 crashes, 0 false convergences, 0 poisoned memories. | PASS |

What this says: hidden tests are necessary (a third of legacy "successes" were wrong).
`adaptive_retry` and `lesson_memory` are **not supported by the evidence** with this model
and stay opt-in, off by default. Two leads from the data: the loop returns the *last*
attempt although energy often rises on retries (keep the best-so-far instead), and
lessons injected as full solutions may distract a 1.5B model (try shorter lessons, or a
larger model).

Run history: the first run found that plain retry rescued 0 of 22 failures and that Ollama
0.1.44 silently ignores `seed`/`temperature` on `/v1/chat/completions`, so two "seeds"
were one sample. It is kept in `results/phase1_evolution_run1_seed_ignored/`. Runs now use
`ollama_native=True` and start with a seed sanity check.

## Phase 2: what changed and the five use cases

Defects fixed: context and target were the same state (the predictor learned identity);
1536-dim embeddings were zero-padded to 4096; train/validation split leaked tasks;
inference did not normalise inputs the way training did; duplicate traces inflated
counts. New: `rank_candidates` to choose what to execute.

UC1 intuition vs constant baseline, UC2 pass/fail AUC, UC3 predictive-pairs ablation,
UC4 intuition-guided candidate selection, UC5 robustness. All scored on held-out
**tasks**, first attempts only (retries leak their own label: a retry exists only
because the previous attempt failed).

Measured on the corrected Phase 1 traces (154 verified states, 20 tasks, 101 transitions,
5 training seeds, task-level 4-fold CV) — gate **2 of 5**:

- UC1 **FAIL**: held-out MAE 14.0 to 15.0 vs 12.3 to 12.6 for the train-mean constant; ridge regression on the raw embedding ~13.1.
- UC2 PASS, barely: first-attempt AUC mean 0.606 (worst seed 0.548); a linear probe on the raw embedding gets 0.669.
- UC3 **FAIL**: relative error vs "nothing changes": self-pairs 1.25, mixed 1.09, transition-only 0.97 (the only arm below 1); 52 of 101 transitions have unchanged code.
- UC4 **FAIL**: on 30 decidable picks, intuition 40.0% vs random 44.3% vs oracle 100%.
- UC5 PASS: no collapse, dimension mismatch raises, NaN/empty skipped, predictions bounded, raw and normalised inputs agree.

What this says: the JEPA latent currently adds nothing over a linear probe on the same
embedding, and must not be used to skip sandbox executions yet. The embedding is of the
whole reply text, not of the code; embedding the code alone is the first thing to try.

## Phase 3: what changed and the five use cases

Defects fixed: the hot swap only printed text; the parent baseline was never measured;
one noisy timing decided swaps; a faster but wrong child was accepted. New: equivalence
gate run by a trusted driver in a separate process (the child cannot read the tests or
the nonce), interleaved repeated measurement with a noise margin, versioned registry
with promote/rollback and an append-only lineage, held-out differential oracle.

UC1 better child promoted (5/5, median speed-up 75x), UC2 fast-but-wrong rejected
(5/5; the legacy rule would have accepted all 5), UC3 A/A noise test (0 false
promotions in 15 trials; legacy rule 5 of 15), UC4 rollback (5/5 restored), UC5
LLM-proposed children (4 proposals, 2 correct, 2 promoted, 0 incorrect promoted).

Current gate: **5 of 5**. Caveat: 0/15 only bounds the false-promotion rate below
roughly 18% at 95% confidence.

## Known limitations


- Tier 1 sandbox has no filesystem or network isolation; Tier 2 (Docker) is untested
  here because the `docker` package is not installed.
- Running `tests/phase3/test_neuro_surgeon.py` rewrites the tracked file
  `.antigravity_attestation`.
- Sample sizes are small (20 tasks, 2 seeds). Treat differences of one or two tasks as noise.
