# H4 verification (adversarial, 2026-10-08)

Verdict: **CORRECTIONS_NEEDED**. These are small wording and number fixes. The PARTIAL status, the P4 failure, and the "no claim about H4" conclusion all hold up.

## 1. Preregistration timing
- `git log -- H4/preregistration.json`: one commit, c1d7cd5 at 2026-10-08 04:28:43 UTC. The file's mtime is 04:27:00, and `written_utc` is 04:27:00.104.
- `git diff --quiet c1d7cd5 -- preregistration.json`: no change since the commit.
- The earliest result file is controls/avg_quintic.json at 04:31:34, after the commit. Everything in design/ (smoke tests) is older than the commit and was committed with it, and those smoke numbers are disclosed under `smoke_tests_seen`.
- sha256 of h4_v2.py is cc84b8a9...e748 and of test_night_h4.py is d0321c3f...bf0c. Both match the preregistration.
- deviations.md has one mtime, 05:31:49, because it was last edited for D8. The claim that each entry was written before the run it affects cannot be checked from mtimes. It can only be checked against the clock times written in the entries.

## 2. Numbers checked against files
- C1 vdp.json: Y = 2.0440649681881586 with Radau and DOP853, and the full-return map changes sign across the root (passes).
- C2 avg_quintic.json: Y = 1.000409, 2.004534 (passes).
- C3: 20 samples (i = 0..19) across 12 chunk files. max radau = max dop853 = 1, and hit_count_deadline is false everywhere.
- N1: {0: 175} and {0: 169}.
- Stage 2a: best k for seeds 100-103 is 1, 2, 2, 1. Seed 104 (the primary F0) has k = 3, strength 4.1662e-4.
- deg6_level.json: 48/48 points ok, A_spread_ulps 5.87e15. The top-3 levels match the report. The extremum of A(Y) is at Y = 2.4655 (A = -6.39897647549e-4). The plateau runs from Y >= 4.2 and its spread is about 1.3e-16 absolute.
- Counts L1/L2/L3: n_confirmed 1, 1, 1 (Y = 1.83127). 14, 14 and 16 brackets were rejected, all for sign_disagreement. statuses are ok 160 each, and hit_count_deadline is false. L1 took 478.7 s.
- MANUAL count: 2 confirmed (Y = 1.9368, 2.9951), 59.1 s.
- Stage 3b: histograms {0: 807, 1: 281} and {0: 759, 1: 310}.

## 3. Independent recomputation (/tmp/h4_verify.py, scipy quad/brentq/DOP853, not h4_v2.py)
- SDI zeros of the primary F0, I(x_R) = int_{x_L}^{x_R} F0'^2/x dx: 0.91603112429, 1.21892815982, 1.37071940753. These agree with design_runs (0.91603112429, 1.21892815982, 1.37071940751) to at least 1e-10.
- The zeros map to Y = F0(x_R)/sqrt(eps) at eps = 0.003: 2.3457, 6.7930, 16.6221. This matches the report.
- van der Pol cycle from an independent DOP853 return map: Y* = 2.04406496837. The report has 2.04406496819, so they agree to 1e-10 relative.
- pytest tests/openai_math/test_night_h4.py with /usr/bin/python3: 11 passed, 1 skipped in 25.6 s. This matches the claim.

## 4. Controls
- C1, C2, C3 and N1 ran and pass.
- P4 ran at only one eps (0.003) and failed there, with max 1 confirmed.
- N2 ran 42/48 curve points and no counts. It is INCOMPLETE, as the report says.
- `controls_pass=false` is correct.
- Weakness in C3: sample 14 has 0 evaluable grid points (statuses: fwd_no_return_bwd_failed 21, fwd_no_return_bwd_blowup 39), so its 0 is vacuous. Samples 5 and 13 lost 22 and 27 of 60 points to fwd_failed_bwd_failed. "Never more than 1" is true, but about 19 of the samples are informative, not 20.

## 5. Corrections
1. Stage 3b says "at most 1 sign change in 3000 trials". sdi_design discards candidates with fewer than 40 admissible points (h4_v2.py:419), so only 1088 + 1069 = **2157** of the 3000 trials were scored. The same applies to N1: 175 + 169 = 344 of 800 trials were scored.
2. "A max at Y=2.4655" has the sign wrong. A is negative, and at Y = 2.4655 it reaches its **most negative value, i.e. maximum |A|** (result.json says "maximum |A|" correctly).
3. "P4 FAILS" should say: "P4 not reproduced at eps = 0.003, the only eps of the 6 preregistered that was run (the other 5 were out of budget)". The headline already says this; claim 2 should too.
4. In lane_results.tsv, row H4n-2 has status `crash`. In this preregistration CRASH means that an instrument control or N2 *failed*, which did not happen. Relabel the row so it does not read as a CRASH verdict, for example `discard` with note "PARTIAL".
5. The C3 claim should say that sample 14 had no evaluable points (a vacuous 0), and that samples 5 and 13 had about 40% failed points.

## 6. Overstatement check
- No upper-bound claim and no discovery claim.
- Stage 3b is labelled theory-level, and the MANUAL count is labelled as not evidence.
- The resolution-limit reading is hedged: it explicitly does not exclude a reconstruction error or an eps-regime failure.
- The paper reconstruction is disclosed as unverified, because the full text was not obtained.
