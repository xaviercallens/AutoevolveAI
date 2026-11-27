theorem epsFree_units {hbar m c k : ℝ} (hh : 0 < hbar) (hm : 0 < m) (hc : 0 < c) :
    epsFree (hbar * c) (2 * m * c / hbar) k = hbar ^ 2 * k ^ 2 / (2 * m) := ... -- proof elided

theorem feynman_sBog_eq {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    epsFree hc ks k / sBog hc ks k = epsBog hc ks k := ... -- proof elided

theorem feynman_le_epsBog_iff {hc ks k S : ℝ} (hhc : 0 < hc) (hk : 0 < k)
    (hS : 0 < S) : epsFree hc ks k / S ≤ epsBog hc ks k ↔ sBog hc ks k ≤ S := ... -- proof elided

theorem feynman_sBog_units {hbar m c k : ℝ} (hh : 0 < hbar) (hm : 0 < m) (hc : 0 < c)
    (hk : 0 < k) :
    hbar ^ 2 * k ^ 2 / (2 * m * sBog (hbar * c) (2 * m * c / hbar) k)
      = epsBog (hbar * c) (2 * m * c / hbar) k := ... -- proof elided
