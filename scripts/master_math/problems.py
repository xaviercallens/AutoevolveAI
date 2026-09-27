"""The master-math problem set, run two: locked Lean statements, not titles.

Source: the 20 problems of `results/master_math_20_problems_closed_loop_receipts.json`
(the only list that came with statements; #10 is split into its two claims),
plus the regen-only titles of the run-one regenerator
(`scripts/regenerate_10_math_problems_dspy.py`, removed in run two; its list
is preserved here as `source: regen#N`) that the local (partial) Mathlib build
can state faithfully. The rest are recorded as BLOCKED with the reason, never
replaced by a toy.

The run-one regenerator sent the model only a title, so the model wrote its
own statement (and could weaken it) and a canned auditor judged it. Here the
statement is ours and fixed; a model only supplies the proof body, which is
compiled against our statement by the kernel gate.

Every item carries:
  statement   our theorem header (proof body supplied separately)
  reference   positive control: must pass the kernel gate
  false_prop  a closed false variant; its refutation `¬ (false_prop)` must be
              kernel-proved (falsity is checked, never assumed), and the
              reference proof must NOT prove it
  fidelity    "faithful" | "proxy" | "special-case" (statement review, LL.md §7)
"""

from __future__ import annotations

TACTICS = [
    "Mathlib.Tactic.Ring",
    "Mathlib.Tactic.Linarith",
    "Mathlib.Tactic.NormNum",
    "Mathlib.Tactic.Positivity",
    "Mathlib.Tactic.FieldSimp",
]


def header(*modules: str) -> str:
    """Pinned import header: only modules whose .olean exists locally."""
    return "".join(f"import {m}\n" for m in [*modules, *TACTICS])


INNER = "Mathlib.Analysis.InnerProductSpace.Basic"

PROBLEMS: list[dict] = [
    {
        "id": "mm01_lagrange", "source": "receipts#1", "fidelity": "faithful",
        "title": "Lagrange's theorem (index multiplicativity)", "domain": "Group theory",
        "header": header("Mathlib.GroupTheory.Index", "Mathlib.Algebra.Group.PUnit",
                         "Mathlib.Data.Fintype.Card"),
        "statement": "theorem mm01_lagrange {G : Type*} [Group G] [Finite G] (H : Subgroup G) :\n"
                     "    Nat.card H * H.index = Nat.card G",
        "reference": "by exact Subgroup.card_mul_index H",
        "false_prop": "∀ (G : Type) [Group G] [Finite G] (H : Subgroup G), Nat.card H + H.index = Nat.card G",
        "refutation": "by\n  intro h\n  have := h PUnit ⊤\n  simp at this",
    },
    {
        "id": "mm02_parallelogram", "source": "receipts#2", "fidelity": "faithful",
        "title": "Parallelogram law in real inner product spaces", "domain": "Functional analysis",
        "header": header(INNER),
        "statement": "theorem mm02_parallelogram {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]\n"
                     "    (x y : E) : ‖x + y‖ ^ 2 + ‖x - y‖ ^ 2 = 2 * (‖x‖ ^ 2 + ‖y‖ ^ 2)",
        "reference": "by\n  have h := parallelogram_law_with_norm ℝ x y\n  simp only [sq]\n  linarith",
        "false_prop": "∀ x y : ℝ, ‖x + y‖ ^ 2 + ‖x - y‖ ^ 2 = ‖x‖ ^ 2 + ‖y‖ ^ 2",
        "refutation": "by\n  intro h\n  have := h 1 0\n  norm_num at this",
    },
    {
        "id": "mm03_banach", "source": "receipts#3", "fidelity": "faithful",
        "title": "Banach contraction principle (unique fixed point)", "domain": "Metric spaces",
        "header": header("Mathlib.Topology.MetricSpace.Contracting"),
        "statement": "theorem mm03_banach {X : Type*} [MetricSpace X] [CompleteSpace X] [Nonempty X]\n"
                     "    {c : NNReal} (hc : c < 1) {T : X → X} (hT : LipschitzWith c T) :\n"
                     "    ∃! x : X, T x = x",
        "reference": "by\n  have hK : ContractingWith c T := ⟨hc, hT⟩\n"
                     "  exact ⟨ContractingWith.fixedPoint T hK, hK.fixedPoint_isFixedPt,\n"
                     "    fun y hy => hK.fixedPoint_unique hy⟩",
        "false_prop": "∀ T : ℝ → ℝ, LipschitzWith 1 T → ∃! x : ℝ, T x = x",
        "refutation": "by\n  intro h\n  obtain ⟨x, -, hu⟩ := h id LipschitzWith.id\n"
                      "  have h1 := hu (x + 1) rfl\n  linarith",
    },
    {
        "id": "mm04_cr_harmonic", "source": "receipts#4", "fidelity": "proxy",
        "title": "Cauchy-Riemann implies harmonic (second-derivative algebra only)",
        "domain": "Complex analysis",
        "note": "Derivatives are free real variables; no function or differentiability appears.",
        "header": header("Mathlib.Data.Real.Basic"),
        "statement": "theorem mm04_cr_harmonic (u_xx u_yy v_xy v_yx : ℝ) (hCR1 : u_xx = v_yx)\n"
                     "    (hCR2 : u_yy = -v_xy) (hSym : v_yx = v_xy) : u_xx + u_yy = 0",
        "reference": "by rw [hCR1, hCR2, hSym]; ring",
        "false_prop": "∀ u_xx u_yy v_xy v_yx : ℝ, u_xx = v_yx → u_yy = -v_xy → u_xx + u_yy = 0",
        "refutation": "by\n  intro h\n  have := h 1 0 0 1 rfl (by norm_num)\n  norm_num at this",
    },
    {
        "id": "mm05_gauss_bonnet", "source": "receipts#5", "fidelity": "proxy",
        "title": "Gauss-Bonnet on the round sphere (K * Area = 2 pi chi, arithmetic only)",
        "domain": "Differential geometry",
        "note": "No surface or integral: K = 1/R^2 and Area = 4 pi R^2 are inserted by hand. "
                "Mathlib.Geometry.Manifold is not built locally.",
        "header": header("Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic"),
        "statement": "theorem mm05_gauss_bonnet (R : ℝ) (hR : 0 < R) :\n"
                     "    (1 / R ^ 2) * (4 * Real.pi * R ^ 2) = 2 * Real.pi * 2",
        "reference": "by\n  have : R ^ 2 ≠ 0 := by positivity\n  field_simp\n  ring",
        "false_prop": "∀ R : ℝ, (1 / R ^ 2) * (4 * Real.pi * R ^ 2) = 4 * Real.pi",
        "refutation": "by\n  intro h\n  have h0 := h 0\n  have := Real.pi_pos\n  norm_num at h0 <;> linarith",
    },
    {
        "id": "mm06_d_squared", "source": "receipts#6", "fidelity": "proxy",
        "title": "Coboundary nilpotency d^2 = 0 on one oriented 2-simplex",
        "domain": "Discrete exterior calculus",
        "note": "A single telescoping sum, not a cochain complex.",
        "header": header("Mathlib.Data.Real.Basic"),
        "statement": "theorem mm06_d_squared (f₀ f₁ f₂ : ℝ) : (f₁ - f₀) + (f₂ - f₁) + (f₀ - f₂) = 0",
        "reference": "by ring",
        "false_prop": "∀ f₀ f₁ f₂ : ℝ, (f₁ - f₀) + (f₂ - f₁) + (f₂ - f₀) = 0",
        "refutation": "by\n  intro h\n  have := h 0 0 1\n  norm_num at this",
    },
    {
        "id": "mm07_gronwall", "source": "receipts#7", "fidelity": "faithful",
        "title": "Discrete Gronwall inequality", "domain": "Dynamical systems",
        "header": header("Mathlib.Data.Real.Basic"),
        "statement": "theorem mm07_gronwall (E : ℕ → ℝ) (α : ℝ) (hα : 0 ≤ α) (hE : ∀ n, 0 ≤ E n)\n"
                     "    (h_step : ∀ n, E (n + 1) ≤ (1 + α) * E n) : ∀ n, E n ≤ (1 + α) ^ n * E 0",
        "reference": "by\n  intro n\n  induction n with\n  | zero => simp\n  | succ k ih =>\n"
                     "    calc E (k + 1) ≤ (1 + α) * E k := h_step k\n"
                     "      _ ≤ (1 + α) * ((1 + α) ^ k * E 0) :=\n"
                     "          mul_le_mul_of_nonneg_left ih (by linarith)\n"
                     "      _ = (1 + α) ^ (k + 1) * E 0 := by ring",
        "false_prop": "∀ E : ℕ → ℝ, (∀ n, 0 ≤ E n) → (∀ n, E (n + 1) ≤ 2 * E n) → ∀ n, E n ≤ E 0",
        "refutation": "by\n  intro h\n  have := h (fun n => 2 ^ n) (fun n => by positivity)\n"
                      "    (fun n => le_of_eq (by ring)) 1\n  norm_num at this",
    },
    {
        "id": "mm08_fermat", "source": "receipts#8", "fidelity": "faithful",
        "title": "Fermat's little theorem in ZMod p", "domain": "Number theory",
        "header": header("Mathlib.FieldTheory.Finite.Basic"),
        "statement": "theorem mm08_fermat (p : ℕ) [Fact p.Prime] (a : ZMod p) (ha : a ≠ 0) :\n"
                     "    a ^ (p - 1) = 1",
        "reference": "by exact ZMod.pow_card_sub_one_eq_one ha",
        "false_prop": "∀ a : ZMod 5, a ^ (5 - 1) = 1",
        "refutation": "by decide",
    },
    {
        "id": "mm09_markov", "source": "receipts#9", "fidelity": "faithful",
        "title": "Markov's inequality (Bochner integral)", "domain": "Probability",
        "note": "Upgraded from run one's pointwise proxy `(if x ≥ ε then ε else 0) ≤ x`.",
        "header": header("Mathlib.MeasureTheory.Integral.Bochner.Basic",
                         "Mathlib.MeasureTheory.Constructions.BorelSpace.Real"),
        "statement": "theorem mm09_markov {α : Type*} [MeasurableSpace α] (μ : MeasureTheory.Measure α)\n"
                     "    {f : α → ℝ} (hf_nonneg : 0 ≤ᵐ[μ] f) (hf_int : MeasureTheory.Integrable f μ)\n"
                     "    (ε : ℝ) : ε * μ.real {x | ε ≤ f x} ≤ ∫ x, f x ∂μ",
        "reference": "by exact MeasureTheory.mul_meas_ge_le_integral_of_nonneg hf_nonneg hf_int ε",
        "false_prop": "∀ (f : ℝ → ℝ) (ε : ℝ), ε * (MeasureTheory.Measure.dirac (0 : ℝ)).real {x | ε ≤ f x}\n"
                      "    ≤ (∫ x, f x ∂(MeasureTheory.Measure.dirac (0 : ℝ))) / 2",
        "refutation": "by\n  intro h\n  have := h (fun _ => 1) 1\n  simp at this\n  norm_num at this",
    },
    {
        "id": "mm10a_cauchy_schwarz", "source": "receipts#10", "fidelity": "faithful",
        "title": "Cauchy-Schwarz, signed form", "domain": "Functional analysis",
        "header": header(INNER),
        "statement": "theorem mm10a_cauchy_schwarz {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]\n"
                     "    (x y : E) : @inner ℝ E _ x y ≤ ‖x‖ * ‖y‖",
        "reference": "by exact real_inner_le_norm x y",
        "false_prop": "∀ x y : ℝ, @inner ℝ ℝ _ x y ≤ ‖x‖ * ‖y‖ - 1",
        "refutation": "by\n  intro h\n  have := h 0 0\n  simp at this\n  norm_num at this",
    },
    {
        "id": "mm10b_cauchy_schwarz_abs", "source": "receipts#10", "fidelity": "faithful",
        "title": "Cauchy-Schwarz, absolute form", "domain": "Functional analysis",
        "header": header(INNER),
        "statement": "theorem mm10b_cauchy_schwarz_abs {E : Type*} [NormedAddCommGroup E]\n"
                     "    [InnerProductSpace ℝ E] (x y : E) : |@inner ℝ E _ x y| ≤ ‖x‖ * ‖y‖",
        "reference": "by exact abs_real_inner_le_norm x y",
        "false_prop": "∀ x y : ℝ, |@inner ℝ ℝ _ x y| < ‖x‖ * ‖y‖",
        "refutation": "by\n  intro h\n  have := h 0 0\n  simp at this",
    },
    {
        "id": "mm11_ivt", "source": "receipts#11", "fidelity": "faithful",
        "title": "Intermediate value theorem", "domain": "Real analysis",
        "header": header("Mathlib.Topology.Order.IntermediateValue", "Mathlib.Topology.Instances.Real.Lemmas"),
        "statement": "theorem mm11_ivt (f : ℝ → ℝ) (a b y : ℝ) (hab : a ≤ b)\n"
                     "    (hf : ContinuousOn f (Set.Icc a b)) (hy : y ∈ Set.Icc (f a) (f b)) :\n"
                     "    ∃ x ∈ Set.Icc a b, f x = y",
        "reference": "by\n  obtain ⟨x, hx, hfx⟩ := intermediate_value_Icc hab hf hy\n  exact ⟨x, hx, hfx⟩",
        "false_prop": "∀ (f : ℝ → ℝ) (a b y : ℝ), a ≤ b → y ∈ Set.Icc (f a) (f b) →\n"
                      "    ∃ x ∈ Set.Icc a b, f x = y",
        "refutation": "by\n  intro h\n"
                      "  obtain ⟨x, -, hx⟩ := h (fun x => if x < 1 then 0 else 2) 0 1 1 (by norm_num)\n"
                      "    (by norm_num)\n"
                      "  split_ifs at hx <;> norm_num at hx",
    },
    {
        "id": "mm12_cayley_hamilton", "source": "receipts#12", "fidelity": "faithful",
        "title": "Cayley-Hamilton theorem", "domain": "Linear algebra",
        "header": header("Mathlib.LinearAlgebra.Matrix.Charpoly.Basic"),
        "statement": "theorem mm12_cayley_hamilton {n R : Type*} [Fintype n] [DecidableEq n] [CommRing R]\n"
                     "    (M : Matrix n n R) : Polynomial.aeval M M.charpoly = 0",
        "reference": "by exact Matrix.aeval_self_charpoly M",
        "false_prop": "∀ M : Matrix (Fin 1) (Fin 1) ℤ, Polynomial.aeval M (Polynomial.X : Polynomial ℤ) = 0",
        "refutation": "by\n  intro h\n  have := h 1\n  simp at this",
    },
    {
        "id": "mm13_zorn", "source": "receipts#13", "fidelity": "faithful",
        "title": "Zorn's lemma (maximal element form)", "domain": "Set theory",
        "header": header("Mathlib.Order.Zorn"),
        "statement": "theorem mm13_zorn {α : Type*} [PartialOrder α]\n"
                     "    (h : ∀ c : Set α, IsChain (· ≤ ·) c → ∃ ub, ∀ a ∈ c, a ≤ ub) :\n"
                     "    ∃ m : α, ∀ a, m ≤ a → a = m",
        "reference": "by\n  obtain ⟨m, hm⟩ := zorn_le (fun c hc => h c hc)\n"
                     "  exact ⟨m, fun a ha => le_antisymm (hm ha) ha⟩",
        "false_prop": "∀ (α : Type) [PartialOrder α], ∃ m : α, ∀ a, m ≤ a → a = m",
        "refutation": "by\n  intro h\n  obtain ⟨m, hm⟩ := h ℕ\n  have := hm (m + 1) (by omega)\n  omega",
    },
    {
        "id": "mm14_baire", "source": "receipts#14", "fidelity": "faithful",
        "title": "Baire category theorem (complete metric spaces)", "domain": "Topology",
        "header": header("Mathlib.Topology.Baire.Lemmas", "Mathlib.Topology.Baire.CompleteMetrizable",
                         "Mathlib.Topology.Instances.Real.Lemmas"),
        "statement": "theorem mm14_baire {X : Type*} [MetricSpace X] [CompleteSpace X] (f : ℕ → Set X)\n"
                     "    (ho : ∀ n, IsOpen (f n)) (hd : ∀ n, Dense (f n)) : Dense (⋂ n, f n)",
        "reference": "by exact dense_iInter_of_isOpen ho hd",
        "false_prop": "∀ f : ℕ → Set ℝ, (∀ n, IsOpen (f n)) → (∀ n, Dense (f n)) → (⋂ n, f n) = Set.univ",
        "refutation": "by\n  intro h\n"
                      "  have hu := h (fun _ => ({0}ᶜ : Set ℝ)) (fun _ => isOpen_compl_singleton)\n"
                      "    (fun _ => dense_compl_singleton 0)\n"
                      "  have h0 : (0 : ℝ) ∈ ⋂ _n : ℕ, ({0}ᶜ : Set ℝ) := by rw [hu]; trivial\n"
                      "  simp at h0",
    },
    {
        "id": "mm15_cantor", "source": "receipts#15", "fidelity": "faithful",
        "title": "Cantor's theorem (no surjection onto the power set)", "domain": "Set theory",
        "header": header("Mathlib.Logic.Function.Basic"),
        "statement": "theorem mm15_cantor {α : Type*} (f : α → Set α) : ¬ Function.Surjective f",
        "reference": "by exact Function.cantor_surjective f",
        "false_prop": "∀ (α : Type) (f : α → α), ¬ Function.Surjective f",
        "refutation": "by\n  intro h\n  exact h Unit id Function.surjective_id",
    },
    {
        "id": "mm16_primes", "source": "receipts#16", "fidelity": "faithful",
        "title": "Infinitude of primes", "domain": "Number theory",
        "header": header("Mathlib.Data.Nat.Prime.Infinite"),
        "statement": "theorem mm16_primes (n : ℕ) : ∃ p, n ≤ p ∧ Nat.Prime p",
        "reference": "by exact Nat.exists_infinite_primes n",
        "false_prop": "∃ N : ℕ, ∀ p, Nat.Prime p → p ≤ N",
        "refutation": "by\n  rintro ⟨N, hN⟩\n  obtain ⟨p, hp, hpp⟩ := Nat.exists_infinite_primes (N + 1)\n"
                      "  have := hN p hpp\n  omega",
    },
    {
        "id": "mm17_am_gm", "source": "receipts#17", "fidelity": "faithful",
        "title": "AM-GM inequality, two variables", "domain": "Inequalities",
        "header": header("Mathlib.Analysis.SpecialFunctions.Sqrt"),
        "statement": "theorem mm17_am_gm (x y : ℝ) (hx : 0 ≤ x) (hy : 0 ≤ y) :\n"
                     "    Real.sqrt (x * y) ≤ (x + y) / 2",
        "reference": "by\n  have h := Real.sqrt_le_sqrt (show x * y ≤ ((x + y) / 2) ^ 2 by\n"
                     "    nlinarith [sq_nonneg (x - y)])\n  rwa [Real.sqrt_sq (by linarith)] at h",
        "false_prop": "∀ x y : ℝ, Real.sqrt (x * y) ≤ (x + y) / 2",
        "refutation": "by\n  intro h\n  have := h (-1) (-1)\n  norm_num at this",
    },
    {
        "id": "mm18_sqrt2", "source": "receipts#18", "fidelity": "faithful",
        "title": "Irrationality of sqrt 2", "domain": "Number theory",
        "header": header("Mathlib.NumberTheory.Real.Irrational"),
        "statement": "theorem mm18_sqrt2 : Irrational (Real.sqrt 2)",
        "reference": "by exact irrational_sqrt_two",
        "false_prop": "Irrational (Real.sqrt 4)",
        "refutation": "by\n  intro h\n  apply h\n  refine ⟨2, ?_⟩\n"
                      "  rw [show (4 : ℝ) = 2 ^ 2 by norm_num, Real.sqrt_sq (by norm_num)]\n  norm_num",
    },
    {
        "id": "mm19_liouville", "source": "receipts#19", "fidelity": "faithful",
        "title": "Liouville's theorem", "domain": "Complex analysis",
        "header": header("Mathlib.Analysis.Complex.Liouville"),
        "statement": "theorem mm19_liouville (f : ℂ → ℂ) (hf : Differentiable ℂ f)\n"
                     "    (hb : Bornology.IsBounded (Set.range f)) (z w : ℂ) : f z = f w",
        "reference": "by exact hf.apply_eq_apply_of_bounded hb z w",
        "false_prop": "∀ f : ℂ → ℂ, Differentiable ℂ f → ∀ z w : ℂ, f z = f w",
        "refutation": "by\n  intro h\n  have := h id differentiable_id 0 1\n  simp at this",
    },
    {
        "id": "mm20_triangle", "source": "receipts#20", "fidelity": "faithful",
        "title": "Triangle inequality in metric spaces", "domain": "Metric spaces",
        "header": header("Mathlib.Topology.MetricSpace.Pseudo.Defs", "Mathlib.Topology.Instances.Real.Lemmas"),
        "statement": "theorem mm20_triangle {X : Type*} [MetricSpace X] (x y z : X) :\n"
                     "    dist x z ≤ dist x y + dist y z",
        "reference": "by exact dist_triangle x y z",
        "false_prop": "∀ x y z : ℝ, dist x z ≤ dist x y",
        "refutation": "by\n  intro h\n  have := h 0 0 1\n  norm_num [Real.dist_eq] at this",
    },
    {
        "id": "mm21_fta", "source": "regen#12", "fidelity": "faithful",
        "title": "Fundamental theorem of algebra", "domain": "Complex analysis / algebra",
        "header": header("Mathlib.Analysis.Complex.Polynomial.Basic"),
        "statement": "theorem mm21_fta (p : Polynomial ℂ) (hp : 0 < p.degree) : ∃ z : ℂ, p.IsRoot z",
        "reference": "by exact Complex.exists_root hp",
        "false_prop": "∀ p : Polynomial ℝ, 0 < p.degree → ∃ z : ℝ, p.IsRoot z",
        "refutation": "by\n  intro h\n"
                      "  obtain ⟨z, hz⟩ := h (Polynomial.X ^ 2 + Polynomial.C 1)\n"
                      "    (by rw [Polynomial.degree_X_pow_add_C (by norm_num)]; norm_num)\n"
                      "  simp at hz\n  nlinarith [sq_nonneg z]",
    },
    {
        "id": "mm22_picard_lindelof", "source": "regen#13", "fidelity": "faithful",
        "title": "Picard-Lindelof uniqueness for Lipschitz ODEs", "domain": "ODE",
        "header": header("Mathlib.Analysis.ODE.ExistUnique"),
        "statement": "theorem mm22_picard_lindelof (v : ℝ → ℝ → ℝ) (K : NNReal)\n"
                     "    (hv : ∀ t, LipschitzWith K (v t)) (f g : ℝ → ℝ) (a b : ℝ)\n"
                     "    (hf : ∀ t, HasDerivAt f (v t (f t)) t) (hg : ∀ t, HasDerivAt g (v t (g t)) t)\n"
                     "    (ha : f a = g a) : Set.EqOn f g (Set.Icc a b)",
        "reference": "by\n  exact ODE_solution_unique hv (fun t _ => (hf t).continuousAt.continuousWithinAt)\n"
                     "    (fun t _ => (hf t).hasDerivWithinAt)\n"
                     "    (fun t _ => (hg t).continuousAt.continuousWithinAt)\n"
                     "    (fun t _ => (hg t).hasDerivWithinAt) ha",
        "false_prop": "∀ f g : ℝ → ℝ, (∀ t, HasDerivAt f 0 t) → (∀ t, HasDerivAt g 0 t) →\n"
                      "    Set.EqOn f g (Set.Icc 0 1)",
        "refutation": "by\n  intro h\n"
                      "  have := h (fun _ => 0) (fun _ => 1) (fun t => hasDerivAt_const t 0)\n"
                      "    (fun t => hasDerivAt_const t 1) (by norm_num : (0 : ℝ) ∈ Set.Icc 0 1)\n"
                      "  norm_num at this",
    },
    {
        "id": "mm23_stokes_1d", "source": "regen#11", "fidelity": "special-case",
        "title": "Stokes' theorem in dimension one (fundamental theorem of calculus)",
        "domain": "Analysis",
        "note": "General Stokes on manifolds is not stateable here (Geometry.Manifold not built); "
                "this is the n = 1 instance, labelled as such.",
        "header": header("Mathlib.MeasureTheory.Integral.IntervalIntegral.FundThmCalculus"),
        "statement": "theorem mm23_stokes_1d (f f' : ℝ → ℝ) (a b : ℝ)\n"
                     "    (hf : ∀ x ∈ Set.uIcc a b, HasDerivAt f (f' x) x)\n"
                     "    (hint : IntervalIntegrable f' MeasureTheory.volume a b) :\n"
                     "    ∫ x in a..b, f' x = f b - f a",
        "reference": "by exact intervalIntegral.integral_eq_sub_of_hasDerivAt hf hint",
        "false_prop": "∀ f f' : ℝ → ℝ, IntervalIntegrable f' MeasureTheory.volume 0 1 →\n"
                      "    ∫ x in (0 : ℝ)..1, f' x = f 1 - f 0",
        "refutation": "by\n  intro h\n  have := h id (fun _ => 0) intervalIntegrable_const\n  simp at this",
    },
]

# Regen-only titles that cannot be stated faithfully on the local build.
BLOCKED: list[dict] = [
    {"source": "regen#14", "title": "Gromov-Witten invariants in algebraic geometry",
     "reason": "no Gromov-Witten definitions anywhere in Mathlib source"},
    {"source": "regen#15", "title": "Elliptic regularity & Sobolev space embedding",
     "reason": "Mathlib.Analysis.FunctionalSpaces.SobolevInequality exists in source but is not built locally; "
               "no elliptic regularity in Mathlib"},
    {"source": "regen#16", "title": "Kähler-Einstein metrics & Fano surfaces",
     "reason": "no Kähler manifolds in Mathlib (RingTheory.Kaehler is Kähler differentials); "
               "Geometry.Manifold not built"},
    {"source": "regen#17", "title": "Intersection theory: Bézout's theorem",
     "reason": "no intersection multiplicity for plane curves in Mathlib"},
    {"source": "regen#18", "title": "Morse theory: critical points & homology",
     "reason": "no Morse theory in Mathlib"},
    {"source": "regen#19", "title": "Stable homotopy & cohomology operations",
     "reason": "no stable homotopy category or Steenrod operations in Mathlib"},
    {"source": "regen#20", "title": "Derived categories & homological algebra",
     "reason": "Mathlib.Algebra.Homology.DerivedCategory exists in source but is not built locally"},
]


def item_ids() -> list[str]:
    """All problem ids, in order."""
    return [p["id"] for p in PROBLEMS]
