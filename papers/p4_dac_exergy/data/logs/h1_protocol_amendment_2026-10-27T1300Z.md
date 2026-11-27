# K1-H1 protocol amendment (2026-10-27 13:00 UTC), written after the 1-D slice scan and before the joint scan

Reason: the 1-D scan of the original protocol holds (T_end, P1, P_end) at values that NSGA-III optimised for a
cold start, so it measures the optimum along a slice, not the joint optimum H1 is about. Warm starts with a deeper
vacuum and pure vacuum swings at T1 = T_end >= T0 (no refrigeration, no sensible heat) were never evaluated.
The 1-D slice result is kept and reported as "conditional (slice) scan".

Amended scoring (joint grid, the same grid for every accounting):
- Rows: the 14 Table 2 rows (material + stored P1).
- Coarse grid: T1 in {200, 210, ..., 320} K; dT in {0, 10, 20, ...} with T1 + dT <= 400 K (dT = 0 included);
  P_end in {100, 1000, 5000, 20000, 60000} Pa (paths with P_end > P1 skipped); P1 = stored value.
- Refinement around the best coarse cell of EACH accounting: T1 +-10 K in 2 K steps, dT +-10 K in 5 K steps,
  P_end x {0.5, 0.7, 1, 1.4, 2}.
- Accountings: face value (published), exergy no-credit r = 0, r = 0.5, signed reversible r = 1; T0 in
  {273.15, 298.15, 313.15} K.
- Report argmax T1 both unconstrained and constrained (purity >= the row's stored nominal purity).
- H1 (headline) holds if, at T0 = 298.15 K and r = 0, the UNCONSTRAINED joint exergy optimum has T1 >= T0 for most
  (> 50 %) of the 14 rows. The constrained result is reported alongside.
- Face-value control: the face-value joint optimum must have T1 < 273.15 K for most rows (it reproduces "start
  cold" in the joint space); otherwise H1 is not scored.
