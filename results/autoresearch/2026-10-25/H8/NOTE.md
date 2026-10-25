# H8: the Bogoliubov structure factor stays under the dual-scale bound

## What the project already had
`lean_src/DualLength.lean` (QuantumFluids) already proves:
- `feynman_ge_iff`: for any `S > 0`, `ℓ_F(k) ≥ 2/ks ⇔ S² ≤ k/(2ks)` (the dual-scale bound restated as a bound on S);
- `bogoliubov_envelope`, `ell_ge`: the Bogoliubov dispersion satisfies `ℓ ≥ 2/ks`;
- `not_bogoliubov_of_structure_factor`: if a measured `S` goes above the bound, the dispersion is not Bogoliubov (Feynman's inequality is a hypothesis there).
`lean_src/Duality.lean` has `bogoliubov_dual_form` and `bogoliubov_selfdual_bound`, the same envelope written in `c`.

No theorem in the project names the Bogoliubov structure factor `S_B = ε₀/ε_B` or states `S_B ≤ √(k/2ks)`.
H8 follows directly from the existing lemmas. The only missing piece is the Bijl–Feynman identity
`ε_F[S_B] = ε_B`, which is proved here as `feynman_sBog_exact`. So H8 was **not already proved as stated**,
but it is a **corollary**, not a new result. The other DS-QF′ item in the doc, the LHY/Beliaev correction
for cold atoms, can't be written in Lean without a verified literature coefficient, and the doc says so
itself. That is why H8 was kept as the target.

## Human proof
Write `x = k/ks`, with `ks = k* = 2mc/ħ = √2/ξ`. Then `ε₀ = ħ²k²/2m = hc·k²/ks` and
`ε_B² = (hc k)² + ε₀² = ε₀(ε₀ + 2gn)`. So

    S_B² = ε₀²/ε_B² = x²/(1+x²).

The bound `S_B² ≤ x/2` is the same as `2x ≤ 1 + x²`, which is `(x−1)² ≥ 0`. Equality holds exactly when
`x = 1`, the self-dual wavenumber `k = k*`. Taking square roots with `S_B > 0` gives `S_B ≤ √(k/2k*)`.
Second route (`sBog_sq_le_via_project`): Bijl–Feynman is exact for Bogoliubov (`ε_F[S_B] = ε_B`).
So `ℓ_F[S_B] = ℓ_B = 1/k + k/ks² ≥ 2/ks` (`ell_ge`), and `feynman_ge_iff` turns that into the bound on S.

## Negative control
The free-particle / ideal-Bose-gas value `S ≡ 1` breaks the bound for every `0 < k < 2k*`
(`free_S_one_violates`), and in particular at `k = k*` (`free_S_one_not_le_at_selfdual`). So the inequality
depends on the interaction. Without interaction there is no phonon branch and `S` does not drop below 1 at
long wavelength. (The non-interacting limit is singular in these variables because `ks ∝ c → 0`. The
control fixes `ks` and asks whether `S = 1` fits under the bound.)

## Physical meaning: a diffraction test of the weakly interacting regime
`S(k)` comes straight from X-ray or neutron diffraction, and in cold atoms from Bragg/in-situ density
correlations. No dispersion measurement is needed. In the weakly interacting (Bogoliubov) gas,
`S(k)/√(k/2k*) ≤ 1` at every `k`, and it touches 1 only at `k = k*`. So a measured `S(k)` that rises above
`√(k/2k*)` anywhere is evidence of correlations beyond Bogoliubov. In ⁴He at the roton the bound requires
`S ≤ 0.565`, and the measured peak is far above it. The project already has the refutation direction
(`not_bogoliubov_of_structure_factor`, given Feynman's variational inequality). This file adds the
consistency direction: Bogoliubov itself always passes the test, and the test is sharp.

## Scope
- These are Tier-A-style statements about the model formulas (`S_B = ε₀/ε_B`). They say nothing about any
  real fluid.
- Bogoliubov at T = 0 only. Feynman's relation is used as the definition of `S_B`, which is exact for
  Bogoliubov theory.
- Physics novelty: none. It is textbook algebra (AM-GM). What this adds is an explicit kernel-checked
  statement in the owner's project vocabulary.
- Producer ≠ verifier: an independent recompile is still pending.
