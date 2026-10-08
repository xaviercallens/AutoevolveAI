# H5 lane deviations (night 2026-10-07)

Written 2026-10-08 ~04:30 UTC, BEFORE any campaign chunk ran. Code, inputs and the chunk table are
unchanged (sha256 of every frozen file re-checked at 04:29 UTC: all equal to preregistration.json).

1. **Wall-clock truncation.** The campaign starts at ~04:30 UTC and the workflow stops at ~06:00 UTC,
   i.e. ~1.5 h wall instead of the preregistered 3.5 h maximum. Chunks not launched by then are
   reported `missing` (the preregistration already provides this category under its cap rule). No
   chunk spec, seed, count or budget is changed to make it fit.
2. **Two parallel queues.** To respect the order "C00, P01, E01, E2_*, W_* and S_* before A_*" as
   far as the time allows, C00, P01 and E01 run first; then queue 1 runs the E2_* chunks and queue 2
   runs W_* and S_* and then A_* chunks (A_*_walsh_top only after their W_* source exists). At most
   2 python3 processes run at any time, as preregistered.
3. **Priority inside the A_* list** (only an order, nothing dropped by choice): walsh_top N5/N6,
   continuation N5..N7, multiscale N5..N7, then N8 chunks, as long as time remains.
4. **Batching.** Small chunks (C00+E01, W_*, S_*, up to 4 E2_* chunks) are batched in one Bash call
   whenever their summed budget stays under the 9-minute limit; every A_* chunk runs alone in its own
   call. E01 ran in the same call as C00, before P01 (P01 ran seconds later; P01 passed). This
   changes no number.
5. **Added exploratory analysis (NOT preregistered), written 04:33 UTC before it ran.**
   `results/openai_math/hypotheses/night_2026-10-07/H5/holder_bound.py` computes, in exact
   integers, the Hoelder-marginal upper bound B_N = max over sign patterns eps of
   (M0 M1 M2)^(1/3) / 2^N, where W_eps(i,j,k) = sum_t eps_t w_t g0_t(i) g1_t(j) g2_t(k) and
   M0 = max_{i,j} sum_k |W|, M1 = max_{j,k} sum_i |W|, M2 = max_{k,i} sum_j |W|. Since
   S = max_eps sum W_eps F0 F1 F2 and Hoelder with the measure |W_eps| gives
   |sum W F0 F1 F2| <= prod_v (M_v sum |F_v|^3)^(1/3), B_N is a rigorous upper bound on the best
   constant over ALL real inputs at resolution N (not only +-1). It is run for N = 1, 2 and, if it
   fits in < 8 min, N = 3. It is a separate file so that no hashed file changes; it decides nothing
   in the preregistered verdict, and its numbers are labelled exploratory.
6. **A_*_walsh_top chunks BLOCKED by a code bug (found 04:40 UTC).** `_init` reads
   `json["top"]` from the W_* source chunk, but `run_chunk` stores it under `json["result"]["top"]`;
   A_N5_witness_coarse_walsh_top raised KeyError before writing anything. Fixing it would change the
   hashed `h5_multiscale.py` and exclude every chunk, so the six A_*_walsh_top chunks and
   A_N8_witness_coarse_walsh_top are reported BLOCKED (bug), not run.
7. **Verification of the W_N8_witness_x_witness exceedance (written 04:41 UTC, before it ran).**
   That preregistered chunk (controls pass) records a certified ratio^3 = 12167/512 (ratio 23/8) for
   kron(w4, w4), w4 = sign(best_inputs_N4.npz). As preregistered for +-1 candidates, it is
   re-evaluated with `h5_exact.exact_ratio`; in addition (not preregistered) `verify_tensor.py` in
   this lane recomputes it with an independent direct implementation written from the upstream
   definition (explicit Haar vectors, triples enumerated as (n0, n2, n1 = n0 xor n2), a different
   contraction order), saves the witness as `witness_N8_w4xw4.npz`, checks the product rule
   R(f (x) g) = H(g) + |T(g)| R(f) for +-1 f, g (H = Haar part, T = top term), and evaluates the
   triple tensor w4 (x) w4 (x) w4 at N = 12 with the independent code (exact: float64 matmul of
   integers < 2^53). Exploratory beyond the h5_exact recheck.
8. **New test file and exploratory tensor search (written 04:53 UTC, before it ran).**
   `tests/openai_math/test_night_h5_tensor.py` (new, lane-owned) tests the two lane-directory tools;
   the hashed `test_night_h5.py` is left untouched. `tensor_search.py` (lane directory) evaluates,
   with h5_exact and the independent code of verify_tensor.py, the tensor products allowed by the
   product rule at N <= 8: g (x) w4 and w4 (x) g for the N=2 exhaustive argmax g (E2_00 chunk), all
   tensor pairs of the committed N=2..4 witness signs, and reports the best exact value per N and
   the fixed point H(g)/(1-|T(g)|) of iterated tensor powers for each g. Exploratory, not part of the
   preregistered verdict.
9. **Closing (05:12 UTC).** Every preregistered chunk finished by about 05:08 UTC, except the 7
   walsh_top ascents BLOCKED by the KeyError bug (item 6). Those appear as `missing` in
   summary.json. Nothing was lost to the time truncation of item 1. Total chunk time was 3638 s
   (about 1.0 CPU-hour). Tests in test_night_h5_tensor.py were tightened after the first run (two
   assertions that could not fail were replaced) and then rerun.
