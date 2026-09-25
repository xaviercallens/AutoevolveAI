import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.Analysis.Calculus.FDeriv.Basic
import Mathlib.Analysis.Calculus.ContDiff.Basic

open InnerProductSpace

-- Spatial domain is Euclidean 3-space R^3
abbrev Point3 := Fin 3 → ℝ
abbrev Vector3 := Fin 3 → ℝ

/-- Canonical basis vector e_i in R^3 -/
def basisVector (i : Fin 3) : Vector3 :=
  fun j => if j = i then (1 : ℝ) else 0

/-- The divergence of a differentiable vector field on R^3: ∇ · v -/
noncomputable def divergence (v : Point3 → Vector3) (x : Point3) : ℝ :=
  ∑ i : Fin 3, fderiv ℝ (fun p => v p i) x (basisVector i)

/-- Incompressibility condition: solenoidal velocity field -/
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

/-- Classical 3D Incompressible Navier-Stokes Equations on R × R^3:
    ∂t u + (u · ∇)u = - ∇p + ν Δu -/
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

/-- Millennium Problem Statement: Global Existence and Smoothness on R^3 -/
def NavierStokesGlobalExistenceAndSmoothness : Prop :=
  ∀ (u₀ : Point3 → Vector3) (ν : ℝ),
    ν > 0 →
    IsDivergenceFree u₀ →
    ContDiff ℝ ⊤ u₀ →
    ∃ (u : ℝ → Point3 → Vector3) (p : ℝ → Point3 → ℝ),
      (∀ t ≥ 0, ContDiff ℝ ⊤ (u t)) ∧
      (∀ t ≥ 0, ContDiff ℝ ⊤ (p t)) ∧
      u 0 = u₀ ∧
      SatisfiesNavierStokes u p ν
