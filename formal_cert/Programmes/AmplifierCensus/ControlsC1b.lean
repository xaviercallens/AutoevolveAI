import Programmes.AmplifierCensus.Amplifiers11

/-!
# Controls for the C1b Lean certificates (nothing imports this file)

Real theorems (negative controls that the kernel must decide the RIGHT way):
* `ctlb_perturbed_vector_rejected`: one coalescence time of the A1 certificate changed by `1/D`: it no
  longer solves eq. (5) on `GA1`.
* `ctlb_wrong_graph_rejected`: the A1 certificate does not solve eq. (5) on `GA3` (A3 is A1 plus one
  edge), so a wrong transition matrix is caught.
* `ctlb_wrong_value_rejected`: the kernel refutes a wrong exact value (A1's N_eff replaced by A3's).

Planted FALSE claims (must be CAUGHT by the axiom audit, i.e. report `sorryAx` or `ctlb_cheat`):
* `ctlb_sorry`: A3's N_eff equals A1's.
* `ctlb_axiom`: Richter's printed rounded value 11.0952 is A1's exact N_eff.
-/

namespace AmplifierCensusControlsC1b

open AmplifierCensus

/-- The A1 certificate with entries (0,1) and (1,0) bumped by `1/D`. -/
def tauBadA1 (i j : Fin 11) : ℚ :=
  if (i.val = 0 ∧ j.val = 1) ∨ (i.val = 1 ∧ j.val = 0) then tauA1 i j + 1 / ((DA1 : ℤ) : ℚ)
  else tauA1 i j

theorem ctlb_perturbed_vector_rejected : ¬ Eq5 GA1 tauBadA1 := by
  unfold Eq5; decide +kernel

theorem ctlb_wrong_graph_rejected : ¬ Eq5 GA3 tauA1 := by
  unfold Eq5; decide +kernel

theorem ctlb_wrong_value_rejected : neff GA1 tauA1 ≠ 88175846355074579 / 8011935789939084 := by
  rw [neff_tauA1]; norm_num

theorem ctlb_sorry : neff GA3 tauA3 = 328435957 / 29601736 := sorry

axiom ctlb_cheat : False

theorem ctlb_axiom : neff GA1 tauA1 = 110952 / 10000 := ctlb_cheat.elim

end AmplifierCensusControlsC1b

#print axioms AmplifierCensusControlsC1b.ctlb_perturbed_vector_rejected
#print axioms AmplifierCensusControlsC1b.ctlb_wrong_graph_rejected
#print axioms AmplifierCensusControlsC1b.ctlb_wrong_value_rejected
#print axioms AmplifierCensusControlsC1b.ctlb_sorry
#print axioms AmplifierCensusControlsC1b.ctlb_axiom
