<div align="center">

# ANSE · AutoevolveAI

### Verification-first agentic AI for computational science

**A research harness that refuses to report success it has not earned.**

[![Tests](https://img.shields.io/badge/tests-1079_passing-brightgreen?style=flat-square&logo=pytest)](#measured-status)
[![Lean 4](https://img.shields.io/badge/Lean_4-218_theorems-blue?style=flat-square&logo=lean)](formal/ANSE)
[![Release](https://img.shields.io/badge/release-v12.5.0-blueviolet?style=flat-square&logo=github)](https://github.com/xaviercallens/AutoevolveAI/releases/tag/v12.5.0)
[![Python](https://img.shields.io/badge/python-3.11+-3776AB?style=flat-square&logo=python)](pyproject.toml)
[![Rust](https://img.shields.io/badge/rust-1.96-000000?style=flat-square&logo=rust)](crates/)
[![License](https://img.shields.io/badge/license-MIT-yellow?style=flat-square)](LICENSE)

[Quickstart](#quickstart) · [Architecture](#architecture) · [What works](#measured-status) · [**Known gaps**](#known-gaps--where-to-help) · [Contributing](#contributing)

</div>

---

## The problem this project is actually about

Ask an LLM agent to do science and it will tell you it succeeded. It will produce a loss
curve, a passing test count, a proof. The hard part is not generating any of that — it is
knowing which parts are real.

This repository ran into that wall the honest way. An internal audit found **14 components
that reported success without doing the work**: a GPU telemetry module returning
`random.uniform()` behind a docstring promising "physical truth"; a nightly trainer
recording config-only dry runs as deployed checkpoints; a "peer review" script that
hardcoded `ACCEPT WITHOUT RESERVATION` while never calling a model; a headline
energy-reduction chart whose every value was a hand-typed literal.

None of that was malice. It is the default failure mode of agentic systems: **a claim is
cheap and a verification is expensive**, so claims accumulate.

So the project's centre of gravity moved. ANSE is now built around one idea:

> **Every quantitative claim must be traceable to an artifact, and every gate must be able
> to fail.** A gate that has never rejected anything is not a gate.

Everything below is measured on named hardware, and the [known gaps](#known-gaps--where-to-help)
section lists what is still broken. That section is the roadmap, and it is where
contributions land best.

---

## What makes it different

**Refusal over fabrication.** The training pipeline declines to run and says why, rather
than producing a number. A representative real output:

```
qlora_7b: SKIPPED — 100 rows carry no attestation verdict; the verified-data gate
          has not landed. Refusing to train for real on unverified rows.
```

**Gates with negative controls.** Every gate is proven able to *reject* before its
acceptance counts. `scripts/verify_release.py` was validated by running it against a prior
release it was designed to catch — it blocked all ten fabricated claims. It then blocked
the release notes of the very version that introduced it, for one imprecise sentence.

**`sorry` is not a proof.** Lean's `sorry` compiles and **exits 0**, so every proof gate
keyed on exit codes silently accepts unproved theorems:

```lean
theorem looks_fine (n : Nat) : n + 0 = n := by sorry
-- warning: declaration uses 'sorry'          EXIT CODE 0  ← accepted by a naive gate
-- #print axioms looks_fine ⇒ [sorryAx]       ← the only reliable signal
```

Acceptance requires an axiom check, not a return code.

**Math is derived, not recalled.** Algebra that appears in a paper is produced by SymPy in
the repository and re-derived on every build. An LLM stating a closed form from memory is
a hallucination risk; a symbolic derivation is an artifact.

**Semantic memory that is actually semantic.** Retrieval runs on real 1024-d embeddings.
The previous implementation hashed character n-grams with MD5 — deterministic, fast, and
carrying no meaning whatsoever. Nearest neighbours were hash collisions.

---

## Quickstart

```bash
git clone https://github.com/xaviercallens/AutoevolveAI.git
cd AutoevolveAI
uv sync --all-extras

# What environment am I on? (never assumed — probed live)
.venv/bin/python -m anse.infrastructure.agent_environment

# Is this deployment actually working? PASS/FAIL/SKIP with evidence per check.
.venv/bin/python scripts/validate_environment.py
```

`validate_environment.py` is the entry point worth running first. It reports what is
true, exits nonzero on any failure, and shows the command output behind each verdict.

```
[PASS] gpu                Tesla T4, driver 580.178.04, 12523 MiB free of 15360
[PASS] torch_cuda         sm 7.5 — use fp16, not bf16; FlashAttention-2 needs sm_80+
[PASS] ollama_placement   a model is resident on the GPU
[PASS] ollama_throughput  34.7 tok/s warm on qwen2.5-coder:7b-instruct
[PASS] embeddings         qwen3-embedding:0.6b returns 1024-d vectors
[PASS] semantic_quality   paraphrase 0.831 > unrelated 0.265
[PASS] lean_sorry_gate    confirmed: `sorry` exits 0 but #print axioms reveals sorryAx
```

---

## Architecture

```
                    ┌─────────────────────────────────────────┐
                    │  Environment detection (probed, never   │
                    │  assumed) — agent, GPU, RAM, backend    │
                    └───────────────────┬─────────────────────┘
        ┌───────────────────────────────┴───────────────────────────────┐
        ▼                                                               ▼
┌───────────────────────┐                                   ┌───────────────────────┐
│ Claude Code / GCP T4  │                                   │ Antigravity / Linux   │
│ cuda · 15 GB · 35 t/s │                                   │ cpu · 31 GB RAM       │
└───────────┬───────────┘                                   └───────────┬───────────┘
            └───────────────────────────┬───────────────────────────────┘
                                        ▼
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                      VERIFICATION LAYER (fail-closed)                 ║
    ║   Rust/cargo · Python sandbox · Lean 4 + axiom check · SymPy           ║
    ║   Nothing is accepted on a model's word. Exit codes and axioms only.  ║
    ╚═══════════════════════════════════════════════════════════════════════╝
                                        ▲
        ┌───────────────────────────────┼───────────────────────────────┐
        ▼                               ▼                               ▼
┌───────────────┐            ┌──────────────────┐            ┌──────────────────┐
│ Reasoning     │            │ Memory           │            │ Learning         │
│ • energy/EBM  │            │ • Redis LTM      │            │ • JEPA world mdl │
│ • JEPA latent │            │ • Chroma 1024-d  │            │ • QLoRA (T4)     │
│ • symbolic    │            │ • PDF provenance │            │ • verified-only  │
│ • Lean prover │            │   {path,sha,page}│            │   episodes       │
└───────────────┘            └──────────────────┘            └──────────────────┘
```

| Layer | Package | What it does |
|---|---|---|
| Detection | `anse/infrastructure/` | Live NVML/agent/RAM probe → one capability profile |
| Verification | `anse/symbolic/`, `anse/formal/` | Sandboxed exec, Lean kernel + `#print axioms` |
| Memory | `anse/memory/` | Redis LTM, Chroma retrieval, PDF provenance store |
| Reasoning | `anse/jepa/`, `anse/physics/`, `anse/core/` | World model, energy surrogate, agent loop |
| Learning | `scripts/night_*`, `train_*` | QLoRA / JEPA on verifier-labelled episodes only |
| Orchestration | `.claude/workflows/` | Multi-agent workflows with verification stages |

### Two environments, one detection engine

Both profiles resolve from the same probe. Precedence is **explicit**, and ambiguity is
reported rather than silently tie-broken:

| | Claude Code / GCP T4 | Antigravity / local Linux |
|---|---|---|
| `profile_id` | `claude_code_tesla_t4` | `antigravity_linux_cpu_31gb` |
| Device | `cuda` · Tesla T4 15,360 MB | `cpu` · no driver |
| RAM | 29.4 GB | 31.3 GB |
| Generation | `qwen3:8b` @ **34.7 tok/s** | CPU-tier local model |
| QLoRA ceiling | **Phi-3-mini 3.8B** @ seq 1024 | small adapters, 869 MB RSS |

`describe_agent_detection()` returns `{resolved, override, signals_matched, ambiguous}`.
A host carrying both agents' signals is a *finding*, not a coin flip — a bug found exactly
because a test passed on one host and failed on the other.

---

## Measured status

Measured on the T4 host at `v12.5.0`. Reproduce with the commands shown.

| What | Result | Command |
|---|---|---|
| Test suite | **1079 passed** / 15 failed / 43 skipped | `pytest tests/ -q` |
| Collection | 1145 tests, exit 0 | `pytest tests/ --collect-only` |
| Anti-stub AST guard | **exit 0** — 124 files | `python test_rigor_guard.py` |
| Environment validator | **10/10** capability checks | `scripts/validate_environment.py` |
| CPU-profile validation | **5 passed** | `pytest tests/test_local_32gb_cpu_antigravity_validation.py` |
| Lean theorems authored | **218** across 34 files | `grep -c theorem formal/ANSE/*.lean` |
| Open proof obligations | **4**, tracked in a registry | `formal/ANSE/Blueprint.lean:155-183` |
| Chroma corpora | 1,881 Mathlib premises + 315 paper chunks | `scripts/validate_environment.py` |

### Hardware findings worth knowing

Measured on Tesla T4 (sm_75, Turing). These cost real time to discover:

| Finding | Measurement | Consequence |
|---|---|---|
| **bf16 is a trap** | fp16 **20.82** vs bf16 **2.28** TFLOPS | bf16 is **9.1× slower** than fp16 and slower than fp32. `torch.cuda.is_bf16_supported()` returns `True` and is misleading. Use fp16. |
| FlashAttention-2 | unavailable (needs sm_80+) | use `attn_implementation="sdpa"` |
| QLoRA ceiling | Phi-3-mini 3.8B @ seq 1024 → 9,601 MiB, 373 tok/s | ~10,500 samples/night; 14B is off the table |
| GPU placement | had been **CPU-only at 2.3 tok/s** for days | Ollama started before the driver existed. A restart gave **15×**. Always verify placement, never assume. |

That last one is the most transferable lesson in this repository: a service that probes for
a GPU once at startup will serve on CPU forever if it loses that race, and nothing will
tell you.

---

## Known gaps — where to help

Listed because they are true, and because this is the most useful map for a contributor.
Each is a real, scoped piece of work.

### 🔴 High impact

- **The 200-problem benchmark embeds its own solutions.** `RUST_KERNELS[id]["source"]` *is*
  the finished program; the math/physics cases compute a value then compare it to the same
  constant. There is no model generation in the loop and **no problem selector at all**.
  Restructuring this into `(statement, hidden reference, tolerance)` triples is the single
  highest-value contribution available.
- **Math and physics have no independent verifier.** Cases self-assert via SymPy against
  their own constants. `anse/benchmark/invariant_registry.yaml` (993 lines of per-case
  invariants, tolerances and units) is the raw material for a genuine dimensional and
  conservation-law check.
- **Peer review is not real.** Three `scripts/review_*.py` files make **zero** model calls
  and hardcode `ACCEPT WITHOUT RESERVATION`. Replacing them with a reviewer that can reject
  — proven on a negative control — is a well-scoped, high-value task.
- **`antigravity_guard.py` exits 1** on 2,306 pre-existing repo-wide Ruff findings (868
  auto-fixable). Mechanical, reviewable, and it unblocks CI.

### 🟡 Structural

- **Six competing top-level pipelines.** `anse/v2`…`v5` form no version chain (v3 doesn't
  import v2, etc.), plus two orchestrators with zero inbound imports. Energy computation
  exists independently in four places, DPO in four.
- **755 LOC of dead code** in `anse/` with no inbound imports, no tests and no entry point.
- **Layering inversion:** `anse/` imports from four root-level scripts, which is why every
  invocation needs `PYTHONPATH=$REPO`.
- **Data-plane schema mismatch:** `LoopTrace.metadata` defaults to `{}`, but the JEPA reader
  treats `metadata["tests_total"]` as required and **silently drops** rows lacking it.

### 🟢 Good first issues

- 15 failing tests — **6 are the remediation working**: `latent_dreamer` now raises
  `SimulationRefusedError` while the old tests assert `status == "success"`. Updating tests
  that asserted fabricating behaviour is a clean, self-contained contribution.
- 7 hardcoded absolute paths in tracked Python, two naming a different user's home.
- `results/` is 402 files / 126 MB tracked in git.
- Two `papers/figures/` PDFs are byte-identical (`sha256 22453f85…`) — a figure labelled
  "200 benchmarks" is the same bytes as the one labelled "120".

Full detail with `file:line` citations: [`docs/remediation/AUDIT_2026-09-26.md`](docs/remediation/AUDIT_2026-09-26.md).
Plan and sequencing: [`docs/remediation/IMPROVEMENT_PLAN_2026-09-26.md`](docs/remediation/IMPROVEMENT_PLAN_2026-09-26.md).

---

## Workflows

Multi-agent workflows in `.claude/workflows/`, each with verification built into its
structure rather than bolted on:

| Workflow | Purpose | Its safeguard |
|---|---|---|
| `anse-honest-baseline` | Restructure the bank into real problems; measure the first honest pass rate | Counts harness errors separately from model failures; refuses to score a domain with no sound verifier |
| `anse-lean-proof-gate` | One axiom-checked proof gate, then best-of-N proving | **Halts** if the gate ever accepts a `sorry` proof |
| `anse-ladder-cascade` | Local-first cascade, escalating only on verified failure | **Halts** on nonzero EVAL/TRAIN hash overlap |
| `anse-nightly-distill` | Night QLoRA on the T4 | Reports the naive first-vs-last metric *and* the honest trend, every night |
| `anse-claims-provenance` | Trace every claim to an artifact; adversarial review | Reviewer must reject a knowingly-broken paper first |

The economics are deliberate: **workflow agents build and verify harnesses; they never
solve the problems themselves.** Candidate generation is local GPU inference. Paid tokens
buy engineering, not answers.

---

## Contributing

Contributions are genuinely welcome, and the [known gaps](#known-gaps--where-to-help) are
the best place to start. Three project-specific rules, all enforced mechanically:

1. **Report only real tool output.** Never write a number you did not observe. If something
   cannot be measured, say so — a gap is a result.
2. **No stubs or fake data outside `tests/`.** Enforced by `test_rigor_guard.py`
   (AST-level) and `antigravity_guard.py`.
3. **Tests need ≥2 real assertions**, no tautologies, and mock only external I/O.

```bash
# before opening a PR
.venv/bin/python -m pytest tests/ -q
.venv/bin/python test_rigor_guard.py
.venv/bin/python scripts/validate_environment.py
```

If you change something a release will claim, `scripts/verify_release.py` will check that
claim against your diff. It is not decorative — it has blocked this project's own releases.

**Discussion and issues:** use GitHub Issues. A report saying "this claim looks
unsupported" is as valuable as a patch — that is how the audit started.

---

## Documentation

| Document | Contents |
|---|---|
| [`AUDIT_2026-09-26.md`](docs/remediation/AUDIT_2026-09-26.md) | Full integrity audit with `file:line` citations |
| [`IMPROVEMENT_PLAN_2026-09-26.md`](docs/remediation/IMPROVEMENT_PLAN_2026-09-26.md) | Architecture target, cost model, capability ladder |
| [`EBM_JEPA_Foundations.md`](docs/EBM_JEPA_Foundations.md) | Energy-based model and JEPA theory |
| [`EVOLUTION_LAB.md`](docs/EVOLUTION_LAB.md) | Local LLM setup and evolution experiments |
| [`CHANGELOG.md`](CHANGELOG.md) | Release history, including a superseded entry retained for the record |
| [`CLAUDE.md`](CLAUDE.md) | Agent guide: environment facts, hooks, MCP |

---

<div align="center">

**Built on the premise that a system which cannot fail its own tests has not been tested.**

MIT licensed · Issues and PRs welcome

</div>
