# SLR-18 (Proposal 5, lane W1-a): result

**Status: PARTIAL. Contiguous closed range: n in [18, 38]. All certified n >= 18: 18-38.** The certified list for 18 <= n <= 94 is in
`result.json` (`certified_n_ge_18`) and in the table below. Tier C.

## Claim (exact, finite, per n)

For each certified n there is a file `certificates/cert_nNNN.json` with distinct positive integers v_1..v_n, integers
a_1..a_n and D, so that with s_i = a_i/D and delta = 1/(n+1) the **open** bad arcs
{t in R/Z : ||s_i + v_i t|| < delta} cover R/Z. Then max_t min_i ||s_i + v_i t|| < 1/(n+1), so (v, s) is a
counterexample of size n to the shifted lonely runner conjecture (Blanco-Criado-Santos Conj. 1.1(ii); Zhang's
Question 8.5 asks for Gamma(n) < 1/(n+1)).

Each certificate was accepted only after both exact checkers returned COVERED, and all of them were re-checked from
the stored JSON alone by `code/verify_all.py` (`logs/verify_all.json`).

## What is NOT claimed

- No breakthrough. This continues a disproof that already exists: the shifted LRC is already known to fail for
  n in 5..17 (Blanco-Criado-Santos, arXiv 2603.24784 v4, Prop. 5.14) and for every n >= 95 (Poliakova,
  arXiv 2609.23952, Thm 2). Only the n listed as certified are new here, and the gap is closed only up to
  n = 38. n in [39, 94] stays open (no certificate found within the budget). That is not evidence
  that the conjecture holds there.
- Nothing about the unshifted Lonely Runner Conjecture.
- Upper bounds only (gamma_sh(v) < 1/(n+1)). No exact gamma_sh values and no value of E_n beyond E_n > 0 for the
  certified n.
- Not Lean-checked (Tier C, not A). No Lean replay was attempted. The optional `decide` replay is left to the next
  stage.
- For n >= 29 the velocity vectors are **not** [n]. The search swaps velocities, and most of those vectors drop
  the large primes and add smooth numbers up to 2n+2. All velocities are distinct positive integers. The trivial
  repeated-velocity counterexample is never used: both checkers reject repeated velocities.

## Definitions used (read from the sources)

- Blanco-Criado-Santos, arXiv 2603.24784 v4, Def. 1.3: gamma(v; s) = sup_t min_i dist(s_i + v_i t, Z); Conj. 1.1(ii)
  says gamma >= 1/(n+1) for distinct |v_i|.
- Zhang, arXiv 2608.13599 v3, App. A: gamma(v; s) = max_t min_i ||s_i + v_i t||,
  Gamma(n) = min over |v| = n of min over s of gamma(v; s). Question 8.5 asks whether Gamma(n) < 1/(n+1) for every
  n >= 5, and the text says it "is therefore open only for 18 <= n <= 94".
- Strictness: max_t min_i ||.|| < delta  <=>  for every t some i has ||s_i + v_i t|| < delta  <=>  the open arcs
  cover the circle. The maximum is attained, by compactness.

## Method

1. **Checker 1** (`code/slr_exact.py`, Python integers). Every arc endpoint (k - s_i -+ delta)/v_i is scaled by
   M = lcm(v)·D·(n+1) into an integer. A greedy sweep decides whether the open integer intervals cover the closed
   fundamental domain [0, M]. The same file has an exact evaluator of gamma(v; s) (Fractions, all peak and crossing
   candidates), used only for the controls.
2. **Checker 2** (`code/check_cover.c`, `__int128`). This one uses a different criterion and no global common
   denominator: open arcs cover the circle iff every right endpoint of every arc lies strictly inside another
   arc. The test is by cross-multiplication per runner pair. It parses the certificate JSON itself.
3. **Search.** Floating point, untrusted (Tier X); only its rounded output is checked. The successive versions,
   all kept in `code/`:
   - `search.py`, `search2.py`, `smooth.py`, `deletion_probe.py`, `diag.py`: **superseded calibration tools.**
     They do chain-LP min-max descent (HiGHS), continuation in n, a smooth surrogate, and a deletion probe. They
     reached the published optima at n = 5, 6, 8, but failed at n = 9, 10, 12 and could not get below
     1/(n+1) for 12 <= n <= 30 (`logs/calib*.log`, `logs/cont_12_30.log`).
   - `cover_ls.py`: coordinate moves on the uncovered measure at fixed radius
     delta* = 1/(n+1) - 1/(8(n+1)^2). For runner i, the set not covered by the others is folded mod 1/v_i, and
     the best window position is found exactly among the breakpoints. It adds breakout weights and random-walk
     moves, and it certified 5..26 with v = [n].
   - `cover_ls_fast.c` + `fast_driver.py`: a C port of the same search. It was rebuilt several times during the
     run: an acceptance rule, then velocity swaps (w <= 2n+2), tunables, an init file and a full-swap option.
     Certificates 27..38 therefore come from different binary versions. That does not affect validity,
     because only the two checkers are trusted. The final source is hashed in `result.json`.
   - Each float solution is rounded to s = a/D with D >= 2/(1/(n+1) - delta*), and then checked by both checkers.
4. Tried and failed at the frontier n = 35, 36: chain-LP polish of stalled states (`certify_file.py --polish`),
   a joint L1 gap-repair LP (`gap_lp.py`), smooth and zero initial states, continuation from the n-1 certificate,
   a full swap scan, radius slack 64 and 1000, and larger velocity pools (3n, 6n). Stalled states have one to
   three real gaps of length 1e-5 to 1e-3, and gamma about 1/31 to 1/36 (`logs/certify_file.log`,
   `logs/manual_runs_ledger.json`). What worked was repeated short restarts. For example, n = 36 failed in 17
   attempts of 200 s, then succeeded in attempt 3 of a 300 s batch.

## Controls (run before any n >= 18 was counted; all outputs in `logs/controls_run1.json`, `logs/fuzz_agree.json`)

| id | control | outcome |
|---|---|---|
| P1 | gamma_exact((1..5), (0,46,38,47,72)/94) | = 15/94 exactly (argmax t = 45/94); both checkers COVERED at delta = 1/6 |
| P2 | gamma_exact((2,3,4,5,6,8), (0,29,17,0,16,22)/30) | = 2/15 exactly; both COVERED at delta = 1/7 |
| P3 | own shifts for [n], n = 5..17 | all 13 certified by both checkers (`certificates/cert_n005..017.json`, v = [n]) |
| N0 | P1 shifts at delta = gamma = 15/94 (tangency) | both checkers reject |
| N1 | [n], s = 0, delta = 1/(n+1), n = 2..94 | 0 of 93 certified by either checker; gamma_exact = 1/(n+1) checked for n <= 12 |
| N2 | single-shift perturbation by ±1/(10·Σv) | at the published deltas (P1 at 1/6, P2 at 1/7) **0 of 10 and 0 of 12 broke**: the margin is larger than the perturbation, so this is reported, not hidden. At near-tight deltas (gamma + 1/(20Σv)) 4/10 and 5/12 broke. On new certificates: n = 18 10/36, n = 30 4/60, n = 35 5/70, n = 37 5/74, n = 38 6/76 broke (logs/verify_all.json). Checker disagreements: 0 everywhere |
| N3 | s = 0, <= 14 distinct speeds (3000 random sets + 5 known tight sets), delta = 1/(k+1) | 0 certified by either checker (consistent with LRC(<=14), Allikvere arXiv 2609.02604, Tier L) |
| F | agreement fuzz: 600 random small instances × 4 deltas (gamma exactly, gamma ± 1e-6, random) | 2400 tests, 0 mismatches among checker 1, checker 2 and gamma_exact < delta |

Deviation from the preregistered N2 wording: "the covering must break" is false at the published deltas, because
the perturbation is smaller than the margin. The rule was therefore applied per runner, with both signs, and the
number broken is reported, both at the published deltas and at near-tight deltas.

## Table n -> certificate status

| n | status | v = [n]? | max v | D | file |
|---|---|---|---|---|---|
| 5 | CERTIFIED | yes | 5 | 577 | certificates/cert_n005.json |
| 6 | CERTIFIED | yes | 6 | 784 | certificates/cert_n006.json |
| 7 | CERTIFIED | yes | 7 | 1024 | certificates/cert_n007.json |
| 8 | CERTIFIED | yes | 8 | 1296 | certificates/cert_n008.json |
| 9 | CERTIFIED | yes | 9 | 1600 | certificates/cert_n009.json |
| 10 | CERTIFIED | yes | 10 | 1937 | certificates/cert_n010.json |
| 11 | CERTIFIED | yes | 11 | 2305 | certificates/cert_n011.json |
| 12 | CERTIFIED | yes | 12 | 2704 | certificates/cert_n012.json |
| 13 | CERTIFIED | yes | 13 | 3137 | certificates/cert_n013.json |
| 14 | CERTIFIED | yes | 14 | 3600 | certificates/cert_n014.json |
| 15 | CERTIFIED | yes | 15 | 4096 | certificates/cert_n015.json |
| 16 | CERTIFIED | yes | 16 | 4625 | certificates/cert_n016.json |
| 17 | CERTIFIED | yes | 17 | 5184 | certificates/cert_n017.json |
| 18 | CERTIFIED | yes | 18 | 5777 | certificates/cert_n018.json |
| 19 | CERTIFIED | yes | 19 | 6400 | certificates/cert_n019.json |
| 20 | CERTIFIED | yes | 20 | 7057 | certificates/cert_n020.json |
| 21 | CERTIFIED | yes | 21 | 7745 | certificates/cert_n021.json |
| 22 | CERTIFIED | yes | 22 | 8464 | certificates/cert_n022.json |
| 23 | CERTIFIED | yes | 23 | 9217 | certificates/cert_n023.json |
| 24 | CERTIFIED | yes | 24 | 10001 | certificates/cert_n024.json |
| 25 | CERTIFIED | yes | 25 | 10816 | certificates/cert_n025.json |
| 26 | CERTIFIED | yes | 26 | 11664 | certificates/cert_n026.json |
| 27 | CERTIFIED | yes | 27 | 12545 | certificates/cert_n027.json |
| 28 | CERTIFIED | yes | 28 | 13457 | certificates/cert_n028.json |
| 29 | CERTIFIED | no | 55 | 14400 | certificates/cert_n029.json |
| 30 | CERTIFIED | no | 60 | 15377 | certificates/cert_n030.json |
| 31 | CERTIFIED | no | 64 | 16384 | certificates/cert_n031.json |
| 32 | CERTIFIED | no | 60 | 17424 | certificates/cert_n032.json |
| 33 | CERTIFIED | no | 60 | 18497 | certificates/cert_n033.json |
| 34 | CERTIFIED | no | 60 | 19601 | certificates/cert_n034.json |
| 35 | CERTIFIED | no | 72 | 20737 | certificates/cert_n035.json |
| 36 | CERTIFIED | no | 72 | 21904 | certificates/cert_n036.json |
| 37 | CERTIFIED | no | 76 | 23105 | certificates/cert_n037.json |
| 38 | CERTIFIED | no | 75 | 24337 | certificates/cert_n038.json |
| 39 | OPEN (no certificate) | | | | |
| 40 | OPEN (no certificate) | | | | |
| 41 | OPEN (no certificate) | | | | |
| 42 | OPEN (no certificate) | | | | |
| 43 | OPEN (no certificate) | | | | |
| 44 | OPEN (no certificate) | | | | |
| 45 | OPEN (no certificate) | | | | |
| 46 | OPEN (no certificate) | | | | |
| 47 | OPEN (no certificate) | | | | |
| 48 | OPEN (no certificate) | | | | |
| 49 | OPEN (no certificate) | | | | |
| 50 | OPEN (no certificate) | | | | |
| 51 | OPEN (no certificate) | | | | |
| 52 | OPEN (no certificate) | | | | |
| 53 | OPEN (no certificate) | | | | |
| 54 | OPEN (no certificate) | | | | |
| 55 | OPEN (no certificate) | | | | |
| 56 | OPEN (no certificate) | | | | |
| 57 | OPEN (no certificate) | | | | |
| 58 | OPEN (no certificate) | | | | |
| 59 | OPEN (no certificate) | | | | |
| 60 | OPEN (no certificate) | | | | |
| 61 | OPEN (no certificate) | | | | |
| 62 | OPEN (no certificate) | | | | |
| 63 | OPEN (no certificate) | | | | |
| 64 | OPEN (no certificate) | | | | |
| 65 | OPEN (no certificate) | | | | |
| 66 | OPEN (no certificate) | | | | |
| 67 | OPEN (no certificate) | | | | |
| 68 | OPEN (no certificate) | | | | |
| 69 | OPEN (no certificate) | | | | |
| 70 | OPEN (no certificate) | | | | |
| 71 | OPEN (no certificate) | | | | |
| 72 | OPEN (no certificate) | | | | |
| 73 | OPEN (no certificate) | | | | |
| 74 | OPEN (no certificate) | | | | |
| 75 | OPEN (no certificate) | | | | |
| 76 | OPEN (no certificate) | | | | |
| 77 | OPEN (no certificate) | | | | |
| 78 | OPEN (no certificate) | | | | |
| 79 | OPEN (no certificate) | | | | |
| 80 | OPEN (no certificate) | | | | |
| 81 | OPEN (no certificate) | | | | |
| 82 | OPEN (no certificate) | | | | |
| 83 | OPEN (no certificate) | | | | |
| 84 | OPEN (no certificate) | | | | |
| 85 | OPEN (no certificate) | | | | |
| 86 | OPEN (no certificate) | | | | |
| 87 | OPEN (no certificate) | | | | |
| 88 | OPEN (no certificate) | | | | |
| 89 | OPEN (no certificate) | | | | |
| 90 | OPEN (no certificate) | | | | |
| 91 | OPEN (no certificate) | | | | |
| 92 | OPEN (no certificate) | | | | |
| 93 | OPEN (no certificate) | | | | |
| 94 | OPEN (no certificate) | | | | |

## Deviations from the preregistration

- For n >= 29 the velocity sets are modified (velocity swaps), not [n]. The preregistration allows this as method
  (iii), "modified velocity sets". The Poliakova uniform-rule route and the add-a-runner chaining were not used:
  the margins are E of about 0.125, which is too small to chain.
- The N2 perturbation control: see above.
- Criado's repository: only the file listing and `output/consecutive.out` were looked at, at the end, as part of
  the scoop check. That file reaches n = 13 only (gamma_sh(1..13) = 1/16, matching Table 2). Nothing from it was
  used as a seed. `verify_solution.py` was not read.
- Lean replay: not done; left to the next stage.
- CPU: 29.75 core-hours in total (search, calibration and checks; `result.json` has the breakdown, parsed from
  the logs plus `logs/manual_runs_ledger.json`). The ledger entry for controls and checks is an estimate.
  Everything ran on core 1 (taskset -c 1), one process at a time. **Stop reason: the total CPU budget was reached** (driver STOP line in the swap5 log; cap 107000 s cumulative including the ledger offset). Frontier attempts per n (driver logs, n >= 36): n=36: 1/20 attempts succeeded, 4083 CPU-s; n=37: 1/8 attempts succeeded, 2158 CPU-s; n=38: 1/15 attempts succeeded, 4398 CPU-s; n=39: 0/23 attempts succeeded, 6900 CPU-s; n=40: 0/15 attempts succeeded, 4170 CPU-s; n=41: 0/12 attempts succeeded, 3600 CPU-s; n=42: 0/12 attempts succeeded, 3600 CPU-s; n=43: 0/12 attempts succeeded, 3600 CPU-s; n=44: 0/12 attempts succeeded, 3600 CPU-s; n=45: 0/12 attempts succeeded, 3600 CPU-s; n=46: 0/12 attempts succeeded, 3600 CPU-s; n=47: 0/12 attempts succeeded, 3600 CPU-s; n=48: 0/12 attempts succeeded, 3600 CPU-s; n=49: 0/12 attempts succeeded, 3600 CPU-s; n=50: 0/12 attempts succeeded, 3600 CPU-s; n=51: 0/12 attempts succeeded, 3600 CPU-s; n=52: 0/12 attempts succeeded, 3600 CPU-s; n=53: 0/12 attempts succeeded, 3600 CPU-s; n=54: 0/12 attempts succeeded, 3600 CPU-s; n=55: 0/12 attempts succeeded, 3600 CPU-s; n=56: 0/12 attempts succeeded, 3601 CPU-s; n=57: 0/12 attempts succeeded, 3601 CPU-s; n=58: 0/12 attempts succeeded, 3601 CPU-s; n=59: 0/12 attempts succeeded, 3601 CPU-s; n=60: 0/11 attempts succeeded, 3301 CPU-s.

## Novelty / scoop check (2026-10-28, re-checked 2026-10-31)

- alphaXiv `discover_papers` (recency) for "shifted lonely runner conjecture" returned 2609.23952, 2603.24784,
  2506.13379, 2609.06259, 2610.23790 (*Near optimal gap in the Lonely Runner Conjecture*, 2026-10-16, about the
  unshifted ML(V), not read), 2609.02604, 2509.14111, 2512.01912, 2608.13599, 2605.27941, 2607.16082 and
  2609.03444. None of them claims shifted counterexamples for 18 <= n <= 94.
- `published_after: 2026-10-20` for "lonely runner" / "shifted lonely runner" returned only 2610.33190 (cosine sign
  correlations, unrelated).
- Criado's GitHub repository (latest commit 2026-04-24) has outputs only for n <= 13 (`consecutive.out`) and
  n = 5, 6, 7 censuses.
- Re-check on 2026-10-31 at handoff (alphaXiv, published_after 2026-10-24, "shifted lonely runner" / "lonely runner"): 2610.35206, 2610.37711 (view-obstruction for spheres in dimensions 6 and 7), 2610.38135, 2610.37512, 2610.36158, 2610.35819, 2610.40382. None is about shifted lonely runner counterexamples. Titles and abstracts only; none read.
- Not checked: arXiv listings after the alphaXiv index date, and private communications. Scoop risk remains.

## Tiers

- A: none.
- L: the definitions and prior results quoted above (Blanco et al. v4 pp. 2, 4, 37-39; Poliakova pp. 2-5;
  Zhang v3 pp. 18-19; Allikvere p. 1).
- C: each certificate (an exact integer check by two independent programs written here; not Lean).
- X: everything the search produced in floating point (gaps, E estimates, stall diagnostics).

## Limits

- Both checkers were written in this session by the same agent. They use different criteria and different
  languages, but they are not independent authors. A Lean `decide` replay, or a third-party check, is the
  natural next step.
- The search is heuristic. Failure for n > 38 says nothing about whether certificates exist there.
