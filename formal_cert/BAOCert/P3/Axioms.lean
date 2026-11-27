import BAOCert.P3.Main

/-! Axiom audit of the P3 results, C8 evaluation of the certified r_d at one point, and planted controls (C11). -/

#print axioms BAOCert.P3.H0_ge_73_excluded
#print axioms BAOCert.P3.H0_ge_73_delta_chi2
#print axioms BAOCert.P3.Point.chi2tot_point
#print axioms BAOCert.H0.rdIv_mem
#print axioms BAOCert.H0.K_le
#print axioms BAOCert.H0.chi2DESI_nonneg
#print axioms BAOCert.P3.Box_000.box
#print axioms BAOCert.P3.Box_088.box
#print axioms ANSE.BAOBBNH0.hrd_strictMonoOn_h

-- C8: the certified r_d bracket at (omega_cb, omega_b) = (0.3 * 0.73^2 - 0.000642, 0.02218) (evaluation only)
#eval let I := BAOCert.H0.rdIv (3 / 10 * (73 / 100) ^ 2 - 107 / 10000 * (6 / 100)) (2218 / 100000) 2 5 60 25
  (toString (I.lo.num) ++ "/" ++ toString I.lo.den, toString (I.hi.num) ++ "/" ++ toString I.hi.den)

-- C11 planted controls
theorem ctl_sorry : BAOCert.H0.chi2tot 0 1 0 = 0 := by sorry
axiom ctl_cheat : False
theorem ctl_axiom : BAOCert.H0.chi2tot 0 1 0 = 0 := ctl_cheat.elim
#print axioms ctl_sorry
#print axioms ctl_axiom
