# DICE-6 independent audit (producer != verifier)

Date 2026-11-01. Auditor: independent Claude agent. Subject: `results/proposal6/2026-11-01/DICE-6/` at commit 7c2b106 (RESULT.md, result.json, PREREG_ITEM.md). No producer code was run or reused. Auditor code and logs are in `/tmp/diceaudit/` (scratch, not committed): `dg.c` (C, histogram/cumulative-count encoding, iterative Tarjan, CSR graph), `cyc.py` (own DFS simple-cycle enumeration, exact `Fraction` checks, parser for the paper's printed cycles), logs `n9.log`, `n10.log`, `cyc.log`. All runs pinned with `taskset -c 6,7`.

**Verdict: ACCEPT_WITH_CORRECTIONS.** Every number in RESULT.md was reproduced exactly by an independent implementation. The corrections are about wording: one false "not stated" remark, the reach of the n>=7 conclusion, provenance notes, and one control label.

## 1. Definitions (read from the paper text myself)
- Die (Def. 1): a "non-standard n-sided die" takes face values in [n], and values may repeat. Each face has probability 1/n. Dice are represented as non-decreasing n-tuples, so dice with the same multiset are the same die and vertex. Number of dice = C(2n-1,n): 10, 35, 126, 462, 1716, 6435, 24310 (and 92378 for n=10). My enumeration gives the same counts.
- "Beats": the face value of D_x is strictly greater; ties do not count. P(D_x beats D_y) = #{(i,j): x_i > y_j}/n^2.
- Minimal winning probability (eq. 1): 1/2 + 1/n^2 for even n and 1/2 + 1/(2n^2) for odd n, i.e. W = floor(n^2/2)+1. The paper shows it is attained with explicit pairs; that it is minimal is immediate, since W is the smallest integer above n^2/2.
- Def. 2: a non-transitive cycle of length k >= 3 is a sequence of distinct dice with P(D_i beats D_{i+1}) > 1/2. "Uniform" means all k probabilities are equal; "minimal" means each equals the minimum in eq. 1. The edges of G_n are exactly the pairs with W(x,y) = floor(n^2/2)+1 (eqs. 3, 4), so a uniform minimal cycle is a directed cycle in G_n.
- "Maximum length n" is **not formally defined**. The proof of Theorem 1 fixes its meaning: the paper exhibits 6-cycles and then rules out a 7-cycle in the 7-vertex SCCs. So the meaning is "G_n has an n-cycle and no longer cycle". The Section 3 evidence (searching for cycles of length >= n+1) uses the same meaning. The producer's reading is correct. RESULT.md should still state the consequence of the alternative reading (see correction 2).

## 2. Independent reproduction (C implementation, exact integers)
W(x,y) = sum_v c_x[v] * C_y[v-1], with c = face histogram and C = cumulative count. 200,000 random pairs per n were cross-checked against the brute-force double sum: 0 mismatches for every n.

| n | dice | edges | self-loops | SCCs | nontrivial SCC (vertices, edges) | f involution and edge-reversal violations |
|---|---|---|---|---|---|---|
| 3 | 10 | 3 | 0 | 10 | none | 0 |
| 4 | 35 | 67 | 0 | 35 | none | 0 |
| 5 | 126 | 620 | 0 | 126 | none | 0 |
| 6 | 462 | 5491 | 0 | 450 | (7,10), (7,10) | 0 |
| 7 | 1716 | 89153 | 0 | 636 | (1081, 53389) | 0 |
| 8 | 6435 | 956307 | 0 | 2115 | (4321, 674108) | 0 |
| 9 | 24310 | 12528131 | 0 | 3860 | (20451, 10933011) | 0 |
| 10 | 92378 | 157244770 | 0 | 10588 | (81791, 147620052) | 0 |

All rows for n=3..9 equal the producer's numbers and the paper's numbers (main text plus Appendices B-I). The n=10 row, which the producer did not compute, equals the paper (Sec. 3 and Appendix J: 92378 dice, 157244770 edges, 10588 SCCs, one nontrivial SCC with 81791 vertices and 147620052 edges). The generalised map f_n(x) = (n+1-x_n, ..., n+1-x_1) is an involution and sends every edge a->b to f(b)->f(a), for every n. Because f is a bijection on a finite edge set, the converse holds too. So Corollary 1 holds for n=6 and generalises to all n checked.

## 3. n=6 cycles (own DFS, all simple cycles, rooted at their minimum vertex)
- SCC 1 has 1-based lexicographic labels {88, 89, 151, 207, 217, 277, 291} and SCC 2 has {118, 119, 160, 235, 286, 385, 391}. Both sets equal the vertex numbers in the paper's Appendix E.
- Each SCC contains 3 three-cycles and 1 six-cycle, with no cycle of length 4, 5 or 7. The totals over G_6 are six 3-cycles and two 6-cycles. This matches Appendix E, which lists 4 cycles per SCC.
- Both 6-cycles equal the paper's cycles. Each has six edges of exactly 19/36 (Fraction check). f applied to cycle A, then reversed, is a rotation of cycle B.
- n=3,4,5: all SCCs are trivial, so these graphs have no cycle. Hence n=6 is the smallest n >= 3 with an n-cycle, and at n=6 the longest cycle has length 6. Theorem 1 is reproduced.

## 4. n >= 7 cycles
- I parsed the paper's printed cycles from the text in print order and checked them with exact Fractions. n=7: 14 distinct dice, valid. n=8: 29, valid. n=9: 10, valid. **n=10: 110 distinct dice, valid, every edge 51/100.** The producer did not check the n=10 cycle.
- My own random-walk search in the big SCC of G_7 found exact-checked cycles of every length from 3 to 28, including 7, 8 and 14. So G_7 has a 7-cycle and also longer cycles.
- Consequence: under the paper's reading, one exact-checked cycle longer than n is enough to show that n fails the property. The property therefore fails at n=7, 8, 9 and also at n=10, and the n=10 case does not need the 157M-edge graph. Conjecture 1 is open only for n >= 11. Under the alternative reading ("an n-cycle exists"), Conjecture 1 is false at n=7.

## 5. Controls (recomputed by the auditor)
- Efron dice: 2/3 on all four edges. Moon-Moser triple (2,4,9), (1,6,8), (3,5,7): 5/9 on each edge.
- Single-face +-1 perturbations of paper cycle 1 (kept in [6], counted per die, face and sign): 62 perturbations, all 62 break the cycle. This matches the producer.
- Near-miss negative control: for x = (1,1,2,5,5,5), the predicate rejects y = (1,1,1,1,1,5) with W=20 and y = (1,1,1,2,2,5) with W=18. The producer's preregistered "W=20" control was actually run on a W=36 pair (see correction 4).
- I did not recompute the maximin context controls (3/5, 7/12, 29/49). They are orthogonal to the claim.

## 6. Hashes and provenance
- 18 of the 19 files listed in result.json are present, and all 18 match their sha256. `./data/paper_fulltext_alphaxiv.txt` is MISSING from the repo, as intended. The external copy at `/home/callensxavier_gmail_com/dice6_thirdparty/paper_fulltext_alphaxiv.txt` has sha256 b30efe502aed842285b9d7d6034f75b29b497a4f47d11e38bdebb55d52cd2c15, which matches the listed hash.
- PREREG_ITEM.md matches its .sha256 (b3425a39...). However, it was committed in the **same commit (7c2b106)** as the results. Git therefore cannot show that it was "written before any computation"; that rests on the producer's word.
- PREREG_ITEM.md says the paper text is "copy in data/". That is stale now that the text has moved out of the repo.

## 7. Literature (alphaXiv discover plus web search, 2026-11-01)
No earlier statement of the n=6 theorem or of the G_n statistics was found. Related work:
- Conrey, Gabbard, Grant, Liu, Morrison, arXiv 1311.6511: "proper" n-sided dice with faces in [n] and face sum n(n+1)/2 (counted by OEIS A076822). This is the closest setting, and Easlick does not cite it. Easlick drops the sum constraint, and Conrey et al. do not study the minimal-advantage graph.
- Angel and Davis, arXiv 1610.08595 (Easlick's ref. [2]): uniform non-transitive sets with advantage 1/2 + 1/(2k^2), using general labels rather than [k].
- Hur and Kim, arXiv 2006.12866: winning probabilities arbitrarily close to 1/2.
- Schaefer and Schweig, arXiv 1602.00969 and 1706.08986: balanced sets.
- Rooney, arXiv 2505.21950: winning probabilities of balanced n-tuples.
- None of these addresses n-cycles in G_n.
- The search was limited (two alphaXiv/web queries plus one web query), so prior work cannot be fully excluded. The recheck/no-novelty framing (Tier C exact, Tier X searches) is appropriate.

## 8. Corrections (old -> new)
1. RESULT.md table, n=8 row: "edges, SCC size match (SCC count not stated)" -> "match (paper Appendix H states 2115 SCCs)".
2. RESULT.md, n=7,8,9 bullet: "so at n=7 an n-cycle exists but longer cycles also exist, which is why the paper's "maximum length n" reading fails for n>=7. The conjecture (n=6 is the largest) rests on this reading and is supported only by the existence of a longer cycle for n=7..10 (n=10 not rechecked)." -> "so at n=7 an n-cycle exists but longer cycles also exist, and the property "longest cycle has length exactly n" fails at n=7. Under the paper's reading, one exact-checked cycle longer than n settles each n. The printed cycles settle n=7,8,9, and also n=10 (the auditor checked the printed 110-cycle exactly). Conjecture 1 is therefore open only for n>=11. Under the alternative reading "an n-cycle exists", Conjecture 1 is false at n=7."
3. RESULT.md "Not done: n=10 graph (157M edges)" -> "n=10 graph counts not rechecked by the producer; the auditor reproduced them independently in C (92378 dice, 157244770 edges, 10588 SCCs, one nontrivial SCC 81791/147620052), matching Appendix J."
4. RESULT.md Controls: "predicate rejects a W=36 pair" -> "predicate rejects a W=36 pair (the preregistered near-miss W=20 control was not run by the producer; the auditor confirmed rejection of W=20 and W=18 near-misses)". In extra_results.json, the key `ctrl_predicate_rejects_W20` refers to a W=36 example and is mislabelled.
5. PREREG_ITEM.md / RESULT.md provenance: add "Preregistration was committed together with the results (7c2b106); its precedence is not git-attested." Replace "copy in data/" with "copy kept outside the repo at ~/dice6_thirdparty/ (sha256 b30efe50...)". In result.json, mark the `./data/paper_fulltext_alphaxiv.txt` hash as external/not-in-repo.
6. RESULT.md: add a short literature note (section 7), naming Conrey et al. 1311.6511 as the closest prior setting that Easlick does not cite.

## 9. Not verified
- n >= 11.
- Any proof of Conjecture 1.
- The full vertex lists of the SCCs for n >= 7 in the paper's appendices (only sizes and counts were checked).
- The maximin context controls.
- Exhaustive prior-art search.
