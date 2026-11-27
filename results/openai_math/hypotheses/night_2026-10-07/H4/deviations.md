# H4 lane deviations (night 2026-10-07)

Written before the affected runs. Clock at writing: 2026-10-08 ~04:32 UTC; hard stop ~06:00 UTC
(about 90 minutes), while the preregistered stage budgets add up to about 6 h. The preregistration
says "a stage out of budget stops and is reported as such"; the items below say what is cut and in
which order things run.

## D1 (scheduling): stage 2a and N1 run alongside stage 1
Stage 2a (sdi-design seeds 100-104) and N1 (sdi-design degree 4, seeds 200, 201) compute slow
divergence integrals only (no ODE, no cycle counts). They run in the second process slot while the
C3 negative chunks run. No ODE count of the slow-fast family starts before C1-C3 have finished.

## D2 (N2 coverage): matched pairs only
N2 (degree-4 canard negative control) as preregistered repeats the full canard pipeline at all six
eps. That does not fit. For every eps at which stage 2b is run on the degree-6 family, N2 is run at
the SAME eps (same curve/level/count settings). An eps without a matched N2 pass gives numbers that
are reported as observed but are not evidence; P4 cannot pass at such an eps.

## D3 (eps order): 0.003 first, then 0.006 if time remains
The preregistered eps order starts at 0.01. The preregistration's own expectation is that |I_ext|/eps
is larger (more favourable) at smaller eps, and the smoke A curve of the primary family is resolved
at eps = 0.003 (A_spread 3.0e9 ulps) and not at 1e-3. Stage 2b is therefore run at eps = 0.003 first,
then eps = 0.006, then the rest of the grid in preregistered order only if time remains. This choice
is fixed now, before any curve chunk has run.

## D4 (chunking, conditional)
If a 2-sample negative-control chunk exceeds ~200 s or is killed by the 480 s call timeout (the JSON
is written only at the end of a chunk), chunks are reduced to one sample (--idx i:i+1). This changes
chunking only, not the samples or the settings.

## D5 (scheduling, 04:38 UTC): A-curve chunks overlap the tail of C3
C1, C2, N1 and stage 2a are finished (written before any stage 2b run). C3 chunks 2-20 are still
running in slot 1. The `curve` chunks (A(Y) search aid, DOP853, no cycle counts, never evidence) of
the chosen degree-6 F0 at eps = 0.003 run in slot 2 meanwhile. No `count` of any slow-fast family
starts before all ten C3 chunks have finished and passed; if C3 fails, the curve files are kept
but nothing from stage 2b is used.

## D6 (04:58 UTC, written at launch of the first count, before any count result exists)
C3 finished: 20/20 samples, max 1 cycle with Radau and DOP853 (pass). The `count` calls use a shell
`timeout 540` instead of the preregistered per-call 480 s: the count deadline of 480 s stops only
the grid evaluation, and bisection + 3-solver confirmation of each bracket run after it, so a 480 s
shell cap could kill a count before it writes its JSON. 540 s stays under the 9-minute hard limit.
Count settings themselves (grid 160, count deadline 480 s, levels from `level`) are unchanged.
The N2 degree-4 curve also runs in the second slot (curve only, as in D5).

## D7 (05:03 UTC, chunking only)
The deg-6 curve chunk 40:48 took 498 s and the N2 chunk 24:32 took 190 s (large Y is slow). The
remaining N2 curve indices 32:48 run in chunks of 2 (--idx 32:34 ... 46:48) so no chunk is killed
before it writes. Same points, same settings; `level` merges all chunk files.

## D8 (05:33 UTC): N2 stopped out of budget; one MANUAL diagnostic count
N2 curve chunks 42:44 and 44:46 were killed at 470 s (large-Y points > 235 s each); N2 indices
42-47 and all N2 counts cannot finish before 06:00 UTC. N2 is therefore reported as INCOMPLETE
(out of budget), not as passed or failed. Stage 2b for eps 0.006 and later is not started.
Preregistered deg-6 counts at eps 0.003 (top 3 levels) are done before this entry was written.
MANUAL (not preregistered, not evidence, never enters the verdict): one count of the deg-6 primary
family at eps 0.003 with a = -6.398975538645e-4, the midpoint between the sampled A-curve maximum
(-6.3989764754877779e-4 at Y = 2.4655) and the plateau value (-6.3989746018e-4), to check whether the
instrument resolves the 2 crossings of the one visible hump. Same count settings as the
preregistered counts. Output canard/eps_0.003/MANUAL_deg6_count_hump_mid.json.

## Note (context only, no deviation): paper access retry
04:33 UTC: alphaXiv MCP search for the De Maesschalck-Dumortier paper was tried twice; both calls
returned "rate_limit_error ... mcp_upstream_auth_rate_limited". The family stays the reconstructed one.
