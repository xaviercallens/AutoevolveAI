# D2 request: narrow Comparator run for four openai/math challenges

Status: REQUEST. Nothing in this file has been run. It needs your approval because it downloads and
installs (lake update, Mathlib cache, comparator, landrun, lean4export). Written by lane LT_D, 2026-10-08.

## What the LT_D pilot did and did not establish (measured here)

Artifacts: `results/openai_math/hypotheses/night_2026-10-08/LT_D/` (`part1a_challenge.json`,
`part1b_closure.json`, `part2_elenchus.json`, `part2_statement_lock.json`, `controls.json`).
Controls (2 positive, 3 negative on the driver's classifiers) passed before and after.

- 1a: `ComparatorChallenges/LiebThirring.lean` elaborates under LeanMaster's Lean v4.34.0-rc2 + Mathlib
  (exit 0, 732 s, cold Mathlib load). That is a statement-parses check only (the file ends in `sorry` by design).
- 1b: of the 38 closure files (13,717 lines), **14 compiled, 1 failed, 23 blocked**. First blocking error,
  `OAI/Analysis/LiebThirring/FiniteParity.lean:505:21: Unknown constant Set.equivOfEq`. This is
  version drift: upstream pins Lean v4.34.1 and its own Mathlib commit, LeanMaster has v4.34.0-rc2.
  Upstream files were not patched. `Main` was not compiled, so the axiom check (1c) was NOT run.
- Conclusion: the pilot does NOT show the Lieb-Thirring proof is kernel-valid here, and does not refute it.
  It shows the closure cannot be checked with LeanMaster's Mathlib; upstream's pinned Mathlib is needed.
- Elenchus (run in-process with REPO_ROOT pointed at LeanMaster, disclosed deviation): all four files exit 1
  with `NO_FOOTPRINT` ("compiled cleanly and emitted no axiom footprint"). Expected for challenge files that
  end in `sorry` and carry no `#print axioms`; no vacuity or smuggling finding was printed.
- No claim is Tier A. No Lean kernel check of any exact challenge statement against a proof ran here.

## The four challenges

| Challenge | sha256 of the .lean file | Solution closure (solution_scan_lt_triangular_packing.json) |
|---|---|---|
| LiebThirring | 008bcfc167bb1931b14682171578ab2422a7176658bafd95dafb8feb13ab8ade | 38 files, 13,717 lines |
| TriangularEnergy | af51979c7baecd3e9852637bbba29eff96cbb09cec84e15eff7d686f1a770616 | 227 files, 65,932 lines (Energy.Universal root; Triangular.Main: 215 files, 64,626) |
| AtomicGaussian | 6207d477e9c4c19689e5df96f485417ef4534a1ac8c5aed1cfdef8ec76ad303d | 216 files, 64,715 lines (GaussianMinorants root) |
| PlanarPacking | 6f2ffada083cfcceddcfbcfc01409e046d7fdb729994443d285cfd9552c1c202 | 563 files, 916,202 lines |

Static scan found no sorry/admit/axiom in any closure (all depend on Mathlib only). LeanMaster
`statement_lock.py --update` on byte-identical copies: "locked 101 declarations in 4 files", `--check` OK
(per-declaration hashes in `part2_statement_lock.json`). A Comparator run should be tied to these hashes.

## Commands (quoted from the real READMEs, fetched 2026-10-08)

leanprover/comparator README: requires `landrun` ("compiled from the main branch's source, must be in PATH"),
`lean4export` (version compatible with your Lean, in PATH), optional `nanoda`; env overrides
`COMPARATOR_LANDRUN`, `COMPARATOR_LEAN4EXPORT`, `COMPARATOR_NANODA`. Build: `lake build lean4export comparator`.
Config JSON: `{"challenge_module": ..., "solution_module": ..., "theorem_names": [...], "permitted_axioms": ["propext","Quot.sound","Classical.choice"]}`.

openai/math lean/ComparatorChallenges README: "Install `comparator`, `landrun`, and `lean4export`, and make
them available on `PATH`. Then, from `lean/`:"

    lake update
    lake exe cache get
    lake env comparator ComparatorChallenges/QuasiRiemannHypothesis.json

For this request substitute `ComparatorChallenges/LiebThirring.json` etc. (check the file exists in the clone first).
Run it in a COPY of upstream `lean/` (not in the LeanMaster clone), so `.lake` of LeanMaster is untouched.

## Cost (estimates, not measurements, except where stated)

- Measured: disk 134 GB free on the data disk; cold `import Mathlib` load took several minutes here;
  the 14 compiled Lieb-Thirring files took 18-69 s each.
- Estimated: `lake exe cache get` downloads several GB of Mathlib oleans; building landrun/lean4export/comparator
  minutes; Lieb-Thirring closure compile tens of minutes on one core; Triangular/Atomic hours; PlanarPacking
  (916k lines) likely many hours to days and large disk. These are guesses to be replaced by the first run.

## Recommended order

1. LiebThirring (smallest closure, 38 files; also the one where version drift bit, so upstream's pin matters).
2. TriangularEnergy, 3. AtomicGaussian (about 65k lines each), 4. PlanarPacking last.
Run the `permitted_axioms` whitelist as above and report the Comparator output verbatim.
