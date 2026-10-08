# Deviations, lane LT_A (2026-10-08)

Frozen instruments (instrument.py, controls.py, campaign.py) are unmodified. Verdict rule and metric unchanged.

## D1 (before any further run, written 2026-10-08 ~11:25 UTC): process-level scheduling, not the instruments
Observed in the first chunk (real output, cells/g0.75_random_K2P8_c00.json): one gamma = 0.75, M = 320 restart takes about
400 s with --threads 2 (preregistration assumed 15-90 s). With a 420 s budget one restart completes; the second concurrent
job (g0.75_embed, seed block 1040-1079) was killed by the driver's 520 s hard timeout before campaign.py wrote its JSON
(campaign.py writes the JSON only at exit). That job produced NO result and is excluded; its seed block 1040-1079 stays
marked used in seed_ledger.json (seeds never reused). Its stray .pt (best_seed1040) is not a result.
Consequence: chunk-per-call with budget 420 cannot reach >= 12 restarts for gamma = 0.75. Change: new lane-owned file
scripts/openai_math/lt_matrix/lt_a_bg.py runs a queue of the SAME campaign.py commands (same flags, same M rule, --threads 2,
at most 2 concurrent processes) as detached background processes with a larger --budget-s (restarts count is the stop rule:
--restarts 12 per job), polled from short Bash calls. No Bash call blocks beyond 9 minutes. Nothing about numerator/denominator,
grids, thresholds or flags-per-restart changes.

## D2 (12:25 UTC): queue 2
Round 1 (12 base cells at gamma 1.0/1.25/1.4, 12 restarts each) done via lt_a_bg.py; no flagged restarts. Queue 2 = K=3,P=10 random cells,
two autoresearch continuation chunks (twist at gamma 1.25 and 1.4, fresh seed blocks; one factor changed = seed block), then the gamma = 0.75 cells
(M = 320, ~400 s/restart, budget 6000 s, 12 restarts; random cell needs 11 more beyond chunk c00).

## D3 (14:40 UTC): queue 3, autoresearch round
Queue 2 finished; no flagged restart anywhere. Best cells are the twist family (closest to L1: g1.25 -2.8e-7, g1.4 -3.4e-7). Changes, one factor each:
seed block (g1.25_twist c02, g1.4_twist c02), K/P (twist K=3,P=10 at g1.25 and g1.4), then the remaining twist cells g1.0 and g0.75 get a fresh seed block.
Kept if best excess rises above the parent's. Note: the 400 s/restart figure in D1 came from the first, contended chunk; the later g0.75 cells needed about 220 s/restart.
