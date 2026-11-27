# LT_B adversarial verification

Verdict: CORRECTIONS_NEEDED. Every number checks out and the process is clean. The headline and the control wording overstate what was shown.

## (1) Preregistration precedes results: PASS
- `preregistration.json` was committed as 1850811 at 11:33:17 UTC. Its mtime is 11:32:41.
- The earliest result file is `part1/control_gamma1.5_m3_call0.best_seed2000.pt` at 11:36:01. The first cell JSON is at 11:37:20.
- The sha256 values of `second_variation.py`, `instrument.py`, `campaign.py`, `controls.py`, the test file and `lt_matrix/preregistration.json` match the registered ones now. All three campaign JSONs carry the registered instrument and campaign hashes.
- `git status` shows no modification to those frozen files. The only untracked script in the folder is `lt_a_bg.py`, which belongs to another lane.
- `driver.py` (11:34:02), `deviations.md` (11:33:55) and `aggregate.py` (13:23:47) are untracked and were written after the commit. `deviations.md` predates every run. `driver.py` and `aggregate.py` are not in the registered hash set, so they are unfrozen code. I read both and found nothing wrong.
- The `deviations.md` header says "written ~11:40", but its mtime is 11:33:55. This is harmless but inconsistent.
- The report says nothing was committed. Correct: the results, driver and aggregate are untracked, so provenance beyond mtimes is weak until they are committed.

## (2) Numbers against the files: PASS
- Every part-1 number in the report matches `part1/*.json` after aggregation. The rounded values -2.0e-7, -1.38e-5, -2.75e-6, -8.2e-7, -9.3e-6, -1.1e-6 and -9.0e-7 are correct. All 28 calls have `n_flagged_above_1e-7 = 0`.
- I loaded every part-2 JSON. Restricted spectrum length is 18, 72 and 162 for m = 1, 2, 3.
  - m=3 has 122 zero modes, 40 negative modes and 0 positive.
  - The lambda_max values and thresholds match the report.
  - The gradient norm is at most 1.8e-9 and the translation/dilation quadratic form at most 1.8e-9.
  - gamma=3: m=1 has 9 positive and 5 confirmed, m=2 has 27 positive and 5 confirmed, and lambda_max is 0.523.
- Spot recompute: I reran `second_variation.py --gamma 1.4 --m 3 --P 8 --L 14 --M 160 --Q 1600 --threads 2`. It took 178 s under load. `lambda_max_restricted` (1.8228843794204407e-10), threshold, gradient norm, quadratic form and mode counts are identical to the stored file to full precision. The run is deterministic.
- All 41 driver jobs ended with rc=0. The driver log shows no STOP or BLOCKED line.

## (3) Controls: PASS for the lane's own controls, with caveats
- Positive control, gamma=1.5 (m=3, 8 restarts): maximum excess is -2.0e-7, so 3/16 is not exceeded. It counts as passed under the registered rule (refined excess no more than 1e-5).
- m=1 control (a) is in every gamma. Control (d) is the FD-vs-autograd gate, and no VOID verdict appears. Control (b) is within 1e-8 for all gamma below 3.
- Negative control (c), gamma=3, m=1 and m=2, gives NEGATIVE_CONTROL_PASS with 5 confirmed positive directions each.
- Caveat 1: at gamma=3 the point theta0 is not critical (gradient 0.43). The control shows that the pipeline can output positive, finite-eps-confirmed curvature at a non-critical point. It does not show that a genuine saddle at a critical point would be detected. The gamma=3 JSONs also have control-b quadratic form 0.087, which would be VOID_FLAT_DIRECTION_NOT_FLAT in the normal path. The `--negative-control` flag bypasses this, as registered.
- Caveat 2: the part-1 detection side was not re-run. The prereg reuses the frozen `lt_matrix/controls.json`. The only part-1 control in this lane is the gamma=1.5 non-exceedance, which is a positive control. It is not an instrument-detects-a-violation control.
- Caveat 3: at gamma=3/2 the search reaches only about 2e-7 below the bound, and at gamma=1.0 and 1.25 only 1e-6 to 1e-5 below L1. Violations smaller than about 1e-6 are invisible to this search. The grid is Galerkin, so R is biased low.

## (4) Overstatement review
Corrections to apply to the report:
1. The headline says "the scalar one-soliton embedding is not a saddle". This is stronger than the evidence. Of 162 restricted modes at m=3, 122 are zero modes (second-order flat), so the test is inconclusive in those directions. The registered claim H-LT3 is "no restricted Hessian eigenvalue above threshold". Say "the Hessian shows no positive direction beyond tolerance", not "not a saddle". The notes admit this, and the headline should too.
2. The threshold is relative: 1e-6 times the spectral norm, which is the largest negative eigenvalue, up to 0.68 at gamma=0.75. Positive curvature below 7e-7 to 3e-6 is declared noise by fiat. This should appear next to the "0 positive modes" claim.
3. The claim "all excess below 0" is accurate. The text should say that excess values around -1e-7 to -1e-6 are within the instrument's discretisation bias (the control at the proved sharp value also sits there), so they are consistent with equality and carry no information about slack. "NO_VIOLATION_FOUND (not a proof)" is the correct label, and numeric search proves no upper bound.
4. The claim "extra matrix directions contribute only zero modes and negative modes" holds at second order. The identical lambda_max across m is expected, because the restricted row-0 block does not depend on m. It is a structural identity, not an independent confirmation at m=2 and m=3.
5. "H-LT3 not killed" is the right phrasing. Do not upgrade it to a result about local maximality of the sharp constant. The extra directions that would matter (rows 2 and above, and rotpair) are not covered. The far-eps scan was not implemented, and the report says so.
6. No upstream claim or corollary is presented as a discovery. The "3/16 proved for operator-valued potentials" statement is cited background, not a lane result.

Process notes: all 41 jobs were run with only the registered grids, so no grid escalation took place. The driver finished at 13:23, before its 19:00 stop. The lane stayed at the minimum of 8 restarts per cell, which keeps the search power small.
