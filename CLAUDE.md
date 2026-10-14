# AutoevolveAI — Claude Code guide

This repo supports two agent environments side by side:

| | Antigravity | Claude Code |
|---|---|---|
| Config | `.antigravity/` | `.claude/`, `.mcp.json`, this file |
| Rules | `.antigravity/rules.md` | same rules apply (see below) |
| MCP | `.antigravity/mcp_config.json` | `.mcp.json` (same `mcp_guard_server.py`) |
| Guards | `.antigravity/hooks/hardened_gate.py` | `.claude/hooks/*.py` (PreToolUse / PostToolUse) |

Each environment normally leaves the other's config directory alone; change it only when the user asks. Branch `antigravity` is the integration branch for Antigravity-driven work. Specialized agent skills live in `.agents/skills/` (`mathematics-symbolic-prover`, `computational-physics-engine`, `high-performance-numeric-kernels`, `strong-gravity-coding-assistant`, `anse-evolution-lab`, `phd-multidisciplinary-benchmark`, `supergravity-guard`).

## Shared engineering rules
Follow `.antigravity/rules.md`. The essentials:
- Type-annotate all function signatures.
- No stubs (`pass`, `...`, `NotImplementedError`) or fake data (`mock_`, `dummy_`) outside `tests/`.
- Tests: at least 2 real assertions, no tautologies, mock only external I/O, use Hypothesis for pure functions.
- Report only real tool output; never invent test results or benchmark numbers.
- Keep large outputs out of context; offload to `.scratchpad/`.

## Verification before calling work done
```bash
python antigravity_guard.py
python test_rigor_guard.py
pytest tests/
```
The `[PROOF_TOKEN]` / `.antigravity_attestation` flow belongs to Antigravity. In Claude Code, completion means the commands above pass and you report their actual output.

## Claude Code hooks (`.claude/settings.json`)
- `PreToolUse` on Bash: blocks force push, `reset --hard`, `clean -f`, `--no-verify`.
- `PostToolUse` on Edit/Write: rejects Python syntax errors and stub functions in the edited file.

## Environment facts
- Tests: `.venv/bin/python -m pytest <paths> -q -p no:cacheprovider`. System `python3` breaks pytest (numpy/zarr mismatch).
- `pyproject.toml` is PEP 621 with extras (`web`, `gateway`, `guard`, `sandbox`, `training`) and a `dev` group; `uv sync --all-extras` installs everything the guards expect. Until that is run, the venv lacks fastapi/docker/hypothesis, and the web server runs with system Python: `PORT=5000 python3 web/server.py`.
- GPU: this box carries an NVIDIA T4 (confirmed by the Ollama models it actually has pulled: `qwen3:8b` + `qwen3-embedding:0.6b`, per `docs/EVOLUTION_LAB.md`'s local-LLM setup). `nvidia-smi` can still fail with "couldn't communicate with the NVIDIA driver" even when the T4 is real and Ollama is serving on it fine — don't treat that as "no GPU". `anse/infrastructure/agent_environment.py` probes live (`detect_gpu()`) and resolves the right Ollama model pair; `AUTOEVOLVE_GPU_HINT=t4` overrides the probe on a host where the driver is unreachable to Python but the box is known to have one. Off-GPU it falls back to `qwen2.5-coder:1.5b`. Either way the client is `anse.core.api_extractor.APIExtractor(..., ollama_native=True)`; Ollama 0.1.44 ignores `seed`/`temperature` on `/v1/chat/completions`.

## Cloud TPU
`detect_tpu()` (same module) finds a local TPU VM (device nodes + GCE metadata) or a remote one named by `AUTOEVOLVE_TPU_NAME` + `AUTOEVOLVE_TPU_ZONE` (verified READY via `gcloud`). Remote TPU in use: `gwenlaya-tpu-1`, `us-west4-a`, `v5litepod-1`, venv `~/venv-tpu` (auto-activated; `jax[tpu]`). `profile.jax_platform` is `"tpu"` only on the TPU VM itself. Worked example and numbers: `scripts/desi_dr2_bao/grid_posterior_jax.py`. TPU rules learned the hard way: v5e emulates float64 (correct but no faster than CPU); for float32 set `jax_default_matmul_precision=highest` or results drift ~3e-3; keep chunks small (16384) or float64 runs out of HBM; never leave CPU-only `XLA_FLAGS=--xla_tpu_*` in `/etc/environment`.

## GWAYA fail-closed gate
`anse/verification/gwaya_gate.py` wraps GWAYA v3.7.1 (`pip`/`uv sync --extra gwaya`; cloned for reading at `/data/cache/gwaya-clone/repo`, never run from inside). `verify_python(code, tests)` / `verify_rust(code)` return ACCEPT / REJECT / BLOCKED: stub audit first (static, no sandbox needed), then execution only inside bubblewrap. **On this host the sandbox is unavailable** (AppArmor `kernel.apparmor_restrict_unprivileged_userns=1` -> `bwrap: loopback: Failed RTM_NEWADDR`), so execution verdicts are BLOCKED until an admin relaxes that or adds a bwrap AppArmor profile. Never set `GWAYA_ALLOW_UNISOLATED=1`. Lean stays on `anse/formal/lean_runner.py`.

## Agent & environment capability detection
`anse/infrastructure/agent_environment.py` resolves, per process: which coding agent is driving the session (`detect_coding_agent()` — Claude Code via its own `CLAUDECODE`/`CLAUDE_CODE_ENTRYPOINT` env vars, Antigravity only via an explicit `AUTOEVOLVE_AGENT=antigravity` override since it has no documented env signal yet, else `"unknown"`) and what compute is reachable (`detect_gpu()`, live `nvidia-smi`, never assumed). `resolve_capability_profile()` combines both into the right `config_dir`/`mcp_config_path` and LLM backend. Run `python -m anse.infrastructure.agent_environment` for the resolved profile as JSON.

`.mcp.json` (Claude Code) uses `${CLAUDE_PROJECT_DIR:-.}` so it never needs per-machine edits. Keep the `:-.` default: `CLAUDE_PROJECT_DIR` is set for hooks but **not** for `.mcp.json` expansion, so a bare `${CLAUDE_PROJECT_DIR}` expands to nothing and every server fails with `ENOENT: posix_spawn '/.venv/bin/python'`, while `:-.` falls back to the project root that sessions start in. Measured from Claude Code's own MCP logs: the `:-.` form connected in 24 of 24 sessions; the bare form failed in all 8 sessions before it was reverted. (An earlier note here claimed the reverse — that Claude Code does not expand `:-default`. It does; that claim was wrong.) Verify with `claude mcp list`, which spawns each server exactly as a session would. The `leanmaster` entry uses an absolute path because that server lives outside this repo; it answers `initialize` (v1.30.0, 7 tools incl. `search_theorems`, `check_lean_snippet`). `.antigravity/mcp_config.json` has no such variable available, so after cloning onto a new machine/user run `python scripts/render_mcp_configs.py --all` to stamp in this machine's real absolute paths (`.agents/mcp_config.json` is a symlink to it and updates automatically). A prior hand-edit had left `claude-subtask-workflow` declared twice in that file (the second entry silently won); the renderer writes each server key once.

## Evolution Lab
Goals, the five use cases per phase, workflow and limitations: `docs/EVOLUTION_LAB.md`.
Runners: `run_phase{1,2,3}_evolution.py` write `results/phase{N}_evolution/results.json`, shown in the web tab "Evolution Lab". Never hand-edit results; a failing gate is reported, not hidden.

## Lessons learned — binding rules (see LL.md for the evidence)
Read `LL.md` before starting research or proving work. Non-negotiables:
- Lean verification goes through `anse/formal/lean_runner.py` only: compile + `#print axioms`, `sorryAx` rejected, axiom whitelist `{propext, Classical.choice, Quot.sound}`. `sorry` and smuggled axioms both exit 0.
- Never emit `import Mathlib` — the local build is partial. Pin imports to built modules (header of `formal/ANSE/MasterMathTribunal.lean` is known-good).
- Every experiment runs a positive and a negative control before its numbers are reported.
- Prover: `DeepSeek-Prover-V2-7B` via Ollama (plain completion prompt). Goedel-Prover needs its chat template first. One model fits the T4; don't interleave embedding jobs with prover jobs.
- Number theory ground truth: PARI/GP + Sage, never hand-rolled arithmetic.
- Every LLM call is logged (APIExtractor default-ON → JSONL + Redis + Chroma `llm_calls`). Training rows need real verdicts; `scripts/ltm_learning_mix.py` enforces the ≤30% dilution cap for unverified signal.
- Simulated agents (stubs returning canned results) are banned; a stage that cannot run reports BLOCKED.
