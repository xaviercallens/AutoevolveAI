# Selecting the next hypothesis from the openai/math Lean library (2026-10-08)

Question: which claim in upstream's formalised library is the best target for an independent, falsifiable test that
could matter for mathematics and physics, using the assets already on this machine? This note records the screen,
the gap analysis, the choice and what was not chosen, so the selection can be audited.

## 1. The screen (all numbers from files on disk)

`scripts/openai_math/screen_physics_families.py` over upstream's `CONTENTS.md` and `lean/docs/`:

| Stage | Count |
|---|---|
| Families | 372 |
| With a Lean scope note (a Comparator challenge) | 235 |
| Families matching a physics keyword | 91 |
| of those, with a Lean scope note | 63 |

Shortlist by physics weight and testability on this box (8 cores, one T4, PARI, Sage, numpy/scipy/torch, mpmath, flint):

| Family | Claim | Why interesting | Why not first |
|---|---|---|---|
| 090 | triangular lattice universally optimal among all planar configurations; planar Cohn-Elkies bound sharp | Wigner crystals, Coulomb/Riesz energies | the main statements are formalised (energy minimality, Gaussian minorants, sharp planar certificate), so a numerical hunt replicates formal work; the unformalised parts (renormalised Riesz/log/jellium) are hard to test |
| 273 | entropy photon-number inequality | bosonic channel capacities | the inequality is formalised; consequences are not, but are not independently testable cheaply |
| 276 | classical capacity of generalised amplitude damping | quantum Shannon theory | explicit formula, little room beyond re-deriving it |
| 221, 234, 281 | spin-glass formulas, QAOA on SK | statistical physics | rest on heavy external hypotheses (Panchenko-Talagrand) |
| **262** | **sharp 1D Lieb-Thirring inequality, scalar (Lean) and matrix-valued with all equality cases (not in Lean)** | **kinetic-energy bounds, stability of matter, multicomponent fermions** | selected |

## 2. Gap analysis for the selected family

Family 262's CONTENTS entry lists three manuscripts. Read against the Lean statement:

| Statement | Manuscript | In Lean? |
|---|---|---|
| sharp constant for scalar W, 1/2 < gamma < 3/2, attained by (r+1) sech^2(rx) | "Sharp one-dimensional Lieb-Thirring constants" (2026-09-23) | yes (`LiebThirring.lean`, scalar `W : R -> R`) |
| same constant for arbitrary m x m matrix W >= 0, non-commuting at different points, any rank | "Sharp one-dimensional Lieb-Thirring inequalities for matrix potentials" (2026-10-05) | **no** |
| all equality cases are direct sums, in one constant unitary basis, of scalar sech^2 solitons and zero channels | "Equality cases in the sharp one-dimensional matrix Lieb-Thirring inequality" (2026-10-05) | **no** |

The scalar paper itself says "the theorem concerns scalar potentials on the line" and that its sharpness "exhibits an
equality potential without classifying all optimizers". So the matrix claim and the classification are exactly the
unformalised, un-checked part, and the family headline is stronger than the formalised statement.

Literature (WebSearch 2026-10-08, novelty status UNCHECKED beyond this): the scalar problem has a numerical
investigation (Levitt, arXiv:1206.1473, which observed convergence to the one-state profile or splitting into
separated copies), so scalar runs here are instrument checks, not results. Laptev-Weidl proved the sharp matrix-valued
inequality at gamma = 3/2. No result for matrix-valued potentials at 1/2 < gamma < 3/2 was found.

## 3. Choice and reasoning

**Selected: the matrix-valued sharp 1D Lieb-Thirring inequality (family 262, matrix and equality-case manuscripts).**

- It is outside the Lean, so a numerical test is not replicating a formal proof.
- It is cheap to attack and one-sided: the instrument gives rigorous lower bounds on the negative-eigenvalue sum (see
  `scripts/openai_math/lt_matrix/instrument.py`), so discretisation cannot manufacture a violation.
- A counterexample would be a new result; a failure to find one is independent evidence for an AI-written proof.
- Physics: Tr(-d^2 - W)_-^gamma bounds are the spectral form of kinetic-energy inequalities for fermions; at gamma = 1 the
  matrix case is the sharp kinetic-energy bound for orthonormal families of spinor-valued functions, Sum ||psi_j'||^2 >=
  (pi^2/4) int tr rho^3, with rho(x) = Sum psi_j(x) psi_j(x)^dagger (derivation in `docs/OPENAI_MATH_LT_MATRIX.md`).

Not chosen first, and why: 090 and 273 are formalised, so the decisive check there is a Comparator run, not a search.
That check needs the user's approval to build upstream's Lean project (TODO 26); a narrow version (four challenges:
`TriangularEnergy`, `AtomicGaussian`, `PlanarPacking`, `LiebThirring`) is proposed in the morning report.

## 4. Assets used, and how

| Asset | Use |
|---|---|
| Elenchus `docs/MAIEUTICS.md`, `HYPOTHESES.md` | the loop (fixed budget, immutable evaluator, mechanical keep/discard, register before running), the filing rule (prediction + kill criterion + evidence kind), results are Tier X settings not findings |
| Elenchus `tools/ledger.py` | tier-capped claim ledger for the lab's results |
| Elenchus `tools/elenchus_check.py` | vacuity and smuggling scan of the upstream Lean statements (needs a Mathlib environment; run through LeanMaster's) |
| Mensura (estimator methodology) | interval-valued verdicts that abstain: a lower bound that does not clearly exceed the constant is WITHIN_TOLERANCE or UNDECIDED, never a pass; calibration controls before the estimator is trusted. Mensura has no physical-units machinery, and none is claimed |
| LeanMaster | Lean toolchain/Mathlib environment for compiling the lab's Lean targets; `statement_lock.py` for freezing reviewed statements; tiers A/L/C |
| AutoevolveAI | preregistration commits, positive/negative control discipline (`LL.md`), night workflow, publish pipeline |
| Not used | `leanautoresearch` (a curated demo, not a real loop), `autoresearch_swarm.py` (simulated), LeanBert (does not exist here) |
