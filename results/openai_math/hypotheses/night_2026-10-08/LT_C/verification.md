# LT_C verification (adversarial)

Verdict: CORRECTIONS_NEEDED. The numbers and the preregistered verdicts hold. Two exploratory sentences in the report overstate what the data show.

## 1. Preregistration precedes results
- Commit b08c9e0 is dated 2026-10-08 11:38:24 UTC. It contains preregistration.json, controls.json, the first-run C2-failed file, kinetic_dual.py, structure_lt2.py, the tests and timing.py.
- The first campaign output is best_m1_N1.pt at 11:39:20. All 12 cell JSONs are later, at 11:41 to 12:54. h_lt2.json was written at 15:02.
- The sha256 of kinetic_dual.py, structure_lt2.py, both test files, instrument.py, controls.json and the first-run file all match preregistration.json.
- Minor: the file's internal timestamp field says 11:40:00Z, which is after the 11:38:24 commit. This is harmless.
- Disclosed amendment: the C2 rule was relaxed after the first failure. It is disclosed in preregistration.json and in the report. controls_first_run_C2_failed.json and the first-run log are kept.
- Not verified: the commit is local and unpushed. Its timestamp is the committer's own clock.
- The results are untracked and uncommitted. The report says so.

## 2. Numbers against files
- H-LT5: all 12 cell JSONs exist and every restart has excess >= -1e-9. Per-cell minimum excess and the count of restarts within 1e-5 match the report exactly.
  - Examples: m1N1 is 1.490e-8 with 9 restarts; m1N3 is 1.224e-5 with 0; m3N4 is 4.169e-6 with 1.
  - The report's resolution claim holds: cells (1,3), (1,4) and (2,4) have 0 restarts within 1e-5.
  - The report's text says cell (2,4) "never got within 1e-5". Its minimum excess is 1.55e-5, so that is correct.
- Spot recompute: I rebuilt best_m2_N2.pt on a fresh 2^16 grid with the independent numpy evaluate_numpy. This gave J = 2.467402353813524 and excess 5.0804e-7. That is identical to the stored value 5.080411e-7. The orthonormality error is 4e-16.
- H-LT2: the status counts are 345 rows in total, 220 not stored, 59 KILLED, 47 INTERMEDIATE and 19 PREDICTION_HOLDS. That gives 125 analysed rows. C ranges from 0.001242 to 0.4955. The maximum R/L1 is 0.9999998. 59 rows meet R >= 1-1e-4 and C > 0.05. 7 of the 59 are at gamma = 1.5, so 52 are outside the control. All of these match.
- The H-LT2 snapshot is a partial dataset: 220 of 345 near-maximisers were not analysed. Row-selection bias is possible, and the report discloses the gap. PREDICTION_HOLDS is therefore unreachable until the missing parameters are regenerated.

## 3. Controls
controls.json has all_pass = true (C1, C2, C4, C5, C6) and its sha matches. C5 is the negative control: all 3 seeds fall below the wrong constant. C1 is the positive control: J converges to pi^2/4 from above, with excess 6.4e-13 at K = 512. Note that C2 passed only after the rule was amended. The report discloses this.

## 4. Overstatement checks
- "NO_VIOLATION_FOUND, not a proof": appropriately hedged. The search is not independent of the optimiser, and the report states it does not converge in 3 cells.
- Weak point in how the report states the H-LT5 headline: "no violation in 144 restarts" does not bound the true constant in any cell. For N >= 3 it cannot rule out violations smaller than about 1e-5 to 1e-4.
- Correction 1. The report says the embed, twist and rotpair kills are tail noise, with C of about 1e-3 on the core region.
  - This is true of embed (8 rows) and twist (14 rows). Their maximum C at tr W > 0.1 max is 0.003.
  - It is FALSE for one rotpair row at gamma = 1.4. That row has C of 0.1685, 0.1347 and 0.132 at the 1e-2, 0.1 and 0.5 regions, with second-channel weight of only 0.0118 or less.
  - That row is a non-commuting near-maximiser with a single dominant channel. It is not tail noise and not a multi-channel mixture.
  - A third category of kill therefore exists. The summary should list it rather than fold it into tail noise.
- Correction 2. The report says the random-family kills keep C of 0.1 to 0.5 with second-channel weight of 0.1 to 0.4.
  - Among the 23 random kills outside gamma = 1.5, second-channel weight ranges from 0.027 to 0.426. C at tr W > 0.5 max falls below 0.05 in 10 of the 23 rows, down to 0.003.
  - Only about half of the random kills are robustly multi-channel at the stricter threshold.
  - "Genuine multi-channel near-maximisers" is supported for those rows only. For the others, tail noise is not excluded.
- Correction 3. The headline says the prediction is "refuted as stated". That is fair for the preregistered rule. Because the data are exploratory and the sample is partial, treat the "one constant unitary is too strong" conclusion as a hypothesis for follow-up. The "spatially separated pieces" mechanism is flagged untested, which is appropriate.
- "Corollaries are not discoveries": the report makes no Tier X claim, which is consistent. No upstream claim is presented as a result. No overstatement was found in the limits section.
- The gamma = 1.5 control rows were included in the preregistered count (59). The report gives the count with and without them (52 outside), which is fine.

## Conclusion
The numeric claims are reproducible from the stored files, the controls pass, and the preregistration precedes the data. Apply the corrections above to the exploratory narrative: add the rotpair gamma = 1.4 row as a third kill type, and qualify the random-family claim to the rows that stay above C = 0.05 at tr W > 0.5 max.
