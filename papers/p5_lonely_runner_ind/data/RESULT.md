# LR-IND (Proposal 5, lane W1-b): an independent check of LRC(10) — producer report, unaudited

**Outcome: KEEP (class (d): an independent re-run, not a new theorem).**

Our independently written code confirms J(10, p) = ∅ for every one of the 61 primes p in Sungkawichai–Trakulthongchai's (S–T) set P_10 = {127, …, 467}. It does so in two ways:

1. Exactly their reduction: the lifts ×2, ×2, ×2, then projection, leave only the class of (1, …, 10). Their Proposition 1.4 then removes that class.
2. With the Proposition 1.4 step replaced by computation: an exhaustive check, at every p, that the whole level-11 fibre over (1, …, 10) is (10, p, 11)-proper. Two separate programs did this: `fiber_check` at all 61 primes, and the generic ×11 lift in `lr_sieve` at p = 127.

The scalar inputs are kernel-checked in Lean:
- P_10 has 61 distinct primes, each > 110;
- 11 is prime;
- B_10 ≤ ∏ P_10.

Premises taken from the literature, not re-derived:
- LRC(9), Trakulthongchai, EJC 33(2) P2.46 (our re-run over his S_9 is reported below as a check only);
- Lemma 2.6, the Malikiosis–Santos–Schymura bound in Rosenfeld's Corollary 3 form;
- the logical chain Lemma 2.2 / Corollary 2.5 / Proposition 2.7. We read these proofs; we did not formalise them.

This is **not a new proof** and claims no novelty for LRC(10). To our knowledge it is the first reimplementation of the k = 10 computation not derived from the S–T code. Allikvere (arXiv 2609.02604 v2) states that "the full computation has not been independently reimplemented or formally verified". A web search and an alphaXiv `discover_papers` query (recency-ranked, 2026-10-28) found no later reimplementation. The newest related items, for example arXiv 2610.23790 (gap bound) and 2609.06259, are not reimplementations.

**Blindness.** Our code was written only from the definitions in arXiv 2604.23906 v2 (Def. 2.1, 2.3, Prop. 3.1, §5.1–5.2). We did not open the S–T repository (github.com/vzsky/13-lonely-runners) or Trakulthongchai's (t-tanupat/nine-and-ten-lonely-runners). `result.json` records the sha256 of every file before any such reading. The count comparison against their logs is left to the independent auditor (§7).

## 1. What was computed (definitions as implemented)

- **Properness.** Let N = l·p, and let u ∈ (Z_N)^k have no coordinate ≡ 0 (mod p). Then u is (k, p, l)-proper iff:
  - (gcd) for some prime q | l, at most one u_j is not divisible by q; or
  - (time) some a ∈ [1, N/2] has (k+1)·min(r, N−r) ≥ N for every r = a·u_i mod N.
  All arithmetic is exact integer arithmetic. No floating point is used anywhere.
- **Phase 1.** One representative per equivalence class of I(k, p, 1), under permutation, sign and multiplication by Z_p^*. The search is a hitting-set branch, the same idea Rosenfeld describes (2509.14111 §6):
  - pick a surviving time with the fewest available killers;
  - branch on which speed kills it, excluding siblings already tried;
  - prune with a capacity bound: the r largest remaining kill counts must cover the surviving times.
  Supports smaller than k, which give tuples with repeats, are expanded into all multiplicities at the leaf where they become improper.
- **Our own additional pruning, not from the paper.** We restrict the search to set-canonical supports. U = {1 = u_1 < u_2 < …} ⊆ [1, (p−1)/2] is set-canonical if it is lexicographically ≤ fold(x⁻¹U) for every x ∈ U, where fold(v) = min(v, p−v). Soundness:
  - Every class has a set-canonical member. The normalisations fold(x⁻¹U) are again subsets of [1, (p−1)/2] containing 1 of the same size, because fold does not merge distinct elements of [1, (p−1)/2] that are ≢ ±each other. Take the lexicographically least.
  - For a set-canonical U and distinct x, y ∈ U, fold(y/x) ≥ u_2. The set fold(x⁻¹U) contains 1, and its second-smallest element is min over y ≠ x of fold(y/x). Lexicographic minimality of U forces this to be ≥ u_2.
  - We enumerate u_2 explicitly and keep only speeds y with min(fold(y/x), fold(x/y)) ≥ u_2 against every chosen x.
  - Tuples with a small support are emitted with all multiplicities, without a multiset filter.
- **Lifting by c** (Prop. 3.1). All c^k preimages of every tuple are enumerated, and the (k, p, cl)-improper ones are kept. **Projection** reduces mod p and canonicalises. The plan for k = 10 is `2,2,2,/`, as in S–T §5.2.
- **Lifting only representatives is sound.** J(k, p) is closed under equivalence (Prop. 5.1, contrapositive), so every v ∈ J has its canonical representative r in J, and r is in our S_1. Prop. 3.1 applies element by element: if r ∈ J and r ∈ π_p(S), then r ∈ π_p(S′), because π_p S′ = π_p S ∩ π_p I(k, p, cl) and J ⊆ π_p I(k, p, cl). Hence J ⊆ {classes of π_p(S_n)} at every step.
- **Representative invariant.** Each level reports the number of distinct classes of π_p(S) and a hash of them. This does not depend on which representatives are used. All cross-checks compare at this level.

## 2. Controls (run before the headline)

- Everything under `data/`, plus `logs/mode_agreement.jsonl`, `logs/brute_py.json` and `logs/direct_vs_sieve.json`, was produced by the frozen binaries in `logs/freeze_sha256.txt`. We re-checked after the runs that their hashes are unchanged.
- **Pre-freeze files** (built from earlier or identical sources before the freeze; kept for the record, not relied on):
  - `logs/control_k8_lift33.jsonl` (first version; superseded by `data/controls_pos/k8_*`);
  - `logs/k10_p127_probe.json`, `logs/probe_k10_p163/199/263.json` (throughput probes);
  - `logs/probe_k10_p127_x11.json`. This is the generic ×11 cross-check at p = 127. Its binary was built from the same source as the frozen one, but before the freeze.

**Counts.** Neither Rosenfeld nor Trakulthongchai prints per-prime retained-tuple counts. So the positive controls compare per-prime verdict patterns only.

### Positive controls: printed per-prime verdict patterns

| k | l | primes tested | J(k,p) = ∅ exactly for | printed source | match |
|---|---|---|---|---|---|
| 8 | 9 (`3,3`) | 11..241 | 47..241 (all 39 primes) | Trakulthongchai 2511.22427 §6: I(8,9,p) ≠ ∅ for all 11 ≤ p ≤ 43, = ∅ on S_8 = {47..241} | **exact** |
| 7 | 8 (`2,2,2`) | 11..257 | every prime ≥ 31 except 41 | Rosenfeld 2509.14111 §7: "any prime p at least 31 other than 41"; Thm 1 uses S = {31..163} | **exact** (41 leaves 4 classes) |
| 6 | 7 (`7`) | 11..197 | 13, 19 and every prime ≥ 31 | Rosenfeld §7: works for 13, 19 and p ≥ 31; fails for 17, 23, 29 | **exact** |
| 5 | 6 (`2,3`) | 7..103 | every prime ≥ 23 | Rosenfeld §7 / Table 1 (from 23 on) | exact |
| 4 | 5 (`5`) | 7..103 | 13 and every prime ≥ 17 | Rosenfeld §7: "larger than 17"; Table 1 uses {17..37} | Table 1 matches. p = 13 also works for us. The naive brute force (`direct_I.py`, all multisets of Z_65) confirms I(4,13,5) = ∅, with 0 improper out of 40,920 multisets. We read his remark as a loose description and not as a claim about 13. **Flagged for the auditor.** |
| 3 | 4 (`4`) | 5..103 | every prime ≥ 7 | Rosenfeld Table 1 {7, 11, 13}; §7 | exact |

- The exact product test ∏{p : J(k,p) = ∅, p > k+1} ≥ B_k = (C(k+1,2)^(k−1)/k)^k holds over the tested ranges for k = 3..8.
- In particular, LRC(7) and LRC(8) are reproduced in the S–T Prop. 2.7 form, without Rosenfeld's lcm bonus, assuming LRC(6) and LRC(7) respectively.

### Cross-implementation checks

- `mode_agreement.py` (rerun with the frozen binary, `logs/mode_agreement.jsonl`): three phase-1 algorithms on all 56 (k, p) cases from k = 5 to k = 10, including k = 10 at p = 127 and 131 in all three modes. They are (a) the plain hitting-set search, (b) (a) plus the capacity bound, and (c) (b) plus the canonical-support pruning. They agree on class counts and hashes at every level. 0 disagreements.
- `brute_py.py`: a naive Python implementation scanning every sorted tuple, with no search and no pruning. It agrees with `lr_sieve` at every level, by count and hash, on 24 cases for k = 4..7. 0 disagreements.
- `direct_vs_sieve.py`: a direct scan of I(k, p, k+1) over all multisets, with no sieve. Its verdict agrees on emptiness for 14 cases with k = 3..5. 0 disagreements.
- k = 10, second pass without the canonical pruning (mode (1,0)): class hashes agree with the main pass at every level for the 33 primes 127..307. This pass was time-boxed and stopped; the remaining 28 primes were not run.

### Negative control 1 (prereg): planted wrong witness rule

| case | correct | MUT=1 (bad iff ‖x‖ ≤ 1/(k+1), the prereg's "< → ≤") | MUT=2 (floor instead of ceil threshold) |
|---|---|---|---|
| k=7, p=31 | final 0 classes | final **4** | S1 **0** (vs 19 classes) |
| k=8, p=47 | final 0 | final **1** | S1 120 tuples (vs 1279) |
| k=8, p=53 | final 0 | final **1** | S1 0 (vs 191) |
| k=10, p=127 | S1 8228 classes, final = identity class | **unchanged** | S1 311; final **0 classes** (identity class wrongly eliminated) |
| k=10, p=131 | S1 2940, final = identity class | **unchanged** | S1 86; final 0 |

- At k = 10 the literal "< → ≤" mutation cannot change anything. Equality ‖x‖ = 1/11 needs 11 | l·p, which never happens at the levels l ∈ {1, 2, 4, 8}. That is why the run shows no change.
- The mutation does bite where equality is possible: k = 7 at l = 8, and k = 8 at l = 9. The counts change there.
- MUT=2 shows the failure mode that matters most: a rounding bug gives a false "pass" at k = 10. Negative control 2 below catches it.

### Negative control 2 (prereg): the survivor without the Prop. 1.4 step

- At all 61 primes, the main k = 10 run reports `identity_survives: true`: the class of (1, …, 10) survives ×2 ×2 ×2 ÷8, as Remark 3.2 requires.
- `fiber_check` at L ∈ {5, 7}, where 11 ∤ L·p, finds exactly one improper class, w = (1..10) mod L, i.e. u = (1, …, 10), at both p = 127 and p = 467.
- At L = 5, k = 4, p = 7, where p < k(k+1), it finds improper tuples. The hypothesis p > k(k+1) matters.

## 3. Headline (k = 10, all 61 primes of P_10)

- For every p ∈ P_10, `lr_sieve 10 p 2,2,2,/` ends with exactly one class, the canonical (1, 2, …, 10) (`only_identity: true`).
- |S_1| (classes of I(10, p, 1)) ranges from 1 to 58,087; the maximum is at p = 137. The S_2/S_3/S_4 sizes are tiny, typically 1–4 tuples (581/4/4 at p = 137). Per-prime numbers are in `logs/summary.json`, and the raw outputs in `data/k10_main/`.
- For every p ∈ P_10, `fiber_check 10 p 11` checks all 2,593,742,461 vectors w ∈ (Z_11)^10 up to Z_11^* scaling. Every corresponding u (u ≡ (1..10) mod p, u ≡ w mod 11) is (10, p, 11)-proper: 0 improper.
  - This is 158,218,290,121 fibre vectors in total.
  - The CRT reduction and the scaling symmetry are argued in the header of `code/fiber_check.c`.
- Independent cross-check at p = 127: the generic ×11 lift in `lr_sieve` enumerated all 25,937,424,601 lifts and left 0 (`logs/probe_k10_p127_x11.json`).
- So J(10, p) = ∅ at every p ∈ P_10 **without using Prop. 1.4**. The Lemma 4.3 inclusion r_k((1/11)Z) ⊆ r_k((1/p)Z) also holds exactly for every prime 101..467 (`logs/lemma43_check.json`), consistent with S–T footnote 4.
- **Tier C** for these per-prime emptiness statements: exhaustive exact-integer enumeration, not a Lean proof.

**Optional premise re-run.** LRC(9): `lr_sieve 9 p 2,5`, i.e. I(9, p, 10), is empty for all 47 primes of Trakulthongchai's S_9 (137..401). This took 214 core-seconds. It is a check of his computation, not used as a derivation, and LRC(9) remains a literature premise.

## 4. Lean (Tier A, scalar inputs only)

- Module: `formal_cert/Programmes/LonelyRunnerInd/ScalarInputs.lean`, compiled with `scripts/certified_numerics/lean_pinned.py` (Lean 4.34.1, Mathlib d13f23b7), rc 0.
- Theorems:
  - `P10_length` (= 61), `P10_nodup`, `P10_gt_k2k` (every p > 110), `P10_prime` (norm_num), `k_succ_prime`, `choose_11_2`;
  - `B10_le_prod_nat`: 55^90 ≤ 10^10·∏P10, by kernel `decide`;
  - `B10_le_prod`: ((C(11,2))^9/10)^10 ≤ ∏P10 in ℚ;
  - `B10_not_le_prod_without_467`: without 467 the bound fails.
- The margin is ln∏P10 − ln B_10 = 342.716 − 337.634 = 5.08 nats.
- `#print axioms` (`logs/lean_axioms.json`): every theorem ⊆ {propext, Classical.choice, Quot.sound}. Several use none, or only propext.
- leanchecker replay of `Programmes.LonelyRunnerInd.ScalarInputs`: rc 0 (`logs/leanchecker.json`).
- grep for sorry, admit, native_decide, implemented_by, extern, axiom, unsafe, skipKernelTC, addDecl, ofReduceBool: no hits.
- Controls:
  - `ControlsMustFail.lean` (P10.length = 60; the bound without 467) is rejected by the kernel, rc 1;
  - `ControlsSorry.lean` compiles, and its audit shows `sorryAx`.
- The B_k formula was confirmed from the PDF text: B_k = (C(k+1,2)^(k−1)/k)^k, with ÷k, not ÷k!. This gives ln B_10 ≈ 337.6, consistent with S–T Table 1 "< 338" and Trakulthongchai's C_8 < 10^80.

## 5. Proposition 1.4 audit

- We read the proof of Prop. 4.1, Lemmas 4.2–4.3 and Prop. 4.4 (polynomial method over Z_11) line by line and found no gap. The key points are:
  - P(0) = 0 = Q(0), using k even;
  - comparing leading coefficients gives |G| ≡ −1 (mod k+1);
  - the u′ = 0 case is handled by the gcd condition.
- Because §3 verifies the conclusion of Prop. 4.4 directly at all 61 primes, the headline does not depend on this audit.

## 6. Compute, deviations

- **Compute.**
  - Main pass: 3,963 core-s.
  - Fibre ×11 pass: 5,068 core-s.
  - Second (unpruned) pass: 1,326 core-s, for 33 primes.
  - k = 9 re-run: 214 core-s.
  - Controls: about 0.3 core-h.
  - Total about 3.3 core-h on cores 2 and 3 (`taskset`), shared with other lanes; the load average was about 9–14 on 8 cores.
  - The kill criterion (projected > 40 core-h at p = 127) did not fire. The first, unpruned version projected about 230 core-h at p = 467 alone. The two pruning steps cut this to about 1 core-h for the whole pass. Measured times: 4.7 s at p = 127, and 215 s at p = 467 in the final version.
- **Deviations.**
  1. The prereg assigns the implementation to Sonnet; this producer is Opus.
  2. The canonical-support pruning and the capacity bound are our own; their soundness is argued in §1 and checked by mode agreement.
  3. The prereg's negative control #1 ("< → ≤") is provably inert at k = 10. It was run anyway, plus a rounding mutation, and at k = 7 and 8 where it bites.
  4. The unpruned second pass was stopped after 33 of 61 primes, to keep the time box.
  5. Prop. 1.4 was both audited and replaced by a direct computation, which goes beyond the prereg.
  6. The k = 4, p = 13 note under the positive controls.
  7. The repo gates `antigravity_guard.py` and `test_rigor_guard.py` exit 1 on pre-existing files elsewhere in the repo; neither flags an LR-IND file (`logs/guard_*.txt`). `pytest tests/` was not run.
  8. Python helper scripts ran under system `python3` without `-I`, reading only files we wrote.
  9. **Kill-criterion handling.** The prereg asks for a throughput measurement at p = 127 and a projection from it.
     - p = 127 alone ran in 4.7 s, which does not fix the growth rate. We therefore projected from a fit over four primes (127, 131, 163, 199).
     - The first implementation (plain hitting-set search) scaled about as p^10 and would have exceeded 40 core-h, roughly 230 core-h at p = 467 alone.
     - We changed the algorithm (capacity bound, canonical-support pruning) **before** the full run, and checked it against the original by mode agreement. The full run then took about 1.1 core-h.

## 7. What the independent auditor must redo

1. Rebuild `code/lr_sieve.c` and `code/fiber_check.c` (`gcc -O3 -march=native`). Re-run a sample of primes, at least 127, 137, 263 and 467, in both programs. Compare against `data/`.
2. Re-derive the soundness of the canonical-support pruning (§1) and of the CRT and scaling reduction in `fiber_check.c`. Re-run `code/mode_agreement.py`, `code/brute_py.py` and `code/direct_vs_sieve.py`.
3. **Only then** open the S–T repository logs and compare per-prime counts.
   - Our counts in the paper's representative convention (all sorted tuples 1 = v_1 ≤ … ≤ v_k ≤ (p−1)/2, before any canonical filter) are `ST_convention_improper_tuples_l1` in `logs/summary.json`, for 33 primes; for example 82,180 at p = 127 and 579,548 at p = 137.
   - Class counts for all 61 primes are `S1_classes`.
   - Their S_2..S_5 sizes may use other representatives. Compare classes where possible.
   - Report any disagreement to the authors first, after a second check (prereg kill rule).
4. Finish the unpruned pass for p = 311..467: `driver.py B` resumes it.
5. Recompile the Lean module, re-run `#print axioms` and leanchecker, and confirm that `P10` matches Table 1 of 2604.23906 v2. `logs/summary.json` also checks that it equals all primes in [127, 467].
6. Check the k = 4, p = 13 reading of Rosenfeld §7.
