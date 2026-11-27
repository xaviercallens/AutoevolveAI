# SLR-EXT independent audit (2026-11-08)

Auditor: independent Claude agent (producer != verifier). Scope: `certificates/cert_n063.json` (sha256 9ee9c38f...e78e9, matches result.json), RESULT.md, Lean replay `/tmp/slr63/`.
Script and log: `/tmp/slrextaudit/audit63.py` (own code, written from scratch; not the producer's checkers and not `verify63.py`). Ran on core 6.

**Verdict: ACCEPT_WITH_CORRECTIONS.**

## 1. Definition (Poliakova 2609.23952 Sec. 1; BCS 2603.24784)
One runner fixed at 0, n runners with distinct positive integer velocities v_i and shifts s_i in R/Z. SLR asserts
gamma(v;s) = max_t min_i ||s_i + v_i t|| >= 1/(n+1). So a counterexample is the same thing as gamma < 1/(n+1), which in turn is the same as the open arcs ||s_i+v_i t|| < 1/(n+1) covering R/Z (gamma is attained because the function is continuous on a compact set).
The certificate meets this: n = 63 runners, 63 distinct velocities in 1..128, all positive, D = 520, a_i in [0,512] so s_i in [0,1), delta = 1/64 = 1/(n+1). The 51 shift-0 runners are exactly the evens 2..128 minus the removed set {4,8,32,72,96,108} minus the rephased set {12,16,24,36,48,64,128}.

## 2. Own exact check
- Exact integer interval union over the common denominator (open intervals, wrap handled): **COVERED at r = 1/64**.
- gamma computed exactly. Candidate set: all pairwise crossings s_i+v_i t = ±(s_j+v_j t) mod 1, 331,632 candidates. A float pre-filter keeps the 4 top values, which are then evaluated exactly with Fractions:
  **gamma = 66/4225 = 66/65^2 ≈ 0.0156213, reached at t* = 4291/8450; gap 1/64 − gamma = 1/270400 ≈ 3.70e-6.**
  An independent exact cross-check: the cover FAILS at r = gamma (tangent) and HOLDS at r = gamma + 1e-12.
- This gives E_63 >= 4225/66 − 64 = 1/66 (Poliakova's E_n), not E_63 >= 1.

## 3. Adversarial tests
- r = gamma: not a strict cover (uncovered point found). Correct.
- r = 1/65: NOT covered (uncovered point at t ≡ 1/130). This matches the producer.
- Duplicate velocity (81 replaced by 27): fails distinctness. Correct.
- Each shift perturbed by ±1/(2D): 83 of 126 perturbations break the cover. The certificate is not trivially loose.

## 4. Lean (/tmp/slr63, not re-run)
In SLRN63.lean, v, s and the radius `1 / 64` match the certificate exactly (checked by parsing the file). compile.log: **rc = 1**, 3304 s.
- `cover` is accepted. It depends only on [propext, Classical.choice, Quot.sound].
- `v_pos` is accepted ([propext]).
- `v_injective` FAILED: `decide` hit "maximum recursion depth" at line 12, so it depends on sorryAx.
So the covering statement is kernel-checked, but the Lean file as a whole does not pass the gate. Distinctness is verified only in Python, by two independent scripts. Possible fix: use `set_option maxRecDepth` or prove `List.Nodup` with `decide` on a list. The run did not go through `anse/formal/lean_runner.py`.

## 5. Literature (alphaXiv, 2026-11-08, two queries, one with published_after 2026-10-01)
No paper covers the shifted conjecture for any n in 18..94, and none proves it there. Poliakova (Sec. 1, p. 3) states that 18 <= n <= 94 remains open.
The producer's description of Poliakova matches her paper:
- start from 2,4,..,2N at shift 0, with δ = 1/(N+1) and a closed δ-cover;
- a "nine replaced by eight" rule at an odd scale b coprime to 6;
- R = {8,32,192}; 12,24,48,96 rephased to (1+δ)/2; 16,64 rephased to −δ; 3,9 added at 1/4;
- L = 192, which gives n >= 95.
Her Table 1 has the 9→8 variant with 48,96 at (1−δ)/2 and 64 at +δ. The producer's note on the sign difference is correct.

## 6. Corrections (RESULT.md, exact old -> new)
1. "rephased 12, 24, 36, 48 to (1+delta)/2 (shift 264/520), 16 and 128 to -delta (512/520), 64 to +delta (8/520), delta = 1/65;" ->
   "rephased 12, 24, 36 to (1+e)/2 (264/520), 48 to (1-e)/2 (256/520), 16 and 128 to -e (512/520), 64 to +e (8/520), where e = 1/65 = 8/520 is the rephasing offset (the cover radius is delta = 1/64);"
   (The certificate has 48 at 256/520, not 264. Calling both 1/64 and 1/65 "delta" is inconsistent.)
2. "Tight: sampled max_t min_i ||.|| = 0.0156212 vs 1/64 = 0.015625; min slack about 3.8e-6." ->
   "Exact: gamma = max_t min_i ||.|| = 66/4225 (at t = 4291/8450) < 1/64; gap 1/270400 (independent audit); min endpoint slack about 3.8e-6."
3. After "Not claimed: anything about the unshifted LRC;" add: "this gives E_63 >= 1/66 only (not E_63 >= 1);"
4. "Lean check (Tier C only)" -> "Lean replay: `cover` kernel-checked (standard axioms), `v_injective` failed (maxRecDepth, sorryAx); file rc = 1, so no Lean gate pass".
5. Wording to keep: counterexample to the SHIFTED conjecture at n = 63 only; sporadic (the same pool is infeasible for N = 65..95 and N = 60..63); new "to our knowledge".

## Unverified
- The CP-SAT negative sweeps were not rerun.
- `cpsat_rule.py 64 8 60` was not rerun.
- The Lean injectivity lemma was not proved.
- The literature search covers alphaXiv only; no other search was run.
