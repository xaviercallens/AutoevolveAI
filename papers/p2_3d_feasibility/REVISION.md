# Revision after the independent audit (AUDIT.md, ACCEPT_WITH_CORRECTIONS)

Date 2026-10-26. Producer of the revision: AI agent. Not reviewed by a human.

## Blocking items
- **B1 applied.** Rigour claim rescoped by rotation invariance, not parameter count: abstract, Section 4.1 ("at most four parameters" removed; a sentence says the number of parameters is not a hypothesis), Section 5.2 (the auditor's exact sentence), ledger C-0018, publication_meta.json. The abstract now says the argument is a hand argument evaluated in floating point, not a rigorous enclosure. Added `data/SUPERSEDED_STATEMENTS.md` (rigour claim, tier "A" meaning C, 33 -> 32 configurations, the W_fcc phrases, "D6" = single-rotation pair bound, hcp gap digit) and a pointer in Reproducibility. The shipped study files in `data/` are unedited.
- **B2 applied.** The simple-tessellation restriction step (density of simple cells, continuity of W_N on separated configurations, margin below the separation distance, unfavourable direction of the Euler inequality for K <= 0) added in Section 6.1 after the transfer sentence, and to ledger C-0015.

## Non-blocking items
- NB-1: `make_all.py` now takes the fcc-bcc gap from `code/n1_energies.json` (8.969202e-5); ratios recomputed from it (printed 0.98, 1.18, 34.5 unchanged; 2 x gap = 1.7938e-4 now equals the Muratov-Novaga margin 1.7938e-4). The hand-typed gap in `n3_green_obstruction.py` is not used (code not edited; its JSON is a shipped result). "Nothing is typed by hand" replaced by a list of the exceptions (MN margin; 2D lattice energies, typed constants with their provenance).
- NB-2 / NB-13: auditor's rotation-convention control reported as an independent-auditor result with its numbers; script is the auditor's scratch file `/tmp/b3audit/ctl.py`, not shipped and not re-run by me (numbers are quoted from AUDIT.md). Alves et al. arXiv:2103.01622 Table III cited for the Madelung constants.
- NB-3: MC error model stated (iid s.e. on one scrambled Sobol sequence per seed is a heuristic; two replicates are not a CI); 2D reference has no s.e., hexagon area 1.0011.
- NB-4: ledger C-0011 now says linear subspace.
- NB-5: Limitations say cyclic group C_6, with the reflection-invariance caveat.
- NB-6: Section 4.3 sentence replaced as specified.
- NB-7: face-trace Chebyshev claim tagged C, modes <= 8.
- NB-8: Lemma 2 hypothesis and bcc separated (1.091 > 0.620), also in ledger C-0012.
- NB-9: disclosure, Limitations "No audit", publication_meta.json updated: one independent AI audit, no human audit.
- NB-10: abstract Outcome wording replaced.
- NB-11: related identifiers added (1504.01153, 2202.09240, 2610.28547, math/9811079, 2103.01622). Creators, license and upload type are supplied by the publish script (noted in `notes`). The gap_hcp digit is recorded in SUPERSEDED_STATEMENTS.md.
- NB-12: Section 2 and Limitations and ledger C-0019 note that the auditor re-read 04-calibration.tex and found G5-G9 accurate.
- NB-14: "in principle reachable" replaced; kill criterion compares with Lieb-Narnhofer -1.4508 (or an actually certified radial constant).
- NB-15: Table 2 caption now gives the radial 4e-6 difference.
- NB-16: unused `\BSqSixC` macro removed from `make_all.py`.

## Declined
None.

## Rebuild
`make_all.py` (ok, 58 macros), `ledger/build_ledger.py` (30 claims), `ledger/run_gate.py` (30 claims checked, no findings, exit_code=0), `build_pdf.py` (10 pages, 0 undefined references, 0 overfull hbox). Not re-run: the numerics scripts (n1, n2, n3, n3b); their JSON are unchanged.
