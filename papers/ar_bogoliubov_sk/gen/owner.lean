noncomputable def bogoliubovSq (hc ks k : ℝ) : ℝ := (hc * k) ^ 2 + (hc * k ^ 2 / ks) ^ 2

noncomputable def ell (ks k : ℝ) : ℝ := 1 / k + k / ks ^ 2

noncomputable def dualLength (hc k epsSq : ℝ) : ℝ := epsSq / (hc ^ 2 * k ^ 3)

theorem ell_ge {ks k : ℝ} (hk : 0 < k) (hks : 0 < ks) : 2 / ks ≤ ell ks k := -- proof elided

theorem feynman_ge_iff {ks k S : ℝ} (_hk : 0 < k) (hks : 0 < ks) (hS : 0 < S) :
    2 / ks ≤ k / (ks ^ 2 * S ^ 2) ↔ S ^ 2 ≤ k / (2 * ks) := -- proof elided

theorem not_bogoliubov_of_structure_factor {hc ks k S epsSq : ℝ}
    (hhc : hc ≠ 0) (hk : 0 < k) (hks : 0 < ks) (hS : 0 < S)
    (hfeyn : epsSq ≤ (hc * k ^ 2 / (ks * S)) ^ 2)        -- Feynman's variational bound
    (hpeak : k / (2 * ks) < S ^ 2) :                      -- measured: S above the dual-scale bound
    epsSq ≠ bogoliubovSq hc ks k := -- proof elided
