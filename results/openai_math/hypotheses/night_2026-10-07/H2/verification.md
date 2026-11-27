# H2 verification (adversarial), 2026-10-08

Verdict: CONFIRMED. No corrections are needed to the numbers. One wording point is optional (see the end).

## 1. Preregistration came before the results
- `git log -- .../H2/preregistration.json` shows one commit: c1d7cd5, 2026-10-08T04:28:43Z ("prereg(openai_math): night 2026-10-07 lane preregistrations"). The same commit adds `h2_extend.py`, `test_h2_extend.py` and `write_preregistration.py`.
- `git diff c1d7cd5 -- preregistration.json h2_extend.py` is empty, so neither file has changed since the commit.
- File mtimes: preregistration.json 2026-10-07 21:41:16. positive_control.json 04:31:44, and with elapsed 131.8 s it started about 04:29:32. The earliest chunk is 04:33:12 and the last write to the chunks directory is 05:42:42. result.json is 05:42:47 and argmin_recheck.json / lane_results.tsv are 05:44:17. Every result file is later than the commit, and all of them finished before the 06:00Z deadline.
- The preregistration was written 21:41Z but committed only at 04:28Z. Nothing on disk shows any test-range result before 04:29Z, but mtimes cannot rule out values seen and then deleted. The preregistration's own disclosure lists only timing probes (sums of h, no minima) and a smoke test below 1e7.

## 2. Numbers trace to the files and to the named code
- `sha256sum h2_extend.py` = 7003d754...6fb. This matches `code.runner.sha256` in the preregistration and `runner_sha256` in result.json.
- I re-aggregated the 180 chunk JSONs independently and every figure matches result.json and the report:
  - The chunks tile (1e7, 1e8] with no gaps.
  - n_fundamental = 27,356,753.
  - n_rechecked = 11,700 (180 x 65), and every chunk has recheck_agrees true.
  - h1_count = 0.
  - min S = 0.567741286418723 at D = -10560643.
  - min L = 0.20250663929194127 at D = -60408307.
  - Sum of elapsed_s = 11,983.8.
  - n_S_below_recheck_threshold = 0.
- The four dyadic window counts add up to the total: 2060040 + 5099663 + 10199281 + 9997769 = 27356753.
- Independent recompute with my own loop (PARI isfundamental + qfbclassno, cypari2, nbthreads 1) over chunk (10,500,000, 11,000,000]:
  - n = 151,989 matches the chunk file.
  - min S = 0.567741286418723 at D = -10560643 with h = 211, an exact match.
  - quadclassunit(-10560643) also gives h = 211.
  - Run time was 43.6 s.

## 3. Controls
- Positive control (positive_control.json, pass = true):
  - known_h agrees for qfbclassno and quadclassunit on {23, 47, 71, 163}.
  - The h=1 list for |D| <= 200 is exactly {3, 4, 7, 8, 11, 19, 43, 67, 163}.
  - The regression slice (2^21, 2^22] gives min S 0.5357676931072192 at D = -2383747, equal to the expected value, with rechecks agreeing.
- Negative control: 0.20324765871906617 (k=26) < 0.20397979320826995 (k=23), so it passes. As the report says, it passes by only 7.3e-4 and the window minima are not monotone. This is disclosed correctly.

## 4. Overstatement check
- The report says this is a finite check and not a proof of H2(b). It is explicit that correctness depends on PARI's documented, unverified unconditional claim for |D| < 2e10. It notes that quadclassunit is GRH-conditional and covers only about 0.04% of the range. It does not present upstream openai/math claims as results.
- The headline "no counterexample ... among 27,356,753 fundamental D" reads correctly as a statement about the computation, which is conditional on qfbclassno.
- Optional wording: "consistent with the D = -163 minimum being a small-|D| effect" is an interpretation, not a tested claim. It is acceptable as written. If this goes into a paper, "suggests" would be better than any stronger word.
