import OAI.Analysis.Triangular.Energy.Universal

/-!
# Riesz-energy optimality of the triangular lattice (corollary of upstream universal optimality)

For every `s > 0` the Riesz potential `g(t) = t^{-s/2}` (energy `Σ |x - y|^{-s}` in terms of `t = |x - y|²`)
is admissible in the sense of `OAI.TriangularUniversal.AdmissiblePotential` (smooth on `(0, ∞)`, non-negative,
completely monotone). Hence, by the Comparator-accepted theorem `OAI.AtomicTriangular.universal_energy_minimum`,
the triangular lattice `A` minimises the Riesz `s`-energy among all locally finite configurations of density one.

Everything here is conditional on upstream's theorem, whose statement fidelity has not been audited by a human.
-/

namespace TriangularRiesz

open OAI.AtomicTriangular

/-- Riesz potential in the variable `t = r²`. -/
noncomputable def riesz (s : ℝ) : ℝ → ℝ := fun t => t ^ (-(s / 2))

theorem riesz_admissible {s : ℝ} (hs : 0 < s) : AdmissiblePotential (riesz s) := by
  refine ⟨?_, ?_, ?_⟩
  · intro x hx
    exact (Real.contDiffAt_rpow_const_of_ne (ne_of_gt hx)).contDiffWithinAt
  · intro t ht
    exact (Real.rpow_pos_of_pos ht _).le
  · intro r t ht
    have ha : 0 < s / 2 := by positivity
    rw [iteratedDeriv_eq_iterate]
    unfold riesz
    rw [Real.iter_deriv_rpow_const]
    have hasc := ascPochhammer_eval_neg_eq_descPochhammer (R := ℝ) (-(s / 2)) r
    rw [neg_neg] at hasc
    have hdesc : (descPochhammer ℝ r).eval (-(s / 2)) = (-1) ^ r * (ascPochhammer ℝ r).eval (s / 2) := by
      have h1 : ((-1 : ℝ) ^ r) * ((-1) ^ r) = 1 := by rw [← mul_pow]; norm_num
      calc (descPochhammer ℝ r).eval (-(s / 2))
          = ((-1) ^ r * (-1) ^ r) * (descPochhammer ℝ r).eval (-(s / 2)) := by rw [h1, one_mul]
        _ = (-1) ^ r * (ascPochhammer ℝ r).eval (s / 2) := by rw [hasc]; ring
    rw [hdesc]
    have hpos := ascPochhammer_pos r (s / 2) ha
    have hpow := Real.rpow_pos_of_pos ht (-(s / 2) - r)
    have h1 : ((-1 : ℝ) ^ r) * ((-1) ^ r) = 1 := by rw [← mul_pow]; norm_num
    calc (0 : ℝ) ≤ (ascPochhammer ℝ r).eval (s / 2) * t ^ (-(s / 2) - r) := by positivity
      _ = (-1) ^ r * ((-1) ^ r * (ascPochhammer ℝ r).eval (s / 2) * t ^ (-(s / 2) - r)) := by
        rw [← mul_assoc, ← mul_assoc, h1, one_mul]

/-- **Riesz optimality.** For every `s > 0` the triangular lattice minimises the Riesz `s`-energy among all locally
finite planar configurations of density one (energies in `[0, ∞]`). For `s ≤ 2` the lattice energy is `∞`, so the
statement then only says `energy C = ∞`; it is informative for `s > 2`, where the lattice energy is finite
(`latticeEnergy_riesz_lt_top`). -/
theorem triangular_riesz_optimal {s : ℝ} (hs : 0 < s) (C : Set Plane) (hC : LocallyFinite C) (hd : DensityOne C) :
    latticeEnergy (riesz s) ≤ energy (riesz s) C :=
  (universal_energy_minimum (riesz s) C (riesz_admissible hs) hC hd).1

end TriangularRiesz
