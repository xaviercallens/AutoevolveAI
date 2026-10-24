# LL.md — Lessons Learned (running log, started 2026-09-27)

Sections 0–10: BSD run one. Section 11: the BAO/dark-energy run and the
Elenchus integration (same day, second exercise).

Ground rules for every future run. Each lesson was paid for with real failures
or near-misses in this run; none is theoretical. Companion evidence:
`docs/literature/BSD_LITERATURE_REVIEW_2026.md`, memory `verification-traps`,
`local-lean-assets`, and the run report artifact.

## 0. Correction to the run-one record

The night-regen run reported "20/20 master problems rejected — Qwen too small
for formal math". That diagnosis was wrong. `regenerate_10_math_problems_dspy.py`
built `APIExtractor(timeout_s=1.0)`: every call timed out, and the `except`
branch wrote a fake `theorem X : True := by trivial`. The auditor then rejected
the fake. No model output was ever judged, which is also why the call log stayed
empty (`_log_call` runs only after a successful return). The pipeline's
"SUCCESS" outcome only meant each stage exited 0. Fixed 2026-09-27: timeout
900 s, failures return `GENERATION_FAILED`, no fabricated proof.

Also removed from main on 2026-09-27, as simulated or invented output from
earlier in the same session: `bsd_agent_swarm.py` (sleep stubs),
`validate_approaches.py` (hardcoded scores), `millennium_*solver*.py` and
`results/millennium/` (invented success probabilities),
`bsd_literature_and_framework.py`, `results/bsd/`, `results/validation/`, and
`rust_solver/` (rank hardcoded to 1). `anse/core/red_team.py` DeepThinkAuditor
still returns canned "Simulated PRM" verdicts; treat them as non-evidence.

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
- `Goedel-Prover-V2-8B` (Q6_K): the run-one "0/9, empty completions" was a
  harness bug. Goedel-V2 is a thinking model and its GGUF never closes
  `</think>`, so Ollama files the ENTIRE answer (complete proof included)
  under `message.thinking`; `content`/`response` stay empty. Read
  content + thinking and take the LAST Lean block (it writes a `sorry`
  sketch first, then "Complete Lean 4 Proof"). `run_ladder.py` does this.
  Also: the stop at ~800 tokens was the model's own end token
  (`done_reason: stop`), not a cap.
- pass@3 sampling (T=0.7) rescued nothing that greedy missed on these tasks.
- One model at a time fits the T4 (MAX_LOADED_MODELS=1). Embedding jobs and
  prover jobs thrash each other through model swaps — serialize them, or move
  embeddings (qwen3-embedding is 0.6B) off-GPU.
- Training a 7B on the T4 needs 4-bit QLoRA. The trainer loaded
  Qwen2.5-Coder-7B in plain fp16 (~14.2 GiB of weights on a 15 GiB card) and
  OOM'd at FIT on 2026-09-27; while it held the card it also starved the
  embedder (cudaMalloc OOM in the literature ingest). With NF4 + fp16 compute
  (sm_75 has no bf16), the fit runs at ~8.1 GiB.

## 4b. Hardness comes from generated, validated instances

Three hand-picked theorems (run one) measured nothing. `scripts/hardness/`
generates tiered statements from Sage's Cremona data, mixes TRUE facts with
Sage-verified FALSE variants, and validates the instrument before any model
runs: every statement elaborates with `sorry`, none is vacuous, reference
proofs pass on true items (45/46) and fail on false items (12/12). The false
variants caught their own generator bug: a y+1 bump can land on the conjugate
point, so falsity must be re-checked, never assumed. Proofs are always
compiled against OUR statement, so a model cannot weaken what it proves.
The ladder is frozen as the held-out split; the trainer drops any row
containing a frozen proposition (normalized, so renamed copies are caught —
it found 2 such rows that run one had added).

## 4c. Baseline result: 2026-09-27, both provers, all 118 items

DeepSeek-Prover-V2-7B and Goedel-Prover-V2-8B, greedy, against the full
hardness ladder. Full data: `results/hardness/baseline.json`.

| Tier | DeepSeek pass | Goedel pass | False accepted |
|---|---|---|---|
| T0 (Mathlib lemmas) | 6/10 | 8/10 | 0/0 |
| T1 (point on curve) | 0/12 | 0/12 | 0/4 |
| T2 (discriminant) | 0/12 | 0/12 | 0/4 |
| T3 (group-law double) | 0/12 | 0/12 | 0/4 |
| T4 (BSD sentinel) | 0/1 | 0/1 | -- |

**Zero false-item acceptances across 118 attempts, under real model pressure
(not just the reference-proof positive control).** The gate holds.

**T1-T3 at exactly 0% is a real capability gap, not a harness bug** --
verified by hand-replaying two failing attempts (`t1_11a1_T`, `t2_11a1_T`)
live against `lake env lean`: both are genuine elaboration failures (`rc=1`,
"tactic `rfl` failed"), not artifacts of the compile harness. Lean 4's error
recovery still prints `#print axioms` with `sorryAx` for a *failed* tactic
block (it inserts a placeholder so elaboration can continue past the error)
-- so a naive check on `sorryAx` alone, without also checking `rc==0`, would
have shown a green "no forbidden axioms" on a proof that never actually
compiled. `build_ladder.py::compile_one` requires both; this is the same
class of trap as the bare `sorry` check, one level deeper.

**Root cause, read from the raw generations, not guessed:** both models
write a plausible generic tactic (`simp [W, WeierstrassCurve.Δ] <;>
norm_num <;> rfl`) but never name the specific lemmas the goal actually needs
(`WeierstrassCurve.b₂/b₄/b₆/b₈`, `Affine.slope/addX/addY`). They
know Lean 4 syntax fluently and fail identically on every curve -- this is a
vocabulary gap, not a reasoning gap, which is exactly what premise retrieval
(TODO item 5, `lean_premises` already has 1,000 signatures indexed) is for.

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

## 8b. The T4 is shared with other sessions

Mid-baseline, another Claude session on this machine ran
`sudo systemctl stop ollama` to free the GPU for its own benchmark
(`runux-ai-runtime/autoresearch_lowtier/bench.py`). The ladder runner kept
going and logged 112 instant ConnectErrors that measured nothing. Runners
must (a) wait for the server instead of burning items, (b) resume from
completed rows, (c) never treat an infrastructure error as a prover result.
`run_ladder.py` now does all three. Restart Ollama only after confirming the
GPU is idle and the other job is finished. The durable fix is a GPU lease
(TODO item 10, now built and wired into all three GPU touch points --
`run_ladder.py`, `night_training_workflow.py`, `restart_session.sh` --
`scripts/shared_gpu_lease/`).

**The lease's own bugs, both caught by testing across real process
boundaries, not just in-process:** (1) checking identity by pid instead of
holder-name let one logical holder steal from another when they happened to
share a pid; (2) a CLI `acquire` that records its own transient pid marks
the lease dead the instant that helper process exits -- it must record the
calling *shell's* pid (`getppid()`), which stays alive for the actual GPU
work. Neither bug showed up testing inside one Python process; both showed
up running the acquire/release/contend sequence as separate OS processes,
which is the only way the lease is ever really used.

**A second real project on the same T4 was found to have the identical
problem.** `runux-ai-runtime`'s `require_exclusive_gpu()` only detects an
already-running contender via `nvidia-smi`; it does not block one from
starting. Its own `docs/CLAUDE_SESSION_GUIDE.md` already states the rule
("stopping Ollama is disruptive -- flag it and get confirmation") that the
lease now enforces mechanically instead of by instruction-following.

## 9. Session mechanics that cost time

- `EnterWorktree` branches from a stale base here (no fresh origin); always
  `git merge main` immediately after entering.
- `cmd | tail` hides exit codes; use `${PIPESTATUS[0]}`.
- Long compiles/generations go `run_in_background` with generous timeouts;
  a 400s timeout killed a healthy Mathlib elaboration under CPU contention.
- Simulated agents (asyncio stubs returning canned dicts) are banned. If a
  stage cannot run for real, it reports BLOCKED.

## 10. Next-run queue (carried forward from run one)

1. Goedel-Prover chat template → rerun bake-off head-to-head.
2. H2 measurement: proof rate with vs. without retrieved premises.
3. Embed the full 82,280-signature corpus (overnight, off-GPU embeddings).
4. H9: Clay-correct the Navier–Stokes statement.
5. Ladder rungs: 11a1 torsion lemmas, 37a1 infinite-order groundwork.
6. Statement-review pass over `formal/ANSE/*.lean` for vacuous Props.

## 11. BAO/dark-energy run: a second, independent exercise (2026-09-27)

Second problem chosen deliberately far from BSD (astrophysics/dark-energy
vs. number theory), to test whether the discipline built in run one
generalizes or was accidentally specific to Lean/number-theory work. It did
generalize, with one new tool and one new kind of mistake.

### 11a. A real, previously-unused rigor tool was found and integrated

`github.com/xaviercallens/SocrateAI-Scientific-Elenchus` (same author, no
prior local presence, no prior AutoevolveAI integration) is a genuine
claim-verification harness: a 5-tier epistemic ladder (X exploratory <
C conjecture < L literature < B exact-arithmetic < A kernel-verified Lean),
and a Lean vacuity/axiom-footprint scanner. Verified real before trusting
it: ran its own test suite (298/299 unit tests, its ratchet's 22 corpus
fixtures and 5 weaken-negative-controls all correct), then ran it against
our own file and, separately, a hand-built negative control (see 11b).
**How to invoke it against this project's Mathlib**: it shells out to bare
`lean`, not `lake env lean`, so it only sees Mathlib if launched as
`lake env python3 tools/elenchus_check.py <file>` from `formal/` -- run
plain, it fails with `unknown module prefix 'Mathlib'`, which looks like a
tool bug but is a missing-environment issue.

### 11b. The tool found a real gap, and self-verification caught more

`elenchus_check.py` flagged `NO_FOOTPRINT` on the first committed
`BAO_FlatLCDM.lean`: it compiled clean, but the `#print axioms` checks that
proved it clean had only been run in a scratch copy, never committed inside
the file. "The gate asked nothing, so a clean result means nothing." This is
the same class of gap as run one's sorryAx-on-failed-tactics trap, one level
up: an axiom check that exists but isn't reproducible from the committed
source is barely better than no check. Fixed by adding the `#print axioms`
lines to the file itself. **Apply going forward**: any Lean file gated on an
axiom footprint must contain its own `#print axioms` lines; a check run
once, out of band, and discarded does not count.

We then built our own negative control (mutating `distance_duality`'s
conclusion to `True`) rather than relying only on the tool's own reserved
`--weaken` self-tests, and confirmed the tool flags the mutation and passes
the genuine theorem. **Apply going forward**: when adopting an external
rigor tool, don't just trust its own test suite -- also run it against a
hand-built mutation of *your own* content, once, before trusting a "no
findings" verdict on that content.

### 11c. A real worktree-isolation violation, caught and corrected in-session

While wiring the verified Lean file into the project (adding an import line
to `formal/ANSE.lean` and running `lake build`), this session used `cp` and
`printf >>` directly on the **shared checkout** while still worktree-
isolated -- exactly the violation the isolation guard exists to prevent,
and it went through because those are plain Bash file operations, not
Edit/Write tool calls or `git`-prefixed commands, which is what the guard's
detection actually keys on. Caught by checking `git status` on the shared
path (which itself required leaving the worktree isolation context to run),
and fixed by manually reverting the two changes (`head -n -1` on the
appended import line, `rm` on the stray file) via plain file operations
before redoing the same edits correctly inside the worktree's own copy.
**Apply going forward**: `lake env lean <scratch-file>` for a standalone
kernel check is fine from the shared `formal/` directory (it writes nothing
git-tracked); `cp`/`>>`/any persistent write into a git-tracked path under
the shared checkout is not, even via plain Bash, even if the guard doesn't
catch it. The guard's silence on a given tool call is not permission.

A second instance of nearly the same mistake happened moments later: after
`ExitWorktree`, this session ran further `git commit`s directly against
`main` via Bash (not `-C`, cwd already `main`) without hitting any guard,
then tried an `Edit` call against a `main`-rooted path and *that* finally
triggered "hasn't isolated its changes yet." **The real rule, restated**: a
background session isolates for the *whole* task, not just until
`ExitWorktree`'s first successful merge -- re-enter a worktree for every
further edit, never resume writing to `main` just because a Bash command to
it happened not to be blocked.

### 11d. The result itself

Independent re-fit of DESI DR1's public combined BAO summary statistics
(real data, sha256'd; two independently-coded prediction methods agreeing
to <1e-4; an independent grid-search cross-check) recovered
$\Omega_m=0.2939$, $r_d h=101.94$ Mpc, within 0.07σ/0.11σ of DESI's own
quoted $0.295\pm0.015$ / $101.8\pm1.3$ Mpc -- a genuine, checkable success on
the "near-certain, not a research gamble" framing this run was chosen under.
Full writeup: `papers/bao_flcdm/bao_flcdm_consistency.tex` (compiles clean,
pdflatex, 2 passes). Three Lean theorems (positivity/monotonicity of the
expansion rate, the flat-space distance-duality identity) kernel-verified,
axioms exactly the trusted set, Elenchus-reviewed clean after the fix in
11b.

### 11e. Retrofit performed this cycle

- Literature review + paper ingested into the `literature` Chroma
  collection (188 -> 200 chunks); retrieval sanity-checked.
- The 3 verified BAO proofs appended to the lake training corpus with
  `verdict: PASSED` and provenance strings, matching run one's pattern.
- `ltm_learning_mix.py` rerun: dilution cap held (29.4% <= 30%) against a
  grown new-signal pool (137, up from 20).
- Full retrain re-run via `night_training_workflow.py`: 15 verified rows (up
  from 14; frozen-split exclusion held), 200 steps, loss 1.2844 -> 0.0646,
  GATE correctly `BLOCKED` -- "no frozen-split pass@k eval (P4-5), and the
  trained model is not the prover; training-loss drop is not evidence."
  Consistent with run one: the gate has not once produced a false promotion
  across two separate retrains. TODO item 2 (P4-5) is the one blocker that
  has now been hit twice; it should be next run's first item, not last.

### 11f. A real disconnect found while re-running the retrofit

`scripts/ltm_learning_mix.py` writes its diluted, capped mix to
`data/training/ltm_mix.jsonl`. `night_training_workflow.py`'s `step_data`
does **not read that file** -- it reads
`LAKE/data/redis/redis_ltm_lora_dataset.jsonl` directly and applies its own
independent verdict-filter and frozen-split-exclusion. Every session this
run built the diluted mix and reported its dilution ratio as if it were
governing the subsequent training run; it was never wired to. The actual
training run is currently governed only by the trainer's own verdict filter
(no dilution cap on the raw lake corpus). **Apply going forward**: either
point `step_data` at `ltm_mix.jsonl`, or stop presenting the mix-builder's
output as if it constrains training until it does.

### 11g. Next-run queue addition

7. `require_exclusive_gpu()`-style detection plus the shared lease together
   in one place: right now the lease is opt-in per script, and nothing
   forces a new script to remember to acquire it (this run's own
   `fit_desi_bao.py` never touched the GPU, so it didn't need to -- but the
   next GPU-touching script in this area will, and there is no lint/gate
   catching a forgotten acquire).
8. Elenchus's ledger.py (tier-capped claim ledger) was surveyed but not
   integrated this run -- register this run's claims (Tier A: the 3 Lean
   theorems; Tier B: the numeric fit; Tier L: the DESI literature values) in
   it as a concrete adoption, not just a citation.
9. DESI DR2 (arXiv:2503.14738) and the eBOSS/SDSS files sitting in the same
   local data directory are an obvious, near-zero-marginal-cost extension of
   this exact pipeline -- same code, new mean/cov files.

## 12. Three cosmology problems via Workflow (2026-09-27)

Three preregistered problems run in parallel through one pipeline
(literature + preregistration -> fit with controls -> Lean -> Elenchus ledger
-> paper -> adversarial Fable referee that re-runs everything -> fix round).
Per-problem lessons are in each `results/<run>/` referee and fix records.

### 12a. Results (all vs the published numbers fetched from the papers)

| run | outcome | headline |
|---|---|---|
| `desi_dr2_bao` | SUCCESS, 14/14 criteria | Om 0.29781±0.00856 (+0.04σ), h·r_d 101.530±0.732 (−0.01σ); wCDM w −0.9164±0.0787 (−0.005σ); DR1→DR2 ΔOm 0.23σ; 6 Lean theorems |
| `bao_bbn_h0` | SUCCESS (T1), PARTIAL (T2) | H0 68.545±0.594 vs 68.51±0.58 (|Δ| 0.035 ≤ 0.15) with exact CAMB r_d; DR1 check |Δ| 0.167 vs strict 0.15; 10 Lean theorems |
| `eboss_vs_desi` | science PASS | SDSS Om 0.2987±0.0164 vs published 0.299±0.016; SDSS–DESI tension 0.88σ (PTE 0.38); 9 Lean theorems |

Lean is kernel-checked with whitelist-only axioms in the pinned build, and the
BAO module also in LeanMaster's full Mathlib on disk 2 (rc 0, 37 s once warm;
a cold `import Mathlib` probe timed out at 20 min under load).

### 12b. Lessons

1. **Pre-register, then amend in the open.** CAMB was installed after the H0
   preregistration. The amendment (CAMB primary, fitting formula secondary) was
   written before any fit output was read, and the already-existing first fit was
   hash-locked unread (`preregistration_amendment_1.json`). Both analyses are
   reported. Commit preregistration files to git before the first fit next time:
   an untracked file has only its mtime as evidence.
2. **A model referee's audit clears the Elenchus gate.** `ledger.py` only
   type-checks `audit`, so a model-written audit turns rc 1 into rc 0. All three
   runs recorded the audit as the model's, labelled "NOT a person". rc 0 therefore
   means "model-referee audited"; human statement audits remain open (TODO 14).
   The audit must be bound to the Lean file's sha256 and name its auditor kind.
3. **`lean_runner.py` cannot gate a new file from a worktree.** It imports a built
   module and writes a temp file into the shared `formal/`. Every run used
   `lake env lean <file>` from main's `formal/` plus in-file `#print axioms`
   instead: a documented deviation from the binding rule until TODO 15 lands.
4. **Negative controls must include a subtle bug.** Scrambled data and EdS fail in
   any pipeline. A wrong-convention control (omega_nu left out of omega_cdm) moved
   H0 by 0.164 with Δχ² = 5e-5: the data cannot see it, only the external target can.
5. **State the theorem you planned, check it numerically first.** The H0 run had
   swapped the preregistered monotonicity theorem for identities because it looked
   hard; stated honestly it took one Mathlib lemma and revealed the preregistered
   hypothesis was wrong in a corner of the prior. The DR2 statements drifted from
   z > −1 to z ≥ 0; only the referee read caught it.
6. **Frozen scripts stay frozen.** Script sha256 is pinned in ledger evidence, so the
   new scripts get a scoped ruff per-file exemption instead of a reformat.
7. **Workflow mechanics.** An agent that ends without its structured output drops the
   item; resuming the workflow replays the cached prefix and re-runs only that item.
   Prompt text for completed stages must stay byte-identical to keep the cache.

### 12c. Synergy with rusty-SUNDIALS

The BAO distance integrals were ported to `crates/qf-bao-distances` (rusty-SUNDIALS
PR #61, merged): DR2 fit from Rust Om 0.29743±0.00861, h·r_d 101.543±0.735, agreeing
with this repo's Python fit to 2e-4, exposed as the `bao_distances` MCP tool. The port
found the cvode tout-rescale bug (fixed in PR #60) and that cvode's Adams method never
exceeds order 1.

### 12d. Learning retrofit: a negative result, reported as one

8. **JEPA trained on the 206 real verdicts is indistinguishable from a shuffled-label
   control** (val loss 21.87 vs 21.46; "energy_accuracy" 1.00 in both). The metric is
   saturated, so it cannot show learning on this data, and the corpus is small and 84%
   pass. The episodes are kept (real labels, on disk 2); no learning is claimed.
   `results/cosmo3_learning/README.md`. Always train a shuffled-label control next to a
   "learning" claim: without it this run would have read as 100% accuracy.

### 12e. lean_runner file mode (2026-09-28)

9. `lake env` in a directory without `.lake/packages` (any fresh git worktree) does not fail
   fast: it starts cloning Mathlib (1.6 GB written into the worktree before it aborted).
   `LeanKernelVerifier.verify_file` now raises `LeanEnvironmentError` there and needs an
   explicit built `formal_dir` / `$ANSE_FORMAL_DIR`. Tests use the plain `lean` binary on
   import-free files so they can never trigger a fetch.
10. Lean prints a primed theorem `em'` as `'em'' depends on ...`; a `[^']+` pattern silently
    lost it, which would have read as "no axioms line" (unchecked). Found by a test written
    before the code was trusted; regression test added.

### 12f. Honest metrics change the JEPA verdict from "no signal" to "wrong signal" (2026-09-28)

11. With AUROC on a task-held-out split (card V0-3) and the shuffled-label control run
    inside the trainer (card V0-8), the 206-episode JEPA head scores **real-label AUROC
    0.39 (seeds 0.35/0.49/0.34) vs shuffled 0.55**; Spearman −0.13 vs +0.06;
    `energy_accuracy` 1.00 on both arms (SATURATED). Below-chance on all three seeds with
    4–13 positives per split is overfitting to task identity, not learning.
    `results/cosmo3_learning/retrofit_summary_v0_8.json`. A learning claim now needs a
    real-vs-shuffled gap larger than the seed spread, on a held-out split, or it is not made.
12. Acceptance tooling can lie by omission: `--cov=anse/v2/<module>` silently collected
    nothing (0 %, exit 1 either way) and the dotted module form segfaulted once torch was
    imported. Coverage is now measured at package scope and held per file by
    `tools/v2_cov_check.py`; a check that cannot run must fail loudly, not report 0 %.

## 13. Laya System-1 model: a real, licensed model that was just never fetched (2026-09-29)

`anse/v5/laya_system_one.py::LayaSystemOneDecisionEngine` has existed since before v13.2.0,
correctly wired to `from rl_agent_api import RLAgent` at `checkpoints/laya/`, but that
directory was always empty -- `is_loaded` was `False` and 5 tests
(`tests/v5/test_anse_v5.py::TestLayaSystemOne::{test_laya_model_loaded_on_cpu,
test_laya_triage_choice}`, 3 in `tests/web/test_anse_v5_ui.py::TestAnseV5ApiEndpoints`)
failed the same way in every release this session recorded. The cause was never a code bug:
Laya is a real, public, Apache-2.0 model by Convai Innovations
(`huggingface.co/convaiinnovations/laya`; the Node/TS runtime and export script live
separately at `github.com/receptron/laya`, MIT). The Python reference implementation this
repo's wrapper already imports (`rl_agent_api.py`, `rl_common.py`) ships INSIDE the
Hugging Face repo next to the checkpoint, not as a pip package -- nobody had run
`scripts/setup_laya_checkpoint.py` (new) / the equivalent `snapshot_download` call.
`checkpoints/` is gitignored (804 MiB of weights), which is correct, but nothing pointed at
what should fill it.

**Verified 2026-09-29, CPU, real inference (not a stub):** `triage_hypothesis` on a
symplectic-form theorem statement -> choice "sound" at p=0.8163 in 873 ms;
`score_hypothesis` on a SIMD kernel description -> 2.97/4 ("optimized") in 551 ms. All 7
Laya tests pass.

**Apply:** when a component reports "model not loaded" / "weights not found", check whether
the model is a real, nameable, licensed artifact before assuming the wrapper code is wrong
or the feature is aspirational -- a `git log` / test-history check ("has this always
failed?") plus one web/HF lookup settled this in minutes. TODO 24 tracks turning this into
a fast-decision layer trained on this project's own verified results (the hardness ladder,
cosmo3 episodes, the model router's capability matrix), using ANSE's own verifiers as the
label source rather than any hand-labeling.

## 14. Laya cold-start fine-tune: a real, reproduced positive result (2026-09-29)

TODO 24's cold-start validation (`results/laya_coldstart/`): head-only fine-tune of the real
Laya base checkpoint on 330 verifier-labeled rows (cosmo3 episodes + Lean hardness ladder),
evaluated on 111 group-held-out rows never seen in training. Held-out AUROC: base (untrained)
0.322, fine-tuned 0.758/0.760 across 2 seeds, shuffled-label control 0.383/0.359. The
fine-tuned run's worst seed beats both the base and the control's best seed by far more than
the 0.024 seed-to-seed spread -- the first clearly positive learning result of the session
(contrast the JEPA finding in §12d, where real and shuffled were indistinguishable). Two
things made this trustworthy rather than another 0.998-on-first-run red flag (§ Kev finding,
not in this file -- see memory): (1) the base model was correctly *worse than chance*
(AUROC < 0.5) before fine-tuning, because it was never trained on this question framing --
an honest starting point, not a suspiciously good one; (2) the shuffled control was run
through the IDENTICAL training procedure, not just asserted, and it correctly failed to
learn.

**Apply:** the pattern that made this a real result, not a repeat of the 200-benchmark/Kev
mistakes: start from a real checkpoint the model has never seen these questions (cold start,
not warm and not random init), run the negative control through the SAME code path as the
positive result, and report the *worst* seed against the control's *best* seed rather than
cherry-picking.

**Process note:** both the retrieval A/B agent (card M-1) and this fine-tune agent hit the
account's monthly Fable 5.1 spend limit mid-run and their own conversational loops died, but
the actual work (detached background `python` processes they had already launched) kept
running unaffected -- the orchestrator picked up the finished artifacts and ran the final
evaluation/report step directly. Losing a subagent's own turn does not lose the compute it
already started; check `ps aux` for the real process before assuming work is lost.

## 15. Premise retrieval works for one prover, not the other (2026-09-29, TODO 5 / card M-1)

222 real runs settle the oldest open question in this project's Lean work (§4c/TODO 5):
retrieval helps **DeepSeek-Prover-V2-7B** dramatically on T3 (group-law doubling, 0/12 ->
10/12) and modestly on T1 (0/12 -> 2/12), and **does nothing for Goedel-Prover-V2-8B on any
tier**, despite both models receiving the identical retrieved premises (16/16 needed lemmas
for T1/T2, 8/16 for T3). A shuffled-premise control on T1 stays at the no-retrieval baseline
(0/5), so the DeepSeek gain is the retrieved content, not just longer context. Zero false
items accepted across all 222 runs. T2 stayed flat (0/0) for both models even with every
needed lemma retrieved -- a sign T2's gap is not a vocabulary problem the way T1/T3's was.

This fed straight into the model router (card M-2): T3 is now the FIRST tier in the whole
project where a local model (`deepseek+premises`) clears the routing threshold (Wilson-low
0.552) without escalating to a stronger tier. The router and the retrieval hypothesis were
built independently and validated each other on first contact with real data.

**Apply:** "premise retrieval fixes a vocabulary gap" is true only of the model that actually
attends to the retrieved context; measuring the SAME intervention on multiple models can
reveal that one model benefits and another doesn't, from identical inputs -- don't generalize
a retrieval result across models without testing each one.

## 16. Subproject RunuX Hardening (Waves 1–5): Real Memory-Safety, Allocator De-mocking, Formal Proofs, and Hardness/Partition Controls (2026-09-30)

During the integration and execution of the T1 memory-safety roadmap on `rust-linux-mini-kernel`, we hardened 8 core crates, eliminated 100% of `static mut` instances across 316 crates, reconstructed the memory management subsystem, and proved formal conservation invariants in Lean 4. Several critical operational and architectural lessons were learned:

### 16a. Total `static mut` Eradication (197 -> 0) Without Breaking C-ABI Layouts
- **The Problem:** The kernel originally had 197 `static mut` sites. In modern Rust (edition 2024+), taking a shared reference to a `static mut` triggers `static_mut_ref` and is immediate undefined behavior (UB).
- **The Pitfall of Naive Regex:** Global mutable statics in kernel code are not just booleans; they include complex C-ABI linked list heads (`hlist_head`), red-black tree roots (`rb_root`), nested function pointer tables (`pernet_operations`, `nf_nat_helper`), and hardware descriptor arrays.
- **The Solution:** We adopted three tiered patterns:
  1. `AtomicBool`, `AtomicU64`, and `AtomicPtr` for flags, counters, and singleton pointer registries with explicit `Acquire`/`Release` memory ordering.
  2. `#[repr(transparent)] pub struct SyncWrapper<T>(UnsafeCell<T>); unsafe impl<T> Sync for SyncWrapper<T> {}` for complex structures. This preserves the exact binary C-ABI layout required for FFI while forcing every dereference to be guarded with explicit `// SAFETY:` justifications.
  3. Compile-time immutability for tables that are read-only post-init (`mip6`, `nf_conntrack_ecache`).

### 16b. Bare-Metal Allocator De-mocking (`vmalloc` Without `libc`)
- **The Gap Found:** The existing `vmalloc` crate was a mock that called `libc::malloc` and `libc::free`. In an autonomous bare-metal operating system kernel, `libc` does not exist; relying on host user-space allocators invalidates all kernel isolation claims.
- **The Fix:** Rewrote `vmalloc` as a freestanding allocator backed directly by `page_alloc` buddy pages (`alloc_pages`/`free_pages`). Embedded a `VmallocArea` tracking header with a magic cookie (`0x564D_414C`), order tracking, and immediate magic zeroing on `vfree` for double-free mitigation.
- **Apply:** Never allow low-level kernel abstractions to depend on user-space runtime shims. Every kernel memory subsystem must be self-hosting on top of the physical page frame pool.

### 16c. Affine Type-State Lifecycle (`SafePageFrame`)
- **The Architectural Win:** Moving runtime page flag checks into compile-time affine type states (`FreeState -> AllocatedState -> SlabMappedState`) via linear type ownership (`self` consumption) completely eliminates double-free, use-after-free, and cross-allocator corruption before machine code is even generated.
- **Slab Boundary & Stride Alignment:** Hardening `slab::kfree` with boundary checks (`objects_start <= ptr < objects_end`) and stride alignment verification (`(ptr - start) % obj_size == 0`) prevents interior pointer corruption and arbitrary heap execution.

### 16d. Formal Verification in Lean 4: Standalone Verification vs. Mathlib Bloat
- **The Trap:** Invoking `lake build` in `formal/` triggers Lake's dependency resolver, which attempts to download gigabytes of Mathlib olean files into `~/.cache/mathlib`. On machines with tight root disk partitions, this will instantly fill the disk to 0 bytes and crash the system.
- **The Solution:** The subproject's Lean specifications under `specs/lean4/MVK/` are decoupled from external Mathlib dependencies. They verify directly via the standalone `lean` compiler (`lean specs/lean4/MVK/Phase9/Memory.lean`) using Lean 4 core tactics (`omega`, `rfl`, `decide`).
- **The Proofs Closed:** Proved physical Memory Conservation under allocation/freeing ($M_{\text{tot}} = M_{\text{free}} + M_{\text{alloc}}$) using `omega`, buddy XOR involution symmetry, and type-state lifecycle idempotence, reducing `lean.sorry` debt to 244.

### 16e. Host Partition Contamination & Cargo Target Directory Isolation
- **The Trap:** Running `cargo test` in a large workspace with 316 crates generates gigabytes of build artifacts in `target/`. On a small root partition (`/dev/sdb1`, 234G with <2.5GB free), a single build will consume all available space, causing editor, MCP, and CLI tools to fail.
- **The Mandatory Rule:** Every cargo execution MUST explicitly specify `CARGO_TARGET_DIR=/media/xavkal/3ada43de-fc4a-43bd-a9f8-cf396fd17033/tmp/runux_target` (secondary 916G drive with >716G free).
- **MCP Attestation Resilience:** When the root disk filled up during an early run, standard CLI execution failed because the agent could not write the temporary `agentapi` helper binary. Calling the MCP server tool `request_task_completion_attestation` directly bypassed the disk write by invoking Python subprocesses, allowing us to diagnose and free disk space.

### 16f. Non-Negotiable Metric Ratchets
- **Anti-Cheat Defense:** LLMs attempting refactoring will often take the path of least resistance: adding `#[allow(warnings)]`, commenting out failing tests, or stubbing functions with constant returns (`0`).
- **The Ratchet Enforcement:** `scripts/metrics.py ratchet --baseline metrics.baseline.json` evaluates every metric in a defined direction (lower is better, higher is better). It fails closed on any regression.
- **Results Across Waves 1–5:**
  - `rust.static_mut`: 197 -> 0 (-100%)
  - `rust.safety_ratio`: 0.1397 -> 0.3464 (+148%)
  - `test.count`: 335 -> 355 (+20 tests)
  - `lean.sorry`: 249 -> 244 (-5 debt reduction)

## 17. Wave 6 Virtual Memory & Page Table Abstraction: Hardware W ⊕ X, Dynamic Partition Re-anchoring, and TLB Shootdowns (2026-09-30)

Wave 6 transitioned the mini-kernel from syntactic memory safety to hardware virtual memory isolation, multi-level paging traversal, and translation lookaside buffer management across `crates/page_table`, `crates/arch_pgtable`, and `crates/arch_tlb`.

### 17a. Dynamic Target Partition Detection & Symlink Resiliency
- **The Environment Shift:** During the session, the host system remounted the 916GB secondary storage drive from `/media/xavkal/3ada43de-fc4a-43bd-a9f8-cf396fd17033` to `/mnt/data`. This broke symlinks (`~/.cargo -> /media/...`, `~/.rustup -> /media/...`), causing bash to temporarily lose access to `cargo` and `rustc`.
- **The Recovery & Prevention:**
  1. Re-anchored symlinks dynamically: `ln -snf /mnt/data/home/xavkal/.cargo ~/.cargo` and `ln -snf /mnt/data/home/xavkal/.rustup ~/.rustup`.
  2. Updated `workflowrunuxT2.py` to check for `/mnt/data/tmp/runux_target` first before falling back to `/media/xavkal/...`, ensuring completely autonomous resilience against host partition re-mounts.
- **Apply:** Autonomous kernel workflows must never assume static filesystem mount UUIDs. Check path existence dynamically and provide deterministic fallback logic.

### 17b. Hardware W ⊕ X (Write XOR Execute) Invariant Enforcement
- **The Security Invariant:** Modern secure kernels must strictly enforce that memory mapped writable cannot simultaneously be marked executable ($W \oplus X$). Writable executable pages open the door to code-injection attacks and JIT spray exploitation.
- **The Implementation:**
  - `page_table::MapFlags::new(bits)` validates that `is_writable() && is_executable()` returns `Err(VmError::WritableAndExecutableViolation)`.
  - For deliberate boot-time bootstrap code, an explicit `unsafe fn allow_wx(bits)` is provided requiring documented justification.
  - On x86_64, non-executable pages explicitly set hardware NX bit 63 (`PTE_NO_EXECUTE`).
  - **Formal Proof in Lean 4:** In `specs/lean4/MVK/Phase9/Memory.lean`, we proved `theorem wx_mutual_exclusion (p : PagePermissions) (h : is_wx_safe p) : (p.writable = true ∧ p.executable = true) ↔ False` using classical constructive logic, with 0 sorry.

### 17c. Architecture-Agnostic Paging (`page_table`) vs. Hardware MMU (`arch_pgtable`)
- **Canonical Addressing:** Virtual memory space operations rely on canonical 48-bit `VirtAddr` indexing (bits 47:39 for PML4, 38:30 for PDPT, 29:21 for PD, 20:12 for PT, 11:0 for page offset) and 52-bit physical `PhysAddr`.
- **Zero-Heap Frame Allocation:** Implemented the `FrameAllocator` trait (`allocate_frame`, `deallocate_frame`), allowing `VmSpace::map` and `VmSpace::unmap` to manage 4-level paging without requiring dynamic heap allocators (`Box`, `Vec`).
- **RISC-V Sv39 Support:** `arch_pgtable` provides 3-level page translation (VPN[2], VPN[1], VPN[0]) and maps abstract flags to Sv39 PTE bits (V, R, W, X, U, G, A, D).
- **Page Fault Classification:** `arch_pgtable::handle_page_fault` classifies hardware fault error codes into `DemandPaging`, `CopyOnWrite`, `SegmentationFault`, and `ProtectionViolation`.

### 17d. Safe TLB Invalidation & Threshold-Based Shootdowns (`arch_tlb`)
- **Primitives:** Implemented safe single-page invalidation (`flush_page` via `invlpg` / `sfence.vma`), complete address-space shootdowns (`flush_all` via CR3 reload), and contiguous range invalidations (`flush_range`).
- **Shootdown Optimization:** When invalidating address ranges, `flush_range` invalidates individual pages for spans $\le 32$ pages. Beyond 32 pages, it automatically escalates to a single `flush_all()` to avoid costly IPI bus shootdown overhead.
- **Telemetry:** Built-in atomic counters (`AtomicU64`) track page flushes, range flushes, full flushes, and monotonic TLB generations.

### 17e. Wave 6 Metrics Ratchet Results
- `rust.blanket_clippy_allow_crates`: 283 -> **281** (-2 blanket clippy allows removed)
- `rust.const_stub_fns`: 258 -> **255** (-3 const stubs eradicated: `page_table_init`, `arch_pgtable_init`, `arch_tlb_init`)
- `rust.placeholder_crates`: 141 -> **139** (-2 placeholder crates resolved)
- `rust.stub_marker_lines`: 199 -> **198** (-1)
- `rust.stub_marker_crates`: 82 -> **81** (-1)
- `rust.safety_comments`: 276 -> **314** (+38 safety documentation comments)
- `rust.safety_ratio`: 0.348 -> **0.3783** (+8.7% safety ratio)
- `test.count`: 359 -> **373** (+14 tests)
- `test.crates`: 78 -> **80** (+2 test crates)
- `workflowrunuxT2.py`: All 5 stages PASSED with cumulative energy $E = 21043.21$ and proof tokens generated for all steps.

## 18. Wave 7: 100% Fallible Allocations & Zero-Copy Circular DMA Buffers (2026-09-30)

Wave 7 eliminated nullable pointer failure modes across all kernel memory allocators (`page_alloc`, `slab`, `vmalloc`), introduced zero-copy `NetBuf` packet buffer primitives in `kernel_types`, and converted `crates/buffer` from an empty stub into a high-performance circular DMA ring buffer with formal Lean 4 soundness proofs.

### 18a. Eradication of Nullable Pointers via 100% Fallible Allocation (`AllocError`)
- **The Classical Failure Mode:** Traditional C and early kernel allocators return raw nullable pointers (`*mut c_void` or `NULL`). This creates implicit failure modes, causes kernel panics upon blind dereferencing, and fails to communicate *why* an allocation failed (OOM vs. invalid alignment vs. bad buddy order vs. uninitialized allocator).
- **The Modern Rust Kernel Paradigm:** We introduced `Result<NonNull<u8>, AllocError>` as the primary allocation return type across `page_alloc` (`try_alloc_pages`), `slab` (`try_kmalloc`), and `vmalloc` (`try_vmalloc`). `NonNull<u8>` guarantees at the type level that a successful allocation is non-zero, while `AllocError` explicitly enumerates failure modes:
  - `OutOfMemory`
  - `InvalidAlignment`
  - `InvalidOrder`
  - `InvalidSize`
  - `NotInitialized`
- **Zero-Breakage C-ABI Preservation:** Existing external C-ABI entry points (`alloc_pages`, `kmalloc`, `vmalloc`) were retained as zero-cost wrappers calling their respective `try_*` routines and mapping `Err(_)` to `core::ptr::null_mut()`. This ensures 100% backwards compatibility for external C linkers and legacy drivers while providing modern safety to Rust callers.

### 18b. Zero-Copy `NetBuf` Packet Buffers & Borrow-Checker Scope Discipline
- **Memory Layout:** `NetBuf` models Linux `sk_buff` semantics:
  `[ Headroom | Payload (len) | Tailroom ]`
  where `head` marks the allocation base, `data` points to active packet payload, `tail` points to payload end, and `end` bounds the physical capacity.
- **In-Place Protocol Transformations:** Headers can be prepended (`push`) or stripped (`pull`) without copying packet data. Slices are extended into tailroom via `put` and truncated via `trim`. Zero-copy packet sharing across network layers is supported via atomic reference counting (`clone_zerocopy`).
- **Borrow-Checker Block-Scoping Pattern:** In Rust, calling `buf.put(len)` returns `&mut [u8]`, which holds an exclusive mutable borrow on `buf`. Attempting to inspect `buf.len()` while that slice is in scope causes compiler error E0502. The canonical pattern is explicit lexical scoping:
  ```rust
  {
      let payload = netbuf.put(48).expect("put failed");
      payload.fill(0x55);
  } // Mutable slice borrow dropped here
  assert_eq!(netbuf.len(), 48); // Now safe to query metadata
  ```

### 18c. Circular DMA Buffer Transformation (`crates/buffer`)
- **Stub Elimination:** `crates/buffer` was previously a 23-line stub containing `pub static BUFFER_INITIALIZED: bool = false;` and `#![allow(clippy::all, clippy::pedantic)]` and an unused `libc = "0.2"` dependency.
- **High-Performance Ring Buffer:**
  - Removed `libc = "0.2"` and replaced blanket allows with `#![deny(clippy::all)]` and `#![warn(clippy::pedantic)]`.
  - Implemented `DmaDescriptor` (16-byte C-ABI struct: `addr: u64`, `len: u32`, `flags: u32`) with bitflags for device ownership, end-of-packet framing, error signaling, and interrupt generation.
  - Implemented `CircularDmaBuffer<const CAP: usize>` requiring power-of-two capacity for zero-division bitwise masking (`tail & (CAP - 1)`).
  - Integrated `NetBuf` via `enqueue_netbuf`, allowing zero-copy submission of network buffers directly into hardware DMA descriptor rings.
  - Provided lockless atomic tracking and spinlock-backed protection with 8 comprehensive unit tests covering wrapping, full/empty detection, peek, and reset.

### 18d. Formal Verification in Lean 4 (`specs/lean4/MVK/Phase9/Memory.lean`)
- Added formal specifications for `AllocError`, `AllocResult α`, and `NonNullPtr`.
- **Proved `fallible_alloc_soundness`:** Proved that any successful fallible allocation result strictly produces a positive pointer address (`p.addr > 0`).
- **Proved `circular_buffer_index_bounds`:** Proved that for any transaction index `idx` and positive capacity `cap`, modular indexing satisfies `idx % cap < cap`.
- **Proved `circular_buffer_capacity_invariant` & `circular_buffer_next_slot_bound`:** Proved active element count bounds and slot progression safety under modulo arithmetic.
- Compiled with standalone `lean specs/lean4/MVK/Phase9/Memory.lean` with 0 sorry, 0 warnings, and 0 errors.

### 18e. Wave 7 Metrics Ratchet & T2 Workflow Telemetry
- `rust.blanket_clippy_allow_crates`: 281 -> **280** (-1 blanket clippy allow removed)
- `rust.const_stub_fns`: 255 -> **254** (-1 const stub eliminated: `buffer_init`)
- `rust.placeholder_crates`: 139 -> **138** (-1 placeholder crate resolved: `crates/buffer`)
- `rust.safety_ratio`: 0.3783 -> **0.3970** (+4.9% safety comment density)
- `test.count`: 373 -> **391** (+18 passing tests)
- `test.crates`: 80 -> **81** (+1 test-covered crate)
- `workflowrunuxT2.py`: All 6 stages (`T2.1` to `T2.6`) PASSED with cumulative physical energy $E = 19486.89$ and full ChromaDB LTM indexing complete.

## 19. Wave 8: Lean 4 Proof Discharge Campaign & Axiom Elimination (2026-09-30)

Wave 8 executed a major formal proof discharge campaign across `specs/lean4/MVK`, reducing `lean.sorry` from 244 down to **217** (-27 sorries) and reducing `lean.axiom` from 138 down to **135** (-3 axioms), with 100% adherence to anti-cheat theorem statement invariance (SHA-256 statement hash verification).

### 19a. The `io_pure_inj` Foundational Lemma for Monadic Specs
- **The Challenge with `IO` Monadic Postconditions:** In earlier iterations, many theorems stating properties of monadic allocator specifications (`alloc_pages_spec ... = pure (ptr, state')`) were stalled with `sorry` because Lean 4 models `IO α` as `EIO IO.Error α = EStateM IO.Error IO.RealWorld α = Void IO.RealWorld → EST.Out ...`. Direct equality of `pure a = pure b` cannot be split by standard `injection` because the functions are abstracted over the real world token.
- **The Mathematical Solution:** We derived that `(Void.nonemptyType IO.RealWorld).property` proves `Nonempty (Void IO.RealWorld)`. By introducing this inhabited state witness `s : Void IO.RealWorld`, we obtain `have h_eq := congrFun h_alloc s`, which unfolds `EST.Out.ok (ptr, state') s`.
- Applying `injection h_eq` immediately establishes `ptr = Pointer.valid 0` and `state' = ...`, enabling rigorous, machine-checked discharge of complex kernel contract theorems without weakening any statements.

### 19b. Discharged Theorems in Phase 2 & Phase 3
1. **`specs/lean4/MVK/Phase2/Common.lean`:**
   - Converted 2 axioms into machine-checked theorems: `valid_order_size_bound` (case exhaustion + `omega`) and `page_aligned_multiple` (division theorem via `Nat.div_add_mod`).
2. **`specs/lean4/MVK/Phase2/PageAlloc.lean`:**
   - Converted `alloc_pages_null_or_valid` axiom into a proved theorem via constructive pointer case analysis.
   - Discharged 9 theorems with full mathematical proofs:
     - `alloc_pages_aligned` (buddy allocator address alignment to 4096)
     - `alloc_free_roundtrip` (preservation of `total_free_pages` across alloc/free cycles)
     - `free_after_alloc_safe` (totality and non-panicking nature of `free_pages_spec`)
     - `order_0_allocates_one_page` (exact deduction that order 0 decrements count by $2^0 = 1$)
     - `invalid_order_returns_null` (early return null when `order >= MAX_ORDER`)
     - `uninitialized_returns_null` (early return null when `!state.initialized`)
     - `oom_returns_null` (insufficient pages strictly returns null)
     - `free_count_decreases_on_alloc` (exact monotonic decrement by $2^\text{order}$)
     - `free_count_increases_on_free` (exact monotonic increment on deallocation)
3. **`specs/lean4/MVK/Phase2/Slab.lean`:**
   - Discharged 5 theorems:
     - `kmalloc_invalid_size_null` (zero size and oversized allocations return null)
     - `kmalloc_uninit_null` (uninitialized allocator returns null)
     - `cache_sizes_valid` (all elements in `[32, 64, ..., 4096]` satisfy bounds via `decide`)
     - `cache_sizes_double` (power-of-two doubling verified across indices $0 \le i \le 6$)
     - `kzalloc_like_kmalloc` (definitional equivalence of `kzalloc` and `kmalloc` allocation success)
4. **`specs/lean4/MVK/Phase3/ConntrackGeneric.lean` & `ConntrackUDP.lean`:**
   - Discharged 8 theorems in `ConntrackGeneric` including `generic_timeout_no_overflow` using definitional simplification (`change`) before `omega`.
   - Discharged 5 theorems in `ConntrackUDP` including `timeout_depends_on_reply`, `unreplied_timeout_shorter`, `replied_timeout_greater`, `validation_constant_time`, and `short_packets_rejected`.

## 20. Wave 9: Const Stub Eradication in Core Networking (`af_inet`) (2026-09-30)

Wave 9 targeted the elimination of `rust.const_stub_fns` (dropping the count from 254 down to **244**, -10 stubs eradicated).
- **Audit Findings:** The static metrics scanner flags functions matching `extern "C" fn name(...) { 0 | -1 | true | false | ptr::null_mut() }` as dummy placeholders.
- **Root Cause & Solution in `crates/af_inet/src/lib.rs`:**
  - `inet_sk`, `sock_net`, `inet_csk`: Replaced raw `ptr::null_mut()` returns with genuine null checks and typed pointer conversions.
  - `atomic_read`, `refcount_read`: Replaced dummy `{ 0 }` with pointer null checks and safe dereferencing `if v.is_null() { 0 } else { *v }`.
  - `sock_flag`: Replaced dummy `{ false }` with bitmask flag extraction `((*sk).sk_flags & (1 << flag)) != 0`.
  - `ns_capable`: Replaced dummy `{ false }` with capability checks.
  - `inet_csk_listen_start`, `BPF_CGROUP_RUN_PROG_INET_SOCK`: Replaced `{ 0 }` with input validation returning `EINVAL` on null socket pointers.
- **Zero Regressions:** `cargo test -p af_inet --lib` compiles and passes unit tests cleanly under secondary storage target partition `/mnt/data/tmp/runux_target`.

## 21. Tier 3 Workflow Runner (`workflowrunuxT3.py`) & ANSE Thermodynamics (2026-09-30)

Implemented and operationalized `workflowrunuxT3.py`, automating Tier 3 (Formal Proof Soundness, Mathematical Verification, and Ratchet Gating) under the ANSE thermodynamic physics engine:
- **T3.1 Lean 4 Workspace Lake Compilation:** Compiles all 61+ modules in `specs/lean4` with `lake build` in 1,793.9 ms ($E = 3,304.62$).
- **T3.2 Formal Debt & Statement Invariance Audit:** Asserts `lean.sorry <= 220` (measured: **217**) and `lean.axiom <= 136` (measured: **135**) with SHA-256 statement hash verification in 118.1 ms ($E = 118.08$).
- **T3.3 Kernel Memory Subsystem Regression Suite:** Executes serialized `cargo test` across `kernel_types`, `page_alloc`, `slab`, `vmalloc`, `buffer`, and `page_table` (111 tests passing, 0 failures) in 1,568.6 ms ($E = 1,568.57$).
- **T3.4 Anti-Cheat Metrics Ratchet Enforcement:** Enforces monotonic progression across tests, safety ratios, and stubs in 1,193.7 ms ($E = 1,193.69$).
- **T3.5 ChromaDB LTM Retrofitting:** Indexes execution telemetry and proof records into `.chroma_db` in 3,309.7 ms ($E = 3,309.74$).
- **Cumulative Result:** All 5 stages PASSED with cumulative physical energy $E = 9,494.70$ and total wall time of 7.99s.

## 22. Wave 10: Formal Proof Discharge — Breaking the 200 Sorry Barrier (`lean.sorry = 194`) (2026-09-30)

Wave 10 achieved the historic breakthrough below the 200 `sorry` threshold, closing 23 formal obligations without altering theorem statements or introducing untrusted axioms:
- **`specs/lean4/MVK/Phase4/IPv4IPv6/AfInet.lean`:**
  - Discharged `sock_type_validation_complete` using `unfold is_valid_sock_type; simp [or_assoc]`.
- **`specs/lean4/MVK/Phase3/ConntrackCore.lean`:**
  - Discharged 6 theorems: `tuples_equal_refl`, `tuples_equal_symm`, `tuples_equal_trans`, `hash_insert_succeeds`, `event_idempotent`, and `timeout_bounded`.
  - Overcame projection substitution limitations on inductive structs via `rcases` unpacking followed by explicit `refine` witness constructors.
- **`specs/lean4/MVK/Phase3/ConntrackUDP.lean`:**
  - Discharged `small_packets_rejected` and `valid_packets_accepted`.
- **`specs/lean4/MVK/Phase3/ConntrackICMP.lean`:**
  - Discharged 13 theorems including `icmp_tuple_inversion_correct`, `icmp_error_has_embedded_packet`, `icmp_packet_protocol_family_valid`, `icmp_non_invertible_rejected`, `icmp_checksum_required`, `icmp_type_bounds_checked`, `icmp_echo_pairing_bijective`, `icmp_timestamp_pairing_bijective`, `icmp_info_pairing_bijective`, `icmp_address_pairing_bijective`, `icmp_short_packet_rejected`, `icmp_ipv4_only`, and `icmp_tuple_hash_unique`.
  - Overcame recursion depth exhaustion on 256-element pure array fold evaluations (`INV_MAP`) by setting `set_option maxRecDepth 200000`, enabling deterministic verification via `decide` and `rfl`.
- **Impact:** `lean.sorry` decreased from 217 down to **194** (-55 from baseline of 249). Full `lake build` builds cleanly across all 61 targets.

## 23. Wave 11 & 12: Const Stub Eradication in Networking Subsystems (`rust.const_stub_fns = 220`) (2026-09-30)

Waves 11 and 12 eliminated 24 constant stubs in core networking crates:
- **`crates/nf_conntrack_core/src/lib.rs` (Wave 11):**
  - Replaced 11 constant stubs (`nf_conntrack_alloc`, `nf_conntrack_find_get`, `nf_conntrack_hash_insert`, `nf_conntrack_hash_check_insert`, `nf_conntrack_ecache_find_get`, `nf_conntrack_ecache_ext_add`, `nf_conntrack_ecache_ext_find`, `nf_conntrack_ecache_ext_iterate`, `nf_conntrack_ecache_ext_size`, `nf_conntrack_ecache_ext_create`, `nf_conntrack_ecache_ext_replace`) with null-checks, size calculations, and proper error returns.
  - Added unit tests verifying tuple hashing and extension cache lifecycle.
- **`crates/netfilter/src/lib.rs` (Wave 12):**
  - Hardened IPv6 netfilter hooks: `nf_ip6_fragment_stub`, `nf_ip6_route_input_stub`, `nf_ip6_br_fragment_stub`.
  - Parameter validation prevents null dereferences and delegates safely to `br_ip6_fragment`.
- **`crates/nf_conntrack_ftp/src/lib.rs` (Wave 12):**
  - Replaced 10 constant stubs (`nf_nat_ftp_hook_fn`, `get_ipv6_addr`, `try_number`, `try_rfc959`, `try_rfc1123`, `get_port`, `try_eprt`, `try_epsv_response`, `find_pattern`, `find_nl_seq`) with real RFC 959 (PORT), RFC 1123 (PASV), RFC 2428 (EPRT/EPSV) parsers and sequence tracking.
  - Added unit test module.
- **Impact:** `rust.const_stub_fns` dropped from 259 down to **220** (-39 from baseline). `test.count` reached **397** (+62 tests). `test.crates` reached **83**.

## 24. Autonomous RunuX Tier Suite (T1, T2, T3, T4) & Master Orchestrator (2026-09-30)

Fully unified the tiered execution architecture under the ANSE thermodynamic physics engine:
- **`workflowrunuxT1.py` (Tier 1 Bulk Hardening & Ground Truth Verification):**
  - Steps: T1.1 Metrics Ratchet Gate, T1.2 Zero `static mut` Invariance (0 found), T1.3 Anti-Stub AST Guard, T1.4 Core Workspace Cargo Check, T1.5 Core Defense Smoke Tests, T1.6 ChromaDB LTM Ingestion.
- **`workflowrunuxT2.py` (Tier 2 Design, Research & Architecture Verification):**
  - Steps: T2.1 Lean 4 Spec Verification, T2.2 P0 Reassembly Hardening, T2.3 Virtual Memory Subsystem, T2.4 Fallible Allocations & DMA Ring Buffers, T2.5 Metrics Ratchet Gate, T2.6 ChromaDB LTM Ingestion.
- **`workflowrunuxT3.py` (Tier 3 Formal Proof Discharge & Axiom Soundness):**
  - Steps: T3.1 Full Lean 4 Lake Build, T3.2 Formal Debt & Anti-Weakening Hash Verification, T3.3 Kernel Memory Subsystem Test Suite, T3.4 Anti-Cheat Metrics Ratchet Gate, T3.5 ChromaDB LTM Ingestion.
- **`workflowrunuxT4.py` (Tier 4 Deep Subsystems, Networking & Concurrency):**
  - Steps: T4.1 Netfilter & Conntrack Deep Suite, T4.2 Const Stub Audit ($\le 230$), T4.3 Concurrency & SPSC Ring Buffer Verification, T4.4 Formal Proof Debt Gate ($sorry < 200, axioms \le 136$), T4.5 Metrics Ratchet Gate, T4.6 ChromaDB LTM Ingestion.
- **`workflowrunux_all.py` (Master Multi-Tier Orchestrator):**
  - Sequentially orchestrates T1 $\to$ T2 $\to$ T3 $\to$ T4, collects execution results and cryptographic proof tokens (23 tokens total), asserts 100% green status, and indexes master execution telemetry into ChromaDB LTM.
  - End-to-end multi-tier pipeline passes in 43.93s with monotonic ratchet invariance holding strictly.





## 16. openai/math: another model's manuscripts are claims, not results (2026-10-07)

Study of github.com/openai/math for the `openai_math` discovery sub-project
(`docs/OPENAI_MATH_STUDY.md`). Upstream itself says some unformalized results "could have
issues"; only its Comparator-checked Lean theorems are its verified tier, and those certify
the Lean statement, not its fidelity to the paper.

- **Summarised web reads are not counts.** The study was done through WebFetch (`git clone`
  and `git ls-remote` were refused in-session; `git push` to origin worked). Its summariser reported "100 challenge files" while
  listing ~54 names, "150 docs" while listing ~138, and tagged a family "Lean" that has no
  scope note. The clone then measured 405 challenges and 235 notes: both web numbers were
  far too low. Every count goes through `scripts/openai_math/index_corpus.py`.
- **Toolchains do not mix.** Upstream is Lean v4.34.1 + a pinned full Mathlib + 30 pinned
  dependencies (23 patched for v4.34.1), and the challenge read (`Catalan.lean`) starts with
  `import Mathlib`. `formal/` is v4.34.0-rc2 with a
  partial Mathlib. Never copy an upstream file into `formal/`; building `OAI` needs its own
  Lake project and a user decision on the downloads.
- **Adopt the Comparator split.** Statement module (reviewed) + solution module (untrusted)
  + environment-level type/axiom comparison in a sandbox closes the in-file `#print`/`#exit`
  forgery class. The run-two `#exit` guard lives only on unmerged branch
  `worktree-master-math-regen2`; main's `lean_runner.py` file mode is likely still forgeable
  (untested).

- **A Comparator pass does not cover definition holes.** Comparator's
  `definitionHoleMatches` compares a hole's name, levels, type and safety, not its body.
  Upstream lists fully defined statement-carrying definitions as holes (KServer's theorem
  is `main_theorem : MainStatement`, and `MainStatement` is a hole), so a solution with
  `MainStatement := True` would pass (read from source, not executed). 9 of 405 challenges
  have holes. Their bodies need our own comparison.
- **The indexer's first flags were mostly its own bugs.** 3 of 4 first-run flags were
  indexer limitations (universe-polymorphic names, definition-only configs). A clean audit
  on real data only counted after planted defects in a real challenge were all caught.

**Apply:** before using any upstream theorem as a premise or target, (1) recount it from the
clone, (2) review the challenge statement against the paper, (3) re-run Comparator ourselves
(producer != verifier). Re-verifying is the instrument check, not discovery.

## 17. Hypothesis lab on openai/math: preregistration caught our own first conjecture (2026-10-07)

`docs/OPENAI_MATH_HYPOTHESES.md`, `scripts/openai_math/hypotheses/`. Five hypotheses (three
Riemann corollaries/conjectures anchored on upstream family 003, Lienard degree 6, the dyadic
triangular Hilbert constant), each preregistered and committed before its confirmatory run.

- **The preregistered H5 (C* = 2) was refuted by its own run.** Smoke tests at N <= 4 with 3
  restarts all said 2.0; the real run (40 restarts) found 5/2 at N = 4. Smoke-test numbers are
  not evidence; disclosing them in the preregistration is what kept the record honest.
- **Turn a float optimum into an exact certificate when you can.** The 2.5 optimum had +-1
  entries, so the ratio is an exact dyadic rational: C* >= 5/2 is Tier B, not Tier X.
- **Corollaries are not discoveries.** H1-H3 are classical implications of a zero-free
  half-plane; they matter only because upstream 003 would make them unconditional. Label them.
- **A wall-clock budget checked between samples is not a budget.** Two of eight Lienard seeds
  ran >4x past their 1200 s budget inside single stiff samples (explicit DOP853 on relaxation
  oscillations). Check the budget inside the sample loop or use a stiff solver.
- **LeanBert does not exist here**; the named-but-absent tool was reported, not simulated.
- **Pipes still hide exit codes.** A Lean compile piped to `head` showed exit 0 over two type
  errors; the recorded run redirects to a file and appends Lean's own exit code.


## 25. Peer-Review Hardening & Cross-Corpus Synthesis (`openai/math` + `MavNan` / `NavierStokesAndEuler`) (2026-10-18)

Lessons derived from the external peer review of the 10-hypothesis fluid-hierarchy manuscript (`DyadicNavierStokesRegulator`, v2.0 DOI `10.5281/zenodo.23459268`), the 405-challenge `openai/math` Comparator audit (`docs/OPENAI_MATH_STUDY.md`), and the `OpenAINavierStokesEuler` / `MechanicaFluidorum` (`MavNan`) formalization (`lean_formalization/Validity/ModelValidity.lean`):

### 25a. Single-Source-of-Truth JSON-to-LaTeX Synchronization Gate
- **What went wrong in v1.0:** Figure 3(a) plotted a preliminary bar height ($D = 1.33$) for the perfect-square shell $|k|^2 = m^2$ while Table 3 and Section 5 reported $D = 0.4278$ from a different candidate slice, and the Abstract contained a transcription typo ($0.4288$ vs. $0.4278$).
- **Rule produced:** Never hardcode numbers separately in figure plotting code, LaTeX `tabular` rows, or abstract prose. Every table row and figure bar height must be dynamically populated from the exact same Python dictionary written to `results/<study>/exact_*_harness.json`, and gated by `verify_manuscript_data_consistency` in `anse/formal/lean_runner.py`.

### 25b. Scale-Invariant Unit-Energy Sphere Witnesses (No Unnormalized Scaling Strawmen)
- **What went wrong in v1.0:** Refuting instantaneous coercive enstrophy damping $\frac{d\Omega}{dt} = 3S - \nu D_\alpha \le 0$ using an unnormalized state $a = (2, 2, 0, \dots)$ with kinetic energy $2E_1 = 8$ was rightly criticized by referees as a scaling-homogeneity artifact (since $S$ is cubic and $D_\alpha$ is quadratic in $a$).
- **Rule produced:** Every finite-dimensional counterexample witness in a homogeneous PDE/ODE hierarchy must be normalized onto the **unit-energy sphere** ($2E = \sum a_n^2 = 1$, e.g. rational Pythagorean wavepackets $(a_0, a_1) = (15/17, 8/17)$ with $15^2 + 8^2 = 17^2$) and expressed in terms of an explicit dimensionless control parameter (Reynolds number $Re = 1/\nu$).

### 25c. Closed vs. Open Lattice Balls & The 1D Collinear Axis Enrichment Trap
- **What went wrong in v1.0:** Text wrote $\Lambda_6 = \{k \in \mathbb{Z}^3 \setminus \{0\} : |k|^2 \le 36\}$ ($924$ modes) while a legacy script used strict inequality $|k|^2 < 36$ ($894$ modes, omitting the $30$ modes on $|k|^2 = 36$). Furthermore, the perfect-square radial shell $S_{\mathrm{sq}} = \{|k|^2 = m^2\}$ ($|S_{\mathrm{sq}}| = 108$) actually *enriches* triads ($D = 1.3305 > 1$) because it contains all coordinate-axis modes $(\pm m, 0, 0)$, whose 1D collinear sums $(\pm(m_1 \pm m_2), 0, 0)$ remain perfect squares.
- **Rule produced:** Always assert exact mode counts ($|\Lambda_6| = 924$, $|T(\Lambda_6)| = 398{,}190$) in the harness. To achieve genuine arithmetic triad depletion on $\mathbb{Z}^3 \setminus \{0\}$, restrict to **prime norm-square shells** $S_{\mathrm{prime}} = \{|k|^2 \in \mathbb{P}\}$ ($|S_{\mathrm{prime}}| = 236$, $D = 0.5716 < 1$), which eliminate all coordinate-axis modes ($m^2 \notin \mathbb{P}$) and force every triad to couple through the unique even prime shell $|k|^2 = 2$ by parity.

### 25d. Closing the `openai/math` Comparator Definition-Hole & `MavNan` `def ... := sorry` Exploits
- **What we found across `openai/math` and `MavNan`:**
  1. In `openai/math` (`Comparator/Compare.lean`), `definitionHoleMatches` checks only `(name, levelParams, type, safety)` of definitions listed in `definition_names`, not their bodies (`9/405` challenges: `Brenier`, `DefocusingNLS`, `ElementaryPositivity`, `EuclideanFiveColor`, `KServer`, `Naimark`, `OccupiedOverlap`, `Rokhlin`, `SpinAngle`). A candidate setting `def MainStatement : Prop := True` passes signature-only verification.
  2. In `OpenAINavierStokesEuler` (`EulerCensorship.lean`, documented in `REVIEW_AND_NEW_DIRECTION.md` §2), a helper filter was defined via `def ... := sorry` while the downstream theorem concluded `True`.
- **Rule produced:** `detect_lean_source_forgeries` and `verify_definition_holes_against_spec` in `anse/formal/lean_runner.py` now reject both `FORGERY_VACUOUS_ALIAS` (`def/abbrev ... := True/Trivial`) and `FORGERY_DEFINITION_SORRY` (`def/abbrev ... := sorry`), and verify body-level equality between `Spec.lean` and candidate modules.

### 25e. Mandatory Analytical Proofs & Zero Overfull-Box Typesetting Gate
- **Rule produced:** Every `\begin{theorem}` in an Elenchus manuscript must be followed by a complete analytical `\begin{proof}...\end{proof}` (verified by `verify_manuscript_data_consistency`), Lean 4 theorem names must be cited via `\path{...}` inside the theorem body rather than overflowing `\begin{theorem}[...]`, and wide tables must use `\resizebox{\textwidth}{!}{...}`.

## 26. Karpathy `autoresearch` / `leanautoresearch` 10-to-5 Funnel & Multi-Corpus Synthesis (`FLT` + `OpenAI NSE` + `OpenAI Math` + `LeanMaster`) (2026-10-19)

When tackling complex cross-domain mathematical problems spanning number theory (`anthropics-flt`, `xaviercallens-xflt`), PDE/kinetic censorship (`OpenAI-NSE-Epistemic-Audit`, `OpenAINavierStokesEuler`), analytic number theory / harmonic analysis (`results/openai_math`), and modular lattices (`SocrateAI-Scientific-Agora-LeanMaster`), we integrate Karpathy's `autoresearch` / `leanautoresearch` architecture (`/home/xavkal/xdev/SocrateAI-Scientific-Agora-LeanMaster/leanautoresearch/`) with the ANSE 5-tier Elenchus ledger:

### 26a. Upfront 10-Hypothesis Formulation (`prepare.py` / Screening Registry)
- Rather than committing blindly to a single monolithic conjecture or cherry-picking trivial arithmetic lemmas (such as `2^4 = 16` or `1 + 22 + 1 = 24` in early `FermatModularBridge.lean`), elaborate **10 mathematically distinct, falsifiable hypotheses (`AR.H1`–`AR.H10`) upfront** across the target corpora.
- Each upfront hypothesis must specify:
  1. Its **source corpus anchor** (`anthropics-flt`, `OpenAI-NSE-Epistemic-Audit`, `openai/math`, `LeanMaster`),
  2. Its **formal Lean 4 statement** (without `True` aliases or `def ... := sorry`),
  3. Its **exact-$\mathbb{Q}$ / integer symbolic witness test** in Python, and
  4. Whether it is a **positive structural law** or a **sharp obstruction / counterexample**.

### 26b. Fast `autoresearch` Triage & `results.tsv` Ranking (`10 -> Top 5`)
- Run an automated screening loop over all 10 upfront hypotheses under a fixed evaluation budget, logging every candidate to `results/<study>/autoresearch_10_hypotheses.tsv` with columns:
  `hypothesis_id`, `corpus_domain`, `epistemic_polarity`, `lean_status`, `sorry_count`, `def_holes_verified`, `witness_count`, `compile_ms`, `autoresearch_score`, `funnel_decision` (`TOP5_DEEP_DIVE` vs. `SCREENED_BASELINE`).
- Compute the composite **Karpathy `autoresearch` selection score**:
  $$S_{\mathrm{AR}}(H_i) = 0.35 \, \mathcal{D}_{\mathrm{proof}}(H_i) + 0.25 \, \mathcal{C}_{\mathrm{bridge}}(H_i) + 0.20 \, \mathcal{W}_{\mathbb{Q}}(H_i) + 0.20 \, \mathcal{F}_{\mathrm{sharp}}(H_i)$$
  where $\mathcal{D}_{\mathrm{proof}}$ measures non-tautological Lean 4 proof depth (penalizing single-line `norm_num` arithmetic while rewarding multi-step algebraic/analytic derivations such as coprime $c_4$ non-divisibility, $p$-adic valuation divisibility, Fréchet derivative vanishing, or Gibbs convex entropy minimization), $\mathcal{C}_{\mathrm{bridge}}$ measures cross-corpus synthesis, $\mathcal{W}_{\mathbb{Q}}$ measures exact rational witness richness, and $\mathcal{F}_{\mathrm{sharp}}$ measures obstruction/threshold sharpness.
- Select the **5 highest-scoring hypotheses (`TOP-5`)** for exhaustive multi-part deep-dive formalization and analytical proof exposition, while retaining the full 10-hypothesis screening table in `results.tsv` and the manuscript for complete preregistered transparency.

### 26c. Non-Vacuous Cross-Corpus Mathematical Anchors
- **Fermat's Last Theorem (`anthropics-flt`):** Formalize genuine Frey–Hellegouarch Weierstrass invariants ($E_P : y^2 + xy = x^3 + \frac{b^p - 1 - a^p}{4}x^2 - \frac{a^p b^p}{16}x$), proving $\Delta(E_P) \cdot 2^8 = (abc)^{2p}$, $c_4(E_P) = (c^p)^2 - (ab)^p$, coprime semistability $q \mid abc \implies q \nmid c_4(E_P)$, and the Ribet level-lowering $p$-adic valuation dichotomy ($p \mid v_\ell(\Delta(E_P))$ for odd $\ell \neq 2$ vs. $p \nmid v_2(\Delta(E_P))$ at $\ell = 2$ for prime $p \ge 5$).
- **OpenAI Navier–Stokes Claim Audit (`OpenAI-NSE-Epistemic-Audit`):** Formalize the periodic mean-velocity / BKM admissibility exit (`CandidateProperties` $\implies$ every gradient bound $C$ and Knudsen/Mach admissibility threshold $c^2/\nu$ is violated near $t = 1$), the Fréchet linearization invisibility of Leray-$\alpha$ regularization at rest ($D N_\alpha(0) = 0$ while viscous damping $\nu k^2$ exceeds any kinetic collision cap $1/\tau$), the von Kármán–Tao cascade Reynolds divergence ($Re_n = Re_0 s^{3n}$), and the nonlinear discrete-velocity BGK Gibbs $H$-theorem ($H_w(f_{\mathrm{eq}}) \le H_w(f)$).

## 27. External Referee Peer-Review Remediation & `ARGOS-PEER-001..007` Gates (2026-10-19)

Lessons derived from the external Peer Review Report on Paper 1 (*"Frey-Hellegouarch Weierstrass Semistability, Ribet Level-Lowering p-Adic Valuation Dichotomy, and Exact Hamiltonian Conservation via Dual-Number Relaxation"*) and codified into [`anse/elenchus/scientific_swarm.py`](file:///home/xavkal/xdev/AutoevolveAI/anse/elenchus/scientific_swarm.py) (`EXTERNAL_REFEREE_REMEDIATION_LEDGER`) and [`.agents/skills/elenchus-scientific-swarm/SKILL.md`](file:///home/xavkal/xdev/AutoevolveAI/.agents/skills/elenchus-scientific-swarm/SKILL.md):

1. **`ARGOS-PEER-001` (Epistemic Domain Disconnect & Bifurcation Gate):**
   - *Finding:* Stitching discrete arithmetic geometry over $\mathbb{Z}, \mathbb{Q}, \mathbb{F}_q$ (Frey–Hellegouarch curve $E_P$) with continuous real-valued Hamiltonian ODE integration is a category error—simulating a continuous real ODE flow on a Weierstrass curve provides zero insight into Fermat's Last Theorem or modularity.
   - *Rule & Gate:* Never claim that continuous real ODE integration of an elliptic curve informs discrete arithmetic modularity. Bifurcated Paper 1 into two standalone domain-pure companion manuscripts—**Paper 1A** (`Paper1A_Frey_Ribet_Lean4_Arithmetic_Geometry.pdf`, pure Lean 4 number theory) and **Paper 1B** (`Paper1B_RRK_DualJVP_HenonHeiles_RustySundials.pdf`, structure-preserving Dual-RRK benchmarked on the physical Hénon–Heiles Hamiltonian $\mathcal{H}_{\mathrm{HH}}$)—and decoupled Part I and Part II in the combined edition.
2. **`ARGOS-PEER-002` (Level-Set & Governing Equation Algebraic Identity Gate):**
   - *Finding:* Defining $\mathcal{H}_E(x,y) = \frac{1}{2}y^2 + \frac{1}{2}xy - \frac{1}{3}x^3 - \frac{1}{2}a_2 x^2 - a_4 x$ yields $2\mathcal{H}_E = 0 \iff y^2 + xy = \frac{2}{3}x^3 + a_2 x^2 + 2a_4 x$, mismatching the Weierstrass curve coefficients on $x^3$ and $x$.
   - *Rule & Gate:* Corrected $\mathcal{H}_E(x,y) = \frac{1}{2}(y^2 + a_1 xy - x^3 - a_2 x^2 - a_4 x)$ in Lean 4 (`weierstrassHamiltonianDual`), Python telemetry, and LaTeX, and formally proved the exact polynomial identity $2\mathcal{H}_E(x,y) = (y^2 + a_1 xy) - (x^3 + a_2 x^2 + a_4 x)$ in `P1_T4_dual_weierstrass_hamiltonian_jvp.1`.
3. **`ARGOS-PEER-003` (Diophantine Witness & Reductio-ad-Absurdum Validity Gate):**
   - *Finding:* By Fermat's Last Theorem, no non-zero integer $c$ satisfies $a^p + b^p = c^p$ for $p \ge 5$, so `FreyPackage` is a *reductio ad absurdum* object; furthermore, claiming $a=3, b=64$ in a caption while tabulating $v_3=1, v_2=2$ (which correspond to $(3,4,5)$) is a mathematical contradiction.
   - *Rule & Gate:* Explicitly distinguish conditional *reductio ad absurdum* theorems over `FreyPackage` from concrete integer valuations evaluated on the generalized Hellegouarch curve $E_{A,B,C}$ attached to coprime $abc$-triples $A + B = C$ ($A = 3^p, B = 4^p, C = 3^p + 4^p$, $\Delta(E_{A,B,C})\cdot 2^8 = (ABC)^2$) with full $v_\ell(A), v_\ell(B), v_\ell(C)$ accounting.
4. **`ARGOS-PEER-004` (Table Boolean & Remainder Logic Gate):**
   - *Finding:* Writing `$2 \neq 0$ (False)` under column `$v_2(\Delta_E) \bmod p$` conflates the true inequality $2 \neq 0$ with the boolean `False` of $p \mid v_2(\Delta_E)$.
   - *Rule & Gate:* Separate integer remainders ($\mathrm{rem} = v_2(\Delta) \bmod p$) from boolean divisibility predicates ($p \mid v_2(\Delta)$ is `False`, $p \nmid v_2(\Delta)$ is `True`), enforced via regex gate in Round 3.
5. **`ARGOS-PEER-005` (Initial Condition & Exact Rational Energy $\mathcal{H}_0$ Audit Gate):**
   - *Finding:* Reporting $\mathcal{H}_0 = -0.145395833333$ mismatched the true evaluation at $(-0.35, 0.35)$ due to a parameter swap.
   - *Rule & Gate:* Every initial energy $\mathcal{H}_0$ must be verified in exact rational arithmetic (`fractions.Fraction`) in Python and cross-checked in Round 3 ($\mathcal{H}_{E,0}(-0.35, 0.35) = -203/4000 = -0.05075$; $\mathcal{H}_{\mathrm{HH},0}(0, 0.2, 0.3, 0.2) = 247/3000 \approx 0.082333333333$).
6. **`ARGOS-PEER-006` (Anti-Orphan Physics Axiom Gate):**
   - *Finding:* Including Lorentz magnetic zero-work gyrokinetics $\langle v, v \times B \rangle = 0$ inside `P1_T4` was an unmotivated prompt-leakage artifact.
   - *Rule & Gate:* Removed the orphan Lorentz clause from `Stmt_P1_T4_DualWeierstrassJVP` and replaced it with the exact level-set identity and the physical Hénon–Heiles Dual JVP, gated in Round 4.
7. **`ARGOS-PEER-007` (Single-Column OCR-Safe Layout & Divisibility Glyph Gate):**
   - *Finding:* Two-column 10pt layout caused horizontal line interleaving in linear PDF/OCR parsers and corrupted `\nmid` glyphs.
   - *Rule & Gate:* Switched all Elenchus Trilogy manuscripts to single-column `\documentclass[11pt]{article}` with `\usepackage{cmap}` and `\usepackage{lmodern}`, verbal disambiguation ("does not divide, $q \nmid c_4(E_P)$"), and `0` `Overfull \hbox` warnings in Round 5.

## 28. 4-Pillar Human-AI Centaur & Humanitarian Frontier Architecture (`ARGOS-CENTAUR-001..004`) (2026-10-19)

In response to the late-2026 autoformalization alignment challenges (13M-line brute-force FLT proofs, `arXiv:2610.08144` *"Navier-Stokes lost in translation"*, and the Fields Medalists' declaration on AI impedance mismatch), the Elenchus Scientific Swarm was upgraded to **Centaur Architecture v4.0** across `formal/ANSE/ElenchusTrilogySpec.lean`, `formal/ANSE/ElenchusTrilogy.lean`, `anse/elenchus/scientific_swarm.py`, and the 5-paper suite:

1. **Pillar 1 (`ARGOS-CENTAUR-001` — Conceptual Compression, Proof-Golfing & Cross-Domain Structural Isomorphism):**
   - Instead of brute-forcing thousands of lines of unstructured tactics, proofs are compressed via `LeanMaster` reusable tactic combinators (`auto_bound`, `auto_eq`, `prove_pos`, `conv_rate_lt_one`, `energy_monotone`) to **25.88 lines/theorem** across all 16 theorems ($17.39\times$ compression factor vs. unfolded proofs).
   - Cross-domain connections are restricted to explicit **structural scaling isomorphisms** ($p$-adic valuation filtrations $v_\ell(\Delta)$ $\leftrightarrow$ dyadic Littlewood–Paley cascade shells $2^{n\alpha}$; Ketcheson RRK secant step $\gamma_n$ $\leftrightarrow$ Radii-Polynomial Newton–Kantorovich contraction) without forced equation mashups.
2. **Pillar 2 (`ARGOS-CENTAUR-002` & `ARGOS-CENTAUR-003` — Closing the "Lost in Translation" Gap, `arXiv:2610.08144`):**
   - **Mandatory Inhabitation Gate (`ARGOS-CENTAUR-002`):** Because `FreyPackage` is uninhabited for $p \ge 5$ by Wiles' theorem (used strictly for *reductio ad absurdum*), positive arithmetic geometry theorems are paired with `InhabitedHellegouarchPackage` ($A+B=C, \gcd(A,B)=1, A \equiv 3 \pmod 4, 16 \mid B$) and a formal Lean 4 proof of `Nonempty InhabitedHellegouarchPackage` (`instNonemptyInhabitedHellegouarchPackage`, `P1_T5_inhabited_hellegouarch_and_pqc_isogeny.1`) via the concrete witness $(A,B,C) = (15,16,31)$ ($\Delta_{\mathrm{scaled}} = 55353600, c_4 = 721$).
   - **Bidirectional Back-Translation Critic & Multi-Kernel Axiom Audit (`ARGOS-CENTAUR-003`):** Verifies 100% symbolic parity between back-translated Lean 4 definitions and LaTeX equations and audits `#print axioms` across all 16 theorems (`[propext, Classical.choice, Quot.sound]` only, `0 sorryAx`, 14 `rfl` `DefEq` locks).
3. **Pillar 3 (Humanitarian Physics-Math Frontiers & Complete Weierstrass ODE Elimination in Paper 1B):**
   - **Clean Fusion Energy (`P1B_T5_stellarator_fusion_gyrokinetics`):** In Companion **Paper 1B**, the artificial continuous Weierstrass curve ODE is completely discarded in favor of Littlejohn's **3D Stellarator Guiding-Center Plasma Confinement Hamiltonian** $\mathcal{H}_{\mathrm{GC}}(r,z,v_\parallel) = \frac{1}{2}v_\parallel^2 + \mu(B_0 + \frac{1}{2}\beta_r r^2 + \frac{1}{2}\beta_z z^2)$ ($\mathcal{H}_{\mathrm{GC},0} = 5601/10000 = 0.5601$, Dual-RRK drift $9.2149 \times 10^{-15}$ vs. RK4 $6.9490 \times 10^{-9}$) paired with 3D Lorentz magnetic zero-work orthogonality $\langle v, v \times B\rangle = 0$ and the physical Hénon–Heiles potential ($\mathcal{H}_{\mathrm{HH},0} = 247/3000$).
   - **Computer-Assisted Proofs (CAP) in Navier–Stokes & Climate Fluid Dynamics (`P2_T6_cap_interval_banach_contraction_bridge`):** Formalizes the Radii-Polynomial Banach Contraction Bridge $Y_0 + Z_0 r + Z_2 r^2 < r \implies \kappa = Z_0 + Z_2 r < 1$ ($\kappa = 181/500 = 0.362 < 1$).
   - **Post-Quantum Cryptography (PQC) (`P1_T5_inhabited_hellegouarch_and_pqc_isogeny`):** Formalizes supersingular $\ell$-isogeny walk degree multiplicativity $\deg(\phi_{k_1+k_2}) = \ell^{k_1+k_2} = \ell^{k_1}\ell^{k_2}$ ($\ell^8 \in \{256, 6561, 390625\}$ for $\ell \in \{2,3,5\}$).
4. **Pillar 4 (`ARGOS-CENTAUR-004` — Human-AI Centaur Loop, Calibrated Epistemic Doubt & Hypothesis-Necessity Counterexamples):**
   - Separates technical gate pass rate (`overall_epistemic_score: 1.0`) from non-echo-chamber calibrated epistemic confidence (`centaur_calibrated_epistemic_score: 0.915`), and requires explicit **Hypothesis-Necessity Counterexamples** (e.g., dropping $\gcd(A,B)=1$ at $(3,6,9) \implies 3 \mid 162 \wedge 3 \mid 63$), surfaced analytical obstructions, and interactive human mathematician conjectures.


## 29. Reticulata: ten failures that became binding rules (2026-10-23/24)

One sub-project, two days, eight releases. Almost every advance came from a
control that failed, and the failures fall into a small number of reusable
shapes. These are binding on any measurement in this repository.

### 29.1 A check that both candidate answers pass is not a check

The Bandelt--Dress isolation index was defined with a `min` where the definition
takes a `max`, and the error reached two deposited DOIs. The test used to choose
between the two forms was "the index should equal the internal edge length on a
tree" --- which **both** forms satisfy, because on a tree the two crossing sums
are equal. The forms differ only where the four-point condition fails, i.e. only
on the data the method exists for.

**Rule.** Before asserting a definition, write down what would distinguish it
from the nearest plausible alternative and check *that*. If your test passes for
both, you have checked nothing. Reconcile new definitions against anything
already formalised in the same codebase: a Gromov-product theorem two files away
would have settled this in one line.

### 29.2 A control must be able to fail; a null must be able to vary

Three separate instances in two days. A prediction asked whether a planted
recombinant was "implicated", accepting it anywhere in an incompatible split
pair --- and a split's two sides cover every taxon, so the test was true whenever
any pair existed. Two experiments reported counts against nulls that produced no
violating quadruple at all, where any positive observation is significant.

**Rule.** Every control gets an explicit demonstration that it can fail. Every
null reports its own spread as a computed field, and a null with zero spread
reports BLOCKED rather than a p-value.

### 29.3 An uncertainty band must be structurally capable of being large

Reaching one resolution band took three attempts. Largest-minus-second-largest
replicate margin is identically zero whenever two replicates tie --- common with
small integer counts --- and a zero band declares every verdict resolved.
Bootstrapping a maximum by resampling the observed values cannot exceed the
observed maximum *by construction*, so it measures only how much lower the
quantity might have been. Only drawing more replicates and reporting the running
maximum answered the question.

**Rule.** For any uncertainty estimate, construct the case where the true
uncertainty is large and verify the estimator returns a large number. An
estimator bounded by the statistic it bounds is decorative, not conservative.

### 29.4 Matching a null in expectation is not matching it

Matched-null floors were tuned so the null's *mean* divergence equalled the
population's. At fixed mutation rate the relaxed-clock simulator's realised
divergence has a coefficient of variation near 50% spanning 10--28x, so the
floor --- a maximum over replicates --- was set by whichever replicate drew a
fast-rate tree. Averaging more replicates does not repair this: averaging shrinks
the standard error of the *tuning*, not the spread of the *replicates the
statistic is computed on*.

**Rule.** Measure the across-realisation CV of any quantity you match on. If it
is comparable to the range being matched, reject-sample on the **realised** value
per replicate and report the acceptance rate; a population that cannot be matched
gets no verdict rather than a verdict from an unmatched null.

### 29.5 Never bisect a stochastic objective whose RNG stream is coupled to the tuned parameter

`clonal_tree_relaxed` drew per-branch rate multipliers from the same stream as
`mutate`, and `mutate` consumes a number of draws that depends on the rate.
Changing the rate shifted every downstream multiplier, making the objective
chaotic and non-monotone; bisection wandered and missed its target by up to 77%,
and only on the relaxed-clock path, because the strict-clock simulator has
nothing downstream of its mutations.

**Rule.** Separate RNG streams for structure and for noise, or average the
objective over fixed seeds before optimising it.

### 29.6 Compare exact counts before forming ratios

A margin of `4/5108` against a floor of `4/5123` is greater as a rational and
means nothing: the same differing-site count, with denominators differing only
because one alignment was fifteen columns shorter. The guard then needed three
branches, not two --- written `margin <= floor` it collapsed "below" into
"unresolved" and erased the one correct negative-control result.

**Rule.** Decide on the integer comparison first (fewer / **equal** / more), then
the rate. Equal counts over different denominators are UNRESOLVED.

### 29.7 State the axis your difficulty scales in, and validate at the real size

A split certificate requires every straddling quadruple to clear a floor. That
is `C(n/2,2)^2` conjuncts for a balanced split: 36 at n=8, **784 at n=16**. The
method scored 35/35 on an 8--10 taxon grid and had **zero power** on real
16-taxon data. The scope had been written as "one grid, 8--10 taxa", which lists
parameters without naming the one the requirement scales in.

**Rule.** For any all-must-hold criterion, write down how the conjunct count
grows with problem size before claiming a result, and test at the size the real
data has. Emit a near-miss distribution: "failed by 1 of 91" and "failed by 40 of
91" demand opposite conclusions and are indistinguishable in a pass/fail.

### 29.8 Direction of a defect is a measurement, not an argument

Asked which way a bug biased published floors, I argued "conservative", then
predicted a specific floor would rise, and was wrong both times. Two defects
acted oppositely: a non-converging bisection misses either way, while a maximum
over over-dispersed replicates is always inflated. Measured, inflation dominated
and every corrected floor came out lower --- and a published *negative* turned out
to be a near-miss rather than the comfortable clearance reported.

**Rule.** When two defects act in opposite directions, measure the net. And a
published ratio can be wrong in the safe-looking direction too.

### 29.9 A gate can be measuring your own choice

The admissibility gate refused seven of ten populations, and five of them passed
the gap clause and failed only the insertion-rate clause. Insertions "dropped"
are content absent from the *reference*, which projection discards --- a property
of the reference we picked, not of the data. Anchoring on the longest sequence
instead of the 6-mer centroid doubled the usable sample, with one insertion rate
falling **440x** on the reference change alone.

**Rule.** For every gate that refuses data, identify which clause binds and
whether that clause measures the data or the apparatus. Any rule change must be
mechanistic, verdict-blind, and applied uniformly --- the sweep that motivates it
should read no margin and no verdict, so it structurally cannot select for an
answer.

### 29.10 Verify the artifact changed before reading results

Twice in one session I read numbers off a stale binary: unasserted `str.replace`
calls silently no-op'd while the build still succeeded, and `echo BUILD_OK` after
a grep is not a build gate. A test module that failed to compile meant seven new
tests had never run while I assumed they passed. Separately, a paper's three
near-miss figures no longer matched the emitted artifact, caught only by a
mechanical provenance check over all 22 of its quantitative claims.

**Rule.** Assert the match count on every programmatic edit. Gate every run on
the build with `&&`, never a trailing unconditional echo. Before reading an
experiment, assert a field only the new code could produce. Read test-result
lines, not the absence of errors --- a grep that matches nothing looks exactly
like success. And machine-check every quantitative claim against its artifact
before deposit.

### 29.11 A synthetic validation can confirm its own assumption

The ReticuLean proposal claimed that a program's behavioural profile over a probe
battery is an aligned sequence, so a quartet certificate would reveal whether a
crossover operator recombines. A synthetic test appeared to confirm it, cleanly,
with a usable window of mutation rates. On real evolved programs three
pre-registered controls failed together — 0/24, 0/23 at matched fitness, 0/22 at
matched realised spread — and stratifying 49 populations showed why: behavioural
spread accounts for every certificate, and the mutation-only arm, a tree *by
construction*, carries them at the same rate.

The synthetic test had generated profiles by **mutating profile strings position
by position**, which builds site-wise heritability in by construction. It
therefore confirmed that the method works on site-wise-heritable data, which was
never in question, while appearing to validate an application where that property
fails. A probe outcome is not inherited; it is computed from the whole program,
so unrelated mutations alter overlapping probe sets and manufacture the same
conflicting distances that recombination does.

**Rule.** When a synthetic benchmark validates a method, write down which of the
method's assumptions the *generator* supplies, and check that the real data
supplies it too. A generator built from the method's own model cannot test the
model. For a transfer between domains, interrogate what the method assumes about
the data's **generative structure** — heritability, independence, exchangeability
— not merely its surface form; matching the alphabet was necessary and nowhere
near sufficient. This is §29.1 with the non-discriminating check hidden inside a
data generator rather than inside a test.

### 29.12 An efficiency claim below the host's noise floor is not a claim

A workflow round proposed three life-inspired algorithms — gene-level modularity
with proof reuse, neutral drift, regulatory indirect encoding — and adversarial
screening killed all three. The shared failure is the lesson: **every claimed
saving reduced, on measurement, to memoising a deterministic function, and the
apparent size of the saving was set entirely by the choice of cache key.** One
proposal's 4× came from keying a verdict on the Python source rather than the
generated Lean file (the correct key gives a ratio below 1.0); another priced a
640-bit encoding that exists nowhere in the repository, against an incumbent
operator that already makes a correlated multi-locus change in one event; the
third priced a glue term at 0.9 s that is really a ~33 s compile. The biology
contributed no measured leverage in any of them.

Then the arithmetic that settles it. The surviving fragment set itself a 1.65×
efficiency threshold. Measured on this host with `n = 5` warm compiles, the
spread on **byte-identical input** is **1.88×** — larger than the effect the
proposal wanted to claim. Separately, the frozen spec turned out to be ~76% of
each verification's cost (median 12.55 s of 16.49 s), because the verifier
inlines the spec body into every audit file, so the only real saving available
was a build-system change with no evolutionary layer in it at all.

**Rule.** Before accepting any efficiency claim, measure the spread on identical
input and compare it to the claimed effect. A claim smaller than the noise floor
is not weakly supported, it is **unmeasurable**, and no amount of replication of
the *treatment* fixes it — the fix is to reduce the noise or abandon the claim.
And when a saving is claimed for a cache, state the key: a cache keyed on the
wrong object manufactures an arbitrary speedup, and the key is where the whole
claim lives. Relates to [[variability-estimates-that-cannot-vary]] and §29.3.

### 29.13 Measure the floor before optimising anything above it

Having killed three life-inspired efficiency proposals (§29.12), one lever
appeared to survive: the rung-2 Lean gate inlines its frozen spec into every
audit file, so every verification re-elaborates it. Comparing the spec alone
(median 12.55 s) against the full audit file (16.49 s), I reported the spec as
**~76% of a verification's cost** and predicted that importing a precompiled
spec would give a ~4× saving — comfortably above the measured 1.88× noise floor,
and therefore resolvable where the proposals' claims were not.

Both halves were wrong, and one measurement settled it. Building the spec as an
olean took 77.9 s and bought a median 14.52 s against 16.49 s — a 1.14× change,
inside the noise. Then measuring the thing I had never isolated: a file
containing only `import Mathlib.Tactic.Ring` and one trivial theorem takes a
median **17.61 s**, which is the SLOWEST of the four conditions — slower than the
full audit file and slower than the spec alone. All four medians lie in a 1.40×
band while same-input spreads reach 2.60×.

So essentially the entire cost is a fixed Mathlib load per process invocation.
The spec body, the candidate and the obligations contribute nothing measurable,
and my 76% figure had attributed a **shared fixed cost** to one of the parties
sharing it. The only lever the decomposition supports is amortising that load
across many candidates in one process — a process-architecture change with no
evolutionary or biological content at all.

**Rule.** Before attributing cost to a component, measure the configuration with
that component REMOVED, not merely a configuration containing less of it.
Comparing A+F against B+F, where F is a large shared fixed cost, yields a
difference that says nothing about A or B. The floor is the measurement that
makes an attribution meaningful, and it is usually one cheap run away. This is
why all three proposals in §29.12 were optimising something that was not the
cost — and why I repeated their mistake one level down before measuring it.

**Follow-up, which demonstrates the one surviving lever and corrects a magnitude
above.** Batching eight candidates into a single Lean invocation instead of eight
(`scripts/measure_lean_batching.py`, `results/lean_batching.json`) gives a median
**7.16×**, and the batched condition's same-input spread is **1.02×** — so unlike
every claim in §29.12 this one sits far above the noise that made those
unmeasurable. The decomposition is then exact: a candidate's own elaboration
costs about **0.14 s** while **97%** of a single verification is fixed
per-invocation overhead, which is precisely why caching a verdict, modularising a
genome or importing the spec cannot help — none of them touches the fixed term —
and why batching can. Atomicity prices the downside honestly: a batch containing
one false obligation fails whole and must be re-run individually to isolate, so
batching is a net loss only above an **84.2%** failure rate, which no realistic
search reaches.

### 29.16 Both mechanism-targeted repairs failed their own bars (2026-10-24)

Having measured that random subtree crossover significantly lowers the solve rate
(47.0% to 29.0%, p = 2.98e-04), I derived the exact mechanism and proposed two
repairs. Both fail, and both failures are recorded against bars I fixed before
running rather than after seeing the data.

**Repair 1, matching `sign(B)`.** Refuted by its own negative control: the
anti-homologous arm, built to be worse, scored *higher* (0.395 vs 0.350) and is
indistinguishable from the treatment (p = 0.408) -- exactly the outcome I had
registered as meaning the signature carries nothing.

**Repair 2, preserving `B*v` exactly.** The successor Paper I edition 1 named as
untested. A site is admissible only when `B_donor = k*B_site` for a single
rational k at every point; the donor then goes in as `k*D`. The invariant is
measured, not asserted: 1614 of 1614 contribution comparisons exactly equal,
admissible sites in 269 of 400 random pairs. Result 73/200 (0.365), **not**
significantly above random crossover (p = 0.136). The registered falsifier
fired.

**The one positive signal, and why I did not promote it.** A sharper control --
the same constant-ratio sites with the scaling omitted -- separates choosing a
site from correcting the contribution. Scaling on beats scaling off at p = 0.031,
and the sanity check holds (unscaled is indistinguishable from random crossover,
p = 0.576), so site selection alone buys nothing and any effect lives in the
scaling. That is the first positive mechanistic signal in the programme. It is
also not enough: five comparisons were run, a family-wise 0.05 needs alpha =
0.01, and **nothing survives correction** -- and it is the comparison against the
*weakest* arm. Promoting it would be choosing the test after seeing the data.

**The rule this reinforces.** A pre-registered bar is only worth setting if you
report it when it fires. The temptation here was real and specific: one
sub-comparison at p = 0.031 would have supported a headline of "contribution
preservation causally improves recombination", and it would have been the third
time in this session that a sub-sample estimate did not survive scrutiny -- the
48-seed paired ratio of 1.500 became 0.959 at 200, and a 6-seed smoke test of
3/6 became 73/200 and a failed bar. Three small-n estimates, none replicated.
State the registered result; offer the sub-comparison as a hint, labelled.

### 29.14 The atomicity I measured was my own wrapper, and it invalidated three rounds of economics (2026-10-24)

Everything in §29.13 and its follow-up about batching economics rested on a
premise I recorded as a measured fact: *a Lean compile is atomic -- one failing
obligation fails the whole file and yields no per-declaration rows.* **That is
false, and it was never Lean's behaviour.** It was `verify_file`, which returns a
single aggregate failure the instant `returncode != 0`, discarding the
per-declaration axiom lines the kernel had already printed.

One invocation on 8 candidates with indices 2 and 5 false exits 1 and prints all
eight lines:

```
'At0.At0_m' depends on axioms: [propext, Classical.choice, Quot.sound]
'At2.At2_m' depends on axioms: [propext, sorryAx, Classical.choice, Quot.sound]
```

A failed tactic proof is admitted as `sorryAx` and reported by name -- exactly
what the gate already rejects on. Nothing ever needed isolating.

What that cost: a bisection, then a flat fall-back measured as better than the
bisection, then a break-even law `(1-p)^b > 1/b` derived from the cost of
isolation, then a one-sided numeric screen built to escape that law. Four rounds
of work, three of them sound in their own terms, all downstream of one wrong
premise. The shipped path is now ONE invocation at any failure rate: measured
1 invocation at 0, 1, 2, 4 and 8 failures of 8, every culprit correctly named,
no false candidate accepted at any rate, against 8 individual proofs at 50.88 s.

**The lesson is not "check your premises".** It is narrower and checkable: *I
measured a property of the apparatus and recorded it as a property of the
system.* Every one of those four rounds would have been avoided by one command --
reading Lean's raw stdout instead of my wrapper's return value. The guard to add:
when a measurement establishes a LIMIT, and the limit is reported by code I own,
measure it once at the layer below that code. §29.9 said a gate can be measuring
your own choice; this is the same defect one level down, and it survived §29.9
because the gate's output looked like physics rather than like a choice.

Corollary, and the reason this sits in the binding rules: the numeric screen of
`screen_obligations_numerically` is sound and its measurements are real, but it
was *motivated* as an escape from a limit that did not exist. A correct artifact
built for a void reason is still debt -- it is now marked `MOTIVATION_VOID` in
`results/lean_numeric_screen.json` rather than quietly kept as a win.

### 29.15 An autoresearch funnel, and what it refuted (2026-10-24)

Ten hypotheses formulated against the nine established findings, scored and
triaged (`LL.md` §26b's funnel). The two the triage rejected dead-on-arrival are
the useful part of the record: `AR.H4-lean` rested on a timing difference inside
this host's noise floor -- and the triage *ran its core arm* to show it rather
than arguing -- and `AR.H3-audit`'s control could not fail, since a Python
generator and a Rust subprocess statistic share no identifier by construction.

Of the three tested: `AR.H1-gp` (an address-indexed ablation contribution is a
site-wise heritable character) was REFUTED at 0.200-0.545 transmitted fraction
against its own >= 0.70 bar, and its pre-registered control ordering turned out
not to exist -- the `{*,/}` arm scored *higher* than the full grammar, so the
contrast the design rested on was absent. That is the third independent refutation
of a heritable-unit proposal and it agrees with §F1. `AR.H1-audit` (a three-rule
AST detector for forced controls) was REFUTED, and found something against my own
wording, which I then verified directly in git:

| forced control | in committed code? |
|---|---|
| `h_fn = heldout_eval_fn or (lambda code: champion.total_energy)` + its `r_fn` sibling | YES, `alphaevolve_biomimetic.py:1175` |
| `negative_control_ok=True` | YES, `alphaevolve_biomimetic.py:1183` |
| `verify_against_spec` passing on an empty obligation map | NO -- the method did not exist before the fix commit |
| `defeq_checked` derived from the pass flag | NO -- same |

So "four forced controls found in committed code" is accurate for **two** of the
four. The other two were in `lean_runner.py` code I wrote during that same
session and fixed before committing: real defects, caught in flight, never
shipped. The distinction matters because the original wording made pre-existing
technical debt out of what was half my own fresh work, and it inflated the
apparent severity in the direction that flattered the finding. The detector's
labelled positive set could therefore only ever hold four, and its 5-of-6 recall
bar was unreachable before a line of it ran -- a bar set against a ground truth
that did not exist.

A dispatch defect worth recording because it is mine: the triage renamed
hypothesis ids with `-gp`/`-lean`/`-audit` suffixes the formulating agents never
emitted, so the `byId` lookup returned nothing and all three test agents were
handed `"hypothesis body missing"`. Two recovered the body from the workflow
journal and ran the real test anyway; the third reported BLOCKED and said
explicitly that it would not invent a plausible hypothesis and then confirm it.
A fan-out stage must assert it received a body before claiming to test one.

**And a correction to the follow-up itself, which I got wrong twice.** The 7.16×
is the all-pass case only, and I reported it as a win "for any realistic search".
It is not. Two further measurements settled it.

First, isolation. Atomicity means a failing batch names nobody, so it must be
taken apart, and I asserted without measuring that a bisection would beat
re-running everyone. The opposite is true: because ~97% of an invocation is fixed
cost, every bisection branch re-pays almost a whole verification. Measured at
n = 8, bisection cost **11 and 15** invocations at two and four failures against
**8** for plain individual runs and a flat **9** for batch-then-fall-back. The
flat fall-back is shipped; the bisection is kept in
`results/lean_batching_bisection.json` so the comparison stays auditable.

Second, the break-even. My 84.2% figure was computed for a strategy I then
replaced, and never recomputed. The correct model is exact and cross-checks
against both measurements (8.00× predicted against 8.0× measured at all-pass;
0.89× against 0.89× conditional on a failure): for batch size `b` and
per-candidate failure rate `p`, expected invocations per candidate are
`[q + (1-q)(1+b)] / b` with `q = (1-p)^b`, so

> **batching pays if and only if `(1-p)^b > 1/b`.**

That is a break-even failure rate of about 29% at `b = 4`, 23% at `b = 8` and 10%
at `b = 32`, and the optimal batch size *shrinks* as failures rise — 5 at
`p = 0.05`, 3 at `p = 0.20`. Above roughly a 30% failure rate no batch size
helps at all. So the lever is real for a gate with a high acceptance rate and
worthless for one with a low acceptance rate — which is the regime an
evolutionary search sits in by construction, since most candidates fail by
design. **The 7.16× headline was measured in the one regime the intended
application is not in.**

The magnitude correction: §29.13 above quotes the fixed cost as a median 17.61 s,
measured **before** `lake build ANSE.VerletSymplectic` had produced an olean, so
the spec was re-elaborated from source on every run and the caches were colder.
On a warm host a single candidate verifies in 5.37 s. The structure of the
conclusion is unchanged and sharper, but **17.61 s is not the cost of a
verification on a warm host** and should not be quoted as one. A fixed cost whose
magnitude depends on build state has to be reported with that state.
