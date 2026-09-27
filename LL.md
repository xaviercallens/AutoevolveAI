# LL.md — Lessons Learned, BSD Run One (2026-09-27)

Ground rules for every future run. Each lesson was paid for with real failures
or near-misses in this run; none is theoretical. Companion evidence:
`docs/literature/BSD_LITERATURE_REVIEW_2026.md`, memory `verification-traps`,
`local-lean-assets`, and the run report artifact.

## 1. Validate the instrument before the experiment

The first prover bake-off scored 0/6 for every model. The cause was not the
models: the harness prepended `import Mathlib`, which does not resolve on this
machine (partial Mathlib build, 3,431/~7,000 oleans, no umbrella). Every
experiment must first pass a **positive control** (a case that must succeed)
and a **negative control** (a case that must fail) before its numbers count.
The Lean gate got the same treatment and it caught a real hole: a smuggled
`axiom cheat : False` passed. Gate now whitelists
`{propext, Classical.choice, Quot.sound}`.

## 2. Kernel checks are the only Lean truth

- `sorry` compiles with exit code 0. Only `#print axioms` + `sorryAx` check
  catches it.
- Untrusted axioms compile with exit code 0. Only the whitelist catches them.
- Vacuous statements (`True := trivial`) pass both. Only statement review
  catches those — schedule it explicitly.
- Use `anse/formal/lean_runner.py` (hardened 2026-09-27) as the single gate.

## 3. Pin imports to the built Mathlib subset

Never emit or accept `import Mathlib` / `import Mathlib.Tactic` here. The
header of `formal/ANSE/MasterMathTribunal.lean` is a known-good set; 129
individual `Mathlib/Tactic/*.olean` files exist (Ring, Linarith, ...). Strip
model-emitted imports and substitute a pinned header
(`scripts/prover_bakeoff.py` shows the pattern).

## 4. Model facts measured on this T4

- `DeepSeek-Prover-V2-7B` (Q8_0, Ollama, plain completion prompt): 2/3
  statements kernel-clean. Current pipeline prover.
- `Goedel-Prover-V2-8B` (Q6_K): returned **empty completions** for 9/9 plain
  prompts. That is a chat-template artifact, not a capability result. Apply
  its documented template before judging it.
- pass@3 sampling (T=0.7) rescued nothing that greedy missed on these tasks.
- One model at a time fits the T4 (MAX_LOADED_MODELS=1). Embedding jobs and
  prover jobs thrash each other through model swaps — serialize them, or move
  embeddings (qwen3-embedding is 0.6B) off-GPU.
- Training a 7B on the T4 needs 4-bit QLoRA. The trainer loaded
  Qwen2.5-Coder-7B in plain fp16 (~14.2 GiB of weights on a 15 GiB card) and
  OOM'd at FIT on 2026-09-27; while it held the card it also starved the
  embedder (cudaMalloc OOM in the literature ingest). With NF4 + fp16 compute
  (sm_75 has no bf16), the fit runs at ~8.1 GiB.

## 5. Computational ground truth is cheap — use it first

PARI/GP (`ellanalyticrank`) plus Sage (`E.rank()`, 2-descent) verified BSD
rank equality for 11a1/37a1/389a1/5077a1 (ranks 0–3) in seconds, both sides
machine-computed. Any hand-rolled arithmetic "solver" (the run-one Rust toy
that hardcoded rank=1) is obsolete on this box and must not be written again.

## 6. The winning strategy: the computational–formal ladder

Selected as **the** approach after the scorecard (see run report): PARI/Sage
computes; Lean kernel-checks the discrete facts (`gen_on_W37` and
`BSD_RankStatement` are the first rungs, both in the project build). Each rung
is small, verifiable, and accumulates. RAG premise retrieval (45,455 FLT +
36,825 NS signatures indexed; 1,000 embedded in `lean_premises`) and the
DeepSeek prover serve this ladder rather than replacing it.

## 7. Statements must be faithful before proofs matter

Two Millennium statements in this repo were defective: BSD's "rank" was a free
field untied to E(ℚ) (fixed: `Module.rank ℚ (ℚ ⊗[ℤ] W.toAffine.Point)`), and
Navier–Stokes lacks the Clay finite-energy/decay conditions (still open, H9).
A proof of a wrong statement is worthless; review statements first.

## 8. Memory and learning discipline

- Every LLM call is recorded: default-ON JSONL (disk 2) + Redis
  `anse:ltm:llm_calls` + Chroma `llm_calls`. Scripts that call Ollama directly
  must either go through `APIExtractor` or write the same JSONL schema.
- Training data needs verdicts. The full trainer BLOCKED on 100 verdict-less
  lake rows (correctly). Only rows with real verdicts (hidden-test episodes,
  kernel-clean proofs) were appended, with provenance strings.
- Dilution cap (`scripts/ltm_learning_mix.py`): new/unverified signal ≤ 30% of
  a training mix, verified episodes anchor the rest; BLOCKED beats silently
  inverting the ratio.
- Failures are data: the bake-off's 12 kernel-verified failures are the first
  discriminative signal this project has produced (the old harvest was 100%
  passing and taught nothing).
- A falling training loss is not an improvement. `night_training_workflow.py`
  EVAL compares first vs last *training* loss (no held-out rows, despite its
  docstring); with 14 rows x 200 steps that falls by construction. GATE
  correctly refuses promotion until card P4-5 (held-out eval) lands. Report
  such adapters as "trained candidate, not promoted", never as better.
- Job tmp dirs are deleted with the job. Experiment evidence (results JSON,
  proof files, controls) must be copied into `results/<run>/` before the run
  ends, or the numbers in the report become unverifiable.

## 9. Session mechanics that cost time

- `EnterWorktree` branches from a stale base here (no fresh origin); always
  `git merge main` immediately after entering.
- `cmd | tail` hides exit codes; use `${PIPESTATUS[0]}`.
- Long compiles/generations go `run_in_background` with generous timeouts;
  a 400s timeout killed a healthy Mathlib elaboration under CPU contention.
- Simulated agents (asyncio stubs returning canned dicts) are banned. If a
  stage cannot run for real, it reports BLOCKED.

## 10. Next-run queue (carried forward)

1. Goedel-Prover chat template → rerun bake-off head-to-head.
2. H2 measurement: proof rate with vs. without retrieved premises.
3. Embed the full 82,280-signature corpus (overnight, off-GPU embeddings).
4. H9: Clay-correct the Navier–Stokes statement.
5. Ladder rungs: 11a1 torsion lemmas, 37a1 infinite-order groundwork.
6. Statement-review pass over `formal/ANSE/*.lean` for vacuous Props.
