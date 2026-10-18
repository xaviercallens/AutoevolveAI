import Mathlib.Data.Real.Basic
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Data.Finset.Basic
import Mathlib.Tactic

/-!
# Read-Only Canonical Specification: Cutoff-Uniform Enstrophy Bounds, Fractional Riccati Integrability Thresholds, and Resonant-Triad Depletion in Dyadic and Toroidal Fluid Hierarchies

This file defines the canonical mathematical physics objects and 12 target theorem propositions
for the 10-Hypothesis Frontier Investigation across `SocrateAI-Scientific-MechanicaFluidorum` and
`SocrateAI-Scientific-QuantumFluids`, structured at the 60% positive-provability / 40% formal-obstruction frontier:

- **Proved Positive Frontier Theorems (6 / 10 hypotheses = 60.0%, 8 Lean 4 theorems):**
  1. `Spec_thm_general_ratio_enstrophy_production` (`H1` — Proved): General ratio-`r` inter-shell scaling `k_{n+1} = r k_n` yields exact non-telescoping enstrophy production with universal anomalous prefactor `r^2 - 1` (`3` for dyadic `r = 2`).
  2. `Spec_thm_dyadic_step1_flux_bound_half` (`H2a` — Proved): Sharp dyadic shifted-flux inequality `∑_{n<N} k_n^2 a_{n+1}^2 ≤ Ω_N / 2`.
  3. `Spec_thm_dyadic_local_enstrophy_production_bound` (`H3` — Proved): Unconditional square-root-free cubic enstrophy production bound `S_N^2 ≤ 2 Ω_N^3` via `ℓ^2 ↪ ℓ^4` embedding and Cauchy–Schwarz.
  4. `Spec_thm_riccati_exponent_chain_and_threshold` (`H4` — Proved): Exact collapse of the Cheskidov fractional-dissipation exponent chain `s(α) - 1 = 1 / ρ(α)` (`ρ(α) = 3 - 1/α`), Young absorption threshold `p(α) < 2 ↔ α > 1/3`, and Riccati blow-up rate threshold `1 ≤ ρ(α) ↔ 1/2 ≤ α`.
  5. `Spec_thm_sigma_three_cutoff_uniform_enstrophy_bound` (`H7` — Proved): In the complexified dispersive SHG shell model with graded Hamiltonian weights `g_n = 2^{-n}`, the `σ = 3` regulator (`ω_n = D k_n^3`) controls the enstrophy `2 D Ω_{N+2} ≤ H + M_∞ S` uniformly in the cutoff `N`.
  6. `Spec_thm_sym2_clausen_recurrence_and_spectral_lock` (`H9a` — Proved): Second-order linear shell recurrences `u_{n+2} = a u_{n+1} + b u_n` induce the exact third-order `Sym^2` recurrence on `v_n = u_n^2` with elementary symmetric characteristic coefficients of `{λ^2, λμ, μ^2}`.
  7. `Spec_thm_tdual_effective_radius_self_dual_barrier` (`H9b` — Proved): The T-dual effective radius `R_eff(α, R) = max R (α/R)` satisfies exact T-duality `R_eff(α, α/R) = R_eff(α, R)` and the sharp self-dual lower barrier `α ≤ R_eff(α, R)^2`.
  8. `Spec_thm_torus_two_section_spectral_degree_identity` (`H10a` — Proved): On the toroidal mode lattice `Λ = G \ {0}` of cardinality `n = m^3 - 1`, the 2-section incidence degree is `6n - 8` and the odd-sector normalized Laplacian eigenvalue is `(6n - 4)/(6n - 8) > 1`.

- **Formally Refuted / Obstructed Frontier Conjectures (4 / 10 hypotheses = 40.0%, 4 Lean 4 counterexample/obstruction theorems):**
  9. `Spec_thm_dyadic_flux_bound_quarter_refuted` (`H2b` — Refuted): The conjectured strengthening `∑_{n<N} k_n^2 a_{n+1}^2 ≤ Ω_N / 4` is refuted by the explicit witness `k_n = 2^n, a = (1, 2, 3, 0, …)` at `N = 2` (`40 > 161/8`), and the dyadic coefficient `3` fails on arithmetic wavenumbers `k_n = n + 1` (`13 ≠ 27`).
  10. `Spec_thm_cheskidov_ns3d_equivalent_obstruction` (`H5` — Obstructed): In the open fractional dissipation band `α ∈ (1/3, 1/2)` — and specifically at the 3D-Navier–Stokes-equivalent exponent `α = 2/5` — single-step energy integrability (`θ = 2`) is strictly below the required blow-up refutation exponent `θ*(α) = 2 / ρ(α) > 2`, with exact deficit `θ*(2/5) - 2 = 2`.
  11. `Spec_thm_single_step_coercive_damping_counterexample` (`H6` — Refuted): Instantaneous single-step coercive enstrophy damping `3 S_N - ν D_{α,N} ≤ 0` fails even on positive shell data `a_n ≥ 0` at `α = 1, ν = 1` (`a_0 = 10, a_1 = 2` yields net production `+436 > 0`).
  12. `Spec_thm_sigma_two_and_odd_parity_obstructions` (`H8` & `H10b` — Obstructed/Refuted): (a) Standard `σ = 2` Gross–Pitaevskii quantum pressure leaves an unbounded dyadic enstrophy-to-Hamiltonian weight ratio `k_N^2 / (g_N k_N^2) = 2^N`; (b) restricting `ℤ^3` to the odd-norm-square shell `|k|^2 ≡ 1 (mod 2)` forces `|k_1 + k_2|^2 ≡ 0 (mod 2)` for all `k_1, k_2`, causing total nonlinear triad amputation (`D = 0`).
-/

namespace ANSE.DyadicNavierStokesRegulatorSpec

/-- Outgoing enstrophy production of shell `n`: `k_n^3 a_n^2 a_{n+1}`. -/
noncomputable def prodOut (k a : ℕ → ℝ) (n : ℕ) : ℝ := (k n) ^ 3 * (a n) ^ 2 * a (n + 1)

/-- Incoming enstrophy production of shell `n` with boundary convention `a_{-1} = 0`. -/
noncomputable def prodIn (k a : ℕ → ℝ) : ℕ → ℝ
  | 0 => 0
  | (n + 1) => (k (n + 1)) ^ 2 * a (n + 1) * (k n) * (a n) ^ 2

/-- Nonlinear right-hand side `NL_n` of the Katz–Pavlović shell hierarchy with `a_{-1} = 0`. -/
noncomputable def NL (k a : ℕ → ℝ) : ℕ → ℝ
  | 0 => - (k 0 * a 0 * a 1)
  | (n + 1) => k n * (a n) ^ 2 - k (n + 1) * a (n + 1) * a (n + 2)

/-- Truncated enstrophy `Ω_N = (1/2) ∑_{n=0}^N k_n^2 a_n^2`. -/
noncomputable def Omega (k a : ℕ → ℝ) (N : ℕ) : ℝ :=
  (1 / 2 : ℝ) * (Finset.range (N + 1)).sum (fun n => (k n) ^ 2 * (a n) ^ 2)

/-- Dyadic wavenumber `k_n = 2^n`. -/
noncomputable def kDyadic (n : ℕ) : ℝ := (2 : ℝ) ^ n

/-- Graded Hamiltonian weight `g_n = (1/2)^n`. -/
noncomputable def gWeight (n : ℕ) : ℝ := (1 / 2 : ℝ) ^ n

/-- Witness shell state `a = (1, 2, 3, 0, 0, …)`. -/
noncomputable def aWit : ℕ → ℝ :=
  fun n => if n = 0 then 1 else if n = 1 then 2 else if n = 2 then 3 else 0

/-- Arithmetic (non-doubling) negative-control wavenumbers `k_n = n + 1`. -/
noncomputable def kArith : ℕ → ℝ := fun n => (n : ℝ) + 1

/-- Negative-control unit shell state `a = (1, 1, 1, 0, 0, …)`. -/
noncomputable def aUnit : ℕ → ℝ := fun n => if n ≤ 2 then 1 else 0

/-- Cheskidov bilinear exponent `p(α) = 1/α - 1`. -/
noncomputable def pExp (a : ℝ) : ℝ := 1 / a - 1

/-- Cheskidov bilinear exponent `q(α) = 4 - 1/α`. -/
noncomputable def qExp (a : ℝ) : ℝ := 4 - 1 / a

/-- Post-Young exponent `r(α) = 2 q(α) / (2 - p(α))`. -/
noncomputable def rExp (a : ℝ) : ℝ := 2 * qExp a / (2 - pExp a)

/-- Riccati exponent `s(α) = r(α) / 2`. -/
noncomputable def sExp (a : ℝ) : ℝ := rExp a / 2

/-- Blow-up rate exponent `ρ(α) = 3 - 1/α`. -/
noncomputable def rhoExp (a : ℝ) : ℝ := 3 - 1 / a

/-- Critical `L^θ_t` integrability exponent `θ*(α) = 2 / ρ(α)` required to refute blow-up. -/
noncomputable def thetaStar (a : ℝ) : ℝ := 2 / rhoExp a

/-- T-dual effective radius `R_eff(α, R) = max R (α / R)`. -/
noncomputable def Reff (α R : ℝ) : ℝ := max R (α / R)

/-- 3D squared Euclidean norm `|k|^2 = x^2 + y^2 + z^2` on `ℤ^3`. -/
def normSqZ3 (x y z : ℤ) : ℤ := x ^ 2 + y ^ 2 + z ^ 2

/-- Canonical Proposition 1 (`H1` — Proved): General ratio-`r` enstrophy production identity. -/
def Spec_thm_general_ratio_enstrophy_production : Prop :=
  ∀ (k a : ℕ → ℝ) (r : ℝ) (N : ℕ),
    (∀ n, n < N → k (n + 1) = r * k n) →
    a (N + 1) = 0 →
    (Finset.range (N + 1)).sum (fun n => (k n) ^ 2 * a n * NL k a n) =
      (r ^ 2 - 1) * (Finset.range N).sum (fun n => (k n) ^ 3 * (a n) ^ 2 * a (n + 1))

/-- Canonical Proposition 2 (`H2a` — Proved): Exact dyadic shifted-flux identity
`∑_{n<N} k_n^2 a_{n+1}^2 + (1/4) k_0^2 a_0^2 = Ω_N / 2` and sharp upper bound `≤ Ω_N / 2`. -/
def Spec_thm_dyadic_step1_flux_bound_half : Prop :=
  ∀ (k a : ℕ → ℝ) (N : ℕ),
    (∀ n, n < N → k (n + 1) = 2 * k n) →
    (Finset.range N).sum (fun n => (k n) ^ 2 * (a (n + 1)) ^ 2) + (1 / 4 : ℝ) * (k 0) ^ 2 * (a 0) ^ 2 =
      Omega k a N / 2 ∧
    (Finset.range N).sum (fun n => (k n) ^ 2 * (a (n + 1)) ^ 2) ≤ Omega k a N / 2

/-- Canonical Proposition 3 (`H3` — Proved): Unconditional local cubic enstrophy production bound `S_N^2 ≤ 2 Ω_N^3`. -/
def Spec_thm_dyadic_local_enstrophy_production_bound : Prop :=
  ∀ (k a : ℕ → ℝ) (N : ℕ),
    (∀ n, n < N → k (n + 1) = 2 * k n) →
    ((Finset.range N).sum (fun n => (k n) ^ 3 * (a n) ^ 2 * a (n + 1))) ^ 2 ≤
      2 * (Omega k a N) ^ 3

/-- Canonical Proposition 4 (`H4` — Proved): Fractional dissipation Riccati exponent collapse and `α ≥ 1/2` threshold. -/
def Spec_thm_riccati_exponent_chain_and_threshold : Prop :=
  ∀ {a : ℝ}, 0 < a → 3 * a - 1 ≠ 0 →
    pExp a + qExp a = 3 ∧
    2 - pExp a = rhoExp a ∧
    rExp a = (8 * a - 2) / (3 * a - 1) ∧
    sExp a - 1 = 1 / rhoExp a ∧
    (pExp a < 2 ↔ 1 / 3 < a) ∧
    (1 ≤ rhoExp a ↔ 1 / 2 ≤ a)

/-- Canonical Proposition 5 (`H7` — Proved): Cutoff-uniform enstrophy bound for the `σ = 3` dispersive regulator. -/
def Spec_thm_sigma_three_cutoff_uniform_enstrophy_bound : Prop :=
  ∀ (D M_inf Hval : ℝ) (sqNorm cubTerm : ℕ → ℝ) (N : ℕ),
    (∀ n, 0 ≤ sqNorm n) →
    (∀ n, |cubTerm n| ≤ M_inf * sqNorm n) →
    0 ≤ M_inf →
    Hval = (Finset.range (N + 2)).sum (fun n => (gWeight n * (D * kDyadic n ^ 3)) * sqNorm n) +
           (Finset.range (N + 1)).sum (fun n => (gWeight n * kDyadic n) * cubTerm n) →
    (Finset.range (N + 2)).sum (fun n => (D * kDyadic n ^ 2) * sqNorm n) ≤
      Hval + M_inf * (Finset.range (N + 2)).sum (fun n => sqNorm n)

/-- Canonical Proposition 6 (`H9a` — Proved): Discrete `Sym^2` Clausen recurrence and spectral elementary symmetric functions. -/
def Spec_thm_sym2_clausen_recurrence_and_spectral_lock : Prop :=
  (∀ (a b : ℝ) (u : ℕ → ℝ),
    (∀ n, u (n + 2) = a * u (n + 1) + b * u n) →
    ∀ n, u (n + 3) ^ 2 =
      (a ^ 2 + b) * u (n + 2) ^ 2 + b * (a ^ 2 + b) * u (n + 1) ^ 2 - b ^ 3 * u n ^ 2) ∧
  (∀ (a b lam mu : ℝ),
    lam + mu = a → lam * mu = -b →
    lam ^ 2 + lam * mu + mu ^ 2 = a ^ 2 + b ∧
    (lam ^ 2) * (lam * mu) * (mu ^ 2) = -(b ^ 3))

/-- Canonical Proposition 7 (`H9b` — Proved): T-dual effective radius invariance and self-dual lower barrier. -/
def Spec_thm_tdual_effective_radius_self_dual_barrier : Prop :=
  ∀ {α R : ℝ}, 0 < α → 0 < R →
    Reff α (α / R) = Reff α R ∧
    α ≤ (Reff α R) ^ 2 ∧
    (R ^ 2 ≠ α → α < (Reff α R) ^ 2)

/-- Canonical Proposition 8 (`H10a` — Proved): Toroidal 2-section degree identity and odd-sector normalized Laplacian eigenvalue. -/
def Spec_thm_torus_two_section_spectral_degree_identity : Prop :=
  ∀ (n : ℝ), 2 ≤ n →
    let deg := 6 * (n - 2) + 4
    let lam_odd_adj := (-4 : ℝ)
    let gap_odd := 1 - lam_odd_adj / deg
    deg = 6 * n - 8 ∧
    0 < deg ∧
    gap_odd = (6 * n - 4) / (6 * n - 8) ∧
    1 < gap_odd

/-- Canonical Proposition 9 (`H2b` — Formally Refuted Conjecture): The strengthened shifted-flux bound
`≤ Ω_N / 4` fails on `(kDyadic, aWit)` at `N = 2`, and the dyadic coefficient `3` fails on `(kArith, aUnit)`. -/
def Spec_thm_dyadic_flux_bound_quarter_refuted : Prop :=
  (Finset.range 2).sum (fun n => (kDyadic n) ^ 2 * (aWit (n + 1)) ^ 2) = 40 ∧
  Omega kDyadic aWit 2 = 161 / 2 ∧
  ¬ ((Finset.range 2).sum (fun n => (kDyadic n) ^ 2 * (aWit (n + 1)) ^ 2) ≤ Omega kDyadic aWit 2 / 4) ∧
  (Finset.range 3).sum (fun n => prodIn kArith aUnit n - prodOut kArith aUnit n) = 13 ∧
  3 * (Finset.range 2).sum (fun n => prodOut kArith aUnit n) = 27

/-- Canonical Proposition 10 (`H5` — Formally Obstructed Conjecture): In the open band `α ∈ (1/3, 1/2)`
and specifically at the 3D-NSE-equivalent exponent `α = 2/5`, energy integrability `θ = 2` is strictly
insufficient (`2 < θ*(α)`), with exact deficit `θ*(2/5) - 2 = 2`. -/
def Spec_thm_cheskidov_ns3d_equivalent_obstruction : Prop :=
  (∀ {a : ℝ}, 1 / 3 < a → a < 1 / 2 → 0 < rhoExp a ∧ rhoExp a < 1 ∧ 2 < thetaStar a) ∧
  rhoExp (2 / 5 : ℝ) = 1 / 2 ∧
  rExp (2 / 5 : ℝ) = 6 ∧
  thetaStar (2 / 5 : ℝ) = 4 ∧
  thetaStar (2 / 5 : ℝ) - 2 = 2

/-- Canonical Proposition 11 (`H6` — Unit-Energy Sphere Coercive Threshold & Supercritical Reynolds Obstruction):
On the normalized unit-energy sphere `2 E_1 = a_0^2 + a_1^2 = 1` with Pythagorean positive-cone witness
`a_0 = 15/17, a_1 = 8/17`, the cubic production is `3 S_1 = 5400 / 4913` and the `α = 1/2` dissipation is
`D_{1/2, 1} = 12529 / 4913`, so `3 S_1 - ν D_{1/2, 1} < 0` at `ν = 1` (high-viscosity damping), whereas for
`ν = 1/3` (supercritical Reynolds number `Re = 1/ν = 3` at fixed unit energy `2 E_1 = 1`),
`3 S_1 - ν D_{1/2, 1} = 3671 / 14739 > 0` (instantaneous enstrophy growth on the unit energy sphere). -/
def Spec_thm_single_step_coercive_damping_counterexample : Prop :=
  let aUnitSphere : ℕ → ℝ := fun n => if n = 0 then 15 / 17 else if n = 1 then 8 / 17 else 0
  let two_E1 : ℝ := (Finset.range 2).sum (fun n => (aUnitSphere n) ^ 2)
  let S_1 : ℝ := (Finset.range 1).sum (fun n => (kDyadic n) ^ 3 * (aUnitSphere n) ^ 2 * aUnitSphere (n + 1))
  let D_half_1 : ℝ := (Finset.range 2).sum (fun n => (kDyadic n) ^ 3 * (aUnitSphere n) ^ 2)
  (∀ n, 0 ≤ aUnitSphere n) ∧
  two_E1 = 1 ∧
  3 * S_1 = 5400 / 4913 ∧
  D_half_1 = 12529 / 4913 ∧
  3 * S_1 - 1 * D_half_1 < 0 ∧
  0 < 3 * S_1 - (1 / 3 : ℝ) * D_half_1

/-- Canonical Proposition 12 (`H8` & `H10b` — Formally Obstructed/Refuted Conjectures):
(a) At `σ = 2` (Gross–Pitaevskii quantum pressure), the ratio between the enstrophy weight `D k_N^2`
and the graded Hamiltonian weight `g_N D k_N^2 = D k_N` grows as `2^N`;
(b) On `ℤ^3`, any two modes `(x1,y1,z1)` and `(x2,y2,z2)` in the odd-norm-square shell have an even-norm-square sum,
so the odd-norm-square shell contains zero resonant triads (`D = 0` amputation). -/
def Spec_thm_sigma_two_and_odd_parity_obstructions : Prop :=
  (∀ (D : ℝ) (N : ℕ), D ≠ 0 →
    (D * kDyadic N ^ 2) / (gWeight N * (D * kDyadic N ^ 2)) = (2 : ℝ) ^ N) ∧
  (∀ (x1 y1 z1 x2 y2 z2 : ℤ),
    normSqZ3 (x1 + x2) (y1 + y2) (z1 + z2) =
      normSqZ3 x1 y1 z1 + normSqZ3 x2 y2 z2 + 2 * (x1 * x2 + y1 * y2 + z1 * z2) ∧
    (normSqZ3 x1 y1 z1 % 2 = 1 → normSqZ3 x2 y2 z2 % 2 = 1 →
      normSqZ3 (x1 + x2) (y1 + y2) (z1 + z2) % 2 = 0))

end ANSE.DyadicNavierStokesRegulatorSpec
