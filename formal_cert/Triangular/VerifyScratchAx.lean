import Triangular.Riesz
import Triangular.RieszFinite

open OAI.AtomicTriangular
open scoped ContDiff

-- verifier's own axiom audit
#print axioms TriangularRiesz.riesz_admissible
#print axioms TriangularRiesz.triangular_riesz_optimal
#print axioms TriangularRiesz.latticeEnergy_riesz_lt_top
#print axioms OAI.AtomicTriangular.universal_energy_minimum

-- statement shapes as the kernel sees them
#check @TriangularRiesz.triangular_riesz_optimal
#check @TriangularRiesz.latticeEnergy_riesz_lt_top
#print OAI.TriangularUniversal.AdmissiblePotential
#print OAI.AtomicTriangular.latticeEnergy

-- smoothness order: (⊤ : ℕ∞) cast into WithTop ℕ∞ is ∞ (C^∞), not ω (analytic)
example : (((⊤ : ℕ∞)) : WithTop ℕ∞) ≠ (⊤ : WithTop ℕ∞) := by simp
example : (((⊤ : ℕ∞)) : WithTop ℕ∞) = ∞ := rfl

-- riesz s (r^2) = r^(-s) for r > 0
example (s r : ℝ) (hr : 0 < r) : TriangularRiesz.riesz s (r ^ 2) = r ^ (-s) := by
  unfold TriangularRiesz.riesz
  rw [← Real.rpow_natCast, ← Real.rpow_mul hr.le]
  congr 1
  push_cast
  ring

-- negative control (a): riesz (-2) = t^1 is NOT admissible (its first derivative is 1 > 0)
theorem ctl_a_false : ¬ OAI.TriangularUniversal.AdmissiblePotential (TriangularRiesz.riesz (-2)) := by
  intro h
  have h3 := h.2.2 1 1 one_pos
  have hfun : TriangularRiesz.riesz (-2) = fun t => t := by
    funext t
    unfold TriangularRiesz.riesz
    norm_num
  rw [hfun] at h3
  simp at h3
  norm_num at h3
#print axioms ctl_a_false
