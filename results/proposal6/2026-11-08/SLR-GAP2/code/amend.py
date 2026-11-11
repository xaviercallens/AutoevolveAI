import hashlib
p = "results/proposal6/2026-11-08/SLR-GAP2/PREREG_ITEM.md"
txt = """
## PHASE2 (amendment dated 2026-11-10, written before any phase-2 run)
Why: phase 1 was solver-limited (60 s, 2 workers; UNKNOWN almost everywhere). Phase 1 hash kept in PREREG_ITEM.md.sha256.phase1.
Method change only in solver budget: same code/cpsat_gen.py (unchanged), ONE family at a time, 6 workers (taskset cores 1-6), 600 s per (N, family). Driver: code/run_phase2.py, resumable from logs/runs2.jsonl (+ logs/runs2_start.log for honest CPU accounting of killed runs). cpsat_gen's own append to logs/runs.jsonl is rolled back by the driver (phase-1 log stays frozen).
Family order: b3 (b=3, evmin 6, evp 2,3, odp 2,5, q=12, dmult 24, jstep 6, J=4), then b2w (b=2, evp 2,3,5, odp 3,5,7, q=8, J=2), then b6 (b=6, evp 2,3, odp 2,5, q=12, dmult 24, jstep 6, J=4). Per-family core-h caps 7 / 4.5 / 2.5.
Positive control first (6 workers, 600 s): N=64 (n=63), b=2, evmin 4, J=8 must be FEASIBLE/OPTIMAL with both exact checkers COVERED; otherwise STOP and report solver-power failure.
Pruning rule (N chosen BEFORE solving, exact rational arithmetic): with F = base multiples b*k (k<=N) not in the removable pool, slots = n - |F|, each added runner covers open measure exactly 2/N. Necessary condition: uncovered measure of the union of F's open arcs (radius 1/N, shift 0) <= slots * 2/N. ratio = uncovered / (slots*2/N). Skip N with ratio > 1. Remaining N (40..95, all parities) are ordered by ratio ascending (most slack first). Further exact pruning is done by cpsat_gen itself (a critical point covered by no candidate = INFEASIBLE_NO_CANDIDATE). Phase-1 INFEASIBLE (family, N) pairs are skipped.
Stop rules: first cover (FOUND), or 14.0 core-h of CPU actually spent in phase 2 (wall x 6, killed runs counted up to their kill time). Reboots: resume from the log. No Lean, no audit, no commit. Any cover: new certificate name (certificates/p2/*), both exact checkers COVERED at radius 1/(n+1), exact gamma as a rational, failure at next smaller radius, negative controls.
"""
open(p, "a").write(txt)
h = hashlib.sha256(open(p, "rb").read()).hexdigest()
open(p + ".sha256", "w").write(f"{h}  {p}\n")
print(h)
