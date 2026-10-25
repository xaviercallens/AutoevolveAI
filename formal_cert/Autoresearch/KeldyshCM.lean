import Autoresearch.Yukawa

/-!
# Autoresearch 2026-10-25, H3L: positive exponential mixtures are admissible; the Rytova–Keldysh mixture

**Generic lemma (`laplace_admissible`).** Let `μ` be a measure on a measurable space, `k, m` measurable with
`k ≥ 0`, `m ≥ 0` `μ`-a.e., and suppose `x ↦ k x ^ n * exp (-(c * k x)) * m x` is `μ`-integrable for every `n : ℕ`
and every `c > 0`. Then `g t = ∫ exp (-(t * k x)) * m x ∂μ` is `AdmissiblePotential` (upstream's definition:
`C^∞` on `(0, ∞)`, `g ≥ 0`, `(-1)^r g^{(r)} ≥ 0`). This covers Laplace transforms of positive measures
(`k = id`), Gaussian mixtures in `t = r²` (`k a = 1/(4a)`), and finite positive combinations (Dirac / finite `μ`).

**Instance (`keldysh_admissible`).** The Rytova–Keldysh potential in the variable `t = r²`, *defined here* by its
Gaussian-mixture representation `keldysh r₀ t = ∫_{a>0} w(a)/(2a) · exp(-t/(4a)) da` with
`w(a) = (1/r₀) erfcx(√a / r₀)` and `erfcx x := (2/√π) ∫_{y>0} exp(-(y² + 2 x y)) dy` (the standard integral form of
`e^{x²} erfc x`; Mathlib at this pin has no `erfc`). The identification of this mixture with the Struve form
`(π/(2r₀)) [H₀(r/r₀) − Y₀(r/r₀)]` is NOT formalised (Tier C/X, see `results/autoresearch/2026-10-25/H3/NOTE.md`).

Everything about the triangular lattice is conditional on upstream's `universal_energy_minimum` (AI-generated,
not peer reviewed) and on definition fidelity.
-/

namespace AutoresearchKeldysh

open MeasureTheory Set Filter Topology OAI.AtomicTriangular TriangularRiesz AutoresearchYukawa

section Generic

variable {α : Type*} [MeasurableSpace α]

/-- Hypotheses of the generic lemma. -/
structure MixtureData (μ : Measure α) (k m : α → ℝ) : Prop where
  k_meas : Measurable k
  m_meas : Measurable m
  k_nonneg : ∀ᵐ x ∂μ, 0 ≤ k x
  m_nonneg : ∀ᵐ x ∂μ, 0 ≤ m x
  integrable : ∀ (n : ℕ) (c : ℝ), 0 < c → Integrable (fun x => k x ^ n * Real.exp (-(c * k x)) * m x) μ

/-- The candidate `n`-th derivative `∫ (-k)^n e^{-t k} m dμ`. -/
noncomputable def G (μ : Measure α) (k m : α → ℝ) (n : ℕ) (t : ℝ) : ℝ :=
  ∫ x, (-(k x)) ^ n * Real.exp (-(t * k x)) * m x ∂μ

variable {μ : Measure α} {k m : α → ℝ}

lemma integrand_meas (h : MixtureData μ k m) (n : ℕ) (t : ℝ) :
    AEStronglyMeasurable (fun x => (-(k x)) ^ n * Real.exp (-(t * k x)) * m x) μ := by
  have hk := h.k_meas
  have hm := h.m_meas
  exact (by fun_prop : Measurable fun x => (-(k x)) ^ n * Real.exp (-(t * k x)) * m x).aestronglyMeasurable

lemma norm_integrand {n : ℕ} {t kx mx : ℝ} (hk : 0 ≤ kx) (hm : 0 ≤ mx) :
    ‖(-kx) ^ n * Real.exp (-(t * kx)) * mx‖ = kx ^ n * Real.exp (-(t * kx)) * mx := by
  rw [Real.norm_eq_abs, abs_mul, abs_mul, abs_pow, abs_neg, abs_of_nonneg hk, abs_of_nonneg hm,
    abs_of_pos (Real.exp_pos _)]

lemma integrable_integrand (h : MixtureData μ k m) (n : ℕ) {t : ℝ} (ht : 0 < t) :
    Integrable (fun x => (-(k x)) ^ n * Real.exp (-(t * k x)) * m x) μ := by
  refine (h.integrable n t ht).mono' (integrand_meas h n t) ?_
  filter_upwards [h.k_nonneg, h.m_nonneg] with x hkx hmx
  exact (norm_integrand hkx hmx).le

/-- Differentiation under the integral sign. -/
lemma hasDerivAt_G (h : MixtureData μ k m) (n : ℕ) {t : ℝ} (ht : 0 < t) :
    HasDerivAt (G μ k m n) (G μ k m (n + 1) t) t := by
  have hs : Ioi (t / 2) ∈ 𝓝 t := Ioi_mem_nhds (by linarith)
  have key := hasDerivAt_integral_of_dominated_loc_of_deriv_le (μ := μ) (x₀ := t)
    (F := fun s x => (-(k x)) ^ n * Real.exp (-(s * k x)) * m x)
    (F' := fun s x => (-(k x)) ^ (n + 1) * Real.exp (-(s * k x)) * m x)
    (bound := fun x => k x ^ (n + 1) * Real.exp (-(t / 2 * k x)) * m x) hs
    (Eventually.of_forall fun s => integrand_meas h n s)
    (integrable_integrand h n ht)
    (integrand_meas h (n + 1) t)
    (by
      filter_upwards [h.k_nonneg, h.m_nonneg] with x hkx hmx
      intro s hs'
      rw [norm_integrand hkx hmx]
      have hst : t / 2 * k x ≤ s * k x := mul_le_mul_of_nonneg_right (le_of_lt hs') hkx
      have he : Real.exp (-(s * k x)) ≤ Real.exp (-(t / 2 * k x)) := Real.exp_le_exp.mpr (by linarith)
      have hp : 0 ≤ k x ^ (n + 1) := pow_nonneg hkx _
      exact mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left he hp) hmx)
    (h.integrable (n + 1) (t / 2) (by linarith))
    (Eventually.of_forall fun x s _ => by
      have h1 : HasDerivAt (fun y => -(y * k x)) (-(k x)) s := (hasDerivAt_mul_const (k x)).neg
      have h2 := (h1.exp.const_mul ((-(k x)) ^ n)).mul_const (m x)
      convert h2 using 1
      ring)
  exact key.2

lemma deriv_G_eqOn (h : MixtureData μ k m) (n : ℕ) :
    EqOn (deriv (G μ k m n)) (G μ k m (n + 1)) (Ioi 0) :=
  fun _ ht => (hasDerivAt_G h n ht).deriv

lemma contDiffOn_G (h : MixtureData μ k m) : ∀ (N n : ℕ), ContDiffOn ℝ N (G μ k m n) (Ioi 0) := by
  intro N
  induction N with
  | zero =>
    intro n
    rw [Nat.cast_zero, contDiffOn_zero]
    exact fun t ht => (hasDerivAt_G h n ht).continuousAt.continuousWithinAt
  | succ N ih =>
    intro n
    rw [Nat.cast_succ, contDiffOn_succ_iff_deriv_of_isOpen isOpen_Ioi]
    refine ⟨fun t ht => (hasDerivAt_G h n ht).differentiableAt.differentiableWithinAt, ?_, ?_⟩
    · intro hω
      exact absurd hω (by simp)
    · exact (ih (n + 1)).congr (fun t ht => deriv_G_eqOn h n ht)

lemma iteratedDeriv_G (h : MixtureData μ k m) :
    ∀ n : ℕ, EqOn (iteratedDeriv n (G μ k m 0)) (G μ k m n) (Ioi 0) := by
  intro n
  induction n with
  | zero => intro t _; simp
  | succ n ih =>
    intro t ht
    rw [iteratedDeriv_succ]
    have hev : iteratedDeriv n (G μ k m 0) =ᶠ[𝓝 t] G μ k m n :=
      Filter.eventuallyEq_of_mem (isOpen_Ioi.mem_nhds ht) ih
    rw [hev.deriv_eq]
    exact deriv_G_eqOn h n ht

lemma G_sign (h : MixtureData μ k m) (n : ℕ) (t : ℝ) : 0 ≤ (-1 : ℝ) ^ n * G μ k m n t := by
  unfold G
  rw [← integral_const_mul]
  refine integral_nonneg_of_ae ?_
  filter_upwards [h.k_nonneg, h.m_nonneg] with x hkx hmx
  have e1 : (-1 : ℝ) ^ n * (-(k x)) ^ n = k x ^ n := by rw [← mul_pow]; simp
  have : (-1 : ℝ) ^ n * ((-(k x)) ^ n * Real.exp (-(t * k x)) * m x) =
      k x ^ n * Real.exp (-(t * k x)) * m x := by rw [← e1]; ring
  simp only [Pi.zero_apply]
  rw [this]
  exact mul_nonneg (mul_nonneg (pow_nonneg hkx _) (Real.exp_pos _).le) hmx

/-- **H3L, generic lemma.** A positive exponential mixture `t ↦ ∫ e^{-t k} m dμ` with all moments
`∫ k^n e^{-c k} m dμ` finite (`c > 0`) is `AdmissiblePotential`; its derivatives are the differentiated integrals. -/
theorem laplace_admissible (h : MixtureData μ k m) :
    AdmissiblePotential (fun t => ∫ x, Real.exp (-(t * k x)) * m x ∂μ) := by
  have hg : (fun t => ∫ x, Real.exp (-(t * k x)) * m x ∂μ) = G μ k m 0 := by
    funext t
    simp [G]
  rw [hg]
  refine ⟨contDiffOn_infty.mpr (fun N => contDiffOn_G h N 0), fun t _ => ?_, fun r t ht => ?_⟩
  · simpa using G_sign h 0 t
  · rw [iteratedDeriv_G h r ht]
    exact G_sign h r t

/-- The derivative formula, stated explicitly: `g^{(n)}(t) = ∫ (-k)^n e^{-t k} m dμ` for `t > 0`. -/
theorem laplace_iteratedDeriv (h : MixtureData μ k m) (n : ℕ) {t : ℝ} (ht : 0 < t) :
    iteratedDeriv n (fun t => ∫ x, Real.exp (-(t * k x)) * m x ∂μ) t =
      ∫ x, (-(k x)) ^ n * Real.exp (-(t * k x)) * m x ∂μ := by
  have hg : (fun t => ∫ x, Real.exp (-(t * k x)) * m x ∂μ) = G μ k m 0 := by
    funext t
    simp [G]
  rw [hg]
  exact iteratedDeriv_G h n ht

end Generic

/-! ## Instances and controls of the generic lemma -/

/-- **Positive control / instance.** `exp(-ε t)` is admissible for `ε ≥ 0` (Dirac mixture). -/
theorem expNeg_admissible {ε : ℝ} (hε : 0 ≤ ε) : AdmissiblePotential (fun t => Real.exp (-(ε * t))) := by
  have hd : MixtureData (Measure.dirac ()) (fun _ : Unit => ε) (fun _ => 1) :=
    { k_meas := measurable_const
      m_meas := measurable_const
      k_nonneg := Eventually.of_forall fun _ => hε
      m_nonneg := Eventually.of_forall fun _ => zero_le_one
      integrable := fun n c _ => integrable_const _ }
  refine admissible_congr (laplace_admissible hd) (fun t _ => ?_)
  simp only [integral_const, mul_one, smul_eq_mul]
  simp [Measure.real, mul_comm]

/-- **Negative control.** The signed mixture `e^{-t} - 2 e^{-2t}` (weights `1, -2`) is not admissible:
it is negative at `t = log (3/2)`. So the positivity hypothesis `m ≥ 0` cannot be dropped. -/
noncomputable def signedMix (t : ℝ) : ℝ := Real.exp (-t) - 2 * Real.exp (-(2 * t))

theorem signedMix_neg : signedMix (Real.log (3 / 2)) < 0 := by
  unfold signedMix
  rw [show -(2 * Real.log (3 / 2)) = -Real.log (3 / 2) + -Real.log (3 / 2) by ring, Real.exp_add,
    Real.exp_neg, Real.exp_log (by norm_num)]
  norm_num

theorem signedMix_not_admissible : ¬ AdmissiblePotential signedMix := by
  intro H
  have := H.2.1 (Real.log (3 / 2)) (Real.log_pos (by norm_num))
  linarith [signedMix_neg]

/-! ## The Rytova–Keldysh mixture -/

/-- `erfcx x = e^{x²} erfc x`, through its integral form `(2/√π) ∫_{y>0} e^{-(y² + 2xy)} dy`
(substitute `s = y + x` in `e^{x²} (2/√π) ∫_{s>x} e^{-s²} ds`). -/
noncomputable def erfcx (x : ℝ) : ℝ :=
  2 / Real.sqrt Real.pi * ∫ y in Ioi (0 : ℝ), Real.exp (-(y ^ 2 + 2 * x * y))

lemma integrable_erfcx_integrand {x : ℝ} (hx : 0 ≤ x) :
    IntegrableOn (fun y => Real.exp (-(y ^ 2 + 2 * x * y))) (Ioi 0) := by
  refine ((integrable_exp_neg_mul_sq (b := 1) one_pos).integrableOn).mono'
    (by fun_prop : Continuous fun y : ℝ => Real.exp (-(y ^ 2 + 2 * x * y))).aestronglyMeasurable ?_
  refine (ae_restrict_iff' measurableSet_Ioi).mpr (Eventually.of_forall fun y hy => ?_)
  have hy' : 0 < y := hy
  rw [Real.norm_eq_abs, abs_of_pos (Real.exp_pos _)]
  exact Real.exp_le_exp.mpr (by nlinarith)

lemma erfcx_nonneg (x : ℝ) : 0 ≤ erfcx x :=
  mul_nonneg (by positivity) (setIntegral_nonneg measurableSet_Ioi fun _ _ => (Real.exp_pos _).le)

/-- `erfcx x ≤ 1` for `x ≥ 0` (Gaussian integral). -/
lemma erfcx_le_one {x : ℝ} (hx : 0 ≤ x) : erfcx x ≤ 1 := by
  unfold erfcx
  have hI : ∫ y in Ioi (0 : ℝ), Real.exp (-(y ^ 2 + 2 * x * y)) ≤ Real.sqrt Real.pi / 2 := by
    have hg := integral_gaussian_Ioi 1
    rw [div_one] at hg
    rw [← hg]
    refine setIntegral_mono_on (integrable_erfcx_integrand hx)
      ((integrable_exp_neg_mul_sq one_pos).integrableOn) measurableSet_Ioi (fun y hy => ?_)
    have hy' : 0 < y := hy
    exact Real.exp_le_exp.mpr (by nlinarith)
  have hpi : 0 < Real.sqrt Real.pi := Real.sqrt_pos.mpr Real.pi_pos
  calc _ ≤ 2 / Real.sqrt Real.pi * (Real.sqrt Real.pi / 2) :=
        mul_le_mul_of_nonneg_left hI (by positivity)
    _ = 1 := by field_simp

/-- `erfcx x ≤ 1 / (√π x)` for `x > 0` (drop `y²`). -/
lemma erfcx_le_inv {x : ℝ} (hx : 0 < x) : erfcx x ≤ 1 / (Real.sqrt Real.pi * x) := by
  unfold erfcx
  have hI : ∫ y in Ioi (0 : ℝ), Real.exp (-(y ^ 2 + 2 * x * y)) ≤ 1 / (2 * x) := by
    have he := integral_exp_mul_Ioi (a := -(2 * x)) (by linarith) 0
    have hval : -Real.exp (-(2 * x) * 0) / -(2 * x) = 1 / (2 * x) := by
      rw [mul_zero, Real.exp_zero, neg_div_neg_eq]
    rw [← hval, ← he]
    refine setIntegral_mono_on (integrable_erfcx_integrand hx.le)
      (integrableOn_exp_mul_Ioi (by linarith) 0) measurableSet_Ioi (fun y hy => ?_)
    have hy' : 0 < y := hy
    exact Real.exp_le_exp.mpr (by nlinarith)
  have hpi : 0 < Real.sqrt Real.pi := Real.sqrt_pos.mpr Real.pi_pos
  calc _ ≤ 2 / Real.sqrt Real.pi * (1 / (2 * x)) := mul_le_mul_of_nonneg_left hI (by positivity)
    _ = 1 / (Real.sqrt Real.pi * x) := by field_simp

lemma measurable_erfcx : Measurable erfcx := by
  have hf : StronglyMeasurable (fun p : ℝ × ℝ => Real.exp (-(p.2 ^ 2 + 2 * p.1 * p.2))) :=
    (by fun_prop : Continuous fun p : ℝ × ℝ => Real.exp (-(p.2 ^ 2 + 2 * p.1 * p.2))).stronglyMeasurable
  have h2 := (hf.integral_prod_right' (ν := volume.restrict (Ioi (0 : ℝ)))).measurable
  exact h2.const_mul _

/-- The Keldysh mixing weight `w(a) = (1/r₀) erfcx(√a / r₀)`. -/
noncomputable def w (r0 a : ℝ) : ℝ := 1 / r0 * erfcx (Real.sqrt a / r0)

/-- **Definition.** The Rytova–Keldysh potential in the variable `t = r²`, defined by its Gaussian mixture
`∫_{a>0} w(a)/(2a) e^{-t/(4a)} da`. (Identification with `(π/(2r₀))[H₀ − Y₀](√t/r₀)` is Tier C/X, not formalised.) -/
noncomputable def keldysh (r0 t : ℝ) : ℝ :=
  ∫ a in Ioi (0 : ℝ), w r0 a / (2 * a) * Real.exp (-t / (4 * a))

lemma measurable_w (r0 : ℝ) : Measurable (w r0) := by
  show Measurable fun a => 1 / r0 * erfcx (Real.sqrt a / r0)
  exact (measurable_erfcx.comp (by fun_prop : Measurable fun a : ℝ => Real.sqrt a / r0)).const_mul _

lemma w_nonneg {r0 : ℝ} (hr0 : 0 < r0) (a : ℝ) : 0 ≤ w r0 a :=
  mul_nonneg (by positivity) (erfcx_nonneg _)

lemma w_le {r0 : ℝ} (hr0 : 0 < r0) (a : ℝ) : w r0 a ≤ 1 / r0 :=
  mul_le_of_le_one_right (by positivity) (erfcx_le_one (by positivity))

lemma w_le_sqrt {r0 a : ℝ} (hr0 : 0 < r0) (ha : 0 < a) :
    w r0 a ≤ 1 / (Real.sqrt Real.pi * Real.sqrt a) := by
  have hsa : 0 < Real.sqrt a := Real.sqrt_pos.mpr ha
  have hpi : 0 < Real.sqrt Real.pi := Real.sqrt_pos.mpr Real.pi_pos
  unfold w
  calc 1 / r0 * erfcx (Real.sqrt a / r0) ≤ 1 / r0 * (1 / (Real.sqrt Real.pi * (Real.sqrt a / r0))) :=
        mul_le_mul_of_nonneg_left (erfcx_le_inv (by positivity)) (by positivity)
    _ = 1 / (Real.sqrt Real.pi * Real.sqrt a) := by field_simp

lemma pow_mul_exp_neg_le {u c : ℝ} (hu : 0 ≤ u) (hc : 0 < c) (N : ℕ) :
    u ^ N * Real.exp (-(c * u)) ≤ (N.factorial : ℝ) / c ^ N := by
  have hE := Real.pow_div_factorial_le_exp _ (mul_nonneg hc.le hu) N
  have hf : (0 : ℝ) < N.factorial := by exact_mod_cast Nat.factorial_pos N
  have hcN : 0 < c ^ N := pow_pos hc N
  rw [div_le_iff₀ hf, mul_pow] at hE
  rw [Real.exp_neg, le_div_iff₀ hcN]
  have hex := Real.exp_pos (c * u)
  calc u ^ N * (Real.exp (c * u))⁻¹ * c ^ N = (c ^ N * u ^ N) * (Real.exp (c * u))⁻¹ := by ring
    _ ≤ (Real.exp (c * u) * N.factorial) * (Real.exp (c * u))⁻¹ :=
        mul_le_mul_of_nonneg_right hE (inv_nonneg.mpr hex.le)
    _ = N.factorial := by field_simp

lemma rpow_neg_three_halves {a : ℝ} (ha : 0 < a) : a ^ (-(3 / 2) : ℝ) = 1 / (Real.sqrt a * a) := by
  rw [Real.sqrt_eq_rpow, ← Real.rpow_add_one ha.ne', Real.rpow_neg ha.le, one_div]
  norm_num

/-- All moments of the Keldysh mixture are finite. -/
lemma keldysh_integrable {r0 : ℝ} (hr0 : 0 < r0) (n : ℕ) {c : ℝ} (hc : 0 < c) :
    IntegrableOn (fun a => (1 / (4 * a)) ^ n * Real.exp (-(c * (1 / (4 * a)))) * (w r0 a / (2 * a)))
      (Ioi 0) := by
  set F : ℝ → ℝ := fun a => (1 / (4 * a)) ^ n * Real.exp (-(c * (1 / (4 * a)))) * (w r0 a / (2 * a))
    with hF
  have hw := measurable_w r0
  have hFm : Measurable F := by rw [hF]; fun_prop
  have hFnn : ∀ a, 0 < a → 0 ≤ F a := fun a ha => by
    rw [hF]
    exact mul_nonneg (mul_nonneg (by positivity) (Real.exp_pos _).le)
      (div_nonneg (w_nonneg hr0 a) (by positivity))
  -- near 0: bounded
  have h1 : IntegrableOn F (Ioc 0 1) := by
    refine (integrableOn_const (C := 2 * (1 / r0) * ((n + 1).factorial / c ^ (n + 1)))
      measure_Ioc_lt_top.ne).mono'
      hFm.aestronglyMeasurable ?_
    refine (ae_restrict_iff' measurableSet_Ioc).mpr (Eventually.of_forall fun a ha => ?_)
    have ha0 : 0 < a := ha.1
    rw [Real.norm_eq_abs, abs_of_nonneg (hFnn a ha0)]
    have hu : 0 ≤ 1 / (4 * a) := by positivity
    have hm : w r0 a / (2 * a) = 2 * (1 / (4 * a)) * w r0 a := by field_simp; ring
    have hFa : F a = 2 * w r0 a * ((1 / (4 * a)) ^ (n + 1) * Real.exp (-(c * (1 / (4 * a))))) := by
      rw [hF]; simp only []; rw [hm, pow_succ]; ring
    rw [hFa]
    exact mul_le_mul (mul_le_mul_of_nonneg_left (w_le hr0 a) zero_le_two) (pow_mul_exp_neg_le hu hc _)
      (mul_nonneg (pow_nonneg hu _) (Real.exp_pos _).le) (by positivity)
  -- near ∞: `≤ C a^{-3/2}`
  have h2 : IntegrableOn F (Ioi 1) := by
    refine ((integrableOn_Ioi_rpow_of_lt (by norm_num : (-(3 / 2) : ℝ) < -1) one_pos).const_mul
      (1 / (2 * Real.sqrt Real.pi))).mono' hFm.aestronglyMeasurable ?_
    refine (ae_restrict_iff' measurableSet_Ioi).mpr (Eventually.of_forall fun a ha => ?_)
    have ha1 : 1 < a := ha
    have ha0 : 0 < a := by linarith
    rw [Real.norm_eq_abs, abs_of_nonneg (hFnn a ha0), rpow_neg_three_halves ha0]
    have hu : 0 ≤ 1 / (4 * a) := by positivity
    have hu1 : 1 / (4 * a) ≤ 1 := by rw [div_le_one (by positivity)]; linarith
    have hpow : (1 / (4 * a)) ^ n ≤ 1 := pow_le_one₀ hu hu1
    have hexp : Real.exp (-(c * (1 / (4 * a)))) ≤ 1 := Real.exp_le_one_iff.mpr (by
      have : 0 ≤ c * (1 / (4 * a)) := by positivity
      linarith)
    have hsa : 0 < Real.sqrt a := Real.sqrt_pos.mpr ha0
    have hpi : 0 < Real.sqrt Real.pi := Real.sqrt_pos.mpr Real.pi_pos
    have hm : w r0 a / (2 * a) ≤ 1 / (Real.sqrt Real.pi * Real.sqrt a) / (2 * a) :=
      div_le_div_of_nonneg_right (w_le_sqrt hr0 ha0) (by positivity)
    have hmnn : 0 ≤ w r0 a / (2 * a) := div_nonneg (w_nonneg hr0 a) (by positivity)
    calc F a ≤ 1 * (w r0 a / (2 * a)) := by
          rw [hF]
          exact mul_le_mul_of_nonneg_right ((mul_le_mul hpow hexp (Real.exp_pos _).le zero_le_one).trans_eq (one_mul 1)) hmnn
      _ ≤ 1 / (Real.sqrt Real.pi * Real.sqrt a) / (2 * a) := by rw [one_mul]; exact hm
      _ = 1 / (2 * Real.sqrt Real.pi) * (1 / (Real.sqrt a * a)) := by field_simp
  have := h1.union h2
  rwa [Ioc_union_Ioi_eq_Ioi zero_le_one] at this

lemma keldysh_data {r0 : ℝ} (hr0 : 0 < r0) :
    MixtureData (volume.restrict (Ioi (0 : ℝ))) (fun a => 1 / (4 * a)) (fun a => w r0 a / (2 * a)) where
  k_meas := by fun_prop
  m_meas := by have hw := measurable_w r0; fun_prop
  k_nonneg := (ae_restrict_iff' measurableSet_Ioi).mpr (Eventually.of_forall fun a ha => by
    have ha0 : 0 < a := ha
    positivity)
  m_nonneg := (ae_restrict_iff' measurableSet_Ioi).mpr (Eventually.of_forall fun a ha => by
    have ha0 : 0 < a := ha
    exact div_nonneg (w_nonneg hr0 a) (by positivity))
  integrable := fun n c hc => keldysh_integrable hr0 n hc

/-- **H3L.** The (mixture-defined) Rytova–Keldysh potential, in the variable `t = r²`, is admissible. -/
theorem keldysh_admissible {r0 : ℝ} (hr0 : 0 < r0) : AdmissiblePotential (keldysh r0) := by
  have H := laplace_admissible (keldysh_data hr0)
  convert H using 1
  funext t
  unfold keldysh
  refine integral_congr_ae (Eventually.of_forall fun a => ?_)
  simp only []
  rw [mul_comm, show -t / (4 * a) = -(t * (1 / (4 * a))) by ring]

lemma setIntegral_Ioi_pos {f : ℝ → ℝ} (hpos : ∀ a, 0 < a → 0 < f a) (hfi : IntegrableOn f (Ioi 0)) :
    0 < ∫ a in Ioi (0 : ℝ), f a := by
  have hnn : 0 ≤ᵐ[volume.restrict (Ioi (0 : ℝ))] f :=
    (ae_restrict_iff' measurableSet_Ioi).mpr (Eventually.of_forall fun a ha => (hpos a ha).le)
  rw [setIntegral_pos_iff_support_of_nonneg_ae hnn hfi]
  have hs : Function.support f ∩ Ioi 0 = Ioi 0 := by
    ext a
    exact ⟨fun h => h.2, fun ha => ⟨(hpos a ha).ne', ha⟩⟩
  rw [hs, Real.volume_Ioi]
  exact ENNReal.zero_lt_top

lemma erfcx_pos {x : ℝ} (hx : 0 ≤ x) : 0 < erfcx x :=
  mul_pos (by positivity) (setIntegral_Ioi_pos (fun _ _ => Real.exp_pos _) (integrable_erfcx_integrand hx))

/-- **Non-vacuity.** The mixture-defined Keldysh potential is strictly positive (so the admissibility
statement is not about the zero function, as it would be if the defining integral were not integrable). -/
theorem keldysh_pos {r0 t : ℝ} (hr0 : 0 < r0) (ht : 0 < t) : 0 < keldysh r0 t := by
  unfold keldysh
  refine setIntegral_Ioi_pos (fun a ha => ?_) ?_
  · have hw : 0 < w r0 a := mul_pos (by positivity) (erfcx_pos (by positivity))
    exact mul_pos (div_pos hw (by positivity)) (Real.exp_pos _)
  · refine (keldysh_integrable hr0 0 ht).congr_fun (fun a _ => ?_) measurableSet_Ioi
    simp only [pow_zero, one_mul]
    rw [mul_comm, show -t / (4 * a) = -(t * (1 / (4 * a))) by ring]

/-- **H3L corollary** (raw energies in `[0, ∞]`). Note: the triangular-lattice Keldysh energy is expected to be
infinite (Coulomb `1/r` tail), in which case this reads `⊤ ≤ ⊤`; that is NOT proved or disproved here. -/
theorem triangular_keldysh_optimal {r0 : ℝ} (hr0 : 0 < r0) (C : Set Plane) (hC : LocallyFinite C)
    (hdens : DensityOne C) : latticeEnergy (keldysh r0) ≤ energy (keldysh r0) C :=
  (universal_energy_minimum (keldysh r0) C (keldysh_admissible hr0) hC hdens).1

/-- The Gaussian-regularised Keldysh interaction `keldysh r₀ t · e^{-ε t}`. -/
noncomputable def keldyshReg (r0 ε t : ℝ) : ℝ := keldysh r0 t * Real.exp (-(ε * t))

theorem keldyshReg_admissible {r0 ε : ℝ} (hr0 : 0 < r0) (hε : 0 ≤ ε) :
    AdmissiblePotential (keldyshReg r0 ε) :=
  admissible_congr (admissible_mul (keldysh_admissible hr0) (expNeg_admissible hε)) (fun _ _ => rfl)

theorem triangular_keldyshReg_optimal {r0 ε : ℝ} (hr0 : 0 < r0) (hε : 0 ≤ ε) (C : Set Plane)
    (hC : LocallyFinite C) (hdens : DensityOne C) :
    latticeEnergy (keldyshReg r0 ε) ≤ energy (keldyshReg r0 ε) C :=
  (universal_energy_minimum (keldyshReg r0 ε) C (keldyshReg_admissible hr0 hε) hC hdens).1

end AutoresearchKeldysh

#print axioms AutoresearchKeldysh.laplace_admissible
#print axioms AutoresearchKeldysh.laplace_iteratedDeriv
#print axioms AutoresearchKeldysh.expNeg_admissible
#print axioms AutoresearchKeldysh.signedMix_not_admissible
#print axioms AutoresearchKeldysh.erfcx_le_one
#print axioms AutoresearchKeldysh.erfcx_le_inv
#print axioms AutoresearchKeldysh.keldysh_integrable
#print axioms AutoresearchKeldysh.keldysh_admissible
#print axioms AutoresearchKeldysh.keldysh_pos
#print axioms AutoresearchKeldysh.triangular_keldysh_optimal
#print axioms AutoresearchKeldysh.keldyshReg_admissible
#print axioms AutoresearchKeldysh.triangular_keldyshReg_optimal
