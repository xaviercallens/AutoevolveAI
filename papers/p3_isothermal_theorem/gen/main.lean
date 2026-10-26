theorem stationary_fixation {μ : Fin n → ℝ} {W : Fin n → Fin n → ℝ} {r : ℝ} (hn : 0 < n)
    (hr : 0 < r) (hμ : ∀ i, 0 < μ i) (hW : RowStochastic W) (hstat : ∀ j, ∑ i, μ i * W i j = μ j)
    (hcut : CutPositive μ W) (S : Finset (Fin n)) :
    Tendsto (fun t => sPow (bdK μ W r) t S univ) atTop (𝓝 (moranFix n r S.card)) ∧
    Tendsto (fun t => sPow (bdK μ W r) t S ∅) atTop (𝓝 (1 - moranFix n r S.card)) := -- proof elided

theorem isothermal_fixation {W : Fin n → Fin n → ℝ} {r : ℝ} (hn : 0 < n) (hr : 0 < r)
    (hW : Isothermal W) (hsc : StronglyConnected W) (S : Finset (Fin n)) :
    Tendsto (fun t => sPow (bdK (fun _ => 1) W r) t S univ) atTop (𝓝 (moranFix n r S.card)) := -- proof elided

theorem isothermal_fixation_single {W : Fin n → Fin n → ℝ} {r : ℝ} (hn : 0 < n) (hr : 0 < r)
    (hr1 : r ≠ 1) (hW : Isothermal W) (hsc : StronglyConnected W) (v : Fin n) :
    Tendsto (fun t => sPow (bdK (fun _ => 1) W r) t {v} univ) atTop
      (𝓝 ((1 - r⁻¹) / (1 - r⁻¹ ^ n))) := -- proof elided

theorem isothermal_fixation_neutral {W : Fin n → Fin n → ℝ} (hn : 0 < n) (hW : Isothermal W)
    (hsc : StronglyConnected W) (S : Finset (Fin n)) :
    Tendsto (fun t => sPow (bdK (fun _ => 1) W 1) t S univ) atTop (𝓝 ((S.card : ℝ) / n)) := -- proof elided

theorem isothermal_fixation_uniform {W : Fin n → Fin n → ℝ} {r : ℝ} (hn : 0 < n) (hr : 0 < r)
    (hr1 : r ≠ 1) (hW : Isothermal W) (hsc : StronglyConnected W) :
    Tendsto (fun t => (∑ v : Fin n, sPow (bdK (fun _ => 1) W r) t {v} univ) / n) atTop
      (𝓝 ((1 - r⁻¹) / (1 - r⁻¹ ^ n))) := -- proof elided

theorem bd_fixation_mono {μ : Fin n → ℝ} {W : Fin n → Fin n → ℝ} {r : ℝ} (hn : 0 < n) (hr : 0 < r)
    (hμ : ∀ i, 0 < μ i) (hW : RowStochastic W) (t : ℕ) (S : Finset (Fin n)) :
    sPow (bdK μ W r) t S univ ≤ sPow (bdK μ W r) (t + 1) S univ := -- proof elided
