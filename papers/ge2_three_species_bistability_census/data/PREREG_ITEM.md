# GE-2 PREREGISTRATION (frozen 2026-11-11 before any computation)

## Prior-art re-query (same day, alphaXiv discover_papers, "3-species bimolecular open reaction networks bistability census", papers since 2026-09-01)
Top-10 returned: Peng 2610.32739 (2 species), 2610.31550, 2610.05242 (parameter-region approximation, no census), 2610.11679, 2610.27188 (planar), 2610.06130 (planar), 2611.02523, 2610.11970, 2611.14501, 2610.18087 (NetBiF). None is a 3-species bistability census. Verdict unchanged: GO-NARROWED (see PRIOR_ART.md).

## Class
Species X,Y,Z. Complexes C = {X,Y,Z,2X,2Y,2Z,X+Y,X+Z,Y+Z} (9 nonzero, molecularity <=2). Internal reaction = directed edge alpha->beta, alpha!=beta in C (72). Network = set of m<=3 distinct edges (labelled count 1+72+2556+59640 = 62269). Plus for every species S: inflow 0->S (rate a_S) and removal S->0 (rate rho_S). Mass action: x_i' = a_i - rho_i x_i + sum_e k_e (beta_e-alpha_e)_i x^alpha_e. All parameters a_i, rho_i, k_e are positive reals (no normalisation).
Symmetry: S3 acting on species. Canonical form = lexicographic minimum of the sorted edge-index tuple over the 6 permutations. Completeness: all labelled sets enumerated, orbit sizes must sum to 62269, orbit count cross-checked by Burnside.
Control class (2 species): C2={X,Y,2X,X+Y,2Y}, 20 edges, m<=3, 1351 labelled, 681 orbits under S2 (Peng).

## Definition of BISTABLE
A network is BISTABLE iff there is a positive parameter vector with at least two distinct positive equilibria, both linearly stable (all Jacobian eigenvalues with negative real part).

## Verdict tiers (a verdict needs the stated certificate; nothing else is claimed)
- BISTABLE_CERT: rational parameters and two distinct RATIONAL positive equilibria p,q; f(p)=f(q)=0 verified by exact Fraction substitution into the polynomial field (independent of the search code); Routh-Hurwitz at p and q in exact rationals (3x3 for -J: a1>0, a3>0, a1*a2>a3; 2x2: tr<0, det>0). Because p,q are exact rationals the interval enclosures are degenerate [p,p].
- MONOSTATIONARY_JAC: all coefficients of det(-J), as a polynomial in (x,rho,k), are nonnegative (the rho_1...rho_n term gives strict positivity) => det J(m) != 0 on the positive orthant; f is quadratic so f(x)-f(y)=J((x+y)/2)(x-y); hence at most one positive equilibrium.
- MONOSTATIONARY_SIGN: sign-pattern exclusion of two equilibria from the rows rho_i(p_i-q_i)=sum_e k_e (beta-alpha)_i (p^alpha-q^alpha) for every sign vector of p-q (monomial-difference sign forced when all variables of the monomial move the same way, otherwise free); excluded when every sign vector is contradicted by some row.
- MULTISTATIONARY_CERT: exact-rational two distinct positive equilibria (as above) but no two-sink witness found.
- UNDECIDED: everything else (includes "no witness after the search budget"; this is search evidence only, never counted as absence).
Buckets (reported separately, all classified by the same pipeline): A = species support of internal edges <=2 (a species occurring in no internal reaction only has flows; reducible to <=2 species, Peng class), B = support 3 but species-interaction graph (species joined if they occur in the same reaction) disconnected, C = connected support 3 (genuinely 3-species).

## Witness search (existence)
Two equilibria p,q force a linear system in (rho,k): rho_i(p_i-q_i) = sum_e k_e (beta-alpha)_i (p^alpha-q^alpha); a_i = rho_i p_i - H_i(p) is linear in (rho,k). Sample p,q log-uniform in [1e-2,1e2]^n (half of the pairs with q=p*exp(N(0,0.5)) coordinatewise), kernel by SVD, random kernel combinations, accept rho,k,a>0 and float Hurwitz at p and q, then rationalise p,q (denominator <=1e4), exact kernel (sympy), rational combination near the float vector, exact verification. Stage 1: 2e5 pairs x 4 combinations per non-excluded network; stage 2 (only networks with an exact multistationary certificate but no two-sink witness): 1e6 pairs. Fixed seed per network id.

## Controls
Positive: pipeline on C2 must give exactly 27 BISTABLE_CERT among 681 orbits; its JAC count is reported against Peng's 245 (informational; here all rho are free). Bucket-A bistable orbits of the 3-species census must correspond to the 2-species bistable networks (Z-decoupled embeddings).
Negative: empty network; a deficiency-zero weakly reversible network (X<->Y<->Z with flows); N0056 (X->X+Y, X+Y->2X); a known monostable network (X->Y): none may be BISTABLE_CERT. A deliberately corrupted witness (p perturbed by 1/1000, or one rho changed) must fail the exact checker.

## Kill / stop criteria
Controls fail -> BLOCKED. After 5 core-hours more than 50% of orbits UNDECIDED -> stop and report PARTIAL. A prior-art re-screen finding a 3-species census -> stop. Cap 15 core-hours of CPU actually spent, cores 1-6 only, resumable jsonl logs.

## Outcome words
FOUND = at least one bucket-C network with BISTABLE_CERT; the minimal ones (no proper edge subset BISTABLE_CERT) are listed. PARTIAL = counts and certified exclusions but a residue UNDECIDED (possible missed bistables). NEGATIVE = no bucket-C bistable and every bucket-C network carries an exclusion certificate. No Lean, no audit, no paper.
