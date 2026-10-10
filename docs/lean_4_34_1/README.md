# Common Lean toolchain: v4.34.1

Upstream latest release at the time of the check (2026-10-10): `leanprover/lean4` **v4.34.1**.
Mathlib tag `v4.34.1` = commit `d13f23b723b8a846827a245b89c10fc7d3f11612`.

Before this change the ~100 pinned projects on disk 2 were spread over 12 toolchains
(4.28.0 … 4.34.1); 24 on `v4.34.0-rc2`, 21 on `v4.33.1`, only 3 on `v4.34.1`.

## What was verified (real output, 2026-10-10)

| Stream | Result on v4.34.1 |
|---|---|
| AutoevolveAI `formal/` (`lake build ANSE`) | exit 0, 3785 jobs; axiom audit of 6 MasterMathTribunal files + VerletSymplectic: 109 theorems, 0 `sorryAx`, axioms ⊆ {propext, Classical.choice, Quot.sound} |
| LeanMaster, 10 libraries (trial copy) | `lake build` exit 0, **9101 jobs, 0 failures, 0 `sorry` warnings** |
| LeanMaster `tools/axiom_audit.py`, per library | 866 theorems audited, 0 failing (table below) |

| Library | Theorems audited | Failing |
|---|---:|---:|
| StringTheoryFoundation | 63 | 0 |
| DualScaleM24Formalization | 62 | 0 |
| DoubleFieldTheory | 44 | 0 |
| DualScaleValidation | 23 | 0 |
| Lean5Corpus | 53 | 0 |
| StringTheoryFormalization | 89 | 0 |
| DualScaleStream2 | 206 | 0 |
| DualScaleCosmology | 59 | 0 |
| DualScaleMoonshine | 101 | 0 |
| DualScaleDyons | 166 | 0 |

Raw: `leanmaster_axiom_audits.json`.

## Caveats (read before citing)

* AutoevolveAI `formal/` still has 4 genuine `declaration uses sorry` warnings
  (`Basic:148`, `System2:160,176`, `Theorems:49`). A green `lake build` there is **not**
  a proof claim; the audit above covers only the MasterMathTribunal and Verlet files.
* The LeanMaster result is from a **trial copy**, not the live checkout, which is still
  on `v4.34.0-rc2`. The audit covers the repo's own gate (G3). The other gates in
  `lean-proof-gate` (statement lock, producer != verifier) were not re-run.
* One breaking change was met: `Mathlib.Logic.Basic` no longer exists at v4.34.1; it is
  `Mathlib.Basic.Logic.Basic`. LeanMaster needed no source change.
* Not compiled, only import-checked (0 missing Mathlib modules): `leanmaster-v2.2.0`
  (4.33.1), `stream2-lean/leanmaster-v4.34.0-trial`, `K3-DarkMatter`, `Elenchus`,
  `QuantumFluids`, `DualScaleTopologicalUniverseModel-LeanProposal`. Import existence
  is not compilation.

## Applying to the live LeanMaster checkout

Not done automatically: other sessions and the nightly cycle build against its
`.lake` (4.34.0-rc2) and flipping the pin forces a rebuild under them.

1. Copy `leanmaster.lean-toolchain` over `lean-toolchain`.
2. `patch lakefile.lean < leanmaster.lakefile.patch`.
3. Copy `leanmaster.lake-manifest.json` over `lake-manifest.json`.
4. Use a `.lake` whose `packages/` is the shared 4.34.1 set:
   `/mnt/disks/disk-socrateai-local-1/AutoevolveAI/formal_.lake-v4341/packages`
   (symlink it; do not reuse `lake-v434`, which holds rc2 builds).
5. `lake build` the nine libraries, then `python3 tools/axiom_audit.py <lib>` for each.
