# AUDIT: BIO-BISTAB (recheck of Peng, arXiv 2610.32739v1, math.DS)

Auditor: independent Claude agent (producer != verifier), 2026-11-01. Own code only, in `/tmp/bistabaudit/code/` (net.py, a1_enum.py, a2_witness.py, a3_rules.py, a4_flux.py, a5_search.py, a6_controls.py). No producer code was run. The producer's `data/p2_witnesses.json` was read only to compare the parsed parameters. Cores 2 and 3 only, about 0.1 core-hours.
Source: the arXiv PDF (7 pp.), pdftotext plus a rendered image of p. 7 (pdftoppm, 110 dpi).

**Verdict: ACCEPT_WITH_CORRECTIONS.** Every computation the producer reports reproduces with independent code. The audit also reproduces the two exclusion rules the producer left open: ROOT gives 179/179 under the paper's reading, and FLUX gives 14/14. The producer's own text undersells the result in one place (the ROOT gap of 88 comes from the producer's own reading of the rule) and needs small wording fixes. Pure mathematics. No biological or medical claim. No novelty.

## 1. Paper pinned (checked against the producer's reading)
- Class: complexes C = {X, Y, 2X, X+Y, 2Y}. At most 3 distinct directed edges with alpha != beta (20 possible edges). Mass action, H_R = sum k_j (beta_j - alpha_j) z^alpha_j.
- Model E: z' = (a,b) - z + H. Model F: z' = (a,b) - diag(rho,1) z + H. Here a, b, k_j, rho > 0.
- Target ("bistable"): two distinct positive zeros with tr DF < 0 and det DF > 0. The abstract calls these "hyperbolic attracting".
- Orbit convention: complexes are ordered as listed, and edge sets are ordered lexicographically within each size. The paper does not spell out the representative rule; first appearance reproduces it.
- Rules (Sec. 2):
  - JAC: det DF in (x, y, rho, k) has nonnegative coefficients and the monomial rho with coefficient 1.
  - DIV: det K has nonnegative coefficients and ab with coefficient 1.
  - ROOT: nominal-degree Sylvester resultant. Each coefficient is either fixed strict (all monomial coefficients share a sign) or free in {-1, 0, 1}. The certificate needs at most 2 sign variations and at least one fixed strict coefficient.
  - FLUX: copositivity of R*^T H R* on the flux cone.
- The producer's reading matches on the class, models, target and convention. It differs on ROOT (see 5).
- Paper-internal inconsistency to note: Sec. 1 gives 1351 labelled networks, but Sec. 5 says "all 1362 labels" (1362 = 1351 + 11). This is not the producer's error.

## 2. Table 2 (PDF image, p. 7)
All 27 rows were read from the text layer and the rendered page. The four ambiguous rows are settled by the image:

| Row | a | b | k1 | k2 | k3 |
|---|---|---|---|---|---|
| N0514 | 3/100 | 3/100 | 17 | 100/9 | 2600/2809 |
| N0524 | 1/25 | 3/100 | 17 | 100/9 | 650/729 |
| N0548 | 1/50 | 1/25 | 17 | 100/159 | 2600/2809 |
| N0554 | 3/100 | 3/100 | 17 | 100/159 | 2600/2809 |

k2 = 25 (an integer) in N0510, N0515, N0520 and N0525. All 27 rows equal the producer's `params` exactly (0 differing rows).

## 3. Enumeration (own code)
- 1351 labelled sets, 11 fixed by species exchange, 681 orbits with sizes 1/10/100/570.
- First-appearance numbering in lexicographic order reproduces all 27 Table-1 IDs (27/27).
- N0056 is X->X+Y, X+Y->2X, as in the paper.
- The 14 FLUX IDs map to the networks listed in a4 output.

## 4. Witnesses (different method: Arb ball arithmetic, python-flint 0.9.0, 400 bits)
Method:
1. Take the exact resultant in y (sympy) and its square-free part.
2. Isolate its roots with certified Arb complex root isolation (flint `complex_roots`). The producer used Sturm sequences instead.
3. For each positive root, take both y roots of g in ball arithmetic. Discard a candidate when f is certified nonzero.
4. Decide the signs of y, tr and det by ball exclusion of 0.

Result: **27/27 have exactly 3 positive equilibria = 2 sinks (tr < 0, det > 0) + 1 saddle (det < 0), with 0 undecided signs.** The x-coordinates agree with the producer's (for example, N0438 gives 0.020611, 2.02, 397.909).

## 5. Exclusion rules (own implementation, F model, symbolic)
- **JAC 245, DIV 216 (further)**, applied in that order. By size: 0 edges 1/0, 1 edge 8/2, 2 edges 54/33, 3 edges 182/181. This is exactly the paper's table. 0 of the 27 positives are excluded.
- 193 negatives remain, and all 14 FLUX IDs are among them.
- **ROOT, two readings:**
  - **(i) Sylvester resultant at the symbolic degree of each polynomial in the eliminated variable** (sympy `resultant`), eliminating x or y. This passes **179** negatives: 13 with 2 edges and 166 with 3 edges, exactly the paper's per-size counts. It passes 0 positives and 0 FLUX networks. Eliminating y alone gives 171; x alone gives 126; their union is 179. Using the exchanged partner adds nothing (it is the same family).
  - **(ii) Fixed degree-2 Sylvester matrix (4x4) in the eliminated variable.** This passes exactly **105**, which reproduces the producer's number.
  - So the producer's 88-network gap is explained by its reading of "nominal degree". Reading (i) is the natural one. It is also sound: a fixed Sylvester determinant vanishes at every common root even under degree drop, and the strict coefficient rules out the zero polynomial.
- **FLUX 14/14 reproduced:**
  - Rays of the cone {w >= 0, U >= 0} were computed by enumerating (m+1)-subsets of active constraints, giving 6 to 9 rays per network. Then G = R^T H R, with w^T H w = det M(w) checked symbolically.
  - 11 networks have G entrywise >= 0.
  - The remaining 3 networks have reduced forms identical to the paper's:
    - N0391: [[1, -1], [-1, 4]], i.e. u^2 - 2uv + 4v^2, which is positive definite.
    - N0646: u^2 - uv + v^2, which is positive definite.
    - N0610: u^2 + 3uv + 2v^2 - uw - vw + w^2. This is not PSD but is copositive. The paper's identity (w - (u+v)/2)^2 + 3u^2/4 + 5uv/2 + 7v^2/4 was checked by hand expansion.
- **Conclusion:** all four certificate families reproduce: 245 + 216 + 179 + 14 = 654. The 654 exclusions rest on Lemma 3 (projection injectivity, ">= 3 equilibria for two sinks", and the Sard saddle argument) and on the JAC midpoint identity. These were read and look correct but are pen-and-paper, not machine-checked. Theorem 2 (minimality and inheritance) was not rechecked.

## 6. Controls and search
- **Sec. 4 baseline, displayed order** (Y->2X 10, 2X->X+Y 50/9, X+Y->Y 10; a = 4/99, b = 1/90):
  - Exact equilibria are x = 1/10, 1/5, 3/5 with y = 1/165, 7/330, 181/990.
  - det = 25/9, -20/9, 100/9, and tr = -1304/99, -1429/99, -2029/99. This matches the paper's trace formula.
  - Fold: a = 0.04610 gives 2 sinks and a = 0.04611 gives 1 sink, consistent with a+ = 0.0461033.
- **Negative controls:** empty, X->Y, X<->Y and X+Y<->2X each give exactly 1 positive equilibrium (a sink). N0056 at a=1/3, b=2/7, k=3/2, h=5/4 gives **0** positive equilibria. That is consistent with "at most 2", but "exactly 1" is parameter-dependent (see C4).
- **Inflow scaling:** scaling a by 2, 5, 20, 100 and 1000 destroys bistability for 27/27 witnesses.
- **Random search (Tier X):**
  - Setup: 20,000 log-uniform samples in [1e-3, 1e3] per network (a, b, rho, k), F model. Networks: the 27 positives plus the 193 ROOT/FLUX negatives, 4.4M samples in all.
  - All 27 positives were re-found; the lowest hit rate was 0.39%.
  - Among the negatives, my float pipeline flagged 247 samples on 10 networks. Every one is a float artefact: exact re-check with Arb on rationalized parameters gave 0 cases with >= 2 sinks and 0 undecided.
  - This is evidence only. Note that the producer's "0 candidates" depends on its pipeline.

## 7. Literature (alphaXiv, 2026-11-01)
- No independent verification or critique of 2610.32739 was found (0 votes, 2 views).
- Related work: 1909.11940 (flow addition preserving bistability), 2207.04971 (smallest bimolecular Hopf), 2608.01116 and 2406.11586 (zero-one networks), Joshi–Shiu, and Banaji–Boros–Hofbauer (cited by the paper).
- I found no prior enumeration of this exact 681/27 class (the search was not exhaustive).

## 8. Corrections (old -> new)
1. RESULT.md Outcome line: "ROOT only partly; FLUX not; the 654 exclusions are NOT claimed reproduced" -> keep this for the producer's own run, and append: "Independent audit (AUDIT.md) reproduced ROOT 179/179 (symbolic-degree Sylvester resultant, either variable) and FLUX 14/14 (own ray enumeration and copositivity), so all four exclusion counts reproduce. The exclusion still rests on the paper's Lemma 3 (pen-and-paper, read, not machine-checked)." Keep PARTIAL, because Lemma 3 and Theorem 2 are not formally checked and the producer did not itself reproduce ROOT and FLUX.
2. RESULT.md P4 row: "The other 88 are NOT reproduced; likely my reading is weaker than theirs" -> "The other 88 are not reproduced under my reading (fixed degree-2, 4x4 Sylvester matrix). With the resultant at the actual symbolic degree, the audit obtains exactly 179 (13 two-edge + 166 three-edge), as in the paper."
3. RESULT.md Deviations: "unique 2-sink reading k1=17, k2=100/9 (or 100/159)... confirm against the PDF image" -> "confirmed against the PDF image (audit): N0514 and N0524 have k2 = 100/9; N0548 and N0554 have k2 = 100/159; k1 = 17 in all four; k3 = 2600/2809, 650/729, 2600/2809, 2600/2809."
4. RESULT.md Controls: "N0056 networks each give exactly 1 positive equilibrium" -> "... each give exactly 1 positive equilibrium at the tested parameters (N0056 can also have 0, e.g. a=1/3, b=2/7, k=3/2, h=5/4, rho=1; the paper's bound is at most 2)."
5. RESULT.md "Not checked" list: "Table 2 against the actual PDF/catalogue values" -> "Table 2 confirmed against the PDF image (audit); author's catalogue not used." Also note the paper's own inconsistency: 1351 labelled networks (Sec. 1) vs "1362 labels" (Sec. 5).

## Still unverified
- Lemma 3 and the Sard step, Theorem 2 (deletion-minimality, inheritance) and the claim BE = BF beyond the counts. No Lean.
- The author's supplementary certificates and checker were not used.
- The 654 exclusions are reproduced as certificate checks, not as a proof independent of Lemma 3.
- Tiers: C for the exact parts (enumeration, witnesses, rule certificates) and X for the search.
