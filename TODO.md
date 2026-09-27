# TODO before run two

Every item has an acceptance criterion: the check that proves it is done.
"Done" means the check was run and its output recorded, not that code exists.
Background: `LL.md` (lessons), `results/hardness/` (ladder + baseline).

## Blockers — the learning loop cannot improve proving until these land

### 1. Train the model that proves (trainer/prover mismatch)
The trainer fine-tunes Qwen2.5-Coder-7B via transformers; the pipeline prover
is DeepSeek-Prover-V2-7B in Ollama. No retrain can move the prover's numbers.
- Do: point `night_training_workflow.py` FIT at DeepSeek-Prover-V2-7B HF
  weights (4-bit NF4, fp16 compute), SFT on kernel-clean proofs; export the
  adapter merged to GGUF for Ollama.
- **Accept when:** the adapter loads in Ollama and answers a ladder prompt,
  and the FIT journal names the prover's base model.

### 2. P4-5: promotion by benchmark, not by training loss
- Do: GATE runs `scripts/hardness/run_ladder.py` for base and adapter on the
  frozen split (`results/hardness/frozen_split.json`), same prompts, pass@3.
- **Accept when:** GATE promotes only if adapter pass@3 > base pass@3 on the
  frozen split with n ≥ 30 true items and 0 false-item acceptances; GATE
  returns BLOCKED below n = 30. Test with one real base-vs-adapter run.

### 3. Grow the ladder so tiers separate
46 true items today (T0 10, T1/T2/T3 12 each). Per-tier rates on 12 items
move 8 points per item.
- Do: raise `PER_TIER_TRUE` to 30 (more Cremona labels); add T3b (P + Q,
  distinct points) and T5 (torsion order via `nsmul`).
- **Accept when:** `build_ladder.py` reports ≥ 30 usable true items per curve
  tier, 0 control failures, and every true item's reference proof clean.

## Pipeline hardening

### 4. DPO pairs from kernel-verified failures
- Do: pair each clean proof with a failed attempt on the same item (from
  `call_logs/hardness_ladder.jsonl` + baseline.json); drop frozen-split items.
- **Accept when:** ≥ 50 pairs written with provenance, 0 frozen-split leaks
  (checked with the same normalized-proposition match the trainer uses).

### 5. Premise retrieval A/B (H2) -- PRIORITY, raised by the 2026-09-27 baseline
Baseline result (`results/hardness/baseline.json`, 118/118 items, both models):
T0 (Mathlib lemmas) DeepSeek 6/10, Goedel 8/10 pass. **T1/T2/T3 (curve facts):
0/12 for both models, on every tier.** 0 false-item acceptances throughout --
the gate held under real pressure, this is a real capability gap, not a
harness bug (verified by hand: a T1 and a T2 failure both replay as a real
Lean elaboration error, `rc=1`, confirmed live).

**Root cause, read from the raw generations**: both models write a plausible
generic tactic block (`simp [W, WeierstrassCurve.Δ] <;> norm_num <;> rfl`)
but never reference the specific lemma names the proof needs
(`WeierstrassCurve.b₂/b₄/b₆/b₈` to unfold Δ; similarly for
`Affine.slope`/`addX`/`addY` on T3). They know Lean 4 syntax, not this API's
vocabulary -- exactly what premise retrieval exists to fix.
- Do: run the ladder with top-5 `lean_premises` hits prepended vs. without.
- **Accept when:** a results file reports pass rate per tier for both arms,
  same model, same seed, same items. Expect T1-T3 to be where retrieval
  either moves the number or definitively doesn't -- T0 is already saturated.

### 6. Embed the full premise corpus off-GPU
82,280 signatures extracted; 1,000 embedded. Embedding on the T4 collides
with proving/training (cudaMalloc OOM seen on 2026-09-27).
- Do: run `index_lean_signatures.py` against a CPU embedding instance
  (`OLLAMA_HOST` pointed at a CPU-only server) or in a GPU-idle window.
- **Accept when:** `lean_premises` count = 82,280 (± dedup) and a query
  returns results.

### 7. Replace the simulated auditor
`anse/core/red_team.py` DeepThinkAuditor returns canned "Simulated PRM"
strings; `regenerate_10_math_problems_dspy.py` still consults it.
- Do: delete the canned branch; verdicts come from `lean_runner` only.
- **Accept when:** `grep -n "Simulated PRM" anse/` returns nothing and the
  regenerate script's verdict field is derived from `lean_runner` output.

### 8. Clay-correct the Navier–Stokes statement (H9)
- Do: add finite-energy / decay conditions to `NavierStokesSmoothness.lean`,
  mirroring the Clay problem statement (Fefferman).
- **Accept when:** it builds in-project and a statement-review note in the
  file maps each Clay hypothesis to a Lean hypothesis.

### 9. Statement-review pass over `formal/ANSE/`
The gate cannot see vacuous statements (`True := trivial`); 3 exist in
`Theorems.lean` (lines 186, 222, 249) plus 4 real `sorry`s.
- **Accept when:** each is either given real content or deleted, and
  `MasterMathTribunal*.lean` headers no longer claim "zero-sorry" falsely.

### 10. GPU lease between sessions -- DONE 2026-09-27
Two sessions contend for one T4; one stopped Ollama under the other's
running baseline (112 wasted attempts, twice).
- Built: `/mnt/disks/disk-socrateai-local-1/gpu_lease/gpu_lease.py` (stdlib
  only, `flock` + JSON state, holder-name identity, reclaim on TTL expiry or
  dead pid). Snapshot + usage at `scripts/shared_gpu_lease/`.
- Wired into: `run_ladder.py` (held for the whole run, renewed per item),
  `night_training_workflow.py::step_fit` (held for load+train+save,
  `TimeoutError` -> `BLOCKED` journal entry), `restart_session.sh` (both
  ollama start and restart branches; restart skips entirely if the lease
  can't be acquired, best-effort start proceeds anyway).
- Proposed to runux-ai-runtime: `docs/SHARED_GPU_LEASE_PROPOSAL.md` in that
  repo (doc only; nothing there edited without being asked).
- **Verified:** cross-process contention blocked (not just in-process),
  trap-based release, `kill -9` reclaimed via dead-pid detection before TTL,
  missing-module best-effort degrade in the bash helper. Not yet verified:
  whether runux actually adopts it -- until it does, the lease only protects
  AutoevolveAI's own jobs from each other, not from an uncoordinated
  `systemctl stop ollama` on the runux side.

### 11. Wire ltm_learning_mix.py's output into the actual trainer
`night_training_workflow.py::step_data` reads
`LAKE/data/redis/redis_ltm_lora_dataset.jsonl` directly; `ltm_learning_mix.py`
writes a separately-diluted `data/training/ltm_mix.jsonl` that is never
consumed. Every dilution-ratio report this session was decorative.
- Do: point `step_data` at `ltm_mix.jsonl` (regenerating it first each run),
  or delete the mix builder if the raw-corpus filter is judged sufficient.
- **Accept when:** a training run's DATA step log line names the file it
  actually read, and that file is the one the dilution cap was computed on.

### 12. Adopt Elenchus's ledger.py for this run's claims
Surveyed and used `elenchus_check.py`; `ledger.py` (the tier-capped claim
ledger, X<C<L<B<A) was not exercised.
- Do: register this run's claims -- the 3 Lean theorems (Tier A), the numeric
  fit (Tier B), DESI's quoted values (Tier L) -- as a real ledger entry.
- **Accept when:** a ledger file/output exists naming these claims with
  tiers and evidence paths, not just a citation in LL.md.

### 13. Extend the BAO pipeline to DESI DR2 / eBOSS / SDSS
Same code (`scripts/bao_flcdm/fit_desi_bao.py`), new mean/cov files already
present in the same local data directory (`desi_2024_eboss_gaussian_bao_*`,
`sdss_DR16_*`, `sdss_DR12*`). Near-zero marginal cost.
- **Accept when:** a joint or DR2-only fit result exists with its own
  external-validation comparison (DR2's own quoted values, arXiv:2503.14738).

## User actions (cannot be done by the agent)

- **Rotate credentials.** The transcript scrubber redacted 1 Anthropic key,
  1 GitHub token and 2 AWS access keys in `~/.claude/projects/` transcripts.
  The LTM copies are redacted; the raw transcripts are not.
- **Start a fresh `claude` session** so `.mcp.json` servers attach
  (leanmaster verified answering; python-code-guard / subtask-workflow).
- Optional: set `HF_TOKEN` (the trainer's HF downloads are rate-limited).

## Done in run-two prep (for the record)
- Run-one record corrected (1 s timeout + fabricated fallback), simulated
  artifacts removed — LL.md §0.
- Goedel-Prover "0/9" explained: its answer lands in the `thinking` field;
  `run_ladder.py` reads content + thinking and takes the last Lean block.
- Hardness ladder built and validated (59 items, 0 control failures).
- Frozen split wired into the trainer; excludes the 2 contaminating rows.
- GATE returns BLOCKED with the real reason instead of OK.
- LeanMaster MCP server verified: `initialize` OK, 7 tools.
