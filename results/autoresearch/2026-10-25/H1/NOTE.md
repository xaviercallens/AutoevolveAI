# H1: bilayer (dipolar / indirect) exciton potential is admissible. KEEP (producer-checked)

**Statement (Lean, `formal_cert/Autoresearch/DipolarExciton.lean`, namespace `AutoresearchDipolar`).**
`g d t = 2 * (t^(-1/2) - (t + d^2)^(-1/2))`.
- `dipolar_admissible (hd : 0 < d) : AdmissiblePotential (g d)`
- `triangular_dipolar_optimal (hd : 0 < d) C (hC : LocallyFinite C) (hdens : DensityOne C) : latticeEnergy (g d) ≤ energy (g d) C`
- Negative control: `h d t = t^(-1/2) - 2 (t + d^2)^(-1/2)`; `h_neg_at : h d (d^2) < 0`, `h_not_admissible : ¬ AdmissiblePotential (h d)`.

**Human proof.** The r-th derivative of `(t + c)^a` is `descPoch_r(a) (t + c)^(a - r)` (Mathlib
`iteratedDeriv_comp_add_const` + `Real.iter_deriv_rpow_const`). So
`(-1)^r g_d^(r)(t) = 2 ascPoch_r(1/2) (t^(-1/2-r) - (t+d^2)^(-1/2-r))`, using `(-1)^r descPoch_r(-1/2) = ascPoch_r(1/2) > 0`.
The bracket is ≥ 0 because `x ↦ x^e` is antitone on (0,∞) for `e ≤ 0`. Smoothness: rpow is smooth away from 0.
Negative control: at `t = d^2`, `(2d^2)^(-1/2) > (4d^2)^(-1/2) = (d^2)^(-1/2)/2`, so `h_d(d^2) < 0`.

**Physics model.** Rigid vertical dipoles: each exciton is an electron in one layer directly above a hole in the
other layer, separation d. Pair energy at in-plane distance r: e-e + h-h = 2/r, e-h' + h-e' = -2/√(r²+d²).
In `t = r²` this is `g_d`. The theorem says the triangular lattice minimises this classical energy.

**Scope.**
- Classical (no kinetic or zero-point energy), density one (other densities by scaling d), rigid dipoles
  aligned perpendicular to the layers (no in-plane e-h offset, no separate electron/hole crystals).
- Conditional on upstream `OAI.AtomicTriangular.universal_energy_minimum` (openai/math, AI-generated, not peer
  reviewed) and on the fidelity of its definitions (`energy` = liminf of disk averages, `LocallyFinite`, `DensityOne`).
- KEEP is producer-checked only. Tier A needs an independent recompile and statement audit.

**Literature (alphaXiv, 2026-10-25).** Experiments and simulations widely assume or observe triangular dipolar
exciton and dipolar-boson crystals (e.g. arXiv:2602.19438, 2601.19603, 2401.04639). The corollary pattern
"completely monotone potential + Cohn–Kumar ⇒ triangular optimal" is known in the literature (arXiv:1908.09714 for
Riesz/Coulomb; arXiv:2110.08728 for two-species CM energies; arXiv:2511.03353 for local optimality). The search did
not find an explicit statement that the full bilayer potential `2(1/r - 1/√(r²+d²))` is completely monotone in r², or a
kernel-checked optimality corollary for it. What may be new is that kernel-checked corollary, which is conditional
on upstream. The complete-monotonicity fact itself is elementary. arXiv:2610.17030 reports a honeycomb crystal in a
mass-asymmetric e-h bilayer. That is a different model (independent quantum species, not rigid dipoles) and does
not contradict this result.
