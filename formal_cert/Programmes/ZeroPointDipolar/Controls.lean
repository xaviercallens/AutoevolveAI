import Programmes.ZeroPointPhys.Basic

/-!
# M1 controls (separate from the certificate module `Programmes.ZeroPointDipolar.Basic`)

* Negative control (honest theorem): the Gaussian `a = 2` enclosure produced by the M1 certifier
  (`results/proposal4/2026-10-27/M1/data/negctl_gauss2.json`, bit-identical to N2's `runs/negctl_g2_N64.json`)
  has a positive lower endpoint, so no window certificate can be built from it.
* Axiom-gate controls: `ctl_sorry` and `ctl_axiom` compile (rc 0) but `#print axioms` must expose `sorryAx` and the
  planted axiom `ProgZeroPointDipolarCtl.ctl_cheat`; the gate rejects both.
-/

namespace ProgZeroPointDipolarCtl

open ProgZeroPointPhys

noncomputable def m1_gauss2_M_lo : ℝ := 172480128863 / 50000000000

theorem m1_gauss2_not_certifiable (M : ℝ) (hM : m1_gauss2_M_lo ≤ M) : ¬ M < 0 :=
  not_certifiable_of_lo_pos M m1_gauss2_M_lo (by norm_num [m1_gauss2_M_lo]) hM

theorem ctl_sorry : (4463084749303 / 1000000000000 : ℝ) < 0 := by
  sorry

axiom ctl_cheat : (4463084749303 / 1000000000000 : ℝ) < 0

theorem ctl_axiom : (4463084749303 / 1000000000000 : ℝ) < 0 := ctl_cheat

end ProgZeroPointDipolarCtl

#print axioms ProgZeroPointDipolarCtl.m1_gauss2_not_certifiable
#print axioms ProgZeroPointDipolarCtl.ctl_sorry
#print axioms ProgZeroPointDipolarCtl.ctl_axiom
