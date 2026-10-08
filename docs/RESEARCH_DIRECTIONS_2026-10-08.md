# Research directions after the openai/math crosswalk and pilot P1 (2026-10-08)

Inputs: `docs/OPENAI_MATH_CROSSWALK_2026-10-08.md` (what openai/math can and cannot do for this programme),
pilot P1 (`results/certified_numerics/P1_bao/`, kernel-checked BAO distance enclosures, verdict P1_OK), the matrix
Lieb-Thirring lab (doi:10.5281/zenodo.23245266) and the Comparator results (LT_CMP, TRI_CMP).

The common thread is **certified numerics**: let the fast solvers (rusty-SUNDIALS, Python) compute, and have Lean's
kernel check a short integer certificate that turns their output into a theorem. P1 shows that this works end to end
on this server in minutes of compute. Ordered by value per effort; each item has a first step and a stop rule.

## R1. Certified cosmology, from distances to likelihoods (extends P1)

| Step | Goal | First step | Success criterion | Effort |
|---|---|---|---|---|
| P2 | Certified D_V/r_d (BGS bin) and a certified DESI DR2 χ² interval at the fit point | integer cube-root bounds for D_V by monotonicity; rational interval arithmetic for rᵀC⁻¹r with C⁻¹ exact over ℚ | χ² enclosure contains the Rust value 10.2710 and has width ≤ 0.05 | 1-2 days |
| P2b | **Certified exclusion of Einstein-de Sitter by DESI DR2** | reuse P2 with Om = 1 | kernel-checked χ²(EdS, best h·r_d range) > 1000 (Rust: 11089) | +0.5 day |
| P3 | Second-order enclosures (width ~1e-8) | convexity of 1/E on [0, z_max] or Mathlib `trapezoidal_error_le`; midpoint lower / trapezoid upper | widths below CVODE's measured 7e-7 error, so the certificate grades the solver at its own tolerance | 2-3 days |
| P4 | Extended models: wCDM, w0waCDM (DESI's evolving dark energy), radiation on | generalise `E`; monotonicity can fail for some (w0, wa), so use cell-wise interval bounds of 1/E | certified D_M/r_d for the DESI DR2 w0wa best fit | 3-5 days |

Why it matters: certified statements are robust against solver bugs of the kind already found in this programme
(the CVODE tight-tolerance Nordsieck bug, Adams stuck at order 1). P2b would be a small but clean "kernel-checked
cosmology" result suitable for a short paper.

## R2. Verified integrator theory for rusty-SUNDIALS (Mathlib only)

- Replace the vacuous / bug-certifying axioms in `proofs/lean4` (`bdf_astability_orders_1_2 : … → True`,
  `rescale_interpolation_exact`) with theorems: BDF1-5 order conditions and zero-stability (root condition), failure at
  BDF6; Nordsieck rescaling exactness; the Adams l/tq tables of PR #63.
- Put `proofs/lean4` under a real lakefile and CI (today CI checks one file).
- Stop rule: if a coefficient table in Rust disagrees with the proved one, that is a solver bug report, not a proof fix.
- Effort: 3-5 days. Work in a rusty-SUNDIALS worktree off origin/main (the main checkout is on another session's branch).

## R3. Certified ODE solutions (beyond quadrature)

- Validated Taylor stepping in Lean, following openai/math's Transonic pattern (integer boxes, a soundness lemma per
  step), for a genuinely nonlinear ODE with a known invariant: the ITER 0-D current quench (two coupled L-R loops) where
  the exact energy identity W_mag(0) − W_mag(t) = Q_p + Q_v is also provable in Lean.
- First step: prove the energy identity and dissipativity (det = L_p L_v − M² > 0) in Lean; then a fixed-step validated
  Taylor enclosure over a short window, compared with rusty-SUNDIALS output.
- Effort: 1-2 weeks. Risk: the stiffness of the problem forces many small steps; start with the non-stiff window.

## R4. Statement-fidelity audit of the Comparator-accepted theorems (highest scientific stakes)

- The Comparator accepted upstream's scalar sharp Lieb-Thirring theorem (one-bound-state constant for 1/2 < γ < 3/2)
  and the triangular-lattice universal-optimality theorem. If the Lean statements are faithful, these are major results;
  if they are not, the acceptance means little. The audit is a human-expert task that tools can only support.
- Support we can provide: a fidelity checklist per statement (domains, function spaces, extended-real conventions,
  definition of the negative moment, quantifier order), Elenchus vacuity scans, and small sanity theorems derived from
  the statement (e.g. that it implies the classical γ ≥ 3/2 cases, known special values, monotonicity in γ).
- First step: derive in Lean, from upstream's `MainClaim`, the known γ = 3/2 Lieb-Thirring constant (a consistency check
  that would fail if the statement were vacuous or mis-scaled).
- Effort: days for the sanity theorems; the expert audit is outside this lab.

## R5. Hygiene of the existing Lean corpus (prerequisite for anything that imports it)

- Remove or quarantine the inconsistent axioms (DualScaleSimulator `BuscherRules`, rusty-SUNDIALS `psc_telemetry_oracle`
  and fusion oracles, likely `autodiff_exactness`) and the tautological runux `regularity` theorem.
- k3: replace the 55 `native_decide` by `decide +kernel` (openai/math shows this scales), then attack the recurrence
  axioms with creative-telescoping certificates checked by `ring`.
- Effort: 1-3 days for the first two bullets; the recurrences are open-ended.

## R6. Matrix Lieb-Thirring follow-up (from the published null result)

- A sharper, certified instrument: use P1-style enclosures for eigenvalue sums so that a candidate violation, if one
  appears, is certified in Lean rather than by floating-point re-evaluation; re-run the near-maximiser classification on
  all 345 near-maximisers with stored parameters; more budget for the three unconverged dual-form cells.
- Expectation: another null result is the most likely outcome; the value is the certified pipeline.

## Recommended order

1. P2 + P2b (fast, publishable, reuses everything from P1).
2. R5 hygiene (cheap, removes false foundations).
3. R2 integrator theory (directly improves rusty-SUNDIALS).
4. R4 sanity theorems for the Comparator-accepted statements.
5. P3/P4 and R3 as the longer programme.

All new work: preregister before running, positive and negative controls, kernel check with the axiom whitelist,
independent verification before any write-up, and no claim beyond what was checked.
