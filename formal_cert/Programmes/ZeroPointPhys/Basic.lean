import Programmes.ZeroPointCert.Basic
import Programmes.ZeroPointPhys.Taylor
import Mathlib.Tactic

/-!
# N2: the triangular lattice is not a local minimum of the harmonic zero-point energy (Yukawa potentials)

Setting (B2, `Programmes.ZeroPointCert.Basic`): `E(t)` is the harmonic zero-point energy per particle of the
unit-covolume lattice `P_t L_ρ`, `P_t = [[1, t], [t, 1 + t²]]`, for a radial pair potential `V`.

New against B2: the comparison matrix depends on `t`. With `X = D₀^{1/2}`, `Y` the solution of `X Y + Y X = ∂ₜD|₀`
and `X_t = X + t Y`, the pointwise inequality `2 tr D_t^{1/2} ≤ tr X_t + tr(X_t⁻¹ D_t)` is B2's
`two_trace_le_of_inverse` applied with `X := X_t` (positive definite on the window: ball-arithmetic check). The
majorant `U₂(t) = ¼ ∫ (tr X_t + tr X_t⁻¹ D_t) dκ` has `U₂(0) = E(0)` (`two_trace_eq_of_eq`) and the same curvature as
`E` at `0`. The window bound `U₂(t) + U₂(-t) - 2U₂(0) ≤ t² M` is derived inside Lean from `second_diff_le_of_deriv2_le`, given
`U₂' `, `U₂''` on `[-t₀, t₀]` (hypotheses: differentiation under the integral, Tier C-human) and `U₂''(u) ≤ M` for
every `|u| ≤ t₀`, where `M` is an Arb enclosure, valid for each fixed `u` in the window, of `¼ ∫ f_κ''(u) dκ`
(Tier C-ball, not kernel-checked).

The kernel checks: the logic, and the sign of the produced rational endpoints. The hypotheses of the final theorems
are exactly the inputs that are NOT kernel-checked (Tier C-ball and C-human), as in B2.
-/

namespace ProgZeroPointPhys

open ProgZeroPointCert

/-- Generic assembly: a majorant window bound with an upper endpoint `M_hi < 0` excludes a local minimum, and with
the mirror symmetry gives `E t < E 0` on the window. -/
theorem not_localMin_of_window_cert (E U : ℝ → ℝ) (t0 M M_hi : ℝ) (ht0 : 0 < t0) (hneg : M_hi < 0)
    (hM : M ≤ M_hi) (hEU : ∀ t, |t| ≤ t0 → E t ≤ U t) (h0 : U 0 = E 0)
    (hwin : ∀ t, 0 < t → t ≤ t0 → U t + U (-t) - 2 * U 0 ≤ t ^ 2 * M)
    (hsym : ∀ t, E (-t) = E t) :
    ¬ IsLocalMin E 0 ∧ ∀ t, 0 < t → t ≤ t0 → E t < E 0 := by
  have hB : M < 0 := lt_of_le_of_lt hM hneg
  exact ⟨not_isLocalMin_of_majorant ht0 hB hEU h0 hwin,
    fun t ht htt => lt_of_majorant_window_symm hB hEU h0 hwin hsym ht htt⟩

/-- The window bound from pointwise second-derivative bounds on `[-t₀, t₀]` (via `second_diff_le_of_deriv2_le`). -/
theorem window_of_deriv2 (U U1 U2pp : ℝ → ℝ) (t0 M : ℝ)
    (hd1 : ∀ u, |u| ≤ t0 → HasDerivAt U (U1 u) u) (hd2 : ∀ u, |u| ≤ t0 → HasDerivAt U1 (U2pp u) u)
    (hK : ∀ u, |u| ≤ t0 → U2pp u ≤ M) :
    ∀ t, 0 < t → t ≤ t0 → U t + U (-t) - 2 * U 0 ≤ t ^ 2 * M := by
  intro t ht htt
  have sub : ∀ u ∈ Set.Icc (-t) t, |u| ≤ t0 := fun u hu => abs_le.2 ⟨by linarith [hu.1], by linarith [hu.2]⟩
  exact second_diff_le_of_deriv2_le ht.le (fun u hu => hd1 u (sub u hu)) (fun u hu => hd2 u (sub u hu))
    (fun u hu => hK u (sub u hu))

/-- Generic assembly with the window bound derived in Lean from `U₂'' ≤ M` on the window. -/
theorem not_localMin_of_deriv_cert (E U U1 U2pp : ℝ → ℝ) (t0 M M_hi : ℝ) (ht0 : 0 < t0) (hneg : M_hi < 0)
    (hM : M ≤ M_hi) (hEU : ∀ t, |t| ≤ t0 → E t ≤ U t) (h0 : U 0 = E 0)
    (hd1 : ∀ u, |u| ≤ t0 → HasDerivAt U (U1 u) u) (hd2 : ∀ u, |u| ≤ t0 → HasDerivAt U1 (U2pp u) u)
    (hK : ∀ u, |u| ≤ t0 → U2pp u ≤ M) (hsym : ∀ t, E (-t) = E t) :
    ¬ IsLocalMin E 0 ∧ ∀ t, 0 < t → t ≤ t0 → E t < E 0 :=
  not_localMin_of_window_cert E U t0 M M_hi ht0 hneg hM hEU h0 (window_of_deriv2 U U1 U2pp t0 M hd1 hd2 hK) hsym

/-- A window certificate cannot be produced from data whose lower endpoint is positive. -/
theorem not_certifiable_of_lo_pos (M M_lo : ℝ) (hlo : 0 < M_lo) (hM : M_lo ≤ M) : ¬ M < 0 := by
  intro h
  linarith

/-! ## Yukawa `V = e^{-r}/r` (κ = 1): `results/proposal3/2026-10-26/N2/runs/o2_y1_merged.json`
(exact merge of `y1_partA.json`, `y1_partB.json`) -/

noncomputable def yuk1_M_hi : ℝ := -1018521206953 / 500000000000
noncomputable def yuk1_lmin_lo : ℝ := 438799291383 / 500000000000
noncomputable def yuk1_lminu_lo : ℝ := 218691342743 / 250000000000
noncomputable def yuk1_qpd_lo : ℝ := 165822978597 / 250000000000

theorem yuk1_cert : yuk1_M_hi < 0 ∧ 0 < yuk1_lmin_lo ∧ 0 < yuk1_lminu_lo ∧ 0 < yuk1_qpd_lo := by
  refine ⟨?_, ?_, ?_, ?_⟩ <;> norm_num [yuk1_M_hi, yuk1_lmin_lo, yuk1_lminu_lo, yuk1_qpd_lo]

/-- **N2, Yukawa κ = 1.** Same hypotheses as `yukawa2_not_localMin_of_certificate`, with `M ≤ yuk1_M_hi`. -/
theorem yukawa1_not_localMin_of_certificate (E U U1 U2pp : ℝ → ℝ) (M : ℝ)
    (hEU : ∀ t, |t| ≤ t0 → E t ≤ U t) (h0 : U 0 = E 0)
    (hd1 : ∀ u, |u| ≤ t0 → HasDerivAt U (U1 u) u) (hd2 : ∀ u, |u| ≤ t0 → HasDerivAt U1 (U2pp u) u)
    (hK : ∀ u, |u| ≤ t0 → U2pp u ≤ M) (hM : M ≤ yuk1_M_hi)
    (hsym : ∀ t, E (-t) = E t) :
    ¬ IsLocalMin E 0 ∧ ∀ t, 0 < t → t ≤ t0 → E t < E 0 :=
  not_localMin_of_deriv_cert E U U1 U2pp t0 M yuk1_M_hi t0_pos yuk1_cert.1 hM hEU h0 hd1 hd2 hK hsym

/-! ## Yukawa `V = e^{-2r}/r` (κ = 2): `results/proposal3/2026-10-26/N2/runs/o2_y2_N64.json` -/

noncomputable def yuk2_M_hi : ℝ := -1868541510831 / 1000000000000
noncomputable def yuk2_lmin_lo : ℝ := 27077389881 / 40000000000
noncomputable def yuk2_lminu_lo : ℝ := 135051100701 / 200000000000
noncomputable def yuk2_qpd_lo : ℝ := 57391246967 / 100000000000

theorem yuk2_cert : yuk2_M_hi < 0 ∧ 0 < yuk2_lmin_lo ∧ 0 < yuk2_lminu_lo ∧ 0 < yuk2_qpd_lo := by
  refine ⟨?_, ?_, ?_, ?_⟩ <;> norm_num [yuk2_M_hi, yuk2_lmin_lo, yuk2_lminu_lo, yuk2_qpd_lo]

/-- **N2, Yukawa κ = 2.** Hypotheses = the non-kernel-checked inputs (E ≤ U₂ on the window from the positivity
checks, U₂(0) = E(0), U₂ twice differentiable on the window with U₂'' = ¼∫f_κ'', the Arb bound
`U₂'' ≤ M ≤ yuk2_M_hi` on the window, mirror symmetry). -/
theorem yukawa2_not_localMin_of_certificate (E U U1 U2pp : ℝ → ℝ) (M : ℝ)
    (hEU : ∀ t, |t| ≤ t0 → E t ≤ U t) (h0 : U 0 = E 0)
    (hd1 : ∀ u, |u| ≤ t0 → HasDerivAt U (U1 u) u) (hd2 : ∀ u, |u| ≤ t0 → HasDerivAt U1 (U2pp u) u)
    (hK : ∀ u, |u| ≤ t0 → U2pp u ≤ M) (hM : M ≤ yuk2_M_hi)
    (hsym : ∀ t, E (-t) = E t) :
    ¬ IsLocalMin E 0 ∧ ∀ t, 0 < t → t ≤ t0 → E t < E 0 :=
  not_localMin_of_deriv_cert E U U1 U2pp t0 M yuk2_M_hi t0_pos yuk2_cert.1 hM hEU h0 hd1 hd2 hK hsym

/-! ## Positive control: Gaussian `V = e^{-π r²}` (B2's case), same code: `runs/o2_g1_N64d1.json` -/

noncomputable def gauss1_M_hi : ℝ := -357889170157 / 50000000000

theorem gauss1_cert : gauss1_M_hi < 0 := by norm_num [gauss1_M_hi]

theorem gauss1_not_localMin_of_certificate (E U U1 U2pp : ℝ → ℝ) (M : ℝ)
    (hEU : ∀ t, |t| ≤ t0 → E t ≤ U t) (h0 : U 0 = E 0)
    (hd1 : ∀ u, |u| ≤ t0 → HasDerivAt U (U1 u) u) (hd2 : ∀ u, |u| ≤ t0 → HasDerivAt U1 (U2pp u) u)
    (hK : ∀ u, |u| ≤ t0 → U2pp u ≤ M) (hM : M ≤ gauss1_M_hi)
    (hsym : ∀ t, E (-t) = E t) :
    ¬ IsLocalMin E 0 ∧ ∀ t, 0 < t → t ≤ t0 → E t < E 0 :=
  not_localMin_of_deriv_cert E U U1 U2pp t0 M gauss1_M_hi t0_pos gauss1_cert hM hEU h0 hd1 hd2 hK hsym

/-! ## Negative control: Gaussian `V = e^{-2π r²}` (a = 2; P2: triangular is a strict local minimum of E_zp):
`runs/negctl_g2_N64.json`, enclosure `M ∈ [gauss2_M_lo, gauss2_M_hi]` with `gauss2_M_lo > 0`. -/

noncomputable def gauss2_M_lo : ℝ := 172480128863 / 50000000000

theorem gauss2_not_certifiable (M : ℝ) (hM : gauss2_M_lo ≤ M) : ¬ M < 0 :=
  not_certifiable_of_lo_pos M gauss2_M_lo (by norm_num [gauss2_M_lo]) hM

end ProgZeroPointPhys

#print axioms ProgZeroPointPhys.not_localMin_of_window_cert
#print axioms ProgZeroPointPhys.not_certifiable_of_lo_pos
#print axioms ProgZeroPointPhys.window_of_deriv2
#print axioms ProgZeroPointPhys.not_localMin_of_deriv_cert
#print axioms ProgZeroPointPhys.yuk1_cert
#print axioms ProgZeroPointPhys.yukawa1_not_localMin_of_certificate
#print axioms ProgZeroPointPhys.yuk2_cert
#print axioms ProgZeroPointPhys.yukawa2_not_localMin_of_certificate
#print axioms ProgZeroPointPhys.gauss1_cert
#print axioms ProgZeroPointPhys.gauss1_not_localMin_of_certificate
#print axioms ProgZeroPointPhys.gauss2_not_certifiable
#print axioms ProgZeroPointPhys.second_diff_le_of_deriv2_le
