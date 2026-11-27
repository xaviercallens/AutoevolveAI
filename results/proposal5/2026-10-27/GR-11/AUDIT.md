# GR-11 independent audit (producer != verifier), 2026-11-01

Verdict: **ACCEPT_WITH_CORRECTIONS**. The numbers reproduce. The literature claim is wrong, and that error changes how the result should be framed.

Auditor code and outputs are in /tmp/gr11audit/ (scratch, not committed): `code/audit_scan.py` (sha256 cd69fc62...6b024), `code/exact_margin.py` (68333249...a40dc), `code/exact_c29.py` (5425168d...7bf4), and `out/*.json`. Heavy runs used `taskset -c 4` / `-c 5` only, about 4.9 core-hours (17.7k s logged). Hashes checked: PREREG_ITEM.md 5a02b566...c3d85 and addendum2 3fd041d3...b10b match their .sha256 files, and all 97 file hashes in result.json match the files on disk.

## 0. Headline: the conjectures are claimed PROVED in the literature (the census is a consistency check, not a new result)
- tr A = 0, so S+ = E(G)/2, where E is the graph energy. Conjectures 20 and 21 together say S+ >= max(n+, n-), which is the same as **E(G) >= 2 max(n+, n-)**.
- H. Kumar, S. Pragada, *Energy and independence number*, arXiv:2607.19817 (22 Jul 2026), Theorem 1.2: E(G) >= 2(n - alpha(G)). This was Fajtlowicz's Graffiti conjecture, Aouchiche-Hansen #543. The paper then uses the classical inertia bound alpha <= min(n - n+, n - n-) to derive E(G) >= 2 max{n+(G), n-(G)}. In the paper's words, this "resolves [Aouchiche-Hansen 2010, Conjectures #20, #21, Table 6] (cf. Liu-Ning 2023)". The step from Theorem 1.2 to the corollary is elementary. Theorem 1.2 itself is an **unrefereed preprint**, and its AI statement says AI tools were used for ideation. I did not check the proof.
- Even before that preprint, the WoW comment on p.19 cites Fajtlowicz 1987 [F2]: E >= rank = n+ + n-. That gives S+ >= min(n+, n-). So for every graph, whichever of 20 or 21 has the smaller count has been a theorem since 1987. Zhang (arXiv:2409.15504) calls "E >= 2 min(n+, n-)" open. That is evidently a slip for max, so do not cite it as evidence that the problem is open.
- The producer wrote "Nothing found for 20, 21". That is a literature miss.

## 1. Primary source (WoW July 2004 scan, sha256 d2c779d2...f7733 verified; pp. 19 and 23 rendered and read by eye)
- 20: "The number of positive eigenvalues of a graph is not more than their sum." The comment cites [F2], sum |eig| >= rank, and calls it "a partial solution to conjecture 21".
- 21: "The number of negative eigenvalues of a graph is not more than the sum of its positive eigenvalues."
- 29 (p.23): "The Randic index is not more than the number of negative distance eigenvalues. Disproved by Alon, Saks, Seymour, Shearer and Winkler. July 88."
- The page does not define "positive eigenvalue count" further. The standard reading, which the producer used, is strictly positive adjacency eigenvalues counted with multiplicity, with zero eigenvalues excluded from both counts and from S+. The pinned definitions match the page.
- The statements are for all graphs, while the scan covers connected graphs only. That restriction loses nothing: n+, n- and S+ are additive over components. Note, however, that disconnected unions of cliques also attain equality in 21.

## 2. Independent recomputation (different code and method)
Method: my own graph6 decoder; **exact inertia** from the integer characteristic polynomial (Faddeev-LeVerrier, guarded to stay below 2^52) plus Descartes' rule, which is exact because the polynomial is real-rooted; S+ as the sum of the top n+ eigenvalues (exact count) from **LAPACK dgeev** (`np.linalg.eigvals`), cross-checked against dsyevd; distance matrix by BFS-layer reachability rather than Floyd; certified enclosures (sympy real-root isolation, width 1e-25) for all argmin graphs.

| scope | graphs | viol20 / viol21 | min margin 20 (graph) | min non-K_n margin 21 (graph) | ctl29 | producer |
|---|---|---|---|---|---|---|
| n=4..9 full | 273,189 | 0 / 0 | 0.23607 (CU = P4) | n=9: 0.080604 (HQhTQji) | 0,0,0,1,1,23 | match |
| n=10 full | 11,716,571 | 0 / 0 | 0.653751 (I?`D@POd?) | 0.064495 (IQhTQiitO) | 18 | match |
| n=11 part 31/40 | 30,714,260 | 0 / 0 | 1.36045 | 0.46502 | 62 | match |
| n=11 part 39/40 | 26,236,872 | 0 / 0 | 1.33663 | **0.056060** (JQhTQiiTVT?) | 62 | match |
| n=11 part 12/40 | 24,726,818 | 0 / 0 | **0.828328** (J?`D@POd?{?) | 0.74603 | 67 | match |
| n=11 part 5/40 | 23,644,128 | 0 / 0 | 1.26439 | 0.43535 | 45 | match |
| n=11 part 7/40 | 17,489,263 | 0 / 0 | 1.95171 | 0.77546 | 9 | match |

- Violation column: these are exact verdicts. The raw strict `< 0` float tally gave viol21 = 1 at n=9, at n=10 and in part 31. Those were K_9, K_10 and K_11 at -8.9e-16, -1.8e-15 and -1.8e-15 (float noise), and each was decided exactly as equality by exact_margin.py.
- Coverage: all 11,989,760 graphs with n <= 10, plus 122,811,341 of the 1,006,700,565 graphs at n=11 (12.2%; parts 31 and 39 chosen from the producer's flags and minima, 12 for the conj-20 minimum, 5 and 7 drawn with seed 20261101). Every part count, margin and ctl29 count equals the producer's per-part log to within 1e-14.
- Producer code rerun, unmodified (`scan.py 11 39 40`): its JSON is identical to logs/scan_n11_39of40.json in every field except `sec`.
- Graph counts: 6, 21, 112, 853, 11117, 261080, 11716571, 1006700565 match OEIS A001349. The 40 n=11 part counts sum to exactly 1,006,700,565.
- Equality in 21: the only graphs with |S+ - n-| < 1e-6 are K_n, at every n <= 10 and in all sampled n=11 parts. The producer's flag files show the same for all 40 parts. Exactly: K_n has spectrum {n-1, (-1)^(n-1)}, so S+ = n-1 = n-. The integer charpoly confirms this for K_4, K_9, K_10 and K_11. In conjecture 20, only P4 reaches margin 0.236. All argmin margins above are certified enclosures, so they are exact verdicts, not floats.

## 3. Rounding soundness (whole census, not only the sample)
- Zero eigenvalues. For an integer symmetric matrix, the product of the nonzero eigenvalues is ± the lowest nonzero charpoly coefficient, an integer of absolute value >= 1. The other k <= 10 nonzero eigenvalues have sum of squares <= 2m <= 110, so by AM-GM their product is at most (110/k)^(k/2) <= 11^5. Hence every nonzero |lambda| >= 1/161051 ≈ 6.2e-6 for n <= 11. dsyevd's backward error is about 1e-14. Therefore the producer's 1e-9 zero threshold classifies every eigenvalue correctly, and n+ and n- are exact for all 1.0e9 graphs, given LAPACK backward stability. Direction of risk: counting a true zero as nonzero would only lower the margin, so it could only create false flags, never hide a violation.
- Corroboration: across the 134.8M graphs I checked, there were 0 mismatches between float-threshold inertia and exact Descartes inertia. The smallest nonzero |lambda| observed was 0.00383, and the largest dgeev-vs-dsyevd difference in S+ was 4.8e-14.
- Margins. By Weyl's inequality plus backward stability, the error in S+ is at most about 1e-12, far below the 1e-6 flag band. For n <= 10, my own exhaustive run shows that only K_n has |m21| < 1e-6, and those cases were decided exactly. For n=11, every graph with margin below 1e-6 was flagged by the producer and decided exactly (only K_11). So no graph in the census can be misclassified, **conditional on LAPACK backward stability**. The scan is not interval-certified (Tier X), but the argument covers the whole census.
- exact_check.py: Descartes plus sympy `intervals` is sound for this use. The addendum promised Sturm sequences, and Descartes is equivalent for real-rooted polynomials. That is a cosmetic deviation.

## 4. Controls
- Graffiti 29: the n=7 first counterexample FEhf? is genuine (exact: Randic 3.4495 > n-(D) = 3). The n=8 firing G?zTb_ is genuine (R = 4 > 3). The n=9 graph H?B@tbg, n=10 graph I??FCpSJ?, and four n=11 firings are genuine (exact distance-matrix inertia via integer charpoly). Regular graphs give exact ties R = n/2 = n-(D). The producer's +1e-9 tolerance handles these correctly: a version of my own code without that tolerance over-counted by one at n=8. The 1862 total is reproduced on 5 of 40 parts (245 firings), but it remains Tier X and was not counted independently on the other 35 parts.
- Negative controls (lambda1 >= average degree; E >= n+ + n-): both are theorems and fire 0 times in my runs. They discriminate in the sense that they cannot fire on correct code.

## 5. Corrections (old -> new)
1. RESULT "Nothing found for 20, 21" -> "Kumar-Pragada, arXiv:2607.19817 (Jul 2026, unrefereed) claim E(G) >= 2(n - alpha) and deduce E >= 2 max(n+, n-), which is equivalent to WoW 20 and 21 (S+ = E/2); Fajtlowicz 1987 (WoW p.19) already gives the min version. The census is a finite consistency check of a claimed theorem, not a novel result." Put this at the top of RESULT.md, and add the same note to result.json and the journal and roadmap entries.
2. "conj 21 ... otherwise a clear gap (next smallest 0.22 at n=10, part 0)" -> "smallest non-K_n margin for 21: 0.2143 (n=5), 0.1463 (6), 0.1249 (7), 0.0941 (8), 0.0806 (9, HQhTQji), 0.0645 (10, IQhTQiitO), 0.0561 (11, JQhTQiiTVT?, part 39), certified; the margin shrinks with n". The producer's min_gap21 statistic includes K_n and could never show this.
3. "(conj 21 non-K_n margins at n=11 are >= the 1e-6 flag threshold, none flagged)" -> "smallest non-K_n margin for conj 21 at n=11 is 0.05606 (part 39)".
4. "all connected graphs with n <= 11" with total 1,018,690,325 -> "4 <= n <= 11 (1,018,690,325 graphs); n <= 3 is trivial: K1 (all zero) and K2 (spectrum {1,-1}) give equality in BOTH 20 and 21, K3 gives equality in 21, P3 is strict". Consequently "smallest margin for conj 20 is 0.236" holds only for n >= 4; over all connected graphs, 20 is tight at K1 and K2.
5. Equality claim -> "among connected graphs, equality in 21 occurs only at K_n (n <= 10 exhaustively, n=11 by the float flag band); disconnected unions of cliques also give equality".
6. "eigenvalue accuracy (~1e-13)" caveat -> add the zero-eigenvalue lower bound 6.2e-6 (section 3), which makes the inertia exact for the whole census under LAPACK backward stability.
7. Remove or strike the stale "n=11 NOT run" sentences in "What was run" and "Outcome", and the "Auditor must redo 2", which the UPDATE supersedes.
8. Addendum said "Sturm sequences"; the code uses Descartes' rule (equivalent for real-rooted polynomials). Note this as a deviation.

## 6. Unverified / open
- Kumar-Pragada's proof was not checked; it is a preprint.
- 35 of the 40 n=11 parts were not recomputed independently. They rest on the producer's run, my match on 5 parts plus one unmodified rerun, and the soundness argument in section 3.
- The ctl29 total of 1862 was not counted independently beyond those 5 parts.
- Conjectures 39, 40, 129, 143, 154, 195, 284 and 698 remain BLOCKED, and the third-party "already resolved" claims were not checked. Both are outside this audit.

Sources: arXiv:2607.19817 (https://arxiv.org/abs/2607.19817); arXiv:2409.15504 (https://arxiv.org/abs/2409.15504); arXiv:2509.05814; WoW scan pp. 19 and 23.
