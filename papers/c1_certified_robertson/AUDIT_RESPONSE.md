# Response to the independent audit (AUDIT.md), 2026-11-25

Verdict of the audit: ACCEPT_WITH_CORRECTIONS, 0 blockers, 9 required corrections, 13 optional improvements. The auditor is an AI model of the same
family as the producer; no human was involved. Line numbers in AUDIT.md refer to the first version of `main.tex`.

| Item | Action |
|---|---|
| R1 wrong figure "about 10^8" | removed; replaced by the measured values (||J|| of order 1e3 to 1e4, ||P^-1 J P|| <= 6.5e3 at 6,684 records). Erratum for the Lean comments (comments only) in `RESULTS_C1C_FULL.md` section 5 |
| R2 controls overstated for the headline mode | rewritten per mode; the meaning of C4 (reduces to nu_plus*h < ln 8) stated; the "margin 7.6" removed. **New mutation controls** (`mutation/`): of four mutations of the checker source two are caught by its own gates, two are not (an optimistic nu is accepted; defect truncation is accepted) and are caught only by comparison with the producer's values or not reliably |
| R3 no Lean theorem for the multi-step result; standalone files with a duplicated robF | stated in the abstract and in section 3 |
| R4 verdict logs missing from the repo | `checker.out`, `producer.log`, `run.log` force-added (evidence repo pull request 57) |
| R5 stale failing gate record | removed from the repo and from the bundle |
| R6 abstract too strong on the discrepancy | "we give evidence" with the limits; the producer source (ph2_enclose.py:236-248) cited; the analysis stated to explain the producer's looseness, not to make the checker sound; the check by inversion described as consistency, not proof |
| R7 nu difference imprecise | "equal at the printed five significant digits", "2 to 4e-8" |
| R8 step column ambiguous | labelled "last step index (0-based)", counts given |
| R9 "inside the published one" | stated through the stored checkpoint boxes, for (y2, y3) only; the two output-time doubles stated |
| O1, O2 | "up to about 540"; the ratio meant is stated |
| O3 | title changed to "an independent re-check"; the body already says independent code, not an independent method |
| O5 | continuity of the competing solution and the bound on q added to the description of the theorem |
| O7 | the swapped hash labels corrected in the evidence repo |
| O8, O13 | the AI comparison of the field and the audit verdict (and that it is a same-family AI audit) stated |
| O9 | "P with its radii" corrected: P is exact rational |
| O10 | done (mutation controls above) |
| O4, O6, O11, O12 | not done: no Robertson-specific witness for the final theorem; two controls fail syntactically rather than mathematically (noted); a direct Sage recomputation of the producer's nu ball at one leap step; axiom reports of the five earlier Lean files were not re-run by the auditor |
| not checked by the auditor | the producer and the checker were not rerun (6.5 hours); stream hashes, `cargo test` and the earlier controls were not independently reproduced |
