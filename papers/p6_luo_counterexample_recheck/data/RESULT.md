# AIC-LUO: independent exact RECHECK of arXiv 2610.13979 (Guo, 11 Oct 2026), "A counterexample to three conjectures of Luo"

Label: recheck of a claim by others. No novelty claim. Producer pass, unaudited. Preregistration: PREREG_ITEM.md (sha256 in PREREG_ITEM.md.sha256, written before any computation).
Environment: own Python code (code/, not from the paper), sympy 1.14, GAP 4.11.1, Regina 7.4.1 and SnapPy 3.3.2 in a venv outside the repo; taskset -c 1.

## Outcome: CONFIRMED for the computational clauses; clause (iv) only numerically, and the logical reduction to Luo's conjectures stays Tier L

### Recomputed exactly (Tier C)
1. Triangulation. From the four face pairings I built the gluing. All 8 faces are glued once, all gluing permutations are odd (1230, 1230, 3201, 3201 and inverses), 1 vertex class, vertex-link counts V,E,F = 6,12,8 with chi = 2, 3 edge classes of degrees 2,5,5, no edge glued to itself with reversed orientation, chi(M) = 1-3+4-2 = 0. The local-edge-to-class table equals the paper's table (2) exactly. Regina agrees: valid, closed, orientable, 1 vertex, 3 edges of degrees 2,5,5.
2. pi1. My code derives the one-vertex edge presentation (relators c^2 b^-1, abc, acb, b^-1 c b^-1). GAP: order 3, abelian invariants [3], C3, and the generator a is trivial, so the loop edge a (vertex to vertex, there is one vertex) is null-homotopic. Second route (dual 2-complex, walk around each edge class, a spanning-tree generator set to 1): order 3, C3. Regina: H1 = Z_3, pi1 simplified to <a | a^3>.
3. Isomorphism signature for the audit: Regina isoSig cMcabbjak. The triangulation is combinatorially isomorphic (Regina isIsomorphicTo) to Regina's Example3.lens(3,1), 2 tetrahedra, same signature. "This is a 2-tetrahedron L(3,1) triangulation" is confirmed against Regina; "2 is the minimum" is the cited Jaco-Rubinstein-Tillmann fact (Tier L).
4. Q-matching. My I (from edge classes) and W = I*Omega equal the paper's matrices (5) entry by entry. rank W = 2, kernel dim 4. The Haken matching equations built independently from the gluing arcs (14 variables, rank 9, solution dim 5) project onto the 6 quad coordinates with dimension 4, equal to ker W. Exhaustive enumeration of all supports of size 1 and 2: the only nonzero vectors with at most 2 nonzero entries are the multiples of (1,0,0,1,0,0), in both the projected space and ker W. So Lemma 3.1 holds. An LP (data/nonneg_lp.json) shows this direction is the projection of a nonnegative Haken solution (triangles (0,0,1,1,1,1,0,0)), so a genuine 2-quad-type normal solution exists but only with quads x1, y1; no cluster of three.
5. Thurston equations. The edge equations from my edge classes coincide with the paper's printed system (symbolic differences zero). The Groebner basis over Q of the system plus the nondegeneracy relation t*z(1-z)w(1-w)=1 is {1}: no solution, in both orientation conventions (paper's cyclic order and its mirror). After w=1/z the last two equations reduce to 1/z and z as the paper says. Remark 4.2 confirmed: at z=w=-1 the edge products are (1,-1,-1); with edge products allowed in {+1,-1}, the system is solvable exactly for the sign patterns (+,-,-), (-,+,-), (-,-,+) and unsolvable for the other five, including (+,+,+).
No Lean used; Tier A not claimed.

### Numerical only (clause (iv), Tier C-numeric, not a proof)
SAS(T): the constraint matrix has rank 4. Solving the periodic constraints by hand gives the family x1=2t, y1=-2t, x2=s, x3=pi-2t-s, y3=t-s+k*pi, y2=pi+t+s-k*pi (t,s in [0,2pi), k in {0,1}); numeric constraint residual 4e-15 and edge c holds identically. Grid 1500^2 plus Nelder-Mead refinement with exact Lobachevsky values: maximum volume 1.58865 attained at 8 symmetric points, all with min|sin theta| = 0.39, so smooth. The best volume found on the sampled non-smooth sub-loci (some u = +-1, coarse sampling) is 1.0149, lower. An earlier random-start SLSQP run (data/m5_sas.json) only reached 1.5747 (inferior local optimizer; kept for transparency). This agrees with (iv) but is a floating-point search; the paper's proof uses Luo Thm 4.2(a) and 4.4 (Futer-Gueritaud), which I did not read or verify (Tier L).

### Controls
- Positive P-a: Regina figure-eight (2 tets, oriented): degrees (6,6); my solver finds it solvable; z=w=exp(+-i pi/3) satisfy my edge equations; SnapPy 4_1 shapes (0.5+0.866i) satisfy them to 1.4e-15. This does not discriminate the two orientation conventions.
- Positive P-b: my pi1 code on Regina lens spaces: L(3,1) C3, L(5,2) C5, L(7,2) C7, L(2,1) C2, S^3 trivial; matches Regina's H1.
- Positive P-c: Regina's quad matching matrix on the paper triangulation has rank 2 on 6 columns (kernel dim 4), equal to my ker W dimension.
- Negative N-a: 20 single-pairing perturbations (each of the 4 pairings, 5 other vertex orderings of the target face): 0 of 20 keep the claim profile (1 vertex, degrees 2,5,5, pi1 of order 3, same I matrix).
- Negative N-b: 18 single-entry increments of I: Thurston unsolvable in all 18. Weak control (the solver never said yes); the discriminating "yes" cases are P-a and the sign patterns in item 5.

## Not checked and limits
- Luo's definitions of cluster, 2-quad-type and Conjectures 1-3 were taken from the paper and from search snippets about Luo arXiv 1003.4413 (not read in full). The step "(i)-(iv) refute C1, C2, C3" is Tier L. I checked both the signed (as in the paper) and the nonnegative variants of the 2-quad-type solutions: same conclusion.
- Minimality of 2 tetrahedra for L(3,1) (JRT 0805.2425) and irreducibility of L(3,1): cited, not reproduced.
- Clause (iv) numerical only; Theorems 4.2(a), 4.4 not verified.
- Regina comparison is by isomorphism of the unlabelled triangulation; vertex-order-labelled facts come from my own code.
- Prior-art search is thin (one alphaXiv discover call, two web searches). No independent recheck or earlier refutation found; "not found" is relative to these queries.

## For an independent auditor to redo
Rebuild the gluing with Regina from the four pairings and confirm isoSig cMcabbjak; recompute I, W with another implementation (e.g. Regina's full normal-surface quad enumeration, not only its rank); read Luo arXiv 1003.4413 and decide whether Conjectures 1-3 as stated there (not as quoted by Guo) are refuted; recompute the SAS maximum with interval arithmetic; confirm minimality via the Regina census.

## Files
code/ (luo_lib.py, m12_structure.py, m34_equations.py, m5_sas_volume.py, m5b_sas_param.py, nonneg_lp.py, controls.py), data/*.json, logs/, result.json (sha256 of every file). The paper full text was read through alphaXiv and is not stored in the repo.
