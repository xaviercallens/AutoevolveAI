# D4 independent verification (producer != verifier)

**VERDICT: ACCEPT_WITH_CORRECTIONS.** All four theorems recompile under pinned Lean 4.34.1 and use only whitelisted axioms.
The definitions match upstream's exactly, with `ball` in place of `closedBall`. The correction: the hypothesis
`LocallyFinite C` is **not needed** for the two identities. I kernel-checked both without it (see 3), so the
"for every locally finite C" framing understates the result, and the negative control asked for does not exist.

## 1. Recompile and axioms
- I copied `formal_cert/Triangular/OpenDisk.lean` verbatim (only the namespace renamed) into a scratch file and compiled it with
  `lean_pinned.py compile` (no `--olean`): rc 0, 33.8 s, deprecation warnings only. `#print axioms`:
  `densityOne_iff_open`, `energy_eq_openEnergy`, `universal_energy_minimum_open`, `A_densityOneOpen` each give
  `[propext, Classical.choice, Quot.sound]`. The `OAI.AtomicTriangular.universal_energy_minimum` it imports (the proved
  upstream `OAI/Analysis/Triangular/Energy/Universal.lean`, not the `sorry` challenge file) gives the same.
- Positive control: a planted `theorem verifyPlanted : (1:ℕ) = 2 := sorry` reports `[sorryAx]`, so the audit can detect a planted `sorry`.
- Grep of OpenDisk.lean for `sorry|native_decide|axiom|admit|unsafe|implemented_by|extern`: no hits.
- Preregistration commit 64d27b9 (07:03 UTC) comes before the proof commit 080ac07 (07:34 UTC).

## 2. Statement adequacy
Upstream definitions are in `OAI/Analysis/Triangular/Energy/Basic.lean`, textually identical to
`ComparatorChallenges/TriangularEnergy.lean`. Compared line by line:
- `openDiskPoints` is `diskPoints` with `Metric.closedBall` replaced by `Metric.ball`, and keeps the same `if h : ... .Finite then
  h.toFinset else ∅`. `openDiskCount`, `DensityOneOpen` (same `/(π R²)`, `atTop`, `𝓝 1`), `openDiskEnergy` (same
  `count⁻¹ * ΣΣ_{y≠x} ofReal (g ‖x-y‖²)`) and `openEnergy` (`liminf … atTop`) are token-for-token the same otherwise.
- Decidability: upstream also has `open Classical`. In any case `dif_pos`/`dif_neg` rewrite under any `Decidable`
  instance, and `Set.Finite.toFinset` takes no instance, so there is no hidden mismatch. `Plane` is the same
  `EuclideanSpace ℝ (Fin 2)` abbrev.
- `universal_energy_minimum_open` has upstream's exact conclusion shape, with `DensityOneOpen`/`openEnergy` substituted, and it
  still assumes `LocallyFinite C` (closed-ball local finiteness, which is equivalent to the open-ball version).
- Vacuity: `A_densityOneOpen` is proved, so the hypothesis set of `universal_energy_minimum_open` is inhabited. The
  `else ∅` branch is never taken in the proofs: every use goes through `dif_pos (hC _)`.

## 3. Negative control: none exists; the hypothesis is superfluous
Argument: if `C` is not locally finite, pick `R0` with `C ∩ closedBall 0 R0` infinite. For every `R > R0`, both
`C ∩ closedBall 0 R` and `C ∩ ball 0 R` contain that set and are infinite, so `diskPoints` and `openDiskPoints` are both `∅`.
The two energy functions are therefore eventually equal (both `0⁻¹ * 0 = 0` in `ℝ≥0∞`) and have the same liminf. The two
count ratios are eventually `0`, so `DensityOne` and `DensityOneOpen` are both false.
I kernel-checked this in a scratch file importing `Triangular.OpenDisk`, rc 0, whitelist axioms only:
- `energy_eq_openEnergy_any (g) (C) : energy g C = openEnergy g C`, with no hypothesis on `C`;
- `densityOne_iff_open_any (C) : DensityOne C ↔ DensityOneOpen C`, with no hypothesis on `C`.
Control showing the result is not just definitional: for `C = {single 0 1}` (one point on the unit circle),
`ctl_open : openDiskCount C 1 = 0` and `ctl_closed : diskCount C 1 = 1` (both kernel-checked). The pointwise count
functions differ at the boundary radius, and only their limits agree.
Note: the unconditional energy statement relies partly on upstream's `else ∅` convention. A non-locally-finite `C`
gets energy `0` under both definitions. That is a modelling artefact of upstream, which excludes such `C` through `hC`; it is not a
physical statement. A copy of the scratch file is kept at `/home/callensxavier_gmail_com/.claude/jobs/6ecda88c/tmp/verify_d4/VerifyScratchD4b.lean`.

## 4. Human proof versus Lean proof
The preregistered sketch is correct, and the Lean proof follows it:
- `open_eq_closed_shift` / `closed_eq_open_shift` produce the shifts δ, δ' ∈ (0,1). They use the finite set inside
  `closedBall R` (respectively `R+1`) and take sup'/inf' of the norms, which is the "slightly smaller/larger radius" step.
- Energy: `openDiskEnergy = diskEnergy ∘ (R ↦ R-δ R)` and `diskEnergy = openDiskEnergy ∘ (R ↦ R+ε R)`. Both
  reparametrisations tend to `atTop`, and `liminf u ≤ liminf (u∘φ)` for such φ. Two inequalities then give equality.
  The sketch's phrase "take each other's values at radii within distance one" is made precise as "reparametrisations that tend to
  infinity". The bound of one is used only for that.
- Density: `N_c(R-1) ≤ N_o(R) ≤ N_c(R)` (as preregistered) and, for the converse, `N_o(R) ≤ N_c(R) ≤ N_o(R+1)`.
  The squeeze uses `f(R+c)/(πR²) → 1`. The sketch states only the first sandwich; the second is the routine symmetric
  step it implies.

## 5. Significance: how much of guideline 4 this settles
It settles guideline 4 **only for upstream's observables**: centred disks at the origin, density by `N(R)/(πR²)`,
energy as the **liminf** of the per-point disk energy, and potentials valued in `ℝ≥0∞` (so no cancellation). Within those, the
choice of open or closed boundary cannot change density one, the lower energy, or the universal-optimality conclusion.
It does **not** cover:
- other window shapes (squares, other convex bodies) or non-centred or moving windows;
- `limsup` (upper) energies, or a `lim` that exists only along subsequences;
- boundary conditions in the physical sense (periodic, hard wall, or a neutralising background such as jellium or
  Coulomb, where the shape of the boundary does matter for signed or conditionally convergent sums).
The result is also mathematically soft. It is a radius-shift argument that works for any liminf/limit along `R → ∞` of quantities
that depend only on `C ∩ disk`. It should be described as a robustness check of the formal statement, not as a new physics result.

## Corrections required
1. Drop the "for every locally finite C" qualifier from the D4 headline (or add the unconditional versions above).
   Both identities hold for every `C`; only `universal_energy_minimum_open` needs `LocallyFinite C`, and only because upstream assumes it.
2. Change the wording "fully settles guideline 4" to "settles it for upstream's centred-disk liminf observables" (see 5).
3. Optional: say in the docstring that the theorem is not definitional (pointwise counts differ, `ctl_open`/`ctl_closed`).
