theorem star_bias :
    upP (fun _ => 1) Wstar 2 {0} = 1 / 2 ∧ downP (fun _ => 1) Wstar 2 {0} = 1 / 2 ∧
    upP (fun _ => 1) Wstar 2 {0} ≠ 2 * downP (fun _ => 1) Wstar 2 {0} := -- proof elided

theorem star_fixation_centre :
    Tendsto (fun t => sPow (bdK (fun _ => 1) Wstar 2) t {0} univ) atTop (𝓝 (5 / 12)) := -- proof elided

theorem star_fixation_leaf :
    Tendsto (fun t => sPow (bdK (fun _ => 1) Wstar 2) t {1} univ) atTop (𝓝 (2 / 3)) := -- proof elided

theorem star_fixation_uniform :
    Tendsto (fun t => (∑ v : Fin 3, sPow (bdK (fun _ => 1) Wstar 2) t {v} univ) / 3) atTop
      (𝓝 (7 / 12)) := -- proof elided

theorem star_ne_moran : (5 / 12 : ℝ) ≠ moranFix 3 2 1 ∧ (7 / 12 : ℝ) ≠ moranFix 3 2 1 ∧
    (2 / 3 : ℝ) ≠ moranFix 3 2 1 := -- proof elided
