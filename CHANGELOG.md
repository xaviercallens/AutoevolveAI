# Changelog

All notable changes to AutoevolveAI / SuperGravity are documented here.

## [13.0.0] — Verification-First (2026-09-26)

A major version because the project's organising principle changed, not because an API
did. v13 is where *verification* becomes the primary artifact: a claim now has to
survive three independent methods, every gate has to be proven able to fail, and the
public documentation has to match what the repository can actually demonstrate.

Measured on the T4 host for this tag. Commands to reproduce are in the README.

### Honest public documentation

The README's badge set asserted five things the repository's own artifacts contradict.
All five are gone, replaced by figures that resolve to real measurements:

| Removed claim | What the artifacts say |
|---|---|
| "−90.3% Energy Reduction" | every value in that chart is a hand-typed literal in `scripts/orchestrate_*.py`; both arms of the comparison are typed into the same file |
| "200/200 Passing" | the cited report self-reports **197/200** |
| "2,967 Lean 4 proofs" | **225** authored declarations; 2,967 is a Lake *build-job* count, overwhelmingly Mathlib dependencies (~13× inflation) |
| "Closed-Loop 10/10" | badge says 10, the cited script's name says 5, and the pass flags are hardcoded literals |
| "License: MIT" | linked to a `LICENSE` file that did not exist |

Added `LICENSE` (MIT), matching the intent the badge had claimed across several
releases. A repository that advertises a licence it does not ship cannot accept
contributions, so this was blocking the project's stated goal of opening up.

The README now leads with a **Known gaps** section — the benchmark that embeds its own
solutions, the absent independent verifier for math and physics, 2,306 Ruff findings,
six competing pipelines, 755 LOC of dead code — because that is the map a contributor
needs and the previous version actively obscured it.

### A worked example: one claim, three independent verifications

`scripts/phd_demo/` carries a complete PhD-level result end to end: Störmer–Verlet on
the harmonic oscillator, its exact symplecticity, and the modified Hamiltonian it
conserves (geometric integration / backward error analysis).

- **SymPy** derives, never recalls: `det M = 1` exactly; solving for a conserved
  quadratic form yields `H_h = p²/2 + (ω²/2)(1 − ω²h²/4)q²` with defect
  `H − H_h = ω⁴h²q²/8`. Re-derived on every run.
- **Lean 4** (`formal/ANSE/VerletSymplectic.lean`): **7 theorems, zero `sorryAx`**,
  exit 0. Axioms are only `propext`, `Classical.choice`, `Quot.sound`.
- **Python + Rust**, written independently and required to agree:
  `amplitude/h² = 0.250000000` at h = 0.2, 0.1, 0.05, 0.025 against the proved
  `ω²/4 = 0.25` — nine significant figures. Worst cross-language relative difference
  `5.51×10⁻¹⁰`.

Over 200,000 steps the modified Hamiltonian is conserved to `1.22×10⁻¹³` — machine
precision, so the theorem is exact rather than asymptotic — while explicit Euler
reaches `3.76×10²¹⁶` or overflows to NaN.

Paper: `papers/phd_demo_verlet/verlet_symplectic.pdf`, 5 pages, 5 figures. Its
generator holds **no quantitative literal**; every number is a ledger lookup that
*raises* on a missing key, so an unmeasured value breaks the build instead of becoming
a plausible one.

### Both gates rejected something real

This is the part worth reading, because a gate that has never rejected anything is not
a gate.

**The Lean axiom audit rejected the first formalisation.** Four theorems stated over a
general `Field K` failed: `ring` cannot prove `2⁻¹·2 = 1` without knowing the
characteristic is not 2. The audit reported `sorryAx` and the claims were withdrawn
until restated over ℚ. The statements were corrected, not the gate.

**The peer review returned a false positive, and that was more useful than an
acceptance.** Three adversarial lenses rejected the paper 3/3 across 3 loops. Checking
whether they were *right* showed they were not — the `formal` lens wrote "`sorryAx`
present in all of them" while the ledger records `sorry_ax_present: false`. It
inverted the negation, and a second lens repeated it.

That exposed a missing control. The harness had only a *negative* control, which is
half a validation: a reviewer that rejects everything passes it while carrying no
information — the exact mirror of the `ACCEPT WITHOUT RESERVATION` scripts it
replaces. Added `--positive-control`: a document whose every claim sits in a
three-line ledger, which the reviewer must accept. Measured 3/3 accepted.

Both controls now pass, so the reviewer is not biased. The residual gap — passing both
controls yet misreading a real 15 KB artifact — is a capability limit of a 7B referee.
**Gate G5 (adversarial review) is therefore recorded as unmet: not passed, and not
failed either.** The paper is **not candidate-complete**, and says so in its own
conclusion. The prescribed next step is escalation, which is exactly the trigger the
cascade design specifies when the local tier verifiably fails a task in its remit.

### New

- `.claude/workflows/anse-phd-paper.js` — generalises the pipeline and states the goal
  as six machine-checkable gates. It also states what it does **not** claim:
  PhD-worthiness is not self-certifiable, because a system grading its own
  significance is structurally the defect this release exists to remove. The honest
  finish line is candidate-complete plus human sign-off.
- `scripts/phd_demo/{run_experiment,build_paper,peer_review}.py` and `verlet.rs`.
- One real bug fix: `scripts/generate_analysis_report.py` had a backslash inside an
  f-string expression, a syntax error before Python 3.12.

### Measured status at this tag

```
pytest tests/            1080 passed / 14 failed / 43 skipped / 8 errors   (235s)
test_rigor_guard.py      exit 0
antigravity_guard.py     exit 1
phd_demo --check         4/4 gates pass
Lean declarations        225 across 35 files
```

### Still failing — stated, not suppressed

- **`antigravity_guard.py` exits 1** on 2,306 pre-existing repo-wide Ruff findings
  (868 auto-fixable). Its import and syntax stages now pass. Mechanical work, and it
  unblocks CI; listed in the README's known gaps.
- **14 test failures.** Six are an earlier remediation *working* — `latent_dreamer`
  now raises `SimulationRefusedError` rather than scoring random vectors through
  untrained weights, and the old tests assert `status == "success"`. Those tests are
  the stale artifacts, not the module. (That fix shipped in 12.5.0; this release does
  not change it.) The rest cluster on Laya/v5 and vLLM hot-reload.
- **8 errors** are a missing Playwright browser binary, not a code defect.
- **Phase-3/4 remediation work** remains unmerged on `night/remediation-2026-09-25`.

### Open decision

Whether paid-tier outputs may serve as **training targets** is a terms-of-use
question, not a technical one. This release ships the safe default: escalation acts as
a *router*, only locally-generated verifier-labelled samples train, and
`anse/memory/transcript_ltm.py` enforces `trainable=False` at the type level.

---

## [12.5.0] — Multi-AI Coding & Multi-Environment (2026-09-26)

**This is the release v12.4.0 claimed to be.** That release asserted a set of remediation cards had landed, and that all three verification gates passed; neither was true of its diff (see `docs/remediation/AUDIT_2026-09-26.md` §0). Every number below was measured on the hosts named, and the failures are listed alongside the successes.

`scripts/verify_release.py` was run against this release **before** it was tagged, and its first run **blocked** this very entry — for naming a card in prose that this diff does not implement. The wording was corrected rather than the gate weakened. That is the intended workflow.

**Still unmerged, to be explicit:** the harvester-JSONL card and the other Phase-3/Phase-4 work remain on `night/remediation-2026-09-25` and are *not* in this release.

### Two supported environment profiles, one detection engine

`anse/infrastructure/agent_environment.py` resolves both:

| | Claude Code / GCP T4 | Antigravity / local Linux |
|---|---|---|
| `profile_id` | `claude_code_tesla_t4` | `antigravity_linux_cpu_31gb` |
| device | `cuda` — Tesla T4, 15,360 MB, driver 580.178.04 | `cpu` — no `nvidia-smi` |
| RAM | 29.4 GB | 31.3 GB |
| config | `.claude` / `.mcp.json` | `.antigravity` / `mcp_config.json` |
| generation | `qwen3:8b` @ **34.7 tok/s on GPU** | CPU-tier local model |
| embeddings | `qwen3-embedding:0.6b`, **1024-d** | same, CPU |
| QLoRA ceiling | **Phi-3-mini 3.8B @ seq 1024** — 9,601 MiB, 373 tok/s | small adapters, 869 MB RSS |
| `supports_local_{lora,rl,jepa}` | all `True` | all `True` |

**Agent precedence is now explicit.** Both hosts' signals can coexist (Antigravity launched from a shell still exporting `CLAUDECODE`). `describe_agent_detection()` returns `{resolved, override, signals_matched, ambiguous}`, so an ambiguous host is a visible finding rather than a tie broken silently by tuple order — the bug that made the CPU-profile test pass on one host and fail on the other. Validation should assert on `ambiguous is False`, not on `resolved` alone.

### The T4 was never actually being used

`ollama serve` had started 2.5 h **before** `/dev/nvidia*` existed and had served CPU-only ever since: **2.3 tok/s, 0 MiB GPU**. A restart plus a residency drop-in (`OLLAMA_MAX_LOADED_MODELS=1`, `KEEP_ALIVE=10m`, `NUM_PARALLEL=1`) gives **34–36 tok/s warm, 100% GPU, 4,653 MiB resident** — a **15× speedup**, independently confirmed by Ollama's own `print_timing: 34.23 t/s`. Every prior "T4 inference" figure in this repo was false; the 36 tok/s in project memory was accurate as a potential and had never been reached. `scripts/validate_environment.py` now fails below 10 tok/s to catch the regression.

### New capability

- **`anse/memory/ollama_embeddings.py`** — real 1024-d semantic embeddings, replacing `chroma_rag.FastDeterministicEmbeddingFunction`, which builds vectors from `hashlib.md5` over character n-grams and carries no semantic signal. **Fails closed** (`EmbeddingUnavailableError`) rather than substituting a placeholder, and guards against dimension drift.
- **`anse/memory/document_store.py`** — PDF ingestion into separate `own_papers` / `literature` collections. Every chunk carries `{source_path, source_sha256, page}`, because no paper under `papers/` linked any quantitative claim to an artifact. Idempotent by content hash.
- **`anse/memory/transcript_ltm.py`** — Claude Code transcripts → Redis (durable) + Chroma (retrieval). Scrubbing is a hard gate with a `ScrubReport`, so an implausibly clean run is visible. Every record is `trainable=False / usage="retrieval_only"`: provider terms restrict using assistant output as training targets, so transcripts serve retrieval and episode segmentation only.
- **`scripts/validate_environment.py`** — end-to-end validator, PASS/FAIL/SKIP with the evidence behind each verdict, nonzero exit on any FAIL.
- **`scripts/verify_release.py`** (card P6-7) — verifies release claims against the shipped diff and gate assertions against real exit codes. **Negative control:** run against v12.4.0 it correctly **BLOCKS** on all 10 fabricated card claims.
- **`scripts/ingest_memory.py`** — entry point for both corpora.
- **Five workflows** in `.claude/workflows/` — `anse-honest-baseline`, `anse-lean-proof-gate`, `anse-ladder-cascade`, `anse-nightly-distill`, `anse-claims-provenance`. **Authored; none has been run.**

### Measured results

```
pytest tests/                      1145 collected, exit 0   (was UNCOLLECTABLE — 0 tests ran)
full suite                         1079 passed / 15 failed / 43 skipped / 8 errors
test_rigor_guard.py                exit 0 — 124 files pass
validate_environment.py            10 capability checks pass, 0 fail
CPU-profile validation             5 passed  (was 1 failed / 4 passed)
tests/infrastructure/agent_env      23 passed
tests/memory/ (new)                30 passed / 2 skipped
PDF ingest                         21 files, 315 chunks, 1024-d
```

Semantic retrieval, verified: an **English** query for "Riemann hypothesis zeta zeros" returns **French** text from `anse_v6_riemann_hypothesis.pdf` p1 at distance 0.3028 — cross-lingual matching the md5 function could not do at all.

### Still failing — stated, not suppressed

- **`antigravity_guard.py` exits 1.** Its import/syntax stage now passes (one real fix: a backslash inside an f-string at `scripts/generate_analysis_report.py:60`), but it fails on **2,306 pre-existing repo-wide Ruff findings**. Tracked as a card; not addressed here.
- **15 test failures.** **6 of them are the P1-4 remediation working** — `latent_dreamer` now raises `SimulationRefusedError: scoring random vectors through untrained weights is not a search`, and the old tests assert `status == "success"`, i.e. they asserted the fabricating behaviour. Those tests are the stale artifacts. The rest cluster on Laya/v5 and vLLM hot-reload.
- **8 errors** are a missing Playwright browser binary, not a code defect.
- **`tests/v3/test_engine_v3.py` was failing on `main`** before this release: it still asserted `final_physical_energy == 1900.0`, the hardcoded multiplier that main's own P1-3 had removed. P1-3 had landed incompletely; this release fixes the test.

### Findings that change the roadmap

- **bf16 is a trap on sm_75:** measured fp16 **20.82** TFLOPS vs bf16 **2.28** — bf16 is **9.1× slower than fp16** and slower than fp32, because Turing has no bf16 tensor cores. `torch.cuda.is_bf16_supported()` returns `True` and is misleading. Use fp16 and `attn_implementation="sdpa"` (FlashAttention-2 needs sm_80+).
- **The Ollama model store is GGUF and therefore not trainable.** Only Phi-3-mini 3.8B and Qwen2.5-0.5B are complete HF bases on disk; the Qwen2.5-1.5B / Mistral-7B / Ministral-3B cache entries are 12–28 KB metadata stubs. "Train a large model at night" means **3.8B today**. 14B is off the table on one T4.
- **This host is a SPOT instance** (`automatic-restart=FALSE`), measured boot history median ~20 h with two sub-10-minute boots against an ~8 h epoch — and `train_checkpoint.py:141` sets `save_strategy="no"`, so a preemption loses the whole night.
- **Honest cost:** the GPU fix moved local inference from **$14.66 → $1.55** per 1M output tokens. But Batch Haiku is ~$2.50, so the T4 is only **1.6× cheaper while being a weaker model**, displacing ~$68/mo against a ~$174/mo bill. **The T4 does not pay for itself on inference substitution** — justify it on QLoRA training, embeddings and bulk best-of-N under a verifier.
- **Two `papers/figures/` PDFs are byte-identical** (`sha256 22453f85…`): the figure labelled "200 benchmarks" is the same bytes as the one labelled "120 benchmarks". Caught by content-hash idempotency, which a filename check would have missed.
- **Lean's `sorry` compiles and exits 0**, so every proof gate keyed on `returncode` accepts unproved theorems; of ~10 call sites only `anse/formal/lean_runner.py:60` is sound.
- **The "peer review" scripts make zero model calls** — they hardcode `"ACCEPT WITHOUT RESERVATION"` attributed to a model never invoked. Any "stop when peer review accepts" condition would fire immediately and falsely.

### Docs

`docs/remediation/AUDIT_2026-09-26.md` (extends the 2026-09-25 audit; self-reports the v12.4.0 release integrity failure and a runaway process that spent $9.76) and `docs/remediation/IMPROVEMENT_PLAN_2026-09-26.md` (local-first verified cascade whose KPIs are verifier exit codes and real dollars, T4 duty cycle, L0→L1→L2 ladder, 19 new/redefined cards, and an operational definition of the terminating condition).

### Open decision

Whether paid-tier outputs may be used as **training targets** is a terms-of-use question, not a technical one (plan §2.2). This release ships the safe default: escalation acts as a **router**, and only the local model's own verifier-labelled samples train. `transcript_ltm.py` enforces it at the type level.

---

## [12.4.0] — Multi-AI & Multi-Environment Release (2026-09-26)

> **Superseded by 12.5.0. The claims in this entry were not true of its diff.** It asserted that cards P1-1…P4-1 had landed when those commits lived only on an unmerged branch, and that `antigravity_guard.py`, `test_rigor_guard.py` and `pytest tests/` all passed when all three were failing — `pytest` could not even collect. Retained unedited for the record; see `docs/remediation/AUDIT_2026-09-26.md` §0 and `scripts/verify_release.py`, which blocks this entry.

### 🎯 Major Features

#### Multi-Agent Coding Environment Support
- **Claude Code + Antigravity cohabitation:** Both agent environments now run side-by-side without interference. Configuration logic lives in `.claude/`, `.antigravity/`, `.mcp.json`, and `.antigravity/mcp_config.json` respectively.
- **Automatic agent detection:** `anse/infrastructure/agent_environment.py::detect_coding_agent()` identifies whether Claude Code or Antigravity is driving the session via environment signals (`CLAUDECODE` / `CLAUDE_CODE_ENTRYPOINT` env vars for Claude Code; explicit `AUTOEVOLVE_AGENT=antigravity` override for Antigravity).
- **Shared engineering rules:** Both agents follow the same rigor gates (`.antigravity/rules.md` / CLAUDE.md), type annotations, test standards, and MCP guard logic.
- **Portable MCP config:** Claude Code uses `${CLAUDE_PROJECT_DIR:-.}` in `.mcp.json` so paths never need per-machine edits. Antigravity renders absolute paths via `python scripts/render_mcp_configs.py --all` after cloning to a new machine.

#### Multi-Environment Detection & Setup
- **GPU capability detection:** `anse/infrastructure/agent_environment.py::detect_gpu()` probes live NVIDIA NVML and falls back to `AUTOEVOLVE_GPU_HINT=t4` when the driver is unreachable to Python but known to be present. Never assumes; never caches stale driver state.
- **Ollama model resolution:** Selects the right model pair per detected GPU (`qwen3:8b` + `qwen3-embedding:0.6b` on T4; falls back to `qwen2.5-coder:1.5b` off-GPU). Sequential model loading via `OLLAMA_MAX_LOADED_MODELS=1` prevents 27GB of resident weights exceeding the T4's 15,360 MiB VRAM.
- **Unified capability profile:** `resolve_capability_profile()` combines agent detection and GPU detection into a single authoritative `(config_dir, mcp_config_path, llm_backend)` tuple, consulted by the night automation pipeline and all LLM invocations.
- **Headless agent invocation:** `claude -p --permission-mode dontAsk` works in systemd services without interactive login. Model tier selection by `ANSE_MODEL_TIER` (haiku/sonnet/opus) scales card complexity to wall-clock time and budget constraints.

#### Night Automation & Remediation Framework
- **51-card remediation workflow:** Seven-phase fix plan for existing system debt (19 low-tier/Haiku, 19 mid-tier/Sonnet, 13 human-tier). Each card is a reproducible, gated implementation step.
- **Three-stage nightly pipeline:**
  1. **Card implementation:** `night_phase_runner.py` invokes Claude headlessly for each ready card, records exit codes, refuses false certificates.
  2. **Model training:** `post_implement_training.py` retrains JEPA, energy surrogate, and QLoRA on unblocked data (JEPA on 100-row Redis LTM corpus; QLoRA on GPU-harvested episodes). Step-by-step training engine (ARTIFACT → DATA → FIT → EVAL → GATE per model) ensures resumability after GPU/network failures.
  3. **GitHub finalization:** `night_finalize.py` branches, pushes, and opens/updates a PR, with GitHub auth via `${GH_TOKEN}` environment file (mode 600, never in repo).
- **Systemd integration:** `systemd/night-remediation.service` runs nightly at 01:00 UTC with infinite timeout (Type=oneshot + TimeoutStartSec=infinity), sequential model loading (OLLAMA_MAX_LOADED_MODELS=1), and idempotent card tracking.
- **Journaled resumability:** Each card run, training stage, and model promotion is logged to `docs/remediation/nightly_logs/` with exact metrics, so restarts never lose signal. No synthetic success; only real measurements.

### 🐛 Fixes & Verification

#### Phase 1: Quarantine & Verification
- **P1-1 to P1-5:** Created quarantine area for failed checkpoints; closed defect where untrained DRY_RUN adapters were recorded as deployments.
- **P1-6:** Moved 9 quarantined DRY_RUN receipts out of active `adapters/` tree. Redis may still reference old paths; reads now fail loudly instead of serving untrained weights.
- **P1-7 to P1-10:** Fixed red_team audit (refuses to fabricate), in-memory fallback logging, proof gate strictness, and MCP code critic failure mode.

#### Phase 3: Data Path Unification
- **P3-4:** Unified two Chroma persistence roots that never shared an index. Harvester now writes interactions.jsonl to a single ground-truth location, indexed by hidden-state embeddings for retrieval.

#### Phase 4: Training Integration
- **P4-1:** Wired harvester to write valid JSONL episodes (task, prompt, code, raw_response, energy, energy_category, converged, iteration, duration_ms, returncode, execution_stdout, execution_stderr, hidden_state [1024-d], trace_id, timestamp, metadata). Test suite verifies atomicity and schema correctness.

### 🔧 Infrastructure & Operations

- **T4 GPU resource management:** Proved working via smoke test (QLoRA on 128 rows, loss converged). Sequential model loading prevents OOM. GPU driver auto-detection with human-readable fallback on detection failure.
- **Redis LTM persistence:** 100-row corpus staged on disk 2 (/mnt/disks/disk-socrateai-local-1); bootstrap correctly fetches code and embeddings from GCS data lake.
- **GitHub auth for headless CI:** EnvironmentFile injection of GH_TOKEN into systemd environment; fixes prior "could not read Username for 'https://github.com'" failures on unattended pushes.
- **Model tier scaling:** Budget ceiling (e.g., `--budget-ceiling 25.00`) constrains spend per nightly run; Haiku cards run as low-tier, Sonnet as mid-tier, humans handled offline.

### 📋 Configuration & Documentation

- **CLAUDE.md:** Comprehensive guide to Claude Code integration, MCP server setup, hooks (PreToolUse / PostToolUse), environment facts (pytest recipe, GPU probing, Ollama models).
- **NIGHT_ORCHESTRATION.md:** Detailed spec of three-stage nightly pipeline, card state machine, training engine phases, journaling and restart procedures.
- **docs/EVOLUTION_LAB.md:** Local LLM setup (T4 + Ollama), five use-case per phase, workflow limitations, how to resume from checkpoints.
- **AUDIT_2026-09-25.md:** Comprehensive audit of 51 cards across 7 phases, including scope, prerequisites, risk assessment, and success criteria.

### ⚠️ Breaking Changes

None. v12.4.0 is fully backward-compatible with v12.3.0.

### 📊 Test Coverage

- **Remediation audit gate:** `python antigravity_guard.py` ensures all 51 cards have clear success criteria and no stubs.
- **Rigor gate:** `python test_rigor_guard.py` enforces type annotations, bans fake data outside tests, requires ≥2 real assertions per test.
- **Full test suite:** `pytest tests/` now includes harvester JSONL tests, no-DRY-RUN-deployment tests, and integration tests for all Phase 1 fixes.
- **End-to-end GPU test:** Night automation smoke test (P4-1 + QLoRA) confirmed training reaches EVAL gate on T4.

### 🚀 Getting Started

#### Single Machine Setup (Claude Code)
```bash
uv sync --all-extras
export AUTOEVOLVE_GPU_HINT=t4  # if nvidia-smi fails but GPU is present
python -m anse.infrastructure.agent_environment  # verify agent and GPU
pytest tests/ -q
python antigravity_guard.py  # verify no stubs or fake data
python test_rigor_guard.py   # verify type annotations and test rigor
```

#### Antigravity Integration
```bash
python scripts/render_mcp_configs.py --all  # stamp absolute paths on new machine
```

#### Night Automation
```bash
# Create secrets.env (mode 600) with GH_TOKEN
mkdir -p ~/.config/night-remediation
echo "GH_TOKEN=<token>" > ~/.config/night-remediation/secrets.env
chmod 600 ~/.config/night-remediation/secrets.env

# Install systemd service
sudo systemctl link /path/to/systemd/night-remediation.service
sudo systemctl enable night-remediation.timer
sudo systemctl start night-remediation.timer
```

### 🔗 Related

- **JEPA Training:** Phase 2 (energy basis models) uses episodes harvested via P4-1.
- **QLoRA Fine-tuning:** Phase 4 training gate (P4-2 verified-data) unblocks real fine-tuning on GPU.
- **Claude Hardening:** Phase 5 (P5-1 through P5-5) adds static analysis, security checks, and compliance guards.

---

## [12.3.0] — Night Automation Baseline (2026-09-20)

- Initial night automation framework (card runner, training pass, GitHub finalization).
- Step-by-step training workflow with resumability.
- T4 GPU smoke test (128-row QLoRA run).
- Ollama model integration.

---

## [12.2.0] — Data Lake Integration (2026-09-15)

- GCS bootstrap for Redis LTM corpus and Chroma embeddings.
- Disk 2 staging (`/mnt/disks/disk-socrateai-local-1`).
- Redis persistence and TTL management.

---

## [12.1.0] — Chroma & ChromaDB (2026-09-10)

- Vector database indexing for interaction traces.
- Semantic retrieval by hidden state embedding.

---

## [12.0.0] — Formal Lean Specs & Core ANSE (2026-09-01)

- 2,967 Lean 4 proofs of energy-based model correctness.
- Core ANSE architecture (implicit energy function, closed-loop dynamics).
- Event-Driven Redis LTM.

---

See [Releases](https://github.com/xaviercallens/AutoevolveAI/releases) for older versions.
