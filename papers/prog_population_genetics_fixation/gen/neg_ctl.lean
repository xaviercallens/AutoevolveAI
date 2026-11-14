theorem ctl_neg_identity_no_absorption :
    InteriorHarmonic (idKernel 2) (fun j => ((j : ℕ) : ℝ) / 2) ∧
    (∀ n, kPow (idKernel 2) n 1 (Fin.last 2) = 0) ∧
    ¬ Tendsto (fun n => kPow (idKernel 2) n 1 (Fin.last 2)) atTop (𝓝 (1 / 2)) := -- proof elided

theorem ctl_neg_flipped_value : flipFix 3 2 1 = 1 / 7 ∧ flipFix 3 2 1 ≠ moranFix 3 2 1 := -- proof elided

theorem ctl_neg_flipped_not_harmonic :
    moranUp 3 2 1 * flipFix 3 2 2 + moranDown 3 2 1 * flipFix 3 2 0
      + (1 - moranUp 3 2 1 - moranDown 3 2 1) * flipFix 3 2 1 ≠ flipFix 3 2 1 := -- proof elided

theorem ctl_neg_neutral_not_harmonic :
    moranUp 3 2 1 * (2 / 3) + moranDown 3 2 1 * 0
      + (1 - moranUp 3 2 1 - moranDown 3 2 1) * (1 / 3) ≠ (1 / 3 : ℝ) := -- proof elided

theorem ctl_neg_wrong_limits :
    ¬ Tendsto (fun n => kPow (moranP 3 2) n 1 (Fin.last 3)) atTop (𝓝 (1 / 3)) ∧
    ¬ Tendsto (fun n => kPow (moranP 3 2) n 1 (Fin.last 3)) atTop (𝓝 (1 / 7)) := -- proof elided
