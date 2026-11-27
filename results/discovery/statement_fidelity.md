# Statement-fidelity audit of `OAI.AtomicTriangular.universal_energy_minimum`

Date 2026-10-10. Auditor: the producing agent (not independent; the D1/D2 verifiers read the same definitions separately, see
`D1/verification.md` §2 and `D2/verification.md` §1). Source: upstream `lean/ComparatorChallenges/TriangularEnergy.lean`
(sha256 af51979c7baecd3e9852637bbba29eff96cbb09cec84e15eff7d686f1a770616), openai/math commit adc7f124; the files under
`lean/ComparatorChallenges/TriangularEnergy.lean` and `lean/OAI/Analysis/Triangular/` are unchanged at the later upstream
commit fd4aeeb2 (2026-10-07, the release that withdrew three Hodge/K3 manuscripts; neither triangular manuscript was withdrawn).
Reference formulation: Cohn, Kumar, Miller, Radchenko, Viazovska, Ann. Math. 196 (2022), Definitions 1.1–1.3, as cited by the
upstream manuscript "Universal optimality of the triangular lattice" (September 23, 2026), Theorem 1.1.

| Item | Lean | Informal (manuscript / CKMRV) | Match |
|---|---|---|---|
| Potential class | `ContDiffOn ℝ ⊤ g (Ioi 0)`, `0 ≤ g t`, `0 ≤ (-1)^r iteratedDeriv r g t` for t > 0 | g : (0,∞) → [0,∞) smooth, completely monotone | yes (C^∞, not analytic; `iteratedDeriv` is global but equals the classical derivative at t > 0 because g is smooth near t) |
| Interaction | `g (‖x − y‖ ^ 2)` | f(\|x−y\|) with f(r) = g(r²) | yes |
| Configuration | `Set Plane`, locally finite (finite in every closed ball about 0) | locally finite point set, no multiplicities | yes |
| Density | `diskCount C R / (π R²) → 1`, closed balls centred at 0 | centred density 1 | yes |
| Energy | `liminf_{R→∞} N_R⁻¹ Σ_{x} Σ_{y ≠ x} ofReal(g(‖x−y‖²))` in `ℝ≥0∞`, N_R = points in the closed R-ball | lower energy: liminf of ordered-pair sum over points in B_R divided by their number | yes, up to closed vs open balls (not analysed; we do not claim the two liminfs agree in general) |
| Lattice | `A = range triangularPoint`, `triangularPoint (j,k) = b^{-1/2} (j + k/2, k b)`, b = √3/2 | triangular lattice of covolume 1 | yes: covolume b^{-1}·b = 1 |
| Lattice energy | `Σ' over A \ 0 of ofReal(g(‖a‖²))` in `ℝ≥0∞` (divergent sums = ⊤) | Σ_{a ∈ A∖0} g(\|a\|²) | yes |
| Conclusion | `latticeEnergy g ≤ energy g C ∧ latticeEnergy g = energy g A` | E_g(C) ≥ Σ g = E_g(A) | yes |
| Edge case N_R = 0 | `0⁻¹ = ⊤`, `⊤ * 0 = 0` in `ℝ≥0∞`, so diskEnergy = 0 | — | harmless: density 1 forces N_R > 0 eventually |

Scope notes.
* The upstream manuscript states it does **not** claim the stronger per-potential form of the Cohn–Kumar conjecture
  (a sharp auxiliary function for each potential); it proves the energy-comparison conclusion only. Our corollaries inherit
  exactly that scope.
* The manuscript already states informally that the theorem "includes every inverse power g(t) = t^{-p} with p > 0".
  D1 is therefore the kernel-checked form of a stated special case, not a new mathematical claim.
* Neither the Lean proof (AI-generated, Comparator-accepted by us under the pinned toolchain) nor the manuscript has been
  peer reviewed. This audit checks the statement only, not the proof.
