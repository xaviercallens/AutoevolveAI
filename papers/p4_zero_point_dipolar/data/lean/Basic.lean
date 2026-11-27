import Programmes.ZeroPointPhys.Basic
import Mathlib.Tactic

/-!
# M1 (proposal 4, 2026-10-27): the triangular lattice is not a local minimum of the harmonic zero-point energy
# for the r⁻³ potentials (Riesz s = 3, bilayer point dipole), with Ewald-split tails

Same setting, logic and hypotheses as N2 (`Programmes.ZeroPointPhys.Basic`): `E(t)` is the harmonic zero-point energy
per particle (ħ = m = 1) of the unit-covolume lattice `P_t L_ρ`, `P_t = [[1, t], [t, 1 + t²]]`, for the stated radial
pair potential; `U` is N2's t-dependent comparison majorant. This file adds only the rational certificates produced by
`results/proposal4/2026-10-27/M1/code/m1_certify.py` (N2's certifier with an Ewald / Gaussian-mixture split of the
r⁻³ tail: short part in real space, long part in reciprocal space), and assembles them with N2's
`not_localMin_of_deriv_cert`.

The kernel checks the logic and the signs of the rational endpoints. The hypotheses of each final theorem are exactly
the inputs that are NOT kernel-checked: the Arb enclosure `U₂'' ≤ M ≤ M_hi` on the window (lattice sums, Poisson
summation of the long part, reciprocal-space bounds, tails, BZ integral: Tier C-ball and C-human), `E ≤ U` on the window
(positivity checks, Tier C-ball), `U(0) = E(0)`, the differentiability of `U` on the window, and the mirror symmetry.
A statement about the harmonic zero-point energy of a model crystal, not about any physical exciton system.
-/

namespace ProgZeroPointDipolar

open ProgZeroPointCert ProgZeroPointPhys

/-! ## Riesz `V = r⁻³`: `results/proposal4/2026-10-27/M1/data/riesz3.json`
(QMAX 300, Ewald split alpha = 1/10, N 64, depth 2, tol 0.5;
M ∈ [-3.17029, -1.66310]) -/

noncomputable def riesz3_M_hi : ℝ := -1663096717477 / 1000000000000
noncomputable def riesz3_lmin_lo : ℝ := 650921395421 / 100000000000
noncomputable def riesz3_lminu_lo : ℝ := 6504907980561 / 1000000000000
noncomputable def riesz3_qpd_lo : ℝ := 469635461457 / 250000000000

theorem riesz3_cert : riesz3_M_hi < 0 ∧ 0 < riesz3_lmin_lo ∧ 0 < riesz3_lminu_lo ∧ 0 < riesz3_qpd_lo := by
  refine ⟨?_, ?_, ?_, ?_⟩ <;> norm_num [riesz3_M_hi, riesz3_lmin_lo, riesz3_lminu_lo, riesz3_qpd_lo]

theorem riesz3_not_localMin_of_certificate (E U U1 U2pp : ℝ → ℝ) (M : ℝ)
    (hEU : ∀ t, |t| ≤ t0 → E t ≤ U t) (h0 : U 0 = E 0)
    (hd1 : ∀ u, |u| ≤ t0 → HasDerivAt U (U1 u) u) (hd2 : ∀ u, |u| ≤ t0 → HasDerivAt U1 (U2pp u) u)
    (hK : ∀ u, |u| ≤ t0 → U2pp u ≤ M) (hM : M ≤ riesz3_M_hi)
    (hsym : ∀ t, E (-t) = E t) :
    ¬ IsLocalMin E 0 ∧ ∀ t, 0 < t → t ≤ t0 → E t < E 0 :=
  not_localMin_of_deriv_cert E U U1 U2pp t0 M riesz3_M_hi t0_pos riesz3_cert.1 hM hEU h0 hd1 hd2 hK hsym

/-! ## bilayer point dipole `V = 2(1/r - 1/√(r² + d²))/d²`, d = 1/10: `results/proposal4/2026-10-27/M1/data/dipolar_d0.1.json`
(QMAX 300, Ewald split alpha = 1/10, N 64, depth 2, tol 0.5;
M ∈ [-3.33620, -1.85185]) -/

noncomputable def dip01_M_hi : ℝ := -925923850457 / 500000000000
noncomputable def dip01_lmin_lo : ℝ := 3192340414971 / 500000000000
noncomputable def dip01_lminu_lo : ℝ := 3190223518759 / 500000000000
noncomputable def dip01_qpd_lo : ℝ := 1850697979331 / 1000000000000

theorem dip01_cert : dip01_M_hi < 0 ∧ 0 < dip01_lmin_lo ∧ 0 < dip01_lminu_lo ∧ 0 < dip01_qpd_lo := by
  refine ⟨?_, ?_, ?_, ?_⟩ <;> norm_num [dip01_M_hi, dip01_lmin_lo, dip01_lminu_lo, dip01_qpd_lo]

theorem dipolar01_not_localMin_of_certificate (E U U1 U2pp : ℝ → ℝ) (M : ℝ)
    (hEU : ∀ t, |t| ≤ t0 → E t ≤ U t) (h0 : U 0 = E 0)
    (hd1 : ∀ u, |u| ≤ t0 → HasDerivAt U (U1 u) u) (hd2 : ∀ u, |u| ≤ t0 → HasDerivAt U1 (U2pp u) u)
    (hK : ∀ u, |u| ≤ t0 → U2pp u ≤ M) (hM : M ≤ dip01_M_hi)
    (hsym : ∀ t, E (-t) = E t) :
    ¬ IsLocalMin E 0 ∧ ∀ t, 0 < t → t ≤ t0 → E t < E 0 :=
  not_localMin_of_deriv_cert E U U1 U2pp t0 M dip01_M_hi t0_pos dip01_cert.1 hM hEU h0 hd1 hd2 hK hsym

/-! ## bilayer point dipole, d = 1/2: `results/proposal4/2026-10-27/M1/data/dipolar_d0.5.json`
(QMAX 300, Ewald split alpha = 1/10, N 64, depth 2, tol 0.5;
M ∈ [-5.38812, -4.11598]) -/

noncomputable def dip05_M_hi : ℝ := -4115980950373 / 1000000000000
noncomputable def dip05_lmin_lo : ℝ := 33156953461 / 7812500000
noncomputable def dip05_lminu_lo : ℝ := 848220618069 / 200000000000
noncomputable def dip05_qpd_lo : ℝ := 382246585097 / 250000000000

theorem dip05_cert : dip05_M_hi < 0 ∧ 0 < dip05_lmin_lo ∧ 0 < dip05_lminu_lo ∧ 0 < dip05_qpd_lo := by
  refine ⟨?_, ?_, ?_, ?_⟩ <;> norm_num [dip05_M_hi, dip05_lmin_lo, dip05_lminu_lo, dip05_qpd_lo]

theorem dipolar05_not_localMin_of_certificate (E U U1 U2pp : ℝ → ℝ) (M : ℝ)
    (hEU : ∀ t, |t| ≤ t0 → E t ≤ U t) (h0 : U 0 = E 0)
    (hd1 : ∀ u, |u| ≤ t0 → HasDerivAt U (U1 u) u) (hd2 : ∀ u, |u| ≤ t0 → HasDerivAt U1 (U2pp u) u)
    (hK : ∀ u, |u| ≤ t0 → U2pp u ≤ M) (hM : M ≤ dip05_M_hi)
    (hsym : ∀ t, E (-t) = E t) :
    ¬ IsLocalMin E 0 ∧ ∀ t, 0 < t → t ≤ t0 → E t < E 0 :=
  not_localMin_of_deriv_cert E U U1 U2pp t0 M dip05_M_hi t0_pos dip05_cert.1 hM hEU h0 hd1 hd2 hK hsym

/-! ## bilayer point dipole, d = 129/2000 (d/a ≈ 0.0600): `results/proposal4/2026-10-27/M1/data/dipolar_da0.06.json`
(QMAX 300, Ewald split alpha = 1/10, N 64, depth 2, tol 0.5;
M ∈ [-3.23699, -1.74649]) -/

noncomputable def dipA006_M_hi : ℝ := -1746491883211 / 1000000000000
noncomputable def dipA006_lmin_lo : ℝ := 1614237109199 / 250000000000
noncomputable def dipA006_lminu_lo : ℝ := 6452645696699 / 1000000000000
noncomputable def dipA006_qpd_lo : ℝ := 1866406079381 / 1000000000000

theorem dipA006_cert : dipA006_M_hi < 0 ∧ 0 < dipA006_lmin_lo ∧ 0 < dipA006_lminu_lo ∧ 0 < dipA006_qpd_lo := by
  refine ⟨?_, ?_, ?_, ?_⟩ <;> norm_num [dipA006_M_hi, dipA006_lmin_lo, dipA006_lminu_lo, dipA006_qpd_lo]

theorem dipolarA006_not_localMin_of_certificate (E U U1 U2pp : ℝ → ℝ) (M : ℝ)
    (hEU : ∀ t, |t| ≤ t0 → E t ≤ U t) (h0 : U 0 = E 0)
    (hd1 : ∀ u, |u| ≤ t0 → HasDerivAt U (U1 u) u) (hd2 : ∀ u, |u| ≤ t0 → HasDerivAt U1 (U2pp u) u)
    (hK : ∀ u, |u| ≤ t0 → U2pp u ≤ M) (hM : M ≤ dipA006_M_hi)
    (hsym : ∀ t, E (-t) = E t) :
    ¬ IsLocalMin E 0 ∧ ∀ t, 0 < t → t ≤ t0 → E t < E 0 :=
  not_localMin_of_deriv_cert E U U1 U2pp t0 M dipA006_M_hi t0_pos dipA006_cert.1 hM hEU h0 hd1 hd2 hK hsym

/-! ## bilayer point dipole, d = 967/10000 (d/a ≈ 0.0900): `results/proposal4/2026-10-27/M1/data/dipolar_da0.09.json`
(QMAX 300, Ewald split alpha = 1/10, N 64, depth 2, tol 0.5;
M ∈ [-3.32496, -1.84069]) -/

noncomputable def dipA009_M_hi : ℝ := -1840689150179 / 1000000000000
noncomputable def dipA009_lmin_lo : ℝ := 1598162775859 / 250000000000
noncomputable def dipA009_lminu_lo : ℝ := 3194205701351 / 500000000000
noncomputable def dipA009_qpd_lo : ℝ := 926217993721 / 500000000000

theorem dipA009_cert : dipA009_M_hi < 0 ∧ 0 < dipA009_lmin_lo ∧ 0 < dipA009_lminu_lo ∧ 0 < dipA009_qpd_lo := by
  refine ⟨?_, ?_, ?_, ?_⟩ <;> norm_num [dipA009_M_hi, dipA009_lmin_lo, dipA009_lminu_lo, dipA009_qpd_lo]

theorem dipolarA009_not_localMin_of_certificate (E U U1 U2pp : ℝ → ℝ) (M : ℝ)
    (hEU : ∀ t, |t| ≤ t0 → E t ≤ U t) (h0 : U 0 = E 0)
    (hd1 : ∀ u, |u| ≤ t0 → HasDerivAt U (U1 u) u) (hd2 : ∀ u, |u| ≤ t0 → HasDerivAt U1 (U2pp u) u)
    (hK : ∀ u, |u| ≤ t0 → U2pp u ≤ M) (hM : M ≤ dipA009_M_hi)
    (hsym : ∀ t, E (-t) = E t) :
    ¬ IsLocalMin E 0 ∧ ∀ t, 0 < t → t ≤ t0 → E t < E 0 :=
  not_localMin_of_deriv_cert E U U1 U2pp t0 M dipA009_M_hi t0_pos dipA009_cert.1 hM hEU h0 hd1 hd2 hK hsym

/-! ## bilayer point dipole, d = 1075/10000 (d/a ≈ 0.1000): `results/proposal4/2026-10-27/M1/data/dipolar_da0.1.json`
(QMAX 300, Ewald split alpha = 1/10, N 64, depth 2, tol 0.5;
M ∈ [-3.36115, -1.88023]) -/

noncomputable def dipA01_M_hi : ℝ := -1880226507233 / 1000000000000
noncomputable def dipA01_lmin_lo : ℝ := 318281757459 / 50000000000
noncomputable def dipA01_lminu_lo : ℝ := 3180707413703 / 500000000000
noncomputable def dipA01_qpd_lo : ℝ := 1846539203077 / 1000000000000

theorem dipA01_cert : dipA01_M_hi < 0 ∧ 0 < dipA01_lmin_lo ∧ 0 < dipA01_lminu_lo ∧ 0 < dipA01_qpd_lo := by
  refine ⟨?_, ?_, ?_, ?_⟩ <;> norm_num [dipA01_M_hi, dipA01_lmin_lo, dipA01_lminu_lo, dipA01_qpd_lo]

theorem dipolarA01_not_localMin_of_certificate (E U U1 U2pp : ℝ → ℝ) (M : ℝ)
    (hEU : ∀ t, |t| ≤ t0 → E t ≤ U t) (h0 : U 0 = E 0)
    (hd1 : ∀ u, |u| ≤ t0 → HasDerivAt U (U1 u) u) (hd2 : ∀ u, |u| ≤ t0 → HasDerivAt U1 (U2pp u) u)
    (hK : ∀ u, |u| ≤ t0 → U2pp u ≤ M) (hM : M ≤ dipA01_M_hi)
    (hsym : ∀ t, E (-t) = E t) :
    ¬ IsLocalMin E 0 ∧ ∀ t, 0 < t → t ≤ t0 → E t < E 0 :=
  not_localMin_of_deriv_cert E U U1 U2pp t0 M dipA01_M_hi t0_pos dipA01_cert.1 hM hEU h0 hd1 hd2 hK hsym

/-! ## bilayer point dipole, d = 5373/10000 (d/a ≈ 0.5000): `results/proposal4/2026-10-27/M1/data/dipolar_da0.5.json`
(QMAX 300, Ewald split alpha = 1/10, N 64, depth 2, tol 0.5;
M ∈ [-5.49473, -4.24958]) -/

noncomputable def dipA05_M_hi : ℝ := -2124789210489 / 500000000000
noncomputable def dipA05_lmin_lo : ℝ := 4007803566753 / 1000000000000
noncomputable def dipA05_lminu_lo : ℝ := 800991052389 / 200000000000
noncomputable def dipA05_qpd_lo : ℝ := 1500064127147 / 1000000000000

theorem dipA05_cert : dipA05_M_hi < 0 ∧ 0 < dipA05_lmin_lo ∧ 0 < dipA05_lminu_lo ∧ 0 < dipA05_qpd_lo := by
  refine ⟨?_, ?_, ?_, ?_⟩ <;> norm_num [dipA05_M_hi, dipA05_lmin_lo, dipA05_lminu_lo, dipA05_qpd_lo]

theorem dipolarA05_not_localMin_of_certificate (E U U1 U2pp : ℝ → ℝ) (M : ℝ)
    (hEU : ∀ t, |t| ≤ t0 → E t ≤ U t) (h0 : U 0 = E 0)
    (hd1 : ∀ u, |u| ≤ t0 → HasDerivAt U (U1 u) u) (hd2 : ∀ u, |u| ≤ t0 → HasDerivAt U1 (U2pp u) u)
    (hK : ∀ u, |u| ≤ t0 → U2pp u ≤ M) (hM : M ≤ dipA05_M_hi)
    (hsym : ∀ t, E (-t) = E t) :
    ¬ IsLocalMin E 0 ∧ ∀ t, 0 < t → t ≤ t0 → E t < E 0 :=
  not_localMin_of_deriv_cert E U U1 U2pp t0 M dipA05_M_hi t0_pos dipA05_cert.1 hM hEU h0 hd1 hd2 hK hsym

end ProgZeroPointDipolar

#print axioms ProgZeroPointDipolar.riesz3_cert
#print axioms ProgZeroPointDipolar.riesz3_not_localMin_of_certificate
#print axioms ProgZeroPointDipolar.dip01_cert
#print axioms ProgZeroPointDipolar.dipolar01_not_localMin_of_certificate
#print axioms ProgZeroPointDipolar.dip05_cert
#print axioms ProgZeroPointDipolar.dipolar05_not_localMin_of_certificate
#print axioms ProgZeroPointDipolar.dipA006_cert
#print axioms ProgZeroPointDipolar.dipolarA006_not_localMin_of_certificate
#print axioms ProgZeroPointDipolar.dipA009_cert
#print axioms ProgZeroPointDipolar.dipolarA009_not_localMin_of_certificate
#print axioms ProgZeroPointDipolar.dipA01_cert
#print axioms ProgZeroPointDipolar.dipolarA01_not_localMin_of_certificate
#print axioms ProgZeroPointDipolar.dipA05_cert
#print axioms ProgZeroPointDipolar.dipolarA05_not_localMin_of_certificate
