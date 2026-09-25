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

## Agent & environment capability detection
`anse/infrastructure/agent_environment.py` resolves, per process: which coding agent is driving the session (`detect_coding_agent()` — Claude Code via its own `CLAUDECODE`/`CLAUDE_CODE_ENTRYPOINT` env vars, Antigravity only via an explicit `AUTOEVOLVE_AGENT=antigravity` override since it has no documented env signal yet, else `"unknown"`) and what compute is reachable (`detect_gpu()`, live `nvidia-smi`, never assumed). `resolve_capability_profile()` combines both into the right `config_dir`/`mcp_config_path` and LLM backend. Run `python -m anse.infrastructure.agent_environment` for the resolved profile as JSON.

`.mcp.json` (Claude Code) uses the portable `${CLAUDE_PROJECT_DIR:-.}` variable so it never needs per-machine edits. `.antigravity/mcp_config.json` has no such variable available, so after cloning onto a new machine/user run `python scripts/render_mcp_configs.py --all` to stamp in this machine's real absolute paths (`.agents/mcp_config.json` is a symlink to it and updates automatically). A prior hand-edit had left `claude-subtask-workflow` declared twice in that file (the second entry silently won); the renderer writes each server key once.

## Evolution Lab
Goals, the five use cases per phase, workflow and limitations: `docs/EVOLUTION_LAB.md`.
Runners: `run_phase{1,2,3}_evolution.py` write `results/phase{N}_evolution/results.json`, shown in the web tab "Evolution Lab". Never hand-edit results; a failing gate is reported, not hidden.
