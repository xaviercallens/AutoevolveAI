# A2(d) Second fidelity audit: Clay statement vs. Lean statement

Written by the A2 agent **before** reading `results/autoresearch/2026-10-25/H9/AUDIT.md`.
The comparison with H9 is in the final section, which was added after this table was written.

## Sources

- **Clay statement.** C. L. Fefferman, "Existence and smoothness of the Navier–Stokes equation".
  - Downloaded 2026-10-26 by `curl` from `https://www.claymath.org/wp-content/uploads/2022/06/navierstokes.pdf`.
  - sha256 `c1b5f27b1a64705cfaf1afceea513db5deedca8a18ca56ab32e7f86445a06d0c`. PDF CreationDate 2006-08-04, ModDate 2013-02-05.
  - Text extracted with `pdftotext -layout` to `/home/callensxavier_gmail_com/proposal2/A2/clay_navierstokes.txt`. The PDF's text includes an "Errata" block.
- **Lean statement.**
  - `ComparatorChallenges/NavierStokes.lean`: the reference, adapted from Formal Conjectures at commit 8bf45ed7.
  - `NavierStokes/ComparatorDefinitions.lean`: the definitions that the proved theorem is actually stated over.
  - `NavierStokes/ComparatorSolution.lean`: the proved theorems.
  - All three come from corpus HEAD f9e8bc5b.
- **Do the two definition files agree?** Yes, as text. `ComparatorDefinitions.lean` is code-identical to the reference once comments and whitespace are dropped and the two `sorry` theorems are removed (`scripts/code_diff.py`).
  - The elaborated-term comparison, which checks what Lean actually built, is reported in AXIOMS.md §"Statement identity". Result: identical up to alpha-renaming.
- **Semantics probes.** `audit/Semantics.lean` and `audit/Semantics2.lean` were compiled against the reused Mathlib 85e3a25e.
  - `∞` under `open ContDiff` elaborates to `WithTop.some (⊤ : ℕ∞)`, which is C^∞ and **not** the analytic `ω`. `(∞ : WithTop ℕ∞) ≠ ω` checked by `decide`.
  - `Δ` on `ℝ³ → ℝ³` is `instLaplacian`. It equals `∑ i, D²w(x)[eᵢ, eᵢ]`, the componentwise vector Laplacian, proved by `laplacian_eq_iteratedFDeriv_orthonormalBasis`.
  - `gradient p x = (toDual ℝ ℝ³).symm (fderiv ℝ p x)`, the Riesz/Euclidean gradient.
  - The norm on `ℝ³ × ℝ` is `max ‖x‖ ‖t‖` (checked by `rfl`).

## (C) Breakdown on ℝ³: `NavierStokes.Comparator.navier_stokes_breakdown_R3`

| Clay (C) ingredient | Lean | Verdict |
|---|---|---|
| "Take ν > 0 and n = 3" | `∀ nu, nu > 0 → …`, with types `ℝ³ = EuclideanSpace ℝ (Fin 3)` | match (the data may depend on ν, as in Clay) |
| ∃ smooth u° on ℝ³ | `∃ u₀`, `InitialVelocityCondition.smooth : ContDiff ℝ ∞ u₀` (∞ = C^∞) | match |
| u° divergence-free | `div_free : ∀ x, ∇⬝ u₀ x = 0`, with ∇⬝ = trace of `fderiv` | match (u₀ is smooth, so no junk value) |
| (4) \|∂ₓ^α u°(x)\| ≤ C_{αK}(1+\|x\|)^{-K} for every α, K | `∀ m : ℕ, ∀ K : ℝ, ∃ C, ∀ x, ‖iteratedFDeriv ℝ m u₀ x‖ ≤ C/(1+‖x‖)^K` | match. The full m-th derivative tensor bounds every \|α\| = m partial and vice versa, up to constants. K ranges over all reals, which is harmless because K ≤ 0 follows from K = 0. |
| ∃ smooth f on ℝ³ × [0,∞) | `ForceCondition.smooth : ContDiffOn ℝ ∞ ↿f (univ ×ˢ Ici 0)` | match (C^∞ up to the boundary t = 0 in Mathlib's `ContDiffOn` sense) |
| (5) \|∂ₓ^α ∂ₜ^m f\| ≤ C(1+\|x\|+t)^{-K} on ℝ³ × [0,∞) | `∀ m K, ∃ C, ∀ x, ∀ t ≥ 0, ‖iteratedFDerivWithin ℝ m ↿f (univ ×ˢ Ici 0) (x,t)‖ ≤ C/(1+‖x‖+t)^K` | match (joint space–time jets within the half-space; the sup product norm is equivalent) |
| "no solutions (p,u) of (1),(2),(3),(6),(7) on ℝ³×[0,∞)" | `¬ ∃ v p, NavierStokesExistenceAndSmoothnessRn nu u₀ f v p` | match, field by field below |
| (1) ∂ₜu + (u·∇)u = νΔu − ∇p + f, for x ∈ ℝ³, t ≥ 0 | `∀ x, ∀ t ≥ 0, derivWithin (v x ·) (Ici 0) t + fderiv ℝ (v · t) x (v x t) = nu • Δ (v · t) x − gradient (p · t) x + f x t` | match. `fderiv(v·t) x (v x t) = Σⱼ vⱼ ∂ⱼ v`. The time derivative is one-sided at t = 0 and agrees with ∂ₜ for t > 0 for the required C^∞ fields. |
| (2) div u = 0 for t ≥ 0 | `div_free : ∀ x, ∀ t ≥ 0, ∇⬝ (v · t) x = 0` | match |
| (3) u(x,0) = u°(x) | `initial_condition : ∀ x, v x 0 = u₀ x` | match |
| (6) p, u ∈ C^∞(ℝ³ × [0,∞)) | `velocity_smooth`, `pressure_smooth : ContDiffOn ℝ ∞ ↿· (univ ×ˢ Ici 0)` | match |
| (7) ∫\|u(x,t)\|² dx < C for all t ≥ 0 | `integrable : ∀ t ≥ 0, MemLp ‖v · t‖ 2` **and** `globally_bounded_energy : ∃ E, ∀ t ≥ 0, ∫ ‖v x t‖² < E` | match. Clay's (7) forces u(·,t) ∈ L² (otherwise the integral is +∞). The `MemLp` conjunct only removes Mathlib's junk value 0 for non-integrable Bochner integrals, so the conjunction is equivalent to (7). |
| the solution class is not further restricted | no additional fields | match: nothing extra is demanded of a solution that would make nonexistence easier |

Notes on (C):
- The witness uses zero initial data and a nonzero force (`ComparatorR3Theorem.lean`: `refine ⟨fun _ => 0, toComparator (rescaledForce ν f), …⟩`). Clay's (C) explicitly allows a force satisfying (5), so this is admissible. Zero data is smooth, divergence-free and satisfies (4).
- Clay's alternative (A) takes f ≡ 0. (C) is the negation of (A) only under that convention, but the official text of (C) allows f, and the Lean follows the official text.

## (D) Breakdown on ℝ³/ℤ³: `NavierStokes.Comparator.navier_stokes_breakdown_periodic`

| Clay (D) ingredient | Lean | Verdict |
|---|---|---|
| ν > 0, n = 3 | `∀ nu > 0` on ℝ³ | match |
| ∃ smooth divergence-free u° on ℝ³ | `InitialVelocityConditionPeriodic` extends `InitialVelocityCondition` (smooth, div-free) | match |
| (8) u°(x+eⱼ) = u°(x) | `isOnePeriodic : ∀ x i, u₀ (x + EuclideanSpace.single i 1) = u₀ x` | match |
| ∃ smooth f on ℝ³ × [0,∞) | `ForceCondition.smooth` (as in (C)) | match |
| (8) f(x+eⱼ,t) = f(x,t) | `isOnePeriodic : ∀ t ≥ 0, IsOnePeriodic (f · t)` | match (Clay states it on the domain t ≥ 0) |
| (9) \|∂ₓ^α ∂ₜ^m f\| ≤ C(1+\|t\|)^{-K} on ℝ³×[0,∞) | `∀ m K, ∃ C, ∀ x, ∀ t ≥ 0, ‖iteratedFDerivWithin … (x,t)‖ ≤ C/(1+t)^K` | match |
| no solutions of (1),(2),(3),(10),(11) | `¬ ∃ v p, NavierStokesExistenceAndSmoothnessPeriodic nu u₀ f v p` | see the next row |
| (1),(2),(3) | the same `NavierStokesExistenceAndSmoothness` fields as in (C) | match |
| (10) u(x,t) = u(x+eⱼ,t) on ℝ³×[0,∞) | `isOnePeriodic_velocity : ∀ t ≥ 0, IsOnePeriodic (v · t)` | match |
| (11) p, u ∈ C^∞(ℝ³×[0,∞)) | `velocity_smooth`, `pressure_smooth` | match |
| Errata: "The further condition p(x+eⱼ,t) = p(x,t) should be made explicit in Eqn (8)" | `isOnePeriodic_pressure : ∀ t ≥ 0, IsOnePeriodic (p · t)`, a field of the **solution** class | match with the errata reading (see the caveat below) |

**Caveat on (D) (interpretive, not a mismatch).**
- Requiring periodic pressure restricts the admissible solutions. That makes nonexistence a weaker claim than nonexistence without the pressure condition.
- The weakening is substantive. Without periodic pressure, a pressure p = −g(t)·x with a spatially constant flow is a classical non-uniqueness device.
- The Clay errata (in the PDF itself) asks for exactly this condition, so the Lean statement follows the official corrected statement.
- The errata attaches it to "Eqn (8)", the data assumptions, but p is an unknown of the problem. Reading it as a condition on accepted solutions, as the Lean does, is the only coherent reading.

## Euler (not a Clay prize problem)

- Fefferman notes that the questions are "also open and very important for the Euler equations (ν = 0), although the Euler equation is not on the Clay Institute's list of prize problems".
- `Euler.euler_breakdown_R3` is the (C)-type statement with ν = 0 and f ≡ 0. It keeps (4), (6) and (7) (MemLp plus the uniform energy bound) and drops the force entirely.
  - Field by field it matches equations (1) with ν = 0 and f = 0, (2), (3), (6) and (7), and the `SolutionDefinitions.lean` text is code-identical to `ComparatorChallenges/Euler.lean`.
- `Euler.exists_compact_smooth_euler_singularity` is a supplementary statement in an all-order Sobolev class on `[0,T*)`. It has no Clay counterpart, so it is reported only as a Lean statement.
  - Its BKM-type clause `∫⁻_0^{T*} ‖ω‖_∞ = ⊤` matches the Beale–Kato–Majda remark on p. 3 of the PDF in form.
  - Its solution class (`SobolevSmoothOn`, interior-time Euler law, no time regularity on p) was read but not audited against a literature source.

## Comparison with H9 (`results/autoresearch/2026-10-25/H9/AUDIT.md`, read only after the table above was written)

**Disagreements on any row of (C) or (D): none.**
- Both audits mark every element of (C) MATCH.
- Both mark (D) as matching the errata-corrected statement. Both note that periodic pressure, required in the solution class, makes the Lean (D) weaker than a reading of the main text alone.

Differences in emphasis or coverage, none of which is a disagreement:

1. **H9 caveat 4, Mathlib version: now resolved.**
   - H9 checked the semantics of `∞`/`Δ` in a Mathlib v4.32.2 copy and compiled nothing.
   - Here they were compiled against the pinned Mathlib 85e3a25e (`audit/Semantics*.lean`, rc 0):
     - `∞ = WithTop.some ⊤` (C^∞), and `∞ ≠ ω` (by `decide`);
     - `Δ w x = ∑ᵢ D²w(x)[eᵢ,eᵢ]`;
     - `gradient` is the Riesz representative of `fderiv`;
     - the product norm is the max.
2. **H9 caveat 6, whether the solution proves *this exact* statement: now resolved, without Comparator.**
   - `ComparatorDefinitions.lean` and `SolutionDefinitions.lean` are code-identical to the challenge files.
   - The elaborated statement closures (5,599 NS and 5,521 Euler constants) are identical up to alpha-renaming (AXIOMS.md). A mutated reference is detected.
3. **H9 row 2** adds an informal ν-scaling remark: ∀ν and ∃ν are equivalent by NS scaling. I did not rely on it. The Lean statement is ∀ν>0, the strong reading, so the remark is not needed.
4. **H9 row 16 / vacuity.** H9 argues informally that the class is non-empty, with v = p = 0 for zero data and force. I agree. I did not mechanise it either.
5. **Euler.** H9 did not cover Euler. My section above does; it is not a Clay statement.
6. **Upstream provenance.** H9 did not diff against formal-conjectures@8bf45ed, and neither did I. That remains open.

## Verdict (my reading, before H9)

- **(C):** I found no mismatch.
- **(D):** I found no mismatch. The periodic-pressure requirement follows the Clay errata, and the interpretive caveat above is flagged.
- **Euler:** this is not a Clay statement. The global Euler statement is the faithful ν = 0, f = 0 analogue of (C).
- **Scope.** This is a statement-fidelity reading only. "Independently rebuilt and audited" applies to the build, axiom and escape checks reported in the other A2 files, and nothing here should be read as more than that.
