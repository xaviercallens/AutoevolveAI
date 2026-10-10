# D1 / D1b independent verification

Verifier: separate agent (producer != verifier), 2026-10-10, worktree commit 4d5a6b3. Toolchain: `scripts/certified_numerics/lean_pinned.py`
(upstream-pinned Lean 4.34.1 + Mathlib + openai/math OAI). Scratch Lean files `formal_cert/Triangular/VerifyScratch{Ax,Neg,NegB}.lean`
were compiled without `--olean` and deleted afterwards (`find formal_cert -iname '*VerifyScratch*'` returns nothing). The two
`--olean` recompiles rewrote the producer's `formal_cert/.olean_out/Triangular/{Riesz,RieszFinite}.olean`; `git status` shows
nothing there, so the directory is untracked or ignored.
**Housekeeping incident.** While this verification was running, the producer's commit 6845de3 (D2) picked up the three scratch files,
including `VerifyScratchNegB.lean`, which contains a deliberate `sorry`. They are now deleted in the working tree (`git status`: ` D`),
but the deletion is not committed. The producer should commit that removal.

## VERDICT: CONFIRMED_WITH_CORRECTIONS

The Lean results hold as stated, with only the three whitelisted axioms; the negative controls fail as they should; the numerics agree.
The corrections are about wording in `docs/DISCOVERY_PROPOSAL_2026-10-10.md` and the theorem docstring (see the last section), not about the proofs.

## 1. Statement adequacy

* **Potential.** `riesz s t = t^(-(s/2))`, evaluated at `t = ‖x−y‖²`. For r > 0, `riesz s (r^2) = r^(-s)` (verifier lemma, kernel-checked
  in `VerifyScratchAx`, via `rpow_natCast`/`rpow_mul`). Every call site has t > 0: `latticeEnergy` sums over `x ∈ A, x ≠ 0`, and
  `diskEnergy` sums over `y ∈ (diskPoints C R).erase x`. The junk value `riesz s 0 = 0` is never evaluated.
* **Upstream definitions** (`OAI/Analysis/Triangular/Energy/Basic.lean`, the same text as `ComparatorChallenges/TriangularEnergy.lean`):
  `energy g C = liminf_{R→∞} (diskCount C R)⁻¹ · Σ_{x≠y ∈ C∩B̄(0,R)} ofReal(g ‖x−y‖²)` in `[0,∞]`, summed over ordered pairs;
  `DensityOne C` means `#(C∩B̄(0,R))/(πR²) → 1`; `LocallyFinite C` means every closed ball meets C in a finite set. This is the
  Cohn–Kumar "lower energy" of an infinite configuration, with f(r) = g(r²). `latticeEnergy g = Σ'_{a∈A∖0} ofReal(g‖a‖²)`, which is
  the per-point energy of a lattice in the same ordered-pair normalisation. The kernel prints D1 as
  `0 < s → ∀ C, LocallyFinite C → DensityOne C → latticeEnergy (riesz s) ≤ energy (riesz s) C`, and that statement says exactly
  "Riesz-s optimal among all locally finite density-1 configurations" in upstream's sense.
* **Smoothness order.** `#print` gives `ContDiffOn ℝ ∞ g (Set.Ioi 0)`. Both `example : ((⊤:ℕ∞) : WithTop ℕ∞) ≠ ⊤` and `… = ∞`
  compile, so the order is C^∞ and not ω (analytic). It is not a hidden extra requirement.
* **Admissibility proof.** It uses only facts at t > 0: `contDiffAt_rpow_const_of_ne (t ≠ 0)`, `rpow_pos_of_pos`, and the global
  identity `deriv^[r] (x ↦ x^p) = descPochhammer(p,r)·x^(p−r)` evaluated at t > 0. Since `iteratedDeriv r g t` depends only on the germ
  of g at t, the junk values for t ≤ 0 cannot matter. The sign pattern is not satisfied for a trivial reason: control (a) below shows
  that the same proof breaks, and the predicate becomes false, as soon as the exponent has the wrong sign.
* **Vacuity.** (i) For 0 < s ≤ 2, `latticeEnergy = ⊤`, because the lattice sum diverges (§3b). D1 then reduces to `energy C = ⊤` for
  every admissible C. That is true but carries no physics. The informative range is **s > 2**. (ii) For s > 2 some admissible C has
  finite energy: A itself. Upstream's second conjunct gives `latticeEnergy g = energy g A`, D1b gives `< ⊤`, and upstream proves
  `triangular_locallyFinite`/`triangular_densityOne` (`Energy/Mixtures.lean:258,332`). So for s > 2 the inequality is a genuine
  comparison against a finite, attained minimum. Those two lemmas are stated for `TriangularUniversal.triangularLattice`, which uses
  √(2/√3) coordinates. Upstream bridges it to `A` with `A_eq_support` (`Lattice/LatticeGeometry.lean:28`). The verifier read that
  bridge but did not kernel-check it separately.
* **D1b lattice.** Upstream `triangularPoint (j,k) = (√b)⁻¹ (j + k/2, k b)` with b = √3/2. Its covolume is (1/b)·b = 1 (basis
  determinant), and ‖p‖² = (1/b)(j² + jk + k²) = (2/√3)(j²+jk+k²). The upstream lemma is for `normForm x y = x² − xy + y²`. The
  `k ↦ −k` reindexing is correct. The (0,0) term is `0^(−σ) = 0` (rpow junk), which is harmless because only summability is used, via
  an injective map from `A∖0`.

## 2. Independent recompile and axiom audit

```
lean_pinned.py compile formal_cert/Triangular/Riesz.lean --olean Triangular.Riesz          -> rc 0, 12.9 s
lean_pinned.py compile formal_cert/Triangular/RieszFinite.lean --olean Triangular.RieszFinite -> rc 0, 13.5 s
   (only a deprecation warning: EuclideanSpace.single_apply)
lean_pinned.py compile formal_cert/Triangular/VerifyScratchAx.lean  (verifier-written)     -> rc 0
'TriangularRiesz.riesz_admissible'                depends on axioms: [propext, Classical.choice, Quot.sound]
'TriangularRiesz.triangular_riesz_optimal'        depends on axioms: [propext, Classical.choice, Quot.sound]
'TriangularRiesz.latticeEnergy_riesz_lt_top'      depends on axioms: [propext, Classical.choice, Quot.sound]
'OAI.AtomicTriangular.universal_energy_minimum'   depends on axioms: [propext, Classical.choice, Quot.sound]
'ctl_a_false'                                     depends on axioms: [propext, Classical.choice, Quot.sound]
```
`grep -rnE "sorry|native_decide|^axiom|admit" formal_cert/Triangular/` finds only `Axioms.lean:16-19`: the producer's planted controls
`ctl_sorry` and `ctl_cheat`. The producer's own audit shows both caught: `sorryAx` and `ctl_cheat` appear in their axiom lists.
Upstream Comparator evidence: `results/openai_math/hypotheses/night_2026-10-08/TRI_CMP/result.json` reports `COMPARATOR_ACCEPTS`,
"Your solution is okay!", real 140m35s. That run does not establish human statement audit or an external kernel check.

## 3. Negative controls (verifier-written)

(a) **s = −2, so riesz = t¹.** The producer's proof was transplanted with `-2` in place of `s`. The `hs` hypothesis was dropped,
since it is unprovable here. The transplant fails at `VerifyScratchNeg.lean:13:35: error: failed to prove strict positivity`, i.e.
`positivity` on `0 < -2/2`, which `ascPochhammer_pos` needs. The claim is
in fact false, and the verifier proved its negation: `ctl_a_false : ¬ AdmissiblePotential (riesz (-2))` compiles with whitelisted
axioms. Argument: riesz (−2) = id, iteratedDeriv 1 id 1 = 1, and (−1)¹·1 < 0.

(b) **s = 2.** The transplant was truncated: it is the first block of the D1b proof, followed by `sorry`. The point it shows is that
the error fires before that `sorry` is reached: `VerifyScratchNegB.lean:7:32: error: linarith failed` on `hσ : 1 < 2/2`. `hσ` is the
proof's only dependence on s, and it feeds `summable_normForm_neg_rpow`, which needs σ > 1. So the full proof cannot get past this
step either. The claim is
false. A density-1 lattice has #(A∩B_R) = πR² + O(R) points, so by partial summation
Σ_{0<|a|≤R} |a|^{-2} = 2π log R + O(1) → ∞. Numerically (own numpy code, triangular lattice, s = 2):
`R=50: S−2π log R = 2.5213; R=100: 2.5222; R=200: 2.5178; R=400: 2.5185`. The difference is constant, so S grows like 2π log R.

## 4. Independent numerics (`/home/callensxavier_gmail_com/.claude/jobs/6ecda88c/tmp/verify_d1/numerics.py`, mpmath 30 digits + numpy)

Closed forms: Σ'(j²+jk+k²)^{-σ} = 6 ζ(σ) L(σ,χ₋₃) and Σ'(j²+k²)^{-σ} = 4 ζ(σ) β(σ), with σ = s/2. The triangular lattice gets an
extra factor (2/√3)^{-σ}. As a cross-check, direct lattice sums up to radius R plus a density-1 integral tail 2πR^{2−s}/(s−2):

| s | triangular (closed) | triangular (direct) | square (closed) | square (direct) | square − triangular |
|---|---|---|---|---|---|
| 3 | 8.8927451004 | 8.892744905 | 9.0336216831 | 9.033621562 | 0.14087658 |
| 4 | 5.78335929968 | 5.783359299 | 6.02681203969 | 6.026812040 | 0.24345274 |
| 6 | 4.1412565472 | 4.141256547 | 4.6589136156 | 4.658913616 | 0.51765707 |

The triangular energy is below the square one at every s tested, as D1 requires (the square lattice is an admissible C). The closed
form ‖p(j,k)‖² = (2/√3)Q(j,k), computed from upstream's coordinates at 1000 random (j,k) ∈ [−50,50]², has a maximum error of 1.6e−27.

## 5. Overclaim scan of `docs/DISCOVERY_PROPOSAL_2026-10-10.md`

* **Probabilities** (85%, 70%, ...) are subjective priors written before the attempt. They are not measurements and should be labelled
  as such. They do not enter any reported result.
* **"Cohn–Kumar conjecture" framing.** The framing is broadly right. Cohn–Kumar (JAMS 2007) conjectured that the hexagonal lattice is
  universally optimal in R², i.e. optimal for every f(r) = g(r²) with g completely monotone, and upstream's definition matches their
  lower-energy notion. Correction: §3 should say the corollary would settle the *Riesz s > 2 special case* conditional on upstream.
  For s ≤ 2 it is the degenerate `⊤ = ⊤` case. The full conjecture is upstream's Gaussian-to-all-g statement, not D1.
* **Lattice-only attributions.** These match the verifier's knowledge (not re-checked against the sources): Rankin (1953) and Cassels
  (1959), Epstein-zeta minimum among 2D lattices; Ennola (1964) and Diananda (1964), alternative proofs; Montgomery (1988), theta
  functions, which give the Epstein case via the Mellin transform. Recommend adding full citations.
* **"Optimality among all configurations in 2D is open".** It was open as far as the verifier knows: Cohn–Kumar–Miller–Radchenko–
  Viazovska (Annals 2022) proved universal optimality only in dimensions 8 and 24. **Not confirmed by a search**: a 2025–26 result, or
  the AI-generated upstream proof itself, could change this. Do not state it as fact without a literature check.
* **Stale text.** §4 "Result recorded … when the compile finishes" is out of date (the compile has finished: rc 0). §1 "Comparator-
  accepted" is supported by TRI_CMP. The caveat "statement fidelity not human-audited" stays mandatory.

## Corrections required

1. In the docstring of `triangular_riesz_optimal` and in the proposal, replace "for s ≤ 2 both sides are *typically* ∞" with
   "for 0 < s ≤ 2 the lattice energy is ∞ (divergent Epstein sum), so the statement is informative only for s > 2".
2. Proposal §3: say "Riesz special case (s > 2) of the Cohn–Kumar conjecture, conditional on upstream's unaudited theorem", and
   mark the P(achieve) values as priors.
3. Proposal §3: soften "open in the literature" to "open as far as we know (no 2026 literature search done)", and add references for
   Rankin, Cassels, Ennola, Diananda, Montgomery, Cohn–Kumar and CKMRV.
4. Proposal §4: update the stale compile sentence.
