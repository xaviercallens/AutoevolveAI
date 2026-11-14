import Autoresearch.YukawaMix

/-! Planted controls for the H2 contribution gate (both must be caught by `#print axioms`), plus positive non-vacuity
instances of the claimed theorems at concrete parameters. -/

namespace AutoresearchYukawaMixControls

open OAI.AtomicTriangular AutoresearchYukawa AutoresearchYukawaMix
open scoped Pointwise

theorem ctl_sorry : (1 : ℕ) = 2 := sorry

axiom ctl_cheat : False

theorem ctl_axiom : (1 : ℕ) = 2 := ctl_cheat.elim

/-- Positive instance: `e^{-r}/r + e^{-2r}/r` is admissible. -/
theorem pos_two_length : AdmissiblePotential (fun t => 1 * g 1 t + 1 * g 2 t) :=
  two_length_admissible (by norm_num) (by norm_num) (by norm_num) (by norm_num)

/-- Positive instance: a concrete two-length mixture on `Fin 2` has finite lattice energy at density `ρ = 3`. -/
theorem pos_mix_rho3_finite :
    latticeEnergy (fun t => yukawaMix (Finset.univ : Finset (Fin 2)) (fun _ => 1) (fun i => (i : ℝ) + 1)
      ((3 : ℝ)⁻¹ * t)) < ⊤ :=
  latticeEnergy_yukawaMix_rho_lt_top _ (fun _ _ => by norm_num) (fun i _ => by positivity) (by norm_num)

/-- Positive instance: single-length every-density optimality at `κ = 1/2`, `ρ = 2`. -/
theorem pos_yukawa_rho2 :
    LocallyFinite ((Real.sqrt 2)⁻¹ • A) ∧ TriangularDensity.DensityRho 2 ((Real.sqrt 2)⁻¹ • A) ∧
      ∀ C : Set Plane, LocallyFinite C → TriangularDensity.DensityRho 2 C →
        energy (g (1 / 2)) ((Real.sqrt 2)⁻¹ • A) ≤ energy (g (1 / 2)) C :=
  yukawa_optimal_any_density (κ := 1 / 2) (by norm_num) (ρ := 2) (by norm_num)

end AutoresearchYukawaMixControls

#print axioms AutoresearchYukawaMixControls.ctl_sorry
#print axioms AutoresearchYukawaMixControls.ctl_axiom
#print axioms AutoresearchYukawaMixControls.pos_two_length
#print axioms AutoresearchYukawaMixControls.pos_mix_rho3_finite
#print axioms AutoresearchYukawaMixControls.pos_yukawa_rho2
#print axioms AutoresearchYukawaMix.admissible_sum
#print axioms AutoresearchYukawaMix.yukawa_optimal_any_density
#print axioms AutoresearchYukawaMix.latticeEnergy_yukawa_rho_lt_top
#print axioms AutoresearchYukawaMix.yukawaMix_optimal_any_density
#print axioms AutoresearchYukawaMix.latticeEnergy_yukawaMix_rho_lt_top
#print axioms AutoresearchYukawaMix.signedMix_not_admissible
