# PH-2 PREREGISTRATION (frozen before any enclosure run)

Note on ordering: the rusty-SUNDIALS comparator outputs (logs/cvode_raw.jsonl) were produced BEFORE this freeze; they are solver outputs only and carry no information about the enclosure. No enclosure code had been run.

## Problem (exact)
y1' = -(1/25) y1 + 10^4 y2 y3 ; y2' = (1/25) y1 - 10^4 y2 y3 - 3*10^7 y2^2 ; y3' = 3*10^7 y2^2 ; y(0)=(1,0,0). Constants are exact rationals (0.04 := 1/25). The Rust CVODE right-hand side uses fl(0.04) != 1/25 (relative difference about 1e-17): stated modelling difference, not corrected.

## Meaning of "enclosure"
For each output time t_k in {0.1,0.4,1,4,10,40,100,400,1000,4000,10000,40000} (reached in order; the run stops at the furthest one it can reach), a box I1 x I2 x I3 of ball intervals with: the unique solution y(t_k) of the IVP lies in it. The method works with (y2,y3) and y1 := 1 - y2 - y3 (conservation).

## Method (single file code/ph2_enclose.py, Sage 9.5 Arb ball arithmetic, 160 bits)
A-posteriori validation. Per step [t_k,t_k+h]: reference q = Taylor polynomial of degree p-1 (dyadic coefficients from midpoints of a ball recursion; any source is allowed, only the checks matter). Obligations:
- O1 invariance: the simplex {y>=0, sum=1} is positively invariant (quasi-positivity: each f_i >= 0 when y_i=0 and the others >=0) and the solution is bounded, hence global. Used only to restrict the region over which the one-sided Lipschitz constant is taken (region box intersected with [0,1]^2 for (y2,y3)) -- NOT to shrink any reported enclosure. (Written proof in RESULT.md.)
- O2 defect: D(t)=f(q(t))-q'(t) computed coefficient-wise in balls from the exact dyadic coefficients of q (degree 2p-2); bound ||P^-1 D(t)||_2 <= sum_k ||P^-1 D_k||_2 h^k on [0,h] (triangle inequality, no Horner on intervals).
- O3 one-sided Lipschitz: Jacobian J(y) is affine in y; over the box U = hull(q([0,h])) + |P| rho (rho = tube radius), the symmetric part of P^-1 J P is enclosed in ball arithmetic and nu = upper bound of its largest eigenvalue by the closed 2x2 formula (monotone in the diagonal entries and in |b|). P is chosen in floats from the eigenvectors (complex pair: Re/Im parts), converted exactly to balls, P^-1 enclosed by the ball adjugate formula.
- O4 bootstrap: with e=z-q, ||e||_P := ||P^-1 e||_2: D^+ ||e|| <= nu ||e|| + deltabar on any interval where z stays in the rho-tube. Choose rho; show eps_max=(eps_k + deltabar h) exp(max(nu,0) h) < rho strictly, so z cannot leave the tube (first-exit argument). The end bound is eps_k exp(nu h) + deltabar * int_0^h exp(nu s) ds (ball arithmetic, nu ball).
- O5 jump: next start m' = mid(q(h)) (rounded dyadic); jump q(h)-m' enclosed by ball and added to eps in the new norm.
- O6 change of basis: eps in the norm of P_{k+1}: eps' <= ||P_{k+1}^-1 P_k||_F * eps (ball Frobenius bound).
- O7 output: |y_i - q_i| <= ||row_i(P)||_2 eps (Cauchy-Schwarz) -> box; y1 interval from 1 - y2 - y3 in balls. Output times are hit exactly by truncating the step.
- Initial condition exact: eps_0 = 0.
Floats only for choosing h, P, p-coefficients' midpoints; every inequality is evaluated in balls and checked with .upper()/.lower().

## Controls (all run before the Robertson run; results recorded whatever they show)
- C+1 stiff linear y'=Ay, A=[[-1,1],[0,-10000]], y(0)=(1,1), exact solution y2=e^{-1e4 t}, y1=(1-C)e^{-t}+C e^{-1e4 t}, C=1/(1-1e4), evaluated in balls: enclosure must contain it at t in {0.1,1,10} with relative width < 1e-9 at t=10.
- C+2 logistic y'=y(1-y), y(0)=1/10 (exact y=1/(1+9e^{-t})) with w'=-2w, w(0)=1: contained at t=1,5,10.
- C-1 exact value times (1+1e-6) (and C+1 y1 at t=10) must be OUTSIDE the enclosure.
- C-2 broken method: same low order p=6 same steps, defect term deltabar set to 0: intact run must keep containment, broken run must lose containment for C+1 or C+2 (otherwise the control is reported as INCONCLUSIVE).
- C-3 CVODE runner on C+1 is NOT run (solver is Robertson-specific); instead the CVODE comparison uses the Robertson enclosure only.

## Comparison
Solver: rusty-SUNDIALS cvode crate (Rust port, repo ~/rusty-SUNDIALS commit af4886f23188baef113e47f3309d64b2bf440e47 on branch merge-mcp-temp; BDF, Newton with dense LU, analytic Jacobian, rhs as above; scalar atol only: vector atol unsupported). NO C CVODE is installed; nothing is labelled CVODE except as "Rust port". rtol in {1e-4,1e-6,1e-8,1e-10}, atol = 1e-3*rtol for all components. Normal mode, one solve through the output times in order. Doubles are converted exactly to balls (RBF(float)). Per component: true error interval E_i=|y_solver,i - y_i| from the enclosure, ratio E_i/(rtol|y_i|+atol), flag "provably exceeds" if lower(E_i) > rtol*|y_i|+atol (tolerance evaluated with upper end of |y_i| ... precisely lower(E_i) > rtol*upper|y_i|+atol), "provably within" if upper(E_i) <= rtol*lower|y_i|+atol.

## Success / kill / cap
- FOUND: enclosure reaches T>=40000 with relative width <= 1e-6 in each component at every output time. PARTIAL: reaches T>=40 but not 40000 (or width criterion only up to some T). NEGATIVE: cannot reach T=40 with relative width <=1e-6 within 4 core-hours of method work: report furthest T and width.
- Controls failing (C+1/C+2 not contained, or C-1 not rejected) -> BLOCKED, no Robertson claims.
- Cap: 10 core-hours of CPU actually spent (getrusage ledger), cores 1-6 only, resumable checkpoints (exact string states).
- Unproved assumptions are listed in RESULT.md. No Lean, no audit, no paper.
