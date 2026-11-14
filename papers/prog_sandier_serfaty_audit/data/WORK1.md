# P1 WORK1: certificate reproduction (S1), negative controls (S1-neg), LeanFlow fail-closed generator (S4)

Date 2026-10-25. All numbers below are from the files in this directory (copied from `/home/callensxavier_gmail_com/programmes-2026-10-25/P1/`). Everything about the triangular-minimality result rests on openai/math material (AI-generated, not peer reviewed) and is conditional on it.

## S1: reproduction of the finite certificate (tier X-exact-integer reproduction, not tier A)

- Sources: `.../Triangular-minimality-for-planar-Coulomb-renormalized-energy-September-23-2026/verification/` (never edited). SHA-256 of `certificate.cpp`, `core.hpp`, `grids.hpp`, `run-certificate.py` equal the hashes in `data/certificate-record.txt` (`53d46bba...`, `c7f76596...`, `4640e0a3...`, `cbef4f4c...`) before and after the run.
- Run: `python3 -I -B run-certificate.py --output-dir .../P1/certificate-run`, cores 0-3 (affinity checked), `OMP_NUM_THREADS=32` as the wrapper hard-codes (so 32 threads on 4 cores), launched 20:23:19 UTC.
- Acceptance conditions (`s1_positive/run-receipt.json`): `exit_status 0`, terminal `OK` (log), `terminal_OK true`, `sources_unchanged true`, `stage_validation.passed true` (all six stages in order, three mesh markers), `wrapper_exit_status 0`. **S1 holds.**
- Wall time: wrapper `elapsed_seconds` 490.35 (20:23:19 to 20:31:30 UTC); child timer `full certificate` 478.001 s (init_core 220.095, calcLam 2.831, calcK 0.319, bdsup 23.643, global_grid 125.407, inside_hess 105.706). The record's 72.6 s was on a 64-core host; no speed comparison is meant.
- Executable sha256 `ca7b5cae54a79c684f08c696a8a182fd9e4d9567701f6975596a26ac2dcddf1f`, `run.log` sha256 `cf6cc0c6fdf8175af35933f9000dfe8cca7edc5714e4922c152b011acb5208f8`.
- Cross-toolchain: g++ 11.4.0 (record: 13.3.0), Boost 1_74 (record 1_83), Python 3.10.12 (record 3.12.13), Linux 6.8.0-1070-gcp (record 5.15 azure). The compile log is empty.
- **All 22 printed pairs equal the saved rows** of `certificate-record.txt` (checked by `scripts/certify_run_outputs.py`: `log_equals_record: true`, 22 vs 22). Key rows (units 1e-7): lambda (-67300312, -67300275), K (-34823, -34809), gmin-factor (120, 162), drneg+er_drop+K (-9944, -4585), det Hess (86252, 1342330).
- Scope (from the corpus README): the wrapper does not read the manuscript; the finite checks rely on the manuscript's analytic bounds, which S2 has not yet audited. The result is a reproduction of an exact-integer interval computation on our hardware, not "verified" or "proved".

## S1-neg: negative controls (separate copies, corpus untouched)

Copy of `verification/` in `.../P1/negctl*/`. Wrapper edit in the copies only: `OMP_NUM_THREADS` taken from the environment (set to 2) and the header regex accepts 2 threads (`negctl.patch`, lower part). Run on 2 cores each.

| Variant | One-line change in `grids.hpp` | Predicted before the run | Result |
|---|---|---|---|
| **S1-neg** (cores 4-5) | midpoint-rule remainder constant in `er0`: `/24` removed (x24) | assertion fails | **REJECTED**: SIGABRT, `exit_status -6`, `terminal_OK false`, `stage_validation.passed false`, failing assertion `(gmin-factor).u>0 && (drneg+er_drop+K).v<0` at `grids.hpp:336`. Printed row: factor (0, 142), gmin-factor **(-7, 162)**. 683 s, ended in `global_grid` (never reached `inside_hess`). |
| **A** (cores 4-5) | `er0` constant `/24` to `/12` (x2) | passes, factor_hi about 20 | **PASSES** end to end: `OK`, exit 0, `terminal_OK true`; factor (0, 20), gmin-factor (114, 162). 1008.9 s. |
| **B** (cores 6-7) | `er_drop` Lipschitz allowance doubled: `Smax*(H/2*Gs+Dh*Gd)` | fails, final lhs about +758 | **REJECTED**: SIGABRT, same assertion; er_drop (0, 10685), last row `(-9944, 758)`. 873.8 s. |

Predictions are in `s1_neg/predictions_AB.txt` (timestamp 20:43:39 UTC, before A and B finished; the S1-neg numbers were already known when the break-even multipliers were estimated, so those are fitted, not blind).

- **Attribution.** Every pair printed before the modified line is identical between the positive run and the negative control (lambda, mu, K, bcon, f0, slope, f(l), all five bounds, gmin, drneg, er_drop); only `factor` (15 to 142) and `gmin-factor` (120 to -7) changed. The failing assertion is the one containing `factor`. Variant A passing through the same edited wrapper at 2 threads is the positive control for the wrapper edits: they are not the cause of the aborts.
- **Margins (derived from the coarsened printed pairs, approximate).** `er0` is about 5.5e-7 and `eri` about 9.5e-7, so the claimed `m_* - E_0 - E_I >= 1.20e-5` survives a midpoint-constant loosening up to about x22 (x2 passes, x24 fails). The negative-part allowance `er_drop` is 5343e-7 against a slack of 4585e-7 (break-even about x1.86; x2 fails). **Observation for S2:** the Lipschitz allowance and the derivative bounds L_1, L_2 behind it are the thin part of the certificate and the Section 6 step ("L_2 h^2/4", `er_drop`) is where the analytic audit should look hardest. It is not a defect found.
- No negative control exercised `inside_hess` (the Hessian positivity block), since both failing variants abort earlier.

## S4: LeanFlow fail-closed data-certificate generator (tier A applies to arithmetic statements only)

- Worktree `/home/callensxavier_gmail_com/LeanFlow-wt-p1`, branch `feat/lean-data-certificates-2026-10-25`, commit `542cea97aa78e30d8935ec81278aeb697a9f5dc7` (local, not pushed). Code `src/leanflow_mcp/lean/`, docs `docs/LEAN_CERTIFY.md`, tests `tests/lean/`.
- `certify(claim, config)`: rational interval enclosures plus linear inequalities over endpoints are turned into one `theorem cert_i : (0:Int) < D ∧ N*RD <= RN*D := by decide` (or `norm_num`) per assertion (Python assembles text from exact integer literals; Lean does the arithmetic), compiled with a configured toolchain, `#print axioms` appended by the checker, and the report parsed. An exact `Fraction` oracle is a second evaluator; disagreement is an error.
- Fail-closed (each with a test): missing toolchain, missing working directory, missing build target (required module with no `.olean`, and a real `import` of a nonexistent module), non-zero rc, killed by signal, rc 0 with no axiom report, timeout, memory cap, `sorry` warning, `sorryAx`, custom axiom, `native_decide`, forged duplicate axiom report, invalid claims (floats, injection text, `lo > hi`, unknown keys; Lean never started), internal exception, oracle disagreement. False statements give `rejected` with the failing theorem names.
- Finding recorded in the tests: on Lean 4.34.1 `native_decide` is reported as `t._native.native_decide.ax_1_1`, not `Lean.ofReduceBool`; a classifier keyed to the old name would label it a generic custom axiom.
- Tests: `82 passed in 23.88s` (`pytest tests/`): 78 core-Lean/pure-Python (including a 300-example Hypothesis property that the rendered Int statement equals the exact `Fraction` oracle, and a 60-assertion mixed true/false random batch whose per-assertion Lean verdicts equal the oracle) and 4 `pinned` tests on Lean 4.34.1 + Mathlib (`norm_num` positive, `norm_num` negative control, `decide`, missing build target); `leanflow_pinned_tests.log`.
- Applied to our runs (`lean_data_certificates/`, script `scripts/certify_run_outputs.py`, core Lean `decide`): the 13 assertions about the **printed** pairs of the positive run (lambda in (-6.731, -6.729), K < 0, f(l) > 0, slope > 0, gmin-factor > 0 and >= 1.20e-5, drneg+er_drop+K < 0 and <= -4.585e-4, g_dd >= 1.0529222, g_xx >= 0.0128335, det >= 0.0086252, ...) are `ok`, tier A, axioms `[]`; the 10 assertions about the S1-neg run's printed pairs are `rejected`, failing exactly the three that contain gmin-factor (`summary.json`). Tier A covers only the arithmetic on the printed outward-rounded integers (display scale 1e-7); it does not show that the C++ computed them.

## Files

`s1_positive/` (receipt, run.log), `s1_neg/` (S1-neg, `A_midpoint_x2/`, `B_lipschitz_x2/` with logs, receipts and patches; `predictions_AB.txt`; launchers), `lean_data_certificates/`, `scripts/certify_run_outputs.py`, `leanflow_provenance.json`, `leanflow_pinned_tests.log`. Working copies: `/home/callensxavier_gmail_com/programmes-2026-10-25/P1/`.

## Not done in this stage

S2 (step-by-step audit of Sections 2-5) and S3 (Lean statement) are other stages. No claim that the Sandier-Serfaty statement is proved is made here.
