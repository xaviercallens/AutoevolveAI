# GE-2 independent audit (auditor != producer), 2026-11-11

Verdict: **ACCEPT_WITH_CORRECTIONS**.

The auditor wrote these scripts from scratch: /tmp/ge2audit/{verify,enum,jac,pc,negctl}.py. They do not import producer code. They ran with system python3 -I on core 7, using exact `fractions` arithmetic and sympy. The only producer artefact read as data is the Peng Table 1 edge list (results/proposal6/.../BIO-BISTAB/code/table1.py), the same list the p6 recheck lane used.

## 1. Definitions and preregistration
- The PREREG_ITEM.md sha256 (a970a7a8...618f) matches PREREG_ITEM.md.sha256. The hash is self-attested and has no independent timestamp.
- Class: every species has its own inflow a_i and removal rho_i, all free and positive, including species that no internal reaction touches. "Bistable" means two distinct positive equilibria, both Hurwitz, for one parameter vector. The prereg, the RESULT and the witness files all use these definitions. Every witness has len(a) = len(rho) = 3, all parameters > 0, and one parameter vector.
- RESULT.md discloses the deviations: N0056 was dropped, the stage-1 sampling defect was fixed and rerun as stage 3, and stage 2 was not run.

## 2. Enumeration (independent)
- n=3: 9 complexes, 72 edges, 62,269 labelled networks, 10,523 orbits. Burnside also gives 10,523.0.
- n=2: 1,351 labelled networks and 681 orbits.
- The census rows cover every orbit exactly once. 0 bucket mismatches and 0 orbit-size mismatches. Every (bucket, verdict) count matches the RESULT table.

## 3. Witnesses (all of them)
- 781 of 781 pass: the 754 G witnesses and the 27 P witnesses. Checks per witness:
  - exact f(p) = f(q) = 0;
  - p != q, and both are positive;
  - exact Routh-Hurwitz at both points (char. poly. of J: c1 > 0, c3 > 0, c1*c2 > c3; for 2x2, tr < 0 and det > 0);
  - the edges match the census row, and the row verdict is BISTABLE_CERT.
- There is no BISTABLE_CERT row without a witness and no witness without such a row.
- Negative controls on the verifier: p+1/1000 fails, rho*1.1 fails, +I is rejected as not Hurwitz.

## 4. JAC rule
- Soundness: f is quadratic, so f(x) - f(y) = J((x+y)/2)(x-y) exactly. The midpoint lies in the positive orthant. If det(-J) is a polynomial in (x, rho, k) with nonnegative coefficients and the rho1*rho2*rho3 coefficient is 1, then det(-J) > 0 there, so there is at most one positive equilibrium. This argument is valid. It is the determinant-sign (Craciun-Feinberg-type) criterion for fully open networks.
- Recomputed with sympy:
  - 60 of 60 random JAC rows have all coefficients nonnegative;
  - 40 of 40 random non-JAC rows have a negative coefficient;
  - jac = True occurs only on MONOSTATIONARY rows.
- Numerical falsification on 30 JAC rows (40 parameter draws x 30 starts each) found no second positive root. A first pass reported 3 hits; these were duplicates of one root that the dedupe tolerance was too tight to merge. The falsifier's positive control found 3 roots on witness G01312.

## 5. Controls
The set of 27 P witnesses equals Peng's Table 1 set up to S2 symmetry, and the 2-species census marks exactly these 27 as bistable.

## 6. Novelty and wording
- All 9 two-edge bucket-C networks are irreducible in this screen: every species is a reactant somewhere, every species changes net, and no equation decouples. Eliminating a species by a quasi-steady-state reduction gives non-mass-action rates, so none of the 9 is literally one of Peng's 27. This was not checked against the literature.
- **79 of the 175 minimal networks** (and 79 of the 727 bucket-C bistable networks) contain a species that is never a reactant. The other two species then form an autonomous 2-species subsystem, so bistability lives in a 2-species projection; these are cascades, not 3-species mechanisms.
- 96 minimal networks remain irreducible.
- The 718 three-edge networks that contain a bistable subnetwork are expected by inheritance; they are not separate findings.
- Possible prior art, from memory and not checked: Joshi-Shiu on small fully open networks with two non-flow reactions, and Tang-Xu arXiv 2008.03846. alphaXiv returned no same-day scoop.

## 7. Corrections to RESULT.md
1. "C = connected genuinely 3-species" -> "C = connected support 3; 79 of the 175 minimal (79 of the 727 bistable) have a never-reactant species and are effectively 2-species cascades; 96 minimal are irreducible by this screen".
2. Outcome line: "FOUND (certified)" -> "FOUND (754 exact witnesses independently re-verified, 781/781 incl. control); 'new' = new within this class, not checked against Joshi-Shiu-type small-network classifications".
3. Add: "MULTISTATIONARY_CERT (807) not independently re-verified (no witness files audited)".

## Tiers
- **C**: the 754 bistable certificates and the 27 controls; the JAC exclusions (sampled 60, rule proven sound); the enumeration counts.
- **Not audited**: the 807 MULTISTATIONARY_CERT rows.
- **X**: the 3,891 UNDECIDED rows; completeness of the census; novelty.
