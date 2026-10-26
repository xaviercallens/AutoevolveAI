# P3 revision after the independent audit (verdict ACCEPT_WITH_CORRECTIONS)

Applied by the REVISE stage on 2026-10-25. No correction was declined. Producer scripts used: `/home/callensxavier_gmail_com/programmes-2026-10-25/P3/revise_main.py` (exact-match replacements; aborts on a miss).

## Blocking

- **R1 (CM-C-0007 tier inversion): applied.** CM-C-0007 (a Tier C reading of the proof-length counts that restated the X numbers) was removed from `ledger/build_ledger.py`; its content, including the explanation of why the closure grows, is merged into the Tier X row CM-X-0002. Ledger now 35 claims (20 A, 5 L, 6 C, 4 X). Section 7 now says the first repair deleted the dependency edge and only hid the inversion, that the audit restored it and the gate blocked again, and that the reading is now Tier X. The proof-length paragraph header is `X, CM-X-0002` only.
- **R2 (sibling DOIs): applied.** Checked against the primary source (`https://zenodo.org/api/records/<id>`): 23646103, 23646105, 23646107, 23646111 and 23646117 all return `status: published`, `publication_date: 2026-10-25`. "DOI reserved ..." removed from the bibitems dip/yuk/kel/sig/bog, and the "may not be published records" sentence in `publication_meta.json` notes replaced.
- **R3 (audit wording): applied.** Disclosure, Limitations, `publication_meta.json` description and notes now report this audit (11 files and 5 prerequisites rebuilt from source with the producer olean dir off LEAN_PATH; `collectAxioms` over 167 constants, 0 off the allowlist; auditor's planted sorry/axiom/transitive-sorry controls caught, clean control passing) and state: no human audit, the 20 `LEDGER_UNAUDITED_TIER_A` flags stay open, upstream OAI and Mathlib oleans and the openai/math commit (pinned copy has no .git) were not re-verified. Ledger evidence `STATUS` text updated accordingly (audit field stays null).
- **R4 (Figure 1 caption): applied.** Caption now "Tier X illustration (CM-X-0004) ... minima are floating-point grid values".

## Non-blocking

- N1 applied (six Mathlib theorems incl. `iteratedDerivWithin_nonneg`, in Section 2 and CM-L-0001). N2 applied (sign-free mirror notion; CM on (0,inf) iff f(-x) absolutely monotone on (-inf,0); abstract wording changed). N3 applied (abstract, Section 5, description; the uncovered hypotheses are named). N4 applied (method text and `proof_length.py` docstring: `Triangular.*` is repository code excluded on both sides, `OAI.*` is upstream; overlapping structure/field ranges double-counted on both sides; the direction of the conclusion is unchanged). N5 applied (Section 7 says only Salazar Thm 2.3 is a theorem item, accepted by `citation_check.py` with a tampered control refused; the other L rows are L by convention). N6 applied ("D. S. P. Salazar", p. 2 Bochner remark added). N7 applied (widder, mlam, d2, uot, txt are now cited in the text; the related identifiers are therefore cited). N8 applied (-0.0447). N9 applied (872.6 s marked as an anecdote traced only to LIBRARY.md). N10 applied (preregistration-vs-outcome bullet in Limitations and in the Zenodo description). N11 applied ("Laplace transform finite for every c > 0"). N12 applied ("its potential energy"). N13 applied (Section 7: `elenchus_check.py` gave no verdict, which is not a pass).
- N10 remark kept as the audit left it: the absence of any rusty-SUNDIALS or LeanFlow change in this lane is accurately disclosed; whether that is acceptable is the parent session's scope call.

## Rebuild and checks (real output)

- `run_all.py` (inputs, ledger, gate, twice): 35 claims, gate `exit_code=1` with 0 blocking findings and 20 `LEDGER_UNAUDITED_TIER_A` flags (nothing else in `ledger/gate_output.txt`).
- `build_pdf.py` (clean aux, pdflatex twice): 14 pages, 0 undefined references, 0 overfull hboxes.
- Lean sources are unchanged by this revision, so the audited sha256 values and 167-constant axiom result still apply. No new Lean was compiled.

## Commits

None: nothing was committed in AutoevolveAI (instruction), and no rusty-SUNDIALS or LeanFlow branch exists for P3. Base commit of the worktree: 9d245742c1655852103abb28f585e21af54851e6; all P3 files are uncommitted.
