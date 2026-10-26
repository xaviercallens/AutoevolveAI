# Revision after the independent AI audit (2026-10-26)

Source: `AUDIT.md` (ACCEPT_WITH_CORRECTIONS) and `results/proposal2/2026-10-26/A1/STATEMENT_LOCK.json`. No locked Lean file was modified.

## Blocking
- B1 (assertion coverage): replaced "all/every executable C++ assertion" with the audit's wording in the abstract, section 5 (`cpp_asserts` paragraph, plus a "Not covered" sentence: `core_test` check at `core.hpp:274` not covered; table separation `core.hpp:251` only window by window), `publication_meta.json` description, ledger A-0007, and `CERTIFICATE_PORT.md` (results copy and `data/` copy).
- B2 (unaudited wording): `\date` line, abstract end, AI-assistance disclosure, Limitations, ledger C-0008, ledger producer string and `publication_meta.json` notes/description now describe the independent AI audit (13 modules rebuilt byte-identical, 3 must-fail files re-run, axiom aggregates re-run, Chain.lean type-checked; 28 chunk files, CalcK.lean, CalcLam.lean not rebuilt; LeanFlow not re-run). "No human audit" kept; the 16 LEDGER_UNAUDITED_TIER_A flags remain open.

## Non-blocking
- N1: section 6 states the 891-window / 18,455-literal consistency check (auditor's script), the 1-ulp absorption observation; new ledger row X-0010.
- N2: section 7 states the lower end is not conservative (auditor's 2.2-2.7x faster compiles, global_grid line ~125 h, rate bound holds only at the measured load); meta description updated.
- N3: P2SS-A-0015 re-filed as X (now P2SS-X-0009, observation of the axiom gate); table row tag updated.
- N4: done without touching locked files. New file `formal_cert/Programmes/SandierSerfaty/ChainLink.lean`, sha256 `ecb144e19dfde7001fa608e8e2f62e6e43a6a6a169ab5bfa946346add4a1d136`, theorems `slope_eq`, `fl_eq` (rc 0, 5.2 s, "does not depend on any axioms", `data/compile_ChainLink.json`). `fl_eq` stays conditional on the table value `f0lC`. New ledger row A-0017. The file is uncommitted and is not in STATEMENT_LOCK.json (53 files now; the 52 locked hashes are unchanged).
- N5: "eight unported stages" replaced by "stage rows 2-4 and 9-12" (six cost lines).
- N6: stale-figure banner at the top of `CERTIFICATE_PORT.md` (both copies) pointing to the recomputed figures.
- N7: skipped (not trivial).

## Rebuild
`gen_inputs.py` -> `ledger/build_ledger.py` (35 claims: A 16, L 1, C 8, X 10) -> `ledger/run_gate.py` (exit code 1: 0 blocking, 16 LEDGER_UNAUDITED_TIER_A flags) -> `gen_inputs.py` -> `build_pdf.py` (10 pages, 0 undefined references, 0 overfull boxes, 0 warnings).
