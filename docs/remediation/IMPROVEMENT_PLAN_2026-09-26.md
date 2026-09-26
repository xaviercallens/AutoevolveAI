# AutoevolveAI — Improvement Plan & Architecture Proposal (v2), 2026-09-26

**Companion to `AUDIT_2026-09-26.md`.** v1 of this document proposed containment and an
architecture target. v2 keeps those and adds what the day's measurements changed: a
cost-optimised local-first execution model for this specific box, a graded capability
ladder, and an operational definition of the terminating condition.

**Execution model:** the five workflows in `.claude/workflows/` are the executable form
of this plan. They are authored and ready; **none has been run.** Section 8 states the
precondition that blocks the first run.

---

## 0. What the day's measurements changed

Four things were measured on this host today that invalidate prior assumptions:

| Measurement | Before | After | Consequence |
|---|---|---|---|
| **Ollama GPU placement** | CPU-only, 2.3 tok/s | **100% GPU, 34–35 tok/s warm** | 15× throughput, achieved by `systemctl restart ollama`. Ollama had started 2.5 h *before* the GPU driver existed and served on CPU ever since. Every "T4 inference" figure in this project was false; the "36 tok/s on T4" in project memory was achievable but never achieved. **Already fixed and enabled.** |
| **Lean `sorry` semantics** | assumed exit code = proof | **`sorry` compiles and exits 0** | Every proof gate keyed on `returncode` accepts unproved theorems. ~10 call sites; only `anse/formal/lean_runner.py:60` (which checks `#print axioms` for `sorryAx`) is sound. |
| **The 200-problem bank** | assumed a benchmark | **every case embeds its own solution** | `RUST_KERNELS[id]["source"]` *is* the finished program; math/physics/python cases compute a value then compare it to the same constant. No model generation anywhere. There is no problem bank yet, and no selector at all. |
| **"Peer review"** | assumed a gate | **a constant function** | `review_paper_gemini_pro.py` reads the paper only to assert `len > 1000`, then hardcodes five `score=10`, `"TOTAL SCORE: 50 / 50"`, `"ACCEPT WITHOUT RESERVATION"`, and writes it to Redis attributed to `gemini-3.1-pro` — a model never invoked (zero HTTP-client imports). The stated stopping condition would fire immediately and falsely. |

Also measured: pytest is far healthier than the gates suggested — **1017 passed, 18 failed,
8 errors** once the single uncollectable module is isolated. One missing `z3` import was
masking a substantially working suite.

---

## 0b. The two supported environment profiles

One detection engine (`anse/infrastructure/agent_environment.py`) resolves both. Verified on this host; the CPU profile's figures are from the Antigravity host's own validation run.

| | **Claude Code / GCP T4** | **Antigravity / local Linux** |
|---|---|---|
| `profile_id` | `claude_code_tesla_t4` | `antigravity_linux_cpu_31gb` |
| `coding_agent` | `claude_code` (`CLAUDECODE=1`) | `antigravity` (`ANTIGRAVITY_AGENT=1`) |
| `device` | `cuda` | `cpu` |
| GPU | Tesla T4, 15,360 MB, driver 580.178.04 | none (`nvidia-smi` absent) |
| RAM | 29.4 GB | 31.3 GB |
| `config_dir` | `.claude` | `.antigravity` |
| MCP config | `.mcp.json` | `.antigravity/mcp_config.json` |
| Generation model | `qwen3:8b` @ **36 tok/s on GPU** | CPU-tier local model |
| Embeddings | `qwen3-embedding:0.6b`, 1024-d | same, CPU |
| QLoRA ceiling | **Phi-3-mini 3.8B @ seq 1024**, 9,601 MiB, 373 tok/s | small adapters (896 trainable params measured, 869 MB RSS) |
| `supports_local_{lora,rl,jepa}` | all `True` | all `True` |

**Detection precedence is now explicit.** Both hosts' signals can coexist (e.g. Antigravity launched from a shell that still exports `CLAUDECODE`). `describe_agent_detection()` returns `{resolved, override, signals_matched, ambiguous}` so an ambiguous host is a visible finding rather than a tie broken silently by tuple order — which is precisely the bug that made PR #4's CPU test pass on one host and fail on the other. `AUTOEVOLVE_AGENT` settles it explicitly. **Deployment validation should assert on `ambiguous is False`, not on `resolved` alone.**

## 1. Principles (binding on every card, workflow and release)

1. **A release is verified against its diff, not its intent.** Read `git diff <base>...<branch>` and require every release-note claim to cite a file that diff touches.
2. **One ledger, one branch of truth**, reconciled against `git log --all` before any card runs.
3. **No unattended process runs unbounded.** Spend ceilings must be enforced by an external supervisor that kills, not by a flag the child can ignore. A prior runaway spent **$9.76** while re-deriving work that already existed.
4. **A metric is not "passing" until its computation is inspectable.** First-vs-last deltas, sentinel-value means, and hand-typed literals presented as measurements are the most-repeated defect class across two audits (11 findings, then 14).
5. **Refuse rather than fabricate.** `post_implement_training.py` declines to train on unverified rows and says why. That is the target pattern, not the exception.
6. **Free tier first, always.** Local T4 inference costs ~electricity. A paid call is only ever reached after the local tier has *verifiably* failed.

---

## 2. The two decisions only you can make

These block Stage 1 of any workflow. They are not code questions.

### 2.1 Merge direction for the divergent git state — **RESOLVED 2026-09-26**

> **Settled in favour of option (a).** `origin/main` advanced independently to `85c709c`, carrying the canonical P1-1…P1-5 card commits plus `z3-solver`, a portable three-path `tests/conftest.py` vendor resolution, and a broadened `test_rigor_guard.py`. Branch `feat/env-profile-ltm-rag-v12.5` merged `origin/main` and then `origin/antigravity-localLinuxenv` (PR #4). All 12 conflicts were card work and were resolved to main's canonical reviewed versions; the runaway process's unreviewed duplicates are discarded, and this session's own work had zero conflicts. **Effect on the gates:** `test_rigor_guard.py` now exits **0** (124 files), `pytest tests/` now **collects 1145 tests, exit 0** (z3 declared *and* installed), and `antigravity_guard.py`'s import/syntax stage passes — it now fails only on 2,306 pre-existing repo-wide Ruff findings, which is card P6-10 below, not a blocker.

### 2.1b The original decision, retained for the record

Local `main` is 4 commits ahead of `origin/main` with duplicate implementations of P1-1/P1-2/P1-3/P1-10 produced by the runaway process, while `night/remediation-2026-09-25` holds 14 reviewed card commits that `origin/main` does not contain.

| Option | Consequence |
|---|---|
| **(a) Discard local duplicates, merge `night/` properly** *(recommended)* | `night/`'s versions are the ones the v12.4.0 CHANGELOG already describes and the ones this session's forks reviewed in detail. The duplicates were produced unsupervised, mid-audit, unreviewed. |
| (b) Keep local duplicates, drop `night/` | Discards 14 reviewed commits including P1-5's `_verify_trained_adapter` and P1-6's quarantine, both of which `main` currently lacks. |
| (c) Diff both, hand-merge | Highest fidelity, highest effort. Justified only if (a)'s discard turns out to lose something. |

### 2.2 May paid-tier outputs be used as **training targets**? — legal/policy, not technical

This is the load-bearing question for the whole learning design, and `docs/ROADMAP_V1_V2_COMPANION.md` §4.5 already flagged it as unsettled: *"Anthropic's terms restrict using Claude outputs to train competing models… A private companion is a grey area, not a clear yes. The defensible design trains on your own artefacts and verifier outcomes."*

| Mode | Escalation tier is… | Learning signal comes from | Status |
|---|---|---|---|
| **ROUTER** *(recommended default)* | a cost-optimiser — pick the cheapest tier that solves it, log the cost | the local model's **own** best-of-N samples that the verifier labels correct, plus this repo's own diffs and test outcomes | Unambiguously safe. Also **scientifically cleaner**: improvement is genuinely the system's own, not compression of a frontier model. |
| TEACHER | a teacher — its solutions become SFT/DPO targets | distillation from paid-tier outputs | Requires your own determination that your terms permit it. Do not enable by default. |

The plan is written for **ROUTER**. Episodes harvested from escalations are stored with `trainable=false`; only locally-generated verified samples train. Switching to TEACHER is a one-flag change but must be a recorded decision, not a drift.

`anse/memory/transcript_ltm.py` (added today) already enforces the safe reading: every imported Claude Code turn is stored `trainable=False, usage="retrieval_only"`, and transcripts are used for **retrieval and episode segmentation**, never as SFT targets.

---

## 3. The execution model: local-first verified cascade

```
                    ┌─ verifier: cargo test / pytest / lean #print axioms ─┐
                    │                                                      │
problem ──▶ T4 local single-shot ──▶ T4 best-of-N (N=4, temp sweep) ──▶ ESCALATE
             ~35 tok/s, ~$0            still ~$0                        haiku → sonnet → opus
                    │                        │                               │
                    └─ solved_local ─────────┴──── solved_after_escalation ───┴──▶ unsolved
                                                                                  (a legitimate outcome)
```

**The KPIs, and why they cannot be faked:**

| KPI | Definition | Why it resists fabrication |
|---|---|---|
| **Escalation rate** | `(attempted − solved_local) / (attempted − harness_error)` | A count of verifier exit codes. `cargo test` either exits 0 or it does not. |
| **Cost per solve** | `usd_spent / verified_solves` | Attested by the API bill. You cannot edit a formula to change it. |
| **Regression count** | EVAL problems solved before that now fail | Makes "improvement" falsifiable — the property every prior metric here lacked. |
| **Episode yield** | verified episodes that survive the JEPA reader | Distinguishes "written to disk" from "actually trainable". |

Escalation rate falls only if the local model genuinely solves more. The **cost curve is the learning curve**, and cost is externally attested.

**Leakage control is mandatory, not optional.** Escalation rate is only meaningful against a **frozen EVAL set** that is never trained on and never drives escalation policy. The bank must split into TRAIN (harvested from) and EVAL (frozen, hash-recorded, re-run identically each night) with a card whose accept command asserts **zero hash overlap**. This repo has already had two leakage incidents: the 49/120 duplicate rows behind the bogus Phase-2 `r=0.40`, and `anse/jepa/dataset.py:389` silently falling back to an item-level split when distinct tasks are too few. Note `data/interactions.jsonl` today holds **3 rows, all `task="test task"`, `hidden_state_dim=16`** — one distinct task, so a JEPA run on it right now would recreate the original leakage silently.

---

## 4. Hardware budget: T4 duty cycle and cost

**Measured envelope (this host):** Tesla T4, sm_75 (Turing), **14,912 MiB usable**, driver 580.178.04, 70 W limit, 8 vCPU / 29 GiB RAM, disk2 492 GB with ~197 GB free, 27 GB of Ollama weights.

| Property | Value | Source |
|---|---|---|
| Warm inference, `qwen2.5-coder:7b-instruct` | **34–35 tok/s** | measured ×3, plus Ollama's own `print_timing: 34.23 t/s` |
| Cold model load | **~197–297 s** | measured — hence `OLLAMA_KEEP_ALIVE=10m` |
| Resident VRAM, that model | 4,653 MiB | `nvidia-smi` |
| Prover at Q8_0 | ~9.5 GB — fits, ~5 GB spare | fork analysis; **re-pull at Q4_K_M (~4.5 GB)** to allow prover + embedder co-residency |
| Training dtype | **fp16, never bf16** | sm_75 has fp16 tensor cores but no bf16 ones. `torch.cuda.is_bf16_supported()` returns `True` here anyway and must not be trusted. FlashAttention-2 needs sm_80+; use SDPA/xformers. |

### 4.1 Measured QLoRA capacity — and three facts that change the training plan

All measured on this T4 with the GPU exclusive (NF4 + double quant, gradient checkpointing, PagedAdamW8bit, r=16 on q/k/v/o, batch 1):

| dtype | TFLOPS (4096² matmul) | |
|---|---|---|
| **fp16** | **20.82** | ← use this |
| fp32 | 3.87 | |
| tf32 | 3.88 | tf32 is a no-op on sm_75 |
| **bf16** | **2.28** | **9.1× slower than fp16** |

**bf16 is a trap on this card.** `torch.cuda.is_bf16_supported()` returns `True` and is misleading — Turing has no bf16 tensor cores, so it is emulated and lands *below fp32*. Any trainer configured `bf16=True` runs ~9× slow. Mandate `bnb_4bit_compute_dtype=torch.float16`, `fp16=True`. Attention: FLASH is **unavailable** (needs sm_80+); MEM_EFFICIENT and MATH are available, so use `attn_implementation="sdpa"`, never `flash_attention_2`.

| Base | seq | peak MiB | train tok/s |
|---|---|---|---|
| **Phi-3-mini 3.8B** | **1024** | **9,601** | **373** ← ceiling with real headroom |
| Phi-3-mini 3.8B | 2048 | OOM | — |
| Qwen2.5-0.5B | 2048 | 10,419 | 640 |
| 7B *(estimated)* | 512 | ~9,200 | fits |
| 7B *(estimated)* | 1024 | ~13,900 | **<1 GB headroom — unreliable** |
| 14B *(estimated)* | any | ~14,000–21,000 | **off the table** |

**Three facts that reshape "train a large model at night":**

1. **The Ollama store is GGUF — not trainable.** Only two complete HF bases exist on disk: **Phi-3-mini-4k-instruct (3.8B)** and Qwen2.5-0.5B, plus a real 2.9 GB qwen2.5-1.5b on disk 2. The Qwen2.5-1.5B / Mistral-7B / Ministral-3B entries in the HF cache are **12–28 KB metadata stubs, never downloaded**; the Qwen3.8-27B entries are GGUF, inference only. So the largest model trainable tonight is **3.8B**, not 7B or larger. 7B needs a ~15 GB download (174 GB free, feasible) and would then only train at seq ≤ 512.
2. **`post_implement_training.py:189`'s ~11,000 MiB budget for "7B"** is roughly right at seq ≤ 512 but **under-budgets seq 1024** (would OOM) — and is moot until a 7B HF base is actually present.
3. **Never size training against a shared GPU.** An earlier probe showed Phi-3/1024 OOM; that was *contention* (Ollama had grown to 4,646 MiB), not a capacity limit. Re-measured exclusive, it fits with 5.3 GB headroom.

**Nightly throughput:** 373 tok/s → 8 h ≈ 10.7 M tokens ≈ **~10,500 samples/night** at seq 1024; 6 h ≈ 7,900.

### 4.2 This is a SPOT instance — checkpoint or lose the night

Instance metadata: `provisioningModel=SPOT`, `preemptible=TRUE`, `automatic-restart=FALSE`, `on-host-maintenance=TERMINATE`. Measured boot history: 3 min, 7 min, 11.9 h, 18.3 h, 22.4 h, 23 h, 86 h — **median ~20 h, with two sub-10-minute boots.** A 10k-sample epoch takes ~8 h, comparable to the short tail.

**`train_checkpoint.py:141` sets `save_strategy="no"`, so a preempted night loses everything.** Required: checkpoint every ~250 steps with resume, and poll `metadata/instance/preempted` (currently `FALSE`; flips ~30 s before termination) to flush. `scripts/train_qwen_lora.py:61` already has `save_steps=50` and is the better template.

### 4.3 Honest cost model — do not build the case on inference arbitrage

Costs are **estimated list prices** (no billing API access). Spot compute ≈ $0.12–0.23/hr (midpoint $0.19); disks ≈ $35/mo billed even when stopped. **24/7 ≈ $174/mo; 8 h-nights-only ≈ $81/mo.**

Marginal cost per 1M output tokens = `$/hr ÷ (tok_s · 3600 / 1e6)`:

| Regime | $/1M output | vs API |
|---|---|---|
| 3.6 tok/s (the CPU state it was actually in) | **$14.66** | worse than Sonnet, worse than Haiku |
| 34 tok/s (GPU, after the fix) | **$1.55** | 3.2× cheaper than Haiku |

The restart moved local inference from *economically indefensible* to *3× cheaper than the cheapest tier* — it is the precondition for the whole local-first thesis.

**But the honest caveat:** Batch API is 50% off, so **Batch Haiku is ~$2.50/1M output**. Local T4 at $1.55 is only **1.6× cheaper while being a far weaker model.** At ~30% duty cycle the T4 yields ~27 M output tok/mo, displacing ~$68/mo of Batch Haiku against a $174/mo bill — **the T4 does not pay for itself on inference substitution.** It is justified by what has no API equivalent at any price: **QLoRA training, embeddings, and bulk best-of-N sampling under a verifier.** Build the economic case on those, not on token arbitrage.

### 4.4 A VRAM thief to pause

`datalake-harvest-daemon.service` (PID 1266, `--interval 1800`, running under `~/venv` py3.10 rather than the repo `.venv`) periodically re-touches the embedding model and refreshes its keep-alive. It will **silently steal VRAM mid-night.** It must be paused for every training window. Observed live in this session: running the validator (code model) concurrently with the PDF ingest (embedding model) under `OLLAMA_MAX_LOADED_MODELS=1` caused ~200 s cold-load thrashing on every alternation — direct evidence that the day/night mutex must be a hard interlock, not a convention.

**Duty cycle** — enforced by systemd timers plus a VRAM mutex so inference and training never contend:

- **Day (~16 h): inference.** Cascade runs problem batches. `OLLAMA_MAX_LOADED_MODELS=1`, `OLLAMA_KEEP_ALIVE=10m` (both **set today** via `/etc/systemd/system/ollama.service.d/10-t4-residency.conf`). Marginal cost ≈ electricity: at 70 W peak, ~1.1 kWh/day.
- **Night (~8 h): training.** `ollama stop` all models, then QLoRA at the largest base that fits. The gate in `anse-nightly-distill` refuses to start unless the card is actually free.

**Cost comparison.** Local inference is effectively free once the box is provisioned; the real question is whether to keep the VM up. GCP `n1-standard-8` + T4 is roughly **$0.35–0.40/hr on-demand (~$250–290/mo)**, or **~$0.11–0.15/hr preemptible**. Against API pricing per 1M output tokens (Haiku ≈ $5, Sonnet ≈ $15, Opus ≈ $75), at 35 tok/s a T4 produces ~1M output tokens per ~8 h of continuous generation — so **continuous local generation beats even Haiku on token cost**, and the break-even against the VM's own cost is reached at a few million tokens/month. The T4's weakness is latency and peak quality, not price. **Recommendation:** keep the VM up while the nightly loop is active; schedule it down if the loop is paused for more than a few days. GCS Cloud Run's `deepseek-prover-v2` has no `minScale`, so it scales to zero and costs ≈$0 idle — a usable L4 burst tier for goals the T4 cannot hold.

---

## 5. The capability ladder

Rungs are gated: **do not advance while the rung below is near zero.** Skipping that ordering is how this project arrived at PhD-level claims with no working baseline.

### L0 — simple Rust + Python solver problems
- **Verifiers (both real today):** `rustc -O` compile+run (`compile_and_run_rust`, ~`:1798`) and `anse/symbolic/sandbox.py` Tier-1 subprocess with resource limits.
- **Rust first**, deliberately: the compiler is the strictest verifier available and rejects error classes a Python test silently passes.
- **Goal:** a real local solve rate on ≥100 problems per language, plus the initial verified-episode corpus.
- **Promotion gate:** local solve rate established and non-trivial; zero EVAL/TRAIN overlap; episode yield through the JEPA reader > 80%.

### L1 — Master level
- Harder algorithmic and mathematical problems with **independent** verification.
- **Blocker to fix first:** math and physics have **no independent verifier** — the cases self-assert via SymPy against their own constant. `invariant_registry.yaml` (993 lines of per-case `invariant_type`/`tolerance`/`units`) is the raw material for a genuine dimensional + conservation check, and is the single most reusable asset in the bank.
- **Goal:** escalation rate falling on the frozen EVAL set across nights; cost per solve trending down.

### L2 — PhD level
- Lean theorem proving against the axiom-checked gate, using the **local** provers (DeepSeek-Prover-V2-7B, Goedel-Prover-V2-8B) so proof search costs nothing.
- **Mathlib is not a blocker:** `formal/.lake` (symlinked to disk 2) holds **1,862 `.olean` ≈ 17.6% of Mathlib**, and `lake exe cache get` fetches prebuilt oleans rather than compiling. Non-Mathlib goals compile *today* — verified: `theorem t (n : Nat) : n + 0 = n := Nat.add_zero n` passes clean.
- **Start with best-of-N, not MCTS.** `lean_mcts_prover.py` has real UCB1 but a hardcoded 12-tactic generator, and MCTS over a ~20 s/verify compiler is expensive with unproven value. Establish single-shot and best-of-N rates first.
- **Real targets exist:** the 4 open `sorry`s (`Theorems.lean:61`, `Basic.lean:160`, `System2.lean:170,185`) are genuine proof obligations tracked in `Blueprint.lean:155-183`. Expect to fail most; failure is a real result.
- **Never** weaken a goal to make it provable. `anse/v5/autonomous_curriculum.py:61-64` already contains `theorem kdv_momentum_conservation ... : ∀ (t : ℝ), True := by intro t; trivial` — a vacuous statement presented as a PhD-level verified result.

---

## 6. The terminating condition, made measurable

You asked to stop when a PhD-level paper passes peer review autonomously. Today that is unmeasurable, because the reviewer is a constant function (§0). Here is the honest operational version.

**A paper is CANDIDATE-COMPLETE when all six machine-checkable criteria hold:**

1. Every quantitative claim resolves to `{file, key, sha256}` and an independent verifier **re-derives** the number.
2. No claim cites a nonexistent file. *(Today: the MIT-licence badge links to a `LICENSE` that does not exist.)*
3. Every cited theorem compiles with **no `sorryAx` and no unexpected axiom**, and no cited theorem is vacuous.
4. Results reproduce from a clean checkout at a pinned commit. *(Today: 10 files in `results/` embed `/home/xavkal/` paths from another machine.)*
5. No adversarial reviewer — each given a distinct lens (provenance, formal, statistics, reproducibility) and instructed to reject — finds an unsupported claim. The reviewer must first be **falsified on a negative control**: fed a knowingly-broken paper, it must reject. An unfalsified gate is not a gate.
6. Novelty: a real literature search (the alphaXiv tools are available) finds no prior work stating the same result.

**And then a human or a venue accepts it.** I want to be direct about this rather than bury it: **a system cannot autonomously certify its own PhD-worthiness.** Self-certification is structurally the same defect as the 14 already found — it is exactly what `review_paper_gemini_pro.py` does. The system can autonomously *produce* a paper that passes 1–6; acceptance is external. Criteria 1–6 are what `anse-claims-provenance` checks, and I'd propose treating "candidate-complete + your sign-off" as the real finish line. Override this if you want, but it should be a deliberate choice.

**Interim stop conditions** — because a loop whose terminal condition cannot be self-evaluated otherwise never halts:

- Budget exhausted (external supervisor kills).
- **N=5 consecutive nights** with no escalation-rate improvement on the frozen EVAL set.
- Regression count above zero on two consecutive nights.
- Episode yield through the JEPA reader below 50% (means the data plane, not the model, is the problem).

---

## 7. The five workflows

All authored in `.claude/workflows/`, invocable by name. Each agent stage is told to report only real command output; each returns structured data so the next stage cannot invent it.

| Workflow | Purpose | Key property |
|---|---|---|
| **`anse-honest-baseline`** | Restructure the 200 cases into real `(statement, hidden reference, tolerance)` problems; measure the first honest local pass rate; declare the frozen EVAL set with a sha256 | Milestone 1. Counts `harness_error` separately from model failure, and refuses to score math/physics until they have an independent verifier |
| **`anse-lean-proof-gate`** | Build **one** axiom-checked gate; **falsify it on negative controls**; then local best-of-N proving | Halts if the gate ever accepts a `sorry` proof. Keeps `repl_pain_loop`'s repair loop, replaces only its acceptance test |
| **`anse-ladder-cascade`** | The cascade at a chosen rung (`args: {level, limit}`); harvest verified episodes | Preflight **halts** on nonzero EVAL/TRAIN overlap or an unrecorded ToS decision. Proves harvested episodes survive the JEPA reader |
| **`anse-nightly-distill`** | Night QLoRA on the T4 with an eval that can reject | Reports the naive first-vs-last metric *and* the honest trend, every night, as a standing reminder. Requires real forward passes on held-out data |
| **`anse-claims-provenance`** | Trace every claim to an artifact; adversarial review with 4 distinct lenses | Reviewer must reject a knowingly-broken paper before its ACCEPT counts. Retracts the two review artifacts falsely attributed to `gemini-3.1-pro` |

**Cost discipline built into the design:** the workflows' Claude agents *build and verify harnesses*; they never solve problems themselves. All candidate generation is local T4 inference invoked by scripts those agents write. Paid tokens buy engineering, not answers.

---

## 8. Sequencing

**Precondition (blocks everything):** resolve §2.1. `scripts/night_phase_runner.py` refuses to start on a dirty tree, so any workflow stage that commits will either abort or compound the divergence. The merge decision is yours; the workflows should not make it.

```
Stage 0  DECIDE           §2.1 merge direction, §2.2 ToS mode           (human)
Stage 1  CONTAIN          P0-10 ledger reconcile, P0-11 z3/collection,
                          P1-11 merge night/, P1-12 harden P1-6 accept
Stage 2  BASELINE         anse-honest-baseline  ← the first honest number
Stage 3  GATES            anse-lean-proof-gate  (parallel with Stage 2)
Stage 4  LADDER L0        anse-ladder-cascade {level:"L0"}
Stage 5  NIGHTLY          anse-nightly-distill  (recurring, 8 h/night)
Stage 6  L1 → L2          advance only on Stage 4/5 promotion gates
Stage 7  TERMINAL         anse-claims-provenance → candidate-complete → your sign-off
```

Stages 2 and 3 are independent and should run concurrently. Stage 7's claims-tracing half can run at any time and is worth running early — it is what replaces the README's fabricated badges.

---

## 9. Cards to add or redefine

Extending `docs/remediation/tasks.yaml` (51 cards: P0×9, P1×10, P2×6, P3×5, P4×8, P5×7, P6×6; low 19 / mid 19 / human 13).

| Card | Tier | Title | Accept criterion |
|---|---|---|---|
| **P0-10** | low | Ledger/git reconciliation pre-check | Exits nonzero if `status.json` disagrees with `git log --all --grep='^P[0-6]-'`; wired into the runner |
| **P0-11** | low | Declare `z3-solver`; make the v4 SMT import lazy | `pytest tests/ --collect-only` exits 0 with no `--ignore` |
| **P0-12** | low | Persist the Ollama GPU/residency fix | Validator asserts `ollama ps` shows `100% GPU` and warm tok/s > 10 |
| **P1-11** | mid | Merge `night/` per the §2.1 decision | `git log main \| grep -c 'P1-'` == 10, no duplicate SHAs per card id |
| **P1-12** | low | Harden P1-6's accept commands | Requires zero `adapter_config.json` under `adapters/**` carrying any `mode` key |
| **P1-13** | low | Salvage the abandoned P1-4 work | `tests/remediation/test_latent_dreamer_honesty.py` passes (verified: **3 passed**) |
| **P2-7** | mid | Frozen EVAL/TRAIN split | Asserts **zero** hash overlap; EVAL id list sha256 recorded |
| **P3-5** | low | One Chroma root | `anse/config.py` owns `chroma_root`; no other module hardcodes a Chroma path |
| **P3-6** | low | Replace md5 pseudo-embeddings where called RAG | `grep -rn FastDeterministicEmbeddingFunction anse/` returns 0 outside a clearly-named cache utility |
| **P4-2** *(redefine)* | mid | Verified-data gate as a **type**, not a filter | Constructing a trace without `tests_total` raises `TypeError`; zero `metadata.get(...)` silent-skip paths remain in the JEPA reader |
| **P4-4** *(redefine, demote from human)* | mid | First real training run, with an accept command | `journal.last_ok == GATE` **and** eval uses mean-of-halves or OLS slope on held-out data, not first-vs-last |
| **P4-9** | mid | Energy surrogate: implement or delete | Either a real `roc_auc_score` eval with `sklearn` declared, or the stage and its AUROC prose are removed |
| **P4-10** | low | External budget supervisor | Kills a run that exceeds the ceiling; proven by a test that exceeds it |
| **P5-6** | low | Generated claims | `CLAIMS.md` where each badge number is emitted by a script that re-derives it from a named artifact |
| **P5-7** | mid | Honest reviewer + retract false attributions | Reviewer rejects a knowingly-broken paper; the two `gemini-3.1-pro` artifacts and the Redis key are retracted |
| **P5-8** | low | Lean gate consolidation | All `lake env lean` call sites route through the axiom-checked gate; controls test in CI |
| **P6-7** | mid | `scripts/verify_release.py <base> <branch>` | Exits nonzero if a release note names a card whose files are not in the diff; required before any `git tag v*` |
| **P6-8** | low | Delete 755 LOC of confirmed dead code | Each module's `grep -rl` returns 0 hits outside git history; suite still passes |
| **P6-9** | low | Add the missing `LICENSE` | File exists and matches the badge |

---

## 10. What was implemented today (not proposed — landed)

To be explicit about the line between plan and action, since the last release blurred it:

| Change | Status |
|---|---|
| Ollama GPU placement + residency policy (`OLLAMA_MAX_LOADED_MODELS=1`, `KEEP_ALIVE=10m`, `NUM_PARALLEL=1`) | **Done** — 2.3 → 35 tok/s, service enabled |
| `anse/memory/ollama_embeddings.py` — real 1024-d semantic embeddings, fail-closed | **Done**, tested |
| `anse/memory/document_store.py` — PDF ingestion with `{source_path, source_sha256, page}` provenance | **Done**, tested |
| `anse/memory/transcript_ltm.py` — Claude Code transcripts → Redis + Chroma, scrub-gated, `trainable=False` | **Done**, tested |
| `scripts/validate_environment.py` — end-to-end validator that reports true exit codes | **Done** |
| The five workflows | **Authored, none run** |
| Redis installed, running, enabled | **Done** |
| Merge/release of the above | **Blocked on §2.1** — deliberately not merged |
