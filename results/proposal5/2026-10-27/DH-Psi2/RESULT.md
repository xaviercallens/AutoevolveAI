# DH-Ψ2: exhaustive Ψ = H + 3|T| over all sign inputs at resolution 2

Proposal 5, item 4 (lane W1-d). Preregistration `results/proposal5/2026-10-27/preregistration.json`.
Its sha256 was `140a28ad…ae9be` at the start and is the same at the end; the file was not edited.
Producer run, not yet audited. Prereg dated 2026-10-27; run started 2026-10-28 17:06 UTC (`logs/prereg_sha_start.txt`), C enumeration finished 18:29 UTC; the producer session was then cut off by a spend limit and aggregation resumed 2026-10-31. No data lost: chunk writes are atomic (tmp -> rename), 0 `.tmp` files remain, and every mode has contiguous F0 coverage [0, 32768).

## Outcome: KEEP (Tier C, sign inputs, resolution 2 only)

Over all 2^48 sign inputs F ∈ {±1}^{3×4×4} at resolution N = 2:

- **max Ψ(F) = 3 exactly.** No input exceeds 3. Two independent full enumerations agree on this.
- 0 of the 2^30 reduced (F0, F1) pairs have max over F2 of Ψ greater than 3.
- 4,608 reduced (F0, F1) pairs attain Ψ = 3 with some F2. The constant input is one of them, and the seed g attains Ψ = 3 as well (controls below).

So Conjecture 1 of doi:10.5281/zenodo.23232389 holds for **sign inputs at resolution 2**. No erratum is needed.

What this does not cover:
- real-valued inputs, at any resolution;
- resolutions N ≥ 3;
- the value of C*.

The paper had already proved resolution 1 and had computed max R = 2 at resolution 2. This run adds the exhaustive Ψ check at resolution 2. It is a finite verification of our own conjecture in a special case, nothing more.

## Method

- **Objective.** S_w(F) = 64·(w_T|T| + H), with w_T = 3 for Ψ. The test is Ψ ≤ 3 ⇔ S_3 ≤ 192. All quantities are integers.
- **Symmetry.** Every term L_I and T is trilinear in (F0, F1, F2). So F_v → −F_v leaves every |term| unchanged, and we fix F0[0,0] = F1[0,0] = +1. That leaves 2^15 · 2^15 = 2^30 pairs.
- **Reduction over F2.** For fixed (F0, F1) each of the six terms (T, the level-0 triple, the four level-1 triples) is linear in F2. Therefore
  max_{F2 ∈ {±1}^16} Σ_t w_t|⟨c_t, F2⟩| = max_{s ∈ {±1}^6, s_0 = +1} ‖Σ_t s_t w_t c_t‖₁.
  This is the same reduction as the 2026-10-07 R run.
- **Enumeration 1 (Python kernel).**
  - Code: `code/psi_exhaust.py`, a parameterised re-implementation of the night-lane kernel. The pinned file `scripts/openai_math/hypotheses/night/h5_multiscale.py` was not edited.
  - Arithmetic: int64 coefficients, then a float32 matmul. The matmul is exact because a guard checks that every partial sum is below 2^24.
  - Rechecks: every per-F0 argmax (32,768 per mode) was rechecked by an independent block-slicing evaluator (`direct_value`) and by the preregistered second evaluator `h5_exact.py`. With h5_exact, Ψ = R + 2T. All 32,768 of 32,768 agree in every mode.
- **Enumeration 2 (C, integer-only).**
  - Code: `code/psi_exhaust.c`, written from eq. (trace) with no floating point.
  - Pattern search: Gray-code order over the 32 sign patterns.
  - Rechecks: the argmax is recomputed by a literal triple sum.
- **Agreement.** For every mode, the full histograms of max_{F2} S over all 2^30 pairs are identical between the two enumerations, and so are the maxima and the violation counts.
- **Brute-force check of the ℓ₁ reduction**, against a literal max over all 2^16 F2:
  - Python: 300 random pairs per mode × 5 modes, all agree.
  - C: 200 pairs for Ψ, 100 for PLANT4, 100 for HF_Ψ, all agree. Both C halves used the same seed, so these are duplicate pairs, not 2×.

## Controls (all passed before the Ψ numbers were counted)

| control | expected | obtained |
|---|---|---|
| positive: exhaustive max R | 2 | 2 (4,096 maximising pairs) |
| positive: Ψ(constant) | 3 | 3 |
| positive: seed g from `tensor/rigor.json` | H = 3/2, T = 1/2, R = 2, Ψ = 3 | the same (Python only: h5_exact and `direct_value`; the C code does not evaluate g) |
| negative: Haar-free max R | N + 1 = 3 | 3 |
| negative: Haar-free Ψ exceeds 3 | > 3 | max 5; 7,356,928 pairs > 3 |
| negative: planted w_T = 4 finds violations | yes | max 4 (at the constant); 741,888 pairs > 3, in 7,360 F0 values. Violating values include 49/16 … 7/2, so the search also detects violations away from the constant input |
| evaluator agreement on random inputs | 2000/2000 | 2000/2000 (w_T = 1, 3, 4) |

The binary `code/psi_exhaust` is a machine-specific `-march=native` build artifact; an auditor must rebuild from `code/psi_exhaust.c`.

Files: `data/controls.json`, `data/summary.json`, `data/chunks/*.json` (160 chunks), `data/c_enum/*.json`.

## Kill criterion and cost

- **1% sample.** F0 ∈ [0, 328), Ψ mode: 40.9 s. That projects to 1.14 core-h for Ψ and 5.7 core-h for all five Python modes, against a threshold of 60 core-h. The kill criterion did not fire (`logs/kill_criterion_projection.json`). The sample showed max Ψ = 3.
- **Actual cost.** Python summed 25,964 s over 160 chunks, about 7.2 core-h, but cores 4 and 5 were shared with the C run during that time. The C run took about 80 min wall on the same two cores. The total is about 10 core-h or less. Only cores 4 and 5 were used.

## Elementary-attack pass (repeated, as required)

- Proposition `prop:level` gives |T| + |L_000| ≤ 1 and Σ_{level 1} |L_I| ≤ 1. Hence Ψ ≤ 2 + 2|T| ≤ 4 at N = 2.
- Closing the gap from 4 to 3 needs the even/odd coupling between T and the fine level, and that does not tensorise.
- No short proof was found. The result above is computational only.

## Literature

- The conjecture is ours (doi:10.5281/zenodo.23232389). To our knowledge it has not been addressed elsewhere.
- No novelty search was preregistered ("none needed").

## Tiers

- **Tier C.** "max Ψ = 3 over all sign inputs at resolution 2" is an exhaustive enumeration with exact integer arithmetic. The first enumeration uses float32 that is exact under the stated 2^24 guard; the second is pure-integer C. The two agree on the full histogram.
- **Tier A.** Nothing. Lean was not called for, because there is no violation, and a 2^48 enumeration is not a `decide` target.
- **Tier X.** None used.

## Deviations from the preregistration

1. The prereg names the `scripts/openai_math/hypotheses/tensor/` evaluator. The exhaustive F2-reduction kernel actually lives in `scripts/openai_math/hypotheses/night/h5_multiscale.py`. That file was not modified. A parameterised copy is in `code/psi_exhaust.py`, and `h5_exact.py` was imported read-only.
2. Added to the plan: an independent integer-only C full enumeration, plus rechecks of every per-F0 argmax rather than only the global one.
3. Lane W1-d was budgeted for 1 core. Cores 4 and 5 were used, as assigned in the task.

## What an independent auditor must redo

1. Rebuild `code/psi_exhaust.c` (gcc 11.4, `-O3 -march=native`) and rerun `c_runs.sh 0` and `c_runs.sh 1` (about 1.5 core-h). Check that max_S = 192 for w_T = 3 with Haar signs, and that the violation count is 0.
2. Re-derive the six term definitions from eq. (trace) (level-1 Haar sign h1(x) = +1 for even x; weights 1 / 1 / 2 in units of 1/64). The term set is already cross-validated against the independently authored `h5_exact.py`: 2000/2000 random inputs at w_T = 1, 3, 4, all 32,768 per-F0 argmaxes in every Haar mode, and the C argmax of every mode. The residual common-mode risk is narrower: the shared F0[0,0] = F1[0,0] = +1 convention and the shared l1 reduction over F2, which is covered only by brute force on random (F0, F1) pairs (Python 1500, C 400 distinct).
3. Recheck that fixing F0[0,0] = F1[0,0] = +1 loses nothing.
4. Compare `data/summary.json` histograms against an independent rerun of at least the Ψ and R modes.
