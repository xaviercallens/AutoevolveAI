# AUDIT: AIC-LUO (recheck of Guo, arXiv 2610.13979)

Auditor: independent Claude agent (producer != verifier). Date: 2026-11-01 (worktree clock). Core: taskset -c 1.
Auditor code: /tmp/luoaudit/ (a1_struct.py, a2_qmatch_thurston.py, thurston.sing, a3b_sas_exact.py, a3c_shape.py, a3d_elementary.py, a4_census.py, a5_ns.py; outputs a*.json). None of the producer's code was imported or run. The producer's venv was used read-only for the Regina 7.4, sympy 1.14 and mpmath 1.3 libraries. Singular, from /usr/bin, was used for the Groebner bases.
Integrity: PREREG_ITEM.md matches PREREG_ITEM.md.sha256 (OK), and all 21 sha256 entries in result.json match the files on disk (0 mismatches).

## Verdict: ACCEPT_WITH_CORRECTIONS

Every computational clause reproduces by an independent route. No disagreement was found. The corrections below concern wording and scope. Two of them are tier upgrades that the audit makes possible: (iv) becomes Tier C through an elementary analytic bound, and minimality becomes Tier C.

## 1. Luo's conjectures as stated by Luo (arXiv 1003.4413v2, read pp. 2-3, 6-9, 12-14, 17-20)

- Conjecture 1 (p. 3) covers a "closed irreducible orientable minimally triangulated 3-manifold". The alternative is (1) a solution to Thurston's equation or (2) a cluster of three 2-quad-type solutions to Haken's equation.
- Conjecture 2 (p. 19) covers a "minimally triangulated closed irreducible 3-manifold" where all maxima of vol on SAS(T) are smooth, and concludes that Thurston's equation has a solution. Orientability is implicit, since Luo's whole setting is oriented.
- Conjecture 3 (p. 20) covers a "minimally triangulated closed orientable 3-manifold" with an edge whose endpoints agree and which is null-homotopic, and concludes that a cluster of three 2-quad-type solutions exists.
- Definitions:
  - 2-quad-type means exactly one or two nonzero quad coordinates (p. 2).
  - A cluster is three such solutions, not necessarily distinct, with x_i(q_i) != 0 for three distinct quads of one tetrahedron (pp. 2-3, 19).
  - Haken's equation (2.1) is a homogeneous linear system on R^Delta x R^Quad, and S_ns is its real solution space (p. 8).
  - i(e,q) counts local edges of class e disjoint from q (p. 7).
  - Thurston's equation (p. 12, eq. 3.7) has z(q) in C\{0,1}, z(q') = 1/(1-z(q)) for q -> q', and prod_q z(q)^{i(e,q)} = 1. The "generalized" equation allows ±1.
  - SAS is defined on p. 14, smooth points on p. 17, Theorem 4.2 is on p. 17 and Theorem 4.4 (Futer-Gueritaud) on p. 18.
- Guo's (C1)-(C3) and his definitions match Luo's text faithfully, including the hypotheses, Luo's real (signed) solutions, and the shape rule. No gap was found between Guo's quotation and Luo.
- Robustness of (ii): requiring nonnegativity, integrality, or at most one quad type per tetrahedron only shrinks the set of 2-quad-type solutions, so their supports stay inside {x1, y1}. The refutations do not depend on which reading of "solution to Haken's equation" is used.
- Logical step: (ii)+(iii) refute C1, (iii)+(iv) refute C2, and (i)+(ii) refute C3. Given the definitions above, this is elementary and checked. The remaining Tier-L inputs are listed in section 9.
- Caveat: I read arXiv v2 (2010). Guo cites the Contemp. Math. 541 (2011) version, which I did not compare.
- Scope: Guo's Remark 1.2 states that L(3,1) is not simply connected, so the special case used in Luo's Poincare-conjecture route is not addressed. The producer's RESULT.md omits this sentence (correction 3).

## 2. Triangulation, H1, pi1 (own union-find, own chain complex, sympy coset enumeration, Regina)

- Gluing permutations are 1230, 1230, 3201, 3201, all odd. Each of the 8 faces is glued exactly once.
- There is 1 vertex class and 3 edge classes, of degrees 2, 5, 5, and no edge is glued to itself reversed.
- The vertex link has (V,E,F) = (6,12,8) and chi = 2, and chi(M) = 0.
- My local-edge table equals the paper's table (2) exactly.
- Homology comes from the integer Smith normal form of my own boundary matrices, where d2 is 3x4, d3 is 4x2 and d2*d3 = 0:
  - SNF(d2) = diag(1,1,3) and SNF(d3) = diag(1).
  - Hence H1 = Z/3, H2 = 0 and H3 = Z.
- Fundamental group:
  - My one-vertex presentation, with generators oriented as in the paper (A01, A02, A03), gives exactly the paper's relators (3): c^-2 b, b c^-1 b, a b^-1 c^-1, a c^-1 b^-1.
  - sympy FpGroup gives order 3. Coset enumeration of <a> gives index 3, so a = 1: the loop edge a is null-homotopic.
- Regina 7.4 confirms valid, closed, orientable, 1 vertex, degrees (2,5,5), isoSig cMcabbjak, H1 = Z_3, pi1 = <a | a^3>. The triangulation is isomorphic to Example3.lens(3,1), and Census.lookup gives "L(3,1) : #3".

## 3. Q-matching and Lemma 3.1

- The I matrix is computed from Regina's own edge skeleton, not from my union-find. It equals the paper's I, and W = I*Omega equals the paper's (5).
- Regina's own quad matching matrix (makeMatchingEquations, NS_QUAD) is entry-for-entry identical to W, signs included.
- rank W = 2, so ker W has dimension 4.
- Regina's standard (Haken) matching matrix has rank 9 and a 5-dimensional solution space. Its projection to the 6 quad coordinates has rank 4 and equals ker W.
- W has no zero column. The only column pair of rank < 2 is (x1, y1), with columns (0,-2,2) and (0,2,-2). So Lemma 3.1 holds, and with it (ii).

## 4. Thurston's equations (Singular std, lex order t > w > z; nondegeneracy t*z(1-z)w(1-w) = 1)

- The edge equations from my I are zw = 1, (w-1)^2/(w(z-1)^2) = 1 and (z-1)^2/(z(w-1)^2) = 1, as in the paper. The mirror convention gives zw = 1, w(z-1)^2/(z^2(w-1)^2) = 1 and z(w-1)^2/(w^2(z-1)^2) = 1.
- In both conventions the Groebner basis is {1} for (+,+,+), so (iii) holds.
- I solved all 8 sign patterns × 2 conventions:
  - Exactly (+,-,-), (-,+,-) and (-,-,+) are solvable.
  - (+,-,-) gives z = w = -1, which is Remark 4.2.
  - (-,+,-) gives the cubic z^3 - z^2 + 3z + 1 = 0, and (-,-,+) gives z^3 - 3z^2 - z - 1 = 0 (paper convention).
  - The other five patterns give {1}.
- A hand check gives the same: w = 1/z reduces the b- and c-equations to 1/z = 1 and z = 1 in both conventions.
- The solvable sign patterns serve as positive controls for the pipeline.

## 5. Clause (iv): now Tier C (elementary bound); no longer depends on Luo Thm 4.2(a), Futer-Gueritaud or Milnor

Argument (auditor):
- **A partially flat tetrahedron contributes zero volume.** Angles are taken mod pi, since Lambda is odd and pi-periodic. In each tetrahedron the three arguments sum to pi mod 2pi. If one of them is in piZ, the other two sum to 0 mod pi, so Lambda(b) + Lambda(c) = 0. Luo uses the same identity on p. 19.
- **A non-smooth point has volume at most v3.** At such a point one tetrahedron contributes 0. The other contributes at most v3 = 3*Lambda(pi/3) = 1.0149416, the regular ideal tetrahedron. To see this, reduce the three angles into [0, pi). Their sum is then 0, pi or 2pi. A sum of 0 gives volume 0. A sum of pi is an ideal tetrahedron, with volume at most v3 by Milnor's bound. A sum of 2pi becomes a sum of pi under a -> pi - a, which flips the sign, so the volume is <= 0. The Milnor-free variant below avoids this bound.
- **The maximum exceeds v3.** The exact point theta/pi = (3/5, 1/8, 11/40, 7/5, 17/40, 47/40) lies in SAS(T), checked in exact rationals:
  - tetrahedron sums 1 and 3;
  - edge sums 2, 4, 2;
  - all six angles are non-integer multiples of pi, so the point is smooth.
- Its volume is evaluated as a partial sum of Lambda(theta) = (1/2) sum sin(2n theta)/n^2 with N = 2000, with an explicit tail bound of 6/(2N) = 0.0015. The partial sum is 1.586786 (mpmath Clausen value 1.586786), so the certified lower bound is 1.58529 > v3 = 1.0149416, a margin of 0.570 (see a3b.json).
- Hence every maximum is smooth.
- **Milnor-free version (a3d_elementary.py).** Lambda'(theta) = -log|2 sin theta|, so |Lambda| <= Lambda(pi/6) everywhere. Lambda(pi/6) is bounded by its partial sum plus a tail of 1/(2N) <= 0.507721, so at any non-smooth point vol <= 3 Lambda(pi/6) <= 1.523163. The smooth lower bound 1.585286 still wins, by 0.062.
- **Tier of (iv).** (iv) therefore rests on calculus, a tail-bounded series and an exact rational SAS point: Tier C. It uses neither Milnor nor Luo Thm 4.2(a)/4.4.
- **Precision caveat.** The partial sums are 30-digit mpmath floats, not interval arithmetic. Rounding error is about 1e-25, many orders below either margin.
- **The supremum v3 is attained.** The non-smooth point theta/pi = (2/3, 0, 1/3, -2/3, 1/3, 4/3) lies in SAS(T), checked exactly: tetrahedron sums 1 and 1, edge sums 0, 2, 2, and x2 = 0. Its volume is exactly v3 = 1.0149416: tetrahedron A contributes 0 and tetrahedron B is the regular one. So the maximum of vol over the non-smooth locus is exactly v3, using Milnor for the upper bound. The producer's "best non-smooth sampled 1.0149" is this supremum, not a sampling artefact.

Reproduction of the producer's numbers (floating point, not needed for the proof):
- I parametrised SAS myself: y1 = -x1, x3 = 1-x1-x2, y2 = x2 + x1/2 (mod 1), y3 = 1+x1-y2. The edge constraints hold identically on this family.
- The local maximum through the exact point is at vol 1.58864663930016, at theta/pi = (0.614567, 0.128478, 0.256956, -0.614567, 0.435761, 1.178806).
- Its Hessian eigenvalues are (-13.7, -50.4), so it is a strict local maximum, and min|sin theta| = 0.392754. The producer reports 1.5886466393 and min|sin| 0.39275.
- A coarse 200x200 scan of the family finds nothing higher than 1.58846.
- Consistency with Luo Thm 4.2(b): at this smooth maximum, Luo's formula z(q) = sin(q')/sin(q'') e^{iq} gives edge products (-1, -1, +1) to 1e-30. The induced shapes obey the shape rule in one of the two cyclic orders (residual 1e-12), and (-,-,+) is solvable in both conventions (section 4). So it is a generalized, not genuine, solution, as Thm 4.2(b) and (iii) together predict.

## 6. Minimality and uniqueness (Regina brute-force census; my own enumeration of all gluings)

- 1 tetrahedron: there are 108 gluings, of which 27 are closed, orientable and valid. They fall into 4 isomorphism classes with H1 in {0, Z_4, Z_5}, and none has H1 = Z_3. So no 1-tetrahedron triangulation of L(3,1) exists, and the minimum is 2. This is Tier C (Regina validity + homology), replacing the JRT citation.
- 2 tetrahedra: there are 136080 gluings, of which 5088 are closed, orientable and valid. They fall into 16 classes, and three of them have H1 = Z_3 and pi1 = <a|a^3>. Regina's census names them L(3,1) #1, #2, #3:
  - cMcabbgaj: 1 vertex, degrees 1, 2, 9;
  - cMcabbjak: 1 vertex, degrees 2, 5, 5 (Guo's);
  - cPcbbbaai: 2 vertices.
- Guo's triangulation is therefore NOT the unique one-vertex minimal triangulation of L(3,1). There are two, and Guo's is the (2,5,5) one. This does not affect the counterexample, but the wording should not suggest uniqueness. The other one-vertex triangulation was not tested against C1-C3.
- Naming the classes as L(3,1) relies on Regina's census and on pi1 = Z/3 implying L(3,1), which is Tier L (geometrization). For Guo's own triangulation, the identification with JRT's figure and Regina's lens(3,1) construction suffices.

## 7. Nonnegative Haken solution (producer's LP)

I enumerated vertex normal surfaces with Regina (NormalSurfaces, standard and quad coordinates, on the paper's labelling).
- Standard coordinates give two vertex surfaces:
  - the vertex-linking sphere (no quads);
  - a connected orientable surface with chi = 0 (a torus), with quads (1,0,0,1,0,0) and triangles (0,0,1,1,1,1,0,0).
- Quad coordinates give the same torus alone.
- This confirms the producer's LP output exactly: a genuine normal surface exists with quads only in x1 and y1, and there is no cluster.

## 8. Literature (same day)

- alphaXiv discover (Luo conjecture / 2-quad-type / Thurston's equation / circle-valued angle structure) found only 2610.13979, 1003.4413, 0903.1138 and 2303.04380.
- 2303.04380 (circle-valued angle structures and obstruction theory) is related background, not a recheck.
- A web search for the exact title found nothing.
- No independent verification or critique of 2610.13979 was found, and no earlier refutation of Luo's Conjectures 1-3. "Not found" holds only relative to these queries.

## 9. Corrections (exact old -> new)

1. RESULT.md item 2: "relators c^2 b^-1, abc, acb, b^-1 c b^-1" -> "relators c^2 b^-1, abc, acb, b^-1 c b^-1 (generators b, c oriented opposite to the paper's A02, A03; with the paper's orientation these are exactly the paper's relators (3): c^-2 b, a b^-1 c^-1, a c^-1 b^-1, b c^-1 b; independently confirmed by the auditor)".
2. RESULT.md "Numerical only (clause (iv), Tier C-numeric, not a proof)" -> "Clause (iv): numerically by the producer; made exact by the auditor (AUDIT.md section 5): a partially flat tetrahedron contributes 0 volume, so vol <= v3 = 1.01494 at every non-smooth point, while the exact smooth point theta/pi = (3/5,1/8,11/40,7/5,17/40,47/40) has vol >= 1.58529 (tail-bounded series, 30-digit floats); even without Milnor, the elementary bound 3 Lambda(pi/6) <= 1.52316 suffices; Tier C; this route does not use Luo Thm 4.2(a), Futer-Gueritaud or Milnor". Likewise, in "The best volume found on the sampled non-smooth sub-loci ... is 1.0149, lower", add: "(this is the exact maximum v3 = 3 Lambda(pi/3) over the non-smooth locus, attained at theta/pi = (2/3,0,1/3,-2/3,1/3,4/3))". In result.json, set tiers "M5": "C-numeric" -> "C (auditor's analytic bound)".
3. RESULT.md "Not checked and limits", first bullet: "Luo's definitions ... were taken from the paper and from search snippets ... (not read in full). The step ... is Tier L." -> "Luo's Conjectures 1-3 and the definitions (2-quad-type, cluster, Haken solutions over R, Thurston's equation, SAS, smooth point) were checked by the auditor against Luo arXiv 1003.4413v2 pp. 2-3, 7, 12-14, 17-20: Guo's quotation is faithful; the deduction (i)-(iv) => not C1, C2, C3 is elementary given them. Scope (Guo Remark 1.2): the conjectures are refuted as stated; since L(3,1) is not simply connected, the restricted versions in Luo's Poincare-conjecture route are not addressed. The published Contemp. Math. 541 text was not compared."
4. RESULT.md item 3 / "Minimality ... cited, not reproduced" -> "Minimality reproduced by the auditor (Tier C via Regina): none of the 108 one-tetrahedron gluings gives H1 = Z_3. Note: L(3,1) has two one-vertex 2-tetrahedron triangulations (cMcabbgaj, degrees 1,2,9; cMcabbjak, degrees 2,5,5) plus one 2-vertex one (cPcbbbaai); Guo's is cMcabbjak = Regina census L(3,1) #3."
5. result.json "outcome": "CONFIRMED (computational clauses); (iv) numeric; logic Tier L" -> "CONFIRMED (recheck, no novelty): (i)-(iii) Tier C; (iv) Tier C (auditor's elementary bound); minimality Tier C (auditor census); Luo's definitions checked against 1003.4413v2; the reduction to C1-C3 needs no unverified theorem once (iv) is shown directly; Tier A not reached".

## 10. What remains unverified

- Milnor's single-tetrahedron maximum v3, a classical fact (Tier L). It is used only for the side remark that the non-smooth maximum equals v3, not for (iv).
- The volume evaluations use 30-digit floats with a rigorous series-tail bound, not interval arithmetic.
- Notes on reading a3b.json:
  - `family_reproduces_point = 2.0` is a mod-2 equivalence (y1 = -3/5 versus 7/5).
  - The "0.5" entry of `coarse_scan_200x200_max` lies off SAS and should be ignored.
  - `shape_rule_resid` is explained by a3c_shape.py: the rule holds in the opposite cyclic order, with residual 1e-12.
- The geometrization step "pi1 = Z/3 implies L(3,1)" for naming the other census classes. It is not needed for Guo's triangulation.
- The Contemp. Math. version of Luo's paper.
- Luo Thm 4.2 and 4.4, which are no longer needed for (iv). The Segerman-Tillmann theorem (Remark 4.3) was not checked.
- No Lean formalisation; Tier A not reached. Wording stays "recheck, no novelty".
