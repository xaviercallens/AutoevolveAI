# LT_B deviations (written 2026-10-08 ~11:40 UTC, before the affected runs)

1. Execution mode: jobs are run by a single sequential background driver (lane dir `driver.py`, one python child at a time, 2 threads),
   not as foreground Bash calls. Foreground calls only poll. Jobs and seeds are exactly those of preregistration.json
   (calls of 2 restarts, `--budget-s 450`, seed table unchanged); each job writes its own file; no file is edited by hand.
2. Job ORDER differs from the listing order of preregistration.json (which only fixes priority for part 2): part-1 gamma=1.5 control first
   (as registered), then part-2 controls and cells m=1 (all gamma, gamma=3 m=1,2), part-2 m=2, then part-1 cells, then part-2 m=3 in the
   registered priority (1.25, 1.0, 1.4, 0.75). Reason: only 1 process allowed; cheap lane-level controls gate everything first.
   The driver launches no new job after 19:00 UTC (m=3 durations unknown); unrun jobs are reported BLOCKED.
   If the gamma=1.5 control fails (excess over 3/16 > 1e-5 refined), the driver is killed by hand and all part-1 cells are VOID.
3. Machine load average ~17 on 8 cores at start; timings are pessimistic. No grid change is made for this reason.
4. Part-2 grids are the registered (L, M, Q) per gamma with P=8; the escalation M is used only if a gate fails, and is then disclosed here.
