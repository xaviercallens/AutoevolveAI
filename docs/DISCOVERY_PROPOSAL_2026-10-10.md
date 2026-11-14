# Discovery proposal: Riesz-energy optimality of the triangular lattice, kernel-checked from the openai/math universal-optimality theorem

Date 2026-10-10. Method: SocrateAI-Scientific-Elenchus (github.com/xaviercallens/SocrateAI-Scientific-Elenchus, commit c9ae8cd):
every hypothesis carries a prediction, a kill criterion, an evidence kind and a tier cap; Maieutics output is Tier X until a
gate promotes it. LeanMaster (MCP `search_theorems`) was queried for existing lattice assets.

## 1. Where the value is (from the claims already analysed)

| openai/math claim | Our status | Extension headroom |
|---|---|---|
| Triangular lattice is universally optimal: for every smooth completely monotone `g` and every locally finite density-1 configuration `C` in the plane, `latticeEnergy g ≤ energy g C` (`OAI.AtomicTriangular.universal_energy_minimum`) | Comparator-accepted on upstream's pinned stack (TRI_CMP, 140 min); statement fidelity not human-audited | Its named special cases (Riesz/Epstein, Gaussian/theta, Yukawa) are the statements physicists use (Wigner crystals, Abrikosov vortex lattices, Riesz and Coulomb gases). Optimality among *all* configurations (not only lattices) is, to our knowledge (no literature search was run), the Cohn–Kumar universal-optimality conjecture in dimension 2, proved in dimensions 8 and 24 (Cohn, Kumar, Miller, Radchenko, Viazovska 2022) |
| Sharp scalar 1D Lieb–Thirring for 1/2 < γ < 3/2 | Comparator-accepted (LT_CMP); our matrix extension: null result, doi:10.5281/zenodo.23245266 | Dual kinetic inequality (needs a variational characterisation not exposed by upstream's definition) |
| Dyadic triangular Hilbert sum | Our lower bound C* ≥ 3, doi:10.5281/zenodo.23232389 | C* = 3 conjecture: open, low probability |

## 2. Candidates, ranked by value × probability

| # | Hypothesis (Tier X until gated) | P(achieve), prior | Why that probability | Kill criterion | Evidence kind |
|---|---|---|---|---|---|
| **D1** | **For every s > 0, `t ↦ t^{-s/2}` is an `AdmissiblePotential`; hence the triangular lattice minimises the Riesz s-energy among all locally finite density-1 planar configurations (informative for s > 2; for s ≤ 2 the lattice energy is ∞)** | **~85%** | Mathlib has `Real.iter_deriv_rpow_const` (k-th derivative of `x^r` is `descPochhammer(r,k) x^{r-k}`), `ascPochhammer_eval_neg_eq_descPochhammer` and `ascPochhammer_pos`, which give exactly the sign pattern; smoothness from `contDiffAt_rpow_const_of_ne`; the rest is one application of the upstream theorem | Admissibility unprovable as stated (e.g. a smoothness-order or junk-value mismatch), or the corollary is vacuous (both sides ⊤ for every s) | Lean kernel, axiom whitelist |
| D1b | Non-vacuity and explicit form: for s > 2, `latticeEnergy (riesz s) = Σ_{(j,k)≠0} ((2/√3)(j²+jk+k²))^{-s/2} < ∞` (the Epstein zeta of the A₂ form at density 1) | ~70% | `‖triangularPoint(j,k)‖² = (2/√3)(j²+jk+k²)` is an identity; summability for σ > 1 exists in openai/math (`NumberTheory/DirichletL/LatticeSummability.summable_normForm_neg_rpow`) but must be matched to this form (sign of the cross term) and to the tsum over `{x ∈ A, x ≠ 0}` (injectivity of `triangularPoint`) | The reindexing or the summability lemma cannot be matched | Lean kernel |
| D2 | All densities: for every ρ > 0 the scaled triangular lattice ρ^{-1/2}A has density ρ and is optimal among locally finite density-ρ configurations, for every admissible g (conditional on upstream; immediate by scaling) | ~65–70% | `g(t/ρ)` is admissible when `g` is; needs a scaling lemma for `diskCount` and the `liminf` energy | The density limit does not transport cleanly under scaling | Lean kernel |
| D3 | Yukawa / screened Coulomb `g(t) = e^{-κ√t}/√t` | ~50% | Complete monotonicity of a composition with a Bernstein function needs Faà di Bruno or Bernstein's theorem, absent from Mathlib in usable form | No usable route to the sign pattern | Lean kernel |
| D4 | Scalar Lieb–Thirring ⇒ sharp 1D kinetic inequality `Σ‖ψ_j'‖² ≥ (π²/4)∫ρ³` (γ = 1) | ~35% | Upstream's negative moment is a supremum over orthonormal families of *weak eigenfunctions*; duality needs min–max over arbitrary families | Min–max not derivable from the exposed API | Lean kernel |
| D5 | Dyadic Hilbert sharp constant C* = 3 | ≤ 20% | A genuinely open extremal problem | – | – |

**Selected: D1 (with D1b as the non-vacuity check).** It is the only candidate whose achievement probability we can justify
at ≥ 80% from concrete library facts, and it is the most valuable for physics. A feasibility proof of D1 was attempted at once
(§4).

## 3. What D1 would and would not be

* **Would be:** a kernel-checked derivation, inside the pinned upstream environment, that the Riesz s-energy statement follows
  from upstream's Comparator-accepted theorem. If upstream's statement is a faithful formalisation and its proof is right, this
  certifies the planar Riesz s > 2 special case of the Cohn–Kumar universal-optimality conjecture among all locally finite configurations; it remains conditional on the unaudited upstream theorem.
* **Would not be:** an independent proof of universal optimality (that is upstream's, and AI-generated); a statement about lattice-only
  optimality (classical: Rankin, Cassels, Ennola, Diananda, Montgomery); a closed form of the minimal energy (that is D1b's Epstein zeta,
  not its evaluation).
* **Mathematically the implication is immediate** once complete monotonicity is shown; the contribution is the formal, auditable named
  corollary and the non-vacuity check, not a new idea. Tier: A for the Lean statement, conditional on upstream; the statement-fidelity
  audit of `universal_energy_minimum` (energies as `liminf` of disk averages in `[0, ∞]`, density via disk counts) is the prerequisite
  for any claim beyond that.

## 4. Feasibility check started

Done. `formal_cert/Triangular/Riesz.lean` (D1), `RieszFinite.lean` (D1b, finiteness for s > 2) and `AnyDensity.lean` (D2, every density) compile
against upstream's pinned build with whitelisted axioms only (commits 57c8a9c, 4d5a6b3, 6845de3). D1/D1b and D2 were each confirmed with corrections by an independent
verification run (separate AI-agent instances; `results/discovery/D1/verification.md`, `results/discovery/D2/verification.md`). The D2 verifier's
sharpness lemmas (`scaled_density`, `attained`) and negative control (`unscaled_false`: without the ρ⁻¹ rescaling the claim is false) were
merged into `AnyDensity.lean` as `triangular_optimal_any_density`; like D1, D2 is conditional on the unaudited upstream theorem.

## 5. Next steps if D1 passes

1. Preregister D1b and D2 with kill criteria; attempt D1b using openai/math's `LatticeSummability`.
2. Independent verification run (fresh build, axiom audit, statement reading) before any write-up.
3. Statement-fidelity checklist for `universal_energy_minimum` (the gate for any claim about the conjecture itself).
