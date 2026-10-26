/-- **H2** (original statement of `AutoresearchYukawa.yukawa_admissible`). -/
theorem H2_yukawa_admissible {κ : ℝ} (hκ : 0 < κ) : AdmissiblePotential (AutoresearchYukawa.g κ) :=
  (((riesz_cm zero_le_one).mul (phi_cm hκ.le)).congr (AutoresearchYukawa.g_eqOn κ)).admissible

/-- **H1** (statement of `AutoresearchDipolar.dipolar_admissible_all`; the original `dipolar_admissible` needed `0 < d`). -/
theorem H1_dipolar_admissible (d : ℝ) : AdmissiblePotential (AutoresearchDipolar.g d) :=
  ((((rpow_neg (by norm_num : (0 : ℝ) ≤ 1 / 2)).sub_comp_add_const (sq_nonneg d)).const_mul
    zero_le_two).congr' fun _ _ => rfl).admissible

/-- **H3L** (original statement of `AutoresearchKeldysh.keldysh_admissible`). -/
theorem H3_keldysh_admissible {r0 : ℝ} (hr0 : 0 < r0) : AdmissiblePotential (AutoresearchKeldysh.keldysh r0) :=
  (keldysh_cm hr0).admissible

/-- The screened bilayer exciton potential is completely monotone (`κ ≥ 0`, every `d`). -/
theorem screenedDipolar_cm {κ : ℝ} (hκ : 0 ≤ κ) (d : ℝ) : IsCompletelyMonotoneOn (screenedDipolar κ d) :=
  ((yukawa_cm hκ).sub_comp_add_const (sq_nonneg d)).const_mul zero_le_two

/-- **Yukawa mixtures with a nonnegative spectral density are completely monotone**, provided
`e^{-cκ} m(κ)` is integrable on `(0, ∞)` for every `c > 0`. Proof: `t^{-1/2} · (Laplace(m) ∘ √)`. -/
theorem yukawaSpectrum_cm {m : ℝ → ℝ} (hm : Measurable m) (hm0 : ∀ κ, 0 < κ → 0 ≤ m κ)
    (hint : ∀ c : ℝ, 0 < c → IntegrableOn (fun κ => Real.exp (-(c * κ)) * m κ) (Ioi 0)) :
    IsCompletelyMonotoneOn (yukawaSpectrum m) := -- proof elided

/-- Second difference in `t = r²` (shifts `0, c, 2c`): completely monotone for completely monotone `f`.
This is NOT the equally spaced-layer quadrupole (shifts `0, d², 4d²`); see Part 3 and Part 4 (`quadrupolarPair_cm`). -/
theorem secondDiff_cm {f : ℝ → ℝ} (hf : IsCompletelyMonotoneOn f) {c : ℝ} (hc : 0 ≤ c) :
    IsCompletelyMonotoneOn (fun t => f t - 2 * f (t + c) + f (t + 2 * c)) :=
  ((hf.sub_comp_add_const hc).sub_comp_add_const hc).congr' fun t _ => by
    show f t - f (t + c) - (f (t + c) - f (t + c + c)) = _
    rw [show t + c + c = t + 2 * c by ring]
    ring
