import Programmes.ZeroPoint.Basic
import Mathlib.Topology.Order.LocalExtr
import Mathlib.Topology.MetricSpace.Pseudo.Defs
import Mathlib.Analysis.SpecialFunctions.ExpDeriv
import Mathlib.Tactic

/-!
# B2 (proposal 2, 2026-10-26): the triangular lattice is not a local minimum of the harmonic zero-point energy
# for the Gaussian `exp(-π r²)` — the kernel-checked part

Setting (fixed in `results/proposal2/2026-10-26/B2/CERTIFIED_CURVATURE.md`). `L_ρ` is the unit-covolume triangular
lattice with a lattice vector on the x axis, `P_t = [[1, t], [t, 1 + t²]]` (det 1, symmetric shear), `L_t = P_t L_ρ`,
`H_n(t) = Hess exp(-π |P_t R_n|²)`, `D_t(κ) = Σ_{n ≠ 0} (1 - cos 2π κ·n) H_n(t)` at fixed reduced `κ ∈ [-1/2,1/2]²`,
`E(t) = ½ ∫ tr D_t(κ)^{1/2} dκ` the harmonic zero-point energy of `L_t` (ħ = m = 1), and
`U(t) = ¼ ∫ [tr X + tr X⁻¹ D_t] dκ` with `X = D_0^{1/2}` (a majorant that is affine in `D_t`).

What is in this file (Tier A, all kernel-checked):

* `two_trace_le_of_inverse` : for symmetric `2×2` real `X, S` and `P = X⁻¹` positive definite,
  `2 tr S ≤ tr X + tr(P S²)`. With `S = D_t^{1/2}` this is the pointwise inequality `tr D^{1/2} ≤ ½(tr X + tr X⁻¹D)`
  behind `E ≤ U`; equality at `S = X` gives `U(0) = E(0)` (`two_trace_eq_of_eq`).
* `sum_lt_of_majorant_window`, `not_isLocalMin_of_majorant`, `lt_of_majorant_window_symm` : the logic. If `E ≤ U`
  on `[-t₀, t₀]`, `U(0) = E(0)` and `U(t) + U(-t) - 2U(0) ≤ t² B` with `B < 0` for `0 < t ≤ t₀`, then `0` is not a
  local minimum of `E`; if moreover `E(-t) = E(t)`, then `E(t) < E(0)` for every `0 < t ≤ t₀`.
* The rational certificate: `cert_B_neg` (`Upp0_hi + trW_hi · esum_hi < 0`), `cert_window` (monotonicity of that
  bound in its inputs), `cert_stability` (`lmin_lo - dB_hi > 0`).
* `triangular_not_localMin_of_certificate` : the assembled statement, with every analytic input as an explicit
  hypothesis.
* The closed form of the second `t`-derivative of the Gaussian weight along the path (`hasDerivAt_qS`,
  `hasDerivAt_q1S`, `hasDerivAt_gaussS`, `hasDerivAt_gaussS'`) and the product rule for one Hessian entry
  (`hasDerivAt_entry'`), which is the formula `hess_and_dd` of `b2_certify.py` evaluates in ball arithmetic. The
  Gaussian step reuses `ProgZeroPoint.gauss_f'`.

What is NOT kernel-checked (stated as hypotheses of `triangular_not_localMin_of_certificate`):
the Brillouin-zone integrals and lattice sums (`U''(0) ≤ Upp0_hi`, `∫ tr X⁻¹ ≤ trW_hi`, the perturbation bound
`esum_hi`, the tails), which are rigorous Arb ball-arithmetic enclosures (Tier C, machine interval arithmetic); and
the glue that `E`, `U` are the integrals above, that `E ≤ U` follows from `two_trace_le_of_inverse` pointwise, that
the window bound follows from the second-order mean-value theorem entrywise, and the mirror symmetry `E(-t) = E(t)`
(Tier C human arguments, written out in CERTIFIED_CURVATURE.md).
-/

namespace ProgZeroPointCert

open Real

/-! ## 1. The pointwise concavity inequality for `2×2` matrices -/

/-- `q(a, b) = p₁₁ a² + 2 p₁₂ a b + p₂₂ b²` is nonnegative for a positive definite `P`. -/
theorem quad_nonneg (p11 p12 p22 a b : ℝ) (hp : 0 < p11) (hdet : 0 ≤ p11 * p22 - p12 ^ 2) :
    0 ≤ p11 * a ^ 2 + 2 * p12 * a * b + p22 * b ^ 2 := by
  have h1 : p11 * (p11 * a ^ 2 + 2 * p12 * a * b + p22 * b ^ 2)
      = (p11 * a + p12 * b) ^ 2 + (p11 * p22 - p12 ^ 2) * b ^ 2 := by ring
  have h2 : 0 ≤ p11 * (p11 * a ^ 2 + 2 * p12 * a * b + p22 * b ^ 2) := by
    rw [h1]
    exact add_nonneg (sq_nonneg _) (mul_nonneg hdet (sq_nonneg b))
  by_contra hneg
  push Not at hneg
  have : p11 * (p11 * a ^ 2 + 2 * p12 * a * b + p22 * b ^ 2) < 0 := mul_neg_of_pos_of_neg hp hneg
  linarith

/-- **Concavity of `tr √·` in tangent form, `2×2`.** `X = [[x₁₁, x₁₂], [x₁₂, x₂₂]]`, `P = [[p₁₁, p₁₂], [p₁₂, p₂₂]]`
with `X P = I` and `P` positive definite, `S = [[s₁₁, s₁₂], [s₁₂, s₂₂]]` symmetric. Then
`2 tr S ≤ tr X + tr(P S²)`. (Proof: the difference is `tr(P (S - X)²) ≥ 0`.) -/
theorem two_trace_le_of_inverse (x11 x12 x22 p11 p12 p22 s11 s12 s22 : ℝ)
    (hp : 0 < p11) (hdet : 0 ≤ p11 * p22 - p12 ^ 2)
    (h11 : x11 * p11 + x12 * p12 = 1) (h12 : x11 * p12 + x12 * p22 = 0)
    (h21 : x12 * p11 + x22 * p12 = 0) (h22 : x12 * p12 + x22 * p22 = 1) :
    2 * (s11 + s22) ≤ (x11 + x22) +
      (p11 * (s11 ^ 2 + s12 ^ 2) + 2 * p12 * (s12 * (s11 + s22)) + p22 * (s12 ^ 2 + s22 ^ 2)) := by
  have key : (x11 + x22) +
      (p11 * (s11 ^ 2 + s12 ^ 2) + 2 * p12 * (s12 * (s11 + s22)) + p22 * (s12 ^ 2 + s22 ^ 2)) - 2 * (s11 + s22)
      = (p11 * (s11 - x11) ^ 2 + 2 * p12 * (s11 - x11) * (s12 - x12) + p22 * (s12 - x12) ^ 2)
        + (p11 * (s12 - x12) ^ 2 + 2 * p12 * (s12 - x12) * (s22 - x22) + p22 * (s22 - x22) ^ 2) := by
    linear_combination (2 * s11 - x11) * h11 + (2 * s12 - x12) * h12 + (2 * s12 - x12) * h21
      + (2 * s22 - x22) * h22
  have q1 := quad_nonneg p11 p12 p22 (s11 - x11) (s12 - x12) hp hdet
  have q2 := quad_nonneg p11 p12 p22 (s12 - x12) (s22 - x22) hp hdet
  linarith

/-- Equality case `S = X`: `2 tr X = tr X + tr(P X²)` when `X P = I` (so `U(0) = E(0)`). -/
theorem two_trace_eq_of_eq (x11 x12 x22 p11 p12 p22 : ℝ)
    (h11 : x11 * p11 + x12 * p12 = 1) (h12 : x11 * p12 + x12 * p22 = 0)
    (h21 : x12 * p11 + x22 * p12 = 0) (h22 : x12 * p12 + x22 * p22 = 1) :
    2 * (x11 + x22) = (x11 + x22) +
      (p11 * (x11 ^ 2 + x12 ^ 2) + 2 * p12 * (x12 * (x11 + x22)) + p22 * (x12 ^ 2 + x22 ^ 2)) := by
  linear_combination (-x11) * h11 + (-x12) * h12 + (-x12) * h21 + (-x22) * h22

/-! ## 2. The logic: a concave-majorant window bound excludes a local minimum -/

theorem sum_lt_of_majorant_window {E U : ℝ → ℝ} {t0 B : ℝ} (hB : B < 0)
    (hEU : ∀ t, |t| ≤ t0 → E t ≤ U t) (h0 : U 0 = E 0)
    (hU : ∀ t, 0 < t → t ≤ t0 → U t + U (-t) - 2 * U 0 ≤ t ^ 2 * B)
    {t : ℝ} (ht : 0 < t) (htt : t ≤ t0) : E t + E (-t) < 2 * E 0 := by
  have h1 := hEU t (by rw [abs_of_pos ht]; exact htt)
  have h2 := hEU (-t) (by rw [abs_neg, abs_of_pos ht]; exact htt)
  have h3 := hU t ht htt
  have h4 : t ^ 2 * B < 0 := mul_neg_of_pos_of_neg (by positivity) hB
  linarith

theorem not_isLocalMin_of_majorant {E U : ℝ → ℝ} {t0 B : ℝ} (ht0 : 0 < t0) (hB : B < 0)
    (hEU : ∀ t, |t| ≤ t0 → E t ≤ U t) (h0 : U 0 = E 0)
    (hU : ∀ t, 0 < t → t ≤ t0 → U t + U (-t) - 2 * U 0 ≤ t ^ 2 * B) : ¬ IsLocalMin E 0 := by
  intro hmin
  obtain ⟨ε, hε, hball⟩ := Metric.eventually_nhds_iff.1 hmin
  have ht : 0 < min (ε / 2) t0 := lt_min (by linarith) ht0
  have htt : min (ε / 2) t0 ≤ t0 := min_le_right _ _
  have htε : min (ε / 2) t0 < ε := lt_of_le_of_lt (min_le_left _ _) (by linarith)
  have a1 : E 0 ≤ E (min (ε / 2) t0) := hball (by rw [Real.dist_eq, sub_zero, abs_of_pos ht]; exact htε)
  have a2 : E 0 ≤ E (-(min (ε / 2) t0)) :=
    hball (by rw [Real.dist_eq, sub_zero, abs_neg, abs_of_pos ht]; exact htε)
  have := sum_lt_of_majorant_window hB hEU h0 hU ht htt
  linarith

theorem lt_of_majorant_window_symm {E U : ℝ → ℝ} {t0 B : ℝ} (hB : B < 0)
    (hEU : ∀ t, |t| ≤ t0 → E t ≤ U t) (h0 : U 0 = E 0)
    (hU : ∀ t, 0 < t → t ≤ t0 → U t + U (-t) - 2 * U 0 ≤ t ^ 2 * B)
    (hsym : ∀ t, E (-t) = E t) {t : ℝ} (ht : 0 < t) (htt : t ≤ t0) : E t < E 0 := by
  have := sum_lt_of_majorant_window hB hEU h0 hU ht htt
  rw [hsym t] at this
  linarith

/-! ## 3. The rational certificate (endpoints produced by `b2_certify.py`, Arb ball arithmetic, a = 1, shear path,
initial grid 64, adaptive depth 3, QMAX = 21, t₀ = 1/100000; values copied verbatim from
`results/proposal2/2026-10-26/B2/result.json`, `cert_rationals`) -/

/-- Window half-width. -/
noncomputable def t0 : ℝ := 1 / 100000
/-- Upper end of the enclosure of `U''(0) = ¼ ∫ tr(X⁻¹ ∂ₜ²D_t|₀) dκ`. -/
noncomputable def Upp0_hi : ℝ := -475041875131 / 250000000000
/-- Upper end of the enclosure of `∫ tr X⁻¹ dκ`. -/
noncomputable def trW_hi : ℝ := 366706720019 / 200000000000
/-- Upper end of `Σ_n Σ_entries sup_{|ξ| ≤ t₀} |H_n''(ξ) - H_n''(0)|` (all `n`, tail included). -/
noncomputable def esum_hi : ℝ := 31964165579 / 1000000000000
/-- Lower end of `min λ_min(D_0(κ)/s²)` over the Duffy cells, and upper end of the perturbation `‖B_t - B_0‖`. -/
noncomputable def lmin_lo : ℝ := 183777872659 / 200000000000
noncomputable def dB_hi : ℝ := 7528036227 / 1000000000000

theorem t0_pos : 0 < t0 := by norm_num [t0]

theorem cert_B_neg : Upp0_hi + trW_hi * esum_hi < 0 := by
  norm_num [Upp0_hi, trW_hi, esum_hi]

theorem cert_stability : 0 < lmin_lo - dB_hi := by
  norm_num [lmin_lo, dB_hi]

theorem cert_window (Upp0 trW esum : ℝ) (hU : Upp0 ≤ Upp0_hi) (hW0 : 0 ≤ trW) (hW : trW ≤ trW_hi)
    (he0 : 0 ≤ esum) (he : esum ≤ esum_hi) : Upp0 + trW * esum ≤ Upp0_hi + trW_hi * esum_hi := by
  have hWhi : 0 ≤ trW_hi := le_trans hW0 hW
  have := mul_le_mul hW he he0 hWhi
  linarith

/-- **B2, assembled.** Let `E` be the zero-point energy along the shear path and `U` the linear-response majorant.
Hypotheses (not kernel-checked, see the module doc): `E ≤ U` on the window, `U(0) = E(0)`, the second-difference
window bound with ball-arithmetic inputs `Upp0 ≤ Upp0_hi`, `0 ≤ trW ≤ trW_hi`, `0 ≤ esum ≤ esum_hi`, and the
mirror symmetry `E(-t) = E(t)`. Conclusion: `t = 0` (the triangular lattice) is not a local minimum of `E`, and
`E(t) < E(0)` for every `0 < t ≤ 1/100000`. -/
theorem triangular_not_localMin_of_certificate (E U : ℝ → ℝ) (Upp0 trW esum : ℝ)
    (hEU : ∀ t, |t| ≤ t0 → E t ≤ U t) (h0 : U 0 = E 0)
    (hwin : ∀ t, 0 < t → t ≤ t0 → U t + U (-t) - 2 * U 0 ≤ t ^ 2 * (Upp0 + trW * esum))
    (hU : Upp0 ≤ Upp0_hi) (hW0 : 0 ≤ trW) (hW : trW ≤ trW_hi) (he0 : 0 ≤ esum) (he : esum ≤ esum_hi)
    (hsym : ∀ t, E (-t) = E t) :
    ¬ IsLocalMin E 0 ∧ ∀ t, 0 < t → t ≤ t0 → E t < E 0 := by
  have hB : Upp0 + trW * esum < 0 := lt_of_le_of_lt (cert_window Upp0 trW esum hU hW0 hW he0 he) cert_B_neg
  exact ⟨not_isLocalMin_of_majorant t0_pos hB hEU h0 hwin,
    fun t ht htt => lt_of_majorant_window_symm hB hEU h0 hwin hsym ht htt⟩

/-! ## 4. The path derivatives used by the ball-arithmetic code (`hess_and_dd`, shear path) -/

/-- `|P_t R₀|²` for `R₀ = (X₀, Y₀)`, `P_t = [[1, t], [t, 1 + t²]]`. -/
def qS (X0 Y0 t : ℝ) : ℝ := (X0 + t * Y0) ^ 2 + (t * X0 + (1 + t ^ 2) * Y0) ^ 2
/-- `q' = 2 (R · R')`, `R' = (Y₀, X₀ + 2 t Y₀)`. -/
def q1S (X0 Y0 t : ℝ) : ℝ := 2 * ((X0 + t * Y0) * Y0 + (t * X0 + (1 + t ^ 2) * Y0) * (X0 + 2 * t * Y0))
/-- `q'' = 2 (|R'|² + R · R'')`, `R'' = (0, 2 Y₀)`. -/
def q2S (X0 Y0 t : ℝ) : ℝ := 2 * (Y0 ^ 2 + (X0 + 2 * t * Y0) ^ 2 + (t * X0 + (1 + t ^ 2) * Y0) * (2 * Y0))

theorem hasDerivAt_lin (X0 Y0 t : ℝ) : HasDerivAt (fun u : ℝ => X0 + u * Y0) Y0 t := by
  simpa using ((hasDerivAt_id t).mul_const Y0).const_add X0

theorem hasDerivAt_quad (X0 Y0 t : ℝ) :
    HasDerivAt (fun u : ℝ => u * X0 + (1 + u ^ 2) * Y0) (X0 + 2 * t * Y0) t := by
  have ha : HasDerivAt (fun u : ℝ => u * X0) X0 t := by
    simpa using (hasDerivAt_id t).mul_const X0
  have hb : HasDerivAt (fun u : ℝ => (1 + u ^ 2) * Y0) ((2 * t) * Y0) t := by
    have hp : HasDerivAt (fun u : ℝ => u ^ 2) (2 * t) t := by
      simpa using hasDerivAt_pow 2 t
    exact (hp.const_add 1).mul_const Y0
  exact (ha.add hb).congr_deriv (by ring)

theorem hasDerivAt_qS (X0 Y0 t : ℝ) : HasDerivAt (fun u => qS X0 Y0 u) (q1S X0 Y0 t) t := by
  have h1 := hasDerivAt_lin X0 Y0 t
  have h2 := hasDerivAt_quad X0 Y0 t
  have h : HasDerivAt (fun u => (X0 + u * Y0) * (X0 + u * Y0) + (u * X0 + (1 + u ^ 2) * Y0) * (u * X0 + (1 + u ^ 2) * Y0))
      (Y0 * (X0 + t * Y0) + (X0 + t * Y0) * Y0 + ((X0 + 2 * t * Y0) * (t * X0 + (1 + t ^ 2) * Y0)
        + (t * X0 + (1 + t ^ 2) * Y0) * (X0 + 2 * t * Y0))) t := (h1.mul h1).add (h2.mul h2)
  have hf : (fun u => qS X0 Y0 u)
      = (fun u => (X0 + u * Y0) * (X0 + u * Y0) + (u * X0 + (1 + u ^ 2) * Y0) * (u * X0 + (1 + u ^ 2) * Y0)) := by
    funext u
    simp only [qS]
    ring
  rw [hf]
  exact h.congr_deriv (by simp only [q1S]; ring)

theorem hasDerivAt_q1S (X0 Y0 t : ℝ) : HasDerivAt (fun u => q1S X0 Y0 u) (q2S X0 Y0 t) t := by
  have h1 := hasDerivAt_lin X0 Y0 t
  have h2 := hasDerivAt_quad X0 Y0 t
  have h3 : HasDerivAt (fun u : ℝ => X0 + 2 * u * Y0) (2 * Y0) t := by
    have h := ((hasDerivAt_id t).const_mul 2).mul_const Y0
    exact (h.const_add X0).congr_deriv (by simp)
  have h := ((h1.mul_const Y0).add (h2.mul h3)).const_mul 2
  exact h.congr_deriv (by simp only [q2S]; ring)

/-- The Gaussian weight `e(t) = exp(-π a q(t))` along the path: `e' = -π a q' e` (via `ProgZeroPoint.gauss_f'`). -/
theorem hasDerivAt_gaussS (a X0 Y0 t : ℝ) :
    HasDerivAt (fun u => Real.exp (-(Real.pi * a) * qS X0 Y0 u))
      (-(Real.pi * a) * q1S X0 Y0 t * Real.exp (-(Real.pi * a) * qS X0 Y0 t)) t := by
  have h := (ProgZeroPoint.gauss_f' a (qS X0 Y0 t)).comp t (hasDerivAt_qS X0 Y0 t)
  exact h.congr_deriv (by ring)

/-- `e'' = e (π² a² q'² - π a q'')`. -/
theorem hasDerivAt_gaussS' (a X0 Y0 t : ℝ) :
    HasDerivAt (fun u => -(Real.pi * a) * q1S X0 Y0 u * Real.exp (-(Real.pi * a) * qS X0 Y0 u))
      (Real.exp (-(Real.pi * a) * qS X0 Y0 t) *
        ((Real.pi * a) ^ 2 * q1S X0 Y0 t ^ 2 - Real.pi * a * q2S X0 Y0 t)) t := by
  have h := ((hasDerivAt_q1S X0 Y0 t).const_mul (-(Real.pi * a))).mul (hasDerivAt_gaussS a X0 Y0 t)
  exact h.congr_deriv (by ring)

/-- Product rule twice for one Hessian entry `H = e · M`: if `e' = e₁`, `e₁' = e₂`, `M' = M₁`, `M₁' = M₂`, then
`(e₁ M + e M₁)' = e₂ M + 2 e₁ M₁ + e M₂` (the formula `hess_and_dd` uses with `e₁ = -π a q' e`,
`e₂ = e (π² a² q'² - π a q'')`, and `M = 4π²a² RᵢRⱼ - 2π a δᵢⱼ`). -/
theorem hasDerivAt_entry' {e e1 M M1 : ℝ → ℝ} {e2 M2 t : ℝ} (he1 : HasDerivAt e1 e2 t) (hM : HasDerivAt M (M1 t) t)
    (he : HasDerivAt e (e1 t) t) (hM1 : HasDerivAt M1 M2 t) :
    HasDerivAt (fun u => e1 u * M u + e u * M1 u) (e2 * M t + 2 * e1 t * M1 t + e t * M2) t := by
  have h := (he1.mul hM).add (he.mul hM1)
  convert h using 1
  ring

end ProgZeroPointCert

#print axioms ProgZeroPointCert.quad_nonneg
#print axioms ProgZeroPointCert.two_trace_le_of_inverse
#print axioms ProgZeroPointCert.two_trace_eq_of_eq
#print axioms ProgZeroPointCert.sum_lt_of_majorant_window
#print axioms ProgZeroPointCert.not_isLocalMin_of_majorant
#print axioms ProgZeroPointCert.lt_of_majorant_window_symm
#print axioms ProgZeroPointCert.t0_pos
#print axioms ProgZeroPointCert.cert_B_neg
#print axioms ProgZeroPointCert.cert_stability
#print axioms ProgZeroPointCert.cert_window
#print axioms ProgZeroPointCert.triangular_not_localMin_of_certificate
#print axioms ProgZeroPointCert.hasDerivAt_lin
#print axioms ProgZeroPointCert.hasDerivAt_quad
#print axioms ProgZeroPointCert.hasDerivAt_qS
#print axioms ProgZeroPointCert.hasDerivAt_q1S
#print axioms ProgZeroPointCert.hasDerivAt_gaussS
#print axioms ProgZeroPointCert.hasDerivAt_gaussS'
#print axioms ProgZeroPointCert.hasDerivAt_entry'
