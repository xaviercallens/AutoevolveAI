/-- Riesz `t^{-s/2}` (energy `Σ r^{-s}`), `s ≥ 0`. -/
theorem riesz_cm {s : ℝ} (hs : 0 ≤ s) : IsCompletelyMonotoneOn (TriangularRiesz.riesz s) :=
  (rpow_neg (by linarith : 0 ≤ s / 2)).congr' fun _ _ => rfl

/-- **H2 as a corollary.** Planar Yukawa `e^{-κ r}/r` (`κ ≥ 0`): Riesz × (exp ∘ √). -/
theorem yukawa_cm {κ : ℝ} (hκ : 0 ≤ κ) : IsCompletelyMonotoneOn (AutoresearchYukawa.g κ) :=
  ((riesz_cm zero_le_one).mul (phi_cm hκ)).congr (AutoresearchYukawa.g_eqOn κ)

/-- **H1 as a corollary.** Bilayer dipolar exciton `2 (1/r - 1/√(r² + d²))`, every `d`: difference of a translate. -/
theorem dipolar_cm (d : ℝ) : IsCompletelyMonotoneOn (AutoresearchDipolar.g d) :=
  (((rpow_neg (by norm_num : (0 : ℝ) ≤ 1 / 2)).sub_comp_add_const (sq_nonneg d)).const_mul
    zero_le_two).congr' fun _ _ => rfl

/-- Screened multipole differences `r^{-s} - (r² + c)^{-s/2}`, `s ≥ 0`, `c ≥ 0`. -/
theorem shiftDiff_cm {s c : ℝ} (hs : 0 ≤ s) (hc : 0 ≤ c) :
    IsCompletelyMonotoneOn (fun t => TriangularRiesz.riesz s t - TriangularRiesz.riesz s (t + c)) :=
  (riesz_cm hs).sub_comp_add_const hc

/-- **H3L as a corollary of the weakened Laplace lemma** (only the `n = 0` integrability is used). -/
theorem keldysh_cm {r0 : ℝ} (hr0 : 0 < r0) : IsCompletelyMonotoneOn (AutoresearchKeldysh.keldysh r0) := -- proof elided

/-- Finite-size (soft-core) Yukawa `e^{-κ √(r² + b²)} / √(r² + b²)`: translation closure. -/
theorem yukawa_softcore_cm {κ b : ℝ} (hκ : 0 ≤ κ) :
    IsCompletelyMonotoneOn (fun t => AutoresearchYukawa.g κ (t + b ^ 2)) :=
  (yukawa_cm hκ).comp_add_const (sq_nonneg b)

/-- Stretched exponential `e^{-a r^{2α}}` (`a ≥ 0`, `0 ≤ α ≤ 1`, i.e. `e^{-a t^α}`): subordination. -/
theorem stretchedExp_cm {a α : ℝ} (ha : 0 ≤ a) (h0 : 0 ≤ α) (h1 : α ≤ 1) :
    IsCompletelyMonotoneOn (fun t => Real.exp (-(a * t ^ α))) :=
  exp_neg_comp ha (IsBernsteinOn.rpow h0 h1) (fun _ ht => Real.rpow_pos_of_pos ht α)

/-- Triangular optimality for the soft-core Yukawa interaction (conditional on upstream). -/
theorem triangular_yukawa_softcore_optimal {κ b : ℝ} (hκ : 0 ≤ κ) (C : Set OAI.AtomicTriangular.Plane)
    (hC : OAI.AtomicTriangular.LocallyFinite C) (hd : OAI.AtomicTriangular.DensityOne C) :
    OAI.AtomicTriangular.latticeEnergy (fun t => AutoresearchYukawa.g κ (t + b ^ 2)) ≤
      OAI.AtomicTriangular.energy (fun t => AutoresearchYukawa.g κ (t + b ^ 2)) C := -- proof elided
