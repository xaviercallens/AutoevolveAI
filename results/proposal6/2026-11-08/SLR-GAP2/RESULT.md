# SLR-GAP2 (2026-11-08/10): NEGATIVE / inconclusive. No shifted-LRC cover found for any n in 39..94 other than the known n=63. Tier X (nothing new claimed).

Prereg: PREREG_ITEM.md (+ .sha256, written before any run). The 12 core-h kill rule was NOT reached: about 3.5 core-h spent (wall x workers). Stopped because every family returned UNKNOWN at 60 s (solver-limited), a host reboot killed the first wave, and the tool-call budget ran out. This is weaker than the prereg'd NEGATIVE: "no cover found in about 3.5 of 12 core-h".

Prior art (2026-11-08): alphaXiv recency search (after 2026-11-01) + WebSearch found nothing covering n in 39..94 (only 2603.24784, 2608.13599, 2609.06259, 2609.23952). Not killed.

## Code
code/cpsat_gen.py = SLR-EXT cpsat_rule.py generalised: base b*k (k=1..N) at shift 0, open radius 1/N = 1/(n+1); shift menu = union of c/q + j*jstep/D; pools of smooth removable base multiples and smooth added non-multiples. Same exact-integer set-cover model and same two exact checkers (slr_exact.py, check_cover). code/sweep_fam.sh, launch2.sh, summarize.py. Every run is in logs/runs.jsonl (n, family, pool sizes, J, status, solve and wall seconds, workers).

## Controls (same code path)
- Positive: N=64 (n=63; b=2, 3-smooth multiples of 4 + {3,5}-smooth odds, J=8, 6 workers) OPTIMAL in about 4-5 s, both checkers COVERED (3961 endpoints), saved under certificates/ctl (not the audited file). N=96 (n=95) OPTIMAL 0.7 s, COVERED (8945 endpoints). A 1-worker 300 s run of N=64 gave UNKNOWN: solver power depends on workers.
- Negative: N=45 (n=44) INFEASIBLE in 1.5 s.

## Families (N = 40..94 step 2, 60 s, 2 workers each)
| family | base | removable | added | shifts | result |
|---|---|---|---|---|---|
| b3s | 3k | 3-smooth multiples of 6 | {2,5}-smooth non-multiples of 3, <=3N | c/12 + 6j/D, abs(j)<=4, D=24(N+1) | UNKNOWN in all runs |
| b4q8 | 4k | 3-smooth multiples of 8 | {3,5}-smooth non-multiples of 4 | c/8 + j/D, abs(j)<=4 | INFEASIBLE n=89,91,93; UNKNOWN otherwise |
| b2w | 2k | 5-smooth evens (incl. 2 mod 4) | {3,5,7}-smooth odds | c/8 + j/D, abs(j)<=2 | UNKNOWN in all runs |
| b3q12, b6q12 | 3k / 6k | smooth | smooth | c/12 + 8 offsets, 204 shifts | UNKNOWN (3 runs, models 100-270k constraints; first wave killed by a host reboot) |

INFEASIBLE = exact solver verdict for that pool and menu only (not about the conjecture). No FEASIBLE verdict outside the controls (logs/summary.txt). Direction (c) is covered only via larger pools; direction (e) local search was not run.

## Structure note
Bases of multiples of 3, 4, 6 and the wider even pool were not tractable within 60 s. The b=2 smooth pool with J=8 decides in 1-5 s and SLR-EXT already showed it INFEASIBLE except n=63. Only b4q8 at n>=89 decided.

## CPU ledger (wall x workers, upper bound, cores 1-6 only)
About 3.5 core-h over about 93 logged runs, controls included; wall-clock about 3 h across a host reboot (first-wave sweeps lost, 3 logged rows). Unused kill budget about 8.5 core-h.

## Update 2026-11-11 (continuation; total about 9.6 core-h of 12, kill rule still not reached)
Wave 2: 6 workers on the tractable b=2 smooth pool (3-smooth multiples of 4 removable, {3,5}-smooth odds added), q=8 shift menu (c/8 + j/D), N=40..94.
- b2q8s (J=4, 90 s): INFEASIBLE for n=39..93 except n=81 (UNKNOWN). CAVEAT: also INFEASIBLE at n=63, where the known cover needs |j|=8, so this family FAILS the positive control; its verdicts only mean "no cover with offsets within 4/D" and are not evidence about n other than 63.
- b2q8J8 (J=8): UNKNOWN in all 34 runs (N=94..65 at 90 s then 45 s; the N=64 control at 45 s too), so the q=8 J=8 menu did not even re-find n=63; verdicts uninformative.
- b4q8w (b=4, J=8, odds {3,5,7}-smooth): UNKNOWN in 6 runs, stopped as too slow.
Conclusion unchanged: NEGATIVE/inconclusive, nothing found. Wide menus need a reformulation (column generation, reflection symmetry breaking), not more solver time.

## Update 2026-11-11 (after the Zenodo record doi 10.5281/zenodo.24131231 was published; that record reflects the 9.6 core-h state)
Final wave b2q4e2: q=4 menu with the control-compatible width J=8, all 3-smooth evens removable (not only multiples of 4), {3,5,7}-smooth odds added, 6 workers, 60 s, N=40..62: UNKNOWN in all 23 runs. Total 12.1 core-h (wall x workers) over 212 logged runs: the 12 core-h kill rule is now reached with no cover found, so the preregistered outcome is NEGATIVE (still: UNKNOWN-dominated, no claim about n other than the narrow-menu INFEASIBLE verdicts). Zenodo record not updated; a new version would be needed to state this.

## Recommendation
Continuing needs a stronger solver strategy (6 workers, 600 s, one family at a time, N chosen by necessary-condition pruning), not wider 60 s sweeps. No audit, Lean or publication warranted.

## PHASE2 (2026-11-10): NEGATIVE_INCONCLUSIVE
Amendment in PREREG_ITEM.md (hash refreshed; phase-1 hash in PREREG_ITEM.md.sha256.phase1). Driver code/run_phase2.py, log logs/runs2.jsonl (+ runs2_start.log). 6 workers, 600 s per (N, family), cores 1-6.
Pruning (exact rational uncovered measure of the fixed runners <= slots*2/N) kept every N in 40..95 for all three families (ratios 0.29-0.4): it is a ranking, not a filter, here. Phase 1 INFEASIBLE pairs were not in these families.

Positive control (6 workers, 600 s cap): N=64 OPTIMAL in 3.9 s solve, checkers {'checker1': True, 'checker2': True, 'out': 'COVERED n=63 endpoints_checked=3961'} (certificates/ctl2 not written; cert in certificates/p2).

| tag | family | N | n | status | solve s | wall s | pool | slots | points |
|---|---|---|---|---|---|---|---|---|---|
| p2_b3_N73 | b3 | 73 | 72 | UNKNOWN | 600.2 | 609.3 | 33 | 13 | 108930 |
| p2_b3_N55 | b3 | 55 | 54 | UNKNOWN | 600.1 | 608.7 | 30 | 11 | 84594 |
| p2_b3_N65 | b3 | 65 | 64 | UNKNOWN | 600.1 | 608.7 | 31 | 12 | 90198 |
| p2_b3_N72 | b3 | 72 | 71 | UNKNOWN | 600.0 | 609.4 | 33 | 13 | 110682 |
| p2_b3_N67 | b3 | 67 | 66 | UNKNOWN | 600.0 | 608.6 | 32 | 12 | 98490 |
| p2_b3_N64 | b3 | 64 | 63 | UNKNOWN | 600.1 | 608.0 | 31 | 12 | 91002 |
| p2_b3_N74 | b3 | 74 | 73 | UNKNOWN | 600.0 | 609.1 | 33 | 13 | 109878 |
| p2_b2w_N83 | b2w | 83 | 82 | UNKNOWN | 600.1 | 605.6 | 50 | 30 | 124380 |
| p2_b2w_N81 | b2w | 81 | 80 | UNKNOWN | 600.1 | 605.7 | 50 | 30 | 127356 |
| p2_b2w_N91 | b2w | 91 | 90 | UNKNOWN | 600.0 | 606.2 | 52 | 31 | 133324 |
| p2_b2w_N82 | b2w | 82 | 81 | UNKNOWN | 600.0 | 606.1 | 50 | 30 | 126856 |
| p2_b2w_N80 | b2w | 80 | 79 | UNKNOWN | 600.4 | 608.6 | 49 | 29 | 117636 |
| p2_b6_N81 | b6 | 81 | 80 | UNKNOWN | 600.1 | 632.8 | 42 | 18 | 389832 |
| p2_b6_N83 | b6 | 83 | 82 | UNKNOWN | 600.1 | 632.3 | 42 | 18 | 385536 |

Status counts: b2w:UNKNOWN=5, b3:UNKNOWN=7, b6:UNKNOWN=2
FEASIBLE n: []
Runs killed before finishing (counted up to their kill time): []
CPU ledger phase 2: 14.28 core-h (wall x 6, rows 14.28 + killed 0.00); phase 1 was about 3.5. INFEASIBLE/UNKNOWN verdicts concern the given pool and shift menu only, not the conjecture.

## PHASE2 (2026-11-10): NEGATIVE_INCONCLUSIVE
Amendment in PREREG_ITEM.md (hash refreshed; phase-1 hash in PREREG_ITEM.md.sha256.phase1). Driver code/run_phase2.py, log logs/runs2.jsonl (+ runs2_start.log). 6 workers, 600 s per (N, family), cores 1-6.
Pruning (exact rational uncovered measure of the fixed runners <= slots*2/N) kept every N in 40..95 for all three families (ratios 0.29-0.4): it is a ranking, not a filter, here. Phase 1 INFEASIBLE pairs were not in these families.

Positive control (6 workers, 600 s cap): N=64 OPTIMAL in 3.9 s solve, checkers {'checker1': True, 'checker2': True, 'out': 'COVERED n=63 endpoints_checked=3961'} (certificates/ctl2 not written; cert in certificates/p2).

| tag | family | N | n | status | solve s | wall s | pool | slots | points |
|---|---|---|---|---|---|---|---|---|---|
| p2_b3_N73 | b3 | 73 | 72 | UNKNOWN | 600.2 | 609.3 | 33 | 13 | 108930 |
| p2_b3_N55 | b3 | 55 | 54 | UNKNOWN | 600.1 | 608.7 | 30 | 11 | 84594 |
| p2_b3_N65 | b3 | 65 | 64 | UNKNOWN | 600.1 | 608.7 | 31 | 12 | 90198 |
| p2_b3_N72 | b3 | 72 | 71 | UNKNOWN | 600.0 | 609.4 | 33 | 13 | 110682 |
| p2_b3_N67 | b3 | 67 | 66 | UNKNOWN | 600.0 | 608.6 | 32 | 12 | 98490 |
| p2_b3_N64 | b3 | 64 | 63 | UNKNOWN | 600.1 | 608.0 | 31 | 12 | 91002 |
| p2_b3_N74 | b3 | 74 | 73 | UNKNOWN | 600.0 | 609.1 | 33 | 13 | 109878 |
| p2_b2w_N83 | b2w | 83 | 82 | UNKNOWN | 600.1 | 605.6 | 50 | 30 | 124380 |
| p2_b2w_N81 | b2w | 81 | 80 | UNKNOWN | 600.1 | 605.7 | 50 | 30 | 127356 |
| p2_b2w_N91 | b2w | 91 | 90 | UNKNOWN | 600.0 | 606.2 | 52 | 31 | 133324 |
| p2_b2w_N82 | b2w | 82 | 81 | UNKNOWN | 600.0 | 606.1 | 50 | 30 | 126856 |
| p2_b2w_N80 | b2w | 80 | 79 | UNKNOWN | 600.4 | 608.6 | 49 | 29 | 117636 |
| p2_b6_N81 | b6 | 81 | 80 | UNKNOWN | 600.1 | 632.8 | 42 | 18 | 389832 |
| p2_b6_N83 | b6 | 83 | 82 | UNKNOWN | 600.1 | 632.3 | 42 | 18 | 385536 |

Status counts: b2w:UNKNOWN=5, b3:UNKNOWN=7, b6:UNKNOWN=2
FEASIBLE n: []
Runs killed before finishing (counted up to their kill time): []
CPU ledger phase 2: 14.28 core-h (wall x 6, rows 14.28 + killed 0.00); phase 1 was about 3.5. INFEASIBLE/UNKNOWN verdicts concern the given pool and shift menu only, not the conjecture.
