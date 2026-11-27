noncomputable def sPow (P : σ → σ → ℝ) : ℕ → σ → σ → ℝ
  | 0 => fun s u => if s = u then 1 else 0
  | t + 1 => fun s u => ∑ v, sPow P t s v * P v u

structure TwoAbsorbing (P : σ → σ → ℝ) (bot top : σ) : Prop where
  ne : bot ≠ top
  nonneg : ∀ s u, 0 ≤ P s u
  rowSum : ∀ s, ∑ u, P s u = 1
  absorbBot : ∀ u, P bot u = if u = bot then 1 else 0
  absorbTop : ∀ u, P top u = if u = top then 1 else 0

theorem two_absorbing_limit {P : σ → σ → ℝ} {bot top : σ} (hP : TwoAbsorbing P bot top)
    {h : σ → ℝ} (hh : ∀ s, s ≠ bot → s ≠ top → ∑ u, P s u * h u = h s) (h0 : h bot = 0)
    (h1 : h top = 1) (hvar : ∀ s, s ≠ bot → s ≠ top → 0 < ∑ u, P s u * (h u - h s) ^ 2)
    (s : σ) :
    Tendsto (fun t => sPow P t s top) atTop (𝓝 (h s)) ∧
    Tendsto (fun t => sPow P t s bot) atTop (𝓝 (1 - h s)) := -- proof elided
