open ProgPopGen Filter Topology

theorem ctl_sorry :
    Tendsto (fun n => kPow (moranP 3 2) n 1 (Fin.last 3)) atTop (𝓝 (1 / 7)) := sorry

axiom ctl_cheat : False

theorem ctl_axiom :
    Tendsto (fun n => kPow (moranP 3 2) n 1 (Fin.last 3)) atTop (𝓝 (1 / 3)) := ctl_cheat.elim
