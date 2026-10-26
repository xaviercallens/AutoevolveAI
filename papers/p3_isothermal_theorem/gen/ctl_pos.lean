theorem wellMixed_up {n : ℕ} {r : ℝ} (hn : 0 < n) (hr : 0 < r) (S : Finset (Fin n)) :
    upP (fun _ => 1) (WH n) r S = moranUp n r S.card := -- proof elided

theorem wellMixed_down {n : ℕ} {r : ℝ} (hn : 0 < n) (hr : 0 < r) (S : Finset (Fin n)) :
    downP (fun _ => 1) (WH n) r S = moranDown n r S.card := -- proof elided

theorem wellMixed3_fixation :
    Tendsto (fun t => sPow (bdK (fun _ => 1) (WH 3) 2) t {0} univ) atTop (𝓝 (4 / 7)) := -- proof elided

theorem starStationary_fixation :
    Tendsto (fun t => sPow (bdK muStar Wstar 2) t {0} univ) atTop (𝓝 (4 / 7)) := -- proof elided
