# H8 verification (independent verifier, producer != verifier), 2026-10-25

**VERDICT: ACCEPT_WITH_CORRECTIONS.** The Lean statements are correct and adequate. Corrections concern the protocol record and the NOTE's ⁴He claim.

## Recompile evidence
- Verbatim copy (`sha256 7ca35dd1...1c75`, identical to `H8/Autoresearch_SkBound.lean`) compiled with
  `leanprover--lean4---v4.34.0-rc2/bin/lean`, `LEAN_PATH` = qf-lake `build/lib/lean` + qf-lake packages (mathlib, batteries,
  aesop, Qq, proofwidgets, importGraph, LeanSearchClient, plausible) + rc2 `lib/lean`. These are the roots in the producer's
  `/proc/<pid>/maps` list (`h8_maps.txt`). `taskset -c 4,5`, page cache warmed with `warm_siblings.py`: **rc 0**, 0 errors/warnings,
  11 `#print axioms` lines, all `[propext, Classical.choice, Quot.sound]`.
- Scratch copy plus verifier additions (outside the repo), **rc 0**. Own `#print axioms` gives `sBog_le_sqrt`, `sBog_sq_eq_iff`,
  `feynman_sBog_exact`, `sBog_sq_le_via_project`: [propext, Classical.choice, Quot.sound]. Planted
  `planted_sorry := by sorry` shows `[propext, sorryAx, Classical.choice, Quot.sound]` and the file still exits rc 0, so the
  audit, not the exit code, is the gate.
- Imported `DualLength.olean` (2026-09-19 23:31) is newer than `lean_src/DualLength.lean` (23:09). Grep of the clean file
  for sorry/admit/native_decide/axiom: no match.

## Statement adequacy
- Conventions match the owner's `DualLength.lean`: `bogoliubovSq = (hc k)² + (hc k²/ks)²` with `ks = 2mc/ħ`. The proposal doc
  (`docs/DUAL_SCALE_PROPOSAL.md` §1) defines `k* := 2mc/ħ`, so `ks = k*`. Physics check: `ħ²k²/2m = ħc·k²·(ħ/2mc) = hc k²/ks` ✓;
  `2gn·ε₀ = 2mc²·ħ²k²/2m = (ħck)²`, so `ε_B² = ε₀(ε₀+2gn) = ε₀² + (ħck)²` ✓ (`epsBog_sq`).
- `S_B = ε₀/ε_B` is the textbook Bogoliubov/Feynman T=0 structure factor. A verifier lemma proves in the kernel
  `sBog = k/√(ks²+k²)`, i.e. `S = ħk/(2m)·1/√(c²+(ħk/2m)²)`. It has the phonon limit `k/ks = ħk/2mc` and tends to 1 at large k ✓.
- The bound `S ≤ √(k/2k*)` is verbatim the owner's DS-QF′ item (§4: "`S(k) ≤ √(k/2k*)`"), with the same `k*`. It matches
  `feynman_ge_iff`'s `S² ≤ k/(2ks)`. `sBog_sq_le_via_project` also shows the result is exactly that lemma applied to S_B.
- Hypotheses `0<hc, 0<k, 0<ks` are natural (positive wavenumber, interacting gas `c>0`) and satisfiable. Non-vacuity was
  kernel-checked by the verifier: equality case `sBog 1 1 1 ^ 2 = 1/2` via `sBog_sq_eq_iff`, and `sBog 1 1 2 ^ 2 = 4/5 < 1`.
- The negative control (`S ≡ 1` violates for `k < 2ks`) is correct but weak: it fixes `ks` while `S=1` is the `c→0` limit.
  NOTE.md says so.

## Corrections required
1. **Protocol.** KEEP came from a third run ("2b"), outside the preregistered "at most 2 attempts". result.json says so honestly.
   `results.tsv` and the commit should label H8 "KEEP (out-of-protocol infra retry)", not plain KEEP. The kernel result
   itself is unaffected: an independent recompile reproduces it.
2. **⁴He claim in NOTE.md.** "the measured peak is far above it [0.565]" is unsourced. The owner's proposal says explicitly
   "This repo holds **no `S(k)` data**", and that the measured dispersion only gives `S ≤ 2.60` at the roton. The
   0.565 number itself checks out: `ks = 2mc/ħ ≈ 3.0 Å⁻¹` for c≈238 m/s, and `√(1.92/6.0) ≈ 0.566`. Either pin a measured S(k)
   source (e.g. a neutron/X-ray ⁴He S(k) dataset) or reword to "would be refuted if S(k_roton) > 0.565 (no data held)".
3. "Bijl–Feynman exact for Bogoliubov" (`feynman_sBog_exact`) holds inside the model by construction, because `S_B` is
   *defined* as `ε₀/ε_B`. It is an algebraic identity, not an independent derivation of S_B from a many-body calculation. Say
   so in the scope section.
4. Novelty: none (AM-GM corollary of `feynman_ge_iff` + `ell_ge`), as NOTE.md states. Tier A applies to the Lean statements
   about the model formulas only.
