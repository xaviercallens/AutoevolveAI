noncomputable def epsFree (hc ks k : ℝ) : ℝ := hc * k ^ 2 / ks

noncomputable def epsBog (hc ks k : ℝ) : ℝ := Real.sqrt (bogoliubovSq hc ks k)

noncomputable def sBog (hc ks k : ℝ) : ℝ := epsFree hc ks k / epsBog hc ks k
