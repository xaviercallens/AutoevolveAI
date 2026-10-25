theorem diffraction_test_model {hc ks k S : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks)
    (hpeak : Real.sqrt (k / (2 * ks)) < S) : S ≠ sBog hc ks k := -- proof elided

theorem diffraction_test_dispersion {hc ks k S epsSq : ℝ} (hhc : 0 < hc) (hk : 0 < k)
    (hks : 0 < ks) (hS : 0 < S)
    (hfeyn : epsSq ≤ (hc * k ^ 2 / (ks * S)) ^ 2)
    (hpeak : Real.sqrt (k / (2 * ks)) < S) : epsSq ≠ bogoliubovSq hc ks k := -- proof elided

theorem peak_sqrt_iff_sq {ks k S : ℝ} (hS : 0 < S) :
    Real.sqrt (k / (2 * ks)) < S ↔ k / (2 * ks) < S ^ 2 := -- proof elided

theorem diffraction_fires_free_at_selfdual {hc ks : ℝ} (hhc : 0 < hc) (hks : 0 < ks) :
    (1 : ℝ) ≠ sBog hc ks ks := -- proof elided

theorem diffraction_silent_on_sBog {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    ¬ (Real.sqrt (k / (2 * ks)) < sBog hc ks k) := -- proof elided

theorem free_S_one_violates_phonon {ks k : ℝ} (hks : 0 < ks) (hlt : k < ks) : k / ks < 1 := -- proof elided

theorem nonvacuous_selfdual : sBog 1 1 1 ^ 2 = 1 / (2 * 1) := -- proof elided
