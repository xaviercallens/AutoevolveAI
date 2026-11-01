# MS-CENSUS independent audit

Date: 2026-11-01. Auditor: independent Claude agent (producer != verifier). No producer code was run or imported.
Auditor scratch: /tmp/msaudit/ (Rust D2C filter `d2c/src/main.rs`, Python `lem.py`, `bf.py`, `ctl.py`, `dfh.py`, `cmp.sh`).

**Verdict: ACCEPT_WITH_CORRECTIONS.** Every number in RESULT.md / result.json was reproduced exactly by my own code.
The corrections are about prior art and wording: the D2C counts are a published OEIS sequence, the bound itself
was already reported proved for these orders, and the preregistration timing cannot be verified from git. No number changes.

## 1. Paper reading (Das-Fox, arXiv 2610.39032v1, full text read via alphaXiv)
- D2C: "every pair of vertices has distance at most 2, but which lose this property if we delete any edge". Matches the producer's reading.
- Lemma 1.2 (verbatim): "Let G be a diameter-2-critical graph on n >= 3 vertices, and let M be any maximal matching of G. Then
  |E(G) \ M| <= |E(G)-bar|." E(G)-bar = set of non-edges. "By a maximal matching, we mean a matching that we cannot add any
  additional edge to while keeping it a matching". So maximal means inclusion-maximal in G, and non-edges are pairs of distinct non-adjacent vertices.
- Lemma 1.3 (verbatim): "Let G be a diameter-2-critical graph on n >= 3 vertices, and suppose that for every maximal matching M of G,
  we have |E(G) \ M| = |E(G)-bar|. Then G is triangle-free."
- Both lemmas are stated for all D2C graphs with n >= 3, with no minimal-counterexample or other extra hypothesis. The producer's
  statements in PREREG_ITEM.md match. (The paper's header says "Date: September 28, 2026"; arXiv v1 is 28 Oct 2026. Not material.)

## 2. Independent D2C census (Rust, different method)
Filter: Rust, u32 bitsets. Edge uv counts as critical iff N(u) and N(v) are disjoint, or some x not adjacent to u has N(u) ∩ N(x) = {v}
(or the same with u and v swapped). This is a common-neighbour characterisation, not explicit deletion. Every graph with n <= 10
was also checked by a second, BFS-based explicit-deletion test: 0 disagreements on all 11,989,762 connected graphs with 3 <= n <= 10.
Fresh `nauty-geng -c` (nauty 2.7001). n = 10 and 11 were split res/mod 4.

| n | connected graphs | D2C (auditor) | producer | canonical-set symmetric difference (labelg) |
|---|---|---|---|---|
| 3..9 | 2, 6, 21, 112, 853, 11117, 261080 | 1, 2, 3, 5, 10, 30, 103 | same | 0 each |
| 10 | 11,716,571 | 519 | 519 | 0 |
| 11 | 1,006,700,565 (full run) | 3,746 | 3,746 | 0 |

The n = 11 per-part values (seen / D2C) are 240722772/797, 234372703/913, 263262466/903, 268342624/1133. They are identical to the
producer's logs/census_n11_p*.log. Total D2C = 4,419. The n = 11 run was not separately timed; from file mtimes it took about 7.5 min wall (18:29 to 18:36:35 UTC).
Filter controls: positives C4, C5, Petersen, K_{2,3}, K_{3,3}, K_{4,5}, K_{1,5}: 7/7 accepted. Negatives K3, K4, K5, K4-e, C6, C7, P4: 0/7 accepted.

## 3. Independent maximal-matching enumeration and lemma test (Python, own code)
Enumerator: branch on the lowest undecided vertex (either leave it unmatched or match it to an undecided neighbour), then keep the
matchings with no edge inside the unmatched set. Control: compared with brute force over all edge subsets on the 51 D2C graphs with n <= 8
plus the 14 control graphs: 0 mismatches. It was run on my own D2C lists, not the producer's.

| n | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|
| maximal matchings | 2 | 5 | 15 | 39 | 147 | 788 | 5142 | 50991 | 719088 |
| D2C with a triangle | 0 | 0 | 0 | 1 | 4 | 20 | 87 | 488 | 3685 |
| min slack of L1.2 over triangle-containing D2C | - | - | - | 1 | 3 | 4 | 5 | 8 | 10 |

Total 776,217 maximal matchings, the same as the producer at every n. Lemma 1.2 violations: 0. Equality for every M: exactly one graph per n,
the balanced K_{a,b}, which is triangle-free, so Lemma 1.3 holds. Max edges = floor(n^2/4), attained only by K_{a,b} (Theorem 1.1 consistent).
Perturbed strict "<" fails at every n. Extra finding: equality in Lemma 1.2 holds for even ONE maximal matching only at K_{a,b}. No graph
containing a triangle comes within 1 of the bound (slack >= 1 at n = 6, >= 10 at n = 11). This confirms and sharpens the producer's
caveat that the Lemma 1.3 test is nearly vacuous in this range.
Not rechecked by me: the intermediate Lemmas 2.4, 2.5, 2.13, 3.1, 3.2 (producer-only numbers).

## 4. Dailly-Foucaud-Hansberg (arXiv 1812.08420): abstract, introduction and concluding section read; full text (3,106 extracted lines) keyword-searched
DFH state: "We have performed a computer search on all graphs of order up to 11." I found **no per-order D2C counts** in the parts read or by keyword search,
so a count comparison was not possible. I tested their published structural facts on my D2C list instead (C5+ family generated independently and canonicalised; all 12
generated C5+ graphs are in the list and have floor((n-1)^2/4)+1 edges):
- non-bipartite D2C graphs at floor((n-1)^2/4)+1 edges and not in C5+: 13 (n = 7: 3, n = 8: 8, n = 9: 2; none at 10, 11). Of these, 3 have no dominating edge. DFH: 13, orders 7-9, 3 without. MATCH.
- non-bipartite D2C at the bound with a dominating edge: 10, all n <= 9. DFH section 4: "only ten ... (all of order at most 9)". MATCH.
- non-bipartite D2C above the bound: only one graph, n = 6 with 8 edges (H5). DFH: H5 (6 vertices, 8 edges). MATCH.
- max degree n-1 only for stars: 0 exceptions. MATCH.
DFH also report (line 59) that Fan (1987) proved the Murty-Simon conjecture for "order at most 24 and 26" (i.e. n <= 24 and n = 26). I did not read Fan.

## 5. Literature
- **OEIS A330333** "Number of diameter-2-critical graphs with n nodes": 1, 2, 3, 5, 10, 30, 103, 519, 3746 (offset 3). Author M. Zivkovic,
  Dec 2019; a(11) = 3746 added by S. A. Irvine, 2026-09-05. Exact match (verified against the raw OEIS text entry: %A Miodrag Zivkovic, Dec 17 2019; %E a(11) from Sean A. Irvine, Sep 05 2026). MacDougall-Eggleton (1997) list all D2C graphs up to n = 7.
- No independent verification, formalisation or critique of Das-Fox 2610.39032 was found (alphaXiv discover, web search on the title and
  on the bare ID, 2026-11-01). No other claimed proof of the full conjecture was found (Füredi 1992: large n only).

## 6. Corrections (exact old -> new)
1. RESULT.md: "I could not match the D2C counts 1,2,3,5,10,30,103,519,3746 against an
OEIS sequence (not searched; no claim)." -> "The D2C counts equal OEIS A330333 (Zivkovic 2019; a(11) = 3746 added by S. A. Irvine,
2026-09-05), so the counts themselves are published; this census recomputes them."
2. RESULT.md: "(Dailly-Foucaud-Hansberg, Discrete Math 2019,
arXiv 1812.08420, per a search snippet; paper not read in full)" -> "(Dailly-Foucaud-Hansberg, Discrete Math 2019, arXiv 1812.08420:
computer search of all graphs of order <= 11; they publish structural facts but no per-order counts; counts are in OEIS A330333; the D2C list
for n <= 7 is in MacDougall-Eggleton 1997)". Make the same change in PREREG_ITEM.md's prior-art paragraph only if a dated erratum note is added.
Do not silently edit the prereg.
3. RESULT.md, Theorem 1.1 line: add "The conjecture for n <= 24 and n = 26 was already reported proved by Fan (1987), per DFH. The Theorem 1.1
check here re-confirms an established range and is a sanity check, not new evidence."
4. RESULT.md / PREREG_ITEM.md: "written before any computation" -> "stated as written before any computation; PREREG_ITEM.md and RESULT.md
were committed together (c981c12), so the order is not verifiable from git".
5. RESULT.md Controls: "Compare with the enumeration in Dailly-Foucaud-Hansberg (2019), including their 13 extra non-bipartite extremal graphs
... (not tested here)" -> may now cite this audit: the 13 / 3 / 10 / H5 facts were reproduced by the auditor.
6. RESULT.md Resources: "Cores 2-5 only, <= 4 processes" -> "Cores 2-5 only; 4 geng|filter pipelines (8 processes, 2 per core)".
The auditor's n = 11 run used the same layout, and I disclose that here.
7. RESULT.md: "Das-Fox, arXiv 2610.39032, which says GPT-5.6 Sol found
the proof" and PREREG_ITEM.md: "the paper says GPT-5.6 Sol found the proof" -> "the paper's AI Statement says GPT-5.6 Sol found a proof
of the floor(n^2/4) bound (Section 2, Lemma 1.2) and an equality-case proof for even n only. The equality-case proof for all n (Section 3,
Lemmas 3.1-3.3 => Lemma 1.3) is the authors' own." Note that Lemma 1.3, whose test is nearly vacuous here, is the part attributed to the
authors, not to the AI. (Same rule for PREREG: dated erratum note, no silent edit.)
8. Optional addition to the Lemma 1.3 caveat: "no triangle-containing D2C graph attains equality for even one maximal matching (min slack 1 at n = 6,
10 at n = 11)".

## 7. Wording check
The headline wording is fine and should be kept: a recheck of the lemma STATEMENTS of a claimed proof on all D2C graphs with 3 <= n <= 11,
Tier C (exact integers), no novelty, does not verify the proof, nothing for n >= 12. With correction 1 the enumeration is a recomputation of
OEIS A330333. The only possibly new element is the per-graph Lemma 1.2 / 1.3 test, and it is weak evidence: it is a finite check of statements
whose consequence (Theorem 1.1) was already reported known for n <= 24 and n = 26 (Fan, per DFH).

## 8. Remains unverified
The Das-Fox proof itself (the logic of Sections 2-3). Intermediate Lemmas 2.4, 2.5, 2.13, 3.1, 3.2 (not recomputed by the auditor).
Anything for n >= 12. Fan 1987 (not read; cited via DFH). The producer's reconstructed Figure 1 graph (not checked).

## Reproduction / resources
nauty 2.7001, rustc 1.96.1, Python 3 (system). Cores 2-5. n <= 10 took seconds. The n = 11 run had 4 pipelines on cores 2-5 and took about 7.5 min wall (from file mtimes, not timed).
The lemma test was a single process pinned to core 2 and took 9 s. result.json: all 142 file hashes verified, 0 mismatches. PREREG sha256 matches the stored value.
