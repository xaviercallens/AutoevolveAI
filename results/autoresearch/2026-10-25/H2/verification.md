# H2 independent verification (producer ≠ verifier), 2026-10-25

**VERDICT: ACCEPT** (Tier A for the Lean statements as written; conditional on upstream `universal_energy_minimum`).

## 1. Recompile + axioms
- A verbatim copy of `formal_cert/Autoresearch/Yukawa.lean` was made, with a verifier block appended (statement pins,
  non-vacuity instances, a planted sorry of my own). It was compiled with
  `taskset -c 4,5 python3 scripts/certified_numerics/lean_pinned.py compile` (pinned Lean 4.34.1). Result:
  **rc 0, 17.9 s**, imports `Triangular.RieszFinite`.
- My own `#print axioms` (verbatim):
  - `yukawa_admissible`, `triangular_yukawa_optimal`, `latticeEnergy_yukawa_lt_top`, `admissible_mul`,
    `phi_admissible`: each `depends on axioms: [propext, Classical.choice, Quot.sound]`
  - planted `VerifierH2.v_planted : AdmissiblePotential (c 1) := sorry`: `[propext, sorryAx, Classical.choice, Quot.sound]`
  - downstream `v_planted_use : False`: `[propext, sorryAx, ...]`. So `sorryAx` propagates and is caught.

## 2. Statement adequacy (adversarial)
- **g is exactly the target.** I proved `g κ t = exp(-κ√t)/√t` and `phi κ t = exp(-κ√t)` by `rfl`. For r > 0 I proved
  `g κ (r^2) = exp(-κ r)/r`, so this is the screened-Coulomb pair interaction in t = r², matching the prereg formula.
- **Definitions are upstream's.** `AdmissiblePotential` unfolds (`Iff.rfl`) to upstream
  `OAI.TriangularUniversal.AdmissiblePotential`: C^∞ on (0,∞), ≥ 0 on (0,∞), and (-1)^r g^(r) ≥ 0 for all r.
  `latticeEnergy` is `rfl`-equal to `∑' a : {x ∈ A, x ≠ 0}, ofReal (g ‖a‖²)` over upstream's density-one lattice `A`.
- **`admissible_mul` is fully general.** Its statement is `∀ {f h}, Admissible f → Admissible h → Admissible (f*h)`,
  with no extra hypotheses. The proof is pointwise Leibniz: `iteratedDeriv_mul` at a point, with every term of the
  binomial sum of sign (-1)^r. This is correct.
- **Hypothesis use.** κ > 0 is used in two places:
  - in `phi_sign`, for the sign of κ/2;
  - in `g_le`, for the bound g ≤ (2/κ²) t^{-3/2}.
  At κ = 0, g = `riesz 1` (s = 1 ≤ 2), whose lattice sum diverges. So finiteness genuinely needs κ > 0. For κ < 0,
  g is not completely monotone.
- **Finiteness is genuine.** `latticeEnergy (g κ) < ⊤` is compared against `latticeEnergy_riesz_lt_top (s := 3)`.
  So the corollary `latticeEnergy ≤ energy C` is not `⊤ ≤ ⊤`. I also proved g > 0 on (0,∞), so the energy is not 0
  either.
- **Non-vacuity.** I instantiated `yukawa_admissible one_pos` and `latticeEnergy_yukawa_lt_top one_pos`.

## 3. Junk values / vacuity
- `g κ 0 = 0` (I proved this). It is a junk value because √0 = 0 and x/0 = 0. It is harmless:
  - `AdmissiblePotential` constrains only t > 0;
  - `energy` evaluates g only at ‖x−y‖² with y ∈ `erase x`, and distinct points give t > 0;
  - `latticeEnergy` evaluates g only at a ≠ 0.
- No definition trivialises the theorem. The negative control `c_not_admissible` also checks.

## Corrections (non-blocking)
1. Keep the caveat that the result is conditional on upstream `universal_energy_minimum`. That theorem is
   AI-generated and Comparator-accepted, not peer reviewed.
2. The H2 title says "Debye–Hückel". As NOTE.md already says, this is the 3D screened Coulomb interaction between
   particles in a plane, not the 2D Debye–Hückel Green function K0(κr). The title should say "Yukawa (3D-screened)".
3. Novelty: complete monotonicity of e^{-κr}/r in r² is classical. Only the kernel-checked corollary is new here.
