# Kernel replay of our own Tier A Lean modules (2026-10-26)

Checker: `leanchecker MODULE` from the pinned Lean 4.34.1 toolchain, with the LEAN_PATH of `scripts/certified_numerics/lean_pinned.py` (pinned openai/math build + Mathlib + `formal_cert/.olean_out`). It replays each module's own declarations through the kernel (default mode, not `--fresh`: imported Mathlib/openai-math declarations are trusted).

Counts: {'OK': 93, 'SKIPPED': 778} over 871 non-control modules under formal_cert/{Triangular,Autoresearch,Programmes}.

## Forgery control

`/tmp/kr_forged/src/KRForged.lean` adds `False` via `set_option debug.skipKernelTC true` + `addDecl`. `#print axioms` reports: 'does not depend on any axioms' (the gate would pass it). `leanchecker KRForged` exits rc=1 with `(kernel) declaration type mismatch, 'KRForged.forged_false' has type True but it is expected to have type False`. Log: `logs/FORGED_CONTROL.log`.

## Grep (skipKernelTC | addDecl | native_decide | implemented_by/implementedBy)

Scanned 871 non-control files (all of them, including skipped ones): 0 hits on these four patterns.
Extra patterns (ofReduceBool, axiom declarations, unsafe/extern/opaque, sorry/admit, set_option debug.): hits listed below, all are in comments or in the audit script `Triangular/Axioms.lean` that carries planted controls:

- sorry: formal_cert/Triangular/Axioms.lean:42  `theorem ctl_sorry : TriangularRiesz.riesz 1 1 = 0 := by sorry`
- axiom_decl: formal_cert/Triangular/Axioms.lean:43  `axiom ctl_cheat : False`
- sorry: formal_cert/Programmes/EvoGraph/Examples.lean:6  `Real theorems (planted `sorry`/axiom controls live in `EvoGraphPlantedControls.lean`). All with uniform`
- sorry: formal_cert/Programmes/PopGen/FixationDataCert.lean:15  `refused by the same kernel check. Planted `sorry`/`axiom` controls for this module are in`
- sorry: formal_cert/Programmes/PopGen/MoranModel.lean:237  `/-! ## Controls (real theorems; planted sorry/axiom controls live in `PopGenProgControls.lean`) -/`
- sorry: formal_cert/Programmes/SandierSerfatyStatement.lean:52  `Planted `sorry` / custom-axiom proofs of `SandierSerfatyStatement` live in `SandierSerfatyStatementControls.le`

## Per-module table

| module | olean fresh? | leanchecker rc | seconds | notes |
|---|---|---|---|---|
| Triangular.AnyDensity | yes | 0 | 191.4 |  |
| Triangular.Axioms | n/a | - | - | SKIPPED: audit script that embeds planted controls (sorry, axiom ctl_cheat), expected to fail |
| Triangular.OpenDisk | yes | 0 | 193.1 |  |
| Triangular.OpenDiskAny | yes | 0 | 190.6 |  |
| Triangular.Riesz | yes | 0 | 164.2 |  |
| Triangular.RieszFinite | yes | 0 | 185.3 |  |
| Triangular.UniversalOptimality | yes | 0 | 177.1 |  |
| Autoresearch.DipolarExciton | yes | 0 | 161.1 |  |
| Autoresearch.DipolarExcitonMultipolar | yes | 0 | 168.9 |  |
| Autoresearch.DipolarExcitonStep1 | yes | 0 | 166.5 |  |
| Autoresearch.DyadicHilbert | yes | 0 | 145.9 |  |
| Autoresearch.DyadicHilbertW4 | rebuilt now (44.8s) | 0 | 164.3 | olean was missing -> built with lean_pinned flags into .olean_out |
| Autoresearch.KeldyshCM | yes | 0 | 150.4 |  |
| Autoresearch.PopGenFisher | yes | 0 | 196.6 |  |
| Autoresearch.PopGenImportBoth | rebuilt now (10.0s) | 0 | 241.5 | olean was missing -> built with lean_pinned flags into .olean_out |
| Autoresearch.PopGenWrightFisher | yes | 0 | 263.4 |  |
| Autoresearch.Yukawa | yes | 0 | 797.4 |  |
| Autoresearch.YukawaMix | yes | 0 | 718.5 |  |
| Programmes.CompletelyMonotone.Applications | yes | 0 | 689.9 |  |
| Programmes.CompletelyMonotone.Basic | yes | 0 | 185.2 |  |
| Programmes.CompletelyMonotone.Bernstein | yes | 0 | 152.9 |  |
| Programmes.CompletelyMonotone.Corollaries | yes | 0 | 183.7 |  |
| Programmes.CompletelyMonotone.Examples | yes | 0 | 189.5 |  |
| Programmes.CompletelyMonotone.Laplace | yes | 0 | 160.1 |  |
| Programmes.CompletelyMonotone.Limits | yes | 0 | 170.0 |  |
| Programmes.CompletelyMonotone.MathlibOnly | yes | 0 | 243.9 |  |
| Programmes.CompletelyMonotone.MathlibOnlyBridge | yes | 0 | 226.6 |  |
| Programmes.EvoGraph.BirthDeath | yes | 0 | 230.7 |  |
| Programmes.EvoGraph.EvoGraphImportAll | rebuilt now (21.3s) | 0 | 124.0 | olean was missing -> built with lean_pinned flags into .olean_out |
| Programmes.EvoGraph.Examples | yes | 0 | 129.1 |  |
| Programmes.EvoGraph.Transport | yes | 0 | 161.3 |  |
| Programmes.Famille.Acronymes | n/a | - | - | SKIPPED: source modified 16.2 min before run start (another job writing) |
| Programmes.FeynmanBijl.Basic | yes | 0 | 162.2 |  |
| Programmes.PopGen.Absorption | yes | 0 | 194.2 |  |
| Programmes.PopGen.FixationDataCert | rebuilt now (37.7s) | 0 | 172.2 | olean was missing -> built with lean_pinned flags into .olean_out |
| Programmes.PopGen.MoranFixation | yes | 0 | 276.8 |  |
| Programmes.PopGen.MoranModel | yes | 0 | 286.8 |  |
| Programmes.PopGen.PopGenProgImportAll | rebuilt now (53.6s) | 0 | 290.2 | olean was missing -> built with lean_pinned flags into .olean_out |
| Programmes.PopGen.Price | yes | 0 | 182.6 |  |
| Programmes.PopGen.PriceImportAll | rebuilt now (35.6s) | 0 | 153.9 | olean was missing -> built with lean_pinned flags into .olean_out |
| Programmes.PopGen.WrightFisherFixation | yes | 0 | 115.4 |  |
| Programmes.SandierSerfaty.Asserts | yes | 0 | 137.8 |  |
| Programmes.SandierSerfaty.Axioms | rebuilt now (41.0s) | 0 | 128.0 | olean was missing -> built with lean_pinned flags into .olean_out |
| Programmes.SandierSerfaty.AxiomsAll | rebuilt now (63.1s) | 0 | 144.0 | olean was missing -> built with lean_pinned flags into .olean_out |
| Programmes.SandierSerfaty.AxiomsCalcK | rebuilt now (32.2s) | 0 | 228.8 | olean was missing -> built with lean_pinned flags into .olean_out |
| Programmes.SandierSerfaty.Bcons | yes | 0 | 914.9 |  |
| Programmes.SandierSerfaty.Bridge | yes | 0 | 187.9 |  |
| Programmes.SandierSerfaty.CalcK | yes | 0 | 115.7 |  |
| Programmes.SandierSerfaty.CalcKCore | rebuilt now (40.7s) | 0 | 138.0 | olean was stale -> built with lean_pinned flags into .olean_out |
| Programmes.SandierSerfaty.CalcKF0 | yes | 0 | 376.9 |  |
| Programmes.SandierSerfaty.CalcKF1 | yes | 0 | 392.5 |  |
| Programmes.SandierSerfaty.CalcKF2 | yes | 0 | 275.9 |  |
| Programmes.SandierSerfaty.CalcKF3 | yes | 0 | 256.0 |  |
| Programmes.SandierSerfaty.CalcKF4 | yes | 0 | 287.5 |  |
| Programmes.SandierSerfaty.CalcKF5 | yes | 0 | 257.6 |  |
| Programmes.SandierSerfaty.CalcKF6 | yes | 0 | 275.5 |  |
| Programmes.SandierSerfaty.CalcKF7 | yes | 0 | 133.3 |  |
| Programmes.SandierSerfaty.CalcKPilot | yes | 0 | 75.8 |  |
| Programmes.SandierSerfaty.CalcKS0 | yes | 0 | 141.3 |  |
| Programmes.SandierSerfaty.CalcKS1 | yes | 0 | 155.3 |  |
| Programmes.SandierSerfaty.CalcKS2 | yes | 0 | 157.4 |  |
| Programmes.SandierSerfaty.CalcKS3 | yes | 0 | 158.2 |  |
| Programmes.SandierSerfaty.CalcLam | yes | 0 | 150.8 |  |
| Programmes.SandierSerfaty.CalcLamCore | yes | 0 | 59.1 |  |
| Programmes.SandierSerfaty.CalcLamE0 | yes | 0 | 511.2 |  |
| Programmes.SandierSerfaty.CalcLamE1 | yes | 0 | 492.9 |  |
| Programmes.SandierSerfaty.CalcLamE2 | yes | 0 | 478.1 |  |
| Programmes.SandierSerfaty.CalcLamE3 | yes | 0 | 418.9 |  |
| Programmes.SandierSerfaty.CalcLamE4 | yes | 0 | 422.1 |  |
| Programmes.SandierSerfaty.CalcLamE5 | yes | 0 | 424.6 |  |
| Programmes.SandierSerfaty.CalcLamE6 | yes | 0 | 428.5 |  |
| Programmes.SandierSerfaty.CalcLamE7 | yes | 0 | 411.8 |  |
| Programmes.SandierSerfaty.CalcLamE8 | yes | 0 | 432.0 |  |
| Programmes.SandierSerfaty.CalcLamE9 | yes | 0 | 751.1 |  |
| Programmes.SandierSerfaty.CalcLamF0 | yes | 0 | 611.9 |  |
| Programmes.SandierSerfaty.CalcLamF1 | yes | 0 | 724.4 |  |
| Programmes.SandierSerfaty.CalcLamF2 | yes | 0 | 812.2 |  |
| Programmes.SandierSerfaty.CalcLamF3 | yes | 0 | 722.9 |  |
| Programmes.SandierSerfaty.CalcLamF4 | yes | 0 | 716.0 |  |
| Programmes.SandierSerfaty.CalcLamF5 | yes | 0 | 445.3 |  |
| Programmes.SandierSerfaty.CalcLamF6 | yes | 0 | 457.8 |  |
| Programmes.SandierSerfaty.CalcLamF7 | yes | 0 | 472.4 |  |
| Programmes.SandierSerfaty.CalcLamF8 | yes | 0 | 527.3 |  |
| Programmes.SandierSerfaty.CalcLamF9 | yes | 0 | 554.7 |  |
| Programmes.SandierSerfaty.Chain | yes | 0 | 61.9 |  |
| Programmes.SandierSerfaty.ChainLink | rebuilt now (45.7s) | 0 | 65.1 | olean was missing -> built with lean_pinned flags into .olean_out |
| Programmes.SandierSerfaty.Constants | yes | 0 | 62.9 |  |
| Programmes.SandierSerfaty.IV | yes | 0 | 91.6 |  |
| Programmes.SandierSerfaty.SignedEndpoints | yes | 0 | 54.7 |  |
| Programmes.SandierSerfatyStatement | yes | 0 | 67.7 |  |
| Programmes.ZeroPoint.Basic | yes | 0 | 63.8 |  |
| Programmes.ZeroPointCert.Basic | yes | 0 | 65.4 |  |
| Programmes.ZeroPointClass.Basic | yes | 0 | 58.9 |  |
| Programmes.ZeroPointPhys.Basic | rebuilt now (44.0s) | 0 | 89.2 | olean was missing -> built with lean_pinned flags into .olean_out |
| Programmes.ZeroPointPhys.Taylor | yes | 0 | 92.9 |  |
| Programmes.SandierSerfatyL1.* (776 modules) | n/a | - | - | SKIPPED: being generated by another job, untracked, no oleans |

Caveats: freshness = olean mtime >= source mtime; dependency staleness not checked. Default leanchecker does not re-replay imports. Per-module logs in `logs/`. Scripts in `scripts/`.

## Not replayed

- QuantumFluids H7 (`Autoresearch_Enstrophy`), H8 (`Autoresearch_SkBound`), P6: no .olean exists on disk (compiled with plain `lean` on the rc2 toolchain, no `-o`), so leanchecker has nothing to replay. They need the QuantumFluids qf-lake environment and an `-o` build; not done here.
- `Triangular/Axioms.lean`: audit script with planted controls (`sorry`, `axiom ctl_cheat`), expected to fail.
- `Programmes/Famille/Acronymes.lean`: modified under 30 min before start (another job writing).
- `Programmes/SandierSerfatyL1/*`: generated by another job, untracked, no oleans.
- Machine load was 12-18; no taskset pinning, 3 workers at nice 10. Page cache was cold for the first ~18 modules (150-800 s each), then warmed.
