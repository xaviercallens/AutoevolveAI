-- Autoresearch_EnstrophyFlow.lean lines 377-379
theorem rate_v11_wrong_weight :
    dHam (fun n => 1 * kk n ^ 3) (fun n => (1 / 2 : ℝ) ^ n * kk n) 0 v11
      (F kk (fun m => 1 * kk m ^ 3) v11) = 8 := ...
