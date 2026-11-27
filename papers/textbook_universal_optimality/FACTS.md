# FACTS — the only admissible source of numbers, names and references for the textbook

Every chapter writer must take numbers, Lean names, file paths and citations from this file, or from a command they
ran themselves (and then show the command and its output in the text or a footnote). Never invent a number, a DOI,
a page, a theorem name or a quote. If something is not here and you cannot compute it, say so in the text.

## 0. Ground rules (binding)
- Elenchus tiers (SocrateAI-Scientific-Elenchus): **A** kernel-checked Lean, **B** exact-rational harness, **L** cited
  literature, **C** argument/conjecture/proposal, **X** floating point / sampling (may steer, never supports a claim).
  Label every claim's tier in the text (use the `\tierA{}`, `\tierL{}`, `\tierC{}`, `\tierX{}` macros).
- Tier A attaches to the formal statement, never to its gloss. No human has audited statement adequacy (6 ledger
  flags). Say "kernel-checked, conditional on the fidelity of the definitions", never "proved true", "certified
  physics" or "100% verified".
- The STRONG (per-potential) Cohn–Kumar conjecture is OPEN. Do not claim it is solved. The s = 2 endpoint is OPEN.
  Renormalized energies are proved only in upstream's manuscript (Section 8), NOT in Lean anywhere.
- Upstream's main theorem is AI-generated (OpenAI release), kernel-checked and Comparator-accepted by us, not peer
  reviewed.
- CPU: use at most 2 cores for anything you run (`taskset -c 2,3 ...`). Python: `/home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I`.

## 1. Definitions as in upstream Lean (file `lean/ComparatorChallenges/TriangularEnergy.lean`, openai/math adc7f124, sha256 af51979c…0616; unchanged at fd4aeeb2)
- `LocallyFinite C := ∀ R, (C ∩ closedBall 0 R).Finite`
- `diskPoints C R` = finset of `C ∩ closedBall 0 R` (∅ if infinite); `diskCount` its card.
- `DensityOne C := Tendsto (fun R => diskCount C R / (π R²)) atTop (𝓝 1)`
- `AdmissiblePotential g := ContDiffOn ℝ ⊤ g (Ioi 0) ∧ (∀ t > 0, 0 ≤ g t) ∧ ∀ r t, 0 < t → 0 ≤ (-1)^r * iteratedDeriv r g t`  (weak inequalities; C^∞ not analytic)
- `diskEnergy g C R := (diskCount C R)⁻¹ * Σ_{x ∈ diskPoints} Σ_{y ∈ diskPoints, y ≠ x} ofReal (g ‖x−y‖²)` in ℝ≥0∞
- `energy g C := liminf (diskEnergy g C) atTop`  (lower energy, closed disks)
- `b = √3/2`, `triangularPoint (j,k) = (√b)⁻¹ • (j + k/2, k b)`, `A = range triangularPoint` (covolume 1)
- `latticeEnergy g := Σ' a ∈ A∖0, ofReal (g ‖a‖²)` (may be ⊤)
- **Upstream theorem** `OAI.AtomicTriangular.universal_energy_minimum g C (hg : AdmissiblePotential g) (hC : LocallyFinite C) (hd : DensityOne C) : latticeEnergy g ≤ energy g C ∧ latticeEnergy g = energy g A`.
  The proved version is `OAI/Analysis/Triangular/Energy/Universal.lean` (the challenge file has `sorry` by design; Comparator certifies the two statements agree).

## 2. Upstream proof architecture (from the upstream manuscript, Section 1; OpenAI, "Universal optimality of the triangular lattice", 2026-09-23)
- Normalisation `f̂(ξ) = ∫ f(x) e^{-2πi x·ξ} dx`; Gaussian `G_α(x) = e^{-π α |x|²}`; dual lattice `A*`.
- Seek radial Schwartz `f_α` with `f_α ≤ G_α`, `f̂_α ≥ 0`, `f_α(a) = G_α(a)` on `A∖0`, `f̂_α(w) = 0` on `A*∖0`.
  Then for every competitor C of centred density one: `E_{e^{-παt}}(C) ≥ f̂_α(0) − f_α(0) = Σ_{a∈A∖0} e^{-πα|a|²}`
  (equality by Poisson summation on A; competitor need not be periodic; disk-vs-area comparison with uniform error).
- Construction (upstream §1–§4): a sine product with double zeros encodes the periodic contact set; multiplied by
  double-pole/simple-pole terms gives entire functions with prescribed values and slopes; compactly supported
  spectral measures; Gaussian damping; finite reference lists by positive quadrature with certified matrix and
  polynomial inequalities (verification scripts use python-flint ball arithmetic). **Not** modular forms (that is the
  CKMRV dimension 8/24 method).
- General g: positive mixtures of Gaussians (Bernstein–Hausdorff–Widder; upstream's own finite-difference proof);
  lower-limit/endpoint/infinite-energy arguments in upstream §5. Upstream: "It identifies the minimum value, not all
  minimizers." and does NOT claim the per-potential (sharp auxiliary function for each mixed potential) form.

## 3. Our Lean results (AutoevolveAI `formal_cert/Triangular/`, toolchain Lean 4.34.1 + Mathlib d13f23b7 + openai/math adc7f124; all footprints ⊆ {propext, Classical.choice, Quot.sound}; 22 audited declarations + 2 planted controls flagged)
- `Riesz.lean`: `TriangularRiesz.riesz s := fun t => t^(-(s/2))`; `riesz_admissible (hs : 0 < s)`; `triangular_riesz_optimal` (D1). Proof idea: `Real.iter_deriv_rpow_const`, `ascPochhammer_eval_neg_eq_descPochhammer`, `ascPochhammer_pos`.
- `RieszFinite.lean`: `norm_sq_triangularPoint : ‖p(j,k)‖² = (1/b)(j²+jk+k²)`; `latticeEnergy_riesz_lt_top (hs : 2 < s)` (D1b), via openai/math `LatticeSummability.summable_normForm_neg_rpow`.
- `AnyDensity.lean`: `DensityRho ρ`; `admissible_comp_mul`; `universal_any_density`; `scaled_density`; `attained`; `triangular_optimal_any_density` (D2); negative control `unscaled_false` (ρ = 1/4, s = 4).
- `Controls.lean`: `riesz_sq` (riesz s (r²) = r^(-s)); `riesz_neg_two_not_admissible`; `rho_one`; `riesz_lattice_homogeneous`; `riesz_any_density_homogeneous`.
- `UniversalOptimality.lean` (D3): `UniversallyOptimal ρ C` (CKMRV Def 1.3 with lower energy — weaker than CKMRV, which also requires the energy limit to exist); `triangular_universally_optimal`; `vacancy := A \ {0}`; `vacancy_energy`; `vacancy_not_isometric_image` (isometries are affine: `Isometry.affineIsometryOfStrictConvexSpace`); `vacancy_universally_optimal`; `universal_optimum_not_unique`.
- **D4 (in progress, this session)**: `OpenDisk.lean` — open-disk density and lower energy coincide with closed-disk ones for locally finite C. Human proof: Section D4 of the preregistration `results/discovery/D4/preregistration.json`. Its Lean status is filled by the editor through the macro `\DFourStatus`.
- Compile: `python3 scripts/certified_numerics/lean_pinned.py compile <file> [--olean Module]`; clean sequential rebuild exits 0; UniversalOptimality ~14 s when cached (310 s cold, 49 min under heavy load).

## 4. Numerical study (rusty-SUNDIALS crate `qf-yukawa-crystal`, PR #72; preregistration 636c514 before code 968b0f2; results 1f46e70) — Tier X
- Yukawa V(r) = e^{-κr}/r, shifted-force cutoff r_c = 8; N = 288, periodic box 16a × 9√3 a, a = √(2/√3), density 1.
- CVODE (BDF, analytic Jacobian = −Hessian) gradient flow to max|F| < 1e-9; Hessian spectrum by cyclic Jacobi; Euler–Maruyama annealing (T 0.05 → 1e-5, 300 000 steps, dt 0.01) outside SUNDIALS then CVODE quench. KINSOL absent; `crates/ida` is a documented fixed-step prototype (not used).
- References: κ=2: e_tri = 0.3935333668, e_sq = 0.4009647699 (Δ = 7.43e-3); κ=1: e_tri = 1.6076092172, e_sq = 1.6171455730 (Δ = 9.54e-3). Box vs direct sum agree to ~1e-14.
- Controls: perfect lattice gap 5.2e-14; noisy (0.1a) gap 2.5e-14; Hessian 2 zero modes then 0.0236; square lattice saddle (72 negative eigenvalues κ=2, 64 κ=1); incommensurate box: all defected, min gap 9.6e-4 (κ=2).
- P1 (no relaxed configuration below e_tri): PASS — 0 undercuts in 100 relaxations at κ=2 (20 of them incommensurate controls), 0 in 50 at κ=1.
- P2 (annealing reaches perfect lattice ≥1 per family): κ=2 PASS narrowly (OC20-derived 1/20, uniform 1/20); κ=1 FAIL (0/10, 2/10).
- P3: T=0 quenches defected 15/20 (OC20), 14/20 (uniform) at κ=2.
- Hessian checked for the 80 (κ=2) and 40 (κ=1) non-control runs: 0 negative; translation modes |λ| ≤ 1.5e-15 / 1.8e-15; other eigenvalues ≥ 5.4e-5 / 5.0e-5.
- Disk (N=300, κ=2; open = harmonic bowl k = 0.02, closed = soft wall ε(r−R)^4, ε=100): interior defect fraction 0.086 (open) vs 0.033 (closed); edge 0.965 vs 0.602; interior |ψ6| 0.913 vs 0.931. Confounded (non-uniform density, different edge-layer sizes).
- Initial conditions: Hugging Face `colabfit/OC20_IS2RES_val_id` (CC-BY-4.0, doi:10.60732/b4005525), shard co/co_10.parquet, random 3D rotation + projection, min separation 0.5a.
- Jellium extension (s = 1, 2D Wigner crystal), branch `physics/jellium-wigner-2026-10-11` (prereg e706f85, code 3bc55fa, Alves credit b7e4380): Ewald energy per particle e_tri = −1.960515789320 vs literature −1.960515789825 (rel 2.6e-10); e_sq = −1.950132460 vs lit (rel 4.3e-10); 64 unstable square modes; α-invariance < 1e-10 over a 4× range. Main relaxation study: result filled by the editor via `\JelliumMainStatus`.
- Figures (PDF) available to include: `../universal_optimality_tiered/figures/{cover,vacancy,gaps,lattices,disks}.pdf`.

## 5. Publications / repositories
- D1–D2 paper doi:10.5281/zenodo.23285631; tiered paper v1 doi:10.5281/zenodo.23293112, v2 doi:10.5281/zenodo.23293429 (concept 10.5281/zenodo.23293111).
- LeanMaster release v3.48.1 (contrib/openai_math_corollaries); rusty-SUNDIALS PR #72; MechanicaFluidorum PR #1 (docs/proposals).
- Code to quote VERBATIM (read the file; never paraphrase code as if it were the file):
  - Lean: `/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/formal_cert/Triangular/*.lean`
  - Rust: `/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-yukawa/crates/qf-yukawa-crystal/src/{lib.rs,jellium.rs,main.rs}`
  - Python: `.../papers/universal_optimality_tiered/{make_figures.py,lab/lab_analysis.py}`, `.../crates/qf-yukawa-crystal/scripts/{hf_initial_conditions.py,summarize.py}`

## 6. References (DOI-verified; use these \cite keys only)
ckmrv (Cohn, Kumar, Miller, Radchenko, Viazovska, Ann. Math. 196 (2022) 983–1082, doi:10.4007/annals.2022.196.3.3);
ck (Cohn, Kumar, JAMS 20 (2007) 99–148, doi:10.1090/S0894-0347-06-00546-7);
oai (OpenAI, Universal optimality of the triangular lattice, OpenAI Math Release preprint, 2026-09-23, github.com/openai/math);
ps (Petrache, Serfaty, Proc. AMS 148 (2020) 3047–3057, doi:10.1090/proc/15003);
bm (Bonsall, Maradudin, PRB 15 (1977) 1959, doi:10.1103/PhysRevB.15.1959);
alves (Alves, Bendazzoli, Evangelisti, Berger, PRB 103 (2021) 245125, doi:10.1103/PhysRevB.103.245125);
zahn (Zahn, Wille, Maret, Sengupta, Nielaba, PRL 90 (2003) 155506, doi:10.1103/PhysRevLett.90.155506);
thomas (Thomas, Morfill, Demmel, Goree, Feuerbacher, Möhlmann, PRL 73 (1994) 652, doi:10.1103/PhysRevLett.73.652);
bubeck (Bubeck, Neser, Bechinger, Leiderer, Prog. Colloid Polym. Sci. (1998) 41–45, doi:10.1007/BFb0118046);
grimes (Grimes, Adams, PRL 42 (1979) 795, doi:10.1103/PhysRevLett.42.795);
fine (Fine, Cass, Flynn, Driscoll, "Relaxation of 2D turbulence to vortex crystals", PRL 75 (1995) 3277, doi:10.1103/PhysRevLett.75.3277);
aboshaeer (Abo-Shaeer, Raman, Vogels, Ketterle, "Observation of vortex lattices in Bose–Einstein condensates", Science 292 (2001) 476, doi:10.1126/science.1060182);
rankin (Rankin, Proc. Glasgow Math. Assoc. 1 (1953) 149, doi:10.1017/S2040618500035668);
cassels (Cassels, Proc. Glasgow Math. Assoc. 4 (1959) 73, doi:10.1017/S2040618500033906);
montgomery (Montgomery, Glasgow Math. J. 30 (1988) 75, doi:10.1017/S0017089500007047);
oc20 (Chanussot et al., OC20 IS2RES val id, ColabFit 2024, doi:10.60732/b4005525);
elenchus (Callens, SocrateAI-Scientific-Elenchus, github.com/xaviercallens/SocrateAI-Scientific-Elenchus);
rusty (Callens, rusty-SUNDIALS, github.com/xaviercallens/rusty-SUNDIALS);
d12 (Callens, doi:10.5281/zenodo.23285631); tiered (Callens, doi:10.5281/zenodo.23293429).
History per CKMRV: Ventevogel–Nijboer proved universal optimality of Z in dimension 1; Cohn–Kumar gave another proof;
before CKMRV no universal optimum in dimension > 1; A2 "in full generality is an important open problem" (CKMRV §1.2).

## 7. The student draft under review ("Universal Optimality of the Planar Triangular Lattice: A Formal Proof Architecture") — errors to correct (Chapter 1 does the review)
1. "derivatives strictly alternate in sign" — the definition is the WEAK inequality (−1)^r g^(r) ≥ 0.
2. Bernstein: g(t) = ∫_{[0,∞)} e^{-αt} dμ(α) for completely monotone g of t = r²; the measure may charge α = 0 (constants), whose energy is infinite at density 1 (upstream lemma `energy_one`). "Strictly sufficient" → "sufficient", and the passage from Gaussians to mixtures needs monotone convergence / Tonelli plus the lower-limit argument (liminf is not linear).
3. Cohn–Elkies-type lemma: f ≤ V is a MINORANT (not "majorization"); the lemma must state the bound E(C) ≥ f̂(0) − f(0) at density 1 and that Poisson summation gives equality on the lattice when the root conditions hold. Normalisation G_α = e^{-π α |x|²}.
4. "integral transforms of weakly holomorphic modular forms adapted to hexagonal symmetry" — WRONG for this proof: upstream uses sine-product cardinal interpolation, Gaussian damping and certified finite quadrature (Section 2 above). Modular forms are the CKMRV method in dimensions 8 and 24, and no modular-form construction is known in dimension 2.
5. "We demonstrate" / author "Statement-Adequacy Review Draft": the theorem is upstream's (AI-generated, not peer reviewed); our contribution is corollaries + audit.
6. Theorem 2 (arbitrary densities) needs local finiteness of C and DensityRho as hypotheses; it holds with the lower energy.
7. Theorem 3 (non-uniqueness): true among ALL locally finite configurations (A∖0 is not periodic); uniqueness among PERIODIC configurations is open in 2D and not claimed.
8. Missing: E_g is the LOWER energy (liminf, CKMRV's Def 1.3 also asks the limit to exist); closed vs open disks (now D4).
