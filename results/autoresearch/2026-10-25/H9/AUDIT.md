# H9: does the Lean statement match the Clay problem? Fefferman (C)/(D) vs `navier_stokes_breakdown_R3` / `_periodic`

Date: 2026-10-25. This audit only reads texts. I built nothing, compiled nothing and proved nothing. It compares two **statements**. It does not check any proof, and it does not claim that the Clay problem is solved.

## Sources

* **[F]** C. L. Fefferman, *Existence and smoothness of the Navier–Stokes equation*, the official Clay problem description, with the errata appended.
  * URL: https://www.claymath.org/wp-content/uploads/2022/06/navierstokes.pdf (fetched 2026-10-25, HTTP 200).
  * Text extracted locally with `pdftotext -layout` from the bytes WebFetch saved.
* **[L]** `ComparatorChallenges/NavierStokes.lean`, 286 lines, in `/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/SocrateAI-Scientific-Agora-LeanMaster/lean4basesource/openai-navierstokes/`.
  * Also read: `ComparatorChallenges/NavierStokes.json`, `ComparatorChallenges/README.md`, `README.md`, `formalization.yaml`, and `NavierStokes/ComparatorSolution.lean`, which restates the same two theorems verbatim at lines 16–27.
  * Toolchain: `leanprover/lean4:v4.34.0-rc2`, Mathlib `v4.34.0-rc2`.
* **[M]** Mathlib definitions, checked in the copy on disk at `/mnt/disks/disk-socrateai-local-1/mensura-lean-baseline-v4322-r2/.lake/packages/mathlib`.
  * That copy is v4.32.2, **not** the pinned v4.34.0-rc2.
  * Files read: `ContDiff/FTaylorSeries.lean:118-120`, which defines the notation `∞ = ((⊤:ℕ∞):WithTop ℕ∞)` (C^∞, not analytic `ω`), and `InnerProductSpace/Laplacian.lean:132-142`, where `Δ` is the trace of the second derivative against the canonical covariant tensor.
* **Provenance.** The header of [L] (lines 25–32) says the file is "Standalone comparator copied from" google-deepmind/formal-conjectures at commit `8bf45ed70d48b2b2a501de9c00b26bfa38c573ee`, `FormalConjectures/Millenium/NavierStokes.lean`. The definitions and (C)/(D) are kept; imports, attributes, namespace and notation are adapted.
  * Upstream has since moved to `.../Millennium/NavierStokes.lean`. Per the web-fetch agent's summary, the upstream (C)/(D) statements have the same shape and are tagged "research solved", with a link to openai/NavierStokesAndEuler@8937a8f.
  * I did **not** diff [L] against upstream byte by byte.

## Fefferman, verbatim (the relevant parts, from the pdftotext output)

* (1) ∂u_i/∂t + Σ_j u_j ∂u_i/∂x_j = νΔu_i − ∂p/∂x_i + f_i(x,t)   (x ∈ R^n, t ≥ 0)
* (2) div u = Σ_i ∂u_i/∂x_i = 0   (x ∈ R^n, t ≥ 0)
* (3) u(x,0) = u°(x)   (x ∈ R^n)
* "Here, u°(x) is a given, C^∞ divergence-free vector field on R^n, … ν is a positive coefficient (the viscosity)"
* (4) |∂_x^α u°(x)| ≤ C_{αK}(1+|x|)^{−K} on R^n, for any α and K
* (5) |∂_x^α ∂_t^m f(x,t)| ≤ C_{αmK}(1+|x|+t)^{−K} on R^n × [0,∞), for any α, m, K
* (6) p, u ∈ C^∞(R^n × [0,∞))
* (7) ∫_{R^n} |u(x,t)|² dx < C for all t ≥ 0 (bounded energy)
* (8) u°(x+e_j) = u°(x), f(x+e_j,t) = f(x,t) for 1 ≤ j ≤ n
* (9) |∂_x^α ∂_t^m f(x,t)| ≤ C_{αmK}(1+|t|)^{−K} on R³ × [0,∞), for any α, m, K ("In place of (4) and (5), we assume that u° is smooth and that")
* (10) u(x,t) = u(x+e_j,t) on R³ × [0,∞) for 1 ≤ j ≤ n
* (11) p, u ∈ C^∞(R^n × [0,∞))
* **(A)** "Take ν > 0 and n = 3. Let u°(x) be any smooth, divergence-free vector field satisfying (4). Take f(x,t) to be identically zero. Then there exist smooth functions p(x,t), u_i(x,t) on R³ × [0,∞) that satisfy (1), (2), (3), (6), (7)."
* **(B)** "Take ν > 0 and n = 3. Let u°(x) be any smooth, divergence-free vector field satisfying (8); we take f(x,t) to be identically zero. Then there exist smooth functions p(x,t), u_i(x,t) on R³ × [0,∞) that satisfy (1), (2), (3), (10), (11)."
* **(C)** "Breakdown of Navier–Stokes solutions on R³. Take ν > 0 and n = 3. Then there exist a smooth, divergence-free vector field u°(x) on R³ and a smooth f(x,t) on R³ × [0,∞), satisfying (4), (5), for which there exist no solutions (p,u) of (1), (2), (3), (6), (7) on R³ × [0,∞)."
* **(D)** "Breakdown of Navier–Stokes Solutions on R³/Z³. Take ν > 0 and n = 3. Then there exist a smooth, divergence-free vector field u°(x) on R³ and a smooth f(x,t) on R³ × [0,∞), satisfying (8), (9), for which there exist no solutions (p,u) of (1), (2), (3), (10), (11) on R³ × [0,∞)."
* **Errata:** "The further condition p(x + e_j, t) = p(x, t) should be made explicit in Eqn (8)." The second erratum, headed "Eqn (10) should read", is a sign fix to the weak formulation (12). It does not affect (A)–(D).

## Lean statements ([L] lines 272–284)

```lean
theorem navier_stokes_breakdown_R3 (nu : ℝ) (hnu : nu > 0) :
    ∃ (u₀ : ℝ³ → ℝ³) (f : ℝ³ → ℝ → ℝ³),
    InitialVelocityConditionDecay u₀ ∧ ForceConditionDecay f ∧
    ¬ (∃ v p, NavierStokesExistenceAndSmoothnessRn nu u₀ f v p)
theorem navier_stokes_breakdown_periodic (nu : ℝ) (hnu : nu > 0) :
    ∃ (u₀ : ℝ³ → ℝ³) (f : ℝ³ → ℝ → ℝ³),
    InitialVelocityConditionPeriodic u₀ ∧ ForceConditionPeriodic f ∧
    ¬ (∃ v p, NavierStokesExistenceAndSmoothnessPeriodic nu u₀ f v p)
```

`ℝ³` is `EuclideanSpace ℝ (Fin 3)` (line 67), so `‖x‖` is the Euclidean |x|. The `divergence` in line 81 is `(fderiv ℝ v x).trace`, which equals Σ ∂v_i/∂x_i.

## Match table for (C) and `navier_stokes_breakdown_R3`

| # | Element in Fefferman (C) | Lean text (file:line) | Mark | Note |
|---|---|---|---|---|
| 1 | n = 3, domain R³ | `ℝ³ := EuclideanSpace ℝ (Fin 3)` L:67; theorem L:273-274 | MATCH | Euclidean norm. |
| 2 | "Take ν > 0 … Then there exist u°, f": viscosity quantifier | `(nu : ℝ) (hnu : nu > 0) : ∃ u₀ f, …` L:273-274 | MATCH | The order is ∀ν>0 ∃u₀ f, the strong reading of "Take ν > 0", not ∃ν. NS scaling (u→νu(x,νt), p→ν²p(x,νt), f→ν²f(x,νt)) maps the classes for different ν onto each other, so the ∀ and ∃ readings are mathematically equivalent anyway. That equivalence is informal and not mechanized. |
| 3 | u° smooth (C^∞) | `smooth : ContDiff ℝ ∞ u₀` L:139 | MATCH | `∞` is C^∞ (`ω` would be analytic) [M]. |
| 4 | u° divergence-free | `div_free : ∀ x, ∇⬝ u₀ x = 0` L:137 | MATCH | u₀ is smooth, so the divergence's junk value never fires. |
| 5 | (4): \|∂^α u°(x)\| ≤ C_{αK}(1+\|x\|)^{−K}, ∀α, K | `decay : ∀ m : ℕ, ∀ K : ℝ, ∃ C : ℝ, ∀ x, ‖iteratedFDeriv ℝ m u₀ x‖ ≤ C / (1 + ‖x‖) ^ K` L:155 | MATCH | Order-m derivative norm vs multi-index α with \|α\| = m: they agree up to constants that depend on m, so the two classes are the same. K ranges over ℝ rather than ℕ: K ≥ 0 is the substantive part, and negative K follows from K = 0. The base is ≥ 1, so rpow has no junk. The class is not vacuous: curl of a vector Gaussian is smooth, divergence-free and Schwartz (informal, not mechanized). |
| 6 | f smooth on R³ × [0,∞) | `smooth : ContDiffOn ℝ ∞ (↿f) (Set.univ ×ˢ Set.Ici 0)` L:177 | MATCH | Smoothness is taken in the closed half-space sense (one-sided at t = 0). Fefferman does not define "smooth on R³ × [0,∞)" further. |
| 7 | (5): \|∂_x^α ∂_t^m f\| ≤ C(1+\|x\|+t)^{−K} on R³×[0,∞), ∀α, m, K | `decay : ∀ m K, ∃ C, ∀ x, ∀ t ≥ 0, ‖iteratedFDerivWithin ℝ m (↿f) (univ ×ˢ Ici 0) (x,t)‖ ≤ C / (1 + ‖x‖ + t) ^ K` L:190-191 | MATCH | The full (x,t) derivative of order m bounds all mixed ∂_x^α∂_t^j with \|α\|+j = m, and vice versa, up to constants. The norm on ℝ³×ℝ is Mathlib's sup norm, which is equivalent. Neither weaker nor stronger than (5). |
| 8 | "no solutions (p,u)": the pressure is a free unknown | `¬ (∃ v p, …)` L:276; `p : ℝ^n → ℝ → ℝ` L:219 | MATCH | Pressure is present and existentially quantified, with no normalization or decay condition at infinity. Fefferman imposes none either. |
| 9 | (1) momentum equation, x ∈ R³, t ≥ 0 | `navier_stokes : ∀ x, ∀ t ≥ 0, derivWithin (v x ·) (Set.Ici 0) t + fderiv ℝ (v · t) x (v x t) = nu • Δ (v · t) x - gradient (p · t) x + f x t` L:222-224 | MATCH | Dv(x)[v] = (v·∇)v. Δ is the componentwise Laplacian [M]. The time derivative is one-sided at t = 0 and the ordinary derivative for t > 0. Rows 12–13 make v and p smooth, so none of the derivative junk values can fire. |
| 10 | (2) div u = 0, t ≥ 0 | `div_free : ∀ x, ∀ t ≥ 0, ∇⬝ (v · t) x = 0` L:227 | MATCH | |
| 11 | (3) u(x,0) = u°(x) | `initial_condition : ∀ x, v x 0 = u₀ x` L:229 | MATCH | |
| 12 | (6) u ∈ C^∞(R³ × [0,∞)) | `velocity_smooth : ContDiffOn ℝ ∞ (↿v) (Set.univ ×ˢ Set.Ici 0)` L:232 | MATCH | Closed interval [0,∞), not (0,∞). Same caveat about the meaning of smoothness as row 6. |
| 13 | (6) p ∈ C^∞(R³ × [0,∞)) | `pressure_smooth : ContDiffOn ℝ ∞ (↿p) (Set.univ ×ˢ Set.Ici 0)` L:235 | MATCH | |
| 14 | (7) ∫\|u(x,t)\|² dx < C for all t ≥ 0 | `integrable : ∀ t ≥ 0, MemLp (‖v · t‖) 2` L:250 and `globally_bounded_energy : ∃ E, ∀ t ≥ 0, (∫ x, ‖v x t‖ ^ 2) < E` L:253 | MATCH | The pair is equivalent to (7). The `MemLp` conjunct is what blocks the Bochner-integral trap, where a non-integrable function integrates to 0 and would make infinite-energy fields count as "bounded energy". (7), read as a Lebesgue integral, already implies L² at each t, so the conjunct adds no restriction. E is uniform in t, as is C in (7). |
| 15 | Time interval [0,∞) throughout | `Set.Ici 0`, `∀ t ≥ 0` in every clause | MATCH | |
| 16 | "there exist no solutions": quantifies over all solutions in the class (1),(2),(3),(6),(7) | `¬ ∃ v p, NavierStokesExistenceAndSmoothnessRn …` with exactly the fields of rows 9–14 | MATCH | The class has no extra restriction, so the negation covers every smooth bounded-energy solution. The class is non-empty for some data: v = p = 0 solves it when u₀ = f = 0. That means "no solution" is not trivially true for all data. Small-data global smooth solutions also belong to it (informal). |

Mismatches for (C): **none found**.

## Match table for (D) and `navier_stokes_breakdown_periodic`

| # | Fefferman (D) | Lean (file:line) | Mark | Note |
|---|---|---|---|---|
| D1 | ν > 0, ∃ u° f | L:280-281 | MATCH | Same as row 2. |
| D2 | u° smooth and divergence-free, periodic as in (8) | `InitialVelocityConditionPeriodic` L:164-167 (`div_free`, `smooth`, `isOnePeriodic`); `IsOnePeriodic` L:121-122 means ∀ x i, f (x + e_i) = f x | MATCH | |
| D3 | f smooth on R³×[0,∞), periodic in x (8), decay (9) C(1+\|t\|)^{−K} | `ForceConditionPeriodic` L:200-205: `smooth` L:177; `isOnePeriodic : ∀ t ≥ 0, IsOnePeriodic (f · t)`; `decay … ≤ C / (1 + t) ^ K` | MATCH | Periodicity is required only for t ≥ 0. f is used only for t ≥ 0. |
| D4 | (1),(2),(3),(11) | the same `NavierStokesExistenceAndSmoothness` fields L:217-235 | MATCH | |
| D5 | (10) u periodic | `isOnePeriodic_velocity` L:267 | MATCH | |
| D6 | Pressure periodicity: absent from the 2000 main text, added by the Clay **errata** ("p(x+e_j,t) = p(x,t) should be made explicit in Eqn (8)") | `isOnePeriodic_pressure : ∀ t ≥ 0, IsOnePeriodic (p · t)` L:269, with docstring L:259-260 "following the errata" | **DIFFERENT from the main text, MATCH with the errata** | Requiring periodic p shrinks the solution class. So "no solution" in Lean is **weaker** than "no solution" read from the main text alone, where p may carry a term a(t)·x. It agrees with the errata-corrected official statement. The erratum places the condition in (8), the data hypotheses, although it constrains the unknown p. Lean puts it in the solution class, the only place it can mean anything. |
| D7 | No energy condition in (D) | none in `…Periodic` | MATCH | |

## Questions the task asked about

* **Quantifier order:** ∀ν>0 ∃u₀ f. This is the strong reading of the Clay text (row 2).
* **f's hypotheses:** exactly (5), neither weaker nor stronger (row 7). In (D), exactly (8)+(9).
* **Scope of "no solution":** it covers all smooth solutions with bounded energy, through `¬ ∃ v p`, with no restriction to a subclass (row 16).
* **Pressure:** present and existential (row 8).
* **Initial condition and divergence-free:** both imposed on the data and on the solution (rows 4, 10, 11).
* **Time interval:** [0,∞) closed (row 15).
* **Vacuity:** I found none. The decay classes contain nonzero Schwartz fields. The solution class is not empty by construction. Junk values (divergence/fderiv of non-differentiable maps, Bochner integral of non-integrable maps, rpow) are each neutralised by `smooth`/`ContDiffOn`/`MemLp` or by a positive base. These are informal arguments, not Lean lemmas.

## Fidelity "in spirit"

If the Lean statement of (C) is faithful, a proof of it is a proof of Fefferman's alternative (C) on R³. Fefferman's text asks "for a proof of one of the following four statements", so that would address the Clay problem in its negative R³ form.

* This audit says nothing about whether any proof is correct.
* It says nothing about the Clay Institute's separate award rules (publication, a waiting period, community acceptance).

Press criticism that the OpenAI result is "forced, not unforced" is **not** a fidelity defect against (C). Fefferman's (C) explicitly allows a smooth f satisfying (5). f ≡ 0 appears only in (A) and (B).

## Caveats (these are not mismatches)

1. **Interpretation of smoothness.** "Smooth on R³ × [0,∞)" is encoded as Mathlib `ContDiffOn ℝ ∞ … (univ ×ˢ Ici 0)`, with one-sided derivatives at t = 0. This is the standard reading, but Fefferman does not define it.
2. **(D) pressure periodicity.** Lean follows the errata. Against the main text alone, Lean's (D) is weaker (row D6).
3. **Equivalences argued, not mechanized.** Norm equivalences (multi-index vs `iteratedFDeriv` operator norm; sup norm vs Euclidean norm on ℝ³×ℝ), the ν-scaling equivalence and the non-vacuity examples are argued by hand. None is a Lean lemma.
4. **Mathlib version.** Definitions (`∞`, `Δ`, `gradient`) were checked against Mathlib v4.32.2 on disk, not the pinned v4.34.0-rc2. Nothing was compiled.
5. **Upstream provenance.** I did not diff [L] against formal-conjectures@8bf45ed. The upstream directory has been renamed `Millenium` → `Millennium`.
6. **Statement only.** This audit covers the challenge statement. Whether `NavierStokes/ComparatorSolution.lean` (via `ComparatorBridge`/`ComparatorDefinitions`) proves *this exact* statement is Comparator's job. I did not run Comparator.

## Existing public discussion (brief search)

* **Bastounis, Circelli, Hansen**, "Navier–Stokes lost in translation", alphaXiv/arXiv 2610.08144, 6 Oct 2026.
  * Per the alphaXiv report: intermediate Lean lemmas in the OpenAI development do not match the natural-language paper. One inverse estimate needs m+5 derivatives in Lean against m+4 in the paper. A pressure-flux bound has different hypotheses and proof route.
  * The paper is about the correspondence between the natural-language proof and the Lean proof. It does not claim that the top-level (C)/(D) statement misstates the Clay problem, and it does not claim that the natural-language proof is wrong.
  * I checked this against the alphaXiv full text, not only its summary. Grepping the full text for "Fefferman", "Clay", "breakdown_R3", "errata", "Millennium", "formal-conjectures" and "ComparatorChallenge" finds only the historical mention in §3 ("designated a Clay Millennium Prize Problem in 2000 [23]") and the reference list. §3.1, §3.2 and Remark 3.4 deal only with intermediate lemmas (paper Lemma 8.6 / eq. (8.19); the pressure-flux bound in the proof of Lemma 10.5).
* **The corpus itself.** I grepped `NavierStokes/` and `Euler/` for `Fefferman|errata|fidelity|faithful|claymath`. The only hits are docstrings in `NavierStokes/ComparatorDefinitions.lean` (lines 119, 136, 157, 172, 233, 242) that tag each definition with its Fefferman condition number and cite the errata for pressure periodicity, plus one unrelated use of "faithful" in `Euler/TerminalTimePrimitive.lean:356`. The corpus contains no fidelity discussion. `formalization.yaml` records `review: status: "self-assessed"`.
* **News coverage** (aiweekly.co, thenextweb, lilting.ch) raises "forced vs unforced". As explained above, that applies to (A)/(B), not to (C).
* I found no GitHub issue in formal-conjectures that disputes the fidelity of its (C)/(D) statement. The search was brief, and the issue tracker was not browsed.

## Verdict

**FAITHFUL_WITH_CAVEATS.**

* For (C), every element matches Fefferman's text. I found no weaker, stronger or vacuous clause.
* For (D), the statement matches the errata-corrected Clay text. Against the main text alone it is weaker on one point: the pressure must be periodic.
* The caveats come from interpretation (closed-half-space smoothness) and from checks done by hand rather than mechanized (norm equivalences, non-vacuity, Mathlib version).
