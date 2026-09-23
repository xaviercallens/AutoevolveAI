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
- No GPU. LLM = Ollama `qwen2.5-coder:1.5b` through `anse.core.api_extractor.APIExtractor(..., ollama_native=True)`. Ollama 0.1.44 ignores `seed`/`temperature` on `/v1/chat/completions`.

## Evolution Lab
Goals, the five use cases per phase, workflow and limitations: `docs/EVOLUTION_LAB.md`.
Runners: `run_phase{1,2,3}_evolution.py` write `results/phase{N}_evolution/results.json`, shown in the web tab "Evolution Lab". Never hand-edit results; a failing gate is reported, not hidden.
