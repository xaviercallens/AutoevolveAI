# Extension: renormalized and jellium energies (long-range interactions, 0 ≤ s < 2)

Date 2026-10-11. Method: SocrateAI-Scientific-Elenchus (tiers A/L/C/X; every hypothesis has a prior, a kill criterion
and an evidence kind). Follows doi:10.5281/zenodo.23293112.

## 1. The gap

For Riesz exponents 0 < s ≤ 2, and for the logarithm, the raw lattice energy Σ_{a≠0} |a|^{-s} diverges. The
universal-optimality statement is then the empty comparison E(C) = ∞ for every competitor C: D1 in
doi:10.5281/zenodo.23285631 is informative only for s > 2. The physically central cases sit inside this gap:
- s = 1 is the classical 2D electron gas (Wigner crystal);
- s = 0 (the logarithm) is the true 2D Coulomb interaction, i.e. the one-component plasma and vortex lattices.

## 2. What already exists, and where it is not formalized

- **Upstream manuscript, Section 8, Corollary "Planar renormalized and jellium energies"** (2026-09-23). For
  0 ≤ s < 2, the triangular lattice minimizes the renormalized energy W_s among density-one configurations, and the
  jellium minimum is e_Jel = κ_s^{-1} W_s(A).
  - It is proved there via Petrache–Serfaty's field formulation and a "heat comparison across period lattices"
    lemma, which writes V_s(C) − V_s(D) as ∫ (H_C − H_D)(t) t^{-s/2} dt with periodic Gaussian (heat-trace)
    sums H.
  - **It is not in upstream's Lean.** No Lean file in openai/math mentions jellium or renormalized energy; checked
    by grep on the pinned tree.
- **Petrache–Serfaty** (Proc. AMS 148, 2020, Thm 2): universal optimality implies the Coulomb/Riesz crystallization
  results.
- **Physics literature:** the triangular Wigner crystal has the lowest Madelung energy among Bravais lattices
  (Bonsall & Maradudin, PRB 15, 1959 (1977)), and the square lattice is dynamically unstable.

## 3. Hypotheses

| # | Hypothesis | Tier target | Prior | Kill criterion | Status |
|---|---|---|---|---|---|
| E1 | s = 1 jellium, CVODE: no relaxed periodic density-1 configuration below e_tri (Ewald). Madelung controls against Bonsall–Maradudin | X | — | Ewald controls fail | **Running.** Preregistered e706f85; controls pass (Madelung to < 1e-8; square lattice is a saddle with 64 negative modes) |
| E2 | s = 0 (log) one-component plasma, same check | X | — | no stable 2D log Ewald with controls | planned |
| E3 | Lean: for every periodic density-one C and t > 0, H_C(t) ≥ H_A(t) (the heat-trace comparison), derived from upstream's Gaussian universal optimality | A | ~30% | upstream's lower energy of a periodic configuration cannot be identified with its periodic Gaussian sum in-session | not started |
| E4 | Lean: the Laplace-transform identity t^{-s/2} = Γ(s/2)^{-1} ∫_0^∞ u^{s/2-1} e^{-tu} du and the resulting positivity transfer (if H_C ≥ H_A pointwise then the s-weighted integrals compare) | A | ~70% | Mathlib's Gamma-integral API does not reach the needed form | not started; low value alone, but it is the second half of the upstream lemma |
| E5 | Formal statement (definition only) of the finite ordered-pair jellium energy J_{s,R} of upstream eq. (finite-ordered-jellium), plus a non-vacuity check (finite for distinct points) | A | ~60% | `∫∫ g_s` over a square needs an integrability lemma that Mathlib lacks for s near 2 | not started |
| E6 | s = 2 endpoint (Riesz s = d) | C | — | — | **outside upstream's statement**; not attempted |

## 4. What this would and would not establish

- **Would:** a numerical (Tier X) consistency check of upstream's renormalized corollary in the electron-gas case.
  If E3 and E4 succeed, it would also give a kernel-checked half of upstream's heat-comparison lemma. It would
  not give the field formulation or the thermodynamic limit, which remain informal.
- **Would not:** a Lean proof of the jellium corollary, which needs the full Petrache–Serfaty field machinery. It is
  also no evidence about s = 2. Tier X numerics support no claim.
