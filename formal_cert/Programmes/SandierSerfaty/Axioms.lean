import Programmes.SandierSerfaty.IV
import Programmes.SandierSerfaty.Constants
import Programmes.SandierSerfaty.Asserts
import Programmes.SandierSerfaty.CalcKPilot
import Programmes.SandierSerfaty.SignedEndpoints

/-! Axiom audit of every A1 theorem (proposal 2, 2026-10-26). Whitelist: `propext`, `Classical.choice`, `Quot.sound`. -/

#print axioms ProgSandierSerfaty.Cert.Q_eq
#print axioms ProgSandierSerfaty.Cert.IV.add_sound
#print axioms ProgSandierSerfaty.Cert.IV.neg_sound
#print axioms ProgSandierSerfaty.Cert.IV.sub_sound
#print axioms ProgSandierSerfaty.Cert.IV.mul_sound
#print axioms ProgSandierSerfaty.Cert.IV.invPos_sound
#print axioms ProgSandierSerfaty.Cert.IV.inv_sound
#print axioms ProgSandierSerfaty.Cert.IV.div_sound
#print axioms ProgSandierSerfaty.Cert.IV.rat_sound
#print axioms ProgSandierSerfaty.Cert.IV.ofInt_sound
#print axioms ProgSandierSerfaty.Cert.IV.hull_sound_left
#print axioms ProgSandierSerfaty.Cert.ln2_comp_eq
#print axioms ProgSandierSerfaty.Cert.pi_comp_eq
#print axioms ProgSandierSerfaty.Cert.p_comp_eq
#print axioms ProgSandierSerfaty.Cert.R_comp_eq
#print axioms ProgSandierSerfaty.Cert.a_comp_eq
#print axioms ProgSandierSerfaty.Cert.log_two_mem
#print axioms ProgSandierSerfaty.Cert.pi_mem
#print axioms ProgSandierSerfaty.Cert.p_mem
#print axioms ProgSandierSerfaty.Cert.R_mem
#print axioms ProgSandierSerfaty.Cert.a_mem
#print axioms ProgSandierSerfaty.Cert.printed_pairs
#print axioms ProgSandierSerfaty.Cert.rat_consts_eq
#print axioms ProgSandierSerfaty.Cert.cpp_asserts
#print axioms ProgSandierSerfaty.Cert.grid_margins
#print axioms ProgSandierSerfaty.Cert.lambda_real
#print axioms ProgSandierSerfaty.Cert.K_real
#print axioms ProgSandierSerfaty.Cert.fl_real
#print axioms ProgSandierSerfaty.Cert.slope_real
#print axioms ProgSandierSerfaty.Cert.gmf_real
#print axioms ProgSandierSerfaty.Cert.neglhs_real
#print axioms ProgSandierSerfaty.Cert.calcK_G0
#print axioms ProgSandierSerfaty.Cert.calcK_G1
#print axioms ProgSandierSerfaty.Cert.calcK_G2
#print axioms ProgSandierSerfaty.Cert.calcK_G3
#print axioms ProgSandierSerfaty.Cert.calcK_G4
#print axioms ProgSandierSerfaty.Cert.calcK_G5
#print axioms ProgSandierSerfaty.Cert.calcK_G6
#print axioms ProgSandierSerfaty.Cert.calcK_G7
#print axioms ProgSandierSerfaty.Reduction.gPrim_neg
#print axioms ProgSandierSerfaty.Reduction.integral_ge_of_negPart
#print axioms ProgSandierSerfaty.Reduction.signed_endpoints
#print axioms ProgSandierSerfaty.Reduction.assembly_algebra
#print axioms ProgSandierSerfaty.Reduction.b_lt_dstar
