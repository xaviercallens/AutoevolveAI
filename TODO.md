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

### 5. Premise retrieval A/B (H2)
- Do: run the ladder with top-5 `lean_premises` hits prepended vs. without.
- **Accept when:** a results file reports pass rate per tier for both arms,
  same model, same seed, same items.

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
