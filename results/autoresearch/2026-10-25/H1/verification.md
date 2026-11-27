# H1 / H1b independent verification (producer ≠ verifier), 2026-10-25

**VERDICT: ACCEPT_WITH_CORRECTIONS.** The kernel results hold and the statements say what they claim. The corrections
below only affect wording and metadata. Optimality stays conditional on upstream `universal_energy_minimum`
(openai/math, AI-generated, not peer reviewed). The 2D Cohn–Kumar conjecture is open in the human literature:
1908.09714 p.1 says so, and so does 2511.03353 §1.3 (Nov 2025).

## 1. Recompile and axioms
- Scratch file: verbatim bodies of `Triangular/Riesz.lean`, `RieszFinite.lean`, `AnyDensity.lean` and
  `Autoresearch/DipolarExciton.lean`, concatenated by script. It imports only upstream (`OAI.Analysis.Triangular.Energy.Universal`,
  `OAI.NumberTheory.DirichletL.LatticeSummability`), so none of the producer's oleans were used.
  Compiled with `lean_pinned.py` (Lean 4.34.1, cores 6,7): rc 0, 42.7 s. The only warnings are deprecations.
- `#print axioms` gives `[propext, Classical.choice, Quot.sound]` for `dipolar_admissible`, `triangular_dipolar_optimal`,
  `h_not_admissible`, `latticeEnergy_dipolar_lt_top`, and for upstream `universal_energy_minimum`.
- Planted control `verifier_sorry_control : 2+2=5 := by sorry`: rc stayed 0 (as expected), and the axiom check flagged
  it as `[sorryAx]`. So the gate is the axiom check, not the exit code, and the gate works.

## 2. Statement adequacy
- **Formula:** kernel-checked (`rfl`) that `g d t = 2*(t^(-1/2) - (t+d^2)^(-1/2))`. I also proved that for r > 0,
  `g d (r^2) = 2*(1/r - 1/√(r^2+d^2))`. Upstream energy evaluates `g (‖x−y‖^2)`, so t = r² is the right variable.
- **Physics:** two rigid vertical dipoles (e above h, layer separation d) at in-plane distance r. The e–e and h–h pairs
  (same layer, distance r) each give +1/r. The two cross pairs (e₁–h₂, h₁–e₂, distance √(r²+d²)) each give −1/√(r²+d²).
  Total: 2/r − 2/√(r²+d²), in units e²/(4πε). Factor and sign are correct; the intra-exciton binding is a constant and is
  dropped. Far field: g ≈ d²/r³ (dipole–dipole), which matches the `g_le` bound d²·t^(-3/2).
- **Pair counting:** upstream `diskEnergy` sums ordered pairs over each point's neighbours, and `latticeEnergy` sums over
  all nonzero lattice points. Both use the same convention (energy per particle ×2), so the comparison is consistent.
  The `ENNReal.ofReal` clamp does nothing because g ≥ 0.
- **`hd : 0 < d` is not used** in `dipolar_admissible` (it is `_hd`). I kernel-checked that `AdmissiblePotential (g 0)`
  holds too (g 0 ≡ 0). The hypothesis is superfluous but harmless.
- **H1b for every d:** this is a correct statement. At d = 0 it is trivial (g ≡ 0). For d > 0 it is the informative case,
  and it is what stops `triangular_dipolar_optimal` from collapsing to `⊤ ≤ ⊤`.
- **Non-vacuity (kernel-checked):** `A` satisfies `LocallyFinite` and `DensityOne`, and `energy (g d) A = latticeEnergy (g d) < ⊤`.
  So the minimum is attained and finite. The upstream theorem, and therefore H1, is a density-one statement.

## 3. Novelty
- arXiv:2110.08728 (Luo–Wei–Zou): two-species lattice-shape minimisation for completely monotone (CM) F, among Bravais
  lattices only. It lists CM-preserving rules (f^(2m), −f^(2m+1), e^f, f(ax^α+b)). It does **not** treat differences
  f(t) − f(t+c), dipolar potentials or bilayer potentials (pp. 1–7).
- arXiv:1908.09714 (Petrache–Serfaty): shows that Cohn–Kumar implies optimality for Riesz/Coulomb/jellium. Bilayer and
  dipolar potentials are not mentioned. It uses the same (1.1) liminf-of-ball-averages energy that upstream formalises.
- arXiv:2005.03541 (Chui–Wang–Wan, full text read): uses the full bilayer Coulomb interaction but simply *assumes* a
  triangular exciton lattice for its phonon/Lindemann calculation. It gives no CM argument and no optimality claim.
- arXiv:2511.03353 (Leblé, full text read): proves local optimality for CM potentials. It says global optimality is a
  "major open problem" (§1.3); the open status is also stated in 1908.09714 p.1. Its examples are Gaussians and Riesz;
  it does not treat differences or dipolar potentials.
- discover_papers, keywords [dipole bilayer, completely monotone, triangular lattice], [dipolar excitons, Wigner crystal,
  bilayer, triangular lattice, classical ground state] and [Cohn-Kumar, dipolar]. Other hits, read as abstracts only:
  2411.17199, 2401.04639, 2512.16509, 2610.17030, 2601.19603. No abstract states the CM fact or the optimality claim.
- **Verdict: not found in the literature, mathematically elementary.** It is folklore-level: if f(t) = ∫e^(−αt)dμ(α),
  then f(t) − f(t+c) = ∫e^(−αt)(1 − e^(−αc))dμ(α) is CM for c ≥ 0. Once universal optimality is granted, every CM
  potential follows at once. What is new is only the explicit, kernel-checked bilayer-exciton corollary, together with
  the finiteness bound. Do not claim it as a new physics result.

## 4. Physics scope
- Classical point particles at zero temperature, with no kinetic or zero-point energy. Experimental dipolar-exciton
  solids are quantum (bosonic) and are often lattice- or moiré-pinned (2401.04639, 2601.19603).
- Rigid, perpendicular, bound e–h pairs with fixed d. Configurations with unpaired electrons and holes, or separate
  electron/hole crystals, are outside the model. The honeycomb result of arXiv:2610.17030 is in such a model and does
  not contradict H1.
- **Every density:** `TriangularDensity.triangular_optimal_any_density` (D2) is generic in the admissible potential. I
  instantiated it for `g d` in the scratch file and it compiled (axioms whitelist only). So the rescaled lattice
  ρ^(−1/2)A is optimal among density-ρ configurations, for every ρ > 0 and d > 0. Equivalently,
  g_d(t/ρ) = √ρ·g_{d√ρ}(t): density ρ at separation d corresponds to density one at separation d√ρ, with energy
  multiplied by √ρ.

## Corrections requested
1. NOTE.md "other densities by scaling d": add the √ρ prefactor, or cite D2 `triangular_optimal_any_density`
   (instantiation verified here).
2. Mention that `hd` is unused in `dipolar_admissible` (the result holds for all real d). Optionally drop the hypothesis.
3. Novelty wording: describe the CM step as elementary (Bernstein) and the corollary as immediate given upstream.
   Keep "kernel-checked corollary" as the only new item.

Verifier scratch (deleted after the run): VerifyH1.lean, out1.json (2 errors in verifier-only checks, fixed),
out2.json (rc 0).
