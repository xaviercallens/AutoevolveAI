theorem ctl_sorry :
    Tendsto (fun t => sPow (bdK (fun _ => 1) Wstar 2) t {0} univ) atTop (𝓝 (4 / 7)) := -- proof elided

theorem ctl_axiom :
    Tendsto (fun t => (∑ v : Fin 3, sPow (bdK (fun _ => 1) Wstar 2) t {v} univ) / 3) atTop
      (𝓝 (4 / 7)) := -- proof elided

theorem ctl_axiom_lumpable :
    upP (fun _ => 1) Wcyc 2 {0, 1} = upP (fun _ => 1) Wcyc 2 {0, 2} := -- proof elided
