# GE-2: bistability census of 3-species open bimolecular mass-action networks (<=3 internal reactions)

Outcome: **FOUND (754 exact witnesses independently re-verified, 781/781 incl. control)**, with a large UNDECIDED residue; the census is not a complete classification. "New" = new within this class, not checked against Joshi-Shiu-type small-network classifications (see PRIOR_ART_ADDENDUM.md). MULTISTATIONARY_CERT (807) not independently re-verified (no witness files audited). Independently audited once (AUDIT.md, ACCEPT_WITH_CORRECTIONS; corrections applied 2026-11-11); no Lean, no human audit, not published. Preregistration: PREREG_ITEM.md (sha256 in PREREG_ITEM.md.sha256, frozen before any run).

## Class and enumeration (sanity counts match)
9 nonzero complexes, 72 directed edges, <=3 internal edges, inflow and linear removal for each species. Labelled networks 62269 (1+72+2556+59640); S3 orbits **10523** (Burnside agrees; orbit sizes 1/2/3/6 = 7/9/266/10241; sizes sum to 62269). 2-species control: 1351 labelled, 681 orbits.
Buckets: A = at most 2 species occur in internal reactions (681 orbits, reducible to Peng's class), B = 3 species but interaction graph disconnected (220 orbits), C = connected support 3 (9622 orbits); 79 of the 175 minimal (79 of the 727 bistable) have a never-reactant species and are effectively 2-species cascades; 96 minimal are irreducible by this screen. Nothing dropped; all classified by the same pipeline.

## Counts (orbits; labelled in brackets)
| bucket | MONOSTATIONARY (JAC) | BISTABLE_CERT | MULTISTATIONARY_CERT (no 2-sink witness) | UNDECIDED |
|---|---|---|---|---|
| A (681) | 245 (1444) | 27 (162) | 102 (612) | 307 (1824) |
| B (220) | 61 (346) | 0 | 0 | 159 (910) |
| C (9622) | 4765 (28158) | 727 (4338) | 705 (4176) | 3425 (20299) |
| total 10523 | 5071 | 754 | 807 | 3891 (37.0%) |

The SIGN rule excluded nothing beyond JAC. Bucket-A counts equal the 2-species control exactly (245/27/102/307), and the 27 are the Peng networks.
Bistable bucket C: 9 networks with 2 internal edges and 718 with 3. **175 of the 727 are minimal** (no proper edge subset is BISTABLE_CERT); these include the 9 two-edge ones: {2X->Y, Y+Z->X+Y}, {2X->2Y, Y+Z->2X}, {2X->2Y, Y+Z->X+Y}, {2X->X+Y, Y+Z->2X}, {2X->X+Y, Y+Z->X+Y}, {2X->Y+Z, Y+Z->X+Y}, {X+Y->Z, X+Z->2X}, {X+Y->2X, X+Z->2Y}, {X+Y->2X, X+Z->X+Y}. The full list is in census.jsonl (verdict BISTABLE_CERT, bucket C); witnesses/G*.json. Mechanism pattern: a quadratic autocatalytic or conversion loop through a complex containing Z (Y+Z, X+Z) closes a positive-feedback cycle; with only two internal edges one species mediates two nonlinear steps. Short descriptions per network were not curated; I did not check whether a Z-as-catalyst network is equivalent to a 2-species mechanism with a modified rate law, so "new" is relative to the class definition only, not to the literature.

## Certificates
BISTABLE_CERT: rational parameters, two distinct rational positive equilibria p,q, f(p)=f(q)=0 checked by exact Fraction substitution, exact Routh-Hurwitz at both (enclosures are degenerate [p,p]). MONOSTATIONARY_JAC: all coefficients of det(-J) nonnegative (midpoint identity for quadratic fields). MULTISTATIONARY_CERT: exact two equilibria only. UNDECIDED: no exclusion certificate and no witness within 2e5 sampled equilibrium pairs; this is search evidence, not absence. Bistable networks missed by the search sit inside UNDECIDED or MULTISTATIONARY_CERT.

## Controls (logs/controls.json)
Positive: 2-species run gives exactly 27 BISTABLE_CERT among 681 orbits, identical to Peng's Table 1 set; JAC 245 (Peng 245). 3-species bucket A reproduces the same counts. Negative: empty, X->Y, the X<->Y<->Z cycle (4 edges, external control): never BISTABLE_CERT. Corrupted witness (p+1/1000; rho*1.1) fails the exact check, uncorrupted passes.

## Deviations (honest list)
1. N0056 removed as a negative control: Peng's Table 1 lists it as bistable (the draft was wrong).
2. Stage-1 search defect found by the bucket-A control: it cannot sample networks with a species never changed by internal reactions (p_i=q_i is forced, probability zero). Fix (set q_i=p_i for such species) applied in code/ge2lib.py and rerun as stage 3 on the 766 affected non-bistable, non-excluded rows (27 became BISTABLE_CERT, 148 MULTISTATIONARY_CERT). Stage-1 rows remain in the logs; census.jsonl keeps the highest stage.
3. The preregistered stage 2 (1e6 pairs for multistationary-only networks) was NOT run. DIV/ROOT/FLUX rules not implemented. Alphabet-specific Peng rules do not transfer.
4. The UNDECIDED fraction (37%) stayed under the 50% kill line.

## CPU ledger
n=3 census all stages 4.231 core-h; n=2 control 0.280 core-h; controls/aggregation small; total about 4.5 core-h of the 15 cap; cores 1-6, detached, resumable jsonl. No reboot occurred during the run (none detected; wall clock was not tracked precisely).

## An auditor must re-derive
Enumeration and orbit count independently; JAC exclusions (sign of every coefficient); every witness (re-substitute rational parameters, re-check f(p)=f(q)=0 and Routh-Hurwitz) in a different CAS; minimality (subset lookup uses canonical forms in census.jsonl); that MULTISTATIONARY_CERT/UNDECIDED rows really lack a witness (search is sampling only); the definition of buckets and the claim that the Z-catalyst mechanisms are not trivial reductions.
