# LR-IND: independent audit

- Auditor: an independent Claude agent (producer ≠ verifier), 2026-10-28.
- Cores used: `taskset -c 4,5` only.
- Scratch, with all auditor code and raw outputs: `/tmp/lrindaudit/` (not committed).
- Subject:
  - `results/proposal5/2026-10-27/LR-IND/` (RESULT.md, result.json, code/, data/, logs/);
  - `formal_cert/Programmes/LonelyRunnerInd/`.

## Verdict: ACCEPT_WITH_CORRECTIONS

The headline claim stands: J(10, p) = ∅ for all 61 primes of P_10 (127..467), with exact integer arithmetic (Tier C). What the auditor checked with its own code, and what rests on the producer's code, are not the same, so they are listed separately.

**Recomputed with the auditor's own code (different algorithms):**
- Phase 1 and the lifts at p = 127, 137 and 263. At each, the full ×2 ×2 ×2 ÷8 pipeline leaves only the identity class.
- The identity fibre at **all 61 primes**, through three pieces:
  - an exhaustive check of S–T Prop. 4.1 for k = 10;
  - an exact check of the Lemma 4.3 inclusion;
  - the hand re-derived proof of Prop. 4.4.
- A direct level-11 fibre enumeration at p = 127, 137, 263 and 467.

**Resting on the producer's code at the other 58 primes (phase 1 and lifts):**
- The producer's binaries, which the auditor rebuilt bit-identically and spot-reproduced at 127, 137, 263 and 467.
- Exact agreement of S1 class counts with the published S–T log at all 61 primes.

The corrections in §6 concern attribution, wording, one soundness paragraph, and a missing boundary-sensitive control. None changes the headline.

## 1. Literature statement (read by the auditor; Tier L)

Source: arXiv 2604.23906 v2 (Sungkawichai–Trakulthongchai, "S–T").

**Definitions (S–T Def. 2.1 and 2.3).**
- Z_{p,l} = {x ∈ Z_{lp} : x ≢ 0 mod p}.
- v ∈ Z_{p,l}^k is (k, p, l)-proper iff either:
  - some i has gcd(l, v_j : j ≠ i) > 1; or
  - some t ∈ (1/(lp))Z has ‖t v_i‖ ≥ 1/(k+1) for all i.
- I(k, p, l) is the set of improper tuples.
- J(k, p) is the set of v ∈ Z_{p,1}^k with v ∈ π_{lp→p} I(k, p, l) for every l (not eventually proper).
- The producer implements exactly this, in the form (k+1)·min(r, N−r) ≥ N with N = lp. That is exact and equivalent.

**Results used.**
- Lemma 2.4: J = ∅ iff I(k, p, l) = ∅ for some l.
- Corollary 2.5: if LRC(k−1) holds and J(k, p) = ∅, then p divides u_1⋯u_k for every counterexample u.
- Lemma 2.6 (Malikiosis–Santos–Schymura, in the form of Rosenfeld 2509.14111 Cor. 3):
  - B_k = (C(k+1, 2)^{k−1} / k)^k, with ÷k and not ÷k!;
  - confirmed from three texts: Rosenfeld's Cor. 3; Trakulthongchai 2511.22427's C_k; Allikvere 2609.02604's ((n+1 choose 2)^{n−1}/n)^n;
  - check values: Rosenfeld's printed k = 7 bound "< 7.4·10^54" vs computed 7.33·10^54; ln B_10 = 337.634 (S–T Table 1 states "< 338"; with ÷k! it would be 209.6).
- Proposition 2.7: if LRC(k−1) holds, J(k, p) = ∅ for all p ∈ P, and ∏P ≥ B_k, then LRC(k) holds.
- Proposition 1.4 / 4.4 (k+1 and p > k(k+1) both prime): every tuple in π^{-1}_{(k+1)p→p}(1, …, k) is (k, p, k+1)-proper.
- §5.2 plan for k = 10: ×2 ×2 ×2 ÷8; S_5 may contain only the class of (1, …, 10).

**What the cited theory gives (Tier L, not a new theorem).**
- Premises:
  - LRC(9), the conjecture for 10 runners (Trakulthongchai, EJC 33(2) P2.46);
  - Lemma 2.6;
  - S–T Corollary 2.5 and Proposition 2.7.
- Inputs:
  - J(10, p) = ∅ for all p ∈ P_10 (Tier C, recomputed here);
  - ∏P_10 ≥ B_10 (Tier A, Lean).
- Conclusion: LRC(10), i.e. the Lonely Runner Conjecture for **11 runners** (k = 10 moving speeds plus the stationary runner).
- This is S–T's Theorem 1.3 for k = 10. LR-IND is an independent recomputation of its computational input, not a new proof.
- The producer says "not a new proof", which is correct. Corrections 1 and 5 fix the attribution and the wording around it.

## 2. Auditor's own implementation (different algorithms), and results

All runs use exact integer arithmetic.

### `aud_sieve.c`, phase 1

- It enumerates supports U ∋ 1 in **increasing order**, unlike the producer's hitting-set branching.
- Pruning:
  - every surviving time must have a killer larger than the last chosen element;
  - a top-r capacity bound over the later candidates.
- Optional mode `pair=1` adds only the necessary pairwise condition min(fold(y/x), fold(x/y)) ≥ u_2. This is the same lemma as the producer's, written in independent code. The unpruned runs at p = 127 and 137 validate the lemma empirically.
- There is no set-canonical filter. All multiplicity patterns are expanded at every improper support.
- Canonicalisation is by brute force over **all** units of Z_p. The producer uses only x^{-1} for x ∈ T.

### `aud_sieve.c`, lifting

- An odometer runs over all c^k preimages, and each time is scanned directly against a byte table. The producer uses bitset ANDs.
- Class hashes use the producer's FNV convention on the global lex-min canonical forms, so the two are directly comparable.

### Results

| case | auditor result | producer `data/` |
|---|---|---|
| k=10 p=127, unpruned | S1 = 8,228 classes, 82,180 sorted improper tuples (the S–T convention), level classes 106/1/1/1, final = {(1..10)} | identical hashes at every level; 82,180 = producer `ST_convention` |
| k=10 p=137, unpruned (max S1) | S1 = 58,087, 579,548 tuples, 526/2/1/1, final = {(1..10)} | identical |
| k=10 p=263, pair mode | S1 = 17 (hash 039dd652…), 1/1/1/1, final = {(1..10)}; 927 s | identical |
| k=10 p=467, pair mode | not completed: stopped by the auditor (see the p = 467 section below) | – |
| k=7 p=31 / 37 (own plan 2,4) / 41, unpruned | 0 / 0 / 4 classes; the 4 survivors identical | identical |
| all 214 positive-control cases k=3..8 (producer's plans), **pair mode** (uses the pairwise lemma) | per-level class counts and hashes | **214/214 identical** |
| same 214 cases, **unpruned** (pair=0, no pairwise lemma), 300 s per case | **214/214 completed and identical**, 0 timeouts | identical |

The positive controls for k = 3..8 are therefore reproduced both with and without the pairwise lemma. At k = 10 the lemma-free runs are p = 127 and 137.

### `aud_fiber.c` (the decisive level-11 step)

**Formulation.** The formulation is my own and was re-derived by hand:
- times are CRT pairs t = s/11 + r/p;
- t·u_i ≡ s·w_i/11 + r·i/p (mod 1);
- allowed sets come from the exact integer test on x = s·w·p + r·i·11 mod 11p;
- (s, r) signatures are deduplicated;
- the normalisation puts the *last* nonzero coordinate at 1; the producer puts the first nonzero coordinate at 1.

**Results.**
- p = 127, 137, 263, 467: 2,593,742,461 leaves each, **0 improper**. Also 0 at p = 53 and 97.
- Nonzero agreement with the producer's `fiber_check`, rebuilt by the auditor:
  - p = 13: 54,976 improper orbits in both programs;
  - p = 23: 7,210 in both.
- **Boundary-sensitive negative control** (new):
  - strict ">" (‖x‖ > 1/11) at p = 127, L = 11 gives exactly 1 improper orbit, w = (10, 9, …, 1) = −(1..10), i.e. the tight identity tuple;
  - at k = 6, p = 43, L = 7 the analogous strict control also flags the identity orbit;
  - the correct rule finds 0 improper at both.

### `prop41.c`: S–T Prop. 4.1 for k = 10, checked exhaustively without the polynomial method

- All 15,937,424,600 vectors of N_10 (11^10 − 10^10 − 1) admit s, r ∈ Z_11^* with s·v + r·(1..10) ∈ {1..9}^10. **0 failures.**
- Negative control: with {1..8} in place of {1..9}, 186,429,550 failures.

### `lemma43.py`: exact check of the inclusion r_10((1/11)Z) ⊆ r_10((1/p)Z)

- It holds for all 61 p ∈ P_10.
- Among primes ≤ 113 it holds exactly for 101, 103, 107, 109 and 113, consistent with S–T footnote 4.
- With the proof of Prop. 4.4 (whose CRT decomposition the auditor re-derived), this gives the identity-fibre conclusion at **all 61 primes**, independently of `fiber_check.c`.

### Brute force of I(k, p, l) over all ordered tuples, no symmetry (`brute_I.py`)

| case | ordered tuples | improper |
|---|---|---|
| I(4, 13, 5) | 12,960,000 | **0** |
| I(4, 17, 5) | 40,960,000 | 0 |
| I(4, 11, 5) (control, must be nonempty) | 6,250,000 | 23,040 |
| I(4, 7, 5) (control, must be nonempty) | 810,000 | 13,824 |

### p = 467 with the auditor's own sieve: not feasible within budget

- The pair-mode run was stopped after 1,898 s with no output.
- Measured growth: the node count went from 20.2 M at p = 127 to 537 M at p = 263 (927 s).
- Extrapolating, p = 467 needs about 13× more nodes at a higher cost per node, which is roughly 6–10 h of core time.
- At p = 467 the claim is still supported by:
  - the producer binary, rebuilt bit-identically, which reproduces its own output exactly (S1 = 1 class, the identity);
  - the S–T log, which also gives S1 = 1;
  - the auditor's own fibre check (0 improper);
  - Prop. 4.1 together with Lemma 4.3.

## 2b. Reproduction of the producer's code, and soundness re-derivation

- `gcc -O3 -march=native` rebuilds of `lr_sieve.c` and `fiber_check.c` (into /tmp) are **bit-identical** to the frozen binaries (sha256 cecbbf92…, 989848e8…).
- Reruns of lr_sieve at p = 127, 137, 263 and 467, and of fiber_check at p = 467, reproduce `data/k10_main/p*.json` and `data/k10_fiber11/p467.json` exactly, timings excluded.

**Canonical-support pruning: sound.**
- Every class has a member whose support is lexicographically minimal among the normalisations fold(x^{-1}U).
- Scaling is a bijection on ±-classes, so fold never merges elements.
- Multiplicities travel with the support, so emitting all multiplicity patterns of a set-canonical support is complete.
- For distinct x, y ∈ U, fold(y/x) ≥ u_2 follows because the second element of fold(x^{-1}U) must be ≥ u_2.
- The hitting-set branching with sibling exclusion reaches every improper support exactly once, because the branch taken is the first killer that lies in U.
- The capacity bound is a valid relaxation.

**`fiber_check.c` CRT and scaling: sound.**
- w ↦ c·w (c ∈ Z_11^*) with the matching time is a bijection that preserves both properness tests. So enumerating w = 0 plus the vectors whose first nonzero coordinate is 1 (1 + (11^10 − 1)/10 = 2,593,742,461) is complete.
- The leaf count matches in both fibre programs.

**Negative control 1 (prereg "<" → "≤") is inert at k = 10, levels 1/2/4/8: confirmed.**
- Equality needs 11 | lp, and l ∈ {1, 2, 4, 8} with p ≠ 11.
- MUT = 2 (floor) coincides with the correct rule whenever 11 | N. So **neither planted mutation ever touched the decisive level-11 step**, and `fiber_check.c` has no mutation switch. The auditor's strict control in §2 fills this gap (correction 4).

## 3. k = 4, p = 13 flag: resolved, no mismatch

- Rosenfeld 2509.14111 v2 §7 is hedged. It reads: "For k = 3, 4, 5 it seems to be true for all prime p larger than 7, 17 and 23 respectively."
- His Table 1 uses {7, 11, 13}, {17..37} and {23..71}. So "larger than" includes the endpoint, and §7 makes **no claim that p = 13 fails** for k = 4 (13 is simply not mentioned).
- His Lemma 6 condition is I(k, p, k+1) = ∅. The auditor's no-symmetry brute force gives I(4, 13, 5) = ∅, with nonempty controls at p = 7 and 11.
- Hence J(4, 13) = ∅. The producer's sieve and its `direct_I.py` are right, and `controls_ok` should be true (correction 2).

## 4. Lean (Tier A, scalar inputs only)

- **Compile.** The auditor compiled a /tmp copy of `ScalarInputs.lean` with the `#print axioms` lines appended, using `lean_pinned.py compile` without `--olean` (Lean 4.34.1, Mathlib d13f23b7). rc 0.
- **Axioms.**
  - P10_length, P10_nodup, choose_11_2: none.
  - P10_gt_k2k, B10_le_prod_nat, B10_not_le_prod_without_467: [propext].
  - P10_prime, k_succ_prime, B10_le_prod: [propext, Classical.choice, Quot.sound].
  - All are within the whitelist.
- **leanchecker.** The auditor built its own olean in /tmp and replayed it with `leanchecker LRIAudit`: rc 0. Control: a nonexistent module gives rc 1.
- **Escape grep** (sorry, admit, native_decide, implemented_by, extern, axiom, unsafe, skipKernelTC, addDecl, ofReduceBool, opaque, set_option, macro, elab, debug): no hits in ScalarInputs.lean.
- **P_10.**
  - The Lean `P10` equals the Table 1 row for k = 10 of 2604.23906 v2 exactly (text compared programmatically), and equals all 61 primes in [127, 467].
  - ln ∏P_10 = 342.716 > ln B_10 = 337.634.
  - Without 467 the bound fails (exact rational check).
- **What Lean says, and only this.** P10 is a list of 61 distinct primes, all > 110. 11 is prime. C(11,2) = 55. 55^90 ≤ 10^10·∏P10, equivalently ((C(11,2))^9/10)^10 ≤ ∏P10 in ℚ. Dropping 467 breaks it.
- **Not in Lean:** J(10, p) = ∅, Lemma 2.6, Prop. 2.7, LRC(9), and the link between these numbers and the theorem.

## 5. Comparison with the S–T logs

Timing: the auditor opened the S–T repository after its own counts at p = 127 and 137 were complete. Its p = 263 run was still in progress at that point.

- Source: github.com/vzsky/13-lonely-runners, `results/result_11` (the k = 10 run; their file index is the runner count).
- Their "Step 1 (l=1): S size" equals the producer's `S1_classes` at **all 61 primes**: 0 disagreements. Their log reports "Subproof Mod p Done" for all 61.
- The auditor's own S1 counts (127: 8,228; 137: 58,087; 263: 17) agree with theirs.
- Their later sizes are not comparable. They remove the identity class first (Prop. 1.4) and then lift, while LR-IND keeps it and checks the fibre.
- Their `Allikvere.md` also lists a k = 10 oracle count at p = 127 (8,228).
- No disagreement was found, so nothing needs to go to the authors.

**Copying / blindness.**
- The producer's blindness statement cannot be verified by the auditor; only the producer can attest it.
- Qualitatively, the code is dissimilar:
  - producer: single-file C99, a bitset hitting-set search with a set-canonical filter, and a separate CRT fibre enumerator;
  - S–T: C++23 templates (`find_cover.h`, `lift_strategy.h`, `TightLargePrime` / `Squeeze` strategies), with a different k = 10 pipeline (the identity is removed before lifting).
- No sign of copying.

## 6. Corrections (numbered, exact)

1. **RESULT.md, intro paragraph "Allikvere (arXiv 2609.02604 v2) states that 'the full computation has not been independently reimplemented or formally verified'".** This is misattributed. In Allikvere §6 the sentence refers to *his own* k = 13 / 14 computation, not to S–T's k = 10.
   - Delete it as evidence.
   - Keep only: "To our knowledge (web + alphaXiv search 2026-10-28), this is the first reimplementation of the S–T k = 10 computation not derived from the S–T code."
   - Optionally note that Allikvere re-inspected the S–T k = 12 residual tuples, not k = 10.
2. **RESULT.md §2 positive-control table and result.json `controls_ok`.**
   - Rename the column "J(k,p) = ∅ exactly for" to "I(k, p, l_final) = ∅ at the tested level". A nonempty I at the final level does not imply J ≠ ∅, so "exactly" overstates, for example, the k = 8 row.
   - Replace the k = 4, p = 13 "flag" with: "Rosenfeld §7 is hedged and makes no claim about p = 13. Independent auditor brute force: I(4,13,5) = ∅ (12,960,000 ordered tuples). Agrees."
   - Set `controls_ok: true` and update `controls_ok_note`.
3. **RESULT.md §1, "Lifting only representatives is sound".**
   - The displayed identity π_p(π^{-1}S ∩ I(k,p,cl)) = π_p S ∩ π_p I(k,p,cl) is false for a general S. The same identity appears in the proof of S–T Prop. 3.1. It holds when S contains every level-l improper tuple over π_p S.
   - Example: k = 10, p = 127, v = (1..10).
     - Take S = {s}, where s is the level-2 lift with every coordinate even (s_i = i or i + 127).
     - s is gcd-proper, so every level-4 lift of s is also gcd-proper. Hence S′ = ∅ and the left side is ∅.
     - v is improper at level 4 (no witness because 11 ∤ 4p; five odd coordinates, so the gcd test fails). Hence v ∈ π_p I(10,127,4) and the right side is {v}.
     - v ∉ J here, so this refutes the proof step only, not the proposition's conclusion.
   - Replace it with the invariant actually used: starting from level-1 representatives r and lifting full fibres, the retained set at level l is exactly F_l(r) = {w ∈ I(k,p,l) : w ≡ r mod p}, by Trakulthongchai 2511.22427 Lemma 7 (improper at cl implies improper at l on reduction), as stated in Allikvere §2. Hence r ∈ J implies F_l(r) ≠ ∅ at every level.
   - The computation is unaffected, because every plan used chains full fibres from level 1.
   - (An exposition remark on S–T Prop. 3.1's proof. Re-check it before sending it to the authors; it is not an error in their theorem or computation.)
4. **RESULT.md §2 negative controls.** State that both planted mutations are inert at the level-11 fibre step (equality is possible only when 11 | N, and floor = ceil there), and that `fiber_check.c` was never mutated. Cite the auditor's boundary control:
   - strict ">" at p = 127, L = 11 flags exactly the identity orbit;
   - nonzero orbit counts agree across two independent fibre programs (p = 13: 54,976; p = 23: 7,210).
5. **Wording of the Tier L consequence.** State explicitly that the chain gives LRC(10), the conjecture for **11 runners**, via premises LRC(9) (10 runners), Lemma 2.6 and S–T Cor. 2.5 / Prop. 2.7, and that this recomputes S–T's Theorem 1.3 for k = 10 and is not a new result.
   - Any downstream text that calls this k = 10 result "10 runners" is wrong.
6. **RESULT.md §6 deviation 8.** Python helpers ran without `-I`. Harmless (own files), but rerun them with `-I` if regenerated.

## 7. What remains unverified

- **Literature premises (Tier L), not re-derived:**
  - LRC(9) (EJC 33(2) P2.46), including that the producer's k = 9 re-run matches his S_9 (not audited);
  - Malikiosis–Santos–Schymura Theorem A and Rosenfeld Cor. 3 (AM–GM step read);
  - the "pre-jump" Lemma 2.2;
  - Lemma 2.4 (read and accepted).
- **Phase 1 and lifts at the other 58 primes** were not rerun with the auditor's own algorithm. Own-algorithm coverage is 127, 137 and 263; 467 was infeasible within budget. They rest on:
  - the producer's code, rebuilt bit-identically and spot-reproduced;
  - its mode agreements;
  - exact S1 agreement with the S–T log at all 61 primes.
- **The identity fibre** at all 61 primes is covered independently, by Prop. 4.1 (exhaustive) + Lemma 4.3 inclusion (exact) + the proof of Prop. 4.4 (read and re-derived). The direct level-11 enumeration with the auditor's own code covers only 4 primes of P_10.
- **The unpruned producer pass** was not finished (33/61).
- **Nothing here is formalised beyond the scalar inputs.**
