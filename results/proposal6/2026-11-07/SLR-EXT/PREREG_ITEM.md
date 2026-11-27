# SLR-EXT preregistration (2026-11-07), written before any search

Question: for which n in 39..94 does an exact shifted-lonely-runner counterexample exist (n distinct positive integer velocities,
rational shifts a_i/D, open arcs ||s_i+v_i t||<1/(n+1) cover R/Z)? Tier C for certificates.

Prior art read (2026-11-07): Poliakova arXiv 2609.23952 (n>=95: start 2,4,..,2N at shift 0, delta=1/(N+1); at odd scale b coprime to 6
remove 8b,32b,192b, rephase 12b..96b to (1+-delta)/2, 16b,64b to -+delta, add 3b,9b at shift 1/4; n=N-1, needs 192b<=2N).
Alphaxiv/web search found no newer paper covering 39..94.

Method (in order): (M1) instantiate Poliakova's rule at N=n+1<=95 and test at the available slack radius 1/(n+1)>1/(N+1) (control: n=95).
(M2) local search (existing cover_ls_fast.c, unchanged) initialised from the even base 2,4,..,2N (minus runners) instead of [n].
(M3) structured search: fix base even velocities at shift 0 except a freed set T, search small rules (removal set R in even velocities,
added set A with |A|=|R|-1, shifts in (1/4)Z + (small multiples of delta)/..) by exact cover check; may prove infeasibility for a grid.
(M4) lifting from n-1 certificates if any.
Controls before counting: s=0 with [n] (N1), tangent case (N0), duplicated velocity, and positive control reproduction of an n>=95 rule instance.
Acceptance: a certificate counts only if slr_exact.py AND check_cover.c both say COVERED at delta=1/(n+1) with exactly n distinct positive velocities.
Kill criterion: budget 60 core-hours total on cores 1-7 (never core 0). If no certificate for any new n after the budget, report NEGATIVE/PARTIAL.
No claim on the unshifted conjecture. Novelty only "to our knowledge".
