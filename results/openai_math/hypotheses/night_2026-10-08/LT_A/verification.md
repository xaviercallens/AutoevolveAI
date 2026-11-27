# Verification of lane LT_A (adversarial), 2026-10-08

Verdict: CORRECTIONS_NEEDED (minor wording only; numbers and controls hold).

## 1. Preregistration precedes results: PASS
- `git log -- preregistration.json`: single commit bdd0dcb at 11:06:46 UTC; no diff against the working copy.
- File mtime 11:06:29; controls.json 11:11:44; all cells, lane_results.tsv, result.json later (12:23 to 15:44).
- SHA-256 of instrument.py, controls.py, campaign.py, lt_a_driver.py match the hashes in the prereg. Each cell JSON embeds the matching instrument/campaign hashes.
- lt_a_bg.py (the background queue runner) is untracked and not hashed in the prereg. It is disclosed in deviations.md D1, and it only schedules the same campaign.py commands. Its hash is not pinned, so that part of the run is unauditable.

## 2. Numbers trace to result files and reproduce: PASS
- cell_summary.json: 22 cells, restarts sum to 336, flagged sum to 0. All best-excess values quoted in the report match to the digits shown. The g0.75 random K3P10 value the report omitted is -9.698e-6.
- No cell JSON has n_flagged_above_1e-7 > 0, and no row has excess > 0. recheck_grid3.json is [].
- Spot recompute (my own run, about 1 minute): stored parameters for g1.25 twist K2P8 seed 1365, rebuilt with the frozen `instrument.py`. The base grid (L=24, M=160, Q=1200) gives R=0.21051853575100365 and excess -2.836744581458106e-07, identical to the stored result. The third grid (L=32, M=256, Q=3200) gives excess -1.97e-07, still below L1.

## 3. Controls: PASS
controls.json (11:11, before any cell): all_pass=True. C1, C2_C3, C4, C6 pass. The negative controls C5 and C7 exceed L1 by +0.1595 (gamma=3, m=1 and m=2). The report says "+15.9%", which is correct to rounding. C6 is -2.55e-7, within tolerance.

## 4. Overstatement and consistency issues
1. "Saturated": the prereg defines saturation as two consecutive extra chunks raising best R by less than 1e-8. For g1.0 and g0.75 twist only one extra chunk ran, so "saturated" is not established there. For g1.25 and g1.4 twist, the extra chunks did raise individual chunk bests; they did not beat the parent.
2. "All discards" is not what lane_results.tsv shows. The K3P10 twist rows (27, 29) are marked "keep" although their best (-9.2e-7, -8.3e-7) is worse than the K2P8 parent (-2.8e-7, -3.4e-7). The prereg keep rule says keep only if the best rises, so these rows are mislabeled or treated as new cells.
3. The grid discretization shifts the excess by about 1e-7. The third-grid value above (-1.97e-7 against -2.84e-7) is the same size as the 1e-7 flag, so the flag is not far above quadrature noise. A real violation of about 1e-7 or less could not be separated from discretization error. The report's "about 1e-6" resolution claim is fair, if anything generous.
4. The report's own "no violation" scope is right: this is finite-power numerical evidence at 4 gammas, 4 families and K up to 3. It proves no upper bound and is not a discovery. The upstream claim stays untested as a theorem.
5. The restart counts are unequal (12 to 36) and the twist cells have the most. This is disclosed. The deviation D1 (a 520 s timeout that killed one job, with seeds 1040-1079 burned and excluded) is disclosed, and so is the $(cat) shell-variable break.

## Bottom line
The conclusion NO_VIOLATION_FOUND in 22 cells with 0 flagged restarts is supported and reproducible. Soften "saturated" and "all discards", and note that lt_a_bg.py is unhashed.
