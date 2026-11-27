# H1b: the dipolar-exciton lattice energy is finite. KEEP (producer-checked)

**Statement (Lean).** `AutoresearchDipolar.latticeEnergy_dipolar_lt_top (d : ℝ) : latticeEnergy (g d) < ⊤`
(holds for every real d; d = 0 gives g = 0). Lemmas: `diff_le : t^(-1/2) - (t+c)^(-1/2) ≤ (c/2) t^(-3/2)`
for c ≥ 0, t > 0, and `g_le : g d t ≤ d^2 * riesz 3 t`.

**Human proof.** Put a = t^(-1/2) and b = (t+c)^(-1/2). Then 0 < b ≤ a, a²t = 1 and b²(t+c) = 1, so
(a-b)(a+b) = a² - b² = c a² b². Since 2b² ≤ a(a+b), we get 2(a-b)(a+b) ≤ c a³ (a+b). Divide by a+b > 0:
a - b ≤ (c/2) a³ = (c/2) t^(-3/2). Hence g_d(t) ≤ d² t^(-3/2). Term by term in the ENNReal tsum (each lattice point
has ‖x‖² > 0), latticeEnergy(g_d) ≤ ofReal(d²) · latticeEnergy(riesz 3), and the right side is finite by
`TriangularRiesz.latticeEnergy_riesz_lt_top` at s = 3.

**Why it matters.** It makes `triangular_dipolar_optimal` informative: the minimum energy is finite. The Coulomb
case (s = 1) does not have this property.

**Scope.** As in H1: classical, density one, rigid vertical dipoles. Depends on our own `RieszFinite.lean` (D1b) and
openai/math's `summable_normForm_neg_rpow`. Only the optimality corollary depends on upstream's
`universal_energy_minimum`; this finiteness statement does not. KEEP is producer-checked. Tier A is pending an
independent recompile.
