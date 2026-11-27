import Programmes.ZeroPointCert.Basic

/-!
# B2 planted controls (must be CAUGHT by the axiom gate; never import this file)

* `ctl_sorry`, `ctl_axiom` "prove" the tampered certificate (sign of `Upp0_hi` flipped), which is false. The file
  compiles with rc 0; only `#print axioms` exposes `sorryAx`, resp. `ProgZeroPointCert.ctl_cheat`.
* `tampered_false` (honest): the tampered inequality is false.
* `a2_not_certifiable` (honest, negative control a = 2): the a = 2 ball-arithmetic run encloses
  `U''(0) ≥ Upp0_lo_a2 = 3173413321863/250000000000 > 0`; then for every admissible `trW, esum ≥ 0` the window
  bound `Upp0 + trW * esum` is positive, so the a = 2 data can never produce the B2 certificate.
-/

namespace ProgZeroPointCert

theorem ctl_sorry : (475041875131 / 250000000000 : ℝ) + trW_hi * esum_hi < 0 := sorry

axiom ctl_cheat : False

theorem ctl_axiom : (475041875131 / 250000000000 : ℝ) + trW_hi * esum_hi < 0 := ctl_cheat.elim

theorem tampered_false : ¬ ((475041875131 / 250000000000 : ℝ) + trW_hi * esum_hi < 0) := by
  norm_num [trW_hi, esum_hi]

/-- Lower end of the a = 2 enclosure of `U''(0)` (`run_a2_shear_negctl.json`, `cert_rationals.Upp0_lo`). -/
noncomputable def Upp0_lo_a2 : ℝ := 3173413321863 / 250000000000

theorem a2_not_certifiable (Upp0 trW esum : ℝ) (hU : Upp0_lo_a2 ≤ Upp0) (hW : 0 ≤ trW) (he : 0 ≤ esum) :
    ¬ (Upp0 + trW * esum < 0) := by
  have h1 : (0 : ℝ) < Upp0_lo_a2 := by norm_num [Upp0_lo_a2]
  have h2 : 0 ≤ trW * esum := mul_nonneg hW he
  intro h
  linarith

end ProgZeroPointCert

#print axioms ProgZeroPointCert.ctl_sorry
#print axioms ProgZeroPointCert.ctl_axiom
#print axioms ProgZeroPointCert.tampered_false
#print axioms ProgZeroPointCert.a2_not_certifiable
