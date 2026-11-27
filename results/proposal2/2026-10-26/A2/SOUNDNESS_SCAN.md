# A2(c)+(e) Soundness-escape scan and independent kernel replay

**Verdict: NO ESCAPE FOUND.** Every layer below ran, and every layer caught its planted negative control.
- **Source scan:** no escape construct in the 2,585-module dependency closure, or in all 2,659 corpus `.lean` files.
- **Environment scan:** no unsafe, partial, opaque, `implemented_by`, `extern` or axiom constant from the corpus appears in the proof closure of any breakdown theorem.
- **Kernel replay:** all 88,400 corpus declarations re-checked by the Lean kernel against the reused Mathlib. NS: 53,752 declarations, 609 modules. Euler: 34,648 declarations, 1,829 modules.
- **leanchecker:** the toolchain's own checker accepts the 8 statement and root modules.

## Dependency closure

`scripts/closure.py` computed the transitive closure of the `import` lines inside the corpus (`closure_*.json`):

| roots | corpus modules | lines | external (Mathlib) imports |
|---|---|---|---|
| `NavierStokes.ComparatorSolution` | 609 | 382,514 | 210 |
| `Euler.Solution` | 1,829 | 210,326 | 190 |
| both plus `NavierStokes`, `Euler`, the two challenges | 2,585 | 615,319 | 309 |

The constant-level proof closure was computed by the metaprogram, as theorem values transitively:
- NS: 93,597 constants, of which 31,516 are from 597 corpus modules.
- Euler: 94,411 constants, of which 26,213 are from 1,756 corpus modules.

## Layer 1: source scan (`scripts/source_scan.py`)

**How it works.** Comments and docstrings are stripped and string literals blanked; only code counts. The scan covers:
- `sorry`, `admit`, `native_decide`, `ofReduceBool`/`trustCompiler`/`reduceBool`
- `axiom` declarations
- `implemented_by`, `extern`, `unsafe`, `csimp`, `opaque`, `partial def`
- `#exit`, `set_option debug.*`, `skipKernelTC`, `set_option pp.*`, any `set_option`
- `addDecl`/`modifyEnv`/`setEnv`/`Kernel.` environment edits
- `#eval`/`run_cmd`/`run_elab`/`initialize`
- `elab`/`macro`/`syntax`/notation definitions, `@[command_elab|term_elab|tactic|…]`
- `import Lean…`, local instances

**Result on the 2,585-module closure** (`evidence/scan_closure.json`), identical on all 2,659 corpus files (`evidence/scan_allfiles.json`):
- **0 hits** for every escape category.
  - This includes `native_decide`, `implemented_by`, `extern`, `unsafe`, `csimp`, `opaque`, `partial`, `axiom`, `#exit`, `set_option` of any kind, `addDecl`/env edits, `#eval`/`run_cmd`/`initialize`, `elab`/`macro`/`syntax`, `import Lean`.
  - In particular, there is no `maxHeartbeats` and no `debug.*` option.
- **`sorry` hits: 4.** All four are the intentional placeholders in `ComparatorChallenges/NavierStokes.lean:277,284` and `ComparatorChallenges/Euler.lean:88,184`. Neither solution imports these modules: they are absent from both closures.
- **`local notation`: 154** (`ℝ³`, `ℝ^n`, `∇⬝`, …), plus 2 `@[inherit_doc]` on a notation.
  - The notation in the statement files is checked semantically by the elaborated-term identity in AXIOMS.md, so a malicious notation would have shown up there.
- **`attribute [local instance]`: 11.**
  - `Classical.propDecidable`: 4.
  - `compactInterval` / `EulerPacketTimePathGluing.compactInterval`: 6. These are corpus instances.
  - `CompletePartialOrder.toSupSet` in `Euler/Solution.lean`: 1. Cleared by the identical type hash in AXIOMS.md.

**Negative control** (`evidence/controls/scan_plant/`).
- One plant per category was appended to a scratch copy of `ComparatorSolution.lean`, plus an `import Lean`.
- **Every category was caught:** sorry 2, admit 1, native_decide 1, ofReduceBool 1, axiom 1, implemented_by 1, extern 1, unsafe 1, csimp 1, opaque 1, partial 1, #exit 1, debug 1, skipKernelTC 1, pp 1, addDecl/modifyEnv 1, run_cmd/#eval/initialize 3, elab/macro/syntax 5, command_elab 1, import Lean 1.
- The unmodified copy (`Clean.lean`) gave no escape hits.

**Regex bug found and fixed during this audit.** The anchored patterns first used `^\s*`, which spans newlines, so 69 notation lines were mis-attributed to the preceding blank line. The patterns now use `[ \t]*`, and both scans above were re-run after the fix.

## Layer 2: environment scan over the built environment (`lean_scripts/DumpCore.lean.txt`, `soundnessScan`)

**How it works.** It runs inside `import NavierStokes.ComparatorSolution` / `import Euler.Solution` and walks the full proof closure, theorem values included. For every reached constant it reports:
- membership of `Lean.ofReduceBool`, `Lean.ofReduceNat`, `Lean.trustCompiler`, `sorryAx`;
- `isUnsafe`, `isPartial`;
- axioms, opaques;
- `implemented_by` (`Compiler.getImplementedBy?`) and `extern` (`isExtern`).
It also lists every axiom in the imported environment, and every flagged corpus constant in the whole environment.

**Result for NS** (`evidence/audit/sound_ns.txt`) and **for Euler** (`sound_euler.txt`):
- **Axioms in the proof closure:** exactly `propext`, `Quot.sound`, `Classical.choice`.
- **`ofReduceBool`/`ofReduceNat`/`trustCompiler`/`sorryAx` in the closure:** none.
- **Closure flags in corpus modules:** **none**.
- **All closure flags are in Lean core or Mathlib:**
  - 58 `extern` (core `Nat`/`Array`/`String` primitives);
  - 6 `implemented_by` (`Lean.Name.*`, core);
  - 2 core opaques;
  - 48 (NS) / 51 (Euler) Mathlib `irreducible_def` wrappers (`….wrapped._@…`, opaque by design).
  These matter to the kernel only through the three whitelisted axioms.
- **Axioms anywhere in the imported environment:** the 15 that core Lean always declares. These are `propext`, `Quot.sound`, `Classical.choice`, `Quot.lcInv`, `sorryAx`, `Lean.ofReduceBool`, `Lean.ofReduceNat`, `Lean.trustCompiler`, and the compiler-only `lc*`/`isScalarObj`. The corpus adds **no** axiom.
- **Whole-environment corpus flags:** 12 (NS) and 39 (Euler) `…._unsafe_rec` constants with `partial=true`.
  - These are compiler auxiliaries Lean generates for executable code of well-founded-recursive definitions.
  - None of them is in any theorem's proof closure, which shows zero corpus flags.
  - No corpus constant is `unsafe`, `opaque`, an `axiom`, `implemented_by` or `extern`.

**Negative control** (`evidence/controls/env/`, `ctl_sound.txt`):
- the planted axiom and the native_decide auxiliary axiom → `AXIOM`;
- `implemented_by` → `IMPLEMENTED_BY`;
- `sorryAx` → `BAD_CONST_IN_CLOSURE`;
- `unsafe def` → `unsafe=true`;
- `partial def` → `OPAQUE` plus `_unsafe_rec partial=true`;
- `@[extern] opaque` → flagged.
All were caught.

## Layer 3: kernel replay of the whole corpus (`lean_scripts/A2Replay.lean`)

**Why this layer exists.** It addresses the gap AXIOMS.md shows: a forged declaration added with `debug.skipKernelTC` passes `#print axioms` as "does not depend on any axioms".

**How it works.**
- `A2Replay.lean` uses the same mechanism as the toolchain's `leanchecker` (`Lean.Replay`, `Kernel.Environment.replay`), with one shared base environment.
- It reads every declaration stored in the `.olean` / `.olean.server` / `.olean.private` files of each corpus module in the closure.
- It imports **only** the non-corpus dependencies (Mathlib etc.) and replays all corpus declarations through the kernel.
- It ran pinned to a single core, with `/usr/bin/time -v`.

| closure | modules | declarations replayed | base env | result | wall | max RSS |
|---|---|---|---|---|---|---|
| NS | 609 | 53,752 | 774,999 constants, 210 imports | `REPLAY OK: 53752 declarations kernel-checked in 621964 ms`, rc 0 | 11:33 | 8.1 GB |
| Euler | 1,829 | 34,648 | 774,999 constants, 190 imports | `REPLAY OK: 34648 declarations kernel-checked in 933056 ms`, rc 0 | 15:42 | 9.8 GB |

**Name clashes with Mathlib.** Two corpus declarations per closure already existed in the base environment:
- NS: `HasDerivWithinAt.congr_simp`, `HasDerivAt.congr_simp`;
- Euler: `ContinuousLinearMap.compLpL.congr_simp`, `AddMonoidHom.compLeftContinuous.congr_simp`.
These are automatically realised `congr_simp` lemmas for Mathlib constants. For all four, the base and corpus type hashes are identical (`logs/replay_clashes_ns.log`, `logs/replay_clashes_euler.log`).

**Controls** (`evidence/controls/forged/replay_control.log`):
- **Negative:** the forged `A2Forged` module is rejected with "(kernel) declaration type mismatch, 'A2Forged.forged_false' has type True but it is expected to have type False", rc 1.
- **Positive:** `NavierStokes.ComparatorDefinitions` replays OK (95 declarations).

## Layer 4 (e): the toolchain's own `leanchecker` (independent kernel checker available here)

**Run.** `leanchecker` ships in the v4.34.0-rc2 toolchain (sha256 `ccef1bfe…`). It replays each named module's declarations into that module's own imported environment. It was run under `lake env` on (`logs/leanchecker_roots.log`):
- `NavierStokes.ComparatorSolution`, `NavierStokes.ComparatorR3Theorem`, `NavierStokes.ComparatorTheorem`, `NavierStokes.ComparatorDefinitions`;
- `Euler.Solution`, `Euler.SolutionDefinitions`;
- `ComparatorChallenges.NavierStokes`, `ComparatorChallenges.Euler`.

**Result.** All rc 0, about 15 s each. The challenge modules pass because `sorryAx` is a legitimate kernel axiom; the axiom check, not the kernel, is what rejects `sorry`.

**Negative control.** `leanchecker A2Forged` exits 1 with the same kernel type-mismatch message.

**Why per-module leanchecker was not run on all 2,438 modules.** It costs about 15–25 s per module of environment import, roughly 10+ CPU-hours. `A2Replay.lean` covers the same per-declaration kernel check for all of them in 27 minutes total.

**Not available:**
- `nanoda`, a second kernel implementation: not installed on this machine.
- Comparator: its build here targets Lean 4.34.1, not rc2.
- `leanchecker --fresh`, a full Mathlib re-replay: not attempted, since it is hours single-threaded and Mathlib is a stated trust assumption.

## Trust base (what this audit does not re-check)

- **The Lean 4.34.0-rc2 kernel and toolchain.** The same kernel built and replayed the corpus. No second kernel implementation was run.
- **Mathlib 85e3a25e and its dependencies.** These oleans came from Mathlib's cache, were reused rather than rebuilt, and were not replayed.
- **`Expr.hash` for non-corpus constants** in the statement-identity check (AXIOMS.md).
