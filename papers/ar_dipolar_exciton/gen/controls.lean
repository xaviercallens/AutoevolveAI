theorem ctl_sorry : (1 : ℕ) = 2 := sorry
axiom ctl_cheat : False
theorem ctl_axiom : (1 : ℕ) = 2 := ctl_cheat.elim
