---
name: anse-evolution-lab
description: >-
  Evolve an ANSE phase (1 reality engine, 2 JEPA intuition, 3 autopoiesis) and prove the
  improvement with five measured use cases and a gate that can fail. Use this skill when asked
  to improve a phase, validate "AI improvement", add or change a use case, re-run the
  evolution benchmarks, or explain the numbers shown in the web tab "Evolution Lab".
---

# ANSE Evolution Lab Skill

Every claimed improvement must be measured on a real model, against an independent check,
with a gate that can fail. Full background, current numbers and known limitations:
`docs/EVOLUTION_LAB.md`.

## The five-step workflow

1. **Baseline.** Read the code, list concrete defects with file and line, and measure current
   behaviour on a real model before changing anything.
2. **Evolve behind a parameter.** Make each improvement opt-in (`hidden_tests=`,
   `lesson_memory=`, `adaptive_retry=`, `pair_mode=`, a registry root) so the old path stays
   runnable and the two can be compared.
3. **Run the five use cases** of the phase. Each answers one question and stores evidence rows.
4. **Gate.** One boolean goal per use case, computed from measured numbers. Exit code 1 on failure.
5. **Skeptical review, then promote or report.** Re-run the evidence looking for label leaks,
   gates that are true by construction, pseudo-replication and unsupported numbers.

## Commands

```bash
uv sync --all-extras                         # once; see "Environment" below
uv run python run_phase1_evolution.py --seeds 1 2        # needs an LLM endpoint, hours on CPU
uv run python run_phase2_evolution.py --seeds 1 2 3 4 5 \
    --traces results/phase1_evolution/traces_uc2_verified.jsonl \
             results/phase1_evolution/traces_uc2_adaptive.jsonl \
             results/phase1_evolution/traces_uc4_memory.jsonl   # CPU, about 5 minutes
uv run python run_phase3_evolution.py        # CPU timing plus about 6 LLM generations
PORT=5000 uv run python web/server.py        # then open /#evolution
```

Results: `results/phase{N}_evolution/results.json` with `gate`, `uc1`..`uc5`, each holding
`title`, `question`, summary metrics and `rows`. The web tab renders this contract generically.

## Hard rules

- A failing gate is a valid result. Report it and say what it implies. Never tune a threshold
  after seeing the result, never hand-edit `results.json`, never seed a run to force a pass.
- Score on held-out **tasks**, not held-out traces. Score first attempts only when the label can
  leak from the input (a retry exists only because the previous attempt failed).
- Always compare against the strongest trivial baseline (constant, linear probe, random pick,
  "nothing changes"), not against nothing.
- Count independent samples honestly. Verify the backend honours `seed` (the Phase 1 runner
  checks this at start-up): Ollama 0.1.44 ignores `seed` and `temperature` on
  `/v1/chat/completions`; use `APIExtractor(..., ollama_native=True)`.
- Correctness before speed: a child is compared on energy only after it passes the equivalence
  gate run by the trusted out-of-process driver in `anse/autopoiesis/hypervisor.py`.
- Only hidden-test-verified solutions may enter `LessonMemory` or any training set.

## Environment

- `pyproject.toml` is PEP 621 with extras `web`, `gateway`, `guard`, `sandbox`, `training` and a
  `dev` group. `uv sync --all-extras` gives an environment in which `antigravity_guard.py`
  finds every import. Before 2026-09-21 the file was Poetry-only and `uv sync` / `uv run`
  would have uninstalled the whole environment.
- No local GPU. Local LLM: Ollama `qwen2.5-coder:1.5b`, about 27 s per generation on CPU.
  Remote GPU endpoints plug in through `ANSE_API_BASE`, `ANSE_API_KEY`, `ANSE_API_MODEL`.

## Current state (2026-09-21, qwen2.5-coder:1.5b)

| Phase | Gate | Takeaway |
|---|---|---|
| 1 | 4 of 6 | Hidden tests are necessary: 36% of legacy "successes" were false. Adaptive retry and lesson memory did not help this model; both stay opt-in. |
| 2 | 2 of 5 | The JEPA latent does not beat a linear probe on the same embedding. Do not use it to skip sandbox runs yet. |
| 3 | 5 of 5 | Equivalence gate, noise-aware domination, registry with rollback all hold; 2 of 4 LLM-proposed children promoted, 0 incorrect. |
