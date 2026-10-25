# H3 — Rytova–Keldysh potential is a positive Gaussian mixture (CM in t = r²)

Tiers: **C** (human proof, below; not peer reviewed, not machine-checked) + **X** (numerics, `keldysh_check.py`,
output `result_numerics.json`). No Lean this round. Attempts: 1.

## Statement
Units e²/(4πε₀ε̄), r₀ > 0. V(r) = (π/(2r₀)) [H₀(r/r₀) − Y₀(r/r₀)], and

  w(a) = (1/r₀) e^{a/r₀²} erfc(√a/r₀) = (1/r₀) erfcx(√a/r₀),  0 < w(a) ≤ 1/r₀,  w(a) ~ 1/√(πa) as a → ∞.

**Claim.** For r > 0, V(r) = ∫₀^∞ w(a) (2a)⁻¹ e^{−r²/(4a)} da. Hence g(t) := V(√t) is C^∞ on (0,∞), g > 0 and
(−1)ⁿ g⁽ⁿ⁾(t) = ∫₀^∞ w(a) (4a)⁻ⁿ (2a)⁻¹ e^{−t/(4a)} da > 0, so g satisfies upstream's `AdmissiblePotential`
(the definition in `OAI/Analysis/Triangular/Energy/Basic.lean`: ContDiffOn ⊤ on Ioi 0, g ≥ 0, (−1)^r iteratedDeriv r g ≥ 0).

## Proof (Tier C)
1. **Hankel representation.** For x > 0, b > 0: ∫₀^∞ J₀(bk)/(k + c) dk = (π/2)[H₀(bc) − Y₀(bc)]
   (standard table integral; the equation number is NOT verified here — the identity itself is checked numerically,
   check 1c, and Route B below avoids it entirely). With c = 1/r₀:
   V(r) = ∫₀^∞ J₀(kr)/(1 + r₀k) dk. This integral is **absolutely** convergent for r > 0 because
   |J₀(x)| ≤ min(1, √(2/(πx))) (up to an absolute constant), so the integrand is O(k^{−3/2}).
   This is exactly the inverse 2D Fourier transform V(r) = (1/2π)∫₀^∞ V̂(k) J₀(kr) k dk with
   V̂(k) = 2π/(k(1 + r₀k)) (convention V̂(k) = ∫ V(|x|) e^{−ik·x} d²x; Coulomb limit r₀ → 0 gives 2π/k ✓).
2. **Laplace representation of V̂ in s = k².** Standard pair: ∫₀^∞ e^{−sa} e^{b²a} erfc(b√a) da = 1/(√s(√s + b)), s > 0.
   With b = 1/r₀: 1/(√s(1 + r₀√s)) = (1/r₀)·1/(√s(√s + 1/r₀)) = ∫₀^∞ e^{−sa} w(a) da (numerically: check 1b).
   Hence 1/(1 + r₀k) = k ∫₀^∞ w(a) e^{−ak²} da for k > 0.
3. **Fubini — correction to the proof route.** The route said "everything is nonnegative (Tonelli)". That is false:
   J₀ changes sign. Moreover the crude bound |J₀| ≤ 1 does **not** suffice:
   ∫∫ w(a) e^{−ak²} k dk da = ∫ w(a)/(2a) da = ∞ (log divergence at a → 0, since w(0⁺) = 1/r₀).
   Correct justification: apply Tonelli to the absolute value with the *a*-integral first:
   ∫₀^∞ ∫₀^∞ w(a) e^{−ak²} k |J₀(kr)| da dk = ∫₀^∞ |J₀(kr)|/(1 + r₀k) dk < ∞ (step 1, decay of J₀).
   So the double integral is absolutely convergent and Fubini applies:
   V(r) = ∫₀^∞ w(a) [∫₀^∞ e^{−ak²} J₀(kr) k dk] da = ∫₀^∞ w(a) e^{−r²/(4a)}/(2a) da,
   using the Weber integral ∫₀^∞ e^{−ak²} J₀(kr) k dk = e^{−r²/(4a)}/(2a). Constants: check 1 (numbers in the Results section).
4. **Complete monotonicity in t = r².** Fix t₀ > 0 and work on t ∈ (t₀/2, ∞). For each n,
   |∂ₜⁿ [w(a) e^{−t/(4a)}/(2a)]| = w(a)(4a)^{−n}(2a)^{−1} e^{−t/(4a)} ≤ (1/r₀)(4a)^{−n}(2a)^{−1} e^{−t₀/(8a)} for a ≤ 1,
   and ≤ w(a)(4a)^{−n}(2a)^{−1} ≤ C a^{−n−3/2} for a ≥ 1. Both dominating functions are integrable on their ranges
   (e^{−t₀/(8a)} kills every power at a → 0; a^{−n−3/2} is integrable at ∞ for all n ≥ 0). The bounds are uniform in
   t > t₀/2, so differentiation under the integral is justified for every n by induction (dominated convergence /
   Mathlib's `hasDerivAt_integral_of_dominated_loc_of_deriv_le`), giving g ∈ C^∞(0,∞) and
   (−1)ⁿ g⁽ⁿ⁾(t) = ∫ w(a)(4a)^{−n}(2a)^{−1} e^{−t/(4a)} da > 0 since w > 0. ∎
   Equivalently (Bernstein): g(t) = ∫₀^∞ e^{−tu} dμ(u) with u = 1/(4a), dμ(u) = w(1/(4u)) (2u)⁻¹ du ≥ 0.
5. **Asymptotics.** r → 0: V = (1/r₀)[ln(2r₀/r) − γ] + o(1) (logarithmic, V > 0 everywhere since it is a positive
   mixture). r → ∞: V ~ 1/r (Coulomb tail; H₀ − Y₀ ~ 2/(πx)). Numerically: r·V(r) at r = 1000 r₀ is in the JSON.

## Results (Tier X, `result_numerics.json`, one run on core 7, r₀ = 1, mpmath dps 40)
- Check 1, mixture vs mpmath closed form, 50 radii in [0.01, 50]: max rel. error **2.1e-21** (target < 1e-8).
  Vs scipy `struve`/`y0`: 1.22e-13, identical to the scipy-vs-mpmath closed-form gap (scipy's own precision).
- Check 1b, erfc Laplace pair, s ∈ {1e-3 … 1e3}: 1.9e-41. Check 1c, Hankel integral (quadosc), r ∈ {0.1, 1, 5}:
  agreement to working precision; an independent truncated zero-partition quadrature at r = 1 differs by 2.4e-5
  (truncation tail) and a perturbed integrand differs by 3e-3, so the check is not vacuous. Check 1d (Route B,
  DLMF 11.5.2): 2.8e-41.
- Check 3: (−1)ⁿ dⁿ/dtⁿ of the **closed form** by mpmath.diff (independent of the mixture), n = 0..8,
  13 values t ∈ [1e-3, 1e3]: all strictly positive; max rel. deviation from the exact mixture derivative 1.4e-21.
- Positive control (Coulomb 1/√t, same pipeline, n ≤ 6): all positive.
- Negative controls (n ≤ 6), all fire: signed weight w(a)(1 − 2e^{−a}) negative already at n = 0 (V → −∞ as t → 0);
  e^{−t} − ½e^{−2t} negative from n = 2; Morse-type negative at n = 0..6.
- Asymptotics: V(10⁻⁶) − (ln(2/r) − γ) = 1.0e-6; r·V(r) at r = 1000 is 0.999999.
- Verdict: **KEEP** (proof checked by the producer only; producer ≠ verifier review still owed).

## Route B (independent, shorter; found during this attempt)
DLMF 11.5.2: H₀(x) − Y₀(x) = (2/π) ∫₀^∞ e^{−xu} (1+u²)^{−1/2} du, x > 0 (checked numerically to ~1e-31 at
x ∈ {0.01, 0.3, 1, 7, 50}, check 1d). Hence V(r) = (1/r₀) ∫₀^∞ e^{−ru/r₀} (1+u²)^{−1/2} du is a positive Laplace
transform in r, i.e. **completely monotone in r**. Since √t is a Bernstein function, f CM ⇒ f(√t) CM
(Schilling–Song–Vondraček, *Bernstein Functions*, Thm 3.7). Explicitly, by Lévy subordination
e^{−ρ√t} = ∫₀^∞ e^{−ta} ρ (4π)^{−1/2} a^{−3/2} e^{−ρ²/(4a)} da, which (Tonelli, all terms ≥ 0 here) re-derives a Gaussian
mixture with a nonnegative density. Consequence for novelty: CM of the Keldysh potential (even in r) is an immediate
consequence of a textbook formula; **only the connection to universal optimality is new**, if anything.

## What this does and does not give for the triangular lattice
- g is admissible, so `universal_energy_minimum` applies formally. But its energies live in ℝ≥0∞ and the
  1/r tail makes the 2D lattice sum diverge: latticeEnergy g = ∞, and the theorem then says ∞ ≤ energy g C, i.e. every
  density-one configuration also has infinite raw Keldysh energy. This is **the same caveat as Coulomb (Riesz s = 1)**:
  the raw-sum statement is ∞ ≤ ∞ and carries no information about which lattice wins.
- The physically meaningful object for a TMD Wigner crystal is the **jellium / neutralised (renormalised) energy**.
  It is **NOT covered** by this result or by upstream's theorem as stated.
- What is covered with content (Tier C, not numerically checked): products of CM functions are CM, so g_ε(t) = V(√t)·e^{−εt} is admissible and has a
  finite lattice sum. Thus the Gaussian-regularised Keldysh interaction is minimised by the triangular lattice among
  density-one configurations, for every ε > 0 and every r₀ (CM is preserved by t ↦ λt, so all densities are covered). The limit ε → 0 of the
  renormalised energies is not addressed.
- Conditional on upstream's theorem (AI-generated, not peer reviewed) and on definition fidelity.

## Literature (alphaXiv, 2026-10-25)
Queries: "Keldysh potential completely monotone / Laplace transform", "Wigner crystal TMD Keldysh",
"Rytova–Keldysh Struve integral representation", "triangular lattice completely monotone lattice energy".
- No paper found stating complete monotonicity of the Rytova–Keldysh potential in r² or its Gaussian-mixture weight.
  Not finding it is weak evidence; in view of Route B (DLMF 11.5.2) the CM property is immediate from a textbook
  formula, so we claim only the explicit statement and the connection to universal optimality.
- Related: 1904.01553 (anisotropic Keldysh interaction), 2606.23033 (strongly anisotropic Rytova–Keldysh, 2D excitons);
  2511.03353 (hexagonal lattice universally *locally* optimal for CM potentials of squared distance);
  2110.08728 (lattice energy minimisers of CM potentials); 1908.09714 (Coulomb/Riesz crystallisation from Cohn–Kumar);
  2601.16319 (Wigner crystallisation in monolayer WSe₂). From recall, not from this search: Montgomery (1988,
  theta functions) gives the lattice-only version for CM-in-r² potentials, which already implies triangular optimality
  *among lattices* for the ε-regularised case.

## H3L (stretch, not attempted) — Lean scoping
Needed in the pinned Mathlib (Lean 4.34.1):
1. Generic lemma: for measurable w ≥ 0 on Ioi 0 with ∀ m t>0, Integrable (w a · a^{−m} · e^{−t/a}),
   g(t) := ∫ a in Ioi 0, w a · e^{−t/(4a)}/(2a) is admissible. Proof: induction on n with
   `hasDerivAt_integral_of_dominated_loc_of_deriv_le` on a ball around t, then transfer to `iteratedDeriv` via
   `iteratedDeriv_succ` + `Filter.EventuallyEq.deriv_eq` on the open set Ioi 0; `ContDiffOn ⊤` via
   `contDiffOn_infty_iff_deriv_of_isOpen` (or the derivWithin form); nonnegativity by `integral_nonneg`.
   Estimated prior ≈ 0.30 within 2×45 min (fiddly bookkeeping, no mathematical obstacle).
2. Keldysh-specific identification: Mathlib has no Struve H₀ / Neumann Y₀ and (as far as checked) no erfcx bound,
   so "Keldysh ∈ Admissible" would have to *define* V by the mixture or by the Hankel integral — a statement-fidelity
   gap. Prior for the Struve-form statement ≈ 0.02; for "mixture-defined Keldysh is admissible" ≈ 0.25.
