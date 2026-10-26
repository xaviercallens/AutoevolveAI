noncomputable def Wcyc : Fin 4 → Fin 4 → ℝ :=
  ![![0, 1 / 2, 0, 1 / 2], ![1 / 2, 0, 1 / 2, 0], ![0, 1 / 2, 0, 1 / 2], ![1 / 2, 0, 1 / 2, 0]]

theorem cycle4_not_lumpable :
    ({0, 1} : Finset (Fin 4)).card = ({0, 2} : Finset (Fin 4)).card ∧
    upP (fun _ => 1) Wcyc 2 {0, 1} = 1 / 3 ∧ upP (fun _ => 1) Wcyc 2 {0, 2} = 2 / 3 ∧
    upP (fun _ => 1) Wcyc 2 {0, 1} = 2 * downP (fun _ => 1) Wcyc 2 {0, 1} ∧
    upP (fun _ => 1) Wcyc 2 {0, 2} = 2 * downP (fun _ => 1) Wcyc 2 {0, 2} := -- proof elided

theorem identity_no_fixation :
    Isothermal (Wid 2) ∧ (∀ t, sPow (bdK (fun _ => 1) (Wid 2) 2) t {0} univ = 0) ∧
    ¬ Tendsto (fun t => sPow (bdK (fun _ => 1) (Wid 2) 2) t {0} univ) atTop
      (𝓝 (moranFix 2 2 ({0} : Finset (Fin 2)).card)) := -- proof elided
