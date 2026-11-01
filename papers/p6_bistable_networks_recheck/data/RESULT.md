# BIO-BISTAB: independent recheck of arXiv 2610.32739 (Peng, 23 Oct 2026, math.DS)

Recheck of a claim by others. Pure mathematical dynamical systems; no biological or medical claim; no novelty claim.
Outcome: **PARTIAL** (enumeration, 27 witnesses, JAC and DIV rules reproduced exactly; ROOT only partly; FLUX not; the 654 exclusions are NOT claimed reproduced).
Preregistration: PREREG_ITEM.md (sha256 in PREREG_ITEM.md.sha256), written before any computation. The author's code/data were not used (repo URL not in the paper; licence unchecked; nothing stored in bistab_thirdparty/).

## Pinned claim (from the paper text)
Complexes X,Y,2X,X+Y,2Y; at most 3 distinct directed edges (20 possible); model F: x'=a-rho x+H_x, y'=b-y+H_y (rho,a,b,k>0); E: rho=1.
Target: two distinct positive equilibria with trace<0, det>0 (the paper additionally shows a saddle in between). 681 orbit reps, 27 positive, 654 negative (JAC 245, DIV 216, ROOT 179, FLUX 14).

## Results
| Step | Result | Tier |
|---|---|---|
| P1 enumeration | 1351 labelled sets; 11 fixed by species exchange; 681 orbits with sizes 1/10/100/570. Numbering by first-seen representative in lexicographic edge order reproduces all 27 catalogue IDs of Table 1 (e.g. N0438, N0549, N0056 = X->X+Y, X+Y->2X). The 27 sets lie in 27 distinct orbits. | C |
| P2 witnesses | All 27 Table-2 rational parameter sets (rho=1): Groebner elimination, exact positive-root count (Sturm), y>0 and trace/det signs by rational interval arithmetic at 1e-40 isolating intervals: every one has exactly 3 positive equilibria = 2 sinks (trace<0, det>0) + 1 saddle (det<0); 0 undecided signs. | C |
| P3 JAC / DIV | Sign tests on the symbolic det DF and det K for all 681 reps: JAC excludes 245, DIV a further 216 (exactly the paper's counts); 0 of the 27 positives excluded. | C (for these sign tests as I implemented them) |
| P4 ROOT | My reading of the paper's description (nominal Sylvester resultant, either variable eliminated, rep or exchanged partner, coefficient classes +,-,mixed, <=2 sign variations, >=1 fixed coefficient): passes 105 of the 193 remaining negatives (paper: 179 of these + 14 FLUX); 0 of the 27 positives pass (correct). The other 88 are NOT reproduced; likely my reading is weaker than theirs, not evidence against them. | C (partial) |
| FLUX | 14 networks: not attempted (flux-cone decomposition). | none |
| P5 search | 681 reps x 125,000 log-uniform samples (a,b,rho,k in [1e-3,1e3]), 85.1M samples total: all 27 positives found with an exact-verified two-sink point (hit rate 0.34%..8.4%); the 654 negatives: 0 candidates at all. Evidence only (grid-resolution and sampling limited), not a proof. | X |

Controls: positive control Section 4 baseline (Y->2X, 2X->X+Y, X+Y->Y; a=4/99, b=1/90): direct exact substitution gives equilibria x=1/10,1/5,3/5 with det 25/9,-20/9,100/9 (paper's values) and my solver gives 2 sinks + 1 saddle. Negative: empty, X->Y, X<->Y, X+Y<->2X and N0056 networks each give exactly 1 positive equilibrium (1 sink). Perturbation: scaling inflow a by 1,2,5,20,100,1000 destroys bistability in all 27 witnesses (bistable at a x1: 27/27; all lose it at some factor). The search also served as a power check (27/27 positives rediscovered).

## Deviations and traps
- Table 2 was read from flattened PDF text; four rows (N0514, N0524, N0548, N0554) were first mis-grouped (k1=17/100, k2=9 ...); testing all token groupings gave a unique 2-sink reading k1=17, k2=100/9 (or 100/159). A transcription fix by testing; confirm against the PDF image or the author's catalogue.
- First search version had a numerical artefact (cancellation in the positive root of g); fixed with a stable root formula before the reported runs; the earlier run was discarded.
- Core-hours used about 1.8 (cores 2,3 only), inside the 4 h box.

## Not checked / what an independent auditor must redo
- The 654 exclusions are not proved here: ROOT 105/179 only under my reading, FLUX 0/14; the Descartes/resultant argument and flux-cone certificates need an independent implementation or the author's certificate files.
- Lemma 3 and the proof of Theorem 2 (minimality, small-rate inheritance) not rechecked; Lean not done.
- Table 2 against the actual PDF/catalogue values; E-model only at rho=1 (checked).
- Search limits: parameter range 1e-3..1e3, 500-point log grid in x, 125k samples per network.
