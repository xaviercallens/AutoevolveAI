theorem kPow_harmonic (P : Fin (N + 1) → Fin (N + 1) → ℝ) (g : Fin (N + 1) → ℝ)
    (hg : ∀ k, ∑ j, P k j * g j = g k) : ∀ n i, ∑ j, kPow P n i j * g j = g i := -- proof elided

theorem second_moment {P : Fin (N + 1) → Fin (N + 1) → ℝ} (hP : AbsorbingChain P)
    {h : Fin (N + 1) → ℝ} (hall : ∀ k, ∑ j, P k j * h j = h k) (k : Fin (N + 1)) :
    ∑ j, P k j * h j ^ 2 = h k ^ 2 + ∑ j, P k j * (h j - h k) ^ 2 := -- proof elided

theorem interiorMass_tendsto_zero {P : Fin (N + 1) → Fin (N + 1) → ℝ} (hP : AbsorbingChain P)
    {h : Fin (N + 1) → ℝ} (hh : InteriorHarmonic P h)
    (hvar : ∀ k : Fin (N + 1), 0 < (k : ℕ) → (k : ℕ) < N → 0 < ∑ j, P k j * (h j - h k) ^ 2)
    (i : Fin (N + 1)) : Tendsto (fun n => interiorMass P n i) atTop (𝓝 0) := -- proof elided

theorem absorption_tendsto {P : Fin (N + 1) → Fin (N + 1) → ℝ} (hP : AbsorbingChain P)
    (hN : 0 < N) {g : Fin (N + 1) → ℝ} (hg : InteriorHarmonic P g) (g0 : g 0 = 0)
    (g1 : g (Fin.last N) = 1)
    (hI : ∀ i, Tendsto (fun n => interiorMass P n i) atTop (𝓝 0)) (i : Fin (N + 1)) :
    Tendsto (fun n => kPow P n i (Fin.last N)) atTop (𝓝 (g i)) := -- proof elided

theorem fixation_limit {P : Fin (N + 1) → Fin (N + 1) → ℝ} (hP : AbsorbingChain P) (hN : 0 < N)
    {h : Fin (N + 1) → ℝ} (hh : InteriorHarmonic P h) (h0 : h 0 = 0) (h1 : h (Fin.last N) = 1)
    (hvar : ∀ k : Fin (N + 1), 0 < (k : ℕ) → (k : ℕ) < N → 0 < ∑ j, P k j * (h j - h k) ^ 2)
    (i : Fin (N + 1)) :
    Tendsto (fun n => kPow P n i (Fin.last N)) atTop (𝓝 (h i)) ∧
    Tendsto (fun n => kPow P n i 0) atTop (𝓝 (1 - h i)) := -- proof elided

theorem harmonic_unique_of_var {P : Fin (N + 1) → Fin (N + 1) → ℝ} (hP : AbsorbingChain P)
    (hN : 0 < N) {h : Fin (N + 1) → ℝ} (hh : InteriorHarmonic P h) (h0 : h 0 = 0)
    (h1 : h (Fin.last N) = 1)
    (hvar : ∀ k : Fin (N + 1), 0 < (k : ℕ) → (k : ℕ) < N → 0 < ∑ j, P k j * (h j - h k) ^ 2)
    {g : Fin (N + 1) → ℝ} (hg : InteriorHarmonic P g) (g0 : g 0 = 0) (g1 : g (Fin.last N) = 1) :
    ∀ i, g i = h i := -- proof elided
