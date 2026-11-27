theorem ProgCM.ctl_sorry : ProgCM.IsCompletelyMonotoneOn Real.cos := sorry
axiom ProgCM.ctl_cheat : False
theorem ProgCM.ctl_axiom : ProgCM.IsCompletelyMonotoneOn Real.cos := ProgCM.ctl_cheat.elim
#print axioms ProgCM.ctl_sorry
#print axioms ProgCM.ctl_axiom
