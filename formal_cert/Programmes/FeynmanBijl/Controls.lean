import Programmes.FeynmanBijl.Basic

/-!
# P6 Feynman–Bijl: planted controls (must be CAUGHT by the axiom gate; never import this file)

Both theorems "prove" the false strengthening `A(ρ) = f` (missing the factor 1/2, and without the
symmetry hypothesis) for every symmetric `H` and eigenvector `ψ`. It is false in general: by
`double_comm_expect`, any `ρ = ρ†` with `A(ρ) ≠ 0` has `f = 2 A(ρ) ≠ A(ρ)`. The file compiles
with exit code 0; only `#print axioms` exposes the cheats (`sorryAx`, resp.
`ProgFeynmanBijl.ctl_cheat`).
-/

namespace ProgFeynmanBijl

open scoped InnerProductSpace
open LinearMap

theorem ctl_sorry {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℂ E]
    [FiniteDimensional ℂ E] (H ρ : E →ₗ[ℂ] E) (E0 : ℝ) (ψ : E) (_hH : H.IsSymmetric)
    (_hψ : H ψ = (E0 : ℂ) • ψ) :
    excess H E0 ψ ρ = ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ := sorry

axiom ctl_cheat : False

theorem ctl_axiom {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℂ E]
    [FiniteDimensional ℂ E] (H ρ : E →ₗ[ℂ] E) (E0 : ℝ) (ψ : E) (_hH : H.IsSymmetric)
    (_hψ : H ψ = (E0 : ℂ) • ψ) :
    excess H E0 ψ ρ = ⟪ψ, comm (adjoint ρ) (comm H ρ) ψ⟫_ℂ := ctl_cheat.elim

end ProgFeynmanBijl

#print axioms ProgFeynmanBijl.ctl_sorry
#print axioms ProgFeynmanBijl.ctl_axiom
