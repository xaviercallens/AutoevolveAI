-- Autoresearch_EnstrophyFlow.lean  sha256 4cd746897f58f7a18eb27e95f703b43d49ec0eb5c5f38753cd5f0bc1a99a8dd4
-- lines 369-371
theorem rate_v11_correct :
    dHam (fun n => (1 / 2 : ℝ) ^ n * (1 * kk n ^ 3)) (fun n => (1 / 2 : ℝ) ^ n * kk n) 0 v11
      (F kk (fun m => 1 * kk m ^ 3) v11) = 0 := ...
-- lines 377-379
theorem rate_v11_wrong_weight :
    dHam (fun n => 1 * kk n ^ 3) (fun n => (1 / 2 : ℝ) ^ n * kk n) 0 v11
      (F kk (fun m => 1 * kk m ^ 3) v11) = 8 := ...
-- lines 387-389
theorem rate_v111_no_truncation :
    dHam (fun n => (1 / 2 : ℝ) ^ n * (1 * kk n ^ 3)) (fun n => (1 / 2 : ℝ) ^ n * kk n) 0 v111
      (F kk (fun m => 1 * kk m ^ 3) v111) ≠ 0 := ...
