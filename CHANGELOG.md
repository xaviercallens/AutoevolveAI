# Changelog

All notable changes to AutoevolveAI / SuperGravity are documented here.

## [12.4.0] — Multi-AI & Multi-Environment Release (2026-09-26)

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
