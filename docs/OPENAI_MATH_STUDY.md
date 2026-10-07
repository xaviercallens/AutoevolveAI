# openai/math — study and the `openai_math` discovery sub-project

Status 2026-10-07: **study done from the public GitHub pages; local clone not yet made.**
The session that wrote this could not run `git clone` (network git was refused by the
permission mode), so everything below was read through GitHub's web pages and API via
WebFetch, which passes pages through a summarising model. Numbers marked
**[recount]** came from that path and are not trusted; `scripts/openai_math/index_corpus.py`
recounts them from disk once the clone exists. Numbers marked **[README]** are quoted from
the upstream README.

## 1. What the repository is

- `github.com/openai/math`, Apache-2.0, a single commit `adc7f124` ("Initial commit",
  2026-10-06) [recount].
- "722 manuscripts organized into 372 families" produced by "an internal OpenAI model";
  "the model was posed approximately 4,000 problems"; "on average, each result used three
  hours of ChatGPT Pro thinking compute" [README].
- Upstream's own caveats, verbatim [README]: "This collection includes results at different
  stages of verification." "Not all have accompanying Lean formalizations." "Some of the
  unformalized results could have issues." One result (the Re(s) > 11/12 zero-free region)
  "was human edited for readability."
- Layout: `preprints/<Title-Date>/paper.pdf` (+ source, BibTeX), `CONTENTS.md` (family
  index with abstracts), `overview.{tex,pdf}`, `reasoning_traces/` (10 PDFs + 1 `.tex` for
  families 007, 017, 087, 102, 159, 197, 221, 271, 287, 362), and `lean/`.
- Preprint folders are dated September 23–24, 2026 [recount].

**Reading rule for this project:** an upstream manuscript is a *claim by another model*, not
a result. Only a Comparator-checked Lean theorem (section 2) is upstream's verified tier, and
even that certifies the Lean statement, not that the statement says what the paper says.
Headline unformalized claims (e.g. family 002 "the full BSD formula from low Selmer corank",
032 Hodge/Kuga–Satake, 014 restricted geometric Langlands) are unverified here and must
never be cited as results.

## 2. The Lean side

- `lean/lean-toolchain`: `leanprover/lean4:v4.34.1`. Local `formal/` is
  `v4.34.0-rc2` with a **partial** Mathlib (LL.md §3). **Not compatible.**
- `lean/lakefile.lean`: package `OAI`, `autoImplicit false`, Mathlib pinned at
  `d13f23b723b8a846827a245b89c10fc7d3f11612`, plus ~30 pinned git dependencies
  (PrimeNumberTheoremAnd, StrongPNT, carleson, sphere-eversion, ClassFieldTheory,
  PrimeCert, leancert, a family of `lana-agents/*` libraries such as `iut`,
  `elliptic-curves`, `heights`, `belyi`, ...). Eleven of them get compatibility patches
  from `lean/patches/*-lean4341.patch`, applied by a `run_cmd` hook *before* Lake resolves
  dependencies. One `lean_lib` per area: `OAI.NumberTheory`, `OAI.Combinatorics`,
  `OAI.Analysis`, ... 23 in all.
- Upstream warns the full library may hit Linux `vm.max_map_count`; workaround is a Lean
  built with `-DMMAP=OFF` or `GLIBC_TUNABLES=glibc.malloc.mmap_max=0:glibc.malloc.arena_max=1`.
- `lean/docs/NNN.md`: one scope note per formalized family (~140–150 files [recount]),
  stating what exactly the Lean proves and linking its Comparator challenge.
- `lean/formalization.yaml`: a catalogue whose `sources` list has ~256 article entries [recount].
- `lean/OAI/NumberTheory/` has these family folders: Catalan, Chromatic, CubicGauss,
  CubicGram, CubicMoment, DirichletL, DuffinSchaeffer, DukePrimeDegree, EgyptianFractions,
  GaussianMoat, Jacobsthal, JointDickman, NumberField, OrdinaryCorrelations, Ostmann,
  PiExponent, PowerFree, PrimeGaps, PrimePackets, QuadraticForms, ShortEgyptian,
  SiegelZeros, SingleFold, TotientAsymptotic, TotientFibers, TwoPoint,
  TwoPointCorrelations, ZetaFive [recount].

### Comparator: the idea worth adopting

Each verified result is a pair in `lean/ComparatorChallenges/`:

```lean
-- Catalan.lean (challenge: the statement only, proof is `sorry`)
import Mathlib
namespace OAI
namespace InternalCatalan
theorem catalan_irrational :
    Irrational (∑' j : ℕ, (-1 : ℝ) ^ j / ((2 * j + 1 : ℕ) : ℝ) ^ 2) := by
  sorry
end InternalCatalan
end OAI
```

```json
{"challenge_module": "ComparatorChallenges.Catalan",
 "solution_module": "OAI.NumberTheory.Catalan.Main",
 "theorem_names": ["OAI.InternalCatalan.catalan_irrational"],
 "definition_names": [], "enable_nanoda": false,
 "permitted_axioms": ["propext", "Quot.sound", "Classical.choice"]}
```

Run with `comparator`, `landrun` (sandbox) and `lean4export` on PATH:
`lake update && lake exe cache get && lake env comparator ComparatorChallenges/<X>.json`.
Comparator checks that the solution module's theorem has *exactly* the challenge's type and
uses only the permitted axioms, working on the exported environment inside a sandbox.

Why this matters for AutoevolveAI: our gate (`anse/formal/lean_runner.py`, file mode)
parses `#print axioms` text from the output of a file that also contains model-written
proof text. Master-math run two found that a proof body can print a forged axiom report and
then `#exit`, and patched `build_ladder.verdict` on branch `worktree-master-math-regen2`,
**which is not merged into main** (checked 2026-10-07: main has no `#exit` guard anywhere in
`scripts/` or `anse/`). `lean_runner.py` on main has no such guard either, so its file mode
is *likely* forgeable; this was not tested in this session. Comparator's split — reviewed
statement module, untrusted solution module, environment-level comparison, sandbox —
removes that whole class.
The permitted-axiom whitelist is the same as ours. What Comparator does **not** check:
whether the challenge statement is faithful to the paper (LL.md §7). That review stays ours.

## 3. What AutoevolveAI can and cannot do with it today

| Can do now (T4 box, no new downloads) | Needs a user decision first |
|---|---|
| Index + audit the clone (`index_corpus.py`) | The clone itself (network git refused in-session) |
| Statement-faithfulness review of challenges vs abstracts | A separate Lake project for OAI: v4.34.1 toolchain, `lake exe cache get` (many GB), ~30 deps, mmap workaround |
| PARI/GP + Sage numerical checks of quantitative number-theory claims | Installing `comparator`, `landrun`, `lean4export` |
| Use scope notes as a source of well-posed target statements | Building any `OAI.*` module locally |

Hard rules carried in: never copy an `import Mathlib` challenge into `formal/` (it will not
build, LL.md §3); never compile in a worktree (no `formal/.lake`); every experiment gets a
positive and a negative control; PARI/Sage, not hand arithmetic, is ground truth.

Overlap with LeanMaster: LeanMaster is about lattices, T-duality, K3/Mukai lattices,
moonshine (MCP `search_theorems`). The nearest upstream family is 032 (Hodge and
Kuga–Satake for K3 surfaces), which is algebraic geometry far above LeanMaster's lattice
arithmetic; treat the link as "shared objects", not shared theorems. Run
`search_theorems` before stating anything K3-related.

## 4. The sub-project: stages

"Discovery" here is staged honestly. Re-verifying another model's claims is **not**
discovery; it is the instrument check that has to come first (LL.md §1).

- **D0 — index and audit** (code ready, BLOCKED on the clone).
  `scripts/openai_math/index_corpus.py` → `results/openai_math/corpus_index.json`: recounts
  every number above, records clone HEAD and README sha256, and audits each challenge
  (permitted axioms ⊆ whitelist, `theorem_names` declared, statement-only file with `sorry`,
  no `axiom`, imports). Tests: `tests/openai_math/` (positive + negative controls).
- **D1 — statement faithfulness.** For the number-theory challenges first: compare each
  Lean statement with its scope note and paper abstract; flag vacuous or weakened
  statements. A model reviewer is recorded as a model, not a human audit (LL.md §12).
- **D2 — independent Comparator re-run** (producer ≠ verifier). After approval: separate
  Lake project on disk 2, start with one small challenge (Catalan), preregister the expected
  outcome, and include a negative control (a challenge with a perturbed statement must fail).
- **D3 — numerical cross-checks.** Preregistered PARI/Sage experiments on quantitative
  claims, e.g. family 012: the density of n with P⁺(n) < P⁺(n+1) is 1/2 (upstream scope note).
  Finite-N numerics can only be *consistent* with a limit, never confirm it; the
  preregistration fixes N, the statistic and the tolerance beforehand. Negative control: a
  deliberately wrong prediction must be rejected at the same N.
- **D4 — discovery proper.** From D1–D3-checked families, generate *new* candidate
  statements (parameter extensions, finite instances, sharper constants suggested by D3 data),
  check them numerically, state them in Lean against the locally built Mathlib subset, and
  run the local provers (DeepSeek-Prover-V2-7B; Goedel needs its chat template) behind the
  sound gate. Anything that survives is a candidate, reported with its controls.
- **D5 — learning.** Only gate-verified episodes go to the datalake with real verdicts
  (`verdict: "PASSED"`), under the ≤30% unverified-signal cap.

## 5. Next command

```bash
git clone --depth 1 https://github.com/openai/math \
  /mnt/disks/disk-socrateai-local-1/callensxavier_home_data/SocrateAI-Scientific-Agora-LeanMaster/lean4basesource/openai-math
python3 scripts/openai_math/index_corpus.py   # D0; exits 2 with BLOCKED until the clone exists
```
