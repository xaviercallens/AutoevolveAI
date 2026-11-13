/-
  ANSE.NavierStokesSmoothness — Clay Millennium Problem Formulation (Fefferman 2000/2006)

  Statement-Review Note (TODO 8 / H9 — Clay Hypothesis Mapping):
  Maps Charles L. Fefferman, "Existence and Smoothness of the Navier-Stokes Equation"
  (Clay Mathematics Institute Millennium Prize Problem, Case A on ℝ³ with f ≡ 0)
  to Lean 4 definitions:
    • Clay Eq. (1) [Momentum PDE on [0, ∞) × ℝ³]:
      `SatisfiesNavierStokes` — `(fderiv ℝ (fun s => u s x) t 1) + advection (u t) x = -gradient (p t) x + ν • laplacian (u t) x`
    • Clay Eq. (2) [Incompressibility / Solenoidal velocity]:
      `IsDivergenceFree u₀` and `IsDivergenceFree (u t)` — `∀ x : Point3, divergence v x = 0`
    • Clay Eq. (3) [Initial velocity condition at t = 0]:
      `u 0 = u₀`
    • Clay Eq. (4) [Schwartz rapid spatial decay of initial data u° and all derivatives]:
      `HasSchwartzRapidDecay u₀` — `∀ m K : ℕ, ∃ C > 0, ∀ x : Point3, ‖iteratedFDeriv ℝ m u₀ x‖ * (1 + ‖x‖) ^ K ≤ C`
    • Clay Eq. (5) [Zero external forcing f ≡ 0]:
      Homogeneous unforced formulation in `SatisfiesNavierStokes`.
    • Clay Eq. (6) [Global C^∞ smoothness on ℝ³ × [0, ∞)]:
      `(∀ t ≥ 0, ContDiff ℝ ⊤ (u t)) ∧ (∀ t ≥ 0, ContDiff ℝ ⊤ (p t))`
    • Clay Eq. (7) [Physically reasonable / Bounded kinetic energy]:
      `HasBoundedKineticEnergy u` — uniform spatial energy envelope `∃ E_max > 0, ∀ t ≥ 0, ∀ x, ‖u t x‖² * (1 + ‖x‖²)² ≤ E_max`,
      which guarantees finite L² kinetic energy on ℝ³ and rules out spatially uniform parasitic
      solutions `u(x, t) = f(t), p(x, t) = -f'(t) · x`.
-/

import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.Analysis.Calculus.FDeriv.Basic
import Mathlib.Analysis.Calculus.ContDiff.Basic

open InnerProductSpace

namespace ANSE.NavierStokes

-- Spatial domain is Euclidean 3-space R^3
abbrev Point3 := Fin 3 → ℝ
abbrev Vector3 := Fin 3 → ℝ

/-- Canonical basis vector e_i in R^3 -/
def basisVector (i : Fin 3) : Vector3 :=
  fun j => if j = i then (1 : ℝ) else 0

/-- The divergence of a differentiable vector field on R^3: ∇ · v -/
noncomputable def divergence (v : Point3 → Vector3) (x : Point3) : ℝ :=
  ∑ i : Fin 3, fderiv ℝ (fun p => v p i) x (basisVector i)

/-- Clay Eq. (2): Incompressibility condition (solenoidal velocity field) -/
def IsDivergenceFree (v : Point3 → Vector3) : Prop :=
  ∀ x : Point3, divergence v x = 0

/-- Spatial Laplacian of a vector field: Δ u = ∑_i ∂²u/∂x_i² -/
noncomputable def laplacian (v : Point3 → Vector3) (x : Point3) : Vector3 :=
  fun k => ∑ i : Fin 3,
    fderiv ℝ (fun p => fderiv ℝ (fun q => v q k) p (basisVector i)) x (basisVector i)

/-- Gradient of a scalar pressure field: ∇p -/
noncomputable def gradient (p : Point3 → ℝ) (x : Point3) : Vector3 :=
  fun i => fderiv ℝ p x (basisVector i)

/-- Non-linear convective directional derivative: (u · ∇)u -/
noncomputable def advection (u : Point3 → Vector3) (x : Point3) : Vector3 :=
  fun k => ∑ i : Fin 3, u x i * fderiv ℝ (fun p => u p k) x (basisVector i)

/-- Clay Eq. (4): Schwartz rapid spatial decay of initial velocity u₀ and all of its
    Fréchet derivatives: for every derivative order m and polynomial weight K,
    ‖D^m u₀(x)‖ · (1 + ‖x‖)^K ≤ C_{m,K}. -/
def HasSchwartzRapidDecay (u₀ : Point3 → Vector3) : Prop :=
  ∀ (m K : ℕ), ∃ C : ℝ, C > 0 ∧
    ∀ x : Point3, ‖iteratedFDeriv ℝ m u₀ x‖ * (1 + ‖x‖) ^ K ≤ C

/-- Clay Eq. (7): Bounded kinetic energy / physically reasonable decay envelope on ℝ³ × [0, ∞),
    ensuring uniform L² integrability on ℝ³ and excluding spatially uniform blowup modes. -/
def HasBoundedKineticEnergy (u : ℝ → Point3 → Vector3) : Prop :=
  ∃ E_max : ℝ, E_max > 0 ∧
    ∀ t : ℝ, t ≥ 0 →
      ∀ x : Point3, ‖u t x‖ ^ 2 * (1 + ‖x‖ ^ 2) ^ 2 ≤ E_max

/-- Clay Eqs. (1)–(2): Classical 3D Incompressible Navier-Stokes Equations on ℝ × ℝ³:
    ∂t u + (u · ∇)u = - ∇p + ν Δu, div u = 0. -/
def SatisfiesNavierStokes
    (u : ℝ → Point3 → Vector3)
    (p : ℝ → Point3 → ℝ)
    (ν : ℝ) : Prop :=
  ∀ (t : ℝ) (x : Point3),
    -- Incompressibility constraint
    IsDivergenceFree (u t) ∧
    -- Momentum conservation
    (fderiv ℝ (fun s => u s x) t 1) + advection (u t) x =
      - gradient (p t) x + ν • laplacian (u t) x

/-- Clay Millennium Problem Statement (Fefferman 2000/2006, Case A):
    Global Existence, Smoothness, and Bounded Kinetic Energy on ℝ³. -/
def NavierStokesGlobalExistenceAndSmoothness : Prop :=
  ∀ (u₀ : Point3 → Vector3) (ν : ℝ),
    ν > 0 →
    IsDivergenceFree u₀ →
    ContDiff ℝ ⊤ u₀ →
    HasSchwartzRapidDecay u₀ →
    ∃ (u : ℝ → Point3 → Vector3) (p : ℝ → Point3 → ℝ),
      (∀ t ≥ 0, ContDiff ℝ ⊤ (u t)) ∧
      (∀ t ≥ 0, ContDiff ℝ ⊤ (p t)) ∧
      u 0 = u₀ ∧
      SatisfiesNavierStokes u p ν ∧
      HasBoundedKineticEnergy u

/-- Consistency check: the stationary zero velocity field satisfies `HasBoundedKineticEnergy`. -/
theorem zero_solution_has_bounded_kinetic_energy :
    HasBoundedKineticEnergy (fun _ _ => (0 : Vector3)) := by
  refine ⟨1, zero_lt_one, ?_⟩
  intro t _ht x
  simp

/-- Pointwise kinetic energy bound implied by the Clay `HasBoundedKineticEnergy` envelope:
    at every time t ≥ 0 and point x ∈ ℝ³, ‖u(t, x)‖² ≤ E_max. -/
theorem pointwise_energy_le_of_bounded_kinetic_energy
    {u : ℝ → Point3 → Vector3} {E_max : ℝ}
    (h_bound : ∀ t ≥ 0, ∀ x : Point3, ‖u t x‖ ^ 2 * (1 + ‖x‖ ^ 2) ^ 2 ≤ E_max)
    {t : ℝ} (ht : t ≥ 0) (x : Point3) :
    ‖u t x‖ ^ 2 ≤ E_max := by
  have h1 : (1 : ℝ) ≤ 1 + ‖x‖ ^ 2 := by
    have : (0 : ℝ) ≤ ‖x‖ ^ 2 := sq_nonneg ‖x‖
    linarith
  have h2 : (1 : ℝ) ≤ (1 + ‖x‖ ^ 2) ^ 2 := by nlinarith
  have h3 : ‖u t x‖ ^ 2 * 1 ≤ ‖u t x‖ ^ 2 * (1 + ‖x‖ ^ 2) ^ 2 :=
    mul_le_mul_of_nonneg_left h2 (sq_nonneg ‖u t x‖)
  have h4 := h_bound t ht x
  linarith

#print axioms zero_solution_has_bounded_kinetic_energy
#print axioms pointwise_energy_le_of_bounded_kinetic_energy

end ANSE.NavierStokes
