import Mathlib.Tactic

/-!
# Proposal 4, K2 (2026-10-31): algebraic core for the carbonate-alkalinity efficiency and the front-delay closed form

Statements about a stylised equilibrium carbonate model and about the Jessen et al. 2026 retardation formula, NOT about
the ocean or about soils. Interval enclosures of the transcendental constants (Weiss, Lueker, Dickson, Millero) are done
outside the kernel (Tier C); this file holds exact algebra.

* `eta_rewrite`: `N/D` and the dependency-reduced form `(h+2K2)/((h+4K2) + h^3 R/(C K1))` used by the interval code agree.
* `eta_pos`, `eta_lt_one`: for `h, K1, K2, C > 0` and `R >= 0`, `0 < eta < 1`.
* `eta_deriv_identity`: `N' D - N D' = A (2 A h^2 K2 + Q)` with the explicit `Q` (so the sign test used by the interval
  code to certify monotonicity in `h` is the right one).
* `Q_nonpos`: `Q <= 0` for nonnegative borate/water terms.
* `delay_*`: the front delay `T = (L/q)(eps_w + k CEC)` is monotone in CEC, L, k and antitone in q.
* `delay_via_R`: `T = L R / (q/eps_w)` with `R = 1 + (k/eps_w) CEC` for `dc` folded into `k`.
* `jessen_*`: exact rational instance with the printed Jessen inputs.
-/

namespace CarbonateK2

/-- eta as ratio N/D with `A = C K1 / h^4`-free explicit form. -/
noncomputable def etaND (C K1 K2 h R : ℝ) : ℝ :=
  (C * K1 * (h + 2 * K2) / h ^ 3) / (C * K1 * (h + 4 * K2) / h ^ 3 + R)

noncomputable def etaRW (C K1 K2 h R : ℝ) : ℝ :=
  (h + 2 * K2) / ((h + 4 * K2) + h ^ 3 * R / (C * K1))

theorem eta_rewrite {C K1 K2 h R : ℝ} (hC : 0 < C) (hK1 : 0 < K1) (hK2 : 0 < K2) (hh : 0 < h) (hR : 0 ≤ R) :
    etaND C K1 K2 h R = etaRW C K1 K2 h R := by
  unfold etaND etaRW
  have hCK : 0 < C * K1 := mul_pos hC hK1
  have hh3 : 0 < h ^ 3 := pow_pos hh 3
  have hd : 0 < (h + 4 * K2) + h ^ 3 * R / (C * K1) := by
    have : 0 ≤ h ^ 3 * R / (C * K1) := div_nonneg (mul_nonneg hh3.le hR) hCK.le
    linarith
  field_simp

theorem eta_pos {C K1 K2 h R : ℝ} (hC : 0 < C) (hK1 : 0 < K1) (hK2 : 0 < K2) (hh : 0 < h) (hR : 0 ≤ R) :
    0 < etaRW C K1 K2 h R := by
  unfold etaRW
  have hCK : 0 < C * K1 := mul_pos hC hK1
  have hh3 : 0 < h ^ 3 := pow_pos hh 3
  have : 0 ≤ h ^ 3 * R / (C * K1) := div_nonneg (mul_nonneg hh3.le hR) hCK.le
  apply div_pos <;> linarith

theorem eta_lt_one {C K1 K2 h R : ℝ} (hC : 0 < C) (hK1 : 0 < K1) (hK2 : 0 < K2) (hh : 0 < h) (hR : 0 ≤ R) :
    etaRW C K1 K2 h R < 1 := by
  unfold etaRW
  have hCK : 0 < C * K1 := mul_pos hC hK1
  have hh3 : 0 < h ^ 3 := pow_pos hh 3
  have : 0 ≤ h ^ 3 * R / (C * K1) := div_nonneg (mul_nonneg hh3.le hR) hCK.le
  have hd : 0 < (h + 4 * K2) + h ^ 3 * R / (C * K1) := by linarith
  rw [div_lt_one hd]
  linarith

/-- The derivative identity behind the monotonicity test (all quantities as plain reals).
`A = C K1 / h^4`, `R = RB + RW + 1`, `R' = -2 RB/(KB+h) - 2 RW/h`. -/
theorem eta_deriv_identity {A h K2 KB RB RW : ℝ} (hh : 0 < h) (hKB : 0 < KB) :
    let N := A * h * (h + 2 * K2)
    let Np := -A * (2 * h + 6 * K2)
    let D := A * h * (h + 4 * K2) + (RB + RW + 1)
    let Dp := -A * (2 * h + 12 * K2) + (-2 * RB / (KB + h) - 2 * RW / h)
    let Q := -(RB * (2 * h * K2 + 2 * h * KB + 6 * K2 * KB) / (KB + h) + 2 * K2 * RW + 2 * h + 6 * K2)
    Np * D - N * Dp = A * (2 * A * h ^ 2 * K2 + Q) := by
  intro N Np D Dp Q
  have hKh : 0 < KB + h := by linarith
  simp only [N, Np, D, Dp, Q]
  field_simp
  ring

theorem Q_nonpos {h K2 KB RB RW : ℝ} (hh : 0 < h) (hK2 : 0 < K2) (hKB : 0 < KB) (hRB : 0 ≤ RB) (hRW : 0 ≤ RW) :
    -(RB * (2 * h * K2 + 2 * h * KB + 6 * K2 * KB) / (KB + h) + 2 * K2 * RW + 2 * h + 6 * K2) ≤ 0 := by
  have hKh : 0 < KB + h := by linarith
  have h1 : 0 ≤ RB * (2 * h * K2 + 2 * h * KB + 6 * K2 * KB) / (KB + h) := by positivity
  have h2 : 0 ≤ 2 * K2 * RW := by positivity
  linarith

/-- Front delay time for depth `L`, Darcy flux `q`, water content `ew`, `k = 10 Δβ (1-ε) ρ / dc`, exchange capacity `cec`. -/
noncomputable def delay (L q ew k cec : ℝ) : ℝ := L / q * (ew + k * cec)

theorem delay_mono_cec {L q ew k c1 c2 : ℝ} (hL : 0 < L) (hq : 0 < q) (hk : 0 ≤ k) (h : c1 ≤ c2) :
    delay L q ew k c1 ≤ delay L q ew k c2 := by
  unfold delay
  have : 0 < L / q := div_pos hL hq
  apply mul_le_mul_of_nonneg_left _ this.le
  nlinarith

theorem delay_mono_L {L1 L2 q ew k cec : ℝ} (hq : 0 < q) (hpos : 0 ≤ ew + k * cec) (h : L1 ≤ L2) :
    delay L1 q ew k cec ≤ delay L2 q ew k cec := by
  unfold delay
  apply mul_le_mul_of_nonneg_right _ hpos
  exact div_le_div_of_nonneg_right h hq.le

theorem delay_anti_q {L q1 q2 ew k cec : ℝ} (hL : 0 ≤ L) (hq1 : 0 < q1) (hpos : 0 ≤ ew + k * cec) (h : q1 ≤ q2) :
    delay L q2 ew k cec ≤ delay L q1 ew k cec := by
  unfold delay
  apply mul_le_mul_of_nonneg_right _ hpos
  exact div_le_div_of_nonneg_left hL hq1 h

theorem delay_mono_k {L q ew k1 k2 cec : ℝ} (hL : 0 < L) (hq : 0 < q) (hc : 0 ≤ cec) (h : k1 ≤ k2) :
    delay L q ew k1 cec ≤ delay L q ew k2 cec := by
  unfold delay
  have : 0 < L / q := div_pos hL hq
  apply mul_le_mul_of_nonneg_left _ this.le
  nlinarith

/-- `T = L R / v` with `v = q/ew` and `R = 1 + (k/ew) cec` (the `dq/dc` of Jessen with `dc` folded into `k`). -/
theorem delay_via_R {L q ew k cec : ℝ} (hq : q ≠ 0) (hew : ew ≠ 0) :
    delay L q ew k cec = L * (1 + k / ew * cec) / (q / ew) := by
  unfold delay
  field_simp

/-- Jessen et al. printed inputs (exact rationals): `Δβ = 0.44`, `ε = 0.3`, `ρ = 2.65`, `ε_w = 0.1`, `dc = 0.8`,
`v = 5 m/yr`. `dq = 10 Δβ CEC (1-ε) ρ / ε_w`, `R = 1 + dq/dc`. -/
def retard (cec : ℚ) : ℚ := 1 + (10 * (44 / 100) * cec * (1 - 3 / 10) * (265 / 100) / (1 / 10)) / (8 / 10)

theorem jessen_R_sum : 58 < retard (56 / 100) ∧ retard (56 / 100) < 59 := by
  unfold retard; norm_num

theorem jessen_R_direct : 164 < retard (16 / 10) ∧ retard (16 / 10) < 165 := by
  unfold retard; norm_num

theorem jessen_yr_per_m_sum : 11 < retard (56 / 100) / 5 ∧ retard (56 / 100) / 5 < 12 := by
  unfold retard; norm_num

theorem jessen_yr_per_m_direct : 32 < retard (16 / 10) / 5 ∧ retard (16 / 10) / 5 < 33 := by
  unfold retard; norm_num

end CarbonateK2

#print axioms CarbonateK2.eta_rewrite
#print axioms CarbonateK2.eta_pos
#print axioms CarbonateK2.eta_lt_one
#print axioms CarbonateK2.eta_deriv_identity
#print axioms CarbonateK2.Q_nonpos
#print axioms CarbonateK2.delay_mono_cec
#print axioms CarbonateK2.delay_mono_L
#print axioms CarbonateK2.delay_anti_q
#print axioms CarbonateK2.delay_mono_k
#print axioms CarbonateK2.delay_via_R
#print axioms CarbonateK2.jessen_R_sum
#print axioms CarbonateK2.jessen_R_direct
#print axioms CarbonateK2.jessen_yr_per_m_sum
#print axioms CarbonateK2.jessen_yr_per_m_direct
