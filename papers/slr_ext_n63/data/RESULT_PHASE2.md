# SLR-EXT phase 2 (2026-11-08): second member of the n=63 family? Outcome: NO NEW n. Tier C / X.

## Incident (fixed)
Phase-2 `cpsat_rule.py` wrote `certificates/cert_n063.json` for N=64 (pool p5, tag sw3_p5), overwriting the audited file. Restored byte-for-byte from
papers/slr_ext_n63/data/certificates/cert_n063.json (sha256 9ee9c38f...e78e9). The overwriting solution is kept as `certificates/cert_n063_alt_sw3_p5.json`
(sha256 dfc8b4d7...8d7a): both checkers COVERED (n=63, 3961 endpoints), a different valid n=63 solution (e.g. shifts of 1 and 9 differ). The writer now never overwrites (suffix _alt_<tag>_<k>).
RESULT.md / result.json of the audited item were not touched by phase 2 (result.json last written in phase 1; code/cpsat_rule.py has changed since, so its hash there is stale).

## Template (a)
`code/template.py`: Poliakova move as (removed, rephased, added) with shifts c/4 + beta*delta. POL reproduces n = 95..109 (covered); the n=63 member N63 reproduces n=63 at N=64.
`code/tpl_scan.py`: N63 applied with delta = 1/(N+k), k=-1..2, for N = 64..129: covered ONLY at N = 64 (k = 1, 2). So the n=63 move is not uniform in N.
It also needs the open-radius slack and the coincidence 128 = 2N, 1/N = 2^-6.

## Exact CP-SAT per N (cores 1-6, 120 s limit, J = 8)
- smooth pool (3-smooth multiples of 4 + {3,5}-smooth odds): INFEASIBLE for every N = 39..59 (`logs/cpsat_p2_smooth8.log`) and, with phase 1, for every N = 39..95 except N = 64.
- p5 pool (5-smooth): N=64 FEASIBLE (alt solution); INFEASIBLE N = 47, 46, 45, 43, 39; UNKNOWN N = 63..48, 44, 42, 41, 40 (`logs/cpsat_p2_p5.log`).
- s23e pool (any 3-smooth even, {3,5,7}-smooth odd): UNKNOWN at 120 s for N = 64, 62..54 (too large; even the positive control N=64 timed out) (`logs/cpsat_p2_s23e.log`).
Not run: scales b in {5,7,11,13}: a scaled rule has L*b <= 2N, and no rule with L below 128 is known, so they cannot apply for N < 64*b... (argument, not a computation).

## Conjecture (evidence only)
Within 3- and 5-smooth pools with shifts c/4 + j/(8(N+1)), the only N in 39..95 admitting a cover is N = 64 (n = 63). Not a theorem; UNKNOWN cases remain.

## CPU ledger phase 2
smooth8 about 0.5, p5 about 5.4, s23e about 2.2 core-h (wall x 6); total about 8 of the 20 allowed. Phase 1 about 16. Stopped early: no new n, remaining work is UNKNOWN-heavy.
