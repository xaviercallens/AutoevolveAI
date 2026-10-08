import BAOCert.Fit
import BAOCert.FitOm101
import BAOCert.EdS

/-! Axiom audit of every certified statement of pilot P1, and two planted negative controls (C3). -/

#print axioms BAOCert.seg_bounds
#print axioms BAOCert.chi_bounds
#print axioms BAOCert.Fit.tbl_check
#print axioms BAOCert.Fit.chi_z0295
#print axioms BAOCert.Fit.chi_z0510
#print axioms BAOCert.Fit.chi_z0706
#print axioms BAOCert.Fit.chi_z0934
#print axioms BAOCert.Fit.chi_z1321
#print axioms BAOCert.Fit.chi_z1484
#print axioms BAOCert.Fit.chi_z2330
#print axioms BAOCert.Fit.invE_z0510
#print axioms BAOCert.Fit.invE_z2330
#print axioms BAOCert.FitOm101.chi_z2330
#print axioms BAOCert.EdS.chi_z2330

-- C3 negative controls: both must show a non-whitelisted axiom.
theorem ctl_sorry : BAOCert.chi 1 1 = 0 := by sorry
axiom ctl_cheat : False
theorem ctl_axiom : BAOCert.chi 1 1 = 0 := ctl_cheat.elim
#print axioms ctl_sorry
#print axioms ctl_axiom
