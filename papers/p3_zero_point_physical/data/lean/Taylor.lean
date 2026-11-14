import Mathlib.Analysis.Calculus.Deriv.MeanValue
import Mathlib.Analysis.Calculus.Deriv.Comp
import Mathlib.Analysis.Calculus.Deriv.Pow
import Mathlib.Tactic

/-!
# N2: the window step, kernel-checked

If `f` is twice differentiable on `[-t, t]` with `f'' ≤ K` there, then `f t + f (-t) - 2 f 0 ≤ t² K`.
In N2 this is applied (in `Basic.lean`) to the majorant `U₂(t) = ¼ ∫ f_κ(t) dκ`,
`f_κ(t) = tr X_t + tr(X_t⁻¹ D_t)`, with `U₂''(u) = ¼ ∫ f_κ''(u) dκ` (differentiation under the integral: a written
step, Tier C-human) and `K = M`, an Arb enclosure valid for every fixed `|u| ≤ t₀` of `¼ ∫ f_κ''(u) dκ`
(ball arithmetic, Tier C-ball, not kernel-checked).
-/

namespace ProgZeroPointPhys

theorem second_diff_le_of_deriv2_le {f f1 f2 : ℝ → ℝ} {t K : ℝ} (ht : 0 ≤ t)
    (h1 : ∀ u ∈ Set.Icc (-t) t, HasDerivAt f (f1 u) u)
    (h2 : ∀ u ∈ Set.Icc (-t) t, HasDerivAt f1 (f2 u) u)
    (hK : ∀ u ∈ Set.Icc (-t) t, f2 u ≤ K) :
    f t + f (-t) - 2 * f 0 ≤ t ^ 2 * K := by
  have mem : ∀ u ∈ Set.Icc (0 : ℝ) t, u ∈ Set.Icc (-t) t ∧ -u ∈ Set.Icc (-t) t := by
    intro u hu
    obtain ⟨a, b⟩ := hu
    exact ⟨⟨by linarith, b⟩, ⟨by linarith, by linarith⟩⟩
  -- φ(u) = f1 u - f1 (-u) - 2 K u is antitone on [0, t] and φ 0 = 0
  set φ : ℝ → ℝ := fun u => f1 u - f1 (-u) - 2 * K * u with hφ
  have hφd : ∀ u ∈ Set.Icc (0 : ℝ) t, HasDerivAt φ (f2 u + f2 (-u) - 2 * K) u := by
    intro u hu
    obtain ⟨m1, m2⟩ := mem u hu
    have a := h2 u m1
    have b : HasDerivAt (fun v => f1 (-v)) (f2 (-u) * (-1)) u :=
      (h2 (-u) m2).comp u (hasDerivAt_neg u)
    have c : HasDerivAt (fun v : ℝ => 2 * K * v) (2 * K) u := by
      simpa using (hasDerivAt_id u).const_mul (2 * K)
    have := (a.sub b).sub c
    convert this using 1
    ring
  have hφanti : AntitoneOn φ (Set.Icc 0 t) := by
    apply antitoneOn_of_deriv_nonpos (convex_Icc 0 t)
    · intro u hu
      exact (hφd u hu).continuousAt.continuousWithinAt
    · intro u hu
      rw [interior_Icc] at hu
      exact (hφd u ⟨hu.1.le, hu.2.le⟩).differentiableAt.differentiableWithinAt
    · intro u hu
      rw [interior_Icc] at hu
      rw [(hφd u ⟨hu.1.le, hu.2.le⟩).deriv]
      obtain ⟨m1, m2⟩ := mem u ⟨hu.1.le, hu.2.le⟩
      have := hK u m1
      have := hK (-u) m2
      linarith
  have hφ0 : φ 0 = 0 := by simp [hφ]
  -- ψ(u) = f u + f (-u) - K u² has derivative φ ≤ 0 on [0, t]
  set ψ : ℝ → ℝ := fun u => f u + f (-u) - K * u ^ 2 with hψ
  have hψd : ∀ u ∈ Set.Icc (0 : ℝ) t, HasDerivAt ψ (φ u) u := by
    intro u hu
    obtain ⟨m1, m2⟩ := mem u hu
    have a := h1 u m1
    have b : HasDerivAt (fun v => f (-v)) (f1 (-u) * (-1)) u :=
      (h1 (-u) m2).comp u (hasDerivAt_neg u)
    have c : HasDerivAt (fun v : ℝ => K * v ^ 2) (K * (2 * u)) u := by
      have := (hasDerivAt_pow 2 u).const_mul K
      simpa using this
    have := (a.add b).sub c
    convert this using 1
    simp only [hφ]
    ring
  have hψanti : AntitoneOn ψ (Set.Icc 0 t) := by
    apply antitoneOn_of_deriv_nonpos (convex_Icc 0 t)
    · intro u hu
      exact (hψd u hu).continuousAt.continuousWithinAt
    · intro u hu
      rw [interior_Icc] at hu
      exact (hψd u ⟨hu.1.le, hu.2.le⟩).differentiableAt.differentiableWithinAt
    · intro u hu
      rw [interior_Icc] at hu
      rw [(hψd u ⟨hu.1.le, hu.2.le⟩).deriv]
      have := hφanti ⟨le_refl 0, ht⟩ ⟨hu.1.le, hu.2.le⟩ hu.1.le
      rw [hφ0] at this
      exact this
  have key := hψanti ⟨le_refl 0, ht⟩ ⟨ht, le_refl t⟩ ht
  simp only [hψ, neg_zero] at key
  nlinarith [key]

end ProgZeroPointPhys

#print axioms ProgZeroPointPhys.second_diff_le_of_deriv2_le
