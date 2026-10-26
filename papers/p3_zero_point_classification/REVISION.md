# Revision of N1 after the independent audit (v1, 2026-10-26)

Audit: AUDIT.md, independent AI audit, ACCEPT_WITH_CORRECTIONS, 0 blocking items. Not a human audit; no statement lock.
No Lean file and no generated certificate was changed. Nothing committed, pushed or published.

| Item | Action | Where |
|---|---|---|
| 1 Title overclaim | Title scoped to "not a local minimum for a in [0.425,1.579] and a strict minimum along the shear for a in [1.584,4]" | main.tex title; publication_meta.json title |
| 2 "sign changes enclosed" | Abstract now says each bracket contains a zero (IVT); uniqueness and absence of other zeros in the uncertified gaps not certified; "a_-/a_+" introduced as "such zeros" | main.tex abstract; publication_meta.json description |
| 3 T7 tag | Tier cell: "A logic (not formalised as one theorem); C-ball (T1, T2 and the 1.583 record)"; Step 5 sentence adds the same | main.tex T7 row, Step 5 |
| 4 Cell count | 1,284,310 over 203 run records (one duplicate, a = 1.584) and 1,276,022 (232,146 refined) over 202 distinct records; CPU 13,685 s over 210 records, 13,599 s distinct; 609 = 3 x 203 includes the duplicate | main.tex abstract, Cost paragraph, Controls, Limitations; ledger PZC-C-0005; publication_meta.json |
| 5 Straddling | "7 with failed cells, 2 straddling a root, 3 inconclusive (too wide)"; caption: "the 12 unsigned runs (7 failed, 5 inconclusive)" | main.tex Controls, Not-certified caption, Cost; ledger PZC-C-0006 |
| 6 Basic theorems | 20 -> 21 | main.tex Section 9 |
| 7 Thin points | 22 = 10 positive + 12 negative (9 near a_-, 3 near a_+); 84 = 71 + 1 + 12, 113 = 103 + 10 stated in the thin-point table caption; the "12, 9, 5, 12, 3" list is failed cells, left as is | main.tex table caption |
| 8 Over-quantified hypotheses | Not fixed (no Lean change allowed). New limitation: hE, hE', hsym are stated for every real a; sound, awkward, fix is to quantify over lo <= a <= hi in n1_make_cert.py | main.tex Limitations |
| 9 Reject controls | Stated that RejectInside/RejectTampered fail at elaboration ("Reduction got stuck"); the negative proof is Honest.lean (decide +kernel, rc 0, replay rc 0) | main.tex Controls |
| 10 Stale status | "audit pending", "no replay for Cert", "no AI audit recorded" replaced by: independent AI audit ACCEPT_WITH_CORRECTIONS, no human audit, no statement lock; leanchecker rc 0 for Cert (55.5 s), Controls, Honest, Basic and imports ZeroPoint.Basic, ZeroPointCert.Basic (data/leanchecker_replay_audit.json). ledger/build_ledger.py now writes an ai_audit field on every Tier A row and updated STATUS text; ledger rebuilt (27 claims, 27 blobs) | main.tex disclosure, abstract, Section 9, Section 10, Limitations; ledger/build_ledger.py; publication_meta.json |
| 11 Prefactor and BZ | Step 2 states that BZ coverage and prefactors are inherited from B2, filed C-human, checked only at Tier X (agreement with P2's c(a) and roots); a positive prefactor cannot change a sign, a missing BZ region could | main.tex Step 2 |
| 12 hasDerivAt remark | Marked "context only: no N1 theorem uses them" | main.tex Step 2 |

## Gate
`ledger/build_ledger.py` then `ledger/run_gate.py` (Elenchus tools/ledger.py): exit_code=1, 0 blocking, 8 flags LEDGER_UNAUDITED_TIER_A (PZC-A-0001..0008). The flags remain correct: the person-audit field is null because no human has audited the statements. Output in ledger/gate_output.txt.

## Build
pdflatex twice on main.tex: 0 errors, 0 undefined references, 10 pages.
