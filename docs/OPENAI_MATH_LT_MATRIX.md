# Matrix-valued sharp 1D Lieb-Thirring: hypotheses, instruments, decision rules

Status: PREREGISTRATION (written before any campaign row). Selection and gap analysis:
`docs/OPENAI_MATH_SELECTION_2026-10-08.md`. Method: Elenchus Maieutics (fixed budget, immutable evaluator, mechanical
keep/discard, every row logged, results are Tier X settings). Nothing here is a proof.

## The claim under test

For 1/2 < gamma < 3/2, every Hermitian W(x) >= 0 of size m x m with int tr W^(gamma+1/2) < infinity:

    R[W] := Tr (-d^2/dx^2 (x) 1_m - W)_-^gamma / int tr W^(gamma+1/2) dx  <=  L1(gamma),

L1 = Lean `sharpConstant` = 2 ((g - 1/2)/(g + 1/2))^(g - 1/2) * Gamma(g + 1) / (2 sqrt(pi) Gamma(g + 3/2)), equality iff W
is, in one constant unitary basis, a direct sum of scalar potentials (r+1) sech^2(r(x - c)) with independent scales and
centres, plus zero channels (upstream manuscripts of 2026-10-05; not in the Lean formalisation).

## Instruments (frozen before the campaign; sha256 in `preregistration.json`)

* `scripts/openai_math/lt_matrix/instrument.py`: Dirichlet box [-L, L], sine-basis Rayleigh-Ritz. Both choices make every
  computed |E_j|^gamma a lower bound on the whole-line value for the same W (domain monotonicity; Rayleigh-Ritz), so the
  numerator is a rigorous lower bound up to exact matrix elements. Quadrature of matrix elements and of the denominator
  is Gauss-Legendre and is re-checked on a doubled grid.
* `scripts/openai_math/lt_matrix/controls.py`: C1 exact equality potential reproduces L1 (one bound state at E = -1);
  C2 constant-unitary invariance for m = 2, 3; C3 additivity of decoupled channels; C4 scalar search reaches L1 and does not
  exceed it; C6 gamma = 3/2 (Laptev-Weidl, proved) is not exceeded by the matrix search; C5 and C7 NEGATIVE controls: at
  gamma = 3 the one-bound-state constant is not the supremum, so the search must exceed it for m = 1 and m = 2.
* `scripts/openai_math/lt_matrix/campaign.py`: one lane = one (gamma, m, family) cell, families random / embed /
  rotpair / twist; refinement of every candidate with excess > 1e-7: grid doubled (M and Q), and an independent
  finite-difference solver with Richardson extrapolation (agreement with the Galerkin value measured at about 1e-6, so
  the cross-check can confirm an excess of about 5e-6 or more).

## Verdict rule (mechanical, interval style, abstaining)

Let excess = R_lower_bound / L1 - 1 on the stored parameters of a candidate.

| Condition | Verdict |
|---|---|
| any control failed | VOID (no numbers count) |
| refined-grid excess > 1e-5 AND finite-difference excess > 5e-6 | VIOLATION_CERTIFIED (Tier X; then re-check by an exact-arithmetic or interval evaluation of the explicit potential) |
| 1e-7 < refined-grid excess <= 1e-5, or the two solvers disagree | UNDECIDED (reported as such, not as a pass) |
| every restart excess <= 1e-7 | NO_VIOLATION_FOUND (not a proof; the search has finite power, stated with the budget) |

## Hypotheses

| # | Statement | Prediction | Kill criterion | Evidence kind |
|---|---|---|---|---|
| H-LT1 | sup R over m = 2 and m = 3 matrix potentials is <= L1(gamma) for gamma in {0.75, 1.0, 1.25, 1.4} | NO_VIOLATION_FOUND in every cell | VIOLATION_CERTIFIED in any cell with all controls passing | numeric (Tier X) |
| H-LT2 | near-maximisers (R >= (1 - 1e-3) L1) are, up to a constant unitary, direct sums of scalar sech^2 solitons and zero channels | commutator statistic C = max over x, y in the support of ||[W(x), W(y)]|| / (||W(x)|| ||W(y)||) is < 0.01 for every near-maximiser | a near-maximiser with R >= (1 - 1e-4) L1 and C > 0.05 | numeric (Tier X) |
| H-LT3 | the embedded scalar extremiser W* = diag(W_ext, 0) is a local maximum of R in matrix directions (second variation <= 0) | all feasible second variations <= noise | a direction with positive second variation beyond numerical noise, confirmed by full evaluation at finite epsilon | numeric (Tier X) |
| H-LT4 | instrument validity: negative controls C5, C7 exceed L1 at gamma = 3; positive controls C1-C4, C6 pass | all pass | any control failing voids the cell | numeric (Tier X) |
| H-LT5 | dual kinetic form at gamma = 1: for orthonormal families (psi_j), j = 1..N, in L^2(R; C^m), Sum ||psi_j'||^2 >= (pi^2/4) int tr rho^3 dx, rho(x) = Sum psi_j psi_j^dagger | explicit test functions never go below pi^2/4 (the m = 1, N = 1 case is attained by c sech^(1/2)(x)) | an explicit orthonormal family with quotient < pi^2/4 (1 - 1e-6) after exact re-evaluation | numeric (Tier X); a hit is a certified explicit counterexample |

**Derivation of H-LT5 from the matrix claim at gamma = 1 (classical, Tier L).** By Ky Fan, for orthonormal psi_j and any
W >= 0, Tr(-d^2 - W)_- >= int tr(W rho) - Sum ||psi_j'||^2, so the claim gives Sum ||psi_j'||^2 >= int tr(W rho) - L1 int tr
W^(3/2) for every W >= 0. Maximising pointwise over W (per eigenvalue: w = (2 rho_i / (3 L1))^2) gives the constant
4/(27 L1^2). With L1(1) = 0.245035... this equals pi^2/4 to the printed precision, which is the sharp one-state
Gagliardo-Nirenberg constant ||u'||^2 >= (pi^2/4) int u^6 for ||u||_2 = 1. So a violation of H-LT5 refutes the matrix
claim at gamma = 1 and, unlike the spectral search, is witnessed by an explicit finite family of functions.

## Lanes (workflow `night_lab_workflow.js` v2: each lane preregisters in detail, commits, runs, is verified)

* A: spectral search, m = 2, gamma in {0.75, 1.0, 1.25, 1.4}, all four families.
* B: spectral search, m = 3 (gamma = 1.0, 1.25), the gamma = 3/2 control, and the second-variation test H-LT3.
* C: kinetic dual H-LT5 (m = 1, 2, 3; N = 1..4) and the structure test H-LT2 on the near-maximisers of A and B.
* D (no compute): vacuity/smuggling and statement-lock pass over the upstream Lean statements; Comparator request to the user.
