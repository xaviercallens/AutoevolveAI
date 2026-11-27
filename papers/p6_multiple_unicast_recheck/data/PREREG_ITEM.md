# PREREG AIC-MUC9: independent exact RECHECK of arXiv 2610.10108 (Braverman, He)

Status: recheck of a claim by others. No novelty claim. Written before any computation on the construction.

## Source pinned (read in full via alphaXiv, 2026-11-02)
Section 4 (deterministic causal code). Note: the causal code of Section 4 is deterministic; the "non-deterministic"
construction (Section 3, 166 deleted edges, 744 edges) is a different, earlier example on the same graph. The plan item is Section 4.
- Conjecture (Li-Li 2004 / Harvey-Kleinberg-Lehman): in undirected networks with edge capacities, network coding throughput = fractional multicommodity flow throughput.
- Graph: F9 = F3[theta]/(theta^2+1); T = 91 normalized triples ordered v0=(0,0,1), v_{1+r}=(0,1,eta_r), v_{10+9r+s}=(1,eta_r,eta_s), eta_r=(r mod 3)+floor(r/3)theta. Point P_p, line L_l, edge iff p.l=0. Vertex labels: P_i = i, L_j = 91+j. Candidate edge e_{10i+r}={i, 91+j_{i,r}}, neighbours increasing. Delete R (175 indices, Appendix A). G has 735 edges.
- Order pi (182 vertices, Appendix A), C and J (9 each), B=R\(C u J), |B|=157. Physical edges oriented earlier->later in pi, deleted edges later->earlier. Claimed: d-(v)=d+(v)=5 and d+_C(v)=d-_J(v) at every vertex.
- Local rule: at vertex z, basis u,w = first two triples of T cap z-perp (in T order), neighbour y = lambda u + mu w (no renormalisation); point vertex: values Q(lambda,mu)=sum a_r lambda^{4-r} mu^r; line vertex: Q(lambda^3,mu^3).
- Code: C-edges carry public 0; each vertex interpolates the 5 known incident values and emits the rest. Claimed dim W >= 166, W_C dim >= 157, B-restriction injective.
- Claimed: sources x_q (q in B) at the earlier endpoint, recovered at the later endpoint; dist(s_q,t_q) >= 5; 735 < 785 so routing rate <= 735/785 = 147/157.

## Questions / checks (all with my own code; the authors' repo/verifier is NOT run)
A1 GF(9) tables exact (field axioms, x^2+1 irreducible, order-8 cyclic group). A2 T ordering: 91 normalized, distinct.
A3 |V|=182, 10-regular, |E|=910, no 4-cycle, any two points share exactly one line. A4 |R|=175 distinct valid indices in [0,909], |C|=|J|=9, C,J subset R, disjoint, |B|=157; pi is a permutation of 0..181.
A5 After deletion: |E|=735; orientation degree conditions d-=d+=5 and d+_C=d-_J at every vertex (full-candidate-graph degrees, as stated).
A6 Local codes: every vertex's 10 values admit a 5-dim code (rank 5 of the 10x... evaluation map); any 5 incident positions are independent (MDS).
A7 Rank: dim W computed exactly by Gaussian elimination over F9 on the 910-variable local-constraint system, expected >= 166; dim W_C >= 157; restriction of W_C to B injective (and bijective if dim = 157).
A8 Causal run: for N random input tuples in F9^157, run the pi-ordered interpolation; check (i) at each vertex the number of known values is 5 and the 5 knowns are independent; (ii) the produced assignment lies in W (all 182 local codes satisfied); (iii) each sink t_q outputs x_q.
A9 dist(s_q,t_q) >= 5 for all 157 pairs (BFS in G); report min and distribution.
A10 Arithmetic: 735 < 157*5 = 785; 735/785 = 147/157 exactly. Report sum of dist (>= 785; actual value).
A11 Flow: solve the undirected unit-capacity max concurrent flow LP (157 commodities, symmetric cost) with HiGHS; compare the optimum to 147/157 (upper bound), and certify the bound by an exact rational dual/length-function argument (distance-metric dual: sum_e c_e l_e = 735 with all l_e=1, sum d_i dist = sum dist >= 785).
   Tier note: A11 LP optimum is X (floating) unless an exact rational dual is checked; the 147/157 bound itself is C (rational arithmetic + BFS).

## Controls
Positive: (P1) butterfly directed network: XOR code delivers rate 1 to both sinks with coding while routing max is 1/2 ... recheck with the same F-linear solver machinery (GF(2)); (P2) undirected instance where flow LP optimum is 1 and equals a trivial routing/coding rate (e.g. 2 disjoint edges pairs / 4-cycle with two opposite pairs: LP optimum checked); (P3) the pipeline on the untampered construction.
Negative: (N1) restore one deleted edge and delete another (sizes preserved): at least one of A5/A7/A8 must fail; (N2) corrupt one field element in a vertex's rule (e.g. wrong basis or wrong output value) must make decoding fail for some trial; (N3) wrong theta^2 relation (x^2+x+1 reducible over F3? use x^2 = 1 reducible) must fail A1.
Controls run and reported before the headline.

## Kill criterion
Any of: |E|!=910 or 735, a 4-cycle, d- != 5 or d+ != 5, rank insufficient (dim W_C < 157), a decoding failure in any random trial of the untampered run, any dist < 5, or flow LP optimum > 147/157 + 1e-9 (which would contradict the stated bound derivation). Then outcome = NOT CONFIRMED (report which). A transcription ambiguity in R or pi (cannot be pinned) = BLOCKED/PARTIAL, not NOT CONFIRMED, unless the controls show the same list works identically.
Outcome rule: CONFIRMED only if A1-A10 all pass and controls behave; A11 reported separately.

## Tiers
C: exact finite field/graph computations (A1-A10, rational arithmetic). X: random-input simulation (A8 sampling; the exact-linearity argument makes it complete modulo trials), HiGHS LP floating optimum (A11). L: that the example refutes the Li-Li conjecture in the intended capacity model, the pipelining argument (R_code >= 1), the amplification theorem (BGS17), Omega((log n)^eps): literature, not verified.

## Not done
The authors' accompanying verifier/simulator not run (third party, licence unchecked). The non-deterministic Section-3 construction (166/744/830) is out of scope except where it shares the graph. Paper claim of PG(2,9) minus edges 'bipartite subgraph' accepted as stated. Resources: taskset -c 1,2, ~3 core-hours cap.
