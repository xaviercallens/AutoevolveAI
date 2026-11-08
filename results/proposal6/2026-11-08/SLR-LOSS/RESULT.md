# SLR-LOSS (2026-11-08): NEGATIVE (no n with gamma strictly below Poliakova's rules). Tier C numbers only; nothing new claimed.

Prereg: PREREG_ITEM.md (+ .sha256, written before any run). Prior art, same day: alphaXiv discover_papers + WebSearch found only 2609.23952, 2603.24784, 2608.13599, 2609.06259; no sharper bound for n>=95.

## E1 baseline (exact; `code/baseline.py`, logs/baseline.log, configs certificates/baseline_*.json)
Exact gamma = max_t min_i ||s_i+v_i t|| by bisection with the exact open-cover checker, then exact crossing evaluation in Fractions; confirmed per config: open cover FAILS at gamma, COVERS at gamma(1+1e-9).

| n | Sec.3 9->8 rule (g=1) | Table 1 19->17 rule (g=2, needs n>=118) | best baseline |
|---|---|---|---|
| 95..117 | exactly 1/(n+2) (every n checked) | not applicable (240 > 2N) | 1/(n+2) |
| 118..140 | 1/(n+2) | exactly 1/(n+3) (sign variants ++++ and ---- both cover) | 1/(n+3) |

Examples: n=95 1/97; n=118 rule9 1/120, rule19 1/121; n=140 rule9 1/142, rule19 1/143. Her E_n>=1 (n=95..117) and E_n>=2 (n>=118) are attained with equality (no slack).

## E2/E3 CP-SAT re-optimisation (`code/cpsat2.py`: gain g, base 2..2N, N=n+g, rational open radius rp/rq)
Controls. New gamma routine on SLR-EXT cert_n063: 66/4225 (matches audit). Positive: unfixed CP-SAT, 5-smooth pool, reduced shift menu c/4 + j/(8(N+1)), j in {0,+-2,+-4,+-8,+-16}, g=2, n=118, r=200/24199: OPTIMAL in 11 s, both checkers COVERED (`certificates/cert_n118_g2_rj_n118.json`), exact gamma 1/121 = Poliakova's (a tie, not an improvement). Negative: n=95 g=1 at strict 1/97 INFEASIBLE (0.1 s). Full 33-shift menu (5148 vars) never found even this known solution (UNKNOWN, 600 s): menu size decides solver power.

Results (within the stated pool and menu; INFEASIBLE = exact solver verdict, UNKNOWN = no verdict):
- g=2, strict open radius 1/(N+1)=1/(n+3), which would beat the Table 1 rule: n=118, 120, 130, 140 INFEASIBLE (1-6 s); n=125 UNKNOWN (150 s). Pool s235e, 33 shifts, 2 workers, 250 s: n=118, 130, 140 UNKNOWN.
- g=2, radius 8/(8N+1) (gamma < 1/(n+2.125), would beat the 9->8 rule), n=95,97,102,107,112,117: UNKNOWN (150 s each). Radius 2/(2N+1), n=100,105,110,117 (full menu, 600 s): UNKNOWN; n=117 reduced menu, 3 workers, 400 s: UNKNOWN.
- One wide4-pool run died (empty log, memory pressure); not counted.
No certificate with gamma strictly below the baseline exists. The INFEASIBLE verdicts say the tight base cannot be improved at g=2 by this pool/menu; they are statements about the search space, not about E_n.

## Structure note
Poliakova's configurations are exactly tight (gamma = delta). A strict improvement at fixed g must cover the tight points left by the unchanged evens using added/rephased runners; none found. Beating her at n<118 needs gain-2 rules with largest velocity < 2N < 236; none found (UNKNOWN, solver-limited).

## Verdict
NEGATIVE / inconclusive. Stopped at about 2.9 core-h (kill criterion 6 core-h not reached; stopped because the control showed the solver cannot decide the interesting cases at this scale, and further waiting on UNKNOWN had low expected value). Not worth an independent Opus audit or Zenodo.

## CPU ledger (wall x workers, upper bound, cores 1-6 only)
baseline 0.02; first g=2 tests 0.42; p5 full-menu 0.83; reduced menu rj 0.67; rk 0.25; rs 0.27; s235e 0.43; total about 2.9 of 20 core-h. No Lean, no commit. File hashes: result.json.
