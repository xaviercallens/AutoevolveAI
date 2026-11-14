# PREREG BIO-BISTAB (written 2026-11-01 before any computation; recheck of a claim by others, no novelty claim)

Claim under recheck: arXiv 2610.32739 (Peng, 23 Oct 2026, math.DS). Pure mathematical dynamical systems; no biological or medical claim.
Class (read from the paper text): complexes X,Y,2X,X+Y,2Y; <=3 distinct directed internal edges (20 possible, alpha != beta);
model F: x' = a - rho x + H_x, y' = b - y + H_y, mass action, a,b,rho,k_j>0; model E: rho=1.
Target: two distinct positive equilibria with trace<0 and det>0. Orbits under species exchange: claimed 681 (1,10,100,570).
Claimed: 27 bistable; rational witnesses Table 2 (rho=1); 654 excluded by JAC 245, DIV 216, ROOT 179, FLUX 14.
Prior-art search (1 Nov 2026, web + alphaXiv): found Joshi-Shiu, Feliu, Tang-Xu 2008.03846, Banaji-Boros-Hofbauer, Wilhelm 2009,
2608.01116 (3-species zero-one networks); no earlier exact enumeration of this two-species <=3-edge class for two sinks found
(search is not exhaustive). Paper's own repo/verifier NOT used.

Planned computations (own code, exact Fractions/sympy):
P1 enumerate labelled sets (expect 1351) and orbits (expect 681, sizes 1/10/100/570); check the 27 Table-1 sets are in distinct orbits.
P2 for each of the 27 witnesses (Table 2 parsed from flattened PDF text; ambiguous parses resolved by testing, reported): eliminate y,
   square-free resultant, exact count of positive equilibria (Sturm), y>0 check, trace/det signs by interval arithmetic with gcd(P,T)=1.
   Expected PASS: exactly >=2 sinks (and a saddle in between).
P3 JAC and DIV sign tests (nonnegative coefficients of det DF, det K) on all 681; expected counts 245 and 216 (as the paper's order of rules).
P4 ROOT rule (stretch, my reading of the paper's description): count passing; FLUX (14 networks) NOT reproduced.
P5 independent test of the remaining networks: random log-uniform search (rho and rates) for two sinks, exact re-verification of any hit
   in rationals. Tier X. Reported as evidence only; not a proof of exclusion.
Controls: positive (i) Schloegl-type cubic in x (x'=a-x+k1 x^2 ... with 2X->3X analog is outside class; use 1-species Schloegl-like
   in the class? see RESULT) and the N0549 baseline of Sec. 4 (3 equilibria x=1/10,1/5,3/5, det 25/9,-20/9,100/9); negative: a linear / complex-balanced
   network gives exactly 1 equilibrium; scaling a witness parameter until the second sink disappears must make the exact checker report <2 sinks.
Tiers: C exact certified computation, X searches. Lean not planned (optional).
Outcome rules: CONFIRMED only if P1 gives 681 and P2 gives 27/27 two-sink witnesses and the unexplained part of the 654 is stated as not reproduced;
PARTIAL if some of P2 fail or exclusions only partly verified (the expected honest outcome); NOT CONFIRMED if a witness fails after trying all
alternative parses, or the search finds an exact two-sink in an "excluded" network.
Cores: taskset -c 2,3, ~4 core-hours cap.
