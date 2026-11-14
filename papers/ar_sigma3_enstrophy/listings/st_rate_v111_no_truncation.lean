-- Autoresearch_EnstrophyFlow.lean lines 387-389
theorem rate_v111_no_truncation :
    dHam (fun n => (1 / 2 : ℝ) ^ n * (1 * kk n ^ 3)) (fun n => (1 / 2 : ℝ) ^ n * kk n) 0 v111
      (F kk (fun m => 1 * kk m ^ 3) v111) ≠ 0 := ...
