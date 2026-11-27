import Programmes.CompletelyMonotone.Bernstein
import Programmes.CompletelyMonotone.Laplace
import Autoresearch.DipolarExciton

/-!
# Programme P3: the H1–H3 admissibility results as short corollaries of the library

Each physical potential (in the variable `t = r²`) is completely monotone by a one- or two-line composition of
library lemmas, and then the triangular lattice minimises its energy among locally finite density-one planar
configurations by `ProgCM.triangular_optimal`, which is conditional on upstream's
`OAI.AtomicTriangular.universal_energy_minimum` (openai/math, AI-generated, not peer reviewed). When the raw
lattice energy is infinite (Coulomb-like tails such as Keldysh), the optimality corollary reads `⊤ ≤ ⊤`.
-/

namespace ProgCM

open Set Filter Topology MeasureTheory IsCompletelyMonotoneOn

/-- Riesz `t^{-s/2}` (energy `Σ r^{-s}`), `s ≥ 0`. -/
theorem riesz_cm {s : ℝ} (hs : 0 ≤ s) : IsCompletelyMonotoneOn (TriangularRiesz.riesz s) :=
  (rpow_neg (by linarith : 0 ≤ s / 2)).congr' fun _ _ => rfl

/-- **H2 as a corollary.** Planar Yukawa `e^{-κ r}/r` (`κ ≥ 0`): Riesz × (exp ∘ √). -/
theorem yukawa_cm {κ : ℝ} (hκ : 0 ≤ κ) : IsCompletelyMonotoneOn (AutoresearchYukawa.g κ) :=
  ((riesz_cm zero_le_one).mul (phi_cm hκ)).congr (AutoresearchYukawa.g_eqOn κ)

/-- **H1 as a corollary.** Bilayer dipolar exciton `2 (1/r - 1/√(r² + d²))`, every `d`: difference of a translate. -/
theorem dipolar_cm (d : ℝ) : IsCompletelyMonotoneOn (AutoresearchDipolar.g d) :=
  (((rpow_neg (by norm_num : (0 : ℝ) ≤ 1 / 2)).sub_comp_add_const (sq_nonneg d)).const_mul
    zero_le_two).congr' fun _ _ => rfl

/-- Screened multipole differences `r^{-s} - (r² + c)^{-s/2}`, `s ≥ 0`, `c ≥ 0`. -/
theorem shiftDiff_cm {s c : ℝ} (hs : 0 ≤ s) (hc : 0 ≤ c) :
    IsCompletelyMonotoneOn (fun t => TriangularRiesz.riesz s t - TriangularRiesz.riesz s (t + c)) :=
  (riesz_cm hs).sub_comp_add_const hc

/-- **H3L as a corollary of the weakened Laplace lemma** (only the `n = 0` integrability is used). -/
theorem keldysh_cm {r0 : ℝ} (hr0 : 0 < r0) : IsCompletelyMonotoneOn (AutoresearchKeldysh.keldysh r0) := by
  have D := AutoresearchKeldysh.keldysh_data hr0
  refine (laplace D.k_meas D.m_meas D.k_nonneg D.m_nonneg
    (fun c hc => by simpa using D.integrable 0 c hc)).congr' fun t _ => ?_
  simp only [AutoresearchKeldysh.keldysh]
  refine integral_congr_ae (Eventually.of_forall fun a => ?_)
  try simp only []
  rw [show -t / (4 * a) = -(t * (1 / (4 * a))) by ring]
  ring

/-- Gaussian-regularised Keldysh: product closure. -/
theorem keldyshReg_cm {r0 ε : ℝ} (hr0 : 0 < r0) (hε : 0 ≤ ε) :
    IsCompletelyMonotoneOn (AutoresearchKeldysh.keldyshReg r0 ε) :=
  ((keldysh_cm hr0).mul (exp_neg_mul hε)).congr' fun _ _ => rfl

/-- Finite-size (soft-core) Yukawa `e^{-κ √(r² + b²)} / √(r² + b²)`: translation closure. -/
theorem yukawa_softcore_cm {κ b : ℝ} (hκ : 0 ≤ κ) :
    IsCompletelyMonotoneOn (fun t => AutoresearchYukawa.g κ (t + b ^ 2)) :=
  (yukawa_cm hκ).comp_add_const (sq_nonneg b)

/-- Stretched exponential `e^{-a r^{2α}}` (`a ≥ 0`, `0 ≤ α ≤ 1`, i.e. `e^{-a t^α}`): subordination. -/
theorem stretchedExp_cm {a α : ℝ} (ha : 0 ≤ a) (h0 : 0 ≤ α) (h1 : α ≤ 1) :
    IsCompletelyMonotoneOn (fun t => Real.exp (-(a * t ^ α))) :=
  exp_neg_comp ha (IsBernsteinOn.rpow h0 h1) (fun _ ht => Real.rpow_pos_of_pos ht α)

/-- **Consistency with the earlier proofs.** The library and the H1/H2/H3L theorems agree (through the bridge). -/
theorem yukawa_admissible' {κ : ℝ} (hκ : 0 < κ) : OAI.AtomicTriangular.AdmissiblePotential (AutoresearchYukawa.g κ) :=
  (yukawa_cm hκ.le).admissible

theorem dipolar_admissible' (d : ℝ) : OAI.AtomicTriangular.AdmissiblePotential (AutoresearchDipolar.g d) :=
  (dipolar_cm d).admissible

/-- Triangular optimality for the soft-core Yukawa interaction (conditional on upstream). -/
theorem triangular_yukawa_softcore_optimal {κ b : ℝ} (hκ : 0 ≤ κ) (C : Set OAI.AtomicTriangular.Plane)
    (hC : OAI.AtomicTriangular.LocallyFinite C) (hd : OAI.AtomicTriangular.DensityOne C) :
    OAI.AtomicTriangular.latticeEnergy (fun t => AutoresearchYukawa.g κ (t + b ^ 2)) ≤
      OAI.AtomicTriangular.energy (fun t => AutoresearchYukawa.g κ (t + b ^ 2)) C :=
  triangular_optimal (yukawa_softcore_cm hκ) C hC hd

/-- Triangular optimality for the stretched exponential (conditional on upstream). -/
theorem triangular_stretchedExp_optimal {a α : ℝ} (ha : 0 ≤ a) (h0 : 0 ≤ α) (h1 : α ≤ 1)
    (C : Set OAI.AtomicTriangular.Plane) (hC : OAI.AtomicTriangular.LocallyFinite C)
    (hd : OAI.AtomicTriangular.DensityOne C) :
    OAI.AtomicTriangular.latticeEnergy (fun t => Real.exp (-(a * t ^ α))) ≤
      OAI.AtomicTriangular.energy (fun t => Real.exp (-(a * t ^ α))) C :=
  triangular_optimal (stretchedExp_cm ha h0 h1) C hC hd

end ProgCM

#print axioms ProgCM.riesz_cm
#print axioms ProgCM.yukawa_cm
#print axioms ProgCM.dipolar_cm
#print axioms ProgCM.shiftDiff_cm
#print axioms ProgCM.keldysh_cm
#print axioms ProgCM.keldyshReg_cm
#print axioms ProgCM.yukawa_softcore_cm
#print axioms ProgCM.stretchedExp_cm
#print axioms ProgCM.yukawa_admissible'
#print axioms ProgCM.dipolar_admissible'
#print axioms ProgCM.triangular_yukawa_softcore_optimal
#print axioms ProgCM.triangular_stretchedExp_optimal
