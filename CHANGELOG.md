# Changelog

All notable changes to AutoevolveAI / SuperGravity are documented here.

## [13.2.0] — A second research exercise, Elenchus rigor tooling, two stranded branches merged (2026-09-27)

**About v13.1.0.** Its notes (below) were written by a parallel session and landed on
`main` inside commit `ca5f7cd`, swept in because `git commit` takes the whole index. The
`v13.1.0` tag was never cut. This release supersedes it; nothing below is re-claimed.

**Measured at this tag** (T4 host, run from a git worktree; see the third correction
below for the number that reproduces in the main checkout, which is the one README's
badges quote):

| Check | Result (worktree, no `formal/.lake`) | Result (main checkout) |
|---|---|---|
| `pytest tests/` | 1359 passed / 21 failed / 49 skipped / 8 errors | **1371 passed** / 15 failed / 43 skipped / 8 errors |
| `test_rigor_guard.py` | exit 0 (141 files; caught 5 violations in the merged branch's tests, all fixed) | exit 0 |
| `antigravity_guard.py` | exit 1: 0 hallucinated imports; pre-existing Ruff debt only (2361, down from 2386) | exit 1, same |
| Lean theorems (sound count, see correction below) | — | **229** across 36 files |

The worktree's extra failures are environment-bound, not code defects. Every one of the
22 that failed before this release's merges fails identically at the pre-session commit
`d8ded3c` in the same environment: Lean calls without `formal/.lake` in a worktree, the
Laya model not loaded, Playwright unable to launch Chromium. The numbers differ from
v13.1.0's 1080/14/43/8, which was measured in the main checkout.

**Third correction, on the same principle.** Re-run in the main checkout (the
environment README's Quickstart actually puts a contributor in) rather than the
release worktree: **1371 passed / 15 failed / 43 skipped / 8 errors.** One failure is
new since the 14-failure baseline: `test_lean_mcts_prover.py::test_mcts_prover_successful_search`
hits a hardcoded 25-second timeout on a `lake env lean` subprocess call, and it fails
in complete isolation on this host at a load average of 3.3–4.7 (several parallel
sessions compiling Lean concurrently) — 25s is tight for `lake env lean` even
uncontended. Whether this is a flaky pre-existing test that this release's traffic
finally exposed, or something that regressed, is **not established**; reporting the
timeout and the load reading rather than picking whichever explanation is more
convenient. `LL.md` already documents the same failure mode for a different timeout.

**Second correction, to the correction above.** The documented reproduction command,
`grep -c theorem formal/ANSE/*.lean`, is itself unsound: it counts every LINE
containing the substring "theorem", not theorem declarations. On this tree that
includes 33 lines of prose, docstrings and string literals — `Blueprint.lean` alone
holds several planned-theorem *names* as data (`"SIMD vector alignment theorem"`,
`"Hash table load-factor theorem"`, ...), each counted as if it were a proof. This is
the same defect class as the original audit's "2,967 Lean proofs" vs. 218 authored
declarations, just smaller (250 vs. 229, ~9% inflation instead of ~13×). So the "244
vs. 226" comparison above was two runs of a flawed command on two different trees, not
evidence either number was hand-incremented — both were undercounting comments as
declarations differently by tree contents. The sound command, anchored to an actual
declaration keyword at line start —
`grep -cE '^(theorem|lemma|example) ' formal/ANSE/*.lean` — gives **229** on this tree,
verified to miss no modified declaration (`private`/`protected`/`noncomputable`
theorems all still start at column 0 here). README's badge and table, and this
command, are corrected to match.

### New: flat-ΛCDM BAO consistency exercise (second end-to-end research run)

Chosen from a survey of local assets as the one problem in the requested areas with a
checkable, near-certain outcome. An independent re-fit of DESI DR1's public combined BAO
data (`dualscale-data-r3/desi_sdss_bao/`, sha256-recorded) recovers **Ωm = 0.2939,
r_d·h = 101.94 Mpc**, within **0.07σ / 0.11σ** of DESI's published 0.295 ± 0.015 /
101.8 ± 1.3 Mpc (arXiv:2404.03002, quoted from the fetched paper). Two independently
coded prediction methods (astropy vs. from-scratch `scipy.integrate.quad`) agree to
<1e-4, cross-checked by a 141×141 grid search. χ²/dof = 1.27 (10 dof).

- `formal/ANSE/BAO_FlatLCDM.lean`: 3 kernel-verified theorems (E(z) > 0, E strictly
  increasing, distance duality D_L = (1+z)² D_A). Axioms are exactly the trusted set,
  printed inside the file.
- `papers/bao_flcdm/bao_flcdm_consistency.{tex,pdf}`: full write-up. The Limitations
  section states it is a reproduction, not a new constraint.
- It is a reproduction exercise by design. No new cosmology is claimed.

### New: SocrateAI-Scientific-Elenchus integrated as the rigor layer

Verified real before use: its own tests (298/299) and its ratchet self-tests. It then
earned trust on this repo's content:

- **`elenchus_check.py`** caught `NO_FOOTPRINT`: the Lean file compiled clean, but its
  axiom check lived only in a scratch copy. Fixed in-file. A hand-built vacuous mutation
  is correctly flagged, and the genuine theorem passes.
- **`ledger.py`** holds 6 claims in `results/bao_flcdm/ledger/` with content-addressed
  evidence. It caught a real **tier inversion**: a comparison claim filed at Tier B
  while resting on a Tier L citation. The 3 Lean claims stay flagged
  `UNAUDITED_TIER_A` (kernel-checked, statement not independently audited). They are
  disclosed, not silenced.

### Merged: `night/remediation-2026-09-25` (PR #2 had been closed unmerged)

`git cherry` showed 8 of its 14 commits already in `main` under other SHAs. The 6 missing
ones are merged:
- P1-6: quarantine the DRY_RUN adapter receipts
- P1-7: red_team refuses rather than fabricates a verdict
- P1-8: silent memory fallbacks announce themselves
- P1-9: `mcts_lean_solver` proof gate that passed almost anything
- P3-4: unified Chroma roots
- P4-1: harvester JSONL spec

P4-1 shipped a test with no implementation. `Harvester._append_jsonl` now appends
atomically (temp file, fsync, `os.rename`). P1-8's test read the main checkout by
absolute path and now reads the code under test.

### Merged: `origin/AIautoevolveClaudeGCP` (181 commits behind, never merged)

This branch brings the Ollama extractor and LLM runners, the 42-card v2 low-tier workflow
(`docs/v2/`, `tools/v2_tasks.py`, `v2_runners/`), a JEPA trainer fix and ~290 coverage
tests. The conflicts were resolved hunk by hunk:

- **Sandbox: kept main's fail-closed policy.** The branch always fell back to Tier-1,
  which would have been a security regression.
- **`web/server.py`:** took the branch's `latent_dim ≤ 32`. This fixes a real bug in
  main, where 33..512 crashed with a 500.
- **`neuro_surgeon`:** measured best-of-N timing replaces main's hardcoded CPU durations
  (50/10 ms), which guaranteed the swap.

18 of the branch's tests asserted behavior main had since changed on purpose. They were
aligned to main's contracts: fail-closed sandbox, no silent zero-padding, refusal
without a trained predictor. One test was removed because it targeted an API the phase-3
redesign replaced.

### Fixed in this release

- The repo guard reported `gpu_lease` and `astropy` as hallucinated imports. Both are
  real modules outside this repo's venv, and both are now allowlisted with their location.
- A generated `sage_curve_facts.sage.py` was committed by mistake. It is untracked, and
  `*.sage.py` is now gitignored.
- The 25 Ruff findings in files authored this session are fixed. A `W→w` rename was
  proven behavior-identical: all 59 ladder statements regenerate byte-for-byte.

### Known issues, stated rather than hidden

- `anse/core/red_team.py::physics_sandbox_thinker` still returns a canned verdict when
  its model call fails. P1-7 fixed only `epistemic_check`.
- `neuro_surgeon`'s CPU VRAM figures (16 vs 4 MB) are still modelled, not measured.
- The P4-5 held-out eval does not exist, so GATE correctly blocked promotion on both of
  today's retrains.
- `ltm_learning_mix.py`'s diluted output is never read by the trainer (TODO item 11).
- `deepseek-r1:14b`, the red team's model, is not pulled in Ollama, so audits refuse.

## [13.1.0] — Operational hardening, honest hardness baseline, BSD formalization (2026-09-27)

Twenty-seven commits since `v13.0.0`, most from parallel Claude sessions running
concurrently on this box. Every measured number below was re-verified independently
rather than taken from commit messages — this project has a documented history of
overstated claims, and that discipline does not get suspended for a busy day.

**Net regression check: zero.** `pytest tests/` reports the identical shape as the
`v13.0.0` baseline — **1080 passed / 14 failed / 43 skipped / 8 errors** — after all 27
commits. `test_rigor_guard.py` still exits 0 (124 files). `antigravity_guard.py` still
exits 1 on the same pre-existing Ruff debt.

### Fixed: a self-inflicted MCP outage across ~9 sessions

The previous release's own commit (`2fade3b`) replaced `.mcp.json`'s
`${CLAUDE_PROJECT_DIR:-.}` with a bare `${CLAUDE_PROJECT_DIR}`, on the claim that Claude
Code does not expand the `:-default` form. **That claim was backwards**, and it broke
every MCP server for roughly nine sessions. Diagnosed this time from Claude Code's own
MCP logs rather than a live session's stale error (the session that made the original
change had started *before* the fix it was "reacting to" had even landed, so it was
looking at a stale ENOENT the whole time):

```
.mcp.json form                       connected   ENOENT
${CLAUDE_PROJECT_DIR:-.}                  24         0
${CLAUDE_PROJECT_DIR}  (the "fix")          0         8
```

`CLAUDE_PROJECT_DIR` is set for hooks but not for `.mcp.json` expansion; without the
`:-.` default it resolves to nothing and `posix_spawn` gets `/.venv/bin/python`.
Reverted, and `scripts/restart_session.sh`'s MCP check now calls `claude mcp list`
directly instead of pattern-matching the config, so it cannot repeat this mistake.
`python-code-guard`, `claude-subtask-workflow` and a newly-registered `leanmaster`
(absolute path, lives outside this repo) all report Connected.

### New: `scripts/restart_session.sh`

End-to-end stack verifier — venv, disk 2, GPU driver, Redis, Ollama **GPU placement**
(the T4 silently serves on CPU if Ollama wins the startup race against the driver;
this script catches and fixes it), the residency policy, warm throughput, MCP health,
the resolved environment profile, and the episode corpus against the JEPA data
contract. PASS/FAIL/SKIP with evidence per line, exit 1 on any FAIL. Both a working
config and the exact broken config above were run through it as controls before it
was trusted.

### New: shared GPU lease across three touch points

Root-caused a real production incident: **another project on this same T4**
(`runux-ai-runtime`) ran `systemctl stop ollama` mid-baseline to free the card for its
own benchmark, and the hardness ladder runner kept going, logging 112 instant
connection errors as if they were prover results. A stdlib-only flock+JSON lease now
coordinates `run_ladder.py`, `night_training_workflow.py`, and `restart_session.sh`.
Two real bugs were found testing it across actual OS process boundaries (not just
in-process): pid-based identity let one holder steal another's lease when pids
coincided, and a CLI acquirer that recorded its own transient pid made the lease look
abandoned the instant that helper process exited. The proposal was also handed to the
other project as a doc-only PR, without touching its uncommitted work.

### New: an honest hardness baseline for Lean theorem proving

`results/hardness/baseline.json` — DeepSeek-Prover-V2-7B and Goedel-Prover-V2-8B,
greedy decoding, full tiered ladder, 118 attempts (59 items × 2 models). Independently
re-verified against the raw file, not just the commit message:

```
           DeepSeek        Goedel
T0 (Mathlib lemmas)   6/10           8/10
T1/T2/T3 (curve facts)  0/12 every tier, both models
T4 (BSD sentinel)       0/1  (correctly never passes)
false-item acceptances: 0 / 118
```

Root cause of the T1-T3 zero, confirmed by hand-replaying two failures against
`lake env lean`: both models write plausible generic tactics but never reference the
specific Mathlib lemma names the goal needs. A second, subtler trap was found one
level past the known `sorryAx`-exits-0 issue: **Lean's error recovery still prints
`sorryAx`-tagged axioms for a *failed* tactic block**, so an axiom-only check without
also requiring `rc == 0` would misread a failed proof as clean. `build_ladder.py`
already required both; this is now documented so it isn't rediscovered.

### New: kernel-verified BSD groundwork

`formal/ANSE/Curve37a1.lean` — `gen_on_W37` proves `(0,0)` satisfies the Weierstrass
equation of curve 37a1 (the canonical rank-1 curve). Re-verified directly for this
release: `lake env lean` exit 0, axioms exactly `[propext, Classical.choice,
Quot.sound]`, zero `sorryAx`.

`formal/ANSE/BSD_RankStatement.lean` replaces a defective free-field "rank" with
`Module.rank ℚ (ℚ ⊗[ℤ] W.toAffine.Point)` and states analytic rank via an entire
continuation of Mathlib's `WeierstrassCurve.LFunction`. This is a **corrected
statement**, not a proof — it type-checks and compiles against the pinned Mathlib, and
is presented as such.

Lean count: **226** declarations across 35 files (was 225), still zero real `sorry`
usage anywhere in `formal/ANSE/*.lean` (confirmed by grepping for the tactic, not the
word — the word appears only in `Blueprint.lean`'s documentation registry).

### New: Lean premise signature indexer, `leanmaster` MCP registered

`scripts/index_lean_signatures.py` indexes theorem signatures from the vendored
`anthropics-flt` (45,455 signatures) and `openai-navierstokes` (36,825 signatures)
corpora into Chroma. **Not yet fully embedded** — the commit that introduced it says so
explicitly ("full 82k embed is an overnight job"); sliced runs via `--limit` have run
so far. Repeating that qualifier here rather than the round total, because presenting
a corpus size as an indexed count is exactly the kind of claim this project exists to
catch.

### Fixed: two real fabrication paths caught and removed before this release

- A `timeout_s=1.0` misconfiguration made every DSPy generation call time out, and the
  `except` branch synthesized a `True := by trivial` proof instead of failing loudly.
  The resulting "20/20 rejected, Qwen too small" result was entirely an artifact of
  the timeout — no model output was ever judged. Fixed (900s timeout, failures return
  `GENERATION_FAILED`), and every simulated artifact it produced
  (`bsd_agent_swarm.py`, `millennium_*solver*.py`, fabricated `results/millennium/`,
  `results/validation/`, `results/bsd/`) was removed from `main` rather than left as
  standing "results."
- Default-on LLM call logging would have written pytest's **mocked** completions into
  the durable long-term memory (disk-2 JSONL and `anse:ltm:llm_calls` in Redis).
  Logging is now off under `PYTEST_CURRENT_TEST` unless a call site opts back in
  explicitly.

### Known limitation carried forward

The 12-episode corpus from `v13.0.0` (harvested again this cycle) still has **zero
failing examples** — well-formed for the JEPA data contract, but with no
correctness signal to train on. `TODO.md` item 3 (raise `PER_TIER_TRUE` to 30, add
harder tiers) and item 1 (point the trainer at the actual prover's base model,
DeepSeek-Prover-V2-7B, instead of Qwen2.5-Coder-7B) are the recorded blockers before a
training run on this data could mean anything.

---

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
