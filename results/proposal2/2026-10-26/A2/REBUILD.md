# A2(a) Independent rebuild of openai/NavierStokesAndEuler

**Verdict: REBUILT.**
- All 2,440 corpus modules rebuilt from source, with `rc=0` and zero errors:
  - 609 in the import closure of `NavierStokes.ComparatorSolution`;
  - 1,829 in the closure of `Euler.Solution`;
  - the 2 `ComparatorChallenges` modules.
- The 2,438 solution-closure modules gave zero warnings. The 2 challenge modules gave exactly their 4 intentional `sorry` placeholder warnings, 2 each.
- This used the corpus's own lakefile options and toolchain.
- Mathlib was **reused**, not rebuilt: an exact-revision prebuilt copy exists on this machine. No `Mathlib.*` module was recompiled.

## Source

| item | value |
|---|---|
| corpus | `/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/SocrateAI-Scientific-Agora-LeanMaster/lean4basesource/openai-navierstokes` |
| HEAD | `f9e8bc5b38b6e212696e8a30e3e91517af887bbd` (`git rev-parse HEAD`). `git status --short` printed nothing, so the tree is clean. |
| toolchain | `leanprover/lean4:v4.34.0-rc2`. `lean --version` reports "Lean (version 4.34.0-rc2, x86_64-unknown-linux-gnu, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, Release)". |
| lean binary sha256 | `e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550` (elan toolchain on disk 2) |
| build copy | `/home/callensxavier_gmail_com/proposal2/A2/ns-copy/` (rsync of the source, without `.git` or `.lake`) |

## Dependencies: exact-revision reuse

`scripts/check_revs.py` compared `git rev-parse HEAD` of each package with `lake-manifest.json`.
- `/mnt/disks/disk-socrateai-local-1/leanmaster/lake-v434/packages` (and `qf-lake`) matches **all nine** library packages exactly:
  - mathlib `85e3a25e006c35636f0e53b0e9296caca2685bc0`
  - plausible `d9598f07`
  - LeanSearchClient `ba67e212`
  - importGraph `d8823026`
  - proofwidgets `a8acbfd8`
  - aesop `18889deb`
  - Qq `507746ab`
  - batteries `d54dddc5`
  - Cli `ab3a82db`
- mathlib's `lean-toolchain` is also `v4.34.0-rc2`.
- The 7.9 GB `packages/` directory was **copied** (rsync, 02:00–02:22 UTC) into `ns-copy/.lake/packages`. The original was never modified. The copy was re-verified as matching afterwards.
- `lake build --no-build Mathlib` reported "All targets up-to-date (8762 jobs)", rc 0, before the real build started.
- The real build logs contain **0** `Built Mathlib…` lines. Mathlib and its dependencies show only as `Replayed`.
- **Mathlib provenance (trust assumption).** The reused `Mathlib.olean` is dated 2026-09-19 16:53, about three minutes after its `packages/` directory was created at 16:50. From those two timestamps alone I *infer* that these are Mathlib's cache artifacts (`lake exe cache get`), not a local build. This was not otherwise verified.
  - Mathlib's oleans are **trusted, not re-checked** here.
  - The kernel replay in SOUNDNESS_SCAN.md re-checks every corpus declaration against them.

## Deviation from upstream build configuration: build infrastructure only

- In the copy only, the `Comparator` `[[require]]` was removed from `lakefile.toml`. Its manifest entries `Comparator` and `lean4export` were removed from `lake-manifest.json`. The script is `scripts/strip_comparator_dep.py`, and the originals are kept as `*.orig`.
- **Why.** Neither package is present in the prebuilt package set, and fetching them would mean downloading third-party code.
- **Why it changes no compiled module.** No corpus file imports `Comparator` or `lean4export`. The grep of every `import` line found only `Mathlib`, `NavierStokes.*`, `Euler.*`, and the corpus's own `ComparatorChallenges`. The require only provides the `lake exe comparator` tool.
- **Consequence.** Comparator itself was **not** run. Its two checks were substituted as follows:
  - statement identity: the elaborated-term comparison in AXIOMS.md;
  - kernel replay: SOUNDNESS_SCAN.md.
  - nanoda was not run either, because it is not on this machine.

Diff (`lakefile.toml.orig` → `lakefile.toml`):
```
11,16d10
< [[require]]
< name = "Comparator"
< scope = "leanprover"
< git = "https://github.com/leanprover/comparator.git"
< rev = "v4.34.0-rc2"
<
```

## Build

- **Driver.** `scripts/run_build.sh`, started with `setsid nohup taskset -c 0-3` and `LEAN_NUM_THREADS=4`.
  - Lake ran at most 4 `lean` processes, all on cores 0–3, at about 3–6 GB RSS each.
  - It ran sequential `lake build -v <target>` invocations, which apply the lakefile options: Euler gets `autoImplicit=false, warningAsError=true`, as confirmed in `.lake/build/ir/Euler/Solution.setup.json`.
- **Contention.** Another session's unrelated Lean job (Lean 4.34.1, `formal_cert`) ran on the same machine at the same time.

| target | modules built | result | wall time |
|---|---|---|---|
| `NavierStokes.ComparatorSolution` | 609 `Built NavierStokes.*` | `Build completed successfully (9371 jobs)`, rc 0 | 3,300 s (02:28:08 → 03:23:08 UTC) |
| `Euler.Solution` | 1,829 `Built Euler.*` | `Build completed successfully (10591 jobs)`, rc 0 | 5,109 s (03:23:08 → 04:48:17 UTC) |
| `ComparatorChallenges.NavierStokes` | 1 | rc 0 (2 expected `sorry` warnings: the challenge placeholders) | 33 s |
| `ComparatorChallenges.Euler` | 1 | rc 0 (2 expected `sorry` warnings) | 12 s |

- **Warnings.** The two solution builds contain **0** warning lines and **0** error lines. Under Euler's `warningAsError`, any `sorry` would have failed that build.
- **The corpus's in-file `#print axioms` lines**, emitted during the build (verbatim from the logs):
```
info: NavierStokes/ComparatorSolution.lean:31:0: 'NavierStokes.Comparator.navier_stokes_breakdown_R3' depends on axioms: [propext, Classical.choice, Quot.sound]
info: NavierStokes/ComparatorSolution.lean:32:0: 'NavierStokes.Comparator.navier_stokes_breakdown_periodic' depends on axioms: [propext, Classical.choice, Quot.sound]
info: Euler/Solution.lean:73:0: 'Euler.euler_breakdown_R3' depends on axioms: [propext, Classical.choice, Quot.sound]
info: Euler/Solution.lean:75:0: 'Euler.exists_compact_smooth_euler_singularity' depends on axioms: [propext, Classical.choice, Quot.sound]
```
  These are the corpus's own `#print axioms` commands. AXIOMS.md has the output of a separate file that I wrote myself.
- **Artifacts.**
  - 2,440 `.olean` files in `ns-copy/.lake/build/lib/lean`.
  - `NavierStokes/ComparatorSolution.olean` sha256 `5025fa4e63160cea4fff8dd8f8350acabd3478cdc08563f383484fd01620de76`.
  - `Euler/Solution.olean` sha256 `4c1131d1d7451f13977111c4116f230ac1067aa0b24e946c398cc2e71dd0102e`.
  - Logs are in `logs/` here and in `/home/callensxavier_gmail_com/proposal2/A2/logs/`.
