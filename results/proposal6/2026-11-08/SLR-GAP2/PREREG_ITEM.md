# SLR-GAP2 PREREG (2026-11-08, written before any run)
Claim sought: an exact shifted lonely runner counterexample (n distinct positive integer velocities, shifts s_i, open arcs ||s_i+v_i t||<1/(n+1) cover R/Z) for some n in 39..94, n != 63.
Prior art (2026-11-08): alphaXiv recency search (after 2026-11-01) + WebSearch: nothing covering 39..94 beyond known 2603.24784, 2608.13599, 2609.06259, 2609.23952. Not killed.
Directions (new vs SLR-EXT): (a) base = multiples of b=3 (and mixed 2/3-adic pools) instead of evens; (b) b=2 with odd velocities at shifts 1/2 and wider odd pools; (d) shift menus c/q + j*step, q in {4,6,8,12}, 1/3-type shifts for 3-adic bases; (c) pools allowing several Poliakova-type moves (larger smooth pools, slots up to pool size); (e) local search only if budget remains.
Method: CP-SAT exact set cover (generalised cpsat_rule.py -> code/cpsat_gen.py), same exact integer point model; any SAT is re-checked by slr_exact.covers_open and check_cover.c at radius 1/(n+1).
Tiers: A = Lean kernel (not planned), L = literature, C = computational exact certificate checked by two exact checkers, X = negative/inconclusive.
Positive controls (same code path): n=63 (N=64, b=2, 3-smooth pool, J=8) and n=95 (N=96) must be FEASIBLE and COVERED. Negative control: n=44 (N=45), b=2 smooth pool J=8 must be INFEASIBLE; plus cert re-check fails at radius 1/(n+2)-style perturbation.
Kill criterion: 12 core-hours (wall x workers, cores 1-6) with no feasible cover -> NEGATIVE. Hard compute cap 25 core-h. Every (n, family, pool, J, status, seconds) logged to logs/runs.jsonl.
Outcomes: FOUND (n != 63 covered), PARTIAL, NEGATIVE, NOT NEW. Certificates only under new names, never overwrite. No Lean, no audit, no commit.
