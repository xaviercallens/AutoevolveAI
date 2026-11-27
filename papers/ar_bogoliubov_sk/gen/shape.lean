theorem sBog_eq_closed {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k = k / Real.sqrt (ks ^ 2 + k ^ 2) := -- proof elided

theorem sBog_sq_lt_sq {hc ks a b : ℝ} (hhc : 0 < hc) (hks : 0 < ks) (ha : 0 < a) (hab : a < b) :
    sBog hc ks a ^ 2 < sBog hc ks b ^ 2 := -- proof elided

theorem sBog_strictMonoOn {hc ks : ℝ} (hhc : 0 < hc) (hks : 0 < ks) :
    StrictMonoOn (sBog hc ks) (Set.Ioi 0) := -- proof elided

theorem sBog_lt_phonon {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k < k / ks := -- proof elided

theorem phonon_lower_lt_sBog {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    k / (ks + k) < sBog hc ks k := -- proof elided

theorem sBog_lt_one {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    sBog hc ks k < 1 := -- proof elided

theorem one_sub_sBog_le {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    1 - sBog hc ks k ≤ ks ^ 2 / k ^ 2 := -- proof elided

theorem sBog_tendsto_one {hc ks : ℝ} (hhc : 0 < hc) (hks : 0 < ks) :
    Filter.Tendsto (sBog hc ks) Filter.atTop (nhds 1) := -- proof elided

theorem epsBog_eq_epsFree_div_sBog {hc ks k : ℝ} (hhc : 0 < hc) (hk : 0 < k) (hks : 0 < ks) :
    epsBog hc ks k = epsFree hc ks k / sBog hc ks k := -- proof elided
