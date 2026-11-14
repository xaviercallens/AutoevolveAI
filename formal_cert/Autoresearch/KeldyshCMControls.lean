import Autoresearch.KeldyshCM

/-! Planted controls for the H3L gate: both must be caught by `#print axioms`.
They live only in this file, never in the claimed module `Autoresearch.KeldyshCM`. -/

namespace AutoresearchKeldyshControls

open AutoresearchKeldysh OAI.AtomicTriangular

/-- Planted `sorry`: a false claim (the signed mixture is admissible), closed by `sorry`. -/
theorem ctl_sorry : AdmissiblePotential signedMix := sorry

axiom ctl_cheat : False

/-- Planted axiom: the same false claim, closed by a smuggled axiom. -/
theorem ctl_axiom : AdmissiblePotential signedMix := ctl_cheat.elim

end AutoresearchKeldyshControls

#print axioms AutoresearchKeldyshControls.ctl_sorry
#print axioms AutoresearchKeldyshControls.ctl_axiom
#print axioms AutoresearchKeldysh.laplace_admissible
#print axioms AutoresearchKeldysh.keldysh_admissible
#print axioms AutoresearchKeldysh.triangular_keldysh_optimal
#print axioms AutoresearchKeldysh.keldyshReg_admissible
#print axioms AutoresearchKeldysh.signedMix_not_admissible
