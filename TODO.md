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

### 5. Premise retrieval A/B (H2) -- DONE 2026-09-29, model-dependent result
222 real runs (`results/hardness/retrieval_ab.json`, `results/hardness/RETRIEVAL_AB_FINDINGS.md`),
both provers, k=0 vs k=5 vs k=5-shuffled control. **DeepSeek-Prover-V2-7B: T1 0/12->2/12,
T3 0/12->10/12 with retrieval; T2 stays 0/12.** Goedel-Prover-V2-8B: no change on any tier.
Shuffled-premise control stays at baseline (0/5) -- the gain is real, not "any text helps."
Zero false items accepted across all 222 runs. Fed into `anse/v2/model_router.py` via
`scripts/hardness/capability_matrix.py`: T3 now routes to `deepseek+premises` with
Wilson-low 0.552, **the first tier that clears the routing threshold without escalating**.
Next: why doesn't retrieval help Goedel; why is T2 flat even with 16/16 needed lemmas
retrieved (read the raw generations before assuming it's a reasoning gap).

Original framing, for the record:
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

### 12. Adopt Elenchus's ledger.py for this run's claims -- DONE 2026-09-27
Ledgers now exist for `results/{bao_flcdm,desi_dr2_bao,bao_bbn_h0,eboss_vs_desi}/ledger/`.

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
- **DONE 2026-09-27** (LL.md §12): `results/desi_dr2_bao`, `results/bao_bbn_h0`,
  `results/eboss_vs_desi`, each with preregistration, controls, Lean, ledger, paper.

### 14. Human statement audit of the cosmology Lean files
Every Tier A ledger row (DR2-A-0001..6, BBNH0-A-0001..10, EVD-A-0001..9) carries a
*model* referee's audit, labelled as such. A person must read
`formal/ANSE/{DESI_DR2_wCDM,BAO_BBN_H0,BAO_Consistency}.lean` against the fit code.
- **Accept when:** audit objects name a human auditor, are bound to the file sha256,
  and `ledger.py` exits 0 with them.

### 15. File-path mode for `anse/formal/lean_runner.py` -- DONE 2026-09-28
`LeanKernelVerifier.verify_file(path)` / `python -m anse.formal.lean_runner FILE.lean`
(`--formal-dir` or `$ANSE_FORMAL_DIR` = a checkout with a built `formal/.lake`). All four
cosmology modules re-gated through it: 28 theorems clean, whitelist axioms only
(`results/cosmo_synthesis/lean_runner_regate.json`); `tests/formal/` (13 tests) covers the
`sorry` and smuggled-axiom negative controls. It refuses to run `lake env` where
`.lake/packages` is missing (that fetched 1.6 GB of Mathlib into a worktree).
Original spec, for the record:
It can only gate built modules and writes a temp file into the shared `formal/`.
- Do: `lake env lean <path>` from `formal/`, parse in-file `#print axioms`, whitelist,
  no shared temp file. Re-gate the three new modules through it.
- **Accept when:** a worktree-staged file is gated by lean_runner with a sorry and a
  smuggled-axiom negative control both rejected.

### 16. Harden the Elenchus ledger builder against model audits
- Audit objects must carry `auditor_kind` and the audited file's sha256; the builder
  refuses a stale sha. A control shows a changed file yields `audit: null`.

### 17. Subtle-bug negative control in the preregistration template
Every BAO fit preregisters one realistic wrong-convention control (e.g. omega_nu
dropped from omega_cdm) with its expected shift written before it runs.

### 18. Commit preregistration files before the first fit
- **Accept when:** the pipeline's prereg stage ends with a git commit of
  `results/<run>/preregistration.json`, and the fit stage checks it is committed.

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

### 19. Make JEPA learning measurable before claiming it
`results/cosmo3_learning/`: real-verdict training matched the shuffled-energy control and
`energy_accuracy` saturated at 1.00 for both.
- Do: replace or fix the saturated metric (e.g. AUROC of predicted energy vs verdict on a
  task-level held-out split), and grow the corpus with failure-rich episodes.
- **Accept when:** real-verdict training beats the shuffled control on the held-out split
  by a margin larger than seed-to-seed spread (3+ seeds).

### 20. Re-tier the cosmology ledgers to Elenchus's own caps
The synthesis paper's round-3 formal referee: Elenchus Tier B means an identity
verified in exact rational arithmetic; floats, sampling and model output are X. Our 34
"Tier B" rows (seeded floating-point / MCMC harness outputs) are X under the tool's caps,
and the L rows resting on them follow by closure. Disclosed in the paper (Sec. 3.5).
- **Accept when:** each ledger either uses Elenchus's kinds faithfully (numeric -> X) or
  declares a named local extension that the gate enforces, and `ledger.py` agrees.

### 21. Record the interpreter in every run record
The H0 DR1 (T2) verdict is PARTIAL under venv-pta (Py 3.10, numpy 1.26) and PASS under
venv-cosmo (Py 3.11, numpy 2.4); the committed run came from venv-pta. The preregistered
verdict stands. Every `fit.json` must record interpreter, numpy/scipy/emcee versions and
the command, and the preregistration must name the environment.

### 22. Low-tier model intelligence: revised plan (2026-09-28)
`docs/v2/IMPLEMENTATION_PLAN_2026-09-28.md` + roadmap §0. Card acceptance made runnable;
7 cards added (V0-8, M-1, G-1, C-0, C-7, N-9, X-1). Sprint 0 = build `.venv-v2`, accept
the cards already met on main (V0-4, V0-5, N-1, N-5a, N-6), then V0-3/V0-8 metrics.
Sprint 1 = retrieval before training (M-1 premise A/B on the ladder, N-6 into Phase 1).
- **Accept when:** `docs/v2/status.json` exists with ≥ 5 cards marked done by the driver,
  and `results/hardness/retrieval_ab.json` reports both arms per tier.

### 23. Regenerate results/v2/heldout_baseline.json once M-1's retrieval A/B finishes
Committed 2026-09-28 with a PARTIAL deepseek+premises arm (n=19 of ~58; sha256 provenance
in the file makes this detectable). Re-run:
  .venv-v2/bin/python scripts/night_training_workflow.py --write-heldout-baseline
- **Accept when:** the file's `provenance.retrieval_ab` sha256 matches the finished
  results/hardness/retrieval_ab.json, and deepseek+premises/goedel+premises both have
  n_items matching the full T1-T3 (+T0 sanity) item count.

### 24. Fine-tune Laya on this project's own verified decisions -- COLD-START VALIDATED 2026-09-29
`results/laya_coldstart/` (README.md, report.json): head-only fine-tune from the real base
checkpoint on 330 verifier-labeled rows (cosmo3 episodes + Lean hardness ladder), evaluated
on 111 group-held-out rows, 2 seeds, with a shuffled-label control. **Real signal**: held-out
AUROC 0.758/0.760 (fine-tuned) vs 0.322 (untrained base) vs 0.383/0.359 (shuffled control);
accuracy 0.712/0.703 vs 0.297 vs 0.360/0.324. The fine-tuned run's worst seed clears both the
base and the control's best seed by far more than the 0.024 seed spread. Limitations: driven
mostly by the cosmo3 slice (best-balanced source); the hardness-baseline held-out split has
zero positives (T1-T3 pass at 0%, AUROC undefined there); only 2 epochs, head-only, CPU.
Fine-tuned weights at `checkpoints/laya_coldstart_v1/` (gitignored, NOT promoted, NOT wired
into `anse/v5/laya_system_one.py`'s serving path).
Original scope, still open (this run used only 2 of 4 named sources):
`checkpoints/laya/` now holds the real English checkpoint (`scripts/setup_laya_checkpoint.py`,
LL.md §13); the wrapper (`anse/v5/laya_system_one.py`) loads it for real and all 7 tests pass.
Laya answers three typed questions in one forward pass (choice / score / noul) -- exactly the
shape of many decisions this project already makes and verifies: is this Lean proof sound
(noul), which tier should a task route to (choice, cf. `anse/v2/model_router.py`), how good is
this candidate (score).
- Do: a labeled-dataset builder that turns EXISTING verified results (`results/hardness/
  baseline.json` + `retrieval_ab.json`, `results/v2/capability_matrix.json`,
  `results/v2/heldout_baseline.json`, the cosmo3 episodes) into Laya's
  `{state, questions: {type, instructions, criteria}, labels}` schema -- the label is always
  a real verifier verdict (kernel, sandbox, `compare()`), never a model's own opinion.
  Then a light fine-tune of `rl_common.build_model`'s head (CPU is fine for a head-only tune
  given the encoder is frozen-ish; only use the GPU lease if that proves too slow) on a
  train/held-out split by task, with a shuffled-label control (V0-8/C-7 pattern) reported
  next to the real result -- no improvement claim without one.
- **Accept when:** a report shows real-vs-shuffled accuracy/AUROC per question type on a
  held-out split, and the fine-tuned checkpoint is versioned separately from the base
  download (never overwrite `checkpoints/laya/model.safetensors` from the upstream download
  in place) so a regression can be rolled back to the base checkpoint.

### 25. openai_math D0: clone and index github.com/openai/math -- DONE 2026-10-07
Plan and stages D0-D5: `docs/OPENAI_MATH_STUDY.md`. The user cloned it (HEAD adc7f124);
`results/openai_math/corpus_index.json` has 722 preprints, 235 scope notes, 405 challenges,
0 defects, 10 review notes, all triaged in the study's section 2b.

### 28. openai_math D1: body-check the nine definition-hole challenges
Comparator does not compare definition-hole bodies (study section 2b). For Brenier,
DefocusingNLS, ElementaryPositivity, EuclideanFiveColor, KServer, Naimark,
OccupiedOverlap, Rokhlin and SpinAngle, compare each hole's body in the challenge with the
solution's definition (KServer `MainStatement` already matches by eye, up to bound-variable
names).
- **Accept when:** each hole has a recorded verdict (matches / differs / sorried in the
  challenge), by elaborated-`Expr` comparison once D2 builds, or by eye before that and
  labelled as such.

### 26. openai_math D2: independent Comparator re-run (needs user approval)
Separate Lake project on disk 2 (v4.34.1, `lake exe cache get`, mmap workaround), with
`comparator`, `landrun`, `lean4export` installed. Start with `Catalan.json`.
- **Accept when:** one challenge passes Comparator on this machine AND a perturbed copy of
  the same challenge (negative control) fails it, both recorded under `results/openai_math/`.

### 27. Merge the `#exit` forgery guard into main
The guard written in master-math run two (`build_ladder.verdict`) is only on branch
`worktree-master-math-regen2`. `anse/formal/lean_runner.py` file mode has no equivalent.
- **Accept when:** a test feeds `lean_runner.verify_file` a proof with a forged
  `#print "... depends on axioms: [propext]"` + `#exit` and it is rejected; or the gate moves
  to a Comparator-style statement/solution split.

### 29. openai_math hypothesis lab follow-ups (2026-10-07)
- H5': an upper-bound proof of C* <= 5/2, or a multi-scale search that beats 5/2.
- H4: a canard (slow-fast) search that first reproduces De Maesschalck-Dumortier's 4 cycles at
  degree 6; fix the per-sample budget (stiff solver or in-loop deadline).
- H2(b): extend past |D| = 1e7; certify h with an unconditional method.
- H1-H3: formal derivations, only after TODO 26 Comparator-checks family 003.
- Night 2026-10-07 follow-ups (`docs/OPENAI_MATH_HYPOTHESES.md`, section "Night run 2026-10-07"):
  - H5': refuted (23/8). Preregister H5'' (C* = 3); have someone other than the lane review the
    NOTE.md product-rule proof (or Lean-check it); check its novelty; recompute B_3 = 5/2 independently.
  - H5: fix the walsh_top `_init` KeyError (`json['top']` vs `result.top`) in a new, re-hashed runner
    under a new preregistration.
  - H4: P4 not reproduced at eps 0.003. Higher-precision integration (mpmath/arb) near the A(Y)
    plateau, or eps 0.006-0.01 with a matched N2. Add a local resolution check and exclude levels
    in the jitter band.
  - D1: Expr-level comparison of the 45 holes once D2 builds; scan the challenge-only opens.
- **Accept when:** each item has a preregistered run with controls in `results.tsv`.

### 30. Nightly dream phase has no JEPA checkpoint to load (found 2026-10-08)
`scripts/nightly_dream_phase.py` calls `FastJEPALatentPredictor.load_checkpoint(checkpoints/latent_dreamer_jepa.pt)`
unconditionally, and no script in the repo writes that file (absent in the main checkout and both
worktrees). The step fails loudly every night, and the Kev gate then rejects the run.
- Do: decide what the predictor is trained on, add the script that trains and saves it, and make
  the dream phase report BLOCKED (not crash) when the checkpoint is absent.
- **Accept when:** a nightly run either trains the checkpoint and the dream step passes, or reports
  BLOCKED with the missing-checkpoint reason and the other steps still run.

### 31. Dyadic triangular Hilbert constant: next steps after the preprint (2026-10-08)
Preprint: papers/dyadic_triangular_hilbert (Zenodo DOI 10.5281/zenodo.23232389). Proved C* >= 3
via the product rule; conjecture H + 3|T| <= 3 prod ||F||_3 (would give C* = 3).
- Formalise the product rule and the per-level bound in Lean (finite statements over Fin (2^N));
  only then can any claim here reach Tier A.
- Attack the conjecture: the coupling between even and odd coarse triples is the obstacle (paper, Sec. 6).
- Exhaustive +-1 maximum of Psi = H + 3|T| at N = 2 by the lane's reduction (currently only R was exhausted).
- **Accept when:** a Lean-checked product rule, or a proof/refutation of the conjecture at N = 2 over real inputs.

### 32. Matrix-valued sharp 1D Lieb-Thirring lab: follow-ups (2026-10-08)
Docs: `docs/OPENAI_MATH_LT_MATRIX.md`, `docs/OPENAI_MATH_SELECTION_2026-10-08.md`; instruments
`scripts/openai_math/lt_matrix/` (frozen, preregistered e15b810); lane results under
`results/openai_math/hypotheses/night_2026-10-08/LT_{A,B,C,D}/`.
- Read the four lane reports and verifications before claiming anything (all Tier X).
- If NO_VIOLATION_FOUND everywhere: write the numerical evidence up honestly as corroboration, with the search power
  (how close each cell came to L1) and the gaps (m <= 3, gamma grid, basis K <= 3).
- If a candidate is VIOLATION_CERTIFIED: re-evaluate the explicit potential in exact/interval arithmetic, then preregister
  a confirmatory run with new seeds before any public statement.
- Comparator request (docs/OPENAI_MATH_D2_REQUEST.md, written by lane D): narrow run on `LiebThirring.json` first.
- **Accept when:** each hypothesis H-LT1..5 has a recorded verdict in the ledger with its controls.
