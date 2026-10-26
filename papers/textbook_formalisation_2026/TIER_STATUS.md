# TIER_STATUS - per-module leanchecker replay status used in the 2026 revision

Snapshot taken 2026-10-26 from `results/kernel_replay_2026-10-26/replay.jsonl` (30 rows, all rc 0, replay still running;
plan.json lists 871 files), `ch4_popgen_trace/leancheck_ch4.json` (10 rows, rc 0) and
`results/textbook_formalisation_2026/acronymes_leanchecker_sources.json` (10 rows, rc 0). The grep record
(`grep_hits.json`) has no code hit outside declared planted-control files and doc comments.
Replay covers the declarations of each module; Mathlib and the Lean core are loaded, not replayed.

Rule applied: replayed rc 0 -> `\tierA` citing the replay record; not (yet) replayed -> `\tierAs` ("Niveau A sans rejeu",
defined in main.tex). When a module below is replayed rc 0, change its `\tierAs` to `\tierA` at the listed places.

| Chapter / place | Module(s) | Replay status used | Label |
|---|---|---|---|
| ch1 CM/Bernstein statements | Programmes.CompletelyMonotone.{Basic,Bernstein,Laplace,Corollaries,Applications,Examples,Limits,MathlibOnly,MathlibOnlyBridge} | rc 0 (replay.jsonl) | A |
| ch1/ch2 Riesz, any density, upstream corollaries | Triangular.{Riesz,RieszFinite,AnyDensity,OpenDisk,OpenDiskAny,UniversalOptimality} | rc 0 (replay.jsonl; sources.json) | A (conditional on upstream) |
| ch2 dipolar (incl. g_inplane) | Autoresearch.{DipolarExciton,DipolarExcitonMultipolar,DipolarExcitonStep1} | rc 0 | A (B2: kept A, replay stated) |
| ch2 Yukawa | Autoresearch.{Yukawa,YukawaMix} | rc 0 | A |
| ch2 Keldysh | Autoresearch.KeldyshCM | rc 0 | A |
| ch2 s2.5 Sandier-Serfaty statement, SignedEndpoints | Programmes.SandierSerfatyStatement, Programmes.SandierSerfaty.SignedEndpoints | not replayed (only builds of Axioms*, CalcKCore, ChainLink) | As (ch2 lines ~935, 977, 1010) |
| ch2 A1 table, init_constants and bcons/eps | Programmes.SandierSerfaty.* | not replayed | As (L1 and L2 rows) |
| ch2 A1 table, calcLam / calcK | Programmes.SandierSerfaty.{CalcLam*,CalcK*} | not replayed, and no producer != verifier pass | C (B2) |
| ch3 P2 zero-point | Programmes.ZeroPoint.Basic | not replayed | As (ch3 lines 168, 187, 328, 339, 421, 466, 474, 519-523) |
| ch3 B2 certificate | Programmes.ZeroPointCert.Basic | not replayed | As |
| ch3 P6 Feynman-Bijl | Programmes.FeynmanBijl.Basic | in plan.json, not yet replayed | As (ch3 lines 647, 687, 702, 716, 754-758, 791-798) |
| ch4 PopGen / EvoGraph | Autoresearch.{PopGenFisher,PopGenWrightFisher,PopGenImportBoth}; Programmes.PopGen.{Absorption,WrightFisherFixation,MoranModel,MoranFixation,Price}; Programmes.EvoGraph.{Transport,BirthDeath,Examples,EvoGraphImportAll} | rc 0 (ch4 trace + replay.jsonl) | A |
| ch5 U3 sBog_le_sqrt | QuantumFluids stack, Lean v4.34.0-rc2 (outside this repo) | no replay record | As (ch5 line 363) |
| ch5 U4 sigma = 3 | project-Mathlib stack, v4.34.0-rc2 (external to the replay) | no replay record for the cited stack | As (ch5 line 459) |
| ch1 flow table row 3 | dipolar/Yukawa/Keldysh A; sigma=3 and Bogoliubov As | as above | mixed |
| A2 forged-declaration observation | n/a | A2 paper files it at Tier X | X (B3) |

Parent action when the full replay finishes: for each As row above whose modules are rc 0, replace `\tierAs` by `\tierA`
on the listed lines, update the ch2 remark `ch2:rem:skip` and the ch3 warnbox (last paragraph) to the audit's
"code de retour 0 pour chacun" wording, and drop the `\tierAs` definition if it becomes unused.
