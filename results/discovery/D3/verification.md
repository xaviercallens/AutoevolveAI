# D3 independent verification (producer != verifier), 2026-10-10

**VERDICT: CONFIRMED_WITH_CORRECTIONS.** I recompiled all five theorems myself. Each depends only on
`[propext, Classical.choice, Quot.sound]`. They are not degenerate: for Riesz s = 4 the lattice energy is finite and
positive, and the vacancy attains it. All corrections below concern wording and definitions. None refutes a claim.

## 1. Recompile and axiom audit
I built a scratch file, `formal_cert/Triangular/VerifyScratchUO.lean`, which is the producer's source followed by my
checks. I deleted it afterwards and no olean was written. The compile command was
`python3 scripts/certified_numerics/lean_pinned.py compile formal_cert/Triangular/VerifyScratchUO.lean` (no `--olean`).
```
{"module": null, "rc": 0, "seconds": 15.6}
triangular_universally_optimal / vacancy_energy / vacancy_not_isometric_image /
vacancy_universally_optimal / universal_optimum_not_unique  -> [propext, Classical.choice, Quot.sound]
verify_vacancy_riesz4 / verify_latticeEnergy_riesz4_pos / verify_vacancy_ne_A /
verify_vacancy_not_density_half                           -> [propext, Classical.choice, Quot.sound]
verify_ctl_sorry (planted)                                 -> [propext, sorryAx, Classical.choice, Quot.sound]
OAI.AtomicTriangular.universal_energy_minimum              -> [propext, Classical.choice, Quot.sound]
```
- I grepped for `sorry|native_decide|^axiom|admit` in UniversalOptimality, AnyDensity, Riesz and RieszFinite. There were
  no hits. The planted `sorry` control was flagged, so the audit does detect `sorryAx`.
- The compile took 15.6 s, against the producer's 310 s, because only this file was elaborated. AnyDensity, Riesz and
  RieszFinite were loaded from the producer's `formal_cert/.olean_out`. Each olean's mtime is later than its source's
  mtime. Residual risk: `RieszFinite.olean` (15:42) is older than `Riesz.olean` (15:59), and raw `lean` does not check
  that an olean matches its source. A clean rebuild of the whole chain would remove that risk.
- The `universal_energy_minimum` used here is the proved upstream theorem in
  `OAI/Analysis/Triangular/Energy/Universal.lean`, which is axiom-clean. It is not the `sorry` stub in
  `ComparatorChallenges/TriangularEnergy.lean`. So "conditional on upstream" means conditional on whether upstream's
  statement and definitions are faithful. It does not mean an unproved hypothesis. I audited the definitions as they
  are written in the Comparator challenge file. That they match the OAI-tree definitions rests on Comparator
  acceptance, not on a check of mine.

## 2. Fidelity of `UniversallyOptimal` to CKMRV Def 1.3
I compared the definition with the CKMRV text: configuration and density at about line 94, Def 1.1 at 125, Def 1.2 at
227, Def 1.3 at 418.

| CKMRV | Lean (upstream + D3) | Match |
|---|---|---|
| configuration = nonempty, discrete, closed (every ball finite) | `LocallyFinite`: C ∩ closedBall 0 R finite for all R; nonempty follows from density ρ > 0 | yes |
| density: \|C ∩ B_r\| / vol B_r → ρ, closed balls | `DensityRho ρ` uses the same ratio with closed balls | yes |
| lower p-energy: liminf of (1/\|C∩B_r\|) Σ_{x≠y} p(\|x−y\|), each pair counted twice | `energy` = liminf of `diskEnergy`, the same sum taken in ENNReal (g ≥ 0) | yes |
| p(r) = g(r²) with g completely monotonic on (0,∞) | `AdmissiblePotential`: C^∞ on Ioi 0, g ≥ 0, (−1)^r g^(r) ≥ 0 | yes |
| competitors: every configuration of density ρ, compared by lower energy | every C' with `LocallyFinite` and `DensityRho ρ`; `energy g C ≤ energy g C'` | yes |
| **Def 1.2: C's p-energy exists, i.e. the limit exists, not only the liminf** | **dropped**: only the liminf is used for C | **gap** |

**Correction 1.** `UniversallyOptimal` is strictly weaker than CKMRV Def 1.3: it does not require E_p(C) to exist as a
limit. Requiring `LocallyFinite` of competitors is not a gap, because CKMRV configurations are locally finite by
definition. A weaker optimality notion admits more optima, which makes non-uniqueness easier to show. So
`universal_optimum_not_unique` certifies non-uniqueness among lower-energy universal optima. It agrees with the CKMRV
remark at about line 549 ("removing a single particle changes neither the density nor the energy"), but the Lean
proof does not show that the energy of A or of A\{0} exists as a limit. The docstring should say "Def 1.3 with lower
energy in place of energy" rather than "transcribes Def 1.3".

## 3. Statement-level traps
- **`vacancy_not_isometric_image` is meaningful.** Mathlib's `Isometry f` does not require f to be surjective, so the
  statement rules out a larger class of maps. Any isometry from ℝ² to ℝ² is affine (Mazur–Ulam, which the proof uses
  through `affineIsometryOfStrictConvexSpace`) and therefore bijective. An isometry between non-collinear subsets of
  the plane extends to the whole plane. So `f '' A = C` is exactly congruence, which is CKMRV's "isometric to C".
- The proof is not trivial. T(1,0) and T(2,0) lie in A\{0}; take their preimages a and b. Then 2a − b ∈ A, and by
  affinity f(2a − b) = 2T(1,0) − T(2,0) = 0, which contradicts 0 ∉ A\{0}.
- **`vacancy_energy` is not degenerate.** The upper bound diskEnergy(vacancy) ≤ (N/(N−1))·diskEnergy(A) together with
  N/(N−1) → 1 holds for every g. The lower bound comes from upstream. The proof does not rely on the energies being ⊤.
  I kernel-checked:
  `verify_vacancy_riesz4 : energy (riesz 4) vacancy = latticeEnergy (riesz 4) ∧ latticeEnergy (riesz 4) < ⊤`, and
  `verify_latticeEnergy_riesz4_pos : 0 < latticeEnergy (riesz 4)`, using the T(1,0) term of the tsum.

## 4. Verifier controls (kernel)
- `verify_vacancy_ne_A : vacancy ≠ A` is proved: 0 ∈ A but 0 ∉ A\{0}.
- Negative control: the false claim "A\{0} has density 1/2" is refuted in the kernel by
  `verify_vacancy_not_density_half : ¬ DensityRho (1/2) vacancy`, via `tendsto_nhds_unique` with `vacancy_density`.
- Planted `sorry` (`verify_ctl_sorry : vacancy = A`): `sorryAx` was flagged as expected (section 1).

## 5. Numerics (Riesz s = 4, density-1 lattice; script `.claude/jobs/6ecda88c/tmp/verify_d3/vac_numerics.py`)
```
lattice Riesz-4 sum (|j|,|k|<=3000): 5.783359
R=20 N_A=1261  E_A=5.504814 N_vac=1260  E_vac=5.500015
R=40 N_A=5005  E_A=5.643274 N_vac=5004  E_vac=5.642091
R=80 N_A=20065 E_A=5.712974 N_vac=20064 E_vac=5.712682
```
The lattice value of 5.7833593 is reproduced. The quantity the theorem predicts should vanish, E_A − E_vac, falls as
0.0048, 0.0012, 0.0003, roughly like R⁻². Both disk energies still sit about 1.2% below the lattice value at R = 80,
because points near the edge of the disk are missing neighbours, and that gap shrinks roughly like 1/R. The numerics
are consistent with the theorem; they do not prove it.

## 6. Overclaim check (preregistration and docstrings)
- H1, H2 and H3 are confirmed as stated in the Lean formulation. H1's "transcribing CKMRV Def 1.3" needs Correction 1.
- **Correction 2.** "Conditional on upstream `universal_energy_minimum`" (preregistration 1a; docstring line 11)
  should read: "relies on upstream's proved, axiom-clean theorem; conditional only on upstream's statement fidelity".
- **Correction 3.** The docstring at lines 16–17, "only the minimum *value* is determined", overreaches. What is shown
  is that the minimiser is not unique up to isometry among all configurations, for lower energy. Uniqueness among
  periodic configurations is still open for d = 2; D3 neither proves nor refutes it, and the text should say so.
- Assessment 1b is correct: "particles always arrange into a triangular lattice" is false in this formulation, and
  A\{0} is a kernel-checked counterexample.
- The history note (assessment 2) is supported by the CKMRV text. Ventevogel–Nijboer settled d = 1 (about line 363),
  and Cohn–Kumar gave another proof (about line 418). CKMRV write, about line 469: "no examples of universal optima in
  R^d with d > 1 had been rigorously proved". So "previously solved only in dimensions 8 and 24" is wrong. Before d = 2,
  the known cases were d = 1, 8 and 24, with d = 1 proved earlier than CKMRV.
