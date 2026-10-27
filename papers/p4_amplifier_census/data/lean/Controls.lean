import Programmes.AmplifierCensus.Richter11

/-!
# Controls for the C1 Lean certificate (nothing imports this file)

Real theorems (negative controls that the kernel must decide the RIGHT way):
* `ctl_perturbed_vector_rejected`: one coalescence time of the certificate changed by `1/D`: it no
  longer solves eq. (5) on `GR11`.
* `ctl_perturbed_graph_rejected`: the certificate vector does not solve eq. (5) on the *parent*
  graph `GP11` (the graph with the edge put back): a wrong transition matrix is caught.
* `ctl_parent_not_amplifier`: on the parent, `¬ 11 < N_eff` for every solution.

Planted FALSE claims (must be CAUGHT by the axiom audit, i.e. report `sorryAx` or `ctl_cheat`):
* `ctl_sorry`: the parent quartic graph is an amplifier of weak selection.
* `ctl_axiom`: Richter's printed rounded value 11.0008 is the exact N_eff.
-/

namespace AmplifierCensusControls

open AmplifierCensus

/-- The certificate with entry (0,1) and (1,0) bumped by `1/D`. -/
def tauBad (i j : Fin 11) : ℚ :=
  if (i.val = 0 ∧ j.val = 1) ∨ (i.val = 1 ∧ j.val = 0) then tauR11 i j + 1 / ((DR11 : ℤ) : ℚ)
  else tauR11 i j

theorem ctl_perturbed_vector_rejected : ¬ Eq5 GR11 tauBad := by
  unfold Eq5; decide +kernel

theorem ctl_perturbed_graph_rejected : ¬ Eq5 GP11 tauR11 := by
  unfold Eq5; decide +kernel

theorem ctl_parent_not_amplifier (τ : Fin 11 → Fin 11 → ℚ) (hτ : Eq5 GP11 τ) :
    ¬ (11 : ℚ) < neff GP11 τ := by
  rw [P11_isothermal τ hτ]; norm_num

theorem ctl_sorry : (11 : ℚ) < neff GP11 tauP11 := sorry

axiom ctl_cheat : False

theorem ctl_axiom : neff GR11 tauR11 = 110008 / 10000 := ctl_cheat.elim

end AmplifierCensusControls

#print axioms AmplifierCensusControls.ctl_perturbed_vector_rejected
#print axioms AmplifierCensusControls.ctl_perturbed_graph_rejected
#print axioms AmplifierCensusControls.ctl_parent_not_amplifier
#print axioms AmplifierCensusControls.ctl_sorry
#print axioms AmplifierCensusControls.ctl_axiom
