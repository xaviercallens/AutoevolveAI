# SLR-EXT (2026-11-07): shifted lonely runner, n = 39..94. Outcome: PARTIAL, FOUND for n = 63 only. Tier C.

Prereg: PREREG_ITEM.md (sha256 in PREREG_ITEM.md.sha256, written before any search).

## Result
- **n = 63** certificate: `certificates/cert_n063.json` (63 distinct positive velocities in 1..128, D = 520, delta = 1/64, open arcs cover R/Z).
  Accepted by `code/slr_exact.py` and `code/check_cover.c` (COVERED, 3961 endpoints); re-verified independently by the coordinator (own Fraction script).
  Exact: gamma = max_t min_i ||.|| = 66/4225 (at t = 4291/8450) < 1/64; gap 1/270400 (independent audit); min endpoint slack about 3.8e-6.
- Not claimed: anything about the unshifted LRC; this gives E_63 >= 1/66 only (not E_63 >= 1); any other n in 39..94; Lean replay: `cover` kernel-checked (standard axioms), `v_injective` failed (maxRecDepth, sorryAx); file rc = 1, so no Lean gate pass (later fixed by set_option maxRecDepth 1000000, see paper). Novelty "to our knowledge" only.

## Prior art (2026-11-07)
Poliakova arXiv 2609.23952: start 2,4,..,2N at shift 0; at odd scale b coprime to 6 remove 8b,32b,192b, rephase 12b,24b,48b,96b to (1+-delta)/2,
16b,64b to -+delta, add 3b,9b at 1/4; needs 192b <= 2N, hence n >= 95. (The paper's Sec. 3 and Table 1 differ in signs for 48, 96, 64; both variants
verified here to cover at n = 95..109, `code/rule.py`.) alphaXiv recency searches (after 2026-03-01 and after 2026-09-20) and a web search found no paper
covering 39 <= n <= 94 and none proving the conjecture in that range; Zhang 2608.13599 still lists it open. No conflict with our result.

## Method and structure
`code/cpsat_rule.py`: base 2,4,..,2N (N = n+1) at shift 0, open radius 1/N = 1/(n+1) (slack over Poliakova's closed radius 1/(N+1)). A pool of 3-smooth multiples of 4
and {3,5}-smooth odd velocities may be removed, rephased or added, with shifts c/4 + j/(8(N+1)), |j| <= 8, using at most |pool evens| - 1 runners. Exact integer
points (all arc endpoints and cell midpoints inside the part left uncovered by the fixed runners) feed a CP-SAT set cover. Positive control N = 96: the model is feasible with
the Poliakova rule fixed (certified n = 95, `controls_certs/cert_n095.json`); an unfixed solve also found a cover in 0.6 s.

n = 63 (N = 64): removed evens {4, 8, 32, 72, 96, 108}; rephased 12, 24, 36 to (1+e)/2 (264/520), 48 to (1-e)/2 (256/520), 16 and 128 to -e (512/520), 64 to +e (8/520), where e = 1/65 = 8/520 is the rephasing offset (the cover radius is delta = 1/64);
added odd runners 1, 3, 9, 27, 81 at about 3/4 (385, 390, 388, 391, 391 over 520). So it is a Poliakova-type replacement whose largest rephased velocity is 128 = 2N instead of 192,
with odd powers of 3 near shift 3/4 filling the gaps; it relies on the open-radius slack. It is sporadic: the same pool is INFEASIBLE for N = 65..95 and for N = 60..63.
Why it does not extend uniformly is not understood; no general rule was proved.

## Negative results (CP-SAT, exact: "no cover for this pool, menu and N"; nothing about the conjecture)
- Pool = 3-smooth multiples of 4 + {3,5}-smooth odds <= 2N, J = 8 (`logs/cpsat_sweep1.log`, `cpsat_smooth_cont.log`): INFEASIBLE for N = 95..65 (N = 72 needed 600 s) and N = 63..60; N = 64 FOUND.
- J = 16 (`logs/cpsat_smooth_J16.log`): INFEASIBLE N = 47, 46, 44; UNKNOWN at 120 s for N = 63..48, 45, 43..40.
- Larger pools (5-smooth, s23e, all multiples of 4): UNKNOWN at 120-400 s (`cpsat_sweep_p5.log`, `cpsat_s23e.log`).
- Random local search from an even base (`logs/even_run1.log`, `frozen1.log`): best uncovered measure 1.2e-4 (n=94), 1.8e-4 (n=90), 4.6e-4 (n=80), 4.9e-4 (n=70), 4.3e-4 (n=60), 3.2e-4 (n=50).
  The 1.2e-4 is the tight state 2*[n] searched at slightly sub-radius, not a near miss. No success.

## Controls
Positive: Poliakova rule N = 96 (n = 95) COVERED by both checkers; `rule.py` n = 95..109. Negative (`logs/final_checks.json`): s = 0 with [63] rejected; duplicated velocity rejected;
cert not covered at radius 1/65 (not trivially loose); one-shift perturbation by +-1/(10 sum v) broke 3 of 126 cases. SLR18 controls (P1, P2, N0, N1, N2, N3) re-run with `code/controls.py` (rc 0, `logs/controls_run.log`).

## CPU ledger (upper bound; CP-SAT counted as wall x 7)
Even-base local search about 1.4 core-h; logged CP-SAT runs 11.8 core-h; unlogged (N=96 controls, wide pool 400 s, s23e J=16 150 s) about 2 core-h. Total about 15-16 of 60 core-h, cores 1-7 only.
A host reboot happened during the run; the final sweep finished (all log lines present). Remaining budget unused.

## Deviations
- `cover_ls_fast.c` patched (SLR_FREE env freezes the first runners); no result depends on it.
- ortools venv at ~/.cache/slrvenv (outside repo; the first one in /tmp was wiped).
- Superset pruning of cover constraints only drops implied constraints.

## What an auditor must redo
Both checkers on `certificates/cert_n063.json`; re-derive the Poliakova rule; rerun `cpsat_rule.py 64 8 60 x`; Lean: see the Update below (the audit's own first compile failed on v_injective; the fixed file later compiled rc 0).

## Update 2026-11-08 (after the audit; audited fields above unchanged)
- Lean: the maxRecDepth-fixed file was compiled twice by the main session through the same runner (`lean_pinned.py`; rc 0 in 3327.6 s and rc 0 in 2028.2 s, identical axioms: cover and v_injective [propext, Classical.choice, Quot.sound], v_pos [propext]). Not an independent auditor's compile; not through anse/formal/lean_runner.py; no statement lock.
- Phase 2 (RESULT_PHASE2.md): within the pools and shift menu tried, N = 64 (n = 63) is the only N in 39..95 admitting a cover (evidence, not a theorem; UNKNOWN cases remain). A second valid n = 63 solution `certificates/cert_n063_alt_sw3_p5.json` (sha256 dfc8b4d7...8d7a) exists: both checkers COVERED, not audited, not Lean-checked. Phase 2 about 8 core-h; total about 24.
