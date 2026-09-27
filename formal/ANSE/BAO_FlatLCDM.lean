/-
Flat-ΛCDM BAO consistency exercise: kernel-verified algebraic skeleton of the
distance-measure relations used in scripts/bao_flcdm/fit_desi_bao.py.

Scope, deliberately: this file proves EXACT ALGEBRAIC FACTS about the model
(positivity and monotonicity of the dimensionless expansion rate E(z), and
the distance-duality identity), not a theorem "solving cosmology." These are
freshman real-analysis/algebra facts, chosen because they are guaranteed
provable against this Mathlib subset -- the point of this exercise (per the
task framing) is a near-certain, checkable result, not a research gamble.
Reference: docs/literature/BAO_FLCDM_LITERATURE_REVIEW_2026.md.
-/
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

namespace ANSE.BAOFlatLCDM

open Real

/-- Dimensionless flat-ΛCDM expansion rate `E(z) = H(z)/H₀ = √(Ωₘ(1+z)³ + (1-Ωₘ))`,
flatness (`Ω_Λ = 1 - Ωₘ`) already substituted. -/
noncomputable def E (Om z : ℝ) : ℝ := Real.sqrt (Om * (1 + z) ^ 3 + (1 - Om))

/-- `E(z) > 0` for `z ≥ 0` and `0 < Ωₘ < 1`: the expansion rate never vanishes
or turns imaginary on the physical branch, so `1/E(z)` (needed for the
comoving-distance integral in the numeric fit) is always well-defined. -/
theorem E_pos {Om z : ℝ} (hOm0 : 0 < Om) (hOm1 : Om < 1) (hz : 0 ≤ z) :
    0 < E Om z := by
  unfold E
  rw [Real.sqrt_pos]
  nlinarith [pow_pos (show (0:ℝ) < 1 + z by linarith) 3]

/-- `E` is strictly increasing on `[0, ∞)` for `0 < Ωₘ < 1`: the universe's
expansion rate is (given matter domination at least at `z ≥ 0`) always
faster in the past, so the comoving-distance integrand `1/E(z)` is strictly
decreasing -- the qualitative fact the numeric integration relies on. -/
theorem E_strictMonoOn {Om : ℝ} (hOm0 : 0 < Om) (hOm1 : Om < 1) :
    StrictMonoOn (E Om) (Set.Ici (0 : ℝ)) := by
  intro z1 hz1 z2 hz2 hlt
  simp only [Set.mem_Ici] at hz1 hz2
  unfold E
  have h1pos : (0:ℝ) < 1 + z1 := by linarith
  have hcube : (1 + z1) ^ 3 < (1 + z2) ^ 3 := by nlinarith [sq_nonneg (z2 - z1), sq_nonneg (1 + z1), sq_nonneg (1 + z2)]
  have harg : Om * (1 + z1) ^ 3 + (1 - Om) < Om * (1 + z2) ^ 3 + (1 - Om) := by nlinarith
  have hargnn : 0 ≤ Om * (1 + z1) ^ 3 + (1 - Om) := by nlinarith [pow_pos h1pos 3]
  exact Real.sqrt_lt_sqrt hargnn harg

/-- Flat-space comoving/luminosity/angular-diameter distance relations, as
pure definitions parametrised by the comoving distance `Dc` (the physics is
entirely in `Dc`; these three lines are algebra, true for ANY `Dc`, model-
independent). -/
noncomputable def D_L (z Dc : ℝ) : ℝ := (1 + z) * Dc
noncomputable def D_A (z Dc : ℝ) : ℝ := Dc / (1 + z)

/-- Distance-duality relation `D_L = (1+z)² D_A`, for any `z > -1` (so `1+z ≠ 0`)
and any comoving distance `Dc` -- exact algebraic consequence of the two
definitions above, independent of the cosmological model (Etherington 1933's
reciprocity relation, specialised to flat space where it is pure algebra
rather than a general-relativistic theorem). -/
theorem distance_duality {z Dc : ℝ} (hz : z ≠ -1) :
    D_L z Dc = (1 + z) ^ 2 * D_A z Dc := by
  have h1 : (1:ℝ) + z ≠ 0 := by intro h; apply hz; linarith
  unfold D_L D_A
  field_simp

end ANSE.BAOFlatLCDM
