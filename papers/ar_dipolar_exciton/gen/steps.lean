lemma iteratedDeriv_rpow (a : ℝ) (r : ℕ) (t : ℝ) :
    iteratedDeriv r (fun x : ℝ => x ^ a) t = (descPochhammer ℝ r).eval a * t ^ (a - r) := -- proof elided

lemma iteratedDeriv_shift (a c : ℝ) (r : ℕ) (t : ℝ) :
    iteratedDeriv r (fun x : ℝ => (x + c) ^ a) t = (descPochhammer ℝ r).eval a * (t + c) ^ (a - r) := -- proof elided

lemma iteratedDeriv_g (d : ℝ) (r : ℕ) {t : ℝ} (ht : 0 < t) :
    iteratedDeriv r (g d) t =
      2 * ((descPochhammer ℝ r).eval (-(1 / 2 : ℝ)) *
        (t ^ (-(1 / 2 : ℝ) - r) - (t + d ^ 2) ^ (-(1 / 2 : ℝ) - r))) := -- proof elided

lemma sign_desc (r : ℕ) :
    (-1 : ℝ) ^ r * (descPochhammer ℝ r).eval (-(1 / 2 : ℝ)) = (ascPochhammer ℝ r).eval (1 / 2 : ℝ) := -- proof elided

lemma diff_nonneg (c e : ℝ) (hc : 0 ≤ c) (he : e ≤ 0) {t : ℝ} (ht : 0 < t) :
    0 ≤ t ^ e - (t + c) ^ e := -- proof elided
