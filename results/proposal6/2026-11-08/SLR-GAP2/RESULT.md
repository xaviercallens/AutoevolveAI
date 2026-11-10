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

## Recommendation
Continuing needs a stronger solver strategy (6 workers, 600 s, one family at a time, N chosen by necessary-condition pruning), not wider 60 s sweeps. No audit, Lean or publication warranted.
