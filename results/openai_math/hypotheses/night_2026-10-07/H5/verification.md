# H5 lane: adversarial verification (2026-10-08)

Verdict: **CORRECTIONS_NEEDED (minor, wording only)**. The verdict and every number checked hold up.

## 1. Preregistration came before the results
- `git log -- preregistration.json`: one commit, c1d7cd5, 2026-10-08 04:28:43 UTC. It is an ancestor of HEAD, and the working file does not differ from the committed one.
- The earliest result is `chunks/C00_controls.json`, mtime 04:30:03. Every file in the lane directory has an mtime after the commit. The prereg's own timestamp field says 2026-10-07T21:49.
- The hashed files (`h5_multiscale.py`, `h5_dyadic.py`, `h5_exact.py`, `test_night_h5.py`, `program.md`) and the input witnesses N4..N7 still match the prereg sha256 values. I recomputed the hashes. Every chunk records the same code and input hashes.

## 2. Numbers, with independent recomputation
- I wrote my own implementation from the definition: explicit Haar vectors, the per-n0 contraction G = F0^T diag(h) F2^T, then a quadratic form against F1. It gives 5/2 for w4 and **23/8 for kron(w4, w4)**. `h5_exact.exact_ratio` also gives 23/8. The saved `witness_N8_w4xw4.npz` equals kron(w4, w4).
- I evaluated the tensor powers of g2 (the E2_00 argmax, with (R, H, T) = (2, 3/2, 1/2)) directly with h5_exact. They give 5/2 at N=4, 11/4 at N=6 and 23/8 at N=8, which equals 3 - 2^(1-r).
- I checked the product rule R(f (x) g) = H(g) + |T(g)| R(f) on 5 fresh random ±1 pairs. It held exactly every time. I read the paper proof in NOTE.md section 2 and found it sound.
- Hoelder-marginal bound: I recomputed it with my own code and got B_1^3 = 1 and B_2^3 = 8, which matches holder_bound.json. I did not recompute B_3^3 = 125/8.
- Kronecker rank of each F_v of w4: 12 (recomputed).
- explain_N4.json: within each level all moduli are equal (8, 32, 256, 1024). Only level -3 saturates (64 of 64). The Walsh support is 256 in each.
- Chunk results:
  - All 32 E2 chunks are complete, with max 2 and the argmax recheck agreeing. E01 gives max 1.
  - S_N5 gives 27/64 (ratio 3/4) and S_N6 gives 1/8 (ratio 1/2).
  - The W lift maxima are float 2.5, with no certified exceedance.
  - The 18 A chunks have best values from 2.4999185665 to 2.49999999995.
  - Summed elapsed_s is 3637.61.
- The walsh_top KeyError bug is real: line 666 reads `["top"]`, but the W chunks store `result.top`. No walsh_top chunk exists.
- pytest on test_night_h5.py and test_night_h5_tensor.py: 20 passed in 1.48 s on my rerun.

## 3. Controls
- `controls.pass` is true in all 83 chunk JSONs. That covers the constant input, the 5/2 witness, the ones-lift, int vs float, int vs brute force, the gradient, Haar-free 64/343, and the exhaustive cross-checks.
- Power control P01 passed: the quantized, sign and high-precision versions were all certified. The sign-rounded value is exactly 5 (ratio^3 = 125).
- holder_bound has its own controls: Haar-free B^3 = 27 and 64.

## 4. Overstatement check (corrections)
1. "Proved" for the product rule, C* >= 3, C_1 = 1 and the Hoelder bound means a paper proof written by this lane. Nobody else has reviewed it and it is not Lean-checked. Say so in the headline: "a product rule proved on paper in NOTE.md (not machine-checked)".
2. C_3 <= 5/2 rests on holder_bound.py alone. This verifier did not recompute it.
3. The N=12 value 95/32 comes only from the lane's verify_tensor code, not h5_exact. NOTE.md says so; the report's numbers list should too.
4. In the report, "per-chunk best between 2.49991857 and 2.49999999": the top value is really 2.49999999995 (rounded down). It is still < 5/2, so nothing changes.
5. Novelty of C* >= 3 / H5'' is unchecked. The report should say so, as NOTE.md does.
6. Nothing on disk confirms that the deviations were written "before each affected run". deviations.md is a single untracked file last modified at 05:11.
7. tensor_search.json gives fixed_point "inf" for ones_N1 (H = 0, T = 1, so 0/0). The tensor powers stay at 1, as NOTE.md says. This is a cosmetic error in the exploratory output.
