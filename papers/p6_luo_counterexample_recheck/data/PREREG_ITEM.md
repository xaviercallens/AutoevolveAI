# AIC-LUO preregistration (written before any computation)
Date: 2026-11-01 (worktree clock). Producer: Claude. Label: RECHECK of a claim by others (Guo, arXiv 2610.13979, 11 Oct 2026). No novelty claim.
Core: taskset -c 1 only. Time box ~2 core-hours.

## Prior-art search (done before this file; same day)
- alphaXiv discover_papers (Luo conjecture / Thurston gluing / 2-quad-type / counterexample): only 2610.13979 itself (4 votes). No independent recheck found.
- WebSearch: 2610.13979 not indexed by the web engine; related known facts: L(3,1) has a 2-tetrahedron triangulation (Jaco-Rubinstein-Tillmann arXiv 0805.2425; minimal tet count 2, Matveev complexity 0), Luo arXiv 1003.4413 (Conjecture 1 = Haken-Thurston Alternative; 2-quad-type = exactly one or two nonzero quad coordinates), Luo-Tillmann arXiv 1312.5087. No statement found that the conjectures were previously known false. "Not found" is relative to these queries only.
- Luo's text 1003.4413 and JRT 0805.2425 NOT read in full: minimality of 2 tetrahedra, Luo Thm 4.2(a), Thm 4.4 (Futer-Gueritaud) stay Tier L.

## Claims to recheck (from the paper, pinned)
Triangulation: tets A,B (vertices 0..3); face pairings (vertex-order preserving, first -> second):
 A(123)->A(230); B(013)->B(120); A(013)->B(321); A(012)->B(320).
 Claimed vertex perms 1230,1230,3201,3201 (all odd); 1 vertex; link = sphere (8 triangles,12 edges,6 vertices); 3 edge classes a,b,c with local labels A: 01 a,02 b,03 c,12 c,13 b,23 c; B: 01 b,02 c,03 b,12 b,13 c,23 a; degrees 2,5,5.
 pi1 = Z/3 (presentation (3) in the paper); a null-homotopic loop edge.
C1 (Q-matching): W = rows a,b,c; cols x1,x2,x3,y1,y2,y3 = [[0,1,-1,0,1,-1],[-2,0,2,2,-1,-1],[2,-1,-1,-2,0,2]]; kernel vectors with <=2 nonzero entries are multiples of (1,0,0,1,0,0).
C2 (Thurston): edge eqs zw=1, (1/(1-z))^2 w ((w-1)/w)^2 = 1, z((z-1)/z)^2 (1/(1-w))^2 = 1 have no solution with z,w not in {0,1}.
C3 (Remark 4.2): z=w=-1 solves the generalized equation with edge products (1,-1,-1).
C4: SAS(T) nonempty, every volume maximum smooth (Tier L for the Futer-Gueritaud reduction; I only do a numeric check of the maxima, not a proof).
C5: the conclusion (counterexample to Luo C1, C2, C3) follows from (i)-(iv) given Luo's definitions as quoted in the paper (not independently re-derived: Tier L).

## Method (independent code, own union-find; no code from the paper)
M1 build gluing from face pairings; verify each face glued once, orientation consistency, vertex classes, vertex link Euler characteristic and connectedness, edge classes and degrees, compare with the paper's table (2).
M2 pi1: presentation from edge-generators/face relations by my own derivation from the dual 2-complex is replaced by the equivalent one-vertex presentation with edge generators and a relation per face (as in the paper's method, but derived by my own code), plus an independent route: dual 2-complex with spanning tree (Reidemeister). Simplify with GAP (/usr/bin/gap): order, abelian invariants, IsTrivial of the loop edge a. Cross-check with Regina (pip, venv outside repo): fundamental group, homology, isomorphism signature, isLensSpace-type recognition (Regina census recognition), and whether the edge a is null-homotopic.
M3 matching equations: build Haken's full matching equations (4 triangle + 3 quad coords per tet) directly from the face gluing arcs, project onto quad coordinates, compute the kernel / projection space with exact rational arithmetic (sympy), compare with the paper's W; find ALL vectors in the projected solution space (and in the kernel of W) with <=2 nonzero entries by exhaustive support enumeration (all supports of size 1,2); also the nonnegative version.
M4 Thurston: edge equations built from my own edge classes, in both orientation conventions; decide solvability exactly (sympy resultant/Groebner over Q in z,w with extra variable t for z(1-z)w(1-w)t-1 to encode non-degeneracy); also with edge products +-1 (generalized) and report solutions.
M5 SAS(T): numeric maximization of volume over the circle-valued angle structure space (finite union of tori from the integer constraints), report maxima and whether any u(q) in {1,-1}. Floating point, Tier C-numeric; not a proof of (iv).

## Controls
Positive: (P-a) figure-eight knot complement 2-tet triangulation (Regina/SnapPy cPcbbbiht_12): gluing eqs solved at z=w=e^{i pi/3}; code of M4 must find that solution; (P-b) the one-tetrahedron-free standard triangulations from Regina: S^3 (e.g. 2-tet) and L(3,1) built by Regina's own generator: my pi1/H1 code gives trivial / Z3; (P-c) Regina's own isomorphism signature for the paper's triangulation; my Q-matching on a Regina-built triangulation matches Regina's normal-surface quad kernel dimension.
Negative: (N-a) change one face pairing (replace perm of A(013)->B(321) by a different permutation, or swap a pairing); the validity / pi1 / edge-class / W results must change and the check "pi1=Z3 and degrees 2,5,5" must fail (record what changes). (N-b) perturb the exponent matrix (one entry of I): the solver must then find a solution or report change; the kernel check must give a different answer.
Success of a control = expected result; if a control fails the headline is not reported.

## Outcome rules
CONFIRMED: M1 valid closed orientable 1-vertex triangulation, pi1=Z/3 with a null-homotopic, vertex-to-vertex loop edge, W equals the paper's (up to ordering conventions, which I will state), <=2-support kernel vectors only (1,0,0,1,0,0) multiples, Thurston system unsolvable, controls pass. Numeric M5 consistent => CONFIRMED with scope caveat for (iv) and C5.
PARTIAL: any listed clause disagrees in detail but the main conclusions hold (e.g. a typo in a table), or M5 inconclusive.
NOT CONFIRMED: a main clause fails (e.g. a solution to Thurston's equation exists, or another <=2-support kernel vector exists). BLOCKED: tools unavailable.
Tiers: C (exact computation) for M1-M4; M5 numeric C-numeric; L for Luo's theorems, JRT minimality, and the logical reduction (C5). No Lean (A) claimed.
Not checked: Luo's theorems; that 2 is the minimum for L(3,1); the Futer-Gueritaud reduction; that the notion of cluster in Luo requires nonnegative normal solutions (the paper drops it; I check both).
