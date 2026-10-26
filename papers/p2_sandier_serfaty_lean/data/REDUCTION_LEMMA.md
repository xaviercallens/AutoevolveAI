# A1b: one complete lemma of the analytic reduction in Lean, and what remains

Date 2026-10-26. Proposal 2, item A1b (preregistration `results/proposal2/2026-10-26/preregistration.json`, prior 0.35).
Subject: the openai/math manuscript "Triangular minimality for planar Coulomb renormalized energy" (2026-09-23; AI-generated, not
peer reviewed), `build/sections/03-geometry.tex` SHA-256 `1b8446c6849e...` (P1 REDUCTION_AUDIT §0).

## Result

**`ProgSandierSerfaty.Reduction.signed_endpoints`** is the manuscript's Lemma `dual:signed-endpoints` (03-geometry.tex lines 567-611),
complete and kernel-checked (`formal_cert/Programmes/SandierSerfaty/SignedEndpoints.lean`, pinned Lean 4.34.1 + Mathlib d13f23b7,
`logs/compile_SignedEndpoints.json`, rc 0).

Statement (Lean, verbatim hypotheses):

```lean
theorem signed_endpoints (G : ℝ → ℝ → ℝ) (K d₀ : ℝ) (hK : K < 0) (hd₀ : 0 < d₀)
    (heven : ∀ d, d₀ ≤ d → ∀ s, G d (-s) = G d s)
    (hint : ∀ d, d₀ ≤ d → ∀ a b : ℝ, IntervalIntegrable (G d) volume a b)
    (hpos : ∀ d, d₀ ≤ d → ∀ x, 0 ≤ x → K ≤ 2 * gPrim G d x)
    (hneg : ∀ d, d₀ ≤ d → ∫⁻ s in Ioi 0, ENNReal.ofReal (-G d s) ≤ ENNReal.ofReal (-K)) :
    ∀ d, d₀ ≤ d → ∀ α β : ℝ, |α| < π / 2 → |β| < π / 2 → 0 < α + β →
      K ≤ gPrim G d (d * Real.tan α) + gPrim G d (d * Real.tan β)
```

with `gPrim G d x = ∫ s in 0..x, G d s` (the manuscript's `g_d`).

Fidelity to the TeX, item by item:

| TeX | Lean |
|---|---|
| `K<0`, `d_0>0` | `hK`, `hd₀` |
| `G(d,·)` even, locally integrable, for `d ≥ d_0` | `heven`; `hint` (interval integrable on every bounded interval, equivalent to local integrability on ℝ) |
| `g_d(x)=∫_0^x G(d,s) ds` | `gPrim` |
| `2g_d(x) ≥ K (x ≥ 0)` | `hpos` |
| `∫_0^∞ max{0,−G(d,s)} ds ≤ −K` | `hneg`, as a `lintegral` of `ofReal(−G) = ofReal(max{0,−G})`, valued in `[0,∞]`: no integrability side condition, and an infinite integral violates the hypothesis instead of producing Bochner's junk value 0 |
| conclusion for `\|α\|,\|β\|<π/2`, `α+β>0` | conclusion, same quantifiers |

The proof follows the TeX: oddness of `g_d` from evenness (`gPrim_neg`, by `integral_comp_neg`); the case `α, β ≥ 0` from `hpos`; the
mixed case `α < 0 < β` via `u = −d tan α < v = d tan β` (strict monotonicity of `tan`), `g(v) − g(u) = ∫_u^v G ≥ −∫_u^v G⁻ ≥ K`
(`integral_ge_of_negPart`); the case `β < 0` by symmetry.

Two further pieces, smaller:

* **`assembly_algebra`**: the final algebraic step of Proposition `dual:assembly` (compatible tori): sector bounds
  `J(S) ≥ K + λA(S) + μθ(S)` over a finite family with `ΣA = N`, `Σθ = 2πN`, at most `6N` members and `K ≤ 0` give
  `ΣJ ≥ N(6K + λ + 2πμ)`. The geometric inputs (Voronoi sectors, the dual identity `W_T(h) = ΣJ + ½∫|∇(h−H)|²`) are hypotheses,
  so this is a step of the proposition, not the proposition.
* **`b_lt_dstar`**: `0.28209 < 1/(2√π)` (Section 7, the certificate's lower edge distance is below `d_*`), from Mathlib's
  `Real.pi_lt_d6`.

`#print axioms` (verbatim, `logs/compile_Axioms.json`):

```
'ProgSandierSerfaty.Reduction.gPrim_neg' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgSandierSerfaty.Reduction.integral_ge_of_negPart' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgSandierSerfaty.Reduction.signed_endpoints' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgSandierSerfaty.Reduction.assembly_algebra' depends on axioms: [propext, Classical.choice, Quot.sound]
'ProgSandierSerfaty.Reduction.b_lt_dstar' depends on axioms: [propext, Classical.choice, Quot.sound]
```

### Controls (`formal_cert/Programmes/SandierSerfaty/Controls.lean`, rc 0, `logs/compile_Controls.json`)

* **Hypothesis `α + β > 0` is load-bearing** (`ctl_signed_without_sum_false`, axioms `[propext, Classical.choice, Quot.sound]`): for
  `G ≡ 1`, `K = −1`, `d = 1`, `α = β = −π/4` the conclusion fails (`g(tan α) + g(tan β) = −2 < −1`).
* **Non-vacuity** (`ctl_signed_hyps`): the same `G ≡ 1` satisfies every other hypothesis (`heven`, `hint`, `hpos`, `hneg` with
  `K = −1`), so the theorem genuinely applies to it.
* Planted cheats `ctl_sorry_pi` / `ctl_axiom_pi` (for the A1a side) show `sorryAx` and `ProgSandierSerfaty.Cert.Controls.ctl_cheat` in
  `#print axioms`, i.e. the axiom gate catches them; the same audit gives the whitelist only for the genuine theorems above.

### Relation to `SandierSerfatyStatement.lean` and to A1a

The lemma is stated, as in the manuscript, for an abstract kernel `G(d,s)`; it uses no definition of `SandierSerfatyStatement.lean`
(electric fields, `W`, cutoffs), and forcing an import would add nothing. The concrete `G` of the manuscript is
`G(d,s) = (d/t²)(f₀(t) − λt²/2 − μ) − (s²/(d t²)) e(t)`, `t = √(d²+s²)` (`grids.hpp: G`), built from the radial functions `f₀, e` of
Section 4, which are not defined in Lean yet. The two hypotheses `hpos`, `hneg` are exactly what the certificate's `global_grid`
stage (outer assertion and negative-part assertion, plus the exterior formula of Theorem `comp:scalar`) is meant to certify; joining
the two needs a Lean definition of `f₀, e` and the L2 (real-semantics) version of `global_grid` (CERTIFICATE_PORT.md).
The only part of A1 stated against the statement file's definitions is the constant bridge `Bridge.lean`:
`tri_eq_triScale : tri = ProgSandierSerfaty.triScale` (rfl), `a_mem_triScale : aC.Contains triScale`,
`p_mem_triScale : pC.Contains (triScale / 2)` (axioms `[propext, Classical.choice, Quot.sound]`).

## What remains of the reduction (Sections 2-5), with the Mathlib situation

P1's audit lists 31 steps (R1-R10, G1-G7, K1-K8, T1-T6). Formalized now: G6 complete; the algebraic step of G7; the numeric fact
`b < d_*` of Section 7. Everything else remains:

| Block | Steps | What Lean/Mathlib lacks (estimate) |
|---|---|---|
| Section 2, square tori to the plane | R1-R10 | Weak div/curl equations with point charges and their local regularity (Weyl's lemma in this form); the cited SS2012 Theorem 1(1),(3),(4), Lemma 4.7, Proposition 4.9 (mass displacement), each a substantial paper-level result with no Mathlib counterpart. This block alone is a multi-month project. |
| Section 3, torus minimizers, separation, Voronoi sectors, dual identity | G1-G5, G7 (geometric part) | Torus Green function (absent; the statement file already notes this); strong minimum principle for `W^{2,2}` supersolutions; Voronoi tessellation of a periodic point set and Euler's formula on the torus (Mathlib has neither); Green's identities on punctured domains. |
| Section 4, calibration | K1-K8 | Mathlib now has the Weierstrass ℘ function (`Mathlib/Analysis/SpecialFunctions/Elliptic/Weierstrass.lean`) and Eisenstein series, a starting point for the Green-function expansion K1; the explicit radial data (`B`, `D_m`, `S`, `P`, `Q`, `τ`, edge polynomials) and the primitive / stationarity identities K4-K7 are elementary but long (Leibniz, integration by parts on concrete splines). Weeks to months. |
| Section 5, tails | T1-T6 | Elementary real analysis (geometric/ratio tails, Leibniz bounds); P1 already checked every constant in exact rationals; formalization is long but routine (weeks). |

No claim is made that the Sandier-Serfaty conjecture, or any part of the reduction other than the three items above, is formally proved.
