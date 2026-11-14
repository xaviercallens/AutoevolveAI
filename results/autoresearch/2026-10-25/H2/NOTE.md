# H2: Yukawa / Debye–Hückel crystals are triangular. Producer KEEP, attempt 1 (about 11 min)

**Statement (Lean):** for `κ > 0`, `g κ t = exp(-κ √t) / √t` (the pair interaction `e^{-κ r}/r` with `t = r²`) is
`AdmissiblePotential` (`yukawa_admissible`). So the triangular lattice minimises the Yukawa energy among locally finite
density-one planar configurations (`triangular_yukawa_optimal`, via `OAI.AtomicTriangular.universal_energy_minimum`).
The lattice energy is finite (`latticeEnergy_yukawa_lt_top`), so the corollary is not vacuous.

**Route.** No Faà di Bruno and no Bernstein integral were needed:
1. (P) `mul_sign`: a pointwise Leibniz sign lemma (Mathlib `iteratedDeriv_mul` at a point, using `ContDiffAt`), which
   gives `admissible_mul`: a product of admissible potentials is admissible.
2. (E) `phi_admissible`: `φ = exp(-κ√t)` satisfies `φ' = -(κ/2) t^{-1/2} φ` on `(0,∞)`. Strong induction on `n`,
   with `Set.EqOn.iteratedDeriv_of_isOpen` to move from `deriv φ` to the product, and `mul_sign` using signs of φ
   only up to order `n`, gives `(-1)^{n+1} φ^{(n+1)} ≥ 0`.
3. `g = riesz 1 · φ` on `(0,∞)` (`g_eqOn`). Then `admissible_congr` (admissibility depends only on values on `(0,∞)`)
   finishes the proof.
4. Finiteness: `exp x ≥ x²/2` gives `g ≤ (2/κ²) t^{-3/2}`, compared with `latticeEnergy_riesz_lt_top (s := 3)`.

**Gate.** Compiles rc 0 (`compile_yukawa.json`, olean `Autoresearch.Yukawa`). Every claimed theorem uses only
`[propext, Classical.choice, Quot.sound]`. The planted controls are caught (`ctl_sorry` → `[sorryAx]`,
`ctl_axiom` → `[AutoresearchYukawaControls.ctl_cheat]`). The forbidden-token grep is clean. Numeric gate run first
(`falsification_gate.json`): 0 violations for g and φ; both negative controls are flagged.

**Negative control (Lean):** `c_not_admissible`: `exp(-κ√t) cos t` is not admissible (negative at `t = π`).

**Caveats.** This is a producer-only KEEP; Tier A needs an independent recompile and a statement audit. The result
depends on upstream's theorem (AI-generated, not peer reviewed) and on definition fidelity. It is the classical
model only. Statement fidelity: `e^{-κr}/r` is the 3D screened-Coulomb (Yukawa) potential between particles confined to a plane (the standard 2D Yukawa crystal of dusty plasmas and colloids), exactly the preregistered formula. It is not the Green function of the 2D Debye–Hückel equation, which is `K_0(κr)`. Novelty is not claimed: complete monotonicity of the Yukawa potential in `r²` is classical. The new part
is the kernel-checked corollary inside this framework.

## Independent verification: ACCEPT (verification.md)
- Title wording: this is the planar **Yukawa** (3D-screened Coulomb e^{-kr}/r) interaction, not the 2D Debye–Hückel Green
  function K0(kr). Conditional on upstream `universal_energy_minimum`.
