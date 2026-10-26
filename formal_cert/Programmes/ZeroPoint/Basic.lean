import Mathlib.Analysis.SpecialFunctions.ExpDeriv
import Mathlib.Analysis.SpecialFunctions.Sqrt
import Mathlib.Analysis.Calculus.Deriv.Inv
import Mathlib.Analysis.Complex.Basic
import Mathlib.Tactic

/-!
# P2 zero-point energy: exact identities behind the curvature analysis at the triangular point

Programmes 2026-10-25, lane P2 (gate G2). These are the finite / algebraic facts that the Tier X curvature analysis of
`results/programmes/2026-10-25/P2/PROOF.md` uses. Nothing here is about the zero-point energy itself, and nothing
here proves or refutes QU-1 (which G1 refuted numerically).

Setting. A unit-covolume planar lattice of shape `τ = x + i y` has basis `a₁ = (1/√y, 0)`, `a₂ = (x/√y, √y)`, so
`|m a₁ + n a₂|² = Q m n x y := ((m + n x)² + n² y²)/y`. The hyperbolic Laplacian is `Δ = y² (∂ₓ² + ∂ᵧ²)`.

* `hasDerivAt_Q_x`, `hasDerivAt_Q_y`, `hasDerivAt_Qx_x`, `hasDerivAt_Qy_y`: the four partial derivatives of `Q`
  (as `HasDerivAt` facts in each variable, `y ≠ 0`).
* `lap_Q` : `y² (Qₓₓ + Qᵧᵧ) = 2 Q`, and `grad_Q` : `y² (Qₓ² + Qᵧ²) = Q²`.
* `lap_comp` : hence, for any values `f₁ = f'(Q)`, `f₂ = f''(Q)`, the chain-rule expression of `Δ (f ∘ Q)` equals
  `Q² f₂ + 2 Q f₁` (the term-wise curvature of a pair energy `Σ f(|R|²)` is the lattice sum of `h(u) = (u² f'(u))'`).
* `gauss_f'`, `gauss_h` : for `f(u) = exp(-π a u)`, `f'` and `h = (u² f')' = (-2π a u + π² a² u²) exp(-π a u)`.
* `m2_f'`, `m2_h` : for the second-moment (sum-rule) density `f(u) = (-4πa + 4π²a² u) exp(-π a u)` (the Laplacian of
  the Gaussian, radial form), `f' = (8π²a² - 4π³a³ u) exp(-π a u)` and
  `h = (16π²a² u - 20π³a³ u² + 4π⁴a⁴ u³) exp(-π a u)`.
* `rot120_comm_symm` : a symmetric `2×2` real matrix commuting with the rotation by 120° is scalar;
  `rot120_fixed_vec` : a vector fixed by that rotation is zero.
* `rho_sq`, `rho_sq_mul_rot` : `ρ = 1/2 + i √3/2` satisfies `ρ² = ρ - 1` (so `γ τ = (τ - 1)/τ`, an element of
  `SL₂(ℤ)`, fixes `ρ`) and `ρ² · (-1/2 - i √3/2) = 1`, i.e. `γ'(ρ) = ρ⁻² = -1/2 - i √3/2` is the rotation by -120°;
  `hasDerivAt_gamma` gives `γ'(ρ) = 1/ρ²` as a complex derivative.
* `deriv_at_one_of_inversion` : if `f(1/α) = α f(α)` for `α > 0` and `f` is differentiable at `1`, then
  `f'(1) = -f(1)/2` (used for `S(1) = θ(1)/(2π)`, hence `⟨tr D⟩ = 4π - 2π θ_L(1)` for the Gaussian with `a = 1`;
  the Jacobi identity for `θ_L` itself is not formalised).

Not formalised (Tier C glue): that `E_zp(τ)` is invariant under `SL₂(ℤ)` (the lattice is unchanged up to rotation),
that it is C² near `ρ`, and the chain rule that turns the `γ`-invariance into `Jᵀ ∇²E J = ∇²E`, `Jᵀ ∇E = ∇E` with
`J` the rotation above; with `rot120_comm_symm` and `rot120_fixed_vec` this gives a vanishing gradient and an
isotropic Hessian at `ρ`, so the sign of `ΔE(ρ)` decides local minimum versus local maximum.
-/

namespace ProgZeroPoint

/-- Squared length of `m a₁ + n a₂` in the unit-covolume lattice of shape `x + i y`. -/
noncomputable def Q (m n x y : ℝ) : ℝ := ((m + n * x) ^ 2 + n ^ 2 * y ^ 2) / y

theorem hasDerivAt_Q_x (m n x y : ℝ) :
    HasDerivAt (fun t => Q m n t y) (2 * n * (m + n * x) / y) x := by
  have h1 : HasDerivAt (fun t => m + n * t) n x := by
    simpa using ((hasDerivAt_id x).const_mul n).const_add m
  have h2 := ((h1.mul h1).add_const (n ^ 2 * y ^ 2)).div_const y
  convert h2 using 1
  · funext t
    simp only [Q, Pi.mul_apply]
    ring
  · ring

theorem hasDerivAt_Q_y (m n x y : ℝ) (hy : y ≠ 0) :
    HasDerivAt (fun t => Q m n x t) (n ^ 2 - (m + n * x) ^ 2 / y ^ 2) y := by
  have hc : HasDerivAt (fun t => (m + n * x) ^ 2 + n ^ 2 * (t * t)) (n ^ 2 * (1 * y + y * 1)) y := by
    have := (((hasDerivAt_id y).mul (hasDerivAt_id y)).const_mul (n ^ 2)).const_add ((m + n * x) ^ 2)
    simpa using this
  have h2 := hc.div (hasDerivAt_id y) hy
  convert h2 using 1
  · funext t
    simp only [Q, Pi.div_apply, id]
    ring
  · simp only [id]
    field_simp
    ring

theorem hasDerivAt_Qx_x (m n x y : ℝ) :
    HasDerivAt (fun t => 2 * n * (m + n * t) / y) (2 * n ^ 2 / y) x := by
  have h1 : HasDerivAt (fun t => m + n * t) n x := by
    simpa using ((hasDerivAt_id x).const_mul n).const_add m
  have h2 := (h1.const_mul (2 * n)).div_const y
  convert h2 using 1
  ring

theorem hasDerivAt_Qy_y (m n x y : ℝ) (hy : y ≠ 0) :
    HasDerivAt (fun t => n ^ 2 - (m + n * x) ^ 2 / t ^ 2) (2 * (m + n * x) ^ 2 / y ^ 3) y := by
  have hd : HasDerivAt (fun t : ℝ => t * t) (1 * y + y * 1) y := (hasDerivAt_id y).mul (hasDerivAt_id y)
  have hyy : y * y ≠ 0 := mul_ne_zero hy hy
  have h2 := ((hasDerivAt_const y ((m + n * x) ^ 2)).div hd hyy).const_sub (n ^ 2)
  convert h2 using 1
  · funext t
    simp only [Pi.div_apply]
    ring
  · field_simp
    ring

theorem lap_Q (m n x y : ℝ) (hy : y ≠ 0) :
    y ^ 2 * (2 * n ^ 2 / y + 2 * (m + n * x) ^ 2 / y ^ 3) = 2 * Q m n x y := by
  simp only [Q]
  field_simp
  ring

theorem grad_Q (m n x y : ℝ) (hy : y ≠ 0) :
    y ^ 2 * ((2 * n * (m + n * x) / y) ^ 2 + (n ^ 2 - (m + n * x) ^ 2 / y ^ 2) ^ 2) = (Q m n x y) ^ 2 := by
  simp only [Q]
  field_simp
  ring

/-- Chain rule bookkeeping: `Δ (f ∘ Q) = y² [f''(Q) (Qₓ² + Qᵧ²) + f'(Q) (Qₓₓ + Qᵧᵧ)] = Q² f''(Q) + 2 Q f'(Q)`. -/
theorem lap_comp (m n x y f1 f2 : ℝ) (hy : y ≠ 0) :
    y ^ 2 * (f2 * ((2 * n * (m + n * x) / y) ^ 2 + (n ^ 2 - (m + n * x) ^ 2 / y ^ 2) ^ 2)
        + f1 * (2 * n ^ 2 / y + 2 * (m + n * x) ^ 2 / y ^ 3))
      = (Q m n x y) ^ 2 * f2 + 2 * Q m n x y * f1 := by
  have h1 := lap_Q m n x y hy
  have h2 := grad_Q m n x y hy
  linear_combination f2 * h2 + f1 * h1

theorem gauss_f' (a u : ℝ) :
    HasDerivAt (fun v => Real.exp (-(Real.pi * a) * v)) (-(Real.pi * a) * Real.exp (-(Real.pi * a) * u)) u := by
  have hl : HasDerivAt (fun v => -(Real.pi * a) * v) (-(Real.pi * a)) u := by
    simpa using (hasDerivAt_id u).const_mul (-(Real.pi * a))
  have h := hl.exp
  convert h using 1
  ring

theorem gauss_h (a u : ℝ) :
    HasDerivAt (fun v => v ^ 2 * (-(Real.pi * a) * Real.exp (-(Real.pi * a) * v)))
      ((-2 * Real.pi * a * u + Real.pi ^ 2 * a ^ 2 * u ^ 2) * Real.exp (-(Real.pi * a) * u)) u := by
  have hv : HasDerivAt (fun v : ℝ => v * v) (1 * u + u * 1) u := (hasDerivAt_id u).mul (hasDerivAt_id u)
  have h := hv.mul ((gauss_f' a u).const_mul (-(Real.pi * a)))
  convert h using 1
  · funext v
    simp only [Pi.mul_apply]
    ring
  · ring

/-- Radial Laplacian of the Gaussian in the variable `u = r²`: `ΔV = 4 (u g')' = (-4πa + 4π²a²u) e^{-πau}`. -/
noncomputable def m2f (a u : ℝ) : ℝ := (-4 * Real.pi * a + 4 * Real.pi ^ 2 * a ^ 2 * u) * Real.exp (-(Real.pi * a) * u)

noncomputable def m2f' (a u : ℝ) : ℝ :=
  (8 * Real.pi ^ 2 * a ^ 2 - 4 * Real.pi ^ 3 * a ^ 3 * u) * Real.exp (-(Real.pi * a) * u)

theorem m2_f' (a u : ℝ) : HasDerivAt (fun v => m2f a v) (m2f' a u) u := by
  have hl : HasDerivAt (fun v => -4 * Real.pi * a + 4 * Real.pi ^ 2 * a ^ 2 * v) (4 * Real.pi ^ 2 * a ^ 2) u := by
    simpa using ((hasDerivAt_id u).const_mul (4 * Real.pi ^ 2 * a ^ 2)).const_add (-4 * Real.pi * a)
  have h := hl.mul (gauss_f' a u)
  unfold m2f m2f'
  convert h using 1
  ring

theorem m2_h (a u : ℝ) :
    HasDerivAt (fun v => v ^ 2 * m2f' a v)
      ((16 * Real.pi ^ 2 * a ^ 2 * u - 20 * Real.pi ^ 3 * a ^ 3 * u ^ 2 + 4 * Real.pi ^ 4 * a ^ 4 * u ^ 3)
        * Real.exp (-(Real.pi * a) * u)) u := by
  have hl : HasDerivAt (fun v => 8 * Real.pi ^ 2 * a ^ 2 - 4 * Real.pi ^ 3 * a ^ 3 * v)
      (-(4 * Real.pi ^ 3 * a ^ 3)) u := by
    simpa using ((hasDerivAt_id u).const_mul (4 * Real.pi ^ 3 * a ^ 3)).const_sub (8 * Real.pi ^ 2 * a ^ 2)
  have hf : HasDerivAt (fun v => m2f' a v)
      ((-(4 * Real.pi ^ 3 * a ^ 3)) * Real.exp (-(Real.pi * a) * u)
        + (8 * Real.pi ^ 2 * a ^ 2 - 4 * Real.pi ^ 3 * a ^ 3 * u) * (-(Real.pi * a) * Real.exp (-(Real.pi * a) * u))) u := by
    unfold m2f'
    exact hl.mul (gauss_f' a u)
  have hv : HasDerivAt (fun v : ℝ => v * v) (1 * u + u * 1) u := (hasDerivAt_id u).mul (hasDerivAt_id u)
  have h := hv.mul hf
  convert h using 1
  · funext v
    simp only [Pi.mul_apply]
    ring
  · unfold m2f'
    ring

/-- A symmetric `2×2` matrix `[[p, q], [q, r]]` commuting with the rotation `[[-1/2, -s], [s, -1/2]]`, `s² = 3/4`
(the rotation by 120°), is scalar. The two hypotheses are the (1,1) and (1,2) entries of `R H = H R`. -/
theorem rot120_comm_symm (p q r s : ℝ) (hs : s ^ 2 = 3 / 4)
    (h11 : -1 / 2 * p + -s * q = p * (-1 / 2) + q * s)
    (h12 : -1 / 2 * q + -s * r = p * -s + q * (-1 / 2)) :
    q = 0 ∧ r = p := by
  have hs0 : s ≠ 0 := by
    intro h
    rw [h] at hs
    norm_num at hs
  constructor
  · have : s * q = 0 := by linarith
    rcases mul_eq_zero.mp this with h | h
    · exact absurd h hs0
    · exact h
  · have : s * (r - p) = 0 := by linarith
    rcases mul_eq_zero.mp this with h | h
    · exact absurd h hs0
    · linarith

/-- A vector fixed by the rotation by 120° is zero. -/
theorem rot120_fixed_vec (g1 g2 s : ℝ) (hs : s ^ 2 = 3 / 4)
    (e1 : -1 / 2 * g1 + -s * g2 = g1) (e2 : s * g1 + -1 / 2 * g2 = g2) :
    g1 = 0 ∧ g2 = 0 := by
  have h1 : g1 = 0 := by linear_combination (s * e2 - 3 / 2 * e1 - g1 * hs) / 3
  refine ⟨h1, ?_⟩
  linear_combination (-(s * e1) - 3 / 2 * e2 - g2 * hs) / 3

theorem sqrt3_half_sq : (Real.sqrt 3 / 2) ^ 2 = 3 / 4 := by
  rw [div_pow, Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 3)]
  norm_num

/-- The triangular point `ρ = 1/2 + i √3/2`. -/
noncomputable def rho : ℂ := ⟨1 / 2, Real.sqrt 3 / 2⟩

theorem rho_sq : rho ^ 2 = rho - 1 := by
  have h3 : Real.sqrt 3 * Real.sqrt 3 = 3 := Real.mul_self_sqrt (by norm_num)
  apply Complex.ext <;> simp [rho, sq] <;> nlinarith [h3]

theorem rho_ne_zero : rho ≠ 0 := by
  intro h
  have := congrArg Complex.re h
  simp [rho] at this

/-- `γ τ = (τ - 1)/τ` fixes `ρ`. -/
theorem gamma_fixes_rho : (rho - 1) / rho = rho := by
  rw [← rho_sq, sq, mul_div_assoc, div_self rho_ne_zero, mul_one]

/-- `ρ² · (-1/2 - i √3/2) = 1`: `γ'(ρ) = ρ⁻² = -1/2 - i √3/2`, the rotation by -120°. -/
theorem rho_sq_mul_rot : rho ^ 2 * (⟨-1 / 2, -(Real.sqrt 3 / 2)⟩ : ℂ) = 1 := by
  have h3 : Real.sqrt 3 * Real.sqrt 3 = 3 := Real.mul_self_sqrt (by norm_num)
  rw [rho_sq]
  apply Complex.ext <;> simp [rho] <;> nlinarith [h3]

theorem hasDerivAt_gamma : HasDerivAt (fun τ : ℂ => (τ - 1) / τ) (1 / rho ^ 2) rho := by
  have h := ((hasDerivAt_id rho).sub_const 1).div (hasDerivAt_id rho) rho_ne_zero
  convert h using 1
  · funext τ
    simp only [Pi.div_apply, id]
  · simp only [id]
    ring

/-- Inversion identity at the self-dual point: if `f (1/α) = α f(α)` for all `α > 0` (the Jacobi identity
`θ_L(1/α) = α θ_L(α)` of a unit-covolume planar lattice, whose dual is a rotation of `L`) and `f` is differentiable
at `1`, then `f'(1) = -f(1)/2`. With `S(α) = Σ |P|² e^{-πα|P|²} = -θ'(α)/π` this gives `S(1) = θ(1)/(2π)` and hence the
Gaussian (`a = 1`) phonon sum rule `⟨tr D⟩ = 4π - 2π θ_L(1)`. -/
theorem deriv_at_one_of_inversion (f : ℝ → ℝ) (d : ℝ) (hf : HasDerivAt f d 1)
    (hinv : ∀ α : ℝ, 0 < α → f (1 / α) = α * f α) : d = -f 1 / 2 := by
  have hg : HasDerivAt (fun α : ℝ => α⁻¹) (-1) 1 := by
    simpa using hasDerivAt_inv (one_ne_zero : (1 : ℝ) ≠ 0)
  have hf' : HasDerivAt f d ((fun α : ℝ => α⁻¹) 1) := by simpa using hf
  have h1 : HasDerivAt (f ∘ fun α : ℝ => α⁻¹) (d * -1) 1 := hf'.comp 1 hg
  have h2 : HasDerivAt (fun α : ℝ => α * f α) (1 * f 1 + 1 * d) 1 := by
    have h := (hasDerivAt_id (1 : ℝ)).mul hf
    convert h using 1
    · funext α
      simp only [Pi.mul_apply, id]
    · simp only [id]
  have heq : (f ∘ fun α : ℝ => α⁻¹) =ᶠ[nhds 1] (fun α : ℝ => α * f α) := by
    filter_upwards [Ioi_mem_nhds (one_pos : (0 : ℝ) < 1)] with α hα
    simp only [Function.comp]
    rw [← one_div]
    exact hinv α hα
  have h3 : HasDerivAt (f ∘ fun α : ℝ => α⁻¹) (1 * f 1 + 1 * d) 1 := h2.congr_of_eventuallyEq heq
  have := h1.unique h3
  linarith

end ProgZeroPoint

#print axioms ProgZeroPoint.deriv_at_one_of_inversion
#print axioms ProgZeroPoint.hasDerivAt_Q_x
#print axioms ProgZeroPoint.hasDerivAt_Q_y
#print axioms ProgZeroPoint.hasDerivAt_Qx_x
#print axioms ProgZeroPoint.hasDerivAt_Qy_y
#print axioms ProgZeroPoint.lap_Q
#print axioms ProgZeroPoint.grad_Q
#print axioms ProgZeroPoint.lap_comp
#print axioms ProgZeroPoint.gauss_f'
#print axioms ProgZeroPoint.gauss_h
#print axioms ProgZeroPoint.m2_f'
#print axioms ProgZeroPoint.m2_h
#print axioms ProgZeroPoint.rot120_comm_symm
#print axioms ProgZeroPoint.rot120_fixed_vec
#print axioms ProgZeroPoint.sqrt3_half_sq
#print axioms ProgZeroPoint.rho_sq
#print axioms ProgZeroPoint.gamma_fixes_rho
#print axioms ProgZeroPoint.rho_sq_mul_rot
#print axioms ProgZeroPoint.hasDerivAt_gamma
