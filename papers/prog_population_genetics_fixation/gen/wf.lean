theorem wf_var_pos {N : ℕ} (hN : 0 < N) (k : Fin (N + 1)) (hk1 : 0 < (k : ℕ)) (hk2 : (k : ℕ) < N) :
    0 < ∑ j, wfP N k j * (((j : ℕ) : ℝ) / N - ((k : ℕ) : ℝ) / N) ^ 2 := -- proof elided

theorem wright_fisher_fixation_limit {N : ℕ} (hN : 0 < N) (i : Fin (N + 1)) :
    Tendsto (fun n => kPow (wfP N) n i (Fin.last N)) atTop (𝓝 (((i : ℕ) : ℝ) / N)) ∧
    Tendsto (fun n => kPow (wfP N) n i 0) atTop (𝓝 (1 - ((i : ℕ) : ℝ) / N)) := -- proof elided
