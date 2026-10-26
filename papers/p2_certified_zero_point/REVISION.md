# Revision after the independent audit (B2, 2026-10-26)

Audit: `AUDIT.md` (ACCEPT_WITH_CORRECTIONS, separate AI agent, no human). Lock: `results/proposal2/2026-10-26/B2/STATEMENT_LOCK.json`.

## Blocking
- BLOCKING-1 applied. `main.tex` disclosure paragraph and Limitations bullet use the audit's exact replacement text; Section 7 and
  `publication_meta.json` (description Status paragraph, notes) rewritten to point to AUDIT.md and STATEMENT_LOCK.json. Still stated: no human audit.
  Ledger: CZP-A-0001..0008 carry a new field `ai_audit` (report, verdict, lock path, lock source hash `d6947d20...`, `human: false`).
  The gate field `audit` stays null on purpose: the gate's flag text says no *person* has certified the statement, and an AI audit is not one.
  Re-run gate (`ledger/gate_output.txt`): exit code 1, 0 blocking findings, 8 flags (LEDGER_UNAUDITED_TIER_A), flags open.
- BLOCKING-2 applied. The wrong "singular at branch degeneracies" sentence is replaced by the audit's text in `main.tex` Section 1 and
  `CERTIFIED_CURVATURE.md` section 1 (both the results/ copy and the data/ copy).

## Non-blocking
- NB-1: `3 * bh2` -> `6 * bh2` and the `e_n` docstring fixed in `b2_certify.py` (results/ and data/code/). Effect nil (tail 2.2e-25 vs 9.2e-13 outward rounding). Full certification NOT re-run.
  The file hash changed: runs used `168115eb...3338c`; current `d8a97f8826a8b41b76b6a0f56716222c9ee3aa71b2efb816f75d09ba45939df8`. Both stated in the paper. Run JSONs still record the old hash.
- NB-2: extra hypotheses (E_zp C^2 near rho; rho critical, Hessian isotropic via order-3 stabilizer) added in abstract, Step 9, CERTIFIED_CURVATURE.md (section 0, 2.6 table, 2.6 text), ledger CZP-C-0013, publication_meta.json.
- NB-3: sentence on `cert_stability` added after Step 7 listing.
- NB-4: keyword "negative result" dropped.
- NB-5: one sentence on global `hsym` in Step 7.
- NB-6: tail remainder stated as asserted, not computed, with the audit's e^-40 estimate (paper engine details, code comment).
- NB-7: N=16 `ball too wide` failure documented (paper, CERTIFIED_CURVATURE.md section 7).
- NB-8: Controls.lean, RejectTampered.lean compiles and the diagonal-path run added to the paper's command block.
- NB-9: one parenthetical added in Step 8.

## Not changed
Lean files (hashes locked, unchanged). No certification re-run. The ledger evidence blobs were regenerated (STATUS text changed, so their hashes changed).
Paper rebuilt with pdflatex (3 passes), 8 pages, no undefined references.
