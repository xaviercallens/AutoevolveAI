/-
  ANSE.PaperC_ForcedVisibility — Paper C, edition 3 (21 October 2026)
  ====================================================================
  Why the `w = -1` half of P3 carries no evidence, and why the `w = +1` half does.

  Paper C's edition-2 claim "no root-number -1 Hecke orbit is visible from the base point"
  was reported as a measurement. It is not one: it cannot come out any other way. This file
  proves that, so the withdrawal rests on a theorem rather than on a remark.

  What is proved here (all quantified, no `sorry`, no extra axioms):
    * `frobenius_forces_vanishing`: if the Frobenius operator `F` fixes the base vector `e₀`,
      commutes with the Hecke projector `π`, and acts on `π`'s image by the scalar `w = -1`,
      then `π e₀ = 0` — identically, for every such configuration. Our base point has
      `j = 1728 ∈ 𝔽_p` for every `p`, so `F e₀ = e₀` always holds and the conclusion is forced
      at every prime in the range. No arithmetic input can change it.
    * `frobenius_forces_nothing_at_w_one`: the same hypotheses with `w = +1` are satisfied both
      by a configuration with `π e₀ ≠ 0` and by one with `π e₀ = 0`. So visibility in the
      `w = +1` stratum is independent of the forcing hypotheses: that stratum is where a
      measurement can live, which is why it carries the replacement test
      (`positive_controls.vii_gross_w_plus_stratum`).
    * `odd_functional_equation_forces_central_zero`: a second, base-point-independent forcing.
      If `L s = w * L (2 - s)` with `w = -1` then `L 1 = 0`. Hence Gross 1987 predicts
      invisibility of a `w = -1` orbit from ANY base point, not just from `j = 1728`; moving
      the base point would not restore content to the claim.
    * `even_functional_equation_permits_nonzero`: control for the previous theorem — with
      `w = +1` the functional equation does not force `L 1 = 0`.
    * `two_smul_eq_zero_iff`: the characteristic hypothesis both forcing arguments turn on,
      isolated so it is visible that each needs `(2 : K) ≠ 0` and nothing else.

  What is NOT proved here: that the Brandt operators and Frobenius actually satisfy these
  hypotheses on the supersingular basis. That is Deuring/Eichler theory plus the numerical
  commutation check the pipeline performs at each prime; it is assumed, not formalised. The
  theorems below are conditional on it, which is exactly how the paper now states them.
-/
import Mathlib.Tactic
import Mathlib.Algebra.Module.LinearMap.Basic
import Mathlib.Data.Real.Basic

namespace ANSE.PaperC_ForcedVisibility

/-! ## 1. The characteristic hypothesis -/

/-- In a module over a field, `2 • v = 0` iff `v = 0`, provided `2 ≠ 0` in the field.
This is the only arithmetic both forcing arguments use. -/
theorem two_smul_eq_zero_iff {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
    (h2 : (2 : K) ≠ 0) (v : V) : (2 : K) • v = 0 ↔ v = 0 := by
  constructor
  · intro h
    rcases smul_eq_zero.mp h with h1 | h1
    · exact absurd h1 h2
    · exact h1
  · intro h
    rw [h, smul_zero]

/-! ## 2. Frobenius forcing: the `w = -1` half of P3 cannot fail -/

/-- **The `w = -1` half of P3 is forced, not measured.**

`F` is the Frobenius permutation of the supersingular set, `π` the projector onto the
`f`-isotypic component, `e₀` the basis vector of the base point. The hypotheses are:
`F` fixes `e₀` (true whenever `j(E₀) ∈ 𝔽_p`, and `j(E₀) = 1728` for every `p` here),
`π` commutes with `F` (`F` commutes with the Brandt matrices), and `F` acts by `w` on the
`f`-component. With `w = -1` these give `π e₀ = 0` outright.

The paper's "0 violations out of 37 orbits" is therefore not an observation with 37 chances
to fail: it is this theorem, instantiated 37 times. -/
theorem frobenius_forces_vanishing {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
    (F π : V →ₗ[K] V) (e₀ : V) (w : K) (h2 : (2 : K) ≠ 0)
    (hfix : F e₀ = e₀)
    (hcomm : ∀ v, π (F v) = F (π v))
    (hscal : ∀ v, F (π v) = w • π v)
    (hw : w = -1) :
    π e₀ = 0 := by
  -- π e₀ = π (F e₀) = F (π e₀) = w • π e₀ = -π e₀
  have key : π e₀ = -π e₀ := by
    calc π e₀ = π (F e₀) := by rw [hfix]
      _ = F (π e₀) := hcomm e₀
      _ = w • π e₀ := hscal e₀
      _ = (-1 : K) • π e₀ := by rw [hw]
      _ = -π e₀ := by rw [neg_one_smul]
  have h2v : (2 : K) • π e₀ = 0 := by
    rw [two_smul]
    nth_rewrite 1 [key]
    simp
  exact (two_smul_eq_zero_iff h2 (π e₀)).mp h2v

/-- **The `w = +1` half is not forced.** The forcing hypotheses with `w = +1` are consistent
both with `π e₀ ≠ 0` and with `π e₀ = 0`, so they leave visibility undetermined. Both
witnesses are taken over `ℚ` with `V = ℚ` and `F = id`; what differs is only `π`.

This is the formal content of "the `w = +1` stratum is where the measurement lives". -/
theorem frobenius_forces_nothing_at_w_one :
    (∃ (F π : ℚ →ₗ[ℚ] ℚ) (e₀ : ℚ),
        F e₀ = e₀ ∧ (∀ v, π (F v) = F (π v)) ∧ (∀ v, F (π v) = (1 : ℚ) • π v) ∧ π e₀ ≠ 0) ∧
    (∃ (F π : ℚ →ₗ[ℚ] ℚ) (e₀ : ℚ),
        F e₀ = e₀ ∧ (∀ v, π (F v) = F (π v)) ∧ (∀ v, F (π v) = (1 : ℚ) • π v) ∧ π e₀ = 0) := by
  refine ⟨⟨LinearMap.id, LinearMap.id, 1, rfl, fun v => rfl, fun v => by simp, ?_⟩,
          ⟨LinearMap.id, 0, 1, rfl, fun v => rfl, fun v => by simp, ?_⟩⟩
  · simp
  · simp

/-- Positive control for `frobenius_forces_vanishing`: its hypotheses are satisfiable, and
satisfiable *non-trivially* — with `e₀ ≠ 0` and `π ≠ 0`. Without this the theorem could be
true merely because nothing meets its hypotheses, and it would say nothing about Paper C.

The witness is `V = ℚ²`, `F (x,y) = (x,-y)`, `π (x,y) = (0,y)`, `e₀ = (1,0)`: Frobenius fixes
the base vector, the projector commutes with it and `F` acts by `-1` on `π`'s image. The
conclusion `π e₀ = 0` then holds for the reason the theorem gives, not because `π` is zero. -/
theorem frobenius_forcing_hypotheses_are_satisfiable_nontrivially :
    ∃ (F π : ℚ × ℚ →ₗ[ℚ] ℚ × ℚ) (e₀ : ℚ × ℚ),
      e₀ ≠ 0 ∧ π ≠ 0 ∧ F e₀ = e₀ ∧ (∀ v, π (F v) = F (π v)) ∧
      (∀ v, F (π v) = (-1 : ℚ) • π v) ∧ π e₀ = 0 := by
  refine ⟨(LinearMap.fst ℚ ℚ ℚ).prod (-(LinearMap.snd ℚ ℚ ℚ)),
          (0 : ℚ × ℚ →ₗ[ℚ] ℚ).prod (LinearMap.snd ℚ ℚ ℚ), (1, 0), ?_, ?_, ?_, ?_, ?_, ?_⟩
  · simp [Prod.ext_iff]
  · intro h
    have := congrArg (fun f => (f : ℚ × ℚ →ₗ[ℚ] ℚ × ℚ) (0, 1)) h
    simp at this
  · simp
  · intro v; simp
  · intro v; simp
  · simp [Prod.ext_iff]

/-! ## 3. The second forcing: parity of the functional equation -/

/-- **A `w = -1` orbit has `L(f,1) = 0` for parity reasons alone.**

If `L` satisfies the functional equation `L s = w * L (2 - s)` with `w = -1`, then the
central value vanishes. Combined with Gross 1987 (`f` visible iff `L(f,1) L(f ⊗ χ₋₄,1) ≠ 0`),
this predicts invisibility of every `w = -1` orbit from *any* base point. So the vacuity of
the `w = -1` half is not an artifact of choosing `j = 1728`: changing the base point cannot
make that half testable. -/
theorem odd_functional_equation_forces_central_zero
    (L : ℝ → ℝ) (w : ℝ) (hfe : ∀ s, L s = w * L (2 - s)) (hw : w = -1) : L 1 = 0 := by
  have h := hfe 1
  rw [hw] at h
  have h21 : (2 : ℝ) - 1 = 1 := by norm_num
  rw [h21] at h
  linarith

/-- Control for `odd_functional_equation_forces_central_zero`: with `w = +1` the functional
equation permits a nonzero central value, so the previous theorem really uses `w = -1`. -/
theorem even_functional_equation_permits_nonzero :
    ∃ (L : ℝ → ℝ) (w : ℝ), w = 1 ∧ (∀ s, L s = w * L (2 - s)) ∧ L 1 ≠ 0 := by
  refine ⟨fun _ => 1, 1, rfl, fun s => by norm_num, ?_⟩
  norm_num

/-! ## 4. Kernel audit -/

#print axioms ANSE.PaperC_ForcedVisibility.two_smul_eq_zero_iff
#print axioms ANSE.PaperC_ForcedVisibility.frobenius_forces_vanishing
#print axioms ANSE.PaperC_ForcedVisibility.frobenius_forcing_hypotheses_are_satisfiable_nontrivially
#print axioms ANSE.PaperC_ForcedVisibility.frobenius_forces_nothing_at_w_one
#print axioms ANSE.PaperC_ForcedVisibility.odd_functional_equation_forces_central_zero
#print axioms ANSE.PaperC_ForcedVisibility.even_functional_equation_permits_nonzero

end ANSE.PaperC_ForcedVisibility
