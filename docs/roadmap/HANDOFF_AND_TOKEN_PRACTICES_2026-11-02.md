# Handoff and token practices (2026-11-02). STATUS: month plan PAUSED by the owner.

Start a fresh session (or /compact) and read ONLY this file first. It replaces re-reading the long history.

## 1. State in one screen
- Published so far this round (Zenodo, each audited by a separate AI agent; no human audit): see `docs/journal/2026-10-31.md`,
  `2026-11-01.md`, `2026-11-02.md` for DOIs. Latest: AIC-LUO 10.5281/zenodo.23867965, BIO-BISTAB 10.5281/zenodo.23867827,
  AIC-MUC9 10.5281/zenodo.23879683. Month plan (`docs/proposals/PROPOSAL_6_30_DAY_PLAN_2026-11-02.md`): days 1-3 done; next
  is day 4 AGT-RESTART (arXiv 2610.36544; read the full proposition first). PAUSED: no daily cron exists.
- Spend: weekly meter 36% (Fable 27%) on 2026-11-02, cap 60% by the reset Sat 7 Nov 08:59 UTC; mode ECONOMY by the pacing
  rule (`docs/roadmap/SPEND_POLICY.md`). The agent-token proxy underestimates ~4x: ask the owner for `/usage`.
- Open owner decisions: patent/secrecy/defensive publication for the private direction (notes in OptimalEnergyAI
  `docs/extensions/ai-reasoning-direction/`, merged; local copy `~/private-ip/`); HiveMind PR #485 (Gen 6 design) unmerged;
  a directory name on the public feature branch that the owner wants kept off public repos (details with the owner);
  human reader (Dr Henry Maurin) for cancer items C2/C3 (ON HOLD, never contact him); JARVIS issue
  usnistgov/jarvis#341 posted (watch replies); extra GPU hosts for the HiveMind router.
- Restart after the T4 host reboot: `bash scripts/start_scheduler.sh` (A1 Lean port, core 0; nothing proved); check the
  hourly merge cron and the HiveMind producers; the 819 MB `formal_cert/Programmes/SandierSerfatyL1` is NOT in git.

## 2. How to publish one audited item (the pipeline that worked)
1. Item folder `results/proposal6/<date>/<ID>/`; prior-art search BEFORE compute; hashed `PREREG_ITEM.md` BEFORE any run.
2. Producer = Sonnet agent; ONE independent Opus audit (auditor writes its own code, a third checker); a Sonnet writer
   applies ALL corrections, builds `papers/<name>/` (main.tex, ledger/, data/, publication_meta.json, BUNDLE_MANIFEST.txt).
3. Staging tree `~/<x>_stage/repo` containing only the paper dir, the lane dir and what `scripts/publish_ar_paper.py`
   hard-codes (it also imports `scripts/publish_universal_optimality_tiered.py`); run the script UNMODIFIED with
   `--paper-dir ... --lane-dir ... --dry-run` from the staging root; third-party text, datasets, binaries, secrets stay out.
4. Publish: `sed 's#^REPO = Path(.*#REPO = Path("<staging root>")#' scripts/ops/zenodo_publish_staged.py > /tmp/pub.py`
   then `python3 -I /tmp/pub.py papers/<name> results/proposal6/<date>/<ID>`; it stamps the DOI and uploads. New version
   of an existing record: `scripts/ops/zenodo_newversion.py <dep id>` first, then pass `<draft id> <draft doi>` as 3rd/4th args.
5. Copy the stamped main.tex/main.pdf back, commit with the two trailers, push the branch
   `worktree-openai-math-discovery` (public repo; normal pushes only; never to main of other repos).
Token `~/.token_workflow_token` is parsed in Python and never printed.

## 3. Token optimisation practices (binding while the cap applies)
1. Fresh/compact session: do not carry a 1000+ turn context; this file is the handoff. The main loop re-reads its whole
   context every turn, which is the largest hidden cost (the agent-token proxy missed it by ~4x).
2. Terse reports: results first, tables over prose, no recap of earlier turns, no narration of obvious steps, one
   short status line per finished chunk. Target under 250 words unless a decision is needed.
3. Delegate large reads (papers over ~30k tokens, logs, datasets) to a subagent that returns a short structured summary;
   never paste agent reports back; reference the file path instead.
4. Batch independent tool calls in one turn; avoid compound shell commands that get refused and re-run; write
   one script file instead of many micro-edits.
5. Do not re-read files just edited; do not poll background agents; wait for their notification.
6. One audit per item; fixes verified by the writer's rebuild; no re-audits unless an audit finds a numerical error.
7. Right-size models: Sonnet for producers/writers/scouts, Opus only for audits and Lean proofs; cap each agent's scope
   (core-hours, files to read) in the brief; ask for the report format that is short.
8. Prior-art search before compute (saves entire items: 5 of 13 earlier items were recomputations).
9. Prefer small items with exact, checkable claims; skip optional extras; defer weekly showcase/PR updates to one batch.
10. Re-anchor on the owner's `/usage` reading at every session start; recompute the allowed daily burn.

## 4. To resume the plan
Owner says "resume": create the daily cron again (the old prompt is in `docs/roadmap/SPEND_POLICY.md` rules: read the
policy first, one item per day in normal mode or one per two days in economy mode), start with day 4.
