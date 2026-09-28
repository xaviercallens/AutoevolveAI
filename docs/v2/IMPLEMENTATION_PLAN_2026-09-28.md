# Low-tier model intelligence: implementation plan, revision 2026-09-28

Companion to [`../ROADMAP_V1_V2_COMPANION.md`](../ROADMAP_V1_V2_COMPANION.md) (strategy,
2026-09-21) and [`tasks.yaml`](tasks.yaml) (cards). This revision reconciles the plan with
what was **measured** between 2026-09-21 and 2026-09-28, fixes the reason no card could
ever be accepted, and sets the next sprints. Everything below is tagged MEASURED (with the
file that holds the number), EXISTS (code on `main`, not measured for the roadmap's
purpose), or OPEN.

## 1. What "low-tier intelligence" measured to, so far

| Signal | Result | Where |
|---|---|---|
| Phase 1 (20 coding tasks, qwen3:8b Q4 on the T4) | 16/20 converged | `results/phase1_evolution/` (2026-09-21) |
| Phase 2 energy surrogate | r ≈ 0 on task-held-out splits | roadmap §1 |
| Phase 3 Micro-ML architect | 0/10 (qwen3:8b), 0/4 (qwen2.5-coder) | roadmap §1 |
| Lean hardness ladder, T0 (Mathlib lemmas) | DeepSeek-Prover-V2-7B 6/10, Goedel-Prover-V2-8B 8/10 | `results/hardness/baseline.json` |
| Lean hardness ladder, T1–T3 (curve facts) | **0/12 on every tier, both provers**; 0 false items accepted in 118 | same; LL.md §4c |
| JEPA world model on 206 real verdicts (cosmo3) | indistinguishable from a shuffled-label control; `energy_accuracy` saturated at 1.00 for both | `results/cosmo3_learning/` |
| Agentic pipeline with tiered models (3 cosmology problems) | all three within preregistered tolerance; the hard stages (Lean, adversarial referee) ran on the top tier, fits and papers on the default tier | LL.md §12, `results/{desi_dr2_bao,bao_bbn_h0,eboss_vs_desi}` |

Two readings follow, and they set the plan.

1. **On this hardware the 7–9B models are competent executors and poor discoverers.**
   They pass fixed-form tasks (Phase 1, T0) and fail every task that needs a strategy
   change (Phase 3) or an API vocabulary they were not shown (T1–T3: both provers write
   `simp [W, WeierstrassCurve.Δ] <;> norm_num <;> rfl` on every curve and never name
   `WeierstrassCurve.b₂/b₄/b₆/b₈`). The cheapest intelligence gain is therefore
   **retrieval into the prompt**, not weight updates: premise retrieval for Lean
   (TODO 5 / card M-1), episode retrieval for coding (N-6).
2. **No learned component has yet beaten a control.** The surrogate (Phase 2) and the
   world model (cosmo3) both sit at chance once leakage and label-shuffling controls are
   applied. Until one does, nothing learned may gate, order or skip a verifier (roadmap
   §3 already says so for the surrogate; it now applies to JEPA as well).

What did work is the **orchestration shape**: preregistered targets, verifiers with
positive and negative controls, a claim ledger, an adversarial referee that re-runs the
work, and routing by tier. That is the v2 "cards + driver" idea, exercised at problem
scale rather than card scale. The cards remain the right unit for low-tier execution.

## 2. Why zero of 42 cards were ever accepted, and the fix

`docs/v2/status.json` does not exist: no card has been marked done since the workflow was
written. Three causes, all structural:

- **Both acceptance blocks are unrunnable on this host (measured 2026-09-28).** 5 cards use
  `acc_full`, which ran the whole suite with `--cov-fail-under=100`; the suite has 22
  environment-bound failures (Laya model, Chromium, Lean cache) and repository coverage is
  nowhere near 100 %. The other 25 cards use `acc_v2`, which demanded 100 % of *all* of
  `anse/v2`: running it exactly as written gives **13 passed, coverage 83.53 %, FAIL**,
  because the package is filled with modules no card owns (next bullet). So every card
  failed its gate before any work started. `.venv-v2` was never built either.
- **Much of Phase 0/C/N landed elsewhere under other names** (table in §3), so the cards
  read as undone while their acceptance criteria are partly met on `main`.
- **`anse/v2/` filled up with the opposite design.** 1,460 lines (`engine_v2`,
  `mezo_optimizer`, `popperian_adversary`, `rem_consolidation`, `surrogate_cache`)
  implement the four proposals roadmap §3 argued *against* (MeZO, surrogate gating,
  unvalidated adversary, in-process consolidation). They arrived with the merged
  `AIautoevolveClaudeGCP` branch, have 13 tests, and no measurement against the roadmap's
  replacements. They are not on any promotion path and must not be until card X-1 measures
  them (see §5).

**Fix (applied in `tasks.yaml`, this revision):** both blocks are scoped to the card: *its
named tests + `tests/v2`, at 100 % line+branch coverage of the module(s) the card itself
creates or edits + `python test_rigor_guard.py` (+ `ruff check` on the touched files for
`acc_full`)*. Card X-1 restores the whole-package 100 % once the foreign modules are measured
or moved. Repository-wide health is the release gate
(`scripts/verify_release.py`, CHANGELOG measured-gates section), not a per-card gate. The
driver still re-runs the accept commands itself; the transcript is still not evidence.

## 3. Card reconciliation (all 42, plus what landed outside the cards)

Status: OPEN (nothing), PARTIAL (a real piece exists on `main`, evidence path given, card
not accepted), DONE-ELSEWHERE (criteria met on `main` by other work; run the card's accept
to confirm and mark it), SUPERSEDED (replaced by a measured decision).

| Card | Status | Evidence / note |
|---|---|---|
| V0-1 group-aware split | PARTIAL | `anse/jepa/dataset.py::train_val_split` splits by task and logs when it cannot; no `group_by_task` flag on `JEPATrainer.train`. |
| V0-2 de-duplicate on ingest | PARTIAL | `JEPADataset(deduplicate=True)` drops `(task, iteration, hidden state)` duplicates; not the card's `(task, code)` key. |
| V0-3 metrics for a zero-inflated target | **OPEN, now urgent** | cosmo3: `energy_accuracy` = 1.00 for real *and* shuffled labels. Without this card no learning claim is measurable. |
| V0-4 VICReg NaN on batch < 2 | DONE-ELSEWHERE | `tests/phase2/test_trainer.py::test_trailing_single_sample_batch_does_not_poison_weights`. |
| V0-5 frozen benchmark split with hash manifest | DONE-ELSEWHERE | `results/hardness/frozen_split.json`; `scripts/hardness/freeze_split.py`; trainer drops frozen propositions. |
| V0-6, V0-7 Phase 3 pain signal / budget ladder | OPEN | Phase 3 still 0/10; no ladder. |
| T-1 MBPP → task yaml | OPEN | |
| A-1 generator protocol | OPEN | `APIExtractor`, `OllamaExtractor`, `HiddenStateExtractor` exist with different contracts. |
| A-2 TransformersExtractor (real hidden state) | OPEN | still no HF backend; hidden states in every dataset so far are embeddings, not generator states. |
| A-3 4-bit loader + smoke runner | PARTIAL | `scripts/night_training_workflow.py` loads NF4 QLoRA at ~8.1 GiB (LL.md §4); no Phase 1 runner on it. |
| GA | OPEN | blocked by A-2. |
| B-1 episode store (SQLite) | PARTIAL | JSONL + Chroma (`anse/memory/harvester.py`, atomic append); `results/*/episodes.jsonl`; no SQLite, no schema versioning. |
| B-2 best-of-N sampler | OPEN | `pass@3` was tried once on the ladder (rescued nothing, LL.md §4) but no reusable sampler. |
| B-3 harvest runner | PARTIAL | `scripts/harvest_episodes.py` (hidden-test tasks, sandbox verdicts). |
| GB data volume (5 k episodes, 1 k pairs) | **OPEN, far** | measured 2026-09-28: 206 cosmo3 episodes, 834 Phase-1 trace rows (mostly unverified), 200 `dpo_200_unified` rows, 100 `redis_ltm_lora` rows, 5 `dpo_phase1_live`, 118 ladder attempts. Roughly 1.3 k rows, < 400 with a verifier verdict, ~200 pairs. |
| C-1 secret/PII scrubber | DONE-ELSEWHERE | `anse/memory/transcript_ltm.py::scrub` (email, home paths, tokens); 8,940 replacements on the 2026-09-28 ingest. Needs the card's dedicated test suite → keep PARTIAL until then. |
| C-2 curator (SFT/DPO files, policy, replay) | PARTIAL | `scripts/ltm_learning_mix.py` enforces the ≤ 30 % dilution cap, but its output is **not read by the trainer** (LL.md §11f, TODO 11). |
| C-3 adapter registry with rollback | PARTIAL | `anse/autopoiesis/registry.py::ComponentRegistry`; `daily_trainer_daemon` refuses DRY_RUN adapters. No adapter-level rollback test. |
| C-4 promotion gate (pure function) | PARTIAL | `night_training_workflow.py` GATE returns BLOCKED because the held-out pass@k eval (P4-5) does not exist. The gate is honest; it cannot yet say yes. |
| C-5, C-6 nightly orchestration / systemd | PARTIAL, **unverified on this host** | `scripts/nightly_dream_phase.py`, `nightly_retrain_at_5am.py`, `setup_nightly_cron.sh` landed 2026-09-28 (commit 6ecf6ee). Their reports were produced on another machine (`/home/xavkal/...`, CPU profile), on 12–16 traces; none acquires the shared GPU lease; the cron is not installed here (`crontab -l` shows only the VM schedule). Do not schedule on this host before card G-1. |
| GC (+5 pts on never-touched split) | OPEN | needs C-4's eval first (card C-7). |
| D-1 surrogate baseline ladder | OPEN | |
| D-2 shadow-mode wrapper | PARTIAL | `anse/v2/surrogate_cache.py` exists but is wired as a filter ("< 2 ms thought filtering"), i.e. the opposite of shadow mode. |
| GD | OPEN | AUROC never computed (needs V0-3). |
| E-1..E-3, GE adversary | OPEN | `anse/v2/popperian_adversary.py` exists without a spec validator or seeded-bug suite. |
| F-1 writable-set guard | OPEN | |
| F-2 gated self-patch | OPEN | `anse/autopoiesis/neuro_surgeon.py` now measures timings (release 13.2.0) but has no promotion gate around it. |
| GF | OPEN | |
| N-1 transcript parser | DONE-ELSEWHERE | `transcript_ltm.py::parse_transcript`; ingested 10,219 turns / 114 sessions on 2026-09-28. |
| N-2 segment into episodes with verification | OPEN | turns are stored `trainable=False`, retrieval only. |
| N-3 live hook spool | OPEN (human) | |
| N-4 Antigravity adapter | OPEN | |
| N-5a math verifier | **DONE-ELSEWHERE, stronger than the card** | `anse/formal/lean_runner.py::verify_file` (kernel + axiom whitelist, file mode, PR #6) plus PARI/Sage ground truth (`scripts/hardness/`). The 2026-09-21 decision "Lean not needed yet" is reversed by evidence: the pinned build is cheap (4–12 s per module) and 254 theorems exist. |
| N-5b physics verifier (dimensions) | PARTIAL | cosmo3 used CAMB/CLASS anchors and closed-form limits as verifiers; no reusable `pint` check. |
| N-6 retrieval memory | DONE-ELSEWHERE | Chroma `literature` (284 chunks), `claude_code_sessions`, `lean_premises` (1,000 signatures); `Harvester.query_similar`. |
| N-7 companion MCP server | OPEN | LeanMaster MCP is wired; no companion server. |
| N-8 what may the companion train on | **OPEN (human), now pressing** | `results/redis_ltm_lora_dataset.jsonl` (100 rows) and `nightly_dream` training inputs are transcript-derived. Roadmap §4.5 says they are not training targets until this decision is written. Card N-9 quarantines them in code. |

Landed outside the card system and relevant to intelligence:
- **Hardness ladder + frozen split** (`scripts/hardness/`, `results/hardness/`): 59 generated,
  Sage-validated Lean items in 5 tiers, with false variants; the only instrument on this
  machine that measures prover capability under pressure. It becomes the math half of GC.
- **GPU lease** (`/mnt/disks/disk-socrateai-local-1/gpu_lease/`): every GPU-touching
  runner must acquire it; nothing enforces that yet (card G-1).
- **Call logging** (`APIExtractor` → JSONL + Redis + Chroma `llm_calls`): every prompt/answer
  is retained, which is what B-1 wanted for provenance.
- **200-problem "unified eval"** (`results/200_unified_eval_report.json`, commit f837350):
  reports 98.5 % verification and a 8.3 × 10⁵ "algorithmic speedup" over 200 problems in
  141 s, with a JEPA "CONVERGED_SOUND" line (val loss −93 %). As established in the
  2026-09-26 audit, the 200 benchmark cases embed their own reference solutions and the
  runners execute them; 200 problems in 141 s is consistent with that and not with model
  generation. Treat it as an infrastructure smoke test. Its JEPA number has no shuffled-label
  control and is not evidence of learning.

## 4. Model plan for the T4 (unchanged decision rule, still partly unmeasured)

Present on the main Ollama store (2026-09-28): `qwen3:8b`, `qwen2.5-coder:7b-instruct`,
`mistral:7b-instruct`, `DeepSeek-Prover-V2-7B` (Q8_0), `Goedel-Prover-V2-8B` (Q6_K),
`qwen3-embedding:0.6b`. `Qwen3.5-9B` and `Qwen3.8-27B` are **not** present; the isolated
Ollama on port 11435 is gone. `MODEL_SELECTION_T4.md` therefore stands: provisional pick
Qwen3.5-9B for train+serve, 27B unmeasured. Two additions from this week:

- **Provers are a separate track.** DeepSeek-Prover-V2-7B (plain completion prompt) and
  Goedel-Prover-V2-8B (thinking model: read `content` + `thinking`, take the last Lean
  block) are the math executors; Goedel leads on T0 (8/10 vs 6/10). Neither is trainable
  and served at the same time as the coding model: one model fits the T4.
- **Tiering is a first-class design input, not a fallback.** In the cosmology run the
  default tier executed fits and papers to tolerance, and the top tier was needed for Lean
  and for the adversarial referee. The card `tier` field should be extended with a
  `verifier_tier` (which tier may sign off) once GC exists.

## 5. Sprints (each ends on a number, none starts before the previous number exists)

**Sprint 0 — make the workflow able to say yes (1–2 days, all `low`/`mid`)**
1. Build `.venv-v2` (`tools/setup_v2_env.sh`), run `tools/v2_tasks.py check` (passes: 42
   cards + this revision's additions, no cycles).
2. Run the accept blocks of V0-4, V0-5, N-1, N-5a, N-6 as they now stand and mark the ones
   that exit 0 with `tools/v2_tasks.py done`. Expected: 3–5 cards done on day one, with
   evidence, none by assertion.
3. **V0-3** metrics (AUROC, Spearman, calibration on a few-valued target) and **V0-8**
   (new): every trainer report carries a shuffled-label control next to the real number.
   Exit: the cosmo3 retrofit re-run reports AUROC for real vs shuffled, and the two differ
   by less than the seed spread (that is the honest current state).

**Sprint 1 — retrieval before training (1 week)**
4. **M-1** (new; TODO 5): premise-retrieval A/B on the hardness ladder, same items, same
   seed, both provers, top-5 `lean_premises` hits prepended. Exit: per-tier pass rates for
   both arms in `results/hardness/retrieval_ab.json`. This is the single measurement most
   likely to move low-tier math intelligence; T0 is saturated, T1–T3 is where it shows.
5. **N-6 → coding**: retrieve the 3 nearest verified episodes into the Phase 1 prompt and
   re-run the 20-task gate on qwen3:8b. Exit: pass count vs the 16/20 baseline, 3 seeds.
6. **G-1** (new): a `require_gpu_lease()` helper used by every runner under `scripts/` and
   `v2_runners/` that touches Ollama or CUDA, plus a test that greps for offenders. Exit: the
   grep test passes; the nightly scripts from 6ecf6ee either acquire the lease or are not
   scheduled here.

**Sprint 2 — an honest flywheel (2 weeks)**
7. **C-7** (new; P4-5): held-out pass@k on the frozen ladder + Phase 1 hold-out, written
   before any adapter is judged; C-4's gate consumes it instead of returning BLOCKED.
8. **C-0** (new; TODO 11): the trainer reads `ltm_learning_mix.py`'s output; the dilution
   ratio becomes load-bearing.
9. **A-1/A-2/A-3**: HF backend with the generator's real hidden state (needed for any
   surrogate claim; embeddings are not generator states).
10. **B-1/B-2/B-3** toward **GB**: the only realistic source of volume is self-generated,
    verified samples (best-of-N on the task pool + the ladder), not transcripts. Exit: 5 k
    episodes, 1 k pairs, ≥ 200 tasks, all with verifier verdicts.
11. **N-9** (new): transcript-derived datasets are tagged `origin=transcript` and refused by
    the curator until `docs/v2/gates/N8.md` exists.

**Sprint 3 — the thesis test: GC.** One nightly consolidation (QLoRA SFT on winners + DPO on
pairs, 30 % replay, under the lease), evaluated by C-7 on never-touched items, 2 of 3 seeds.
**If +5 points does not appear, stop and rethink data before D–F**, as the roadmap says.

**Parked until GC:** D (surrogate), E (adversary), F (autopoiesis), and **X-1** (new): measure
`anse/v2`'s MeZO/EWC/surrogate-filter modules against the SFT+DPO path on the same data, or
move them under `anse/v2/experimental/` with their tests; they must not sit on the import
path of the engine as if they were the plan.

## 6. Risks that are already visible

- **Metric saturation** (V0-3) can make any future report look like learning. It is the
  first card for that reason.
- **Transcript training** (N-8) is being done de facto by scripts that landed this week;
  the policy decision is the user's and is overdue.
- **GPU contention**: three sessions share one T4; only lease-holding runners are safe.
- **Provenance drift across machines**: reports committed from `/home/xavkal/...` describe a
  different host. Every report should record host, interpreter and lease id (TODO 21).
- **Volume**: at 10–50 verified episodes per day, GC is weeks away without the self-play
  sampler; do not let that pressure weaken the "verified only" rule.
